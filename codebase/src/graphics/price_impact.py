"""
Graphics for the marginal price-impact surfaces (cycle 2).

Sibling of graphics/liquidity_profile.py + graphics/liquidity_vs_price.py: same
magma colormap, month-tick handling, and three plot forms — but the plotted
quantity is log10(marginal price impact) instead of log(liquidity).

Public API
----------
plot_impact_profile  — time-collapsed mean ±1 std of log10(impact) vs x-axis.
plot_impact_surface  — 3-D log10(impact) surface (3 selectable x-axes).
plot_impact_heatmap  — top-down (absolute-tick × time) heatmap with spot overlay.
"""
import warnings
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3D projection

from .config import CFG
from .labels import lm_xlabel
from .liquidity_profile import _apply_month_ticks_3d
from ..math_core.liquidity_vs_price import compute_tick_window
from ..math_core.price_impact import build_impact_surface, impact_units

# Human labels keyed by quantity.
_QTITLE = {"absolute": "Absolute", "relative": "Relative"}
# Only the orientation-independent axes live here; log-moneyness is resolved
# through labels.lm_xlabel, which needs the pool's `invert` flag.
_XLABEL = {
    "relative-ticks": "Relative Tick",
    "absolute-ticks": "Absolute Tick",
}


def _xlabel(axis: str, invert: bool) -> str:
    """x-axis label; the log-moneyness label depends on the pool's orientation."""
    if axis == "log-moneyness":
        return lm_xlabel(invert)
    return _XLABEL[axis]


def _cbar_label(quantity: str, pair: str) -> str:
    """Value-axis label naming the trade denominator (always the base token)."""
    quote, base = impact_units(pair)
    if quantity == "absolute":
        return f"log10(Δ({quote}/{base}) per {base})"
    return f"log10(Δln P per {base})"


def _impact_surface_for_axis(
    df: pd.DataFrame,
    tick_spacing: int,
    fee_label: str,
    quantity: str,
    d0: int,
    d1: int,
    invert: bool,
    axis: str,
    n_time_samples: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Dispatch build_impact_surface with the axis-appropriate tick geometry
    (mirrors how the liquidity plotters derive tick_radius / tick window)."""
    if axis in ("log-moneyness", "relative-ticks"):
        tick_radius = (CFG.liquidity_M[fee_label] // 2) * tick_spacing
        return build_impact_surface(
            df, tick_spacing, axis, quantity, d0, d1, invert,
            tick_radius=tick_radius, n_time_samples=n_time_samples,
            relative_tick_M=CFG.liquidity_M[fee_label],
        )
    if axis == "absolute-ticks":
        tick_window = compute_tick_window(
            df["curr_tick"].to_numpy(dtype=np.int64), CFG.ZOOM
        )
        return build_impact_surface(
            df, tick_spacing, axis, quantity, d0, d1, invert,
            tick_window=tick_window, n_time_samples=n_time_samples,
        )
    raise ValueError(
        "axis must be 'log-moneyness', 'relative-ticks', or 'absolute-ticks'; "
        f"got {axis!r}"
    )


def plot_impact_profile(
    df: pd.DataFrame,
    pair: str,
    fee_label: str,
    tick_spacing: int,
    out_path: Path,
    quantity: str,
    d0: int,
    d1: int,
    invert: bool,
    axis: str = "log-moneyness",
    n_time_samples: int = 200,
    block_ts: pd.Series | None = None,
) -> None:
    """Time-collapsed mean ±1 std of log10(impact) vs the selected x-axis
    (analogue of plot_liquidity_shape). ATM reference at x=0 on recentred axes."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    x_axis, _times, log10_imp, _curr, _blocks = _impact_surface_for_axis(
        df, tick_spacing, fee_label, quantity, d0, d1, invert, axis, n_time_samples
    )
    atm_x = 0.0 if axis in ("log-moneyness", "relative-ticks") else None

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        mean_imp = np.nanmean(log10_imp, axis=0)
        std_imp = np.nanstd(log10_imp, axis=0)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.fill_between(
        x_axis, mean_imp - std_imp, mean_imp + std_imp,
        color="gray", alpha=0.25, label="±1 std",
    )
    ax.plot(x_axis, mean_imp, color="black", lw=1.4, label="mean")
    if atm_x is not None:
        ax.axvline(atm_x, color=CFG.ATM_color, linestyle="--", linewidth=0.8, label="ATM")

    ax.set_xlabel(_xlabel(axis, invert))
    ax.set_ylabel(f"mean {_cbar_label(quantity, pair)}")
    ax.set_title(f"{_QTITLE[quantity]} Price Impact ({axis}) — {pair} {fee_label}")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [saved] {out_path}")


def plot_impact_surface(
    df: pd.DataFrame,
    pair: str,
    fee_label: str,
    tick_spacing: int,
    out_path: Path,
    quantity: str,
    d0: int,
    d1: int,
    invert: bool,
    axis: str = "log-moneyness",
    n_time_samples: int = 200,
    block_ts: pd.Series | None = None,
) -> None:
    """3-D log10(impact) surface over (x-axis, time) (analogue of
    plot_liquidity_surface / _absolute)."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    x_axis, times, log10_imp, _curr, sampled_blocks = _impact_surface_for_axis(
        df, tick_spacing, fee_label, quantity, d0, d1, invert, axis, n_time_samples
    )
    x_grid, time_grid = np.meshgrid(x_axis, times)

    fig = plt.figure(figsize=(12, 7))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(  # type: ignore[no-untyped-call]
        x_grid, time_grid, np.ma.masked_invalid(log10_imp),
        cmap="magma", linewidth=0, antialiased=False, rcount=200, ccount=200,
    )
    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=12, pad=0.1)
    cbar.set_label(_cbar_label(quantity, pair))

    ax.set_xlabel(_xlabel(axis, invert))
    ax.set_zlabel(_cbar_label(quantity, pair))  # type: ignore[no-untyped-call]
    ax.set_title(
        f"{_QTITLE[quantity]} Price Impact Surface ({axis}) — {pair} {fee_label}"
    )
    if block_ts is not None:
        _apply_month_ticks_3d(ax, sampled_blocks, block_ts)
    else:
        ax.set_ylabel("Time")

    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [saved] {out_path}")


def plot_impact_heatmap(
    df: pd.DataFrame,
    pair: str,
    fee_label: str,
    tick_spacing: int,
    out_path: Path,
    quantity: str,
    d0: int,
    d1: int,
    invert: bool,
    n_time_samples: int = 200,
    block_ts: pd.Series | None = None,
) -> None:
    """Top-down (absolute-tick × time) heatmap of log10(impact) with the pool
    spot (curr_tick) overlaid (analogue of plot_lvsp)."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tick_window = compute_tick_window(
        df["curr_tick"].to_numpy(dtype=np.int64), CFG.ZOOM
    )
    x_axis, times, log10_imp, curr_ticks, sampled_blocks = build_impact_surface(
        df, tick_spacing, "absolute-ticks", quantity, d0, d1, invert,
        tick_window=tick_window, n_time_samples=n_time_samples,
    )

    if block_ts is not None:
        ts_arr = pd.DatetimeIndex(block_ts.loc[sampled_blocks].values)
        times_x: np.ndarray = mdates.date2num(ts_arr)
        use_dates = True
    else:
        times_x = times
        use_dates = False

    fig, ax = plt.subplots(figsize=(12, 6))
    mesh = ax.pcolormesh(
        times_x, x_axis, np.ma.masked_invalid(log10_imp.T),
        cmap="magma", shading="auto",
    )
    ax.plot(times_x, curr_ticks, color="black", linewidth=1.0,
            label="Spot price (curr_tick)")

    if use_dates:
        ax.xaxis_date()
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)
        ax.set_xlabel("Month")
    else:
        ax.set_xlabel("Time")

    cbar = fig.colorbar(mesh, ax=ax, pad=0.02)
    cbar.set_label(_cbar_label(quantity, pair))
    ax.set_ylabel("Tick")
    ax.set_title(f"{_QTITLE[quantity]} Price Impact vs Price — {pair} {fee_label}")
    ax.legend(fontsize=8, loc="upper left")

    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [saved] {out_path}")
