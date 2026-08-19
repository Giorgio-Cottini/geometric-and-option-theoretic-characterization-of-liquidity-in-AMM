# `price-impact/`: marginal price-impact profile, surface, and impact-vs-price

This page is filled from `../README.template.md`. It covers 154 files.

## Purpose

The plots show the marginal price impact of a trade against the liquidity surface `L(P, t)`, as
two pointwise transforms: absolute impact `2·P^1.5 / L` and relative impact `2·P^0.5 / L`. This
group shares the sweep and chart-kind shape of `../liquidity-pipeline/`, with one extra split
for the impact quantity. This study is `liquidity_profile_study.py`'s "cycle 2" companion.

## Generating script

`price_impact_study.py`. The script uses the same job list and input parquets as
`liquidity_profile_study.py` (`data/processed/liquidity/{PAIR}/{fee}bp_ticks.parquet`). It
writes under `CFG.impact_out_dir` (`results/price-impact`).

## Sweep dimensions

| Dimension | Source of truth | Values |
|---|---|---|
| pool × fee-tier | `data_extraction/config.py POOLS` | same 11 jobs as `liquidity-pipeline/` |
| impact quantity | `_QDIR` in `price_impact_study.py` | `abs-impact` (absolute), `rel-impact` (relative) |
| axis-basis | `_AXES` in `price_impact_study.py` | `log-moneyness`, `relative-ticks`, `absolute-ticks` |

## Directory shape

```
price-impact/
├── abs-impact/                      77 files — absolute impact, 2·P^1.5 / L
│   ├── profile/                     33 files, per axis
│   │   ├── log-moneyness/
│   │   ├── relative-ticks/
│   │   └── absolute-ticks/
│   │       └── {fee}bp_{PAIR}.png
│   ├── surface/                     33 files, per axis
│   │   ├── log-moneyness/
│   │   ├── relative-ticks/
│   │   └── absolute-ticks/
│   │       └── {fee}bp_{PAIR}.png
│   └── impact-VS-price/             11 files, no axis split
│       └── {fee}bp_{PAIR}.png
└── rel-impact/                      77 files — same layout, relative impact, 2·P^0.5 / L
    ├── profile/...
    ├── surface/...
    └── impact-VS-price/...
```

The `abs-impact` / `rel-impact` split sits above `profile` / `surface` / `impact-VS-price`, one
level deeper than `liquidity-pipeline/`. Here the impact quantity is chosen first, and the
chart-kind/axis-basis structure repeats identically underneath each choice. `impact-VS-price/`
stays flat for the same reason as `liquidity-VS-price/` above: it plots against absolute price
directly, and no axis choice applies.

Axis-basis meaning: identical to `../liquidity-pipeline/README.md` (`log-moneyness`,
`relative-ticks`, `absolute-ticks`: re-centring and log-transform choices, not different data).

## File-naming pattern

`{fee}bp_{PAIR}.png`: identical convention to `../liquidity-pipeline/README.md`. `{fee}` is the
fee tier in basis points, `{PAIR}` is the pool's pair label. The enclosing folders carry the
impact quantity and chart-kind, not the filename, since one job produces one file per folder
combination.

## How to read one file

`abs-impact/surface/absolute-ticks/30bp_WBTC_WETH.png`: the 30bp WBTC/WETH pool's absolute
price-impact surface `(time × absolute tick)`, not re-centred, so actual price movement is
visible on the axis. The plot shows where impact spikes as liquidity thins relative to the
trade size implied by the `P^1.5` scaling.
