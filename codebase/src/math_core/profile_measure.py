"""
Shared estimator core for cycle 3, the CEV elasticity of the liquidity profile.

Sibling module.  It reads the frozen replication and never edits it, copying the
cycle-2 arrangement in which src/math_core/price_impact.py wrapped the frozen
builders read only.

Conventions implemented here, quoted from
docs/superpowers/specs/2026-08-10-cev-elasticity-and-lvr-neutrality-design.md.

C1.  "The profile is L, never ell."  The parquet `liquidity` column is ell, the
     intrinsic liquidity.  RTW26 defines L(q) = ell(q) / (2 q**1.5).
     Anchor: graph:math_core_impermanent_loss_compute_lvr_function computes the
     total token measure as sum ell_i (1/sqrt(a_i) - 1/sqrt(b_i)), which is
     integral ell / (2 q**1.5) dq.  The conversion is therefore already implicit
     in the frozen reserve integrals and is not taken on the paper's authority
     alone.  Fitting an exponent to ell and reading it as -2 beta biases beta by
     exactly 0.75, with no error and a plausible-looking number.

C2.  "The ell measure extends to the next surviving tick."
     Anchor: graph:liquidity_clean_parquet_reconstruct_block drops ticks with
     liquidity_gross == 0 and then sets price_upper from tick_idx + spacing, so
     where surviving ticks are sparse its intervals do not cover the price axis.
     Uniswap semantics are that ell is constant from one surviving tick to the
     next.  The piecewise-constant lookup used below is the one already used by
     graph:math_core_liquidity_vs_price_build_lvsp_surface, namely
     searchsorted(ticks, grid, side="right") - 1.

C3.  "Orientation."  invert is a required argument, with no default, on every
     function that turns a tick into a price.
     Anchor: graph:graphics_labels_lm_xlabel, where the same argument was made
     required in cycle 2 precisely so that no new call site could inherit the
     wrong frame.
     Why it stops at the price boundary: ell is invariant under quote
     inversion.  ell = sqrt(x y), and under Q = 1/P the reserve roles swap, so
     ell_tilde / sqrt(Q) = y = ell / sqrt(Q) gives ell_tilde = ell.  Inversion
     therefore enters only through the tick-to-price map.  Once q is human
     price, the slope of log L on log q carries no further sign, which is why
     beta_from_slope takes no invert argument.  The end-to-end recovery is
     asserted separately for each orientation in tests/test_profile_measure.py.

C4.  The decimal normalization of graph:liquidity_clean_parquet_decimal_adj is a
     constant.  It moves the intercept C / nu**2 and cannot move the slope.
     Asserted by test, not by argument.

C5.  "Two branches, always."  This module returns x = log(q / spot) so that the
     caller can split at x = 0.  It never averages the two sides.

Units and orientation.  Every price in this module is HUMAN price q, that is the
output of graph:liquidity_clean_parquet_price_from_tick under the pool's own
invert flag, in units of token1 per token0 for a non-inverted pool and token0 per
token1 for an inverted one.  x is log(q / spot), which is log(K / S) in BOTH
orientations.  That is NOT the cycle-2 array
(curr_tick - tick_idx) * log(1.0001), which is log(K / S) only when inverted, so
graph:graphics_labels_lm_xlabel must not be used to label x.  See X_LABEL.
"""

from __future__ import annotations

import math
from typing import NamedTuple

import numpy as np
import pandas as pd

from ..data_processing.liquidity.clean_parquet import _price_from_tick

LOG_TICK: float = math.log(1.0001)

# See the module docstring and deviation D2 of the R1 plan.  x is log(K/S) in
# both orientations, so the label does not depend on invert.
X_LABEL: str = "log(K / S)"


class BlockProfile(NamedTuple):
    """
    One block's liquidity profile in human price, on a uniform tick grid.

    Grid-level arrays (length n_grid), sorted ascending in x:
        x          log(q / spot), dimensionless
        log_L      natural log of L(q) = ell / (2 q**1.5)
        grid_tick  the absolute tick of that grid point
        bin_id     index into the bin-level arrays, so that a caller can count
                   DISTINCT surviving ticks inside a band (C8) rather than grid
                   points, which oversample wide bins

    Bin-level arrays (length n_bin), sorted ascending in q, spanning the WHOLE
    retained support and not only the grid window:
        q_lower, q_upper   human-price edges of each C2 bin
        ell                intrinsic liquidity, constant on that bin

    q_spot   human price at curr_tick
    """
    x: np.ndarray
    log_L: np.ndarray
    grid_tick: np.ndarray
    bin_id: np.ndarray
    q_lower: np.ndarray
    q_upper: np.ndarray
    ell: np.ndarray
    q_spot: float


def extended_bins(
    tick_idx: np.ndarray,
    ell: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    C2.  Bin i runs from surviving tick i to surviving tick i + 1.

    The highest surviving tick opens no bin: above it every position has closed
    and the reconstruction gives ell = 0, so nothing is lost by dropping it
    (deviation D3 of the R1 plan).  Fewer than two ticks raises rather than
    guessing a width.

    Args:
        tick_idx : 1-D int array of surviving tick indices, any order.
        ell      : 1-D float array of intrinsic liquidity, aligned to tick_idx.
    Returns:
        lo_tick, hi_tick : 1-D int64 arrays, tick bounds of each bin.
        bin_ell          : 1-D float64 array, ell constant on that bin.
    """
    t = np.asarray(tick_idx, dtype=np.int64)
    e = np.asarray(ell, dtype=np.float64)
    if t.size != e.size:
        raise ValueError(f"tick_idx and ell disagree: {t.size} vs {e.size}")
    if t.size < 2:
        raise ValueError(f"need at least 2 surviving ticks to form a bin, got {t.size}")
    order = np.argsort(t)
    t = t[order]
    e = e[order]
    return t[:-1], t[1:], e[:-1]


def bin_prices(
    lo_tick: np.ndarray,
    hi_tick: np.ndarray,
    token0_decimals: int,
    token1_decimals: int,
    invert: bool,
) -> tuple[np.ndarray, np.ndarray]:
    """
    C3.  Human-price edges of each bin, returned ascending in q.

    Under inversion human price DECREASES with tick, so the tick-lower edge is
    the price-upper edge.  Sorting here is what lets every downstream integral
    assume q_lower < q_upper.

    Returns:
        q_lower, q_upper : 1-D float64 arrays, human price, q_lower < q_upper.
    """
    p_lo = np.asarray(_price_from_tick(lo_tick, token0_decimals, token1_decimals, invert),
                      dtype=np.float64)
    p_hi = np.asarray(_price_from_tick(hi_tick, token0_decimals, token1_decimals, invert),
                      dtype=np.float64)
    return np.minimum(p_lo, p_hi), np.maximum(p_lo, p_hi)


def mass_between(
    q_lower: np.ndarray,
    q_upper: np.ndarray,
    ell: np.ndarray,
    q_lo: float,
    q_hi: float,
) -> float:
    """
    C8.  Liquidity mass, in token0 units, over [q_lo, q_hi], clipping partial bins.

    integral_a^b L dq = integral_a^b ell / (2 q**1.5) dq = ell (1/sqrt(a) - 1/sqrt(b)),
    which is the same expression that
    graph:math_core_impermanent_loss_compute_lvr_function uses for x_total, so
    coverage is measured in the frozen replication's own token measure.

    Args:
        q_lower, q_upper : bin edges, human price, ascending, q_lower < q_upper.
        ell              : intrinsic liquidity per bin.
        q_lo, q_hi       : integration limits, human price, both strictly positive.
    Returns:
        The integral, a non-negative float.
    """
    if not (q_lo > 0.0 and q_hi > q_lo):
        raise ValueError(f"bad integration limits: q_lo={q_lo}, q_hi={q_hi}")
    a = np.clip(q_lower, q_lo, q_hi)
    b = np.clip(q_upper, q_lo, q_hi)
    return float(np.sum(ell * (1.0 / np.sqrt(a) - 1.0 / np.sqrt(b))))


def block_profile(
    block_df: pd.DataFrame,
    tick_spacing: int,
    token0_decimals: int,
    token1_decimals: int,
    invert: bool,
    x_max: float,
) -> BlockProfile:
    """
    Build one block's profile: C2 bins, a uniform tick grid, then C1.

    The grid is uniform in tick, hence uniform in log q, so ordinary least
    squares on the grid weights every unit of log-price equally and needs no
    weight vector.  Grid points are looked up piecewise-constant against the
    surviving ticks, which is C2 rather than the one-spacing measure of
    graph:liquidity_clean_parquet_reconstruct_block.

    The grid is truncated to |x| <= x_max because no band in the C6 sweep
    reaches further; the BINS are not truncated, so branch mass fractions are
    computed against the whole retained support.

    Args:
        block_df        : rows of one block, columns
                          [tick_idx, liquidity, curr_tick]; `liquidity` is ell.
        tick_spacing    : fee-tier tick spacing, 1, 10, or 60.
        token0_decimals : token0 decimals, for the price map.
        token1_decimals : token1 decimals, for the price map.
        invert          : pool orientation, required, C3.
        x_max           : grid half-width in log-moneyness, dimensionless.
    Returns:
        BlockProfile.  Human price throughout; x is log(K / S) in both
        orientations.
    """
    t = block_df["tick_idx"].to_numpy(dtype=np.int64)
    e = block_df["liquidity"].to_numpy(dtype=np.float64)
    curr_tick = int(block_df["curr_tick"].iloc[0])

    lo_tick, hi_tick, bin_ell = extended_bins(t, e)
    q_lower, q_upper = bin_prices(lo_tick, hi_tick, token0_decimals,
                                  token1_decimals, invert)
    # bin_prices sorts each PAIR, not the sequence; sort the bins themselves so
    # that the arrays are ascending in q as BlockProfile documents.
    bin_order = np.argsort(q_lower)
    q_lower, q_upper, bin_ell = q_lower[bin_order], q_upper[bin_order], bin_ell[bin_order]

    q_spot = float(_price_from_tick(curr_tick, token0_decimals, token1_decimals, invert))

    ticks_sorted = np.sort(t)
    half = int(math.ceil(x_max / LOG_TICK))
    lo_bound = max(int(ticks_sorted[0]), curr_tick - half)
    hi_bound = min(int(ticks_sorted[-1]), curr_tick + half)
    if hi_bound <= lo_bound:
        raise ValueError(
            f"empty grid window: ticks span [{ticks_sorted[0]}, {ticks_sorted[-1]}], "
            f"curr_tick={curr_tick}, x_max={x_max}"
        )
    anchor = int(ticks_sorted[0])
    start = anchor + int(math.ceil((lo_bound - anchor) / tick_spacing)) * tick_spacing
    grid = np.arange(start, hi_bound + 1, tick_spacing, dtype=np.int64)

    # C2 lookup, copied from graph:math_core_liquidity_vs_price_build_lvsp_surface.
    idx = np.searchsorted(ticks_sorted, grid, side="right") - 1
    keep = (idx >= 0) & (idx < ticks_sorted.size - 1)   # last tick opens no bin, D3
    grid, idx = grid[keep], idx[keep]

    # idx indexes the tick-sorted bins; remap to the q-sorted bin arrays.
    remap = np.empty_like(bin_order)
    remap[bin_order] = np.arange(bin_order.size)
    bin_id = remap[idx]

    ell_grid = bin_ell[bin_id]
    positive = ell_grid > 0.0
    grid, bin_id, ell_grid = grid[positive], bin_id[positive], ell_grid[positive]

    q = np.asarray(_price_from_tick(grid, token0_decimals, token1_decimals, invert),
                   dtype=np.float64)
    x = np.log(q / q_spot)
    log_L = np.log(ell_grid) - math.log(2.0) - 1.5 * np.log(q)   # C1

    srt = np.argsort(x)
    return BlockProfile(
        x=x[srt], log_L=log_L[srt], grid_tick=grid[srt], bin_id=bin_id[srt],
        q_lower=q_lower, q_upper=q_upper, ell=bin_ell, q_spot=q_spot,
    )


def beta_from_slope(slope: float) -> float:
    """
    RTW26 Example 3.3.  L(q) = C / (nu**2 q**(2 beta)), so
    log L = const - 2 beta log q and beta = -slope / 2.

    Takes no invert argument by design: see C3 in the module docstring and
    deviation D1 of the R1 plan.  Orientation is fully absorbed by the time q is
    human price, and a dead argument here would weaken rather than strengthen
    the check.
    """
    return -0.5 * float(slope)
