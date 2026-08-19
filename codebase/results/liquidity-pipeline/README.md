# `liquidity-pipeline/`: liquidity profile, surface, and liquidity-vs-price

This page is filled from `../README.template.md`. It covers 77 files.

A fourth subfolder, [`functional-pca/`](functional-pca/README.md), sits alongside `profile/`,
`surface/`, and `liquidity-VS-price/` (`CFG.fpca_out_dir` nests under `CFG.liq_out_dir`), but
comes from a separate script, `functional_pca_study.py`, with its own sweep and its own page.
It is not one of the three chart-kinds this page describes.

## Purpose

The plots show the pool's intrinsic liquidity `ℓ(q)` (see `Thesis/README.md`, `math_core` step
1) three ways: as a time-collapsed shape, as a 3-D time × price surface, and as a top-down
liquidity-vs-price heatmap. This group is the extension phase. It sweeps every pool the project
tracks, not just the single ETH/USDC replication pair.

## Generating script

`liquidity_profile_study.py`. The script reads
`data/processed/liquidity/{PAIR}/{fee}bp_ticks.parquet` (cleaned Uniswap V3 tick data) and
writes under `src/graphics/config.py`'s `CFG.liq_out_dir` (`results/liquidity-pipeline`).

## Sweep dimensions

| Dimension | Source of truth | Values |
|---|---|---|
| pool × fee-tier | `data_extraction/config.py POOLS` | 11 jobs across 5 pairs: WETH_USDC (1/5/30bp), WETH_USDT (1/5/30bp), WBTC_WETH (5/30bp), WBTC_USDT (5/30bp), USDC_USDT (1bp) |
| axis-basis | `_AXES` in `liquidity_profile_study.py` | `log-moneyness`, `relative-ticks`, `absolute-ticks` |

## Directory shape

```
liquidity-pipeline/
├── profile/                     33 files — time-collapsed 2-D shape, per axis
│   ├── log-moneyness/
│   ├── relative-ticks/
│   └── absolute-ticks/
│       └── {fee}bp_{PAIR}.png   one per pool × fee-tier job
├── surface/                     33 files — 3-D log-liquidity surface, per axis
│   ├── log-moneyness/
│   ├── relative-ticks/
│   └── absolute-ticks/
│       └── {fee}bp_{PAIR}.png
└── liquidity-VS-price/          11 files — top-down heatmap, no axis split
    └── {fee}bp_{PAIR}.png
```

`profile/` and `surface/` spread across all 3 axis-bases (33 = 11 jobs × 3 axes each).
`liquidity-VS-price/` stays flat: one file per job, no axis subfolder, because it plots against
absolute price directly and an axis choice does not apply.

Axis-basis meaning:
- `log-moneyness`: re-centred at the block's `curr_tick` (ATM) each block, then
  log-transformed. This re-centring makes different pools and blocks comparable on one axis.
- `relative-ticks`: re-centred at `curr_tick` each block, not log-transformed. Same alignment
  as `log-moneyness`, raw tick units.
- `absolute-ticks`: not re-centred. Real tick/price axis. It shows actual price movement over
  time, at the cost of cross-block comparability.

## File-naming pattern

`{fee}bp_{PAIR}.png`

- `{fee}`: fee tier in basis points (`1`, `5`, `30`), from `POOLS[...]['fee_bps']`.
- `{PAIR}`: pair label matching `POOLS[...]['pair']` (`WETH_USDC`, `WETH_USDT`, `WBTC_WETH`,
  `WBTC_USDT`, `USDC_USDT`). Several fee tiers of one pair share a folder; this stem
  distinguishes them, not a separate subfolder.

## How to read one file

`surface/log-moneyness/5bp_WETH_USDC.png`: the 5bp WETH/USDC pool's log-liquidity surface,
`(time × log-moneyness)`, each block's profile re-centred at that block's spot price. The plot
shows where liquidity concentrates relative to spot and how that concentration shifts over the
sample window.
