---
title: Price Impact Code
layer: core
type: concept
origin: thesis
date: 2026-07-22
---

# Marginal Price Impact (code path)

The extension lane added in cycle 2: a sibling of the frozen liquidity builders that turns the
historical liquidity surface `L(P, t)` into two marginal price-impact surfaces and renders them
across the same plot forms. This page describes the *modules and calls*, citing the parked graph
(`wiki/graphs/code/graph.json`); the quantity itself and what the figures show are in
[[concept-marginal-price-impact]].

## The two modules

**`src/math_core/price_impact.py`** (`graph:math_core_price_impact`) holds the mathematics:

- `graph:math_core_price_impact_impact_from_pl` — the elementwise transform. Absolute impact is
  `2 · P^1.5 / L`, relative impact is `2 · P^0.5 / L`. `NaN` in `L` (liquidity absent at that
  price and time) propagates to `NaN` impact; `P` is always defined.
- `graph:math_core_price_impact_build_impact_surface` — the surface builder. It *calls* the frozen
  `graph:math_core_liquidity_profile_build_liquidity_surface` and
  `graph:math_core_liquidity_vs_price_build_lvsp_surface` read-only, recovers `L` as
  `exp(log_liq)`, computes `P` per cell through
  `graph:liquidity_clean_parquet_price_from_tick`, and returns `log10` of the impact together
  with the axis, times, current ticks, and sampled blocks.
- `graph:math_core_price_impact_impact_units` — splits a `BASE_QUOTE` pair label into the
  `(quote, base)` token pair that names the units of the plotted quantity.

**`src/graphics/price_impact.py`** (`graph:graphics_price_impact`) holds the rendering:
`graph:graphics_price_impact_plot_impact_profile`,
`graph:graphics_price_impact_plot_impact_surface`, and
`graph:graphics_price_impact_plot_impact_heatmap`, sharing the axis helper
`graph:graphics_price_impact_impact_surface_for_axis` and the two label helpers
`graph:graphics_price_impact_cbar_label` (which names the trade denominator) and
`graph:graphics_price_impact_xlabel` (which delegates the log-moneyness case to
`graph:graphics_labels_lm_xlabel`).

The runner `graph:price_impact_study` assembles jobs in
`graph:price_impact_study_build_jobs` and drives the plotters from
`graph:price_impact_study_main`, producing fourteen figures per pool: two quantities
(absolute, relative) times three forms (profile, surface, heatmap) times the tick axes each form
supports.

## Why it is a sibling, not an edit

The replication code is frozen by the project's coding contract, so the impact lane was built to
call the existing builders rather than extend them. In the graph this shows as a one-way
dependency: `graph:math_core_price_impact_build_impact_surface` points into the liquidity and
LVsP builders, and nothing in those modules points back. The only edits to existing files were
additive: three exports in the graphics package and one output-directory entry in
`graph:graphics_config`.

Structurally the lane now dominates the connectivity ranking. Three of the graph's six most
connected nodes are the impact plotters, and `graph:math_core_price_impact_build_impact_surface`
sits just behind them, because each plotter reaches the builder, the label helpers, and the shared
axis helper. The "Price-Impact Plotting" community is the largest in the codebase at 54 nodes,
with a low cohesion score of 0.07 that reflects wide fan-out from a small number of entry points
rather than tangled coupling.

## The shared label module

`src/graphics/labels.py` (`graph:graphics_labels`) exists because both plotting families need the
same decision. `graph:graphics_labels_lm_xlabel` resolves the log-moneyness axis label from the
pool's `invert` orientation; the reasoning is in [[concept-marginal-price-impact]]. It is a small
module rather than a cross-import between sibling plot modules, so neither plotting family depends
on the other.

## Test coverage

`graph:tests_test_price_impact` carries the numeric contract:
`graph:tests_test_price_impact_test_impact_from_pl_values`,
`graph:tests_test_price_impact_test_reciprocal_ratio_equals_p`,
`graph:tests_test_price_impact_test_absolute_over_relative_recovers_p`,
`graph:tests_test_price_impact_test_surface_mask_matches_liquidity`,
`graph:tests_test_price_impact_test_inverted_pool_price_convention` (the suite's first numeric
coverage of an `invert=True` pool),
`graph:tests_test_price_impact_test_base_token_is_the_impact_denominator`, and
`graph:tests_test_price_impact_test_lm_xlabel_follows_orientation`. Job assembly is covered
separately by `graph:tests_test_price_impact_study`. The suite is standalone, without pytest.

## Connections

- The quantity and the empirical reading: [[concept-marginal-price-impact]].
- The liquidity surface it transforms: [[concept-liquidity-pipeline-code]], [[concept-liquidity-surface]].
- Which pools it runs over: [[concept-pool-selection-code]].
- Structural overview: [[synthesis-codebase-architecture]].
- Codebase narrative: [[source-thesis-codebase]].
- Graph unit: `wiki/graphs/code/graph.json`.
