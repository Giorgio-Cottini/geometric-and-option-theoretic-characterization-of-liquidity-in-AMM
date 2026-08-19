---
title: Thesis Codebase
layer: core
type: source
origin: thesis
date: 2026-07-22
---

# Thesis Codebase — CFMM Liquidity Research (computational overview)

The thesis's own Python implementation: it replicates and extends RTW26 (*Pricing and
Hedging for Liquidity Provision in Constant Function Market Making*), computing liquidity
profiles, impermanent loss, an LVR proxy, IL replication prices, and Black–Scholes implied
volatility surfaces from Uniswap V3 tick data. Source: `README.md` and `codebase/`.

**Institution / scope:** Master's thesis, University of Padova. Focus: pricing and hedging
for liquidity provision in CFMMs, applied to Uniswap V3.

## Key points
- **Two goals.** *Replication* — reproduce RTW26's results; *Extension* — expand the
  framework to liquidity profiles, impermanent loss, implied-volatility surfaces, and
  related quantities across CFMM designs. Replication and extension code are kept strictly
  isolated.
- **Pipeline (`codebase/src/math_core/`), in computation order:**
  1. **Liquidity profile** (`liquidity_profile.py`) — extract the piecewise-constant
     intrinsic liquidity `ℓ(q)` from Uniswap V3 tick data; `build_liquidity_surface`
     stacks per-block profiles into a `(time × log-moneyness)` grid centred at ATM.
  2. **Option proxy** (`interpolation.py`) — piecewise-affine market proxy `O^mkt(K)` from
     parity-filled option mid-prices, enabling closed-form antiderivatives.
  3. **IL & replication price** (`impermanent_loss.py`) — pathwise IL
     `IL(P_T) = V_pool − V_hold`; IL replication price `Π^IL` (RTW26 eq. 18) as put+call
     legs `∫ L(q)·P^mkt(q) dq + ∫ L(q)·C^mkt(q) dq`; LVR proxy `Ψ(P_T)−Ψ(P_0)`
     (RTW26 eq. 17); I-remainder `I(P_0,F)=∫ L(q)(q−F) dq` (RTW26 App. C), giving
     `E^Q[LVR] = Π^IL − I` by put–call parity.
  4. **Implied volatility** (`implied_volatility.py`) — solve for `σ_BS` matching BS-model
     IL price to market IL price (RTW26 eq. 20); aggregate IV (one `σ`) and fine-structure
     IV (one `σ_i` per tick → the IV surface). Newton–Raphson with analytic derivative
     `∫ L(q)·vega_BS(q) dq`, bisection fallback; monotone in `σ` (Proposition 3.6).
  5. **LVsP surface** (`liquidity_vs_price.py`) — liquidity-vs-absolute-price heatmap on a
     `(time × absolute_tick)` grid with the spot-price trajectory overlaid.
  6. **Marginal price impact** (`price_impact.py`, cycle-2 extension) — pointwise transforms of
     the liquidity surface giving absolute `2P^{3/2}/L` and relative `2√P/L` impact; a sibling of
     the frozen builders, calling them read-only. See [[concept-marginal-price-impact]].
- **Data.** Per-pool Uniswap V3 tick + pool-state parquet and raw JSON snapshots (liquidity
  and options book), extracted via `codebase/data_extraction/` API scripts. As of cycle 2 the
  historical dataset is **11 pools across 5 pairs** — WETH/USDC, WETH/USDT, WBTC/WETH,
  WBTC/USDT, USDC/USDT, each at every materially traded fee tier — all sitting on one identical
  1641-block grid. The pool set was measured rather than assumed; see
  [[synthesis-pool-selection-findings]]. The frozen snapshot pipeline still reads its own
  separate JSON snapshots.
- **Structure.** `src/{data_processing, graphics, math_core}`; runners
  `liquidity_profile_study.py` (liquidity surface + LVsP), `price_impact_study.py` (impact
  surfaces), and `snapshot_study.py` (IL price + IV surface); outputs in `tester_results/`.

## Notable claims & data
- Numerical integrals are evaluated **exactly** on merged tick-boundary × strike grids:
  `ℓ` piecewise-constant and `O^mkt` piecewise-affine give the closed-form antiderivative
  `F(q) = ℓ·(a1·√q − a0/√q)`.
- LVR proxy vectorised over `P_T` via numpy broadcasting `(n_PT × n_ticks)`.
- Compute defaults: CPU + numpy; CUDA only for clear bottlenecks (4 GB VRAM ceiling).

## Structural graph (curated)

The codebase's structural graph is staged at `wiki/graphs/code/graph.json` (319 nodes, 605
edges, 18 communities, 100% AST-extracted; refreshed 2026-07-22 after cycle 2). Structural
load-bearers, by connectivity:

- `graph:math_core_liquidity_profile_piecewise_constant_liquidity_profile` — the
  piecewise-constant `ℓ(q)`, still the most-connected node; every downstream integral and surface
  consumes it.
- `graph:graphics_price_impact_plot_impact_surface`,
  `graph:graphics_price_impact_plot_impact_profile`,
  `graph:graphics_price_impact_plot_impact_heatmap`, and
  `graph:math_core_price_impact_build_impact_surface` — the cycle-2 impact lane, which now
  occupies four of the six most connected positions.
- `graph:snapshot_study_main`, `graph:liquidity_profile_study_main`, and
  `graph:price_impact_study_main` — the three runner entry points.
- `graph:snapshot_options_pipeline_run_options_pipeline`,
  `graph:snapshot_liquidity_pipeline_run_liquidity_pipeline` — the two data pipelines.
- `graph:math_core_implied_volatility_compute_bs_implied_vol`,
  `graph:math_core_implied_volatility_compute_bs_iv_fine_structure` — the IV solvers.

Community map (18 clusters): price-impact plotting; impermanent-loss plotting; snapshot
liquidity pipeline; liquidity-profile plotting; implied-volatility math; tick data download;
pool discovery; parquet cleaning; block-timestamp fetching; extraction config and block grid;
IV surface plotting; dataset verification; LVsP surface math; LVsP plotting; block-timestamp
loading; plus three single-node package inits. The three clusters new since cycle 1 are the
impact lane and the two halves of the rebuilt data-extraction lane (pool discovery, dataset
verification). The full call-spine and bridge analysis is in
[[synthesis-codebase-architecture]]; the liquidity half in depth is
[[concept-liquidity-pipeline-code]].

## Connections
- Replicates and extends the anchor paper [[source-rtw26-cfmm-liquidity-pricing-hedging]].
- Structural architecture: [[synthesis-codebase-architecture]].
- Liquidity code path: [[concept-liquidity-pipeline-code]].
- Price-impact code path: [[concept-price-impact-code]].
- Pool selection and dataset integrity: [[concept-pool-selection-code]].

## Open questions
- Final thesis prose (`latex/chapters/`) is still empty (stubs) — the written argument and
  results narrative are pending.
- Extension scope across other CFMM designs is open-ended.
- The `liquidity-VS-price` colorbar still reads `log(Liquidity)` and names no token; the
  unit-bearing treatment the impact colorbars received has not been extended to it.
