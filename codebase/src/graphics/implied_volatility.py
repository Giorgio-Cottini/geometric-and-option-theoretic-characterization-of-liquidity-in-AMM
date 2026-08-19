"""
Graphics for Black-Scholes implied volatility fine structure.

Public API
----------
plot_iv(liq_df, fee_label, P0, iv_results, expiries_F, out_dir, x_min, x_max)
    Per-tick implied volatility vs log(K / F).  Step-function style, one subplot
    per expiry.  Saved as {iv_out_dir}/{fee_label}s.png.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from .config import CFG

# ————————————————————————————————————————————————————————————————————————— #
# Private helpers


def _save_figure(fig: Figure, out_dir: Path, filename: str) -> None:
    """Create parent directories, save figure, close it, and print confirmation."""
    out_path = out_dir / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  [saved] {out_path}")


# ————————————————————————————————————————————————————————————————————————— #
# Public API


def plot_iv(
    liq_df: pd.DataFrame,
    fee_label: str,
    P0: float,
    iv_results: list[dict],
    expiries_F: list[tuple[str, float]],
    out_dir: Path | None = None,
    x_min: float | None = CFG.iv_x_min,
    x_max: float | None = CFG.iv_x_max,
) -> None:
    """
    Plot per-tick BS implied volatility vs log(K / F) for one fee tier.

    Each tick interval is drawn as a horizontal segment at its solved sigma_BS.
    Put side (K < P0) in red, call side in blue.  Ticks where Newton-Raphson
    did not converge are omitted.

    Args:
        liq_df     : output of reconstruct_liquidity_cumsum for this fee tier.
        fee_label  : short label, e.g. "5bp".
        P0         : pool spot price (USDC/ETH).
        iv_results : list of dicts from compute_BS_iv_fine_structure, one per expiry.
                     Each must also contain key "sigma_BS_agg" (aggregate IV).
        expiries_F : ordered list of (expiry_label, F) pairs matching iv_results.
        out_dir    : directory for the output PNG.  None → CFG.iv_out_dir.
        x_min      : optional left  x-axis limit (log-moneyness).
        x_max      : optional right x-axis limit (log-moneyness).
    Saves:
        {out_dir}/{fee_label}s.png
    """
    out_dir = Path(out_dir) if out_dir is not None else CFG.iv_out_dir
    n = len(expiries_F)
    filename = f"{fee_label}s.png"

    fig, axes = plt.subplots(n, 1, figsize=(10, 4 * n))
    if n == 1:
        axes = [axes]

    for ax, (expiry, F), iv_res in zip(axes, expiries_F, iv_results):
        tl = iv_res["tick_lower"]
        tu = iv_res["tick_upper"]
        sigma = iv_res["sigma_BS"]
        conv = iv_res["converged"]

        # Only plot converged ticks
        mask = conv & np.isfinite(sigma)

        # Transform tick boundaries to log-moneyness
        x_lo = np.log(tl[mask] / F)
        x_hi = np.log(tu[mask] / F)
        sig = sigma[mask]

        # Geometric midpoint for put/call split
        mid_price = np.sqrt(tl[mask] * tu[mask])
        put_mask = mid_price < P0
        call_mask = ~put_mask

        put_label_added = False
        call_label_added = False

        for xlo_i, xhi_i, s, is_put in zip(x_lo, x_hi, sig, put_mask):
            if is_put:
                color = CFG.P_color
                lbl = "Put side (P)" if not put_label_added else None
                put_label_added = True
            else:
                color = CFG.C_color
                lbl = "Call side (C)" if not call_label_added else None
                call_label_added = True

            ax.plot([xlo_i, xhi_i], [s, s], color=color, lw=1.2, label=lbl)

        # Add vertical connector lines at discontinuities
        # Build a sorted list of segment endpoints to identify jumps
        endpoints = []
        for xlo_i, xhi_i, s, is_put in zip(x_lo, x_hi, sig, put_mask):
            color = CFG.P_color if is_put else CFG.C_color
            endpoints.append((xlo_i, s, color, "left"))
            endpoints.append((xhi_i, s, color, "right"))

        endpoints.sort(key=lambda ep: ep[0])  # Sort by x-coordinate

        # Find discontinuities: where two adjacent segments at the same x have different sigma
        for i in range(len(endpoints) - 1):
            x_curr, sig_curr, col_curr, pos_curr = endpoints[i]
            x_next, sig_next, col_next, pos_next = endpoints[i + 1]

            # If x-coordinates match and sigma values differ, draw a vertical connector
            if np.isclose(x_curr, x_next) and not np.isclose(sig_curr, sig_next):
                y_min, y_max = min(sig_curr, sig_next), max(sig_curr, sig_next)
                ax.plot(
                    [x_curr, x_curr], [y_min, y_max], color="gray", lw=0.8, alpha=0.7
                )

        # Reference lines
        ax.axvline(
            np.log(P0 / F), color="green", ls="-", lw=0.8, label=f"P₀ = {P0:.0f} USDC"
        )
        ax.axvline(0.0, color="black", ls="--", lw=0.8, label=f"F = {F:.0f} USDC")

        # Aggregate IV horizontal line
        sigma_agg = iv_res.get("sigma_BS_agg", None)
        if sigma_agg is not None and np.isfinite(sigma_agg):
            ax.axhline(
                sigma_agg,
                color=CFG.ATM_color,
                ls=":",
                lw=1.0,
                label=f"σ_BS(agg) = {sigma_agg:.4f}",
            )

        n_conv = int(conv.sum())
        n_total = len(conv)
        title = f"BS Implied Volatility — {fee_label}  expiry={expiry}  ({n_conv}/{n_total} ticks)"
        if sigma_agg is not None:
            title += f"   σ_BS = {sigma_agg:.4f}"
        ax.set_title(title)
        ax.set_xlabel("log(K / F)")
        ax.set_ylabel("σ_BS (annualized)")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        if x_min is not None or x_max is not None:
            ax.set_xlim(x_min, x_max)

        # y-limits: derive from sigma values whose segment overlaps the visible x window,
        # so off-screen wing ticks with extreme sigma don't inflate the y-axis range.
        in_window = np.ones(len(sig), dtype=bool)
        if x_min is not None:
            in_window &= x_hi >= x_min
        if x_max is not None:
            in_window &= x_lo <= x_max
        visible_sig = sig[in_window]
        visible_sig = visible_sig[np.isfinite(visible_sig)]
        if len(visible_sig) > 0:
            v_range = max(visible_sig.max() - visible_sig.min(), 0.0)
            pad = max(0.01, 0.05 * v_range)
            ax.set_ylim(visible_sig.min() - pad, visible_sig.max() + pad)

    fig.tight_layout()
    _save_figure(fig, out_dir, filename)
