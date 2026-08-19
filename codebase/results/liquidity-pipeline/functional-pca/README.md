# `functional-pca/`: rolling-window CPVE, Fig. 4 (bottom) replication

This page is filled from `../../README.template.md`. It covers 27 files (26 PNGs, 1 CSV).

Physically nested under `liquidity-pipeline/` (`src/graphics/config.py`, `CFG.fpca_out_dir`),
but produced by a separate script from the other three chart-kinds in that folder
(`profile/`, `surface/`, `liquidity-VS-price`, all from `liquidity_profile_study.py`). This
group has its own sweep, its own job-skip logic, and its own coverage CSV, so it gets its own
page rather than a section in `../README.md`.

## Purpose

Functional PCA of a pool's log-liquidity surface, on a rolling window over a rank-standardized
grid (`math_core.functional_pca`, Appendix B of the anchor paper). Each plot tracks CPVE_K
(cumulative proportion of variance explained, K=1..6) against the calendar date of each
window's start, replicating Fig. 4 (bottom), Risk/Tung/Wang, "Dynamics of Liquidity Surfaces in
Uniswap V3." It answers how many principal components the surface needs to explain most of its
variance, and whether that number drifts over time.

## Generating script

`functional_pca_study.py`. It reads
`data/processed/liquidity/{PAIR}/{file_basename}_ticks.parquet` (cleaned Uniswap V3 tick data)
and `data/block_timestamps.parquet` (block-to-date lookup), and writes under
`src/graphics/config.py`'s `CFG.fpca_out_dir`.

## Sweep dimensions

| Dimension | Source of truth | Values |
|---|---|---|
| pool × fee-tier | `data_extraction/config.py POOLS` | 11 jobs across 5 pairs: WETH_USDC (1/5/30bp), WETH_USDT (1/5/30bp), WBTC_WETH (5/30bp), WBTC_USDT (5/30bp), USDC_USDT (1bp) |
| window length `T` | `T_VALUES` in `functional_pca_study.py` | `300`, `400`, `500` rows, step `10` |

Not every (pool, T) combination produces a plot. A pool is skipped for a given T when it has
fewer qualifying blocks than T. `coverage.csv` (below) records every combination, produced or
skipped, with the reason for each skip.

## Directory shape

```
functional-pca/
├── 1bp/
│   ├── WETH_USDC_300.png
│   ├── WETH_USDC_400.png
│   ├── WETH_USDC_500.png
│   ├── WETH_USDT_300.png
│   ├── WETH_USDT_400.png
│   └── WETH_USDT_500.png
├── 5bp/
│   ├── WBTC_USDT_300.png
│   ├── WBTC_USDT_400.png
│   ├── WBTC_WETH_{300,400,500}.png
│   ├── WETH_USDC_{300,400,500}.png
│   └── WETH_USDT_{300,400,500}.png
├── 30bp/
│   ├── WBTC_WETH_{300,400,500}.png
│   ├── WETH_USDC_{300,400,500}.png
│   └── WETH_USDT_{300,400,500}.png
└── coverage.csv
```

No axis-basis split, unlike `profile/` and `surface/` next door: CPVE has one natural axis
(window-start date), so a chart-kind/axis-basis fan-out does not apply here. One fee-tier
folder, one file per produced (pool, T) job.

`USDC_USDT@1bp` and `WBTC_USDT@30bp` produce no files: both fall short of the minimum 300
qualifying blocks (`coverage.csv` rows, outcome `skipped`). `WBTC_USDT@5bp` produces only
`_300` and `_400`; it falls short of 500.

## File-naming pattern

`{PAIR}_{T}.png`, inside a `{fee}bp/` folder.

- `{fee}`: fee tier in basis points (`1`, `5`, `30`), from `POOLS[...]['fee_bps']` — folder
  name, not part of the filename stem (unlike `liquidity-pipeline/`'s other three chart-kinds,
  which fold `{fee}bp` into the stem itself).
- `{PAIR}`: pair label matching `POOLS[...]['pair']`.
- `{T}`: rolling-window length in rows (`300`, `400`, `500`).

## Date-range alignment

`rolling_cpve` always starts its slide at qualifying-block index 0 with the same step
regardless of `T`, so window k starts at the same qualifying block for every T value — each
T's window list is an exact prefix of any shorter-T list produced by the same pool. The runner
exploits this and crops every T-curve for a pool down to the window count of that pool's
shortest-produced T, so a pool's `_300`, `_400`, and `_500` plots always share the same
(start, end) calendar range. This crop is unconditional, applied even to a thin pool: it leaves
`WBTC_USDT@5bp`'s `_300` plot at 2 points, matching its `_400` plot, down from the 12 points the
uncropped window count would have produced.

`coverage.csv` carries both the pre-crop count (`n_windows`) and the post-crop count
(`n_windows_aligned`) per produced row, so the amount cropped away stays visible per pool.

## How to read one file

`5bp/WETH_USDC_500.png`: the 5bp WETH/USDC pool's CPVE_K, K=1..6, against the start date of
each 500-row rolling window, step 10. A curve that sits close to 1.0 for a low K means a small
number of principal components already explains most of the surface's variance in that window;
a curve that drifts down over time means the surface needs more components to explain the same
share of variance as time passes, i.e. its shape grows more complex. Horizontal reference lines
mark the 90% and 95% thresholds used to read off K directly.
