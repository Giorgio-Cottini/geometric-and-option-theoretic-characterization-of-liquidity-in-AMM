"""
LvsP — Liquidity vs Price 2D heatmap.

Public API
----------
plot_lvsp(df, fee_label, tick_spacing, out_dir, n_time_samples)
    Top-down log-liquidity heatmap (time × absolute tick) with spot-price overlay.
    Saved as {out_dir}/{fee_label}_LvsP.png
"""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import CFG
from ..math_core.liquidity_vs_price import compute_tick_window, build_lvsp_surface


def plot_lvsp(
    df: pd.DataFrame,
    pair: str,
    fee_label: str,
    tick_spacing: int,
    out_path: Path,
    n_time_samples: int = 200,
    block_ts: pd.Series | None = None,
) -> None:
    """
    Plot the LvsP (Liquidity vs Price) 2D heatmap for one fee tier.

    Top-down view: x-axis = time, y-axis = absolute tick, colour =
    log(liquidity) in magma colormap. The pool spot price (curr_tick) is
    overlaid as a black line.

    The y-axis window [tick_lower, tick_upper] is derived from the data's
    actual curr_tick range, expanded by CFG.ZOOM:
        tick_lower = min(curr_tick) - spread * ZOOM
        tick_upper = max(curr_tick) + spread * ZOOM
    where spread = max(curr_tick) - min(curr_tick).

    Args:
        df             : processed parquet DataFrame with columns
                         [block_number, tick_idx, liquidity, curr_tick].
        fee_label      : short label used in title and filename, e.g. "5bp".
        tick_spacing   : fee-tier tick spacing (10 for 5bp, 60 for 30bp).
        out_dir        : output directory. None → CFG.liq_out_dir.
        n_time_samples : number of time slices retained after downsampling.
        block_ts       : optional pd.Series[Timestamp, tz=UTC] indexed by
                         block_number (from load_block_timestamps()).  When
                         provided, the X (time) axis shows calendar month
                         ticks instead of the normalised [0, 1] range.
    Saves:
        {out_dir}/{fee_label}_LvsP.png
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tick_lower, tick_upper = compute_tick_window(
        df["curr_tick"].to_numpy(dtype=np.int64), CFG.ZOOM
    )

    abs_tick_grid, times, log_liq, curr_ticks_sampled, sampled_blocks = (
        build_lvsp_surface(df, tick_lower, tick_upper, tick_spacing, n_time_samples)
    )

    # ── Choose time axis values ───────────────────────────────────────────────
    # When block_ts is provided, convert sampled block numbers to matplotlib
    # date floats (days since the matplotlib epoch) so that MonthLocator works
    # natively.  Otherwise fall back to the normalised [0, 1] representation.
    if block_ts is not None:
        ts_arr = pd.DatetimeIndex(block_ts.loc[sampled_blocks].values)
        times_x: np.ndarray = mdates.date2num(ts_arr)
        use_dates = True
    else:
        times_x = times
        use_dates = False

    fig, ax = plt.subplots(figsize=(12, 6))

    # pcolormesh expects (n_y, n_x) → transpose log_liq from (n_time, n_ticks)
    mesh = ax.pcolormesh(
        times_x,
        abs_tick_grid,
        np.ma.masked_invalid(log_liq.T),
        cmap="magma",
        shading="auto",
    )

    ax.plot(
        times_x,
        curr_ticks_sampled,
        color="black",
        linewidth=1.0,
        label="Spot price (curr_tick)",
    )

    if use_dates:
        ax.xaxis_date()
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)
        ax.set_xlabel("Month")
    else:
        ax.set_xlabel("Time")

    cbar = fig.colorbar(mesh, ax=ax, pad=0.02)
    cbar.set_label("log(Liquidity)")

    ax.set_ylabel("Tick")
    ax.set_title(f"Liquidity vs Price — {pair} {fee_label}")
    ax.legend(fontsize=8, loc="upper left")

    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [saved] {out_path}")
