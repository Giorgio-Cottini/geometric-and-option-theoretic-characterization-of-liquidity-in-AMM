"""
Graphics for Impermanent Loss (IL) and the IL replication price integrand.

Public API
----------
plot_IL(liq_df, fee_label, P0, il_results, expiries_F, out_dir, x_min, x_max)
    Pathwise IL(P_T) vs log(P_T / F).  One figure per fee tier; one subplot
    per expiry.  Saved as {IL_out_dir}/{fee_label}s_{n}_expiries.png.

plot_IL_price(liq_df, fee_label, P0, il_results, expiries_F, opt_res,
              out_dir, x_min, x_max)
    IL price integrand L(q)·O(q) vs log(q / F).  The area under this curve
    equals Π^IL (RTW26 eq. 18).  One figure per fee tier; one subplot per
    expiry.  Saved as {IL_price_out_dir}/{fee_label}s_{n}_expiries.png.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from ..math_core import (
    impermanent_loss,
    IL_price_integrand,
    compute_LVR_function,
    compute_I_remainder,
    IL_integrand_I_component,
)
from .config import CFG

# ————————————————————————————————————————————————————————————————————————— #
# Private helpers


def _make_PT_grid(
    liq_df: pd.DataFrame,
    P0: float,
    n: int = 500,
    p_min: float | None = None,
    p_max: float | None = None,
) -> np.ndarray:
    """
    Build a log-uniform P_T grid spanning the active liquidity price range.

    Args:
        liq_df : output of reconstruct_liquidity_cumsum.
        P0     : pool spot price — used as safety lower-bound guard.
        n      : number of grid points.
        p_min  : optional lower bound for the grid (USDC/ETH).
        p_max  : optional upper bound for the grid (USDC/ETH).
    Returns:
        Sorted 1-D float64 array of length n.
    """
    active = liq_df[liq_df["liquidity"] > 0]
    lo = float(active["price_lower"].min())
    hi = float(active["price_upper"].max())
    lo = max(lo, P0 * 1e-3)  # guard against near-zero lower bound
    if p_min is not None:
        lo = max(lo, p_min)
    if p_max is not None:
        hi = min(hi, p_max)
    return np.exp(np.linspace(np.log(lo), np.log(hi), n))


def _save_figure(fig: Figure, out_dir: Path, filename: str) -> None:
    """Create parent directories, save figure, close it, and print confirmation."""
    out_path = out_dir / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  [saved] {out_path}")


# ————————————————————————————————————————————————————————————————————————— #
# Public API


def plot_IL(
    liq_df: pd.DataFrame,
    fee_label: str,
    P0: float,
    il_results: list[dict | None],
    expiries_F: list[tuple[str, float]],
    out_dir: Path | None = None,
    x_min: float | None = CFG.il_x_min,
    x_max: float | None = CFG.il_x_max,
) -> None:
    """
    Plot pathwise IL(P_T) vs log(P_T / F) for one fee tier.

    One subplot per expiry.  Put side (P_T < P₀) in red, call side in blue.
    Vertical lines mark P₀ and F (ATM).  The Π^IL scalar is annotated in
    the subplot title when an il_result is available.

    Args:
        liq_df     : output of reconstruct_liquidity_cumsum for this fee tier.
        fee_label  : short label, e.g. "5bp".
        P0         : pool spot price (USDC/ETH).
        il_results : list of dicts from run_IL_pipeline, one per expiry
                     (None entries still produce the IL curve, just no Π^IL annotation).
        expiries_F : ordered list of (expiry_label, F) pairs matching il_results.
        out_dir    : directory for the output PNG.  None → CFG.IL_out_dir.
        x_min      : optional left  x-axis limit (log-moneyness).
        x_max      : optional right x-axis limit (log-moneyness).
    Saves:
        {out_dir}/{fee_label}s.png
    """
    out_dir = Path(out_dir) if out_dir is not None else CFG.IL_out_dir
    n = len(expiries_F)
    filename = f"{fee_label}s.png"

    fig, axes = plt.subplots(n, 1, figsize=(10, 4 * n))
    if n == 1:
        axes = [axes]

    for ax, (expiry, F), il_res in zip(axes, expiries_F, il_results):
        # Clip P_T grid to displayed x window — keeps y-axis scale sensible
        p_min_val = float(F * np.exp(x_min)) if x_min is not None else None
        p_max_val = float(F * np.exp(x_max)) if x_max is not None else None
        P_T = _make_PT_grid(liq_df, P0, p_min=p_min_val, p_max=p_max_val)
        il = impermanent_loss(liq_df, P0, P_T)
        x = np.log(P_T / F)

        put_mask = P_T < P0
        call_mask = ~put_mask

        ax.plot(x[put_mask], il[put_mask], color=CFG.P_color, label="Put side (P)")  # type: ignore
        ax.plot(x[call_mask], il[call_mask], color=CFG.C_color, label="Call side (C)")  # type: ignore

        ax.axvline(
            np.log(P0 / F), color="green", ls="-", lw=0.8, label=f"P₀ = {P0:.0f} USDC"
        )
        ax.axvline(0.0, color="black", ls="--", lw=0.8, label=f"F = {F:.0f} USDC")
        ax.axhline(0, color="black", lw=0.4)

        title = f"Impermanent Loss — {fee_label}  expiry={expiry}"
        if il_res is not None:
            title += f"   Π^IL = {il_res['IL_price']:,.0f} USD"
        ax.set_title(title)
        ax.set_xlabel("log(P_T / F)")
        ax.set_ylabel("IL (USDC)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

        # Plot same N expiries in another graph
        if x_min is not None or x_max is not None:
            ax.set_xlim(x_min, x_max)

    fig.tight_layout()
    _save_figure(fig, out_dir, filename)


# ————————————————————————————————————————————————————————————————————————— #


def plot_IL_price(
    liq_df: pd.DataFrame,
    fee_label: str,
    P0: float,
    il_results: list[dict | None],
    expiries_F: list[tuple[str, float]],
    opt_res: dict[str, dict],
    out_dir: Path | None = None,
    x_min: float | None = CFG.il_x_min,
    x_max: float | None = CFG.il_x_max,
) -> None:
    """
    Plot the IL price integrand L(q)·O(q) vs log(q / F) for one fee tier.

    The area under this curve equals Π^IL (RTW26 eq. 18).  Put side (q < P₀)
    is shown in red with fill; call side in blue.  The Π^IL scalar is annotated
    in the subplot title.

    Args:
        liq_df     : output of reconstruct_liquidity_cumsum for this fee tier.
        fee_label  : short label, e.g. "5bp".
        P0         : pool spot price (USDC/ETH).
        il_results : list of dicts from run_IL_pipeline, one per expiry.
        expiries_F : ordered list of (expiry_label, F) pairs matching il_results.
        opt_res    : full dict from run_options_pipeline, keyed by expiry label.
                     Used to retrieve the per-expiry interp data for IL_price_integrand.
        out_dir    : directory for the output PNG.  None → CFG.IL_price_out_dir.
        x_min      : optional left  x-axis limit (log-moneyness).
        x_max      : optional right x-axis limit (log-moneyness).
    Saves:
        {out_dir}/{fee_label}s.png
    """
    out_dir = Path(out_dir) if out_dir is not None else CFG.IL_price_out_dir
    n = len(expiries_F)
    filename = f"{fee_label}s.png"

    fig, axes = plt.subplots(n, 1, figsize=(10, 4 * n))
    if n == 1:
        axes = [axes]

    for ax, (expiry, F), il_res in zip(axes, expiries_F, il_results):
        if expiry not in opt_res:
            ax.set_title(
                f"IL Price Integrand — {fee_label}  expiry={expiry}  [no option data]"
            )
            continue

        interp = opt_res[expiry]["interp"]

        # Clip q grid to the displayed x-axis window for performance
        p_lo = float(F * np.exp(x_min)) if x_min is not None else None
        p_hi = float(F * np.exp(x_max)) if x_max is not None else None
        q_grid = _make_PT_grid(liq_df, P0, n=1000, p_min=p_lo, p_max=p_hi)
        integrand = IL_price_integrand(liq_df, interp, P0, q_grid)
        x = np.log(q_grid / F)

        put_mask = q_grid < P0
        call_mask = ~put_mask

        ax.plot(
            x[put_mask],
            integrand[put_mask],
            color=CFG.P_color,
            lw=1.4,
            label="Put side: L(q)·P(q)",
        )
        ax.plot(
            x[call_mask],
            integrand[call_mask],
            color=CFG.C_color,
            lw=1.4,
            label="Call side: L(q)·C(q)",
        )
        ax.fill_between(x[put_mask], integrand[put_mask], color=CFG.P_color, alpha=0.2)
        ax.fill_between(
            x[call_mask], integrand[call_mask], color=CFG.C_color, alpha=0.2
        )

        ax.axvline(
            np.log(P0 / F), color="green", ls="-", lw=0.8, label=f"P₀ = {P0:.0f}"
        )
        ax.axvline(0.0, color="black", ls="--", lw=0.8, label=f"ATM  F={F:.0f}")
        ax.axhline(0, color="black", lw=0.4)

        title = f"IL Price Integrand — {fee_label}  expiry={expiry}"
        if il_res is not None:
            title += f"   Π^IL = {il_res['IL_price']:,.0f} USD"
        ax.set_title(title)
        ax.set_xlabel("log(K / F)")
        ax.set_ylabel("L(q) · O(q)  [USD / USDC]")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

        if x_min is not None or x_max is not None:
            ax.set_xlim(x_min, x_max)

    fig.tight_layout()
    _save_figure(fig, out_dir, filename)


# ————————————————————————————————————————————————————————————————————————— #


def plot_IL_LVR(
    liq_df: pd.DataFrame,
    fee_label: str,
    P0: float,
    expiries_F: list[tuple[str, float]],
    il_results: list[dict | None] | None = None,
    out_dir: Path | None = None,
    x_min: float | None = CFG.il_x_min,
    x_max: float | None = CFG.il_x_max,
) -> None:
    """
    Plot pathwise IL(P_T) decomposed into LVR and hedging cost components.

    Decomposition (RTW26 §3.2.1, eq. 14 + eq. 17):
        IL(P_T) = [Ψ(P_T) − Ψ(P_0)]  +  hedging_cost(P_T)
    where Ψ is the second antiderivative of L (Ψ'' = L), so:
        E^Q[Ψ(P_T) − Ψ(P_0)] = E^Q[LVR_T]   (LVR replication price)
        E^Q[hedging_cost(P_T)] = I(P_0)       (hedging price, ≤ 0)

    Green fill:        between Ψ(P_T) − Ψ(P_0) and zero.
    Light-green fill:  between IL(P_T) and Ψ(P_T) − Ψ(P_0) (hedging cost).

    Note: Ψ(P_T) − Ψ(P_0) > 0 for P_T > P_0 and < 0 for P_T < P_0.  The hedging
    cost magnitude is typically much larger than net IL, revealing partial
    cancellation between LVR and hedging components.

    Args:
        liq_df     : output of reconstruct_liquidity_cumsum for this fee tier.
        fee_label  : short label, e.g. "5bp".
        P0         : pool spot price (USDC/ETH).
        expiries_F : ordered list of (expiry_label, F) pairs.
        il_results : optional list of dicts from run_IL_pipeline; used for title
                     annotation of Π^IL, I, and LVR prices.  None → no annotation.
        out_dir    : directory for the output PNG.  None → CFG.IL_out_dir.
        x_min      : optional left  x-axis limit (log-moneyness).
        x_max      : optional right x-axis limit (log-moneyness).
    Saves:
        {out_dir}/{fee_label}s_LVR.png
    """
    out_dir = Path(out_dir) if out_dir is not None else CFG.IL_out_dir
    n = len(expiries_F)
    filename = f"{fee_label}s_LVR.png"

    fig, axes = plt.subplots(n, 1, figsize=(10, 4 * n))
    if n == 1:
        axes = [axes]

    il_list = il_results if il_results is not None else [None] * n

    for ax, (expiry, F), il_res in zip(axes, expiries_F, il_list):
        # I remainder depends on the forward price — compute per expiry
        I_val = compute_I_remainder(liq_df, P0, F)
        p_min_val = float(F * np.exp(x_min)) if x_min is not None else None
        p_max_val = float(F * np.exp(x_max)) if x_max is not None else None
        P_T = _make_PT_grid(liq_df, P0, p_min=p_min_val, p_max=p_max_val)
        il = impermanent_loss(liq_df, P0, P_T)
        lvr = compute_LVR_function(liq_df, P0, P_T)
        x = np.log(P_T / F)

        # LVR region: fill between Ψ(P_T)−Ψ(P_0) and the x-axis
        ax.fill_between(
            x, lvr, 0,
            color=CFG.LVR_color, alpha=0.35,
            label="LVR proxy Ψ(P_T)−Ψ(P₀)",
        )
        # Hedging cost region: fill between IL and LVR proxy
        ax.fill_between(
            x, il, lvr,
            color=CFG.hedge_color, alpha=0.45,
            label=f"Hedging cost  [E^Q = I = {I_val:,.0f} USD]",
        )

        # IL curve and LVR proxy curve on top
        put_mask = P_T < P0
        call_mask = ~put_mask
        ax.plot(x[put_mask], il[put_mask], color=CFG.P_color, lw=1.4, label="IL — put side")
        ax.plot(x[call_mask], il[call_mask], color=CFG.C_color, lw=1.4, label="IL — call side")
        ax.plot(x, lvr, color=CFG.LVR_color, lw=1.0, ls="--", label="LVR proxy curve")

        ax.axvline(
            np.log(P0 / F), color="green", ls="-", lw=0.8, label=f"P₀ = {P0:.0f} USDC"
        )
        ax.axvline(0.0, color="black", ls="--", lw=0.8, label=f"F = {F:.0f} USDC")
        ax.axhline(0, color="black", lw=0.4)

        title = f"IL Decomposition: LVR + Hedging Cost — {fee_label}  expiry={expiry}"
        if il_res is not None:
            pi_il = il_res["IL_price"]
            title += f"   Π^IL={pi_il:,.0f}  I={I_val:,.0f}  LVR={pi_il - I_val:,.0f}"
        ax.set_title(title)
        ax.set_xlabel("log(P_T / F)")
        ax.set_ylabel("Value (USDC)")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        if x_min is not None or x_max is not None:
            ax.set_xlim(x_min, x_max)

    fig.tight_layout()
    _save_figure(fig, out_dir, filename)


# ————————————————————————————————————————————————————————————————————————— #


def plot_IL_price_I(
    liq_df: pd.DataFrame,
    fee_label: str,
    P0: float,
    il_results: list[dict | None],
    expiries_F: list[tuple[str, float]],
    opt_res: dict[str, dict],
    out_dir: Path | None = None,
    x_min: float | None = CFG.il_x_min,
    x_max: float | None = CFG.il_x_max,
) -> None:
    """
    Plot the IL price integrand decomposed into LVR and I components.

    From RTW26 Appendix C (Proposition C.1, r=δ=0):
        Π^IL = ∫₀^∞ L(q) C(q,T) dq  +  I(P_0)
        I(P_0) = ∫₀^{P_0} L(q)(q − P_0) dq  ≤ 0

    The existing integrand L(q)·O(q) is shown as lines (no fill) to represent Π^IL.
    The I-component integrand L(q)·(q − P_0) is shown as a green shaded region
    below the x-axis on the put side (q < P_0), representing the negative correction
    that converts put prices to call-equivalent prices.

    Visual interpretation:
        Red curve  (q < P₀): L(q)·P(q)  — put integrand
        Blue curve (q ≥ P₀): L(q)·C(q)  — call integrand
        Green area (q < P₀): L(q)·(q−P₀) below x-axis — I component (< 0)

    Args:
        liq_df     : output of reconstruct_liquidity_cumsum for this fee tier.
        fee_label  : short label, e.g. "5bp".
        P0         : pool spot price (USDC/ETH).
        il_results : list of dicts from run_IL_pipeline, one per expiry.
        expiries_F : ordered list of (expiry_label, F) pairs matching il_results.
        opt_res    : full dict from run_options_pipeline.
        out_dir    : directory for the output PNG.  None → CFG.IL_price_out_dir.
        x_min      : optional left  x-axis limit (log-moneyness).
        x_max      : optional right x-axis limit (log-moneyness).
    Saves:
        {out_dir}/{fee_label}s_I.png
    """
    out_dir = Path(out_dir) if out_dir is not None else CFG.IL_price_out_dir
    n = len(expiries_F)
    filename = f"{fee_label}s_I.png"

    fig, axes = plt.subplots(n, 1, figsize=(10, 4 * n))
    if n == 1:
        axes = [axes]

    for ax, (expiry, F), il_res in zip(axes, expiries_F, il_results):
        if expiry not in opt_res:
            ax.set_title(
                f"IL Price Decomposed — {fee_label}  expiry={expiry}  [no option data]"
            )
            continue

        # I remainder depends on the forward price — compute per expiry
        I_val = compute_I_remainder(liq_df, P0, F)
        interp = opt_res[expiry]["interp"]
        p_lo = float(F * np.exp(x_min)) if x_min is not None else None
        p_hi = float(F * np.exp(x_max)) if x_max is not None else None
        q_grid = _make_PT_grid(liq_df, P0, n=1000, p_min=p_lo, p_max=p_hi)
        integrand = IL_price_integrand(liq_df, interp, P0, q_grid)
        i_comp = IL_integrand_I_component(liq_df, P0, F, q_grid)
        x = np.log(q_grid / F)

        put_mask = q_grid < P0
        call_mask = ~put_mask

        # Integrand lines only (no fill) — represent Π^IL = LVR + I
        ax.plot(
            x[put_mask], integrand[put_mask],
            color=CFG.P_color, lw=1.4, label="L(q)·P(q)  put side",
        )
        ax.plot(
            x[call_mask], integrand[call_mask],
            color=CFG.C_color, lw=1.4, label="L(q)·C(q)  call side",
        )

        # I component: green shaded region below x-axis on put side
        x_put = x[put_mask]
        i_put = i_comp[put_mask]
        finite_i = np.isfinite(i_put)
        if finite_i.any():
            ax.fill_between(
                x_put[finite_i], i_put[finite_i], 0,
                color=CFG.LVR_color, alpha=0.4,
                label=f"I component = {I_val:,.0f} USD",
            )
            ax.plot(x_put[finite_i], i_put[finite_i], color=CFG.LVR_color, lw=1.0, ls="--")

        ax.axvline(
            np.log(P0 / F), color="green", ls="-", lw=0.8, label=f"P₀ = {P0:.0f}"
        )
        ax.axvline(0.0, color="black", ls="--", lw=0.8, label=f"ATM  F={F:.0f}")
        ax.axhline(0, color="black", lw=0.4)

        title = f"IL Price Decomposed (Π^IL = LVR + I) — {fee_label}  expiry={expiry}"
        if il_res is not None:
            pi_il = il_res["IL_price"]
            title += f"   Π^IL={pi_il:,.0f}  I={I_val:,.0f}  LVR={pi_il - I_val:,.0f}"
        ax.set_title(title)
        ax.set_xlabel("log(K / F)")
        ax.set_ylabel("L(q) · O(q)  [USD / USDC]")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

        if x_min is not None or x_max is not None:
            ax.set_xlim(x_min, x_max)

    fig.tight_layout()
    _save_figure(fig, out_dir, filename)
