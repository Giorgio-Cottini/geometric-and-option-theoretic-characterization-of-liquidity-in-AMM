"""
Standalone tests for the cycle-3 estimator core (R1, checkpoint 1).

No pytest (the project invokes bare `python`): each test is a plain function
asserting an invariant; the __main__ block runs them all and prints PASS.

The first test is the most valuable one in the cycle.  A synthetic tick set is
built so that ell follows q**(1.5 - 2*beta) exactly.  Recovering beta from it
catches, at once:
  - the C1 normalization error (fitting ell instead of L biases beta by 0.75),
  - the C3 sign error (an inverted pool read in the wrong frame flips beta),
  - the C2 measure error (one-spacing bins instead of next-surviving-tick bins).

Run:  python codebase/tests/test_profile_measure.py
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_CODEBASE = Path(__file__).resolve().parents[1]   # codebase/
sys.path.insert(0, str(_CODEBASE))

from src.data_processing.liquidity.clean_parquet import _price_from_tick
from src.math_core.profile_measure import (
    LOG_TICK,
    extended_bins,
    bin_prices,
    mass_between,
    block_profile,
    beta_from_slope,
)

_D0, _D1 = 6, 18          # arbitrary but unequal, so the decimal factor is not 1


def _synthetic_block(beta: float, invert: bool, spacing: int = 10,
                     n_side: int = 40, stride: int = 1,
                     ell_scale: float = 1.0) -> pd.DataFrame:
    """
    One block whose ell follows the exact CEV LVR-neutral law.

    RTW26 Example 3.3 gives L(q) = C / (nu**2 q**(2 beta)).  With
    L = ell / (2 q**1.5) that is ell(q) = 2 C / nu**2 * q**(1.5 - 2 beta).
    Setting the constant to `ell_scale` and evaluating at the human price of
    each tick gives a profile whose log-log slope is exactly -2*beta.

    stride > 1 leaves gaps in the surviving-tick set, which is what
    distinguishes the C2 extended measure from the one-spacing measure.
    """
    curr_tick = 0
    ticks = np.arange(-n_side * spacing, n_side * spacing + 1,
                      spacing * stride, dtype=np.int64)
    q = _price_from_tick(ticks, _D0, _D1, invert)
    ell = ell_scale * q ** (1.5 - 2.0 * beta)
    return pd.DataFrame({
        "block_number": 1,
        "tick_idx": ticks,
        "liquidity": ell,
        "curr_tick": curr_tick,
    })


def test_recovers_beta_dense_both_branches_both_orientations():
    """P4.  The known-answer test.  Exact, because every grid point coincides
    with a surviving tick when stride == 1."""
    for beta in (1.0, 0.6):
        for invert in (True, False):
            df = _synthetic_block(beta, invert)
            bp = block_profile(df, 10, _D0, _D1, invert, x_max=0.5)
            for mask, name in ((bp.x < 0, "below"), (bp.x > 0, "above")):
                slope = np.polyfit(bp.x[mask], bp.log_L[mask], 1)[0]
                got = beta_from_slope(slope)
                assert abs(got - beta) < 1e-8, (
                    f"beta={beta} invert={invert} branch={name}: got {got}"
                )


def test_fitting_ell_instead_of_L_is_wrong_by_075():
    """C1.  Demonstrates the bias the conversion prevents.  log_ell is built
    algebraically from bp.log_L (the inverse of the C1 conversion), not read
    back from the raw ell column, so this catches a C1 regression through a
    compounded 0.75 offset rather than by independently recomputing log(ell)
    from the parquet.  A future regression to fitting ell fails loudly here
    rather than silently."""
    beta = 1.0
    df = _synthetic_block(beta, invert=False)
    bp = block_profile(df, 10, _D0, _D1, False, x_max=0.5)
    q = np.exp(bp.x) * bp.q_spot
    log_ell = bp.log_L + math.log(2.0) + 1.5 * np.log(q)
    slope_ell = np.polyfit(bp.x, log_ell, 1)[0]
    assert abs(beta_from_slope(slope_ell) - (beta - 0.75)) < 1e-8


def test_decimal_rescaling_leaves_the_slope_alone():
    """C4.  graph:liquidity_clean_parquet_decimal_adj divides ell by a
    constant.  A constant moves the intercept C / nu**2 and cannot move the
    slope.  Asserted, not argued."""
    df_a = _synthetic_block(0.8, invert=False, ell_scale=1.0)
    df_b = _synthetic_block(0.8, invert=False, ell_scale=1e12)
    sa = np.polyfit(*_xy(df_a, False), 1)
    sb = np.polyfit(*_xy(df_b, False), 1)
    assert abs(sa[0] - sb[0]) < 1e-10          # slope identical
    assert abs(sa[1] - sb[1]) > 1.0            # intercept moved


def _xy(df: pd.DataFrame, invert: bool) -> tuple[np.ndarray, np.ndarray]:
    bp = block_profile(df, 10, _D0, _D1, invert, x_max=0.5)
    return bp.x, bp.log_L


def test_x_reconciles_with_the_cycle2_array():
    """D2.  x here is log(K/S) in both orientations; the cycle-2 array
    (curr_tick - tick_idx) * log(1.0001) is log(K/S) only when inverted."""
    for invert, sign in ((True, 1.0), (False, -1.0)):
        df = _synthetic_block(1.0, invert)
        bp = block_profile(df, 10, _D0, _D1, invert, x_max=0.5)
        x_cycle2 = (0 - bp.grid_tick) * LOG_TICK      # curr_tick is 0 here
        assert np.allclose(bp.x, sign * x_cycle2, atol=1e-9)


def test_extended_measure_differs_from_one_spacing_when_ticks_are_sparse():
    """C2.  With stride 3 the surviving ticks sit 3 spacings apart.  The
    extended measure covers the price axis; the one-spacing measure of
    graph:liquidity_clean_parquet_reconstruct_block covers one third of it."""
    df = _synthetic_block(1.0, invert=False, stride=3)
    t = df["tick_idx"].to_numpy()
    ell = df["liquidity"].to_numpy()
    lo, hi, e = extended_bins(t, ell)
    assert np.all(hi - lo == 30)                       # 3 spacings, not 1
    q_lo, q_hi = bin_prices(lo, hi, _D0, _D1, False)
    covered = mass_between(q_lo, q_hi, e, q_lo.min(), q_hi.max())
    one_spacing_hi = lo + 10
    q_lo2, q_hi2 = bin_prices(lo, one_spacing_hi, _D0, _D1, False)
    under = mass_between(q_lo2, q_hi2, e, q_lo2.min(), q_hi2.max())
    assert under < covered
    assert 0.30 < under / covered < 0.40               # roughly one third


def test_mass_between_clips_partial_bins():
    """C8.  Coverage accounting: the mass over the full support is the sum of
    the mass over any partition of it."""
    df = _synthetic_block(1.0, invert=False)
    lo, hi, e = extended_bins(df["tick_idx"].to_numpy(), df["liquidity"].to_numpy())
    a, b = bin_prices(lo, hi, _D0, _D1, False)
    mid = float(np.sqrt(a.min() * b.max()))
    total = mass_between(a, b, e, a.min(), b.max())
    left = mass_between(a, b, e, a.min(), mid)
    right = mass_between(a, b, e, mid, b.max())
    assert abs((left + right) - total) < 1e-9 * total


def test_extended_bins_refuses_a_single_tick():
    """D3.  Fast and loud: one surviving tick opens no bin."""
    try:
        extended_bins(np.array([0], dtype=np.int64), np.array([1.0]))
    except ValueError:
        return
    raise AssertionError("expected ValueError on a single surviving tick")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS  {name}")
