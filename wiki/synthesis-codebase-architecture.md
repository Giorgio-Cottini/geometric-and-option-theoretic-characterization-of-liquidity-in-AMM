---
title: Codebase Architecture
layer: core
type: synthesis
origin: thesis
date: 2026-07-22
---

# Thesis Codebase — Structural Architecture (call-graph spine)

A structural synthesis of the thesis's Python implementation, derived from the parked code
graph at `wiki/graphs/code/graph.json` (319 nodes, 605 edges, 18 communities, 100% AST-extracted;
refreshed 2026-07-22 after cycle 2).
Where [[source-thesis-codebase]] narrates *what* each stage computes, this page describes *how the
code is wired* — the runner-to-pipeline-to-math-to-graphics call spine, the structural
load-bearers, and the bridges that tie otherwise separate clusters together. All theory lives in
the prose concept pages; here every claim is anchored to a `graph:NodeId` in the staged graph.

## The three entry points

The codebase has three runner scripts, each orchestrating one part of the framework:

- **`snapshot_study.py`** — the impermanent-loss / implied-volatility study. Its
  `graph:snapshot_study_main` is the highest-betweenness bridge in the whole graph: it calls the
  options snapshot pipeline, then fans out into every graphics entry point
  (`graph:graphics_impermanent_loss_plot_il`, `graph:graphics_impermanent_loss_plot_il_lvr`,
  `graph:graphics_impermanent_loss_plot_il_price_i`, `graph:graphics_implied_volatility_plot_iv`).
  It is why the "IL Price Integrand + Implied Vol Math", "Impermanent Loss Graphics", and "Implied
  Vol Plot" communities are one connected system rather than three islands.
- **`liquidity_profile_study.py`** — the liquidity-surface / LVsP study. Its
  `graph:liquidity_profile_study_main` and `graph:liquidity_profile_study_build_jobs`
  assemble per-pool plot jobs and drive the liquidity graphics. This is the runner behind
  the cycle-1 extension work; the code path it exercises is detailed in
  [[concept-liquidity-pipeline-code]].
- **`price_impact_study.py`** — the marginal price-impact study added in cycle 2.
  `graph:price_impact_study_main` and `graph:price_impact_study_build_jobs` drive the three impact
  plotters over the same pools as the liquidity study, fourteen figures each. The code path is
  detailed in [[concept-price-impact-code]].

Both dataset runners now iterate the pool-keyed configuration rather than a per-pair view, so the
job list is the measured pool universe; see [[concept-pool-selection-code]]. The snapshot runner is
unaffected, since it reads frozen JSON snapshots rather than the historical dataset.

## Four structural layers

The graph resolves into a clean bottom-up dependency stack:

1. **Data extraction** — `data_extraction/download_liquidity_evolution.py`
   (`graph:data_extraction_download_liquidity_evolution_main`) pulls Uniswap V3 ticks and pool
   states over GraphQL. The download community remains the most self-contained cluster in the
   codebase — a deliberate seam between raw I/O and computation. Cycle 2 split two further tight
   clusters out of this layer: pool discovery (`graph:data_extraction_discover_pools_main`, which
   measures which pools and fee tiers actually carry flow over the study window) and dataset
   verification (`graph:data_extraction_verify_dataset_main`, which asserts that every pool sits on
   one identical block grid). Both are read-only and neither is imported by the computation
   layers, so the seam holds in both directions; see [[concept-pool-selection-code]].
2. **Data processing** — two sub-lanes. The snapshot lane
   (`graph:snapshot_liquidity_pipeline_run_liquidity_pipeline`,
   `graph:snapshot_options_pipeline_run_options_pipeline`) reconstructs `ℓ(q)` from ticks and
   filters the options book; the parquet-cleaning lane
   (`graph:liquidity_clean_parquet_clean_parquet`) and block-timestamp utilities
   (`graph:data_processing_fetch_block_timestamps_fetch_block_timestamps`,
   `graph:data_processing_block_timestamps_load_block_timestamps`) prepare the time axis.
3. **math_core** — the numerical heart. `graph:math_core_liquidity_profile_piecewise_constant_liquidity_profile`
   is the single most-connected node in the codebase (15 edges): the piecewise-constant `ℓ(q)`
   every downstream integral and surface consumes. Alongside it,
   `graph:math_core_liquidity_profile_build_liquidity_surface`,
   `graph:math_core_liquidity_vs_price_build_lvsp_surface`,
   `graph:math_core_implied_volatility_compute_bs_implied_vol`, and
   `graph:math_core_implied_volatility_compute_bs_iv_fine_structure` form the computational core.
   Cycle 2 added `graph:math_core_price_impact` beside them, which is a *sibling* rather than an
   extension: `graph:math_core_price_impact_build_impact_surface` calls the frozen liquidity and
   LVsP builders read-only and nothing in those modules points back.
4. **Graphics** — pure sinks. The IL, IV, liquidity, and impact plotters consume math_core outputs
   and write PNGs; no math_core node depends on a graphics node, confirming the one-way
   replication-safe boundary the coding contract requires. The one shared module inside this layer
   is `graph:graphics_labels`, whose `graph:graphics_labels_lm_xlabel` resolves the log-moneyness
   axis label from a pool's orientation for both plotting families, so neither depends on the
   other.

## Cross-community bridges (why the clusters cohere)

- **`graph:snapshot_study_main`** — the master bridge, joining the snapshot pipeline to all three
  IL/IV graphics-and-math communities.
- **`graph:snapshot_options_pipeline_run_options_pipeline`** — bridges the snapshot pipeline to the
  market-proxy interpolation (`graph:math_core_interpolation_linear_interpolation`), the one link
  from raw options data into the closed-form antiderivative machinery.
- **`graph:snapshot_utils_sep`** — a shared console-formatting helper reached from both the pipeline
  and graphics clusters; a low-semantic-value but high-degree utility node.

## Structural observations

- **Weak intra-community cohesion in the largest clusters** (price-impact plotting 0.07, IL
  graphics 0.08, snapshot pipelines 0.10, liquidity plotting 0.14). The graph's own
  suggested-questions flag these as split candidates. In practice the low score reflects wide
  fan-out from a small number of runners rather than tangled coupling — acceptable for a research
  codebase, worth revisiting if these files grow.
- **The tightest clusters are the data-extraction ones** — dataset verification 0.39,
  block-timestamp loading 0.33, LVsP math and plotting 0.29 each, IV plotting 0.28, extraction
  config 0.25. Small, single-purpose modules with few external callers.
- **One 1-file import cycle** in `options_pipeline.py` (self-referential) — benign, an artifact of
  intra-module helper calls, not a genuine dependency cycle.
- **26 isolated nodes** — mostly `ndarray` / `DataFrame` / `Path` type leaves and config constants;
  expected for AST extraction, not documentation gaps.

## Connections

- Narrative companion: [[source-thesis-codebase]] (what each stage computes).
- The liquidity half of the code, in depth: [[concept-liquidity-pipeline-code]].
- The cycle-2 extension lane: [[concept-price-impact-code]], [[concept-marginal-price-impact]].
- The data-extraction lane and the dataset it defines: [[concept-pool-selection-code]],
  [[synthesis-pool-selection-findings]].
- Theory anchors: [[concept-impermanent-loss]], [[concept-loss-versus-rebalancing]],
  [[concept-implied-volatility-surface]], [[concept-concentrated-liquidity]].
- Project map: [[synthesis-thesis-map]].
- Graph unit: `wiki/graphs/code/graph.json`.

## Open questions

- Should the three low-cohesion runner-driven communities be refactored into narrower modules, or
  is the runner-fan-out shape intentional and fine as-is?
- The `options_pipeline.py` self-cycle — worth breaking for clarity, or immaterial?
