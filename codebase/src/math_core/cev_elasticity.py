"""
Band fits, coverage, and the headline half-width for cycle 3 R1.

This module knows about bands and regressions and never touches a tick index
directly; profile_measure.py owns the tick-to-price measure.  The split is what
lets R5 reuse profile_measure.py unchanged.

Conventions, quoted from
docs/superpowers/specs/2026-08-10-cev-elasticity-and-lvr-neutrality-design.md.

C5.  "Two branches, always."  The profile is peaked near spot, so a single fit
     across the peak measures the position of the peak.  Every fit runs
     separately below and above spot and the two are reported separately.  A
     below-above average is never the headline.

C6.  "Fixed log-moneyness bands, swept."  The band family is |log(q / spot)| <= w
     for a fixed half-width w, identical across pools and across snapshots.  The
     argument for fixed over quantile bands is in tmp/cycle3-doubt2.md: a
     quantile band removes the concentration difference that the cross-tier
     comparison of R2 exists to measure, and its moving outer edge confounds a
     change of shape with a change of measurement range.

C7.  "The headline half-width is an output, not an input."  It is the smallest w
     in the grid such that every pool entering the cross-tier comparison has at
     least 10 distinct surviving ticks on each branch in at least 95 percent of
     snapshots.  The floor of 10 is a stated convention, not a derived one.

C8.  "Coverage travels with every slope."  Every reported slope carries the
     fraction of branch liquidity mass inside its band and the count of distinct
     surviving ticks.  A slope without coverage is not interpretable.

Units.  w and x are dimensionless log-price.  mass_frac is a ratio of token0
measures and is dimensionless.  beta_shape is the CEV elasticity of RTW26
Example 3.3.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .profile_measure import BlockProfile, beta_from_slope, block_profile, mass_between

W_GRID: tuple[float, ...] = (0.02, 0.05, 0.10, 0.15, 0.22, 0.35, 0.50)
BRANCHES: tuple[str, str] = ("below", "above")

# A straight line through two points is not evidence, so a branch with fewer
# than three DISTINCT surviving ticks returns a NaN slope.  Its coverage is
# still recorded, because C7 is decided from coverage and would be undecidable
# if the narrow bands were dropped.
MIN_FIT_TICKS: int = 3

HEADLINE_MIN_TICKS: int = 10      # C7, a stated convention
HEADLINE_PCT: float = 5.0         # p5 >= floor is "at least 95 percent of snapshots"


def _band_limits(bp: BlockProfile, w: float, branch: str) -> tuple[float, float]:
    """Human-price limits of one branch of the band |x| <= w."""
    if branch == "below":
        return bp.q_spot * float(np.exp(-w)), bp.q_spot
    if branch == "above":
        return bp.q_spot, bp.q_spot * float(np.exp(w))
    raise ValueError(f"branch must be 'below' or 'above', got {branch!r}")


def branch_fit(bp: BlockProfile, w: float, branch: str) -> dict:
    """
    C5, C6, C8.  Ordinary least squares of log L on log q over one branch.

    x = log q - log spot, so the slope on x equals the slope on log q and the
    band restriction is a restriction on x alone.

    Args:
        bp     : one block's profile, human price, from block_profile.
        w      : band half-width in log-moneyness, dimensionless.
        branch : "below" or "above" spot, in HUMAN price.
    Returns:
        dict with slope, beta_shape, r2, n_ticks, n_grid, mass_frac.  slope,
        beta_shape and r2 are NaN when n_ticks < MIN_FIT_TICKS; the coverage
        fields are always populated.
    """
    if branch == "below":
        m = (bp.x < 0.0) & (bp.x >= -w)
    elif branch == "above":
        m = (bp.x > 0.0) & (bp.x <= w)
    else:
        raise ValueError(f"branch must be 'below' or 'above', got {branch!r}")

    xs, ys = bp.x[m], bp.log_L[m]
    n_ticks = int(np.unique(bp.bin_id[m]).size)

    q_lo, q_hi = _band_limits(bp, w, branch)
    full_lo, full_hi = (float(bp.q_lower.min()), bp.q_spot) if branch == "below" \
        else (bp.q_spot, float(bp.q_upper.max()))
    full = mass_between(bp.q_lower, bp.q_upper, bp.ell, full_lo, full_hi)
    inside = mass_between(bp.q_lower, bp.q_upper, bp.ell, q_lo, q_hi)
    mass_frac = float(inside / full) if full > 0.0 else float("nan")

    out = {"slope": float("nan"), "beta_shape": float("nan"), "r2": float("nan"),
           "n_ticks": n_ticks, "n_grid": int(xs.size), "mass_frac": mass_frac}
    if n_ticks < MIN_FIT_TICKS or xs.size < 2:
        return out

    slope, intercept = np.polyfit(xs, ys, 1)
    resid = ys - (slope * xs + intercept)
    ss_tot = float(np.sum((ys - ys.mean()) ** 2))
    out["slope"] = float(slope)
    out["beta_shape"] = beta_from_slope(slope)
    out["r2"] = float(1.0 - np.sum(resid ** 2) / ss_tot) if ss_tot > 0.0 else float("nan")
    return out


def full_support_fit(bp: BlockProfile) -> dict:
    """
    The unrestricted single fit across the whole grid window, reported only to
    document that it is not usable (spec section 7, fourth output).  It crosses
    the peak, so its slope measures where the peak sits inside the window.
    """
    if bp.x.size < 2:
        return {"slope": float("nan"), "beta_shape": float("nan"), "r2": float("nan")}
    slope, intercept = np.polyfit(bp.x, bp.log_L, 1)
    resid = bp.log_L - (slope * bp.x + intercept)
    ss_tot = float(np.sum((bp.log_L - bp.log_L.mean()) ** 2))
    return {"slope": float(slope), "beta_shape": beta_from_slope(slope),
            "r2": float(1.0 - np.sum(resid ** 2) / ss_tot) if ss_tot > 0.0 else float("nan")}


def sweep_pool(
    df: pd.DataFrame,
    tick_spacing: int,
    token0_decimals: int,
    token1_decimals: int,
    invert: bool,
    w_grid: tuple[float, ...] = W_GRID,
) -> pd.DataFrame:
    """
    C6.  Fit every (block, w, branch) of one pool.

    Args:
        df           : the pool's processed parquet, columns
                       [block_number, tick_idx, liquidity, curr_tick].
        tick_spacing : 1, 10, or 60.
        invert       : pool orientation, required, C3.
    Returns:
        Long DataFrame, one row per (block_number, w, branch), with the columns
        named in the R1 plan's Task 2 interface block.  Blocks with fewer than
        two surviving ticks are skipped and counted in the returned frame's
        `attrs["skipped_blocks"]`.
    """
    x_max = max(w_grid)
    rows: list[dict] = []
    skipped = 0
    for block, grp in df.groupby("block_number", sort=True):
        try:
            bp = block_profile(grp, tick_spacing, token0_decimals,
                               token1_decimals, invert, x_max)
        except ValueError:
            skipped += 1
            continue
        for w in w_grid:
            for branch in BRANCHES:
                rows.append({"block_number": int(block), "w": float(w),
                             "branch": branch, **branch_fit(bp, w, branch)})
    out = pd.DataFrame(rows)
    out.attrs["skipped_blocks"] = skipped
    return out


def coverage_table(sweep: pd.DataFrame) -> pd.DataFrame:
    """
    C7, C8.  Collapse a sweep across snapshots into the gate material.

    Args:
        sweep : output of sweep_pool, with a `pool` column already attached by
                the runner.
    Returns:
        One row per (pool, w, branch): median and 5th-percentile distinct
        surviving-tick counts, median in-band mass fraction, and the median and
        interquartile range of beta_shape.
    """
    g = sweep.groupby(["pool", "w", "branch"], sort=True)
    out = pd.DataFrame({
        "n_ticks_median": g["n_ticks"].median(),
        "n_ticks_p5": g["n_ticks"].quantile(HEADLINE_PCT / 100.0),
        "mass_frac_median": g["mass_frac"].median(),
        "beta_median": g["beta_shape"].median(),
        "beta_iqr": g["beta_shape"].quantile(0.75) - g["beta_shape"].quantile(0.25),
    }).reset_index()
    return out


def headline_w(
    coverage: pd.DataFrame,
    min_ticks: int = HEADLINE_MIN_TICKS,
    pct: float = HEADLINE_PCT,
) -> tuple[float | None, pd.DataFrame]:
    """
    C7.  The smallest w at which every pool clears the floor on both branches.

    Smallest, because a wider band buys variance reduction by averaging over
    more of a curve that is not straight, which is bias.

    Args:
        coverage : output of coverage_table.
        min_ticks: the C7 floor, a stated convention.
        pct      : unused in the arithmetic, carried so that the caller records
                   which percentile the n_ticks_p5 column was built from.
    Returns:
        (w, qualifying) where w is the headline half-width or None if no w in
        the grid qualifies for every pool, and `qualifying` lists, per w, the
        pools that clear the floor on BOTH branches.  When w is None the caller
        reports the restricted pool set instead, per C7.
    """
    if float(pct) != HEADLINE_PCT:
        raise ValueError(
            f"coverage_table built n_ticks_p5 at p{HEADLINE_PCT}; got pct={pct}"
        )
    ok = (coverage.groupby(["pool", "w"])["n_ticks_p5"].min() >= min_ticks)
    qual = ok[ok].reset_index()[["pool", "w"]]
    n_pools = coverage["pool"].nunique()
    counts = qual.groupby("w").size()
    full = sorted(w for w, c in counts.items() if c == n_pools)
    return (float(full[0]) if full else None, qual)


def local_slope_profile(
    df: pd.DataFrame,
    tick_spacing: int,
    token0_decimals: int,
    token1_decimals: int,
    invert: bool,
    x_centres: np.ndarray,
    half_window: float = 0.02,
) -> pd.DataFrame:
    """
    The time-averaged local slope d log L / d log q against log-moneyness.

    A rolling regression, not a finite difference: the profile is a staircase
    between surviving ticks, so a difference of neighbouring grid points is
    zero inside a bin and a spike at its edge.  A window of +/- half_window is
    fitted at each centre, per block, and the blocks are then summarised.

    Args:
        x_centres   : 1-D float array of window centres in log-moneyness.
        half_window : window half-width, dimensionless log price.
    Returns:
        One row per centre: x_centre, slope_median, slope_q25, slope_q75,
        n_blocks_fitted.
    """
    x_max = float(np.max(np.abs(x_centres))) + half_window
    per_centre: list[list[float]] = [[] for _ in range(len(x_centres))]
    for _block, grp in df.groupby("block_number", sort=True):
        try:
            bp = block_profile(grp, tick_spacing, token0_decimals,
                               token1_decimals, invert, x_max)
        except ValueError:
            continue
        for k, c in enumerate(x_centres):
            m = np.abs(bp.x - c) <= half_window
            if int(np.unique(bp.bin_id[m]).size) < MIN_FIT_TICKS:
                continue
            per_centre[k].append(float(np.polyfit(bp.x[m], bp.log_L[m], 1)[0]))
    rows = []
    for c, vals in zip(x_centres, per_centre):
        a = np.asarray(vals, dtype=np.float64)
        rows.append({
            "x_centre": float(c),
            "slope_median": float(np.median(a)) if a.size else float("nan"),
            "slope_q25": float(np.quantile(a, 0.25)) if a.size else float("nan"),
            "slope_q75": float(np.quantile(a, 0.75)) if a.size else float("nan"),
            "n_blocks_fitted": int(a.size),
        })
    return pd.DataFrame(rows)
