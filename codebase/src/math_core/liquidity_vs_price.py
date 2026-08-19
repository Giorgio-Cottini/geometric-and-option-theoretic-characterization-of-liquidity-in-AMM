"""
Math functions for the LVsP (Liquidity vs Price) heatmap.

Public API
----------
compute_tick_window(curr_ticks, zoom) -> (tick_lower, tick_upper)
build_lvsp_surface(df, tick_lower, tick_upper, tick_spacing, n_time_samples)
    -> (abs_tick_grid, times, log_liq, curr_ticks_out)
"""

import numpy as np
import pandas as pd


def compute_tick_window(
    curr_ticks: np.ndarray,
    zoom: float,
) -> tuple[int, int]:
    """
    Compute the absolute tick display window for the LVsP plot.

    Window = [a - (b-a)*zoom, b + (b-a)*zoom]
    where a = min(curr_ticks), b = max(curr_ticks).

    Args:
        curr_ticks : 1-D int array of pool slot0 tick values across all blocks.
        zoom       : multiplicative expansion factor (e.g. 1.1 adds 10% padding).
    Returns:
        tick_lower, tick_upper : integer tick bounds (inclusive).
    """
    a = int(curr_ticks.min())
    b = int(curr_ticks.max())
    spread = b - a
    tick_lower = int(np.floor(a - spread * zoom))
    tick_upper = int(np.ceil(b + spread * zoom))
    return tick_lower, tick_upper


def build_lvsp_surface(
    df: pd.DataFrame,
    tick_lower: int,
    tick_upper: int,
    tick_spacing: int,
    n_time_samples: int = 200,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Build a dense 2D log-liquidity surface in absolute tick × time space.

    Unlike build_liquidity_surface, the column axis is absolute tick index,
    not relative to curr_tick. Because initialized ticks are always multiples
    of tick_spacing, the grid aligns exactly with the data for every block —
    there is no curr_tick-drift misalignment and no interior NaN.

    Args:
        df             : processed parquet DataFrame with columns
                         [block_number, tick_idx, liquidity, curr_tick].
        tick_lower     : lower absolute tick bound (inclusive).
        tick_upper     : upper absolute tick bound (inclusive).
        tick_spacing   : fee-tier tick spacing (10 for 5bp, 60 for 30bp).
        n_time_samples : number of evenly-spaced time slices to retain.
    Returns:
        abs_tick_grid  : 1-D int64 array of absolute tick values (y-axis).
        times          : 1-D float64 array of normalized block numbers in [0, 1].
        log_liq        : 2-D float64 array (n_time × n_ticks) of ln(liquidity).
                         NaN where no LP position covers that tick.
        curr_ticks_out : 1-D int64 array of pool curr_tick per sampled block,
                         used to draw the spot-price line overlay.
        sampled_blocks : 1-D int64 array of the Ethereum block numbers
                         corresponding to each row of log_liq / times.  Pass
                         this together with a block → timestamp Series to the
                         plot functions to enable calendar-month axis labels.
    """
    # Fixed absolute tick grid — same for every block, no curr_tick dependence.
    abs_tick_grid = np.arange(tick_lower, tick_upper + 1, tick_spacing, dtype=np.int64)
    N_GRID = len(abs_tick_grid)

    curr_tick_map = df.groupby("block_number")["curr_tick"].first()

    # ── Downsample block list ─────────────────────────────────────────────────
    all_blocks = np.sort(curr_tick_map.index.to_numpy())
    n_blocks = len(all_blocks)
    if n_blocks > n_time_samples:
        step = n_blocks / n_time_samples
        keep_idx = np.unique(np.round(np.arange(0, n_blocks, step)).astype(int))
        keep_idx = keep_idx[keep_idx < n_blocks]
        sampled_blocks = all_blocks[keep_idx]
    else:
        sampled_blocks = all_blocks

    blocks_f = sampled_blocks.astype(float)
    times = (blocks_f - blocks_f.min()) / (blocks_f.max() - blocks_f.min())

    # ── Build dense surface row by row ────────────────────────────────────────
    rows: list[np.ndarray] = []
    curr_ticks_out: list[int] = []

    for block in sampled_blocks:
        curr_tick = int(curr_tick_map.loc[block])
        curr_ticks_out.append(curr_tick)

        blk = df.loc[
            df["block_number"] == block, ["tick_idx", "liquidity"]
        ].sort_values("tick_idx")

        # ± one tick_spacing slack ensures boundary bins are captured.
        blk = blk[
            (blk["tick_idx"] >= tick_lower - tick_spacing)
            & (blk["tick_idx"] <= tick_upper + tick_spacing)
        ]

        if blk.empty:
            rows.append(np.full(N_GRID, np.nan))
            continue

        tick_array = blk["tick_idx"].to_numpy(dtype=np.int64)
        liq_array = blk["liquidity"].to_numpy(dtype=np.float64)

        # Piecewise-constant lookup: find the last initialized tick ≤ each
        # grid point.  searchsorted side="right" then -1 gives the active bin.
        i = np.searchsorted(tick_array, abs_tick_grid, side="right") - 1
        valid = (i >= 0) & (i < len(tick_array))
        row = np.where(valid, liq_array[np.clip(i, 0, len(tick_array) - 1)], np.nan)
        row = np.where(row > 0, row, np.nan)   # guard against zero/negative ℓ
        rows.append(row)

    liq_values = np.vstack(rows)               # (n_time, N_GRID)
    log_liq = np.log(liq_values)              # NaN propagates

    return (
        abs_tick_grid,
        times,
        log_liq,
        np.array(curr_ticks_out, dtype=np.int64),
        sampled_blocks,
    )
