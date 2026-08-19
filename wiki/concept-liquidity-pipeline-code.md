---
title: Liquidity Pipeline Code
layer: core
type: concept
origin: thesis
date: 2026-07-22
---

# Liquidity Pipeline (code path)

The end-to-end code path that turns raw Uniswap V3 tick data into liquidity profiles, surfaces, and
the liquidity-versus-price (LVsP) heatmap. This is the structural companion to the liquidity theory
in [[concept-concentrated-liquidity]]: it describes the *modules and calls*, citing the parked graph
(`wiki/graphs/code/graph.json`), not the mathematics. This is the code path the cycle-1 extension
work extended, so it is documented here in its own right.

## Stages

1. **Reconstruction** — `graph:snapshot_liquidity_pipeline_reconstruct_liquidity_cumsum` rebuilds
   the intrinsic liquidity `ℓ(q)` from tick data by cumulative sum, anchored to `ℓ_curr` at the
   current tick; `graph:snapshot_liquidity_pipeline_run_liquidity_pipeline` runs it per fee tier.
2. **Cleaning** — `graph:liquidity_clean_parquet_clean_parquet` preprocesses the raw tick-evolution
   parquet for one pair, applying the same reconstruction logic per block
   (`graph:liquidity_clean_parquet_reconstruct_block`) with a geometric-mean decimal adjustment
   (`graph:liquidity_clean_parquet_decimal_adj`) and tick-to-price conversion
   (`graph:liquidity_clean_parquet_price_from_tick`). The block-timestamp utilities
   (`graph:data_processing_fetch_block_timestamps_fetch_block_timestamps`,
   `graph:data_processing_block_timestamps_load_block_timestamps`) supply the time axis so profiles
   can be stacked chronologically.
3. **Core profile** — `graph:math_core_liquidity_profile_piecewise_constant_liquidity_profile` is the
   piecewise-constant `ℓ(q)` (the codebase's single most-connected node), and
   `graph:math_core_liquidity_profile_build_liquidity_surface` stacks per-block profiles into a
   `(time × log-moneyness)` grid centred at ATM.
4. **LVsP surface** — `graph:math_core_liquidity_vs_price_build_lvsp_surface` builds a dense
   `(time × absolute_tick)` log-liquidity surface, with `graph:math_core_liquidity_vs_price_build_lvsp_surface`
   paired to a tick-window helper for the display range.
5. **Study runner + plotters** — `graph:liquidity_profile_study_main` and
   `graph:liquidity_profile_study_build_jobs` assemble per-pool jobs and drive the
   graphics. Since cycle 2 the job tuple is `(pair, fee_label, tick_spacing, parquet_path,
   invert)` and is built from the pool-keyed configuration rather than a per-pair view, so all
   eleven pools are plotted rather than one tier per pair; see [[concept-pool-selection-code]].

## Cycle-1 extension (2026-07-19)

The graphics layer gained the profile-shape plotter and a three-axis generalization landed in the
extension cycle:

- `graph:graphics_liquidity_profile_plot_liquidity_shape` — collapses the time axis of a surface to
  a single mean ± 1 std log-liquidity curve versus a selectable x-axis, isolating the average
  profile shape from day-to-day level fluctuations. The `axis` parameter selects one of three
  x-axes (log-moneyness, relative ticks, absolute ticks), reusing the same surface builders as the
  3-D plots so each profile lines up with its sibling surface.
- Sibling plotters `graph:graphics_liquidity_profile_plot_liquidity_surface`,
  `graph:graphics_liquidity_profile_plot_liquidity_surface_absolute`, and
  `graph:graphics_liquidity_profile_plot_liq` render the full surfaces.
- Outputs are organized under `tester_results/liquidity-pipeline/{profile,surface}/{axis}/` plus
  `liquidity-VS-price/`. As run in cycle 1 this covered six pair/fee jobs at seven plots each,
  two of them an `ETH_USDC` dataset on a non-standard path; that dataset was found in cycle 2 to
  duplicate `WETH_USDC` on an unaligned block grid and was deleted, and the job list is now the
  eleven measured pools. See the planner ledger for both run records.

## Cycle-2 changes (2026-07-22)

The pipeline itself did not change; what it is run over, and how its axes are named, did.

- **Orientation is now threaded through the plotters.** `plot_liquidity_surface`
  (`graph:graphics_liquidity_profile_plot_liquidity_surface`) and `plot_liquidity_shape`
  (`graph:graphics_liquidity_profile_plot_liquidity_shape`) take a required `invert` argument and
  resolve their log-moneyness label through `graph:graphics_labels_lm_xlabel` instead of hardcoding
  `log(K/S)`. The argument is required rather than defaulted precisely so that no new call site can
  silently inherit the wrong frame. This is a relabel with zero numerical change; the reasoning is
  in [[concept-marginal-price-impact]].
- **Every materially traded fee tier is now plotted**, eleven pools rather than four, all on one
  identical block grid. The 1bp tier gained its own spatial window so that its far finer tick
  spacing lands on the same log-moneyness half-width as the coarser tiers.
- **The calendar-date time axis is populated again**, since the block-timestamp table was
  regenerated for the expanded pool set.

## Structural notes

- The reconstruction logic is deliberately duplicated between the snapshot pipeline (live ticks) and
  the parquet-cleaning lane (persisted evolution) — the same `ℓ(q)` cumulative-sum rule applied to
  two different data sources. This is intentional, not drift; both must stay in step if the
  reconstruction rule changes.
- This liquidity path is one of the two runner-driven halves of the codebase; the other (IL / IV)
  and the overall wiring are in [[synthesis-codebase-architecture]].

## Connections

- Theory: [[concept-concentrated-liquidity]], [[concept-bonding-curve]].
- The transform built on this surface: [[concept-price-impact-code]],
  [[concept-marginal-price-impact]].
- Which pools it runs over: [[concept-pool-selection-code]], [[synthesis-pool-selection-findings]].
- Structural overview: [[synthesis-codebase-architecture]].
- Codebase narrative: [[source-thesis-codebase]].
- Graph unit: `wiki/graphs/code/graph.json`.
