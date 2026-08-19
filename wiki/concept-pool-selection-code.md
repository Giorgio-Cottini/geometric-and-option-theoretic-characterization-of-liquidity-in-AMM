---
title: Pool Selection Code
layer: core
type: concept
origin: thesis
date: 2026-07-22
---

# Pool Selection and Dataset Integrity (code path)

The data-extraction lane rebuilt in cycle 2: which Uniswap V3 pools the study runs over, how that
set was measured rather than assumed, and what asserts that the resulting dataset is internally
comparable. This page describes the *modules and calls*, citing the parked graph
(`wiki/graphs/code/graph.json`); what the measurement actually found is in
[[synthesis-pool-selection-findings]].

## Three modules, one contract

**Discovery — `data_extraction/discover_pools.py`** (`graph:data_extraction_discover_pools`).
Exploratory, read-only; it prints a report and writes nothing.
`graph:data_extraction_discover_pools_fetch_pools` enumerates every pool the subgraph knows for
each candidate pair across both on-chain token orderings, and
`graph:data_extraction_discover_pools_fetch_window_stats` aggregates `poolDayDatas` **over the
existing block grid** rather than over pool lifetime. That distinction is the point of the module:
`Pool.volumeUSD` is cumulative since deployment, so a tier that dominated in 2021 would outrank a
currently dominant one. `graph:data_extraction_discover_pools_load_block_grid` reads the grid back
from the stored download, `graph:data_extraction_discover_pools_fetch_chain_anchor` and
`graph:data_extraction_discover_pools_block_to_unix` convert block numbers to the timestamps the
day-level query needs, and `graph:data_extraction_discover_pools_report_pair` prints per-tier
volume share, cumulative share, and TVL share so the cut point is visible instead of applied from
a threshold chosen in advance.

**Configuration — `data_extraction/config.py`** (`graph:data_extraction_config`). The result of
discovery, frozen as data. `POOLS` is keyed per pool as `"{PAIR}@{fee}bp"`, not per pair, because
the fee tiers of one pair are not interchangeable and the within-pair contrast is part of the
thesis's subject. Each entry carries the pool address, fee tier, both token decimals, the
`invert_price` orientation flag, and the measured `volume_share_pct`. Tick spacing is derived from
the fee tier through `TICK_SPACING_BY_FEE_BPS` rather than hand-written; the previous hardcoded
`10` was correct only because every configured pool happened to be 5bp.
`graph:data_extraction_config_load_block_grid` recovers the shared block grid from the existing
download and never recomputes it, which is what makes grid alignment structural rather than
incidental. `graph:data_extraction_config_out_dir` and
`graph:data_extraction_config_processed_dir` give the per-pair folder layout; several tiers of one
pair share a folder and are distinguished by file basename.

**Verification — `data_extraction/verify_dataset.py`** (`graph:data_extraction_verify_dataset`).
Read-only, exits non-zero on failure. `graph:data_extraction_verify_dataset_check_pool` asserts
four properties per pool: grid identity (each pool's block set is *identical* to the reference
grid, not merely a subset or the same length), completeness, sanity (non-empty, finite
non-negative liquidity, one `curr_tick` per block, positive prices with lower not exceeding
upper), and, via `graph:data_extraction_verify_dataset_find_orphans`, that no processed parquet
exists which `POOLS` does not name. The orphan check is what catches superseded tiers left behind
on disk after a selection change. Nothing else in the pipeline asserts the same-grid property,
which is precisely the property that makes surfaces comparable across pairs and across tiers of
one pair.

## Consumers

Every downstream consumer now iterates `POOLS`. The transitional per-pair `PAIRS` view was deleted
rather than kept as a shim, because it selected each pair's highest-volume tier by argmax, which is
a live selection policy hiding in a compatibility layer: it fixed one pool but silently re-pointed
another as a side effect, and would move again whenever volume shares shifted. The consumers are
`graph:data_extraction_download_liquidity_evolution_main` (the downloader),
`graph:data_processing_fetch_block_timestamps_fetch_block_timestamps` (the time axis),
`graph:price_impact_study_build_jobs`, and the liquidity study's job builder. Each job tuple now
carries the pool's `invert` flag through to the plotters, so no call site can inherit the wrong
orientation.

## Structural notes

- Discovery, configuration, and verification form three separate small communities in the graph
  ("Pool Discovery" 17 nodes, "Extraction Config and Block Grid" 8 nodes, "Dataset Verification"
  7 nodes), with cohesion 0.16, 0.25, and 0.39 respectively — the tightest clusters in the
  codebase after the download lane. The seam between measuring the universe, declaring it, and
  checking it is real, not incidental.
- Discovery and configuration each define their own `load_block_grid()`
  (`graph:data_extraction_discover_pools_load_block_grid`,
  `graph:data_extraction_config_load_block_grid`). Discovery is deliberately standalone so it can
  run before the configuration it will later justify.

## Connections

- What discovery measured, and the defects it exposed: [[synthesis-pool-selection-findings]].
- Downstream of the selection: [[concept-liquidity-pipeline-code]], [[concept-price-impact-code]].
- Pool mechanics: [[concept-uniswap-v3-ticks]], [[concept-concentrated-liquidity]].
- Structural overview: [[synthesis-codebase-architecture]].
- Codebase narrative: [[source-thesis-codebase]].
- Graph unit: `wiki/graphs/code/graph.json`.
