"""
Arbitrage-free IL replication price (IL price) for Uniswap V3 liquidity profiles.

Implements the risk-neutral IL replication price from RTW26 (eq. 18):

    Π^IL = ∫₀^P0  L(q) · P^mkt(q, T) dq   [put leg]
         + ∫_P0^∞  L(q) · C^mkt(q, T) dq   [call leg]

where:
  - L(q) = ℓ(q) / (2q^{3/2})  is the liquidity profile derived from Uniswap V3 tick data.
  - ℓ(q)                       is the piecewise-constant intrinsic liquidity.
  - Π^IL                       is the arbitrage-free IL replication price (NOT the IL itself).

The integral is evaluated exactly via a closed-form antiderivative.  On each
sub-interval of the merged tick-boundary × option-strike grid, both ℓ and
O^mkt are individually piecewise-affine, giving:

    F(q) = ℓ · (a₁·√q  −  a₀/√q)      with  O(q) = a₀ + a₁·q

The integral over each sub-interval is F(b) − F(a), summed across the grid.

Black-Scholes scope
-------------------
All public functions in this module (prefixed BS_) operate under the
Black-Scholes model: option prices are piecewise-affine proxies from
linear_interpolation, passed as pre-computed (strikes, prices) arrays.
"""

import numpy as np
import pandas as pd
from .liquidity_profile import piecewise_constant_liquidity_profile
from ..data_processing import _sep

# ———————————————————————————————————————————————————————————————————————————————————————————— #


def run_IL_pipeline(
    liq_df: pd.DataFrame,
    opt_res: dict[str, dict],
    P0: float,
    fee_bps: int,
    expiry: str,
    verbose: bool = True,
) -> dict | None:
    """
    Run the full IL replication pipeline for one fee tier and one expiry.

    Combines pre-processed option data (from run_options_pipeline) with the
    reconstructed Uniswap V3 liquidity profile to compute the arbitrage-free
    IL replication price Π^IL (RTW26 eq. 18) via BS_compute_IL_price.

    Integration domain: [min(K_put), P0] ∪ [P0, max(K_call)], i.e. truncated
    to the observed post-fill strike range. Tail mass outside this range is
    omitted; it is negligible for concentrated Uniswap V3 liquidity profiles.

    Args:
        liq_df  : output of reconstruct_liquidity_cumsum for this fee tier.
        opt_res : dict returned by run_options_pipeline:
                  {expiry_label -> {"filtered", "filled", "interp"}}.
        P0      : Uniswap pool spot price (USDC) — the put/call split point.
        fee_bps : fee tier label (used in printed output only).
        expiry  : expiry label to evaluate, e.g. "25SEP26".
    Returns:
        dict from BS_compute_IL_price, or None if expiry is unavailable.
        Keys: expiry, P0, F, put_total, call_total, IL_price,
              put_K_lo, put_K_hi, put_contrib,
              call_K_lo, call_K_hi, call_contrib.
    """
    if verbose:
        _sep()
        print(f"IL PIPELINE — ETH/USDC {fee_bps}bp   expiry={expiry}")

    # Validate expiry
    exp_data = opt_res.get(expiry)
    if exp_data is None:
        available = sorted(opt_res.keys())
        if verbose:
            print(f"  [SKIP] expiry '{expiry}' not found. Available: {available}")
        return None
    F = float(exp_data["filled"]["forward"].iloc[0])

    # Compute IL replication price
    il = BS_compute_IL_price(
        liq_df=liq_df,
        interp=exp_data["interp"],
        P0=P0,
        F=F,
        expiry=expiry,
    )

    if verbose:
        # Print numerical summary
        print(f"  P0 = {il['P0']:.2f} USDC    F = {il['F']:.2f} USDC")
        print(
            f"  Put  leg : {il['put_total']:>16.4f} USD   ({len(il['put_contrib'])}  sub-intervals)"
        )
        print(
            f"  Call leg : {il['call_total']:>16.4f} USD   ({len(il['call_contrib'])} sub-intervals)"
        )
        print(f"  Π^IL     : {il['IL_price']:>16.4f} USD")

    return il


# ———————————————————————————————————————————————————————————————————————————————————————————— #
#  Closed-form antiderivative of L(q) · O(q)


def _antiderivative(q: float, ell: float, a0: float, a1: float) -> float:
    """
    Evaluate the antiderivative of L(q) · O(q) at q.

    On a sub-interval where ℓ is constant and O^mkt(q) = a₀ + a₁·q:

        L(q) · O(q)  =  ℓ/(2q^{3/2}) · (a₀ + a₁·q)
                     =  ℓ/2 · ( a₀·q^{−3/2} + a₁·q^{−1/2} )

        ∫ L(q)·O(q) dq  =  ℓ · ( a₁·√q  −  a₀/√q )          ← F(q)

    Args:
        q  : evaluation point (must be > 0).
        ell: constant intrinsic liquidity ℓ on this sub-interval.
        a0 : intercept of affine option price: O(q) = a₀ + a₁·q.
        a1 : slope    of affine option price.
    Returns:
        F(q) = ℓ · (a₁·√q − a₀/√q).
    """
    sqrt_q = np.sqrt(q)
    return ell * (a1 * sqrt_q - a0 / sqrt_q)


# ———————————————————————————————————————————————————————————————————————————————————————————— #
# Build the merged integration grid


def _build_merged_grid(
    opt_strikes: np.ndarray,
    tick_lower: np.ndarray,
    tick_upper: np.ndarray,
    q_lo: float,
    q_hi: float,
) -> np.ndarray:
    """
    Merge option-strike and tick-boundary breakpoints into a sorted unique grid.

    On each sub-interval of the resulting grid, both ℓ(q) and O^mkt(q) are
    individually piece-affine (ℓ constant, O linear), which is the prerequisite
    for applying the closed-form antiderivative.

    Args:
        opt_strikes          : sorted array of option strikes.
        tick_lower/tick_upper: tick interval boundaries from piecewise_constant_liquidity_profile.
        q_lo, q_hi           : integration domain for this leg.
    Returns:
        Sorted unique 1-D array of breakpoints clipped to [q_lo, q_hi].
    """
    strikes_in = opt_strikes[(opt_strikes >= q_lo) & (opt_strikes <= q_hi)]
    tick_bounds = np.concatenate([tick_lower, tick_upper])
    ticks_in = tick_bounds[(tick_bounds >= q_lo) & (tick_bounds <= q_hi)]

    all_points = np.concatenate([[q_lo, q_hi], strikes_in, ticks_in])
    return np.unique(all_points)


# ———————————————————————————————————————————————————————————————————————————————————————————— #
# Integrate one leg using the closed-form antiderivative


def _integrate_leg(
    opt_strikes: np.ndarray,
    opt_prices: np.ndarray,
    tick_lower: np.ndarray,
    tick_upper: np.ndarray,
    tick_ell: np.ndarray,
    q_lo: float,
    q_hi: float,
) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """
    Integrate L(q) · O^mkt(q) over [q_lo, q_hi] using the closed-form antiderivative.

    Sub-interval loop
    -----------------
    For each consecutive pair (a, b) in the merged grid:

      1. Locate the tick interval containing the midpoint → ℓ.
         Uses searchsorted on tick_lower: last tick whose lower bound ≤ mid.
         Skips if the midpoint falls in a gap between tick intervals (ℓ = 0 gap).
      2. If ℓ = 0, skip (no liquidity; no IL exposure in this interval).
      3. Interpolate O^mkt at a and b via np.interp (linear; clamps at boundaries
         outside the option strike range — acceptable for tails).
      4. Derive affine coefficients: a₁ = (O_b − O_a)/(b − a), a₀ = O_a − a₁·a.
      5. contrib = F(b) − F(a) via _antiderivative.

    Args:
        opt_strikes, opt_prices: sorted arrays from linear_interpolation.
        tick_lower, tick_upper : tick boundaries from piecewise_constant_liquidity_profile.
        tick_ell               : ℓ values from piecewise_constant_liquidity_profile.
        q_lo, q_hi             : integration domain for this leg.
    Returns:
        total      : scalar integral value (float).
        sub_K_lo   : left  endpoint of each contributing sub-interval.
        sub_K_hi   : right endpoint of each contributing sub-interval.
        sub_contrib: integral contribution of each sub-interval.
    """
    grid = _build_merged_grid(opt_strikes, tick_lower, tick_upper, q_lo, q_hi)

    sub_K_lo_list: list[float] = []
    sub_K_hi_list: list[float] = []
    sub_contrib_list: list[float] = []

    for i in range(len(grid) - 1):
        a, b = grid[i], grid[i + 1]
        if b <= a:
            continue

        # searchsorted(tick_lower, mid, side="right") - 1 gives the last index
        # where tick_lower[idx] ≤ mid, i.e. the candidate tick interval.
        mid = 0.5 * (a + b)
        tick_idx = int(np.searchsorted(tick_lower, mid, side="right")) - 1

        if tick_idx < 0 or tick_idx >= len(tick_ell):
            continue  # mid is outside all tick intervals
        if mid > tick_upper[tick_idx]:
            continue  # mid falls in a gap between tick intervals

        ell = tick_ell[tick_idx]
        if ell == 0:
            continue

        # Affine option price on [a, b]: O(q) = a₀ + a₁·q
        O_a = float(np.interp(a, opt_strikes, opt_prices))
        O_b = float(np.interp(b, opt_strikes, opt_prices))
        a1_coef = (O_b - O_a) / (b - a)
        a0_coef = O_a - a1_coef * a

        contrib = _antiderivative(b, ell, a0_coef, a1_coef) - _antiderivative(
            a, ell, a0_coef, a1_coef
        )

        sub_K_lo_list.append(a)
        sub_K_hi_list.append(b)
        sub_contrib_list.append(contrib)

    sub_K_lo = np.array(sub_K_lo_list, dtype=float)
    sub_K_hi = np.array(sub_K_hi_list, dtype=float)
    sub_contrib = np.array(sub_contrib_list, dtype=float)
    total = float(sub_contrib.sum()) if sub_contrib.size > 0 else 0.0

    return total, sub_K_lo, sub_K_hi, sub_contrib


# ———————————————————————————————————————————————————————————————————————————————————————————— #
# Public entry point (Black-Scholes)


def BS_compute_IL_price(
    liq_df: pd.DataFrame,
    interp: dict[str, tuple[np.ndarray, np.ndarray]],
    P0: float,
    F: float,
    expiry: str = "25SEP26",
) -> dict:
    """
    Compute the arbitrage-free IL replication price Π^IL (RTW26 eq. 18)
    under the Black-Scholes model:

        Π^IL = ∫₀^P0  L(q) · P^mkt(q, T) dq + ∫_P0^∞  L(q) · C^mkt(q, T) dq

    Note: Π^IL is the risk-neutral price of the IL exposure, NOT the IL itself.

    Args:
        liq_df : output of reconstruct_liquidity_cumsum.
        interp : pre-computed piecewise-affine option proxy from linear_interpolation.
                 Dict keyed by "C" and "P", values are (strikes, prices) arrays.
        P0     : Uniswap pool spot price (USD); defines the put/call split.
        F      : Deribit forward price for this expiry (used for log-moneyness
                 in downstream plots).
        expiry : expiry label string, e.g. "25SEP26".  Default "25SEP26".
    Returns:
        dict with keys:
            "expiry"       str         — expiry label.
            "P0"           float       — pool spot price.
            "F"            float       — forward price.
            "put_total"    float       — put  leg integral value.
            "call_total"   float       — call leg integral value.
            "IL_price"     float       — Π^IL = put_total + call_total.
            "put_K_lo"     np.ndarray  — put  leg sub-interval left  endpoints.
            "put_K_hi"     np.ndarray  — put  leg sub-interval right endpoints.
            "put_contrib"  np.ndarray  — put  leg per-sub-interval contributions.
            "call_K_lo"    np.ndarray  — call leg sub-interval left  endpoints.
            "call_K_hi"    np.ndarray  — call leg sub-interval right endpoints.
            "call_contrib" np.ndarray  — call leg per-sub-interval contributions.
    Raises:
        KeyError: if type "C" or "P" is absent in interp.
    """
    for leg_type in ("C", "P"):
        if leg_type not in interp:
            raise KeyError(f"Option type '{leg_type}' missing for expiry '{expiry}'.")
    options = interp

    q_lower, q_upper, ell = piecewise_constant_liquidity_profile(liq_df)

    # Put leg: ∫_{min(K_p)}^{P0} L(q) · P^mkt(q) dq
    K_p, P_p = options["P"]
    put_total, put_K_lo, put_K_hi, put_contrib = _integrate_leg(
        opt_strikes=K_p,
        opt_prices=P_p,
        tick_lower=q_lower,
        tick_upper=q_upper,
        tick_ell=ell,
        q_lo=float(K_p.min()),
        q_hi=float(P0),
    )

    # Call leg: ∫_{P0}^{max(K_c)} L(q) · C^mkt(q) dq
    K_c, P_c = options["C"]
    call_total, call_K_lo, call_K_hi, call_contrib = _integrate_leg(
        opt_strikes=K_c,
        opt_prices=P_c,
        tick_lower=q_lower,
        tick_upper=q_upper,
        tick_ell=ell,
        q_lo=float(P0),
        q_hi=float(K_c.max()),
    )

    return {
        "expiry": expiry,
        "P0": float(P0),
        "F": float(F),
        "put_total": put_total,
        "call_total": call_total,
        "IL_price": put_total + call_total,
        "put_K_lo": put_K_lo,
        "put_K_hi": put_K_hi,
        "put_contrib": put_contrib,
        "call_K_lo": call_K_lo,
        "call_K_hi": call_K_hi,
        "call_contrib": call_contrib,
    }


# ———————————————————————————————————————————————————————————————————————————————————————————— #
def _reserve_integrals(
    p: float,
    q_lower: np.ndarray,
    q_upper: np.ndarray,
    ell: np.ndarray,
) -> tuple[float, float]:
    """
    Compute x(p) and y(p) from the piecewise-constant liquidity profile.

        x(p) = ∫_p^∞  L(q) dq  =  Σ_i  ℓ_i · (1/√a  −  1/√b)
        y(p) = ∫_0^p  q·L(q) dq  =  Σ_i  ℓ_i · (√b  −  √a)

    where [a, b] = [q_lower_i, q_upper_i] ∩ relevant half-line, clipped to p.

    Args:
        p        : price at which to evaluate the reserves.
        q_lower  : tick interval left  endpoints (sorted ascending).
        q_upper  : tick interval right endpoints.
        ell      : intrinsic liquidity on each interval.
    Returns:
        (x_p, y_p): ETH reserve x(p) and USDC reserve y(p).
    """
    x_p = 0.0
    y_p = 0.0
    for lo, hi, l in zip(q_lower, q_upper, ell):
        if l == 0:
            continue
        # x(p) = ∫_p^∞: active on intervals above p
        a_x = max(lo, p)
        b_x = hi
        if b_x > a_x:
            x_p += l * (1.0 / np.sqrt(a_x) - 1.0 / np.sqrt(b_x))
        # y(p) = ∫_0^p: active on intervals below p
        a_y = lo
        b_y = min(hi, p)
        if b_y > a_y:
            y_p += l * (np.sqrt(b_y) - np.sqrt(a_y))
    return x_p, y_p


# ———————————————————————————————————————————————————————————————————————————————————————————— #


def impermanent_loss(
    liq_df: pd.DataFrame,
    P0: float,
    P_T: float | np.ndarray,
) -> float | np.ndarray:
    """
    Compute the pathwise Impermanent Loss IL(P_T) for a given realized price P_T.

    Definition (RTW26 / standard):

        IL(P_T) = V_L(P_T) − V_hold(P_T)

    where:
        V_L(P_T)    = x(P_T)·P_T + y(P_T)          pool value at P_T
        V_hold(P_T) = x(P_0)·P_T + y(P_0)           buy-and-hold value at P_T
        x(p), y(p)  = reserve functions at price p (RTW26 eq. 4)

    IL(P_T) ≤ 0 always (the pool underperforms the initial basket at any P_T ≠ P_0).

    Args:
        liq_df : output of reconstruct_liquidity_cumsum.
        P0     : pool price at entry (USDC per ETH).
        P_T    : realized terminal price(s); scalar or 1-D np.ndarray.
    Returns:
        IL(P_T): scalar or array of the same shape as P_T.
    """
    q_lower, q_upper, ell = piecewise_constant_liquidity_profile(liq_df)

    x0, y0 = _reserve_integrals(P0, q_lower, q_upper, ell)

    scalar_input = np.ndim(P_T) == 0
    P_T_arr = np.atleast_1d(np.asarray(P_T, dtype=float))

    il = np.empty_like(P_T_arr)
    for idx, pt in enumerate(P_T_arr):
        x_t, y_t = _reserve_integrals(pt, q_lower, q_upper, ell)
        V_pool = x_t * pt + y_t
        V_hold = x0 * pt + y0
        il[idx] = V_pool - V_hold

    return float(il[0]) if scalar_input else il


# ———————————————————————————————————————————————————————————————————————————————————————————— #


def IL_price_integrand(
    liq_df: pd.DataFrame,
    interp: dict[str, tuple[np.ndarray, np.ndarray]],
    P0: float,
    q_grid: np.ndarray,
) -> np.ndarray:
    """
    Evaluate the IL price integrand  L(q) · O(q)  on a grid of prices q.

    The integral of this function over all q gives the IL replication price Π^IL:

        Π^IL = ∫₀^P0  L(q) · P^mkt(q) dq  +  ∫_P0^∞  L(q) · C^mkt(q) dq

    where L(q) = ℓ(q) / (2·q^{3/2})  (RTW26 eq. 4).

    Put options are used for q < P0, call options for q ≥ P0.

    Args:
        liq_df : output of reconstruct_liquidity_cumsum.
        interp : dict {"C": (strikes, prices), "P": (strikes, prices)},
                 as returned by linear_interpolation.
        P0     : pool spot price (USDC) — put/call split point.
        q_grid : 1-D float64 array of evaluation prices (sorted ascending).
    Returns:
        1-D float64 array of L(q)·O(q) values, same length as q_grid.
        NaN at points where ℓ = 0 (no liquidity) or q is outside all tick intervals.
    """
    q_lower, q_upper, ell_arr = piecewise_constant_liquidity_profile(liq_df)
    K_p, P_p = interp["P"]
    K_c, P_c = interp["C"]

    result = np.full(len(q_grid), np.nan, dtype=float)
    for i, q in enumerate(q_grid):
        # Locate the tick interval containing q via binary search
        idx = int(np.searchsorted(q_lower, q, side="right")) - 1
        if idx < 0 or idx >= len(ell_arr):
            continue
        if q > q_upper[idx]:
            continue  # q falls in a gap between tick intervals
        el = ell_arr[idx]
        if el == 0.0:
            continue
        L_q = el / (2.0 * q ** 1.5)
        O_q = (
            float(np.interp(q, K_p, P_p))
            if q < P0
            else float(np.interp(q, K_c, P_c))
        )
        result[i] = L_q * O_q
    return result


# ———————————————————————————————————————————————————————————————————————————————————————————— #


def compute_LVR_function(
    liq_df: pd.DataFrame,
    P0: float,
    P_T: np.ndarray,
) -> np.ndarray:
    """
    Compute the LVR proxy function Ψ(P_T) − Ψ(P_0) for an array of terminal prices.

    Ψ(P) = ∫₀^P (P − q) L(q) dq  is the second antiderivative of L (Ψ'' = L).

    By Itô's formula applied to Ψ(P_t):
        E^Q[LVR_T] = E^Q[Ψ(P_T)] − Ψ(P_0)   (RTW26 eq. 17)

    The pointwise function Ψ(P_T) − Ψ(P_0) decomposes the pathwise IL profile:
        IL(P_T) = [Ψ(P_T) − Ψ(P_0)]  +  hedging_cost(P_T)
    where the first term integrates to the LVR replication price under Q.

    Numerically:
        Ψ(P) = P · (x_total − x(P)) − y(P)
    where x_total = Σᵢ ℓᵢ(1/√aᵢ − 1/√bᵢ) is the total ETH measure (finite since
    all tick lower bounds > 0), x(P) and y(P) come from _reserve_integrals.

    Vectorised over P_T via numpy broadcasting: O(n_ticks × n_PT) operations.

    Args:
        liq_df : output of reconstruct_liquidity_cumsum.
        P0     : pool spot price (USDC/ETH).
        P_T    : 1-D float64 array of terminal prices.
    Returns:
        1-D float64 array of Ψ(P_T) − Ψ(P_0), same length as P_T.
        Positive for P_T > P_0 (LVR-dominant region), negative for P_T < P_0.
    """
    q_lower, q_upper, ell = piecewise_constant_liquidity_profile(liq_df)

    # Total ETH measure x(0⁺): finite because all tick lower bounds > 0
    x_total = float(np.sum(ell * (1.0 / np.sqrt(q_lower) - 1.0 / np.sqrt(q_upper))))

    # Broadcast over (n_PT, n_ticks) to compute x(P) and y(P) for all P_T at once
    P_col = P_T[:, None]        # (n_PT, 1)
    lo = q_lower[None, :]       # (1, n_ticks)
    hi = q_upper[None, :]       # (1, n_ticks)
    l = ell[None, :]            # (1, n_ticks)

    # x(P) = Σᵢ ℓᵢ · (1/√max(loᵢ, P) − 1/√hiᵢ)  for hiᵢ > max(loᵢ, P)
    a_x = np.maximum(lo, P_col)
    valid_x = (hi > a_x) & (l > 0)
    x_P = np.where(valid_x, l * (1.0 / np.sqrt(a_x) - 1.0 / np.sqrt(hi)), 0.0).sum(axis=1)

    # y(P) = Σᵢ ℓᵢ · (√min(hiᵢ, P) − √loᵢ)  for min(hiᵢ, P) > loᵢ
    b_y = np.minimum(hi, P_col)
    valid_y = (b_y > lo) & (l > 0)
    y_P = np.where(valid_y, l * (np.sqrt(b_y) - np.sqrt(lo)), 0.0).sum(axis=1)

    Psi_PT = P_T * (x_total - x_P) - y_P

    # Ψ(P_0) (scalar)
    a_x0 = np.maximum(q_lower, P0)
    valid_x0 = (q_upper > a_x0) & (ell > 0)
    x_P0 = float(np.where(valid_x0, ell * (1.0 / np.sqrt(a_x0) - 1.0 / np.sqrt(q_upper)), 0.0).sum())
    b_y0 = np.minimum(q_upper, P0)
    valid_y0 = (b_y0 > q_lower) & (ell > 0)
    y_P0 = float(np.where(valid_y0, ell * (np.sqrt(b_y0) - np.sqrt(q_lower)), 0.0).sum())
    Psi_P0 = P0 * (x_total - x_P0) - y_P0

    return Psi_PT - Psi_P0


# ———————————————————————————————————————————————————————————————————————————————————————————— #


def compute_I_remainder(liq_df: pd.DataFrame, P0: float, F_fwd: float) -> float:
    """
    Compute the integral remainder I(P_0, F) from RTW26 Appendix C (r=δ=0):

        I(P_0, F) = ∫₀^{P_0} L(q)(q − F) dq  ≤ 0

    Derived by applying put-call parity P(q,T) = C(q,T) − (F − q) to the put leg
    of Π^IL (valid for r=δ=0):

        Π^IL = ∫₀^∞ L(q) C(q,T) dq  +  I(P_0, F)

    so  E^Q[LVR_T] = Π^IL − I(P_0, F) > 0   (LVR replication price)
    and I(P_0, F) ≤ 0.

    Note: RTW26 Appendix C writes the kernel as (q − P_0) because it assumes
    r=δ=0 → F=P_0 analytically.  In practice F is taken from Deribit and may
    differ from P_0 by up to ~50 USDC at long maturities; using P_0 would make
    I constant across expiries and corrupt the LVR decomposition.

    Exact closed-form via _antiderivative with a₀ = −F_fwd, a₁ = 1:
        ∫_a^b L(q)(q − F)dq = _antiderivative(b, ℓ, −F, 1) − _antiderivative(a, ℓ, −F, 1)
                             = ℓ [(√b − √a) − F(1/√a − 1/√b)]

    Args:
        liq_df : output of reconstruct_liquidity_cumsum.
        P0     : pool spot price (USDC/ETH) — upper integration limit.
        F_fwd  : forward price for this expiry (USDC/ETH) — used in the kernel.
    Returns:
        I(P_0, F): a non-positive scalar.
    """
    q_lower, q_upper, ell_arr = piecewise_constant_liquidity_profile(liq_df)
    total = 0.0
    for lo, hi, el in zip(q_lower, q_upper, ell_arr):
        if el == 0.0:
            continue
        a = lo
        b = min(hi, P0)
        if b <= a:
            continue
        total += _antiderivative(b, el, -F_fwd, 1.0) - _antiderivative(a, el, -F_fwd, 1.0)
    return total


# ———————————————————————————————————————————————————————————————————————————————————————————— #


def IL_integrand_I_component(
    liq_df: pd.DataFrame,
    P0: float,
    F_fwd: float,
    q_grid: np.ndarray,
) -> np.ndarray:
    """
    Evaluate the I-component integrand L(q)·(q − F) on a grid of prices q.

    This is the integrand of the integral remainder I(P_0, F):
        I(P_0, F) = ∫₀^{P_0} L(q)(q − F) dq  ≤ 0

    The function is non-positive for q ∈ (0, P_0) (since q < P_0 ≤ F) and NaN
    elsewhere (q ≥ P_0 or q outside all active tick intervals).

    Args:
        liq_df : output of reconstruct_liquidity_cumsum.
        P0     : pool spot price (USDC/ETH) — upper integration limit.
        F_fwd  : forward price for this expiry — used in the kernel (not P_0).
        q_grid : 1-D float64 array of evaluation prices (sorted ascending).
    Returns:
        1-D float64 array, same length as q_grid.
        NaN for q ≥ P_0 or outside all tick intervals.
    """
    q_lower, q_upper, ell_arr = piecewise_constant_liquidity_profile(liq_df)
    result = np.full(len(q_grid), np.nan, dtype=float)
    for i, q in enumerate(q_grid):
        if q >= P0:
            continue
        idx = int(np.searchsorted(q_lower, q, side="right")) - 1
        if idx < 0 or idx >= len(ell_arr):
            continue
        if q > q_upper[idx]:
            continue
        el = ell_arr[idx]
        if el == 0.0:
            continue
        L_q = el / (2.0 * q ** 1.5)
        result[i] = L_q * (q - F_fwd)
    return result


# ———————————————————————————————————————————————————————————————————————————————————————————— #
