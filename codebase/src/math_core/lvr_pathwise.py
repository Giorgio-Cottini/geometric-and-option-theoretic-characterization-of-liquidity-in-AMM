"""
Realized LVR under the observed profile, and its LVR-neutral counterfactual (cycle 3, R5).

Sibling module.  Reads src.math_core.profile_measure (checkpoint 1) and the frozen
src.math_core.impermanent_loss read-only; edits neither.

Conventions implemented here, quoted from
docs/superpowers/specs/2026-08-10-cev-elasticity-and-lvr-neutrality-design.md.

C1, C2.  Reused verbatim from src.math_core.profile_measure.block_profile: the profile
     is L = ell / (2 q**1.5) (C1), read from the C2 extended measure (bins run to the next
     surviving tick, not one spacing).  This module adds nothing to either; it only reads
     the BlockProfile bin-level arrays, which cover the whole retained support.

C10. RTW26 eq. 16 discretizes on the 8-hour grid to
     LVR_t = (1/2) sum_s L_s(P_s) (P_{s+1} - P_s)**2.  The 8-hour sampling understates true
     quadratic variation by an unknown factor, but the observed and counterfactual paths are
     built from the identical d<P> series, so the factor cancels in their ratio.  Anchor:
     spec section 10, estimand 1, and the C10 decision (headline quantities are the ratio and
     the coefficient of variation, not the absolute level).

C11. The counterfactual constant C_tilde (which absorbs C / nu**2 of RTW26 Example 3.3) is
     fixed once, at the panel's first snapshot, so that the counterfactual profile's
     mark-to-market value at spot equals the observed profile's, using RTW26 eq. 6,
     V_L(p) = x(p) p + y(p).  Decision (human, 2026-08-10, spec section 10): beta = 1 is the
     only variant computed this cycle (R2 and R3 are descoped, GATE 1 closure decision B), and
     the match is applied once, not re-matched every snapshot, modelling a real static
     counterfactual position held alongside the observed one.

     At beta = 1, L*(q) = C_tilde / q**2.  The untruncated capital-match integral for y*(p) is
     log-divergent as q -> 0 (see counterfactual_constant's docstring), so the match is solved
     on the observed profile's own finite retained support [a, b] at entry.  After C_tilde is
     fixed, every later snapshot's realized-LVR increment evaluates L*(q) = C_tilde / q**2
     pointwise and unbounded — see this module's Task 1 step 1 confidence block for why.

Units and orientation.  Every price here is HUMAN price q, the output of
graph:liquidity_clean_parquet_price_from_tick under the pool's own invert flag, matching
profile_measure.py's own convention.  No function in this module takes an invert argument
directly: orientation is fully absorbed by block_profile before anything here is called.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .impermanent_loss import _reserve_integrals
from .profile_measure import BlockProfile, block_profile


def ell_at_spot(bp: BlockProfile) -> float:
    """
    C2.  The intrinsic liquidity ell on the bin containing q_spot, piecewise-constant lookup.

    bp.q_lower, bp.q_upper, bp.ell are bin-level arrays covering the WHOLE retained support
    (see BlockProfile's docstring), not the x_max-truncated grid, so this is correct
    regardless of the x_max the caller built bp with.

    Orientation.  profile_measure.extended_bins returns bin_ell = e[:-1], so every C2 bin
    carries the ell of its LOWER TICK — the same convention block_profile applies to its own
    grid with searchsorted(ticks_sorted, grid, side="right") - 1.  That convention lives in
    TICK space and does not depend on invert; its image in PRICE space does.  Under invert
    human price decreases with tick, so the bin's ell sits at its q_upper edge; without
    invert it sits at q_lower.  When q_spot falls exactly on a bin edge — which happens
    whenever curr_tick is itself a surviving tick, and is common — the two cases resolve to
    opposite searchsorted sides, so no single fixed side is correct for both orientations.
    An earlier version used side="left" unconditionally and returned the neighbouring bin's
    ell on every non-inverted pool.  Orientation is read back off bp rather than taken as an
    argument, so it cannot disagree with the profile being read: bp.grid_tick is sorted
    ascending in x, hence in q, so its own direction is the orientation.

    Known fragility, not fixed here.  Resolving the edge case at all depends on q_spot being
    bit-identical to the edge, and q_spot comes from a SCALAR _price_from_tick call while the
    edges come from an ARRAY one.  Bitwise agreement between the two is not guaranteed by the
    language, only observed.  This function makes the intended side explicit; it does not make
    the comparison robust to a last-ulp disagreement.

    Args:
        bp: one block's profile, from profile_measure.block_profile.
    Returns:
        ell on the bin containing bp.q_spot.
    Raises:
        ValueError: q_spot lies outside [bp.q_lower.min(), bp.q_upper.max()], or bp carries
        fewer than two grid points so its orientation cannot be read — fast and loud, per the
        project's error-handling convention, rather than silently clamping or guessing.
    """
    if not (bp.q_lower[0] <= bp.q_spot <= bp.q_upper[-1]):
        raise ValueError(
            f"q_spot={bp.q_spot} outside retained support "
            f"[{bp.q_lower[0]}, {bp.q_upper[-1]}]"
        )
    if bp.grid_tick.size < 2:
        raise ValueError(
            f"cannot read orientation off a {bp.grid_tick.size}-point grid; "
            "bp must span at least two grid ticks"
        )
    side = "right" if bp.grid_tick[-1] > bp.grid_tick[0] else "left"
    idx = int(np.searchsorted(bp.q_upper, bp.q_spot, side=side))
    idx = min(idx, bp.ell.size - 1)
    return float(bp.ell[idx])


def _l_from_ell(ell: float, q: float) -> float:
    """
    C1.  L(q) = ell(q) / (2 q**1.5).

    The single definition of the C1 conversion in this module.  It takes (ell, q) rather than
    a BlockProfile so that realized_lvr_series can reuse the ell it already holds instead of
    paying for a second bin lookup per block, which is why the expression was duplicated here
    in the first place.
    """
    return ell / (2.0 * q**1.5)


def l_at_spot(bp: BlockProfile) -> float:
    """C1.  L(q_spot) = ell(q_spot) / (2 q_spot**1.5)."""
    return _l_from_ell(ell_at_spot(bp), bp.q_spot)


def counterfactual_constant(a: float, b: float, p0: float, v_obs_p0: float) -> float:
    """
    C11.  Solve C_tilde so that the beta=1 counterfactual L*(q) = C_tilde / q**2, truncated to
    [a, b], has V_{L*}(p0) = v_obs_p0 (RTW26 eq. 6, V_L(p) = x(p) p + y(p)).

    Closed form, derived directly (not a root solve):
        x*(p0) = integral_{p0}^{b} C_tilde / q**2 dq = C_tilde (1/p0 - 1/b)
        y*(p0) = integral_{a}^{p0} q (C_tilde / q**2) dq = C_tilde ln(p0 / a)
        V_{L*}(p0) = p0 x*(p0) + y*(p0) = C_tilde [ (1 - p0/b) + ln(p0/a) ]
    so C_tilde = v_obs_p0 / [ (1 - p0/b) + ln(p0/a) ].

    The bracket is guaranteed positive when a < p0 < b (1 - p0/b > 0 since p0 < b; ln(p0/a) > 0
    since p0 > a), which is why the caller must supply a, b spanning p0's own retained support.

    Args:
        a, b     : truncation bounds, human price, the observed profile's own retained support
                   at the snapshot the match is solved on (bp.q_lower[0], bp.q_upper[-1]).
        p0       : spot price at that snapshot, human price.
        v_obs_p0 : the observed profile's V_L(p0), computed by the caller from
                   _reserve_integrals on that same snapshot's bins.
    Returns:
        C_tilde, the counterfactual's constant (absorbs C / nu**2 of RTW26 Example 3.3).
    Raises:
        ValueError: a < p0 < b does not hold, or v_obs_p0 <= 0 — fast and loud.
    """
    if not (a < p0 < b):
        raise ValueError(f"need a < p0 < b, got a={a}, p0={p0}, b={b}")
    if v_obs_p0 <= 0.0:
        raise ValueError(f"v_obs_p0 must be positive, got {v_obs_p0}")
    bracket = (1.0 - p0 / b) + math.log(p0 / a)
    return v_obs_p0 / bracket


def realized_lvr_series(
    df: pd.DataFrame,
    tick_spacing: int,
    token0_decimals: int,
    token1_decimals: int,
    invert: bool,
) -> pd.DataFrame:
    """
    C1, C2, C10.  Per-block spot price and L(spot), and the discretized LVR increment between
    consecutive blocks.

    LVR_t = (1/2) sum_s L_s(P_s) (P_{s+1} - P_s)**2 (RTW26 eq. 16, C10).  L_s is read from that
    block's OWN profile at its OWN spot (C1, C2) — not held fixed — because the realized side is
    the actual, evolving position, unlike the counterfactual (C11).

    Args:
        df              : one pool's full processed parquet, columns
                          [block_number, tick_idx, liquidity, curr_tick].
        tick_spacing    : fee-tier tick spacing, 1, 10, or 60.
        token0_decimals, token1_decimals, invert : the price map, C3.
    Returns:
        DataFrame, one row per block, columns:
            block_number, q_spot, ell_spot, l_spot,
            lvr_increment  (NaN on the last block, which has no forward increment)
        Sorted ascending in block_number.
    """
    rows = []
    for block, grp in df.groupby("block_number", sort=True):
        bp = block_profile(grp, tick_spacing, token0_decimals, token1_decimals, invert,
                           x_max=0.5)
        e = ell_at_spot(bp)
        rows.append({
            "block_number": int(block),
            "q_spot": bp.q_spot,
            "ell_spot": e,
            "l_spot": _l_from_ell(e, bp.q_spot),   # C1, single definition
        })
    out = pd.DataFrame(rows).sort_values("block_number").reset_index(drop=True)
    dp = out["q_spot"].diff().shift(-1)   # P_{s+1} - P_s, aligned to row s
    out["lvr_increment"] = 0.5 * out["l_spot"] * dp**2
    return out


def counterfactual_lvr_series(q_spot: np.ndarray, c_tilde: float) -> np.ndarray:
    """
    C10, C11.  The counterfactual's LVR increments, beta = 1, L*(q) = C_tilde / q**2,
    evaluated pointwise at every observed q_spot (see this module's docstring for why the
    counterfactual is NOT re-truncated to [a, b] here).

    Args:
        q_spot  : 1-D array of per-block spot prices, same order as realized_lvr_series.
        c_tilde : from counterfactual_constant, fixed once at the panel's first snapshot.
    Returns:
        1-D array, same length as q_spot, last entry NaN (no forward increment).
    Raises:
        ValueError: any q_spot is non-finite or non-positive.  C_tilde / q**2 turns a zero or
        non-finite spot into an infinity with no trace, and lvr_ratio_and_cv's mask used to let
        that infinity through into the sum, so the two defects composed into a silently wrong
        total.  Guarding here is the fast-and-loud half of that fix.
    """
    q = np.asarray(q_spot, dtype=np.float64)
    bad = ~np.isfinite(q) | (q <= 0.0)
    if np.any(bad):
        where = np.flatnonzero(bad)
        raise ValueError(
            f"q_spot must be finite and strictly positive; "
            f"{where.size} bad entry/entries at index {where[:10].tolist()}"
            f"{' ...' if where.size > 10 else ''}, first value {q[where[0]]!r}"
        )
    l_star = c_tilde / q**2
    dp = np.diff(q, append=np.nan)
    return 0.5 * l_star * dp**2


def lvr_ratio_and_cv(obs_increments: np.ndarray, neutral_increments: np.ndarray,
                     label: str | None = None) -> dict:
    """
    C10.  The ratio LVR_obs / LVR_neutral and the coefficient of variation of each side's
    increments, both computed over the identical index range (spec section 10, estimand 3,
    "matched windows" — the same grid for both series, not a sub-windowed split; see
    src/math_core/lvr_pathwise.py's module docstring and spec section 10).

    The last row of each series is NaN by construction (the forward-difference convention, see
    realized_lvr_series) and is dropped before summing or computing CoV.  A non-finite value
    ANYWHERE ELSE is an error, not something to filter: the mask here used to be ~np.isnan,
    and np.isnan(inf) is False, so an infinity manufactured upstream by C_tilde / q**2 passed
    straight through into the sum and turned lvr_neutral_total into inf, ratio into 0.0 and
    cv_neutral into nan with nothing on the record.  Silently dropping a bad block is the same
    failure mode one step quieter, so this raises instead, per the project's convention.

    Args:
        obs_increments, neutral_increments : 1-D arrays, same length, same block order.
        label : optional pool identifier, e.g. "30bp_WETH_USDC".  Carried into the error and
                the degenerate-denominator warning, which otherwise report a bare nan with no
                way to tell which of the eleven pools produced it.
    Returns:
        dict with keys: lvr_obs_total, lvr_neutral_total, ratio, cv_obs, cv_neutral.
    Raises:
        ValueError: shapes disagree, or a non-finite increment appears anywhere but the last row.
    """
    who = f"[{label}] " if label else ""
    obs = np.asarray(obs_increments, dtype=np.float64)
    neu = np.asarray(neutral_increments, dtype=np.float64)
    if obs.shape != neu.shape:
        raise ValueError(f"{who}length mismatch: obs {obs.shape} vs neutral {neu.shape}")

    finite = np.isfinite(obs) & np.isfinite(neu)
    is_tail = np.zeros(obs.shape, dtype=bool)
    if obs.size:
        is_tail[-1] = True                      # the documented NaN tail, the only allowed one
    bad = ~finite & ~is_tail
    if np.any(bad):
        where = np.flatnonzero(bad)
        raise ValueError(
            f"{who}non-finite increment outside the last row at index "
            f"{where[:10].tolist()}{' ...' if where.size > 10 else ''}: "
            f"obs={obs[where[0]]!r}, neutral={neu[where[0]]!r}"
        )

    obs, neu = obs[finite], neu[finite]
    obs_total = float(np.sum(obs))
    neu_total = float(np.sum(neu))
    if neu_total == 0.0:
        print(f"WARN {who}lvr_neutral_total is 0, ratio reported as nan", flush=True)
    return {
        "lvr_obs_total": obs_total,
        "lvr_neutral_total": neu_total,
        "ratio": obs_total / neu_total if neu_total != 0.0 else float("nan"),
        "cv_obs": float(np.std(obs) / np.mean(obs)) if np.mean(obs) != 0.0 else float("nan"),
        "cv_neutral": float(np.std(neu) / np.mean(neu)) if np.mean(neu) != 0.0 else float("nan"),
    }
