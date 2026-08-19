"""
Black-Scholes implied volatility for Uniswap V3 liquidity profiles (RTW26 eq. 20).

Defines sigma_BS(L, T) as the unique sigma satisfying:

    integral L(q) * P_BS(q, T, sigma) dq  +  integral L(q) * C_BS(q, T, sigma) dq
                [0, P0]                            [P0, inf]

  = integral L(q) * P_mkt(q) dq  +  integral L(q) * C_mkt(q) dq
                [0, P0]                    [P0, inf]

where L(q) = ell(q) / (2*q^{3/2}) and the RHS is the market-side IL price (Pi^IL).

The module provides:
  - Aggregate IV:       compute_BS_implied_vol        (single sigma for whole profile)
  - Fine-structure IV:  compute_BS_iv_fine_structure   (one sigma per tick interval)

Root-finding uses Newton-Raphson (user spec); safe because the LHS is strictly
increasing in sigma (Proposition 3.6) and BS vega > 0 everywhere.

Black-Scholes scope
-------------------
All functions assume r = 0 (Deribit convention, RTW26 section 5.2.5).
Forward price F is used for all model pricing.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm

from .liquidity_profile import piecewise_constant_liquidity_profile
from .impermanent_loss import _antiderivative, _integrate_leg

# ———————————————————————————————————————————————————————————————————————————————————————————— #
# Black-Scholes primitives (r = 0)


def _bs_d1(K: np.ndarray, F: float, T: float, sigma: float) -> np.ndarray:
    """Compute d1 = [log(F/K) + 0.5*sigma^2*T] / (sigma*sqrt(T))."""
    s_sqrt_t = sigma * np.sqrt(T)
    return (np.log(F / K) + 0.5 * sigma**2 * T) / s_sqrt_t


def _bs_price(
    K: np.ndarray, F: float, T: float, sigma: float, opt_type: str
) -> np.ndarray:
    """
    Vectorized Black-Scholes option pricer (r = 0).

    Args:
        K        : strike array (must be > 0).
        F        : forward price.
        T        : time to maturity in years (must be > 0).
        sigma    : annualized volatility (must be > 0).
        opt_type : "C" for call, "P" for put.
    Returns:
        Array of BS prices, same shape as K.
    """
    d1 = _bs_d1(K, F, T, sigma)
    d2 = d1 - sigma * np.sqrt(T)
    if opt_type == "C":
        return F * norm.cdf(d1) - K * norm.cdf(d2)
    else:
        return K * norm.cdf(-d2) - F * norm.cdf(-d1)


def _bs_vega(K: np.ndarray, F: float, T: float, sigma: float) -> np.ndarray:
    """
    Vectorized Black-Scholes vega (identical for calls and puts, r = 0).

    vega = F * phi(d1) * sqrt(T)

    where phi is the standard normal PDF.
    """
    d1 = _bs_d1(K, F, T, sigma)
    return F * norm.pdf(d1) * np.sqrt(T)


# ———————————————————————————————————————————————————————————————————————————————————————————— #
# Integration of L(q) * O_BS(q) over one leg using piecewise-linear approximation


def _integrate_bs_leg(
    tick_lower: np.ndarray,
    tick_upper: np.ndarray,
    tick_ell: np.ndarray,
    F: float,
    T: float,
    sigma: float,
    q_lo: float,
    q_hi: float,
    opt_type: str,
) -> float:
    """
    Integrate L(q) * O_BS(q, T, sigma) over [q_lo, q_hi].

    Uses the same merged-grid + closed-form antiderivative approach as
    impermanent_loss._integrate_leg, but with BS model prices instead of
    market proxy prices.

    On each sub-interval [a, b] of the tick grid where ell is constant:
      1. Evaluate O_BS at endpoints a and b.
      2. Derive affine coefficients: O(q) ~ a0 + a1*q.
      3. Contribution = _antiderivative(b, ...) - _antiderivative(a, ...).

    This piecewise-linear approximation of O_BS is accurate because
    sub-intervals are single ticks (~0.1% wide in price space).

    Args:
        tick_lower, tick_upper, tick_ell : from piecewise_constant_liquidity_profile.
        F, T, sigma : BS model parameters.
        q_lo, q_hi  : integration domain endpoints.
        opt_type    : "C" or "P".
    Returns:
        Scalar integral value.
    """
    # Build grid from tick boundaries only (BS prices are smooth — no strike
    # breakpoints needed unlike market proxy)
    tick_bounds = np.concatenate([tick_lower, tick_upper])
    ticks_in = tick_bounds[(tick_bounds >= q_lo) & (tick_bounds <= q_hi)]
    grid = np.unique(np.concatenate([[q_lo, q_hi], ticks_in]))

    total = 0.0
    for i in range(len(grid) - 1):
        a, b = grid[i], grid[i + 1]
        if b <= a:
            continue

        mid = 0.5 * (a + b)
        tick_idx = int(np.searchsorted(tick_lower, mid, side="right")) - 1
        if tick_idx < 0 or tick_idx >= len(tick_ell):
            continue
        if mid > tick_upper[tick_idx]:
            continue

        ell = tick_ell[tick_idx]
        if ell == 0:
            continue

        # Evaluate BS price at endpoints → affine approximation
        K_ab = np.array([a, b])
        O_ab = _bs_price(K_ab, F, T, sigma, opt_type)
        O_a, O_b = float(O_ab[0]), float(O_ab[1])

        a1_coef = (O_b - O_a) / (b - a)
        a0_coef = O_a - a1_coef * a

        contrib = _antiderivative(b, ell, a0_coef, a1_coef) - _antiderivative(
            a, ell, a0_coef, a1_coef
        )
        total += contrib

    return total


def _integrate_bs_vega_leg(
    tick_lower: np.ndarray,
    tick_upper: np.ndarray,
    tick_ell: np.ndarray,
    F: float,
    T: float,
    sigma: float,
    q_lo: float,
    q_hi: float,
) -> float:
    """
    Integrate L(q) * vega_BS(q, T, sigma) over [q_lo, q_hi].

    Same structure as _integrate_bs_leg but with BS vega instead of price.
    Used as the derivative of the BS IL price w.r.t. sigma for Newton-Raphson.
    """
    tick_bounds = np.concatenate([tick_lower, tick_upper])
    ticks_in = tick_bounds[(tick_bounds >= q_lo) & (tick_bounds <= q_hi)]
    grid = np.unique(np.concatenate([[q_lo, q_hi], ticks_in]))

    total = 0.0
    for i in range(len(grid) - 1):
        a, b = grid[i], grid[i + 1]
        if b <= a:
            continue

        mid = 0.5 * (a + b)
        tick_idx = int(np.searchsorted(tick_lower, mid, side="right")) - 1
        if tick_idx < 0 or tick_idx >= len(tick_ell):
            continue
        if mid > tick_upper[tick_idx]:
            continue

        ell = tick_ell[tick_idx]
        if ell == 0:
            continue

        K_ab = np.array([a, b])
        V_ab = _bs_vega(K_ab, F, T, sigma)
        V_a, V_b = float(V_ab[0]), float(V_ab[1])

        a1_coef = (V_b - V_a) / (b - a)
        a0_coef = V_a - a1_coef * a

        contrib = _antiderivative(b, ell, a0_coef, a1_coef) - _antiderivative(
            a, ell, a0_coef, a1_coef
        )
        total += contrib

    return total


# ———————————————————————————————————————————————————————————————————————————————————————————— #
# Full BS IL price and its sigma-derivative


def _bs_il_price(
    tick_lower: np.ndarray,
    tick_upper: np.ndarray,
    tick_ell: np.ndarray,
    F: float,
    T: float,
    sigma: float,
    P0: float,
    K_put_lo: float,
    K_call_hi: float,
) -> float:
    """
    Compute the BS-model IL price for a given sigma (LHS of eq. 20).

    Split at P0: put leg [K_put_lo, P0] + call leg [P0, K_call_hi].
    """
    put = _integrate_bs_leg(
        tick_lower, tick_upper, tick_ell, F, T, sigma, K_put_lo, P0, "P"
    )
    call = _integrate_bs_leg(
        tick_lower, tick_upper, tick_ell, F, T, sigma, P0, K_call_hi, "C"
    )
    return put + call


def _bs_il_vega(
    tick_lower: np.ndarray,
    tick_upper: np.ndarray,
    tick_ell: np.ndarray,
    F: float,
    T: float,
    sigma: float,
    P0: float,
    K_put_lo: float,
    K_call_hi: float,
) -> float:
    """
    Compute d/d_sigma of the BS-model IL price.

    This is the integral of L(q) * vega_BS(q) over both legs.
    """
    put_v = _integrate_bs_vega_leg(
        tick_lower, tick_upper, tick_ell, F, T, sigma, K_put_lo, P0
    )
    call_v = _integrate_bs_vega_leg(
        tick_lower, tick_upper, tick_ell, F, T, sigma, P0, K_call_hi
    )
    return put_v + call_v


# ———————————————————————————————————————————————————————————————————————————————————————————— #
# Newton-Raphson IV solver


def _newton_iv(
    target: float,
    tick_lower: np.ndarray,
    tick_upper: np.ndarray,
    tick_ell: np.ndarray,
    F: float,
    T: float,
    P0: float,
    K_put_lo: float,
    K_call_hi: float,
    sigma0: float = 0.7,
    tol: float = 1e-8,
    max_iter: int = 50,
) -> tuple[float, bool]:
    """
    Newton-Raphson solver for BS implied volatility on a single bin.

    Solves: _bs_il_price(..., sigma) - target = 0.

    Args:
        target     : market-side IL price for this bin (RHS of eq. 20).
        tick_lower, tick_upper, tick_ell : tick data for this bin.
        F, T, P0   : forward, time-to-maturity, spot price.
        K_put_lo   : lower bound of put integration domain.
        K_call_hi  : upper bound of call integration domain.
        sigma0     : initial guess for sigma.
        tol        : convergence tolerance on |f(sigma)|.
        max_iter   : maximum Newton iterations.
    Returns:
        (sigma, converged): solved IV and convergence flag.
    """
    sigma = sigma0
    SIGMA_MIN, SIGMA_MAX = 0.01, 10.0

    for _ in range(max_iter):
        f_val = (
            _bs_il_price(
                tick_lower, tick_upper, tick_ell, F, T, sigma, P0, K_put_lo, K_call_hi
            )
            - target
        )
        if abs(f_val) < tol:
            return sigma, True

        f_prime = _bs_il_vega(
            tick_lower, tick_upper, tick_ell, F, T, sigma, P0, K_put_lo, K_call_hi
        )
        if abs(f_prime) < 1e-16:
            # Vega too small — fall back to bisection
            return _bisection_iv(
                target, tick_lower, tick_upper, tick_ell,
                F, T, P0, K_put_lo, K_call_hi, tol, max_iter,
            )

        sigma_new = sigma - f_val / f_prime
        sigma_new = np.clip(sigma_new, SIGMA_MIN, SIGMA_MAX)
        sigma = float(sigma_new)

    # Newton did not converge — fall back to bisection
    return _bisection_iv(
        target, tick_lower, tick_upper, tick_ell,
        F, T, P0, K_put_lo, K_call_hi, tol, max_iter,
    )


def _bisection_iv(
    target: float,
    tick_lower: np.ndarray,
    tick_upper: np.ndarray,
    tick_ell: np.ndarray,
    F: float,
    T: float,
    P0: float,
    K_put_lo: float,
    K_call_hi: float,
    tol: float = 1e-8,
    max_iter: int = 60,
) -> tuple[float, bool]:
    """
    Bisection fallback solver for BS implied volatility on a single bin.

    Safe because LHS(sigma) is strictly monotone increasing in sigma (Prop. 3.6),
    so f(sigma) = LHS(sigma) - target is guaranteed to change sign over
    [SIGMA_MIN, SIGMA_MAX] = [0.01, 10.0].

    Args:
        target     : market-side IL price for this bin.
        tick_lower, tick_upper, tick_ell : tick data for this bin.
        F, T, P0   : forward, time-to-maturity, spot price.
        K_put_lo   : lower bound of put integration domain.
        K_call_hi  : upper bound of call integration domain.
        tol        : convergence tolerance on |f(sigma)|.
        max_iter   : maximum bisection iterations (60 suffices for tol=1e-8).
    Returns:
        (sigma, converged): solved IV and convergence flag.
    """
    SIGMA_MIN, SIGMA_MAX = 0.01, 10.0

    def _f(s: float) -> float:
        return (
            _bs_il_price(
                tick_lower, tick_upper, tick_ell, F, T, s, P0, K_put_lo, K_call_hi
            )
            - target
        )

    f_lo = _f(SIGMA_MIN)
    f_hi = _f(SIGMA_MAX)

    if f_lo > 0.0:
        # target below the minimum achievable LHS
        return SIGMA_MIN, False
    if f_hi < 0.0:
        # target above the maximum achievable LHS
        return SIGMA_MAX, False

    sigma_lo, sigma_hi = SIGMA_MIN, SIGMA_MAX
    for _ in range(max_iter):
        sigma_mid = 0.5 * (sigma_lo + sigma_hi)
        f_mid = _f(sigma_mid)
        if abs(f_mid) < tol:
            return sigma_mid, True
        if f_lo * f_mid <= 0.0:
            sigma_hi = sigma_mid
        else:
            sigma_lo = sigma_mid
            f_lo = f_mid

    return 0.5 * (sigma_lo + sigma_hi), False


# ———————————————————————————————————————————————————————————————————————————————————————————— #
# Public API


def compute_BS_implied_vol(
    liq_df: pd.DataFrame,
    interp: dict[str, tuple[np.ndarray, np.ndarray]],
    F: float,
    T: float,
    P0: float,
) -> dict:
    """
    Compute the aggregate Black-Scholes implied volatility (RTW26 eq. 20).

    This is the single sigma_BS for the entire liquidity profile (n = 1 resolution).
    Solves: BS_IL_price(sigma) = market_IL_price.

    Args:
        liq_df : output of reconstruct_liquidity_cumsum.
        interp : {"C": (strikes, prices), "P": (strikes, prices)} from linear_interpolation.
        F      : Deribit forward price.
        T      : time to maturity in years.
        P0     : pool spot price (put/call split point).
    Returns:
        dict with keys:
            "sigma_BS"  : float — annualized BS implied volatility.
            "converged" : bool  — whether Newton-Raphson converged.
    """
    q_lower, q_upper, ell = piecewise_constant_liquidity_profile(liq_df)
    K_p, P_p = interp["P"]
    K_c, P_c = interp["C"]

    # Market-side IL price (RHS of eq. 20) — same computation as BS_compute_IL_price
    put_total, _, _, _ = _integrate_leg(
        K_p, P_p, q_lower, q_upper, ell, float(K_p.min()), float(P0)
    )
    call_total, _, _, _ = _integrate_leg(
        K_c, P_c, q_lower, q_upper, ell, float(P0), float(K_c.max())
    )
    target = put_total + call_total

    sigma, converged = _newton_iv(
        target=target,
        tick_lower=q_lower,
        tick_upper=q_upper,
        tick_ell=ell,
        F=F,
        T=T,
        P0=P0,
        K_put_lo=float(K_p.min()),
        K_call_hi=float(K_c.max()),
    )
    return {"sigma_BS": sigma, "converged": converged}


def compute_BS_iv_fine_structure(
    liq_df: pd.DataFrame,
    interp: dict[str, tuple[np.ndarray, np.ndarray]],
    F: float,
    T: float,
    P0: float,
) -> dict:
    """
    Compute the per-tick-interval fine structure of BS implied volatility
    (RTW26 section 3.3.3).

    For each tick interval [q_lower_i, q_upper_i] with ell_i > 0, solves for sigma_i:

        integral_{bin_i} L(q) * O_BS(q, T, sigma_i) dq
          = integral_{bin_i} L(q) * O_mkt(q) dq

    where the integration domain for each bin is restricted to the put or call side
    (or split at P0 if the bin straddles it).

    Args:
        liq_df : output of reconstruct_liquidity_cumsum.
        interp : {"C": (strikes, prices), "P": (strikes, prices)} from linear_interpolation.
        F      : Deribit forward price.
        T      : time to maturity in years.
        P0     : pool spot price (put/call split point).
    Returns:
        dict with keys:
            "log_moneyness" : np.ndarray — log(midpoint / F) per tick.
            "sigma_BS"      : np.ndarray — implied vol per tick (NaN if not converged).
            "converged"     : np.ndarray — bool mask.
            "tick_lower"    : np.ndarray — tick interval lower bounds.
            "tick_upper"    : np.ndarray — tick interval upper bounds.
    """
    q_lower, q_upper, ell = piecewise_constant_liquidity_profile(liq_df)
    K_p, P_p = interp["P"]
    K_c, P_c = interp["C"]

    # Only process ticks with positive liquidity
    active = ell > 0
    n_active = int(active.sum())

    log_m = np.full(n_active, np.nan)
    sigma_arr = np.full(n_active, np.nan)
    conv_arr = np.zeros(n_active, dtype=bool)
    tl_arr = np.empty(n_active)
    tu_arr = np.empty(n_active)

    idx = 0
    for i in range(len(q_lower)):
        if not active[i]:
            continue

        lo_i, hi_i = float(q_lower[i]), float(q_upper[i])
        ell_i = ell[i]
        tl_arr[idx] = lo_i
        tu_arr[idx] = hi_i
        mid = np.sqrt(lo_i * hi_i)  # geometric midpoint
        log_m[idx] = np.log(mid / F)

        # Single-tick arrays for this bin
        bin_lower = np.array([lo_i])
        bin_upper = np.array([hi_i])
        bin_ell = np.array([ell_i])

        # Market-side target for this bin
        target = 0.0

        # Put side contribution: bin intersected with [min_K_p, P0]
        put_lo = max(lo_i, float(K_p.min()))
        put_hi = min(hi_i, P0)
        if put_hi > put_lo:
            put_val, _, _, _ = _integrate_leg(
                K_p, P_p, bin_lower, bin_upper, bin_ell, put_lo, put_hi
            )
            target += put_val

        # Call side contribution: bin intersected with [P0, max_K_c]
        call_lo = max(lo_i, P0)
        call_hi = min(hi_i, float(K_c.max()))
        if call_hi > call_lo:
            call_val, _, _, _ = _integrate_leg(
                K_c, P_c, bin_lower, bin_upper, bin_ell, call_lo, call_hi
            )
            target += call_val

        if target <= 0.0:
            # No market-side IL contribution for this bin — skip
            idx += 1
            continue

        # Determine integration bounds for the BS side
        K_put_lo = max(lo_i, float(K_p.min()))
        K_call_hi = min(hi_i, float(K_c.max()))

        sigma, converged = _newton_iv(
            target=target,
            tick_lower=bin_lower,
            tick_upper=bin_upper,
            tick_ell=bin_ell,
            F=F,
            T=T,
            P0=P0,
            K_put_lo=K_put_lo,
            K_call_hi=K_call_hi,
        )
        sigma_arr[idx] = sigma
        conv_arr[idx] = converged
        idx += 1

    return {
        "log_moneyness": log_m,
        "sigma_BS": sigma_arr,
        "converged": conv_arr,
        "tick_lower": tl_arr,
        "tick_upper": tu_arr,
    }


# ———————————————————————————————————————————————————————————————————————————————————————————— #
