"""
Standalone tests for the cycle-3 band sweep (R1, checkpoint 2).

Run:  python codebase/tests/test_cev_elasticity.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_CODEBASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_CODEBASE))

from src.data_processing.liquidity.clean_parquet import _price_from_tick
from src.math_core.profile_measure import block_profile
from src.math_core.cev_elasticity import (
    W_GRID,
    HEADLINE_MIN_TICKS,
    branch_fit,
    sweep_pool,
    coverage_table,
    headline_w,
)

_D0, _D1 = 6, 18


def _power_law_pool(beta: float, invert: bool, n_blocks: int = 4,
                    spacing: int = 10, n_side: int = 600) -> pd.DataFrame:
    """A whole pool of blocks whose ell follows q**(1.5 - 2 beta) exactly.
    n_side 600 at spacing 10 spans +/- 6000 ticks, which is +/- 0.6 in
    log-moneyness, so every w in W_GRID including 0.50 is populated."""
    frames = []
    for b, curr in enumerate(range(0, n_blocks * spacing, spacing), start=1):
        ticks = np.arange(-n_side * spacing, n_side * spacing + 1, spacing,
                          dtype=np.int64)
        q = _price_from_tick(ticks, _D0, _D1, invert)
        frames.append(pd.DataFrame({
            "block_number": b,
            "tick_idx": ticks,
            "liquidity": q ** (1.5 - 2.0 * beta),
            "curr_tick": curr,
        }))
    return pd.concat(frames, ignore_index=True)


def test_sweep_is_flat_in_w_for_a_true_power_law():
    """The whole point of R1.  A power law has no characteristic scale, so
    beta_shape must be identical at every w, on both branches."""
    df = _power_law_pool(0.85, invert=False)
    out = sweep_pool(df, 10, _D0, _D1, False)
    fitted = out.dropna(subset=["beta_shape"])
    assert len(fitted) > 0
    assert fitted["beta_shape"].std() < 1e-8
    assert abs(fitted["beta_shape"].mean() - 0.85) < 1e-8


def test_sweep_is_flat_in_w_when_inverted():
    df = _power_law_pool(0.85, invert=True)
    out = sweep_pool(df, 10, _D0, _D1, True).dropna(subset=["beta_shape"])
    assert abs(out["beta_shape"].mean() - 0.85) < 1e-8


def test_coverage_is_recorded_even_when_the_slope_is_nan():
    """C7 cannot be evaluated from a table that drops the narrow bands, so
    n_ticks and mass_frac are populated on every row, fitted or not."""
    df = _power_law_pool(1.0, invert=False, spacing=60, n_side=100)
    out = sweep_pool(df, 60, _D0, _D1, False)
    narrow = out[out["w"] == 0.02]
    assert len(narrow) > 0
    assert narrow["n_ticks"].notna().all()
    assert narrow["mass_frac"].notna().all()


def test_mass_fraction_rises_with_w_and_stays_in_the_unit_interval():
    df = _power_law_pool(1.0, invert=False)
    out = sweep_pool(df, 10, _D0, _D1, False)
    assert out["mass_frac"].between(0.0, 1.0 + 1e-9).all()
    med = out.groupby("w")["mass_frac"].median()
    assert med.is_monotonic_increasing


def test_headline_rule_picks_the_smallest_qualifying_w():
    """C7.  Smallest w whose 5th-percentile tick count clears the floor, for
    every pool and both branches."""
    cov = pd.DataFrame([
        {"pool": p, "w": w, "branch": br,
         "n_ticks_p5": 4 if w < 0.10 else 40,
         "n_ticks_median": 50, "mass_frac_median": 0.5,
         "beta_median": 1.0, "beta_iqr": 0.0}
        for p in ("A", "B") for w in W_GRID for br in ("below", "above")
    ])
    w, qual = headline_w(cov)
    assert w == 0.10
    assert set(qual.loc[qual["w"] == 0.10, "pool"]) == {"A", "B"}


def test_headline_rule_returns_none_when_nothing_qualifies():
    cov = pd.DataFrame([
        {"pool": "A", "w": w, "branch": br, "n_ticks_p5": HEADLINE_MIN_TICKS - 1,
         "n_ticks_median": 5, "mass_frac_median": 0.1,
         "beta_median": 1.0, "beta_iqr": 0.0}
        for w in W_GRID for br in ("below", "above")
    ])
    w, qual = headline_w(cov)
    assert w is None
    assert qual.empty


def test_branch_fit_refuses_to_average_the_two_sides():
    """C5.  A profile that is steep below spot and flat above must return two
    different slopes, not one."""
    ticks = np.arange(-3000, 3001, 10, dtype=np.int64)
    q = _price_from_tick(ticks, _D0, _D1, False)
    ell = np.where(q < _price_from_tick(0, _D0, _D1, False),
                   q ** (1.5 - 2 * 1.5), q ** (1.5 - 2 * 0.5))
    df = pd.DataFrame({"block_number": 1, "tick_idx": ticks,
                       "liquidity": ell, "curr_tick": 0})
    bp = block_profile(df, 10, _D0, _D1, False, x_max=0.5)
    lo = branch_fit(bp, 0.20, "below")
    hi = branch_fit(bp, 0.20, "above")
    assert abs(lo["beta_shape"] - 1.5) < 1e-8
    assert abs(hi["beta_shape"] - 0.5) < 1e-8


def test_runner_assembles_one_job_per_pool_with_its_own_convention():
    """Spec section 13, last row: eleven pools, correct decimals, correct
    invert per pool.  Mirrors tests_test_price_impact_study."""
    import importlib
    study = importlib.import_module("cev_elasticity_study")
    jobs = study._build_jobs()
    assert len(jobs) == 11
    for pair, fee_label, spacing, path, d0, d1, invert in jobs:
        assert fee_label.endswith("bp")
        assert spacing in (1, 10, 60)
        assert isinstance(invert, bool)
        assert path.name.endswith("_ticks.parquet")
        assert pair in path.parts
    # WETH_USDC is the inverted pair; every other pair is not.
    for pair, _f, _s, _p, _d0, _d1, invert in jobs:
        assert invert == (pair == "WETH_USDC")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS  {name}")
