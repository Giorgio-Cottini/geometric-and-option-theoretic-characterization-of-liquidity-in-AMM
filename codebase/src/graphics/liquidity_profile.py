"""
Graphics for the piecewise-constant liquidity profile ℓ(P_T).

Public API
----------
plot_liq(liq_df, fee_label, P0, expiries_F, out_dir, x_min, x_max)
    One figure per fee tier; one subplot per expiry.
    x-axis: log(K / F)  where F is the expiry-specific forward price.
    Saved as  {out_dir}/{fee_label}s.png
"""

import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 — registers 3D projection

from .config import CFG
from .labels import lm_xlabel
from ..math_core import piecewise_constant_liquidity_profile, build_liquidity_surface
from ..math_core.liquidity_vs_price import compute_tick_window, build_lvsp_surface

# ————————————————————————————————————————————————————————————————————————— #
# Month-tick helper (3-D surfaces)


def _apply_month_ticks_3d(
    ax,
    sampled_blocks: np.ndarray,
    block_ts: pd.Series,
) -> None:
    """
    Replace the normalised [0, 1] Y-axis ticks of a 3-D surface with calendar
    month labels derived from actual block timestamps.

    The Y-axis keeps its numerical [0, 1] range so the surface geometry is
    unchanged; only the tick positions and labels are overwritten.

    Args:
        ax            : matplotlib 3-D Axes.
        sampled_blocks: 1-D int64 array of block numbers (one per time row).
        block_ts      : pd.Series[Timestamp, tz=UTC] indexed by block_number,
                        as returned by load_block_timestamps().
    """
    # Unix seconds for each sampled block (float64 for arithmetic)
    ts_unix = (
        block_ts.loc[sampled_blocks].values.astype("datetime64[s]").astype(np.float64)
    )
    t_min, t_max = ts_unix.min(), ts_unix.max()

    # Month-start boundaries that fall within the data range
    dt_first = pd.Timestamp(t_min, unit="s", tz="UTC")
    dt_last = pd.Timestamp(t_max, unit="s", tz="UTC")
    months = pd.date_range(
        start=pd.Timestamp(dt_first.year, dt_first.month, 1, tz="UTC"),
        end=dt_last,
        freq="MS",
    )

    # Map month boundaries to [0, 1] using the same linear scale as `times`
    month_pos = (months.asi8 / 1e9 - t_min) / (t_max - t_min)
    valid = (month_pos >= 0.0) & (month_pos <= 1.0)

    ax.set_yticks(month_pos[valid][::2].tolist())
    ax.set_yticklabels(
        [m.strftime("%b %Y") for m in months[valid][::2]],
        fontsize=6,
        rotation=-15,
        ha="left",
        va="center",
    )
    # ax.set_ylabel("Month")


# ————————————————————————————————————————————————————————————————————————— #
# Private helpers


def _draw_liq_step(
    ax,
    x_lo: np.ndarray,
    x_hi: np.ndarray,
    ell: np.ndarray,
    p0_x: float,
    extra_vlines: list[tuple[float, str, str]],
    xlabel: str,
    title: str,
    x_min: float | None = None,
    x_max: float | None = None,
) -> None:
    """
    Draw the piecewise-constant liquidity profile as a step function on ax.

    Each tick interval [x_lo_i, x_hi_i] is drawn as a horizontal segment at
    height ℓ_i, with a vertical connector to zero at each boundary.
    Intervals entirely below p0_x are red (put side); intervals entirely above
    are blue (call side); straddling intervals are split at p0_x.

    A low-alpha smooth overlay (box-filtered on a fine grid) is added to
    convey the envelope without obscuring the step structure.

    Args:
        ax           : matplotlib Axes to draw on.
        x_lo, x_hi  : transformed left/right tick-interval boundaries.
        ell          : intrinsic liquidity value on each interval.
        p0_x         : transformed x-coordinate of P₀ (split point).
        extra_vlines : additional vertical reference lines as (x, label, linestyle).
        xlabel       : x-axis label string.
        title        : subplot title string.
        x_min, x_max : optional axis limits.
    """
    put_label_added = False
    call_label_added = False

    for xlo_i, xhi_i, l in zip(x_lo, x_hi, ell):
        if not (np.isfinite(xlo_i) and np.isfinite(xhi_i)):
            continue
        if xlo_i >= xhi_i or l == 0:
            continue

        def _seg(xa: float, xb: float, color: str, label: str | None) -> None:
            # Horizontal segment at height l
            ax.plot([xa, xb], [l, l], color=color, lw=1.2, label=label)
            # Vertical connectors to zero
            ax.vlines([xa, xb], ymin=0, ymax=l, color=color, lw=0.6, alpha=0.5)

        if xhi_i <= p0_x:
            lbl = "Put side (P)" if not put_label_added else None
            _seg(xlo_i, xhi_i, CFG.P_color, lbl)
            put_label_added = True
        elif xlo_i >= p0_x:
            lbl = "Call side (C)" if not call_label_added else None
            _seg(xlo_i, xhi_i, CFG.C_color, lbl)
            call_label_added = True
        else:
            # Straddles P₀: split at p0_x
            lbl_p = "Put side (P)" if not put_label_added else None
            _seg(xlo_i, p0_x, CFG.P_color, lbl_p)
            put_label_added = True
            lbl_c = "Call side (C)" if not call_label_added else None
            _seg(p0_x, xhi_i, CFG.C_color, lbl_c)
            call_label_added = True

    # ── Reference lines ─────────────────────────────────────────────────────
    ax.axvline(p0_x, color="gray", linestyle="--", linewidth=0.8, label="P₀")
    for xv, vlabel, ls in extra_vlines:
        ax.axvline(xv, color="black", linestyle=ls, linewidth=0.8, label=vlabel)

    ax.set_xlabel(xlabel)
    ax.set_ylabel("ℓ (intrinsic liquidity)")
    ax.set_title(title)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    if x_min is not None or x_max is not None:
        ax.set_xlim(x_min, x_max)


# ————————————————————————————————————————————————————————————————————————— #
# Public API


def plot_liq(
    liq_df: pd.DataFrame,
    fee_label: str,
    P0: float,
    expiries_F: list[tuple[str, float]],
    out_dir: Path | None = None,
    x_min: float | None = CFG.l_x_min,
    x_max: float | None = CFG.l_x_max,
) -> None:
    """
    Plot ℓ vs log(P_T / F) for one fee tier, one subplot per expiry.

    The liquidity profile ℓ(q) is drawn as a piecewise-constant step function
    with a low-alpha smooth overlay.  Segment colours split at P₀: red for the
    put side (q < P₀), blue for the call side (q ≥ P₀).

    Args:
        liq_df     : output of reconstruct_liquidity_cumsum for this fee tier.
        fee_label  : short label, e.g. "5bp" or "30bp".
        P0         : pool spot price (USDC/ETH).
        expiries_F : ordered list of (expiry_label, F) pairs.  One subplot
                     is produced for each entry, using F for the x-axis.
        out_dir    : directory for the output PNG.  None → CFG.liq_out_dir.
        x_min      : optional left  x-axis limit (log-moneyness).
        x_max      : optional right x-axis limit (log-moneyness).
    Saves:
        {out_dir}/{fee_label}s.png
    """
    out_dir = Path(out_dir) if out_dir is not None else CFG.liq_out_dir
    n = len(expiries_F)
    filename = f"{fee_label}.png"

    q_lower, q_upper, ell = piecewise_constant_liquidity_profile(liq_df)

    fig, axes = plt.subplots(n, 1, figsize=(10, 4 * n))
    if n == 1:
        axes = [axes]

    for ax, (expiry, F) in zip(axes, expiries_F):
        valid = q_lower > 0
        safe_lo = np.where(valid, q_lower, 1.0)
        x_lo = np.where(valid, np.log(safe_lo / F), np.nan)
        x_hi = np.log(q_upper / F)
        p0_x = float(np.log(P0 / F))
        extra_vlines = [(0.0, f"ATM  F={F:.0f}", ":")]

        _draw_liq_step(
            ax=ax,
            x_lo=x_lo,
            x_hi=x_hi,
            ell=ell,
            p0_x=p0_x,
            extra_vlines=extra_vlines,
            xlabel="log(K / F)",
            title=f"Liquidity Profile — {fee_label}  expiry={expiry}",
            x_min=x_min,
            x_max=x_max,
        )

    fig.tight_layout()
    out_path = out_dir / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  [saved] {out_path}")


# ————————————————————————————————————————————————————————————————————————— #


def plot_liquidity_surface(
    df: pd.DataFrame,
    pair: str,
    fee_label: str,
    tick_spacing: int,
    out_path: Path,
    invert: bool,
    n_time_samples: int = 200,
    log_scale_offset: float = 0.0,
    use_log_moneyness: bool = True,
    block_ts: pd.Series | None = None,
) -> None:
    """
    Plot the 3-D log-liquidity surface for one fee tier.

    The x-axis is either log-moneyness (default) or a rank-standardized relative-tick axis,
    controlled by use_log_moneyness.  Both are centred at 0 (ATM / anchor) using the pool's
    actual slot0 tick from the processed parquet.

    log-moneyness branch (use_log_moneyness=True): the plotted x-array is
    (curr_tick - tick_idx) * log(1.0001); that equals log(K/S) only on an inverted pool and
    log(S/K) on a native-ordered one, so `invert` selects the label (see graphics/labels.py).
    Cells with no tick data at a given grid point are left NaN (matplotlib's masked_invalid
    skips them when rendering) -- there is no ffill/bfill interpolation pass anywhere in this
    module, despite what an earlier revision of this docstring claimed.

    relative-tick branch (use_log_moneyness=False): rank-standardized per block (Appendix B,
    Risk/Tung/Wang) via math_core._select_rank_standardized_row_filled -- column j is "the j-th
    nearest-rank initialized tick to this block's own anchor", affine-mapped to [-1, 1], not a
    shared geometric tick position. A block whose local tick density can't fill a given rank
    position leaves that cell NaN rather than dropping the block or the cell's neighbors.

    The spatial window is derived from CFG.liquidity_M, with a different role per branch:
        log-moneyness  : tick_radius = (CFG.liquidity_M // 2) * tick_spacing (a raw tick-
                          distance radius, so both fee tiers span a comparable log-moneyness
                          range despite their different tick_spacing).
        relative-ticks : M = CFG.liquidity_M directly (a rank-instance count, not a distance --
                          (M-1)//2 nearest-rank ticks each side of the anchor).

    Args:
        df               : processed parquet DataFrame with columns
                           [block_number, tick_idx, liquidity, curr_tick].
        fee_label        : short label used in the title and filename, e.g. "5bp".
        out_dir          : output directory.  None → CFG.liq_out_dir.
        invert           : pool orientation (config.POOLS[...]["invert_price"]).
                           Selects the log-moneyness LABEL only — the plotted
                           values do not depend on it.
        n_time_samples   : number of time slices retained after downsampling
                           (default 200).
        tick_spacing     : fee-tier tick spacing (10 for 5 bp, 60 for 30 bp).
        log_scale_offset : additive offset on log_liq (default 0.0).
                           Pass np.log(1e12) to match the paper's un-normalized
                           y-scale.
        use_log_moneyness: if True (default), x-axis is log-moneyness and filename
                           ends with '_surface.png'.  If False, x-axis is the
                           rank-standardized relative-tick axis (see above) and
                           filename ends with '_surface_ticks.png'.
        block_ts         : optional pd.Series[Timestamp, tz=UTC] indexed by
                           block_number (from load_block_timestamps()).  When
                           provided, the Y (time) axis shows calendar month
                           labels instead of the normalised [0, 1] range.
    Saves:
        {out_dir}/{fee_label}_surface.png          (use_log_moneyness=True)
        {out_dir}/{fee_label}_surface_ticks.png    (use_log_moneyness=False)
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tick_radius = (CFG.liquidity_M[fee_label] // 2) * tick_spacing

    x_axis, times, log_liq, sampled_blocks = build_liquidity_surface(
        df,
        tick_radius,
        n_time_samples,
        log_scale_offset,
        use_log_moneyness,
        relative_tick_M=CFG.liquidity_M[fee_label],
    )

    # Build meshgrid: X = x-axis, Y = time, Z = log-liquidity
    x_grid, time_grid = np.meshgrid(x_axis, times)

    fig = plt.figure(figsize=(12, 7))
    ax = fig.add_subplot(111, projection="3d")

    surf = ax.plot_surface(  # type: ignore[no-untyped-call]
        x_grid,
        time_grid,
        np.ma.masked_invalid(log_liq),
        cmap="magma",
        linewidth=0,
        antialiased=False,
        rcount=200,
        ccount=200,
    )

    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=12, pad=0.1)
    cbar.set_label("log(Liquidity)")

    x_label = lm_xlabel(invert) if use_log_moneyness else "Relative Tick (rank-standardized)"
    ax.set_xlabel(x_label)
    ax.set_zlabel("log(Liquidity)")  # type: ignore[no-untyped-call]
    ax.set_title(f"Liquidity Surface — {pair} {fee_label}")

    if block_ts is not None:
        _apply_month_ticks_3d(ax, sampled_blocks, block_ts)
    else:
        ax.set_ylabel("Time")

    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [saved] {out_path}")


# ————————————————————————————————————————————————————————————————————————— #


def plot_liquidity_surface_absolute(
    df: pd.DataFrame,
    pair: str,
    fee_label: str,
    tick_spacing: int,
    out_path: Path,
    n_time_samples: int = 200,
    block_ts: pd.Series | None = None,
) -> None:
    """
    Plot the 3-D log-liquidity surface with absolute tick on the x-axis.

    Unlike plot_liquidity_surface, the x-axis is not recentred at curr_tick
    each block — it uses the raw absolute tick grid fixed across the entire
    dataset.  This lets you see the absolute position of liquidity in tick
    space over time (e.g. whether LPs migrated upward/downward in price).

    The tick window [tick_lower, tick_upper] is derived from the dataset's
    actual curr_tick range, expanded by CFG.ZOOM:
        tick_lower = min(curr_tick) - spread * ZOOM
        tick_upper = max(curr_tick) + spread * ZOOM

    Args:
        df             : processed parquet DataFrame with columns
                         [block_number, tick_idx, liquidity, curr_tick].
        fee_label      : short label used in the title and filename, e.g. "5bp".
        tick_spacing   : fee-tier tick spacing (10 for 5bp, 60 for 30bp).
        out_dir        : output directory.  None → CFG.liq_out_dir.
        n_time_samples : number of time slices retained after downsampling.
        block_ts       : optional pd.Series[Timestamp, tz=UTC] indexed by
                         block_number (from load_block_timestamps()).  When
                         provided, the Y (time) axis shows calendar month
                         labels instead of the normalised [0, 1] range.
    Saves:
        {out_dir}/{fee_label}_surface_abs.png
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tick_lower, tick_upper = compute_tick_window(
        df["curr_tick"].to_numpy(dtype=np.int64), CFG.ZOOM
    )

    abs_tick_grid, times, log_liq, _, sampled_blocks = build_lvsp_surface(
        df, tick_lower, tick_upper, tick_spacing, n_time_samples
    )

    # meshgrid: X = absolute tick, Y = time, Z = log-liquidity
    x_grid, time_grid = np.meshgrid(abs_tick_grid, times)

    fig = plt.figure(figsize=(12, 7))
    ax = fig.add_subplot(111, projection="3d")

    surf = ax.plot_surface(  # type: ignore[no-untyped-call]
        x_grid,
        time_grid,
        np.ma.masked_invalid(log_liq),
        cmap="magma",
        linewidth=0,
        antialiased=False,
        rcount=200,
        ccount=200,
    )

    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=12, pad=0.1)
    cbar.set_label("log(Liquidity)")

    ax.set_xlabel("Absolute Tick")  # type: ignore[no-untyped-call]
    ax.set_zlabel("log(Liquidity)")  # type: ignore[no-untyped-call]
    ax.set_title(f"Liquidity Surface (Absolute Ticks) — {pair} {fee_label}")

    if block_ts is not None:
        _apply_month_ticks_3d(ax, sampled_blocks, block_ts)
    else:
        ax.set_ylabel("Time")

    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [saved] {out_path}")


# ————————————————————————————————————————————————————————————————————————— #


def plot_liquidity_shape(
    df: pd.DataFrame,
    pair: str,
    fee_label: str,
    tick_spacing: int,
    out_path: Path,
    invert: bool,
    axis: str = "log-moneyness",
    n_time_samples: int = 200,
    block_ts: pd.Series | None = None,
) -> None:
    """
    Plot the time-averaged liquidity *profile* (shape): a 2-D collapse of the
    3-D surface along the time axis.

    The log-liquidity surface log_liq(x, t) is reduced along time to one curve:
        mean(x) = nanmean_t log_liq(x, t)
        std(x)  = nanstd_t  log_liq(x, t)
    drawn as a neutral mean line with a ±1 std band, isolating the average
    profile shape from day-to-day level fluctuations.

    The x-axis is selected by `axis`, reusing the same surface builders as the
    3-D plots so each profile lines up with its sibling surface:
        "log-moneyness"  : log-moneyness, ATM at 0            (build_liquidity_surface, True)
        "relative-ticks" : rank-standardized rel tick, [-1,1] (build_liquidity_surface, False)
        "absolute-ticks" : absolute tick                      (build_lvsp_surface)
    The log-moneyness axis is log(K/S) on an inverted pool and log(S/K) on a
    native-ordered one; `invert` selects the label (see graphics/labels.py).
    For the two recentred axes an ATM reference line is drawn at x = 0; the
    absolute-tick axis has no fixed ATM (curr_tick moves over time), so none is
    drawn.

    Args:
        df             : processed parquet DataFrame with columns
                         [block_number, tick_idx, liquidity, curr_tick].
        pair           : currency-pair label used in the title, e.g. "WETH_USDC".
        fee_label      : short label used in the title, e.g. "5bp".
        tick_spacing   : fee-tier tick spacing (10 for 5bp, 60 for 30bp).
        out_path       : full output PNG path (parents created if absent).
        invert         : pool orientation (config.POOLS[...]["invert_price"]).
                         Selects the log-moneyness LABEL only — the plotted
                         values do not depend on it.
        axis           : "log-moneyness" | "relative-ticks" | "absolute-ticks".
        n_time_samples : number of time slices retained after downsampling.
        block_ts       : accepted for call-site uniformity with the surface/LvsP
                         plots; unused here (the time axis is collapsed away).
    Saves:
        out_path
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if axis in ("log-moneyness", "relative-ticks"):
        tick_radius = (CFG.liquidity_M[fee_label] // 2) * tick_spacing
        x_axis, _times, log_liq, _blocks = build_liquidity_surface(
            df, tick_radius, n_time_samples, 0.0, axis == "log-moneyness",
            relative_tick_M=CFG.liquidity_M[fee_label],
        )
        xlabel = lm_xlabel(invert) if axis == "log-moneyness" else "Relative Tick (rank-standardized)"
        atm_x: float | None = 0.0
    elif axis == "absolute-ticks":
        tick_lower, tick_upper = compute_tick_window(
            df["curr_tick"].to_numpy(dtype=np.int64), CFG.ZOOM
        )
        x_axis, _times, log_liq, _curr, _blocks = build_lvsp_surface(
            df, tick_lower, tick_upper, tick_spacing, n_time_samples
        )
        xlabel = "Absolute Tick"
        atm_x = None
    else:
        raise ValueError(
            "axis must be 'log-moneyness', 'relative-ticks', or "
            f"'absolute-ticks'; got {axis!r}"
        )

    # Collapse the time axis.  Edge columns can be entirely NaN (ticks never
    # populated in the window) → nanmean/nanstd emit an all-NaN-slice
    # RuntimeWarning; suppress it and let the NaN result flow through
    # (matplotlib skips NaN when drawing the line/band).
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        mean_log_liq = np.nanmean(log_liq, axis=0)
        std_log_liq = np.nanstd(log_liq, axis=0)

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.fill_between(
        x_axis,
        mean_log_liq - std_log_liq,
        mean_log_liq + std_log_liq,
        color="gray",
        alpha=0.25,
        label="±1 std",
    )
    ax.plot(x_axis, mean_log_liq, color="black", lw=1.4, label="mean")
    if atm_x is not None:
        ax.axvline(atm_x, color=CFG.ATM_color, linestyle="--", linewidth=0.8, label="ATM")

    ax.set_xlabel(xlabel)
    ax.set_ylabel("mean log(Liquidity)")
    ax.set_title(f"Liquidity Profile ({axis}) — {pair} {fee_label}")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [saved] {out_path}")
