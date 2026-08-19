# CFMM Liquidity Research

Master's thesis, University of Padova. The thesis studies pricing and hedging for liquidity
provision in Constant Function Market Makers (CFMMs), with Uniswap V3 as the working case. Its
anchor is Tai-Ho Wang's *Pricing and Hedging for Liquidity Provision in Constant Function
Market Making* and the companion papers described in `wiki/`. The work builds from that
mathematical framework into areas the anchor papers state but do not compute, plus its own
extensions.

## Requirements

- Python 3.12. No version-specific syntax was found in a source scan, so an earlier 3.10+
  interpreter likely works, though only 3.12 has been run against this codebase.
- The packages in `requirements.txt` (add `requirements-dev.txt` to run the test suite).
- No GPU and no unusual hardware. No tracked dataset exceeds 30 MB on disk, and none needs more
  than a few gigabytes of free memory to load and process with pandas and pyarrow.
- A [The Graph](https://thegraph.com) gateway API key, only to re-pull raw data from Uniswap
  V3's subgraph. Reproducing the tracked results needs no credentials at all, since the
  processed data those results are built from is already in `codebase/data/processed/`.

## Setup

```bash
pip install -r requirements.txt          # add requirements-dev.txt for the test suite
```

To re-pull raw data instead of using the tracked processed data, copy
`codebase/data_extraction/.env.example` to `codebase/data_extraction/.env` and set
`GRAPH_API_KEY`.

## Running the pipeline

Each script is a standalone entry point, run as `python codebase/<script>.py` from the
repository root. All write into `codebase/results/`.

| Script | Produces |
| --- | --- |
| `snapshot_study.py` | Impermanent-loss price, priced IL, and implied-volatility surface (single-pair replication) |
| `liquidity_profile_study.py` | Liquidity profile, liquidity surface, and liquidity-vs-price plots (11-pool extension) |
| `price_impact_study.py` | Marginal price-impact plots per pool and fee tier |
| `functional_pca_study.py` | Rolling-window functional PCA of the log-liquidity surface |
| `functional_pca_eigenvectors_study.py` | Eigenvectors u₁–u₄ of the rank-standardized log-liquidity surface |
| `cev_elasticity_study.py` | CEV elasticity band-sweep shape diagnostic |
| `lvr_pathwise_study.py` | Pathwise loss-versus-rebalancing (LVR) variability against range width |

`codebase/results/README.md` is the legend for the output: what each of the seven result
groups contains, how its filenames are built, and where its own per-group page lives.

## Codebase layout

```
codebase/
├── data/
│   └── processed/       ← parquet tick data the runner scripts read directly
├── data_extraction/     ← API download scripts, run only to refresh data/processed/
├── src/
│   ├── data_processing/ ← parquet cleaning, block timestamps, options pipeline
│   ├── graphics/        ← plot functions, one module per output type
│   └── math_core/       ← the mathematical core (see below)
├── tests/                ← pytest suite
├── results/              ← output plots, see codebase/results/README.md
└── *_study.py            ← the seven runner scripts above
```

`data_extraction/` also writes a `data/raw/` directory, the tick and pool-state pulls
`data/processed/` is built from. That directory is excluded from this repository, since
redistribution rights over raw subgraph pulls are not cleared. It regenerates locally by
running `data_extraction/` against a live API key, and no runner script needs it directly.

## `math_core`: logical steps

All files live in `codebase/src/math_core/`. The computation follows this order.

### 1. Liquidity profile: `liquidity_profile.py`

Extract `ℓ(q)`, the piecewise-constant intrinsic liquidity, from Uniswap V3 tick data. Each
tick interval `[q_lower, q_upper]` carries a constant `ℓ` value, with zero-liquidity bins
dropped.

`build_liquidity_surface` stacks these profiles across blocks into a 2D `(time × log-moneyness)`
grid, log-transformed and centred at ATM (`curr_tick`) per block.

### 2. Option proxy: `interpolation.py`

Build a piecewise-affine market proxy `O^mkt(K)` by linearly interpolating the filtered,
parity-filled option mid-prices. On each sub-interval `[K_i, K_{i+1}]` the proxy is exactly
`a0 + a1·K`, which gives a closed-form antiderivative in the integration step.

### 3. IL and replication price: `impermanent_loss.py`

Three quantities are computed here, all from the same reserve-integral backbone.

**Pathwise IL** (`impermanent_loss`):

```
IL(P_T) = V_pool(P_T) − V_hold(P_T)
         = [x(P_T)·P_T + y(P_T)] − [x(P_0)·P_T + y(P_0)]
```

where `x(p)`, `y(p)` are the ETH and USDC reserves at price `p`, each computed as `∫ L(q) dq`
over the appropriate half-line from the piecewise-constant profile.

**IL replication price** (`BS_compute_IL_price`, RTW26 eq. 18):

```
Π^IL = ∫_0^P0   L(q) · P^mkt(q) dq   [put leg]
     + ∫_P0^∞   L(q) · C^mkt(q) dq   [call leg]
```

Evaluated exactly: on each sub-interval of the merged tick-boundary × strike grid, both `ℓ` and
`O^mkt` are piecewise-constant or piecewise-affine, which gives the closed-form antiderivative
`F(q) = ℓ·(a1·√q − a0/√q)`.

**LVR proxy** (`compute_LVR_function`, RTW26 eq. 17):

```
Ψ(P_T) − Ψ(P_0)   where   Ψ(P) = P·x(0+) − P·x(P) − y(P)
```

Vectorized over `P_T` with numpy broadcasting, `(n_PT × n_ticks)`.

**I-remainder** (`compute_I_remainder`, RTW26 Appendix C):

```
I(P_0, F) = ∫_0^P0  L(q)·(q − F) dq   ≤ 0
```

Separates the LVR replication price from Π^IL through put-call parity: `E^Q[LVR] = Π^IL − I`.

### 4. Implied volatility: `implied_volatility.py`

Find `σ_BS` such that the Black-Scholes IL price equals the market IL price (RTW26 eq. 20).

**Aggregate IV** (`compute_BS_implied_vol`): one `σ` for the whole profile.
**Fine-structure IV** (`compute_BS_iv_fine_structure`): one `σ_i` per tick interval, producing
the implied-vol surface.

Root-finding uses Newton-Raphson with the analytic derivative `∫ L(q)·vega_BS(q) dq`, with a
bisection fallback when vega is near zero. The method is safe because the left-hand side is
strictly increasing in `σ` (Proposition 3.6).

### 5. LVsP surface: `liquidity_vs_price.py`

Build the liquidity-vs-absolute-price heatmap: a `(time × absolute_tick)` grid aligned to the
pool's tick spacing, with `curr_tick` overlaid as the spot-price trajectory. Unlike the
log-moneyness surface in step 1, the x-axis is not re-centred per block, so real price movement
stays visible.

## Reproducibility and the AI workflow

This codebase and its wiki knowledge base were developed with AI coding assistants under the
author's direction. `AI-WORKFLOW.md` states what those assistants touched, what `wiki/` is, and
how to check a thesis claim against its source.

## License

`codebase/` is MIT-licensed, in `LICENSE`. The knowledge base under `wiki/` carries a separate
license, CC BY 4.0, in `LICENSE-DOCS`.

## Citation

See `CITATION.cff`.

## Author

Giorgio Cottini, University of Padova. cottinigiorgio@gmail.com
