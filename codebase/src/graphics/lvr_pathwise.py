"""
Plotters for the R5 LVR consequence (cycle 3, checkpoint 4).

Sibling of src/graphics/cev_elasticity.py.  Reads only the DataFrames the runner already built;
no math_core import.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_lvr_ratio(summary_df: pd.DataFrame, out_path: Path) -> None:
    """
    One bar per pool: LVR_obs / LVR_neutral (beta=1), spec section 10 estimand 3.

    Args:
        summary_df : columns [pool, ratio, cv_obs, cv_neutral], one row per pool — the runner's
                    per-pool lvr_ratio_and_cv() output, concatenated.
        out_path   : PNG destination; parent directory must already exist.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    order = summary_df.sort_values("ratio")
    ax.barh(order["pool"], order["ratio"])
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1,
               label="ratio = 1 (equal LVR variability)")
    ax.set_xlabel("LVR_obs / LVR_neutral (beta = 1)")
    ax.set_title("R5: realized vs. LVR-neutral counterfactual, all pools")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_lvr_increments(pool_series: pd.DataFrame, pair: str, fee_label: str,
                        out_path: Path) -> None:
    """
    One pool: observed vs. counterfactual LVR increment, block by block.

    Args:
        pool_series : columns [block_number, lvr_increment, lvr_neutral_increment].
        pair, fee_label : for the title, e.g. "WETH_USDC", "30bp".
        out_path    : PNG destination; parent directory must already exist.
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(pool_series["block_number"], pool_series["lvr_increment"],
            label="observed", linewidth=0.8)
    ax.plot(pool_series["block_number"], pool_series["lvr_neutral_increment"],
            label="counterfactual (beta=1)", linewidth=0.8)
    ax.set_xlabel("block_number")
    ax.set_ylabel("LVR increment (8h, token1 units, lower bound — C9)")
    ax.set_title(f"{fee_label} {pair}: realized vs. counterfactual LVR increments")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
