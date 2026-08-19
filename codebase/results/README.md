# `results/`: plot output

4 study scripts produce 295 files (289 PNGs, 6 CSVs) across 7 groups. This file is the entry
point: a legend for what each group is and means, plus where to find the groups whose internal
structure needs its own page. It does not cover how to regenerate a plot or which commit or
parameters produced a given file. The reader finds that detail in the generating script
directly.

## Why the groups look so different

The project runs two phases (see `../README.md` and `../CLAUDE.md`): **replication** of RTW26 on
a single ETH/USDC pair, and **extension** sweeping every pool the project tracks. That split
explains why three groups below are a handful of flat files and three are dozens to hundreds of
files nested several folders deep. The shape follows the sweep, not an arbitrary choice.

| Group | Script | Shape | Sweep |
|---|---|---|---|
| `impermanent-loss/` | `snapshot_study.py` | flat, 4 files | replication: 1 pair, 2 fee tiers (5bp, 30bp) |
| `implied-volatility/` | `snapshot_study.py` | flat, 2 files | same |
| `priced-impermanent-loss/` | `snapshot_study.py` | flat, 4 files | same |
| [`liquidity-pipeline/`](liquidity-pipeline/README.md) | `liquidity_profile_study.py` | nested, 3 levels, 77 files | extension: 11 pool × fee-tier jobs across 5 pairs, 3 axis-bases |
| [`liquidity-pipeline/functional-pca/`](liquidity-pipeline/functional-pca/README.md) | `functional_pca_study.py` | nested, 2 levels, 27 files (26 PNGs, 1 CSV) | extension: same 11 jobs, swept over rolling-window length `T` (300/400/500) |
| [`price-impact/`](price-impact/README.md) | `price_impact_study.py` | nested, 4 levels, 154 files | extension: same 11 jobs × 3 axes × 2 impact quantities |
| [`cev-elasticity/`](cev-elasticity/README.md) | `cev_elasticity_study.py` | flat, 27 files (22 PNGs, 5 CSVs) | extension: same 11 jobs, swept over band half-width `w` and branch inside the CSVs, not the directory tree |

The three extension groups share the same 11-job pool × fee-tier list. `liquidity-pipeline/` and
`price-impact/` also share a file-naming convention and fan out into chart-kind/axis-basis
subfolders; `cev-elasticity/` shares the job list and pair/fee-tier filename tokens but stays
flat, since its sweep dimensions (`w`, branch) live inside the CSVs rather than the folder tree.
Each has its own page, filled from [`README.template.md`](README.template.md); those pages give
the directory shape and how to decode a filename. Any future group with the sweep-and-fan shape,
a new script iterating pools or fee-tiers into chart-kind/axis-basis subfolders (or, like
`cev-elasticity/`, into per-row CSV columns), should get its own page from that template rather
than being included here.

## Replication groups (`snapshot_study.py`)

All four fixed-name files below live directly under their group folder, one pair (ETH/USDC) at
two fee tiers, filename `{fee}bps[_suffix].png`:

| File | Plots |
|---|---|
| `impermanent-loss/{fee}bps.png` | Pathwise IL, `IL(P_T) = V_pool(P_T) − V_hold(P_T)`, vs `log(P_T / F)`. |
| `impermanent-loss/{fee}bps_LVR.png` | IL decomposed into the LVR proxy and the hedging-cost region (RTW26 eq. 17). |
| `priced-impermanent-loss/{fee}bps.png` | The IL price integrand `L(q)·O(q)`. Its area equals the IL replication price `Π^IL` (RTW26 eq. 18). |
| `priced-impermanent-loss/{fee}bps_I.png` | `Π^IL` decomposed into the LVR replication price and the `I`-remainder (RTW26 Appendix C), via put-call parity `E^Q[LVR] = Π^IL − I`. |
| `implied-volatility/{fee}bps.png` | Per-tick Black-Scholes implied vol vs `log(K / F)` (fine structure), plus the single aggregate `σ_BS` for the whole profile. |

`../README.md`'s `math_core` section derives the math behind each quantity. This table only
maps plot files to that derivation.

## Legend shared across all groups

- **Fee-tier token**: replication groups write `{fee}bps` (for example, `5bps.png`). Extension
  groups write `{fee}bp_{PAIR}` (for example, `5bp_WETH_USDC.png`). Different scripts, different
  convention. Both are current, neither is a typo.
- **Pair token** (`{PAIR}`, extension groups only): a pair label from `data_extraction/config.py`
  `POOLS` (`WETH_USDC`, `WETH_USDT`, `WBTC_WETH`, `WBTC_USDT`, `USDC_USDT`), matching the
  human-facing price direction, not necessarily on-chain token0/token1 order. All three extension
  groups share it, `cev-elasticity/` included.
- **Chart-kind** (`liquidity-pipeline/` and `price-impact/` only — `cev-elasticity/` stays flat,
  see its own page):
  - `profile`: time-collapsed 2-D shape.
  - `surface`: 3-D time × axis-basis surface.
  - `liquidity-VS-price` / `impact-VS-price`: top-down heatmap against absolute price, always
    flat (no axis-basis split).
- **Axis-basis** (under `profile/` and `surface/` only, so `liquidity-pipeline/` and
  `price-impact/` only):
  - `log-moneyness`: re-centred at the block's spot price, then log-transformed.
  - `relative-ticks`: re-centred, not log-transformed.
  - `absolute-ticks`: not re-centred, real price axis.
  Re-centring trades cross-block comparability for visible price movement. `cev-elasticity/`
  uses `log-moneyness` internally (see its own page) but does not split files by axis-basis.

## Known drift elsewhere (do not trust this for this directory's shape)

- `snapshot_study.py`'s own module docstring names old output paths (`results/l/`, `IL/`,
  `price_IL/`). The paths above come from `src/graphics/config.py`'s `CFG`, the actual output
  root. The reader should trust that, not the docstring, if the two disagree.
