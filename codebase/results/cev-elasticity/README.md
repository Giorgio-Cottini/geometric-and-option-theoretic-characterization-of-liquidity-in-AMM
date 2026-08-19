# `cev-elasticity/`: shape diagnostic for the CEV elasticity of the liquidity profile

This page is filled from `../README.template.md`. It covers 27 files under `diagnostic/`: 22
PNGs and 5 CSVs.

## Purpose

The plots and tables test one question — does the observed liquidity profile behave like the
power law of RTW26 Example 3.3 over any contiguous band of price around spot — and, if so, fix
the headline band half-width `w` that cycles R2 through R5 use downstream. This is cycle 3, R1.

## Generating script

`cev_elasticity_study.py`. It reads the same processed parquets as `price_impact_study.py`
(`data/processed/liquidity/{PAIR}/{fee}bp_ticks.parquet`) and the same 11-job list from
`data_extraction/config.py POOLS`. It writes under `CFG.cev_out_dir / "diagnostic"`
(`results/cev-elasticity/diagnostic`).

## Sweep dimensions

| Dimension | Source of truth | Values |
|---|---|---|
| pool × fee-tier | `data_extraction/config.py POOLS` | same 11 jobs as `../price-impact/` and `../liquidity-pipeline/` |
| band half-width `w` | `W_GRID` in `src/math_core/cev_elasticity.py` | `0.02, 0.05, 0.10, 0.15, 0.22, 0.35, 0.50` (log-moneyness) |
| branch | `BRANCHES` in `src/math_core/cev_elasticity.py` | `below`, `above` spot — fit separately, never averaged (spec convention C5) |

Unlike `../price-impact/` and `../liquidity-pipeline/`, this group has no axis-basis or
chart-kind split: every pool gets exactly one band-dependence plot and one local-slope plot, and
the `w` / branch sweep lives inside the CSVs, not the directory structure.

## Directory shape

```
cev-elasticity/
└── diagnostic/                          27 files, flat — one job, two plots, no axis split
    ├── {fee}bp_{PAIR}_band-dependence.png   11 files — beta_shape vs w, per pool
    ├── {fee}bp_{PAIR}_local-slope.png       11 files — local d log L / d log q vs log-moneyness, per pool
    ├── band_sweep.csv                       one row per (pool, block, w, branch)
    ├── coverage.csv                         one row per (pool, w, branch) — the C7 gate material
    ├── full_support_fit.csv                 one row per (pool, block) — the unrestricted fit, kept only to document it is unusable
    ├── headline_w.csv                       the C7 verdict and which pools qualify at each w
    └── local_slope.csv                      one row per (pool, x_centre)
```

Every job produces exactly two PNGs directly under `diagnostic/`; there is no per-chart-kind or
per-axis subfolder, because this diagnostic only asks one question per pool. The five CSVs are
the audit trail behind the plots — each PNG is a rendering of one or two of these tables,
per pool.

## File-naming pattern

`{fee}bp_{PAIR}_{plot}.png`, `plot ∈ {band-dependence, local-slope}`. Identical `{fee}` / `{PAIR}`
convention to `../price-impact/README.md` and `../liquidity-pipeline/README.md`. The CSVs carry
no per-pool filename split — all 11 pools stack into the same file, distinguished by the `pool`
column (`{fee}bp_{PAIR}`, for example `5bp_WETH_USDC`).

## How to read one file

`5bp_WETH_USDC_band-dependence.png`: the 5bp WETH/USDC pool's fitted shape elasticity
`beta_shape = -slope/2` against band half-width `w`, one line per branch (below spot, above
spot), with the branch's interquartile range across snapshots shaded around the median. A flat
line at `beta_shape = 1` (the green dashed reference, the variance-swap case) would mean the
profile has no characteristic scale over that stretch of `w`; a line that slopes away from it
says the power-law family stops describing the pool once the band widens or narrows past that
point.

`5bp_WETH_USDC_local-slope.png` shows the companion view: the time-averaged local slope
`d log L / d log q`, evaluated in a rolling `+/- 0.02` window centred at each point of
`log(K / S)` (`X_LABEL` in `src/math_core/profile_measure.py`), with its cross-snapshot
interquartile band shaded. The dashed line at `slope = -2` is the same `beta_shape = 1`
reference restated on the slope axis. Where the median line sits relative to that dashed line,
and how far the band extends before the fit runs out of surviving ticks on either side of
`log-moneyness = 0`, is the peak-position and monotone-region read.

`coverage.csv` and `headline_w.csv` are read together, not separately: `coverage.csv` carries the
`n_ticks_p5` floor check per `(pool, w, branch)` (spec convention C7 — at least 10 distinct
surviving ticks in at least 95% of snapshots), and `headline_w.csv` lists, for every `w` in the
grid, which pools clear that floor on both branches. A pool absent from `headline_w.csv`
altogether never clears the floor at any `w` in the grid; the current run has no `w` that every
one of the 11 pools clears, so the C7 headline column is empty and the qualifying set must be
read per-`w` from this file rather than as a single verdict.
