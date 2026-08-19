"""
Plot for the cycle-4 functional PCA of the liquidity surface -- per-component PVE, stacked, vs.
rolling-window start, the individual-contribution companion to Fig. 4 (bottom),
Risk/Tung/Wang, "Dynamics of Liquidity Surfaces in Uniswap V3" (which plots CPVE, cumulative).

Pure plotting: takes already-computed src.math_core.functional_pca.WindowResult objects,
computes nothing. Matches the math_core/graphics split every other module in this project uses.
One PNG per (pool, window_T) -- single-pool, not the old multi-pool overlay.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..math_core.functional_pca import WindowResult, effective_rank

PVE_K_VALUES: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8)

# Colors for ranks 1-6 are the original YlOrRd sampling (unchanged from the K=1..6 version:
# cmap(0.1 + 0.8*i/5) for i=0..5). Ranks 7-8 are appended explicitly, breaking out of YlOrRd
# toward purple, so the original six bands render pixel-identically to before.
_PVE_COLORS_1_TO_6: tuple[str, ...] = tuple(
    plt.get_cmap("YlOrRd")(0.1 + 0.8 * i / 5) for i in range(6)
)
_PVE_COLORS_7_TO_8: tuple[str, ...] = ("#984ea3", "#4a148c")  # purple, deep purple
PVE_COLORS: tuple = _PVE_COLORS_1_TO_6 + _PVE_COLORS_7_TO_8

# One (color, linestyle) per overlaid window in plot_eigenvectors_grid, in window order.
# First three match the reference figure's own Window 1/2/3 convention (solid blue, dashed
# green, dash-dot black); a 4th is appended since this project's own cap is "up to 4 windows",
# one more than the reference figure shows.
WINDOW_STYLES: tuple[dict, ...] = (
    {"color": "#377eb8", "linestyle": "-"},   # Window 1
    {"color": "#4daf4a", "linestyle": "--"},  # Window 2
    {"color": "#000000", "linestyle": "-."},  # Window 3
    {"color": "#e41a1c", "linestyle": ":"},   # Window 4
)


def _apply_date_axis(ax: plt.Axes) -> None:
    """
    Shared calendar-date x-axis setup -- month ticks, "%b %Y" labels, rotated. Factored out of
    plot_pve_stacked_vs_window_start (unchanged behavior there) so the two new line plots below
    don't duplicate it a second and third time.
    """
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.figure.autofmt_xdate()


def plot_pve_stacked_vs_window_start(
    windows: list[WindowResult],
    window_start_dates: list[pd.Timestamp],
    pool_label: str,
    window_T: int,
    out_path: Path,
    k_values: tuple[int, ...] = PVE_K_VALUES,
) -> None:
    """
    Per-component PVE, stacked, vs. rolling-window start date, for one pool at one window
    length. Band k's thickness at each date is PVE_k itself (not cumulative); the band's own
    top edge is CPVE_k, so no new statistic is computed here -- WindowResult.cpve already
    carries both.

    Style: reproduces a stacked-area reference the user supplied (unrelated domain, "CSP"
    plot) -- full-opacity bands (alpha=1), no gridlines, one color per rank sampled from a
    yellow-to-red colormap, a matching-color boundary line traced on top of each band.

    Args:
        windows            : one pool's rolling-window FPCA spectra, ascending window-start
                              order (rolling_cpve's own output order).
        window_start_dates : calendar date of each window's start block, same length and order
                              as windows (resolved by the caller via block_timestamps).
        pool_label          : e.g. "WETH_USDC@5bp" -- title only.
        window_T            : rolling-window length in rows -- title only.
        out_path             : PNG destination; parent directory must already exist (caller's
                              responsibility).
        k_values            : ranks to stack, ascending (default PVE_K_VALUES = 1..8).
    """
    assert len(windows) == len(window_start_dates), (
        f"plot_pve_stacked_vs_window_start: windows ({len(windows)}) and window_start_dates "
        f"({len(window_start_dates)}) must be the same length"
    )
    assert (
        len(windows) > 0
    ), "plot_pve_stacked_vs_window_start: windows must be non-empty"
    assert len(k_values) <= len(PVE_COLORS), (
        f"plot_pve_stacked_vs_window_start: {len(k_values)} k_values but only "
        f"{len(PVE_COLORS)} colors defined in PVE_COLORS"
    )

    x_dates = mdates.date2num(pd.DatetimeIndex(window_start_dates))
    colors = PVE_COLORS[: len(k_values)]

    fig, ax = plt.subplots(figsize=(11, 6))

    cum_prev = np.zeros(len(windows))
    for K, color in zip(k_values, colors):
        cum_k = np.array([w.cpve[K - 1] for w in windows])
        label = f"PVE {K}"
        ax.fill_between(x_dates, cum_prev, cum_k, color=color, alpha=1.0, label=label)
        ax.plot(x_dates, cum_k, color=color, linewidth=1.2)
        cum_prev = cum_k

    ax.axhline(0.90, color="dimgray", linewidth=0.8, linestyle="-", zorder=3)
    ax.axhline(0.95, color="dimgray", linewidth=0.8, linestyle=":", zorder=3)

    _apply_date_axis(ax)

    ax.grid(False)
    ax.set_xlabel("Rolling-window start date")
    ax.set_ylabel("CPVE")
    ax.set_ylim(0.7, 1.0)
    ax.set_title(f"{pool_label} — PVE vs. window start (T={window_T})")
    ax.legend(fontsize=8, ncol=1, loc="upper right")

    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [saved] {out_path}")


def plot_spectral_diagnostics_vs_window_start(
    windows: list[WindowResult],
    window_start_dates: list[pd.Timestamp],
    pool_label: str,
    window_T: int,
    out_path: Path,
) -> None:
    """
    Two-row companion figure, sharing the x-axis: effective rank (top) and total variance
    (bottom) vs. rolling-window start date, for one pool at one window length. Both series are
    cheap derivatives of WindowResult.eigenvalues (no new estimation) -- effective rank is the
    continuous companion to the discrete "K needed for X% variance" reading the PVE plot gives;
    total variance is its level-shift companion, catching a period boundary where the surface's
    raw variance moves but the spectral *shape* (effective rank, PVE distribution) does not.
    One figure, not two, so the two series read off the same calendar axis at a glance.

    Args:
        windows            : one pool's rolling-window FPCA spectra, ascending window-start
                              order (rolling_cpve's own output order).
        window_start_dates : calendar date of each window's start block, same length and order
                              as windows (resolved by the caller via block_timestamps).
        pool_label          : e.g. "WETH_USDC@5bp" -- title only.
        window_T            : rolling-window length in rows -- title only.
        out_path             : PNG destination; parent directory must already exist (caller's
                              responsibility).
    """
    assert len(windows) == len(window_start_dates), (
        f"plot_spectral_diagnostics_vs_window_start: windows ({len(windows)}) and "
        f"window_start_dates ({len(window_start_dates)}) must be the same length"
    )
    assert len(windows) > 0, "plot_spectral_diagnostics_vs_window_start: windows must be non-empty"

    x_dates = mdates.date2num(pd.DatetimeIndex(window_start_dates))
    eff_rank = np.array([effective_rank(w.eigenvalues) for w in windows])
    total_var = np.array([float(w.eigenvalues.sum()) for w in windows])

    fig, (ax_rank, ax_var) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

    ax_rank.plot(x_dates, eff_rank, color="#377eb8", linewidth=1.4)
    ax_rank.grid(False)
    ax_rank.set_ylabel("Effective rank")
    ax_rank.set_title(f"{pool_label} — spectral diagnostics vs. window start (T={window_T})")

    ax_var.plot(x_dates, total_var, color="#e6550d", linewidth=1.4)
    ax_var.grid(False)
    ax_var.set_ylabel("Total variance (trace of Σ̂)")
    ax_var.set_xlabel("Rolling-window start date")

    _apply_date_axis(ax_var)  # bottom row only carries date tick labels (sharex=True)
    plt.setp(ax_rank.get_xticklabels(), visible=False)

    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [saved] {out_path}")


def plot_eigenvectors_grid(
    windows: list[WindowResult],
    window_labels: list[str],
    x_grid: np.ndarray,
    pool_label: str,
    out_path: Path,
    k_values: tuple[int, int, int, int] = (1, 2, 3, 4),
) -> None:
    """
    First four eigenvectors u_1..u_4 of the log-liquidity surface's FPCA, vs. the
    rank-standardized grid coordinate, 2x2 subplot -- Fig. 5, Risk/Tung/Wang, "Dynamics of
    Liquidity Surfaces in Uniswap V3." One curve per window; the current default caller
    (functional_pca_eigenvectors_study.py) passes exactly one window (the whole dataset), so
    today's plots show a single curve per subplot.

    NOTE 1 (planned): a future caller is meant to pass up to 4 windows here (e.g. "Window
    1/2/3" the way the reference figure does), each a separate WindowResult from
    src.math_core.functional_pca.select_single_window. This function's signature already
    supports that -- windows/window_labels are lists, and WINDOW_STYLES has 4 entries -- so no
    change is needed here to light that up.
    NOTE 2 (the catch): src.math_core.functional_pca._fpca_core's sign convention fixes each
    window's eigenvectors independently (largest-magnitude entry positive), with no reference
    to any other window. That is fine for a single curve, but once NOTE 1 lands, two windows'
    u_k can come out sign-flipped relative to each other for no economic reason -- unlike the
    reference figure, whose Window 1/2/3 curves are consistently oriented. Switching
    _fpca_core's convention to sign-align every window against a fixed reference window (by the
    sign of their inner product), or a manual per-plot flip, resolves it; neither is done yet.

    Args:
        windows       : 1-4 WindowResult objects, each already carrying eigenvectors (M, M).
        window_labels : legend label per window, same length and order as windows (e.g.
                        ["Whole dataset"], or ["Window 1", "Window 2", "Window 3"] once NOTE 1
                        lands).
        x_grid        : (M,) rank-standardized grid coordinate in [-1, 1]
                        (src.math_core.functional_pca.rank_standardized_x_grid).
        pool_label    : e.g. "WETH_USDC@5bp" -- suptitle only.
        out_path      : PNG destination; parent directory must already exist (caller's
                        responsibility).
        k_values      : which eigenvector ranks to plot, one per subplot -- exactly 4 (2x2).
    """
    assert len(windows) == len(window_labels), (
        f"plot_eigenvectors_grid: windows ({len(windows)}) and window_labels "
        f"({len(window_labels)}) must be the same length"
    )
    assert 1 <= len(windows) <= len(WINDOW_STYLES), (
        f"plot_eigenvectors_grid: {len(windows)} windows, but only {len(WINDOW_STYLES)} "
        "WINDOW_STYLES are defined"
    )
    assert len(k_values) == 4, (
        f"plot_eigenvectors_grid: exactly 4 k_values for a 2x2 grid, got {len(k_values)}"
    )
    for w in windows:
        assert w.eigenvectors.shape[0] == x_grid.shape[0], (
            f"plot_eigenvectors_grid: eigenvectors have {w.eigenvectors.shape[0]} rows, "
            f"x_grid has {x_grid.shape[0]}"
        )

    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True)

    for ax, K in zip(axes.flat, k_values):
        for w, label, style in zip(windows, window_labels, WINDOW_STYLES):
            ax.plot(
                x_grid, w.eigenvectors[:, K - 1], label=label,
                color=style["color"], linestyle=style["linestyle"], linewidth=1.4,
            )
        ax.axhline(0.0, color="dimgray", linewidth=0.6)
        ax.grid(False)
        ax.set_title(f"$u_{{{K}}}$")

    for ax in axes[-1, :]:
        ax.set_xlabel("Relative tick (rank-standardized)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Loading")

    handles, labels_ = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels_, loc="lower center", ncol=len(windows), fontsize=8,
               bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(f"{pool_label} — eigenvectors $u_1$–$u_4$")
    fig.tight_layout(rect=(0.0, 0.03, 1.0, 0.97))

    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [saved] {out_path}")
