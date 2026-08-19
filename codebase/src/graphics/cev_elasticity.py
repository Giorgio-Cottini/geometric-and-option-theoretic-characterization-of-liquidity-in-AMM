"""
Plots for cycle 3 R1, the shape diagnostic.

Two figures per pool.

plot_band_dependence is the R1 headline.  A power law has no characteristic
scale, so under RTW26 Example 3.3 beta_shape is the same at every half-width, on
both branches.  A flat line is the null; a sloped line says the family does not
describe the pool at that scale.

plot_local_slope shows where the peak sits and how far the monotone region
extends on each side of it.

Axis convention.  x is log(K / S) in BOTH orientations, because it is computed
from human price as log(q / spot).  It is NOT the cycle-2 array
(curr_tick - tick_idx) * log(1.0001), so graph:graphics_labels_lm_xlabel is
deliberately not used here; see deviation D2 of the R1 plan.  The label comes
from src.math_core.profile_measure.X_LABEL so that the two never drift.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..math_core.profile_measure import X_LABEL

_BRANCH_STYLE = {"below": ("#1f77b4", "o", "below spot"),
                 "above": ("#d62728", "s", "above spot")}


def plot_band_dependence(
    sweep: pd.DataFrame,
    pair: str,
    fee_label: str,
    out_path: Path,
) -> None:
    """
    beta_shape against band half-width w, one line per branch, with an
    interquartile band across snapshots.

    Args:
        sweep     : sweep_pool output for one pool.
        out_path  : destination PNG; parent directories are created.
    """
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    for branch, (colour, marker, label) in _BRANCH_STYLE.items():
        sub = sweep[sweep["branch"] == branch]
        g = sub.groupby("w")["beta_shape"]
        med, q25, q75 = g.median(), g.quantile(0.25), g.quantile(0.75)
        ax.plot(med.index, med.to_numpy(), color=colour, marker=marker, label=label)
        ax.fill_between(med.index, q25.to_numpy(), q75.to_numpy(),
                        color=colour, alpha=0.18, linewidth=0)
    ax.axhline(1.0, color="#2ca02c", linestyle="--", linewidth=1.0,
               label=r"$\beta = 1$  (variance swap)")
    ax.set_xlabel("band half-width $w$  (log-moneyness)")
    ax.set_ylabel(r"$\hat{\beta}_{\mathrm{shape}} = -\mathrm{slope}/2$")
    ax.set_title(f"{pair} {fee_label} — band dependence of the shape elasticity")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_local_slope(
    prof: pd.DataFrame,
    pair: str,
    fee_label: str,
    out_path: Path,
) -> None:
    """
    Time-averaged d log L / d log q against log-moneyness, with an
    interquartile band across snapshots.  The horizontal line at -2 is the
    beta = 1 log-contract slope.

    Args:
        prof : local_slope_profile output for one pool.
    """
    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    x = prof["x_centre"].to_numpy()
    ax.plot(x, prof["slope_median"].to_numpy(), color="#1f77b4")
    ax.fill_between(x, prof["slope_q25"].to_numpy(), prof["slope_q75"].to_numpy(),
                    color="#1f77b4", alpha=0.18, linewidth=0)
    ax.axhline(-2.0, color="#2ca02c", linestyle="--", linewidth=1.0,
               label=r"slope $=-2$  ($\beta = 1$)")
    ax.axvline(0.0, color="#666666", linewidth=0.8)
    ax.set_xlabel(X_LABEL)
    ax.set_ylabel(r"local $d\log L / d\log q$")
    ax.set_title(f"{pair} {fee_label} — local slope profile")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
