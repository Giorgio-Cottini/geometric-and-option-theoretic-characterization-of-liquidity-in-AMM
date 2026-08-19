# Graph Report - .  (2026-07-22)

## Corpus Check
- 16 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 319 nodes · 605 edges · 18 communities
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Price-Impact Plotting
- Impermanent-Loss Plotting
- Snapshot Liquidity Pipeline
- Liquidity-Profile Plotting
- Implied Volatility Math
- Tick Data Download
- Pool Discovery
- Parquet Cleaning
- Block Timestamp Fetching
- Extraction Config and Block Grid
- IV Surface Plotting
- Dataset Verification
- LVsP Surface Math
- LVsP Plotting
- Block Timestamp Loading

## God Nodes (most connected - your core abstractions)
1. `piecewise_constant_liquidity_profile()` - 15 edges
2. `main()` - 14 edges
3. `plot_impact_surface()` - 14 edges
4. `plot_impact_profile()` - 13 edges
5. `build_impact_surface()` - 13 edges
6. `plot_impact_heatmap()` - 12 edges
7. `run_options_pipeline()` - 11 edges
8. `plot_IL_LVR()` - 11 edges
9. `plot_IL_price_I()` - 11 edges
10. `ndarray` - 11 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `plot_IL()`  [EXTRACTED]
  snapshot_study.py → src/graphics/impermanent_loss.py
- `main()` --calls--> `plot_IL_LVR()`  [EXTRACTED]
  snapshot_study.py → src/graphics/impermanent_loss.py
- `main()` --calls--> `plot_IL_price()`  [EXTRACTED]
  snapshot_study.py → src/graphics/impermanent_loss.py
- `main()` --calls--> `plot_IL_price_I()`  [EXTRACTED]
  snapshot_study.py → src/graphics/impermanent_loss.py
- `main()` --calls--> `plot_iv()`  [EXTRACTED]
  snapshot_study.py → src/graphics/implied_volatility.py

## Import Cycles
- 1-file cycle: `src/data_processing/snapshot/options_pipeline.py -> src/data_processing/snapshot/options_pipeline.py`

## Communities (18 total, 0 thin omitted)

### Community 0 - "Price-Impact Plotting"
Cohesion: 0.07
Nodes (54): lm_xlabel(), Axis labels shared by the liquidity and price-impact plotters.  Both families, Log-moneyness axis label for a pool of the given orientation., _cbar_label(), _impact_surface_for_axis(), plot_impact_heatmap(), plot_impact_profile(), plot_impact_surface() (+46 more)

### Community 1 - "Impermanent-Loss Plotting"
Cohesion: 0.08
Nodes (49): _make_PT_grid(), plot_IL(), plot_IL_LVR(), plot_IL_price(), plot_IL_price_I(), Graphics for Impermanent Loss (IL) and the IL replication price integrand.  Publ, Plot the IL price integrand L(q)·O(q) vs log(q / F) for one fee tier.      The a, Plot pathwise IL(P_T) decomposed into LVR and hedging cost components.      Deco (+41 more)

### Community 2 - "Snapshot Liquidity Pipeline"
Cohesion: 0.10
Nodes (32): datetime, linear_interpolation(), Build piecewise-affine market proxy O^mkt(K) for each option type via linear int, Config, Reconstruct ℓ(q) from ticks using cumulative sum, anchored to ℓ_curr at curr_tic, Reconstruct ℓ(q) for one fee tier.     Returns the DataFrame from reconstruct_l, reconstruct_liquidity_cumsum(), run_liquidity_pipeline() (+24 more)

### Community 3 - "Liquidity-Profile Plotting"
Cohesion: 0.14
Nodes (23): Config, _apply_month_ticks_3d(), _draw_liq_step(), plot_liq(), plot_liquidity_shape(), plot_liquidity_surface(), plot_liquidity_surface_absolute(), Graphics for the piecewise-constant liquidity profile ℓ(P_T).  Public API --- (+15 more)

### Community 4 - "Implied Volatility Math"
Cohesion: 0.14
Nodes (25): _bisection_iv(), _bs_d1(), _bs_il_price(), _bs_il_vega(), _bs_price(), _bs_vega(), compute_BS_implied_vol(), compute_BS_iv_fine_structure() (+17 more)

### Community 5 - "Tick Data Download"
Cohesion: 0.24
Nodes (18): _blocks_present(), _download_pool(), _download_pool_states(), _download_ticks(), fetch_latest_block(), fetch_pool_state(), fetch_ticks(), graphql() (+10 more)

### Community 6 - "Pool Discovery"
Cohesion: 0.16
Nodes (17): Any, block_to_unix(), fetch_chain_anchor(), fetch_pools(), fetch_window_stats(), _fmt_usd(), load_block_grid(), main() (+9 more)

### Community 7 - "Parquet Cleaning"
Cohesion: 0.17
Nodes (14): clean_parquet(), _decimal_adj(), _dirs(), _price_from_tick(), clean_parquet.py ---------------- Preprocesses raw Uniswap V3 tick evolution p, Apply reconstruct_liquidity_cumsum logic to one block's tick data using the, Preprocess the raw tick evolution parquet for one pool and write the     cleane, Return (raw_dir, processed_dir) for the given pair label. (+6 more)

### Community 8 - "Block Timestamp Fetching"
Cohesion: 0.24
Nodes (10): _collect_block_numbers(), _fetch_batch(), fetch_block_timestamps(), fetch_block_timestamps.py ------------------------- Fetches Ethereum block tim, Fetch and persist block → UTC timestamp mapping for all known blocks.      Rea, Collect all unique block numbers from pool_states parquets across every     poo, Fetch block timestamps for one batch via a single JSON-RPC batch request., Session (+2 more)

### Community 9 - "Extraction Config and Block Grid"
Cohesion: 0.25
Nodes (8): load_block_grid(), out_dir(), processed_dir(), Path, config.py --------- Configuration for the multi-pool liquidity evolution downl, The shared block grid, recovered from the existing download.      Returns 1641, Raw output directory for a given pair label (e.g. 'WETH_USDC')., Processed output directory for a given pair label.

### Community 10 - "IV Surface Plotting"
Cohesion: 0.28
Nodes (8): plot_iv(), Graphics for Black-Scholes implied volatility fine structure.  Public API ------, Create parent directories, save figure, close it, and print confirmation., Plot per-tick BS implied volatility vs log(K / F) for one fee tier.      Each ti, _save_figure(), DataFrame, Figure, Path

### Community 11 - "Dataset Verification"
Cohesion: 0.39
Nodes (7): _check_pool(), _find_orphans(), main(), _processed_path(), verify_dataset.py ----------------- Read-only integrity check over the process, Return a list of failure strings for one pool — empty means it passed., Processed parquets on disk that no config.POOLS entry claims.

### Community 12 - "LVsP Surface Math"
Cohesion: 0.29
Nodes (7): build_lvsp_surface(), compute_tick_window(), Math functions for the LVsP (Liquidity vs Price) heatmap.  Public API ----------, Compute the absolute tick display window for the LVsP plot.      Window = [a - (, Build a dense 2D log-liquidity surface in absolute tick × time space.      Unlik, DataFrame, ndarray

### Community 13 - "LVsP Plotting"
Cohesion: 0.29
Nodes (6): plot_lvsp(), LvsP — Liquidity vs Price 2D heatmap.  Public API ---------- plot_lvsp(df, fee_l, Plot the LvsP (Liquidity vs Price) 2D heatmap for one fee tier.      Top-down vi, DataFrame, Path, Series

### Community 14 - "Block Timestamp Loading"
Cohesion: 0.33
Nodes (5): load_block_timestamps(), block_timestamps.py ------------------- Loader utility for the persisted block →, Load the block → UTC timestamp lookup as a pd.Series.      Args:         path :, Path, Series

## Knowledge Gaps
- **26 isolated node(s):** `Path`, `Series`, `Config`, `ndarray`, `Figure` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `Snapshot Liquidity Pipeline` to `Impermanent-Loss Plotting`, `IV Surface Plotting`, `Implied Volatility Math`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `_sep()` connect `Snapshot Liquidity Pipeline` to `Impermanent-Loss Plotting`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **What connects `Execution order (mirrors section 5 of the paper):    Liquidity sub-pipeline:`, `Run the full RTW26 replication pipeline for multiple expiries.      Args:`, `Path` to the rest of the system?**
  _140 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Price-Impact Plotting` be split into smaller, more focused modules?**
  _Cohesion score 0.06666666666666667 - nodes in this community are weakly interconnected._
- **Should `Impermanent-Loss Plotting` be split into smaller, more focused modules?**
  _Cohesion score 0.08245981830887492 - nodes in this community are weakly interconnected._
- **Should `Snapshot Liquidity Pipeline` be split into smaller, more focused modules?**
  _Cohesion score 0.09581646423751687 - nodes in this community are weakly interconnected._
- **Should `Liquidity-Profile Plotting` be split into smaller, more focused modules?**
  _Cohesion score 0.1396011396011396 - nodes in this community are weakly interconnected._