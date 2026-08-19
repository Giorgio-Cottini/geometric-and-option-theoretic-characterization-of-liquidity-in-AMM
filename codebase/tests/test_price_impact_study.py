"""
Standalone test for the price-impact runner's job assembly.

Run:  python codebase/tests/test_price_impact_study.py
"""
import sys
from pathlib import Path

_CODEBASE = Path(__file__).resolve().parents[1]   # codebase/
sys.path.insert(0, str(_CODEBASE))

from data_extraction import config as ext_config
from price_impact_study import _build_jobs


def test_build_jobs_shape_and_decimals():
    jobs = _build_jobs()
    # One job per configured pool — several fee tiers per pair, no ETH_USDC.
    assert len(jobs) == len(ext_config.POOLS)
    for pair, fee_label, spacing, path, d0, d1, invert in jobs:
        assert isinstance(d0, int) and isinstance(d1, int) and isinstance(invert, bool)
        assert path.suffix == ".parquet"
        # Several tiers share a pair folder; the stem is what separates them.
        assert path.parent.name == pair
        assert path.stem == f"{fee_label}_ticks"

    by_key = {(p, f): (d0, d1, inv) for p, f, _s, _pt, d0, d1, inv in jobs}
    # Inverted pool: token0=USDC(6), token1=WETH(18), price quoted USDC per WETH.
    assert by_key[("WETH_USDC", "5bp")] == (6, 18, True)
    # Native-ordered pool: token0=WBTC(8), token1=WETH(18) — never covered before
    # the multi-pool expansion, and the case the axis labels were wrong for.
    assert by_key[("WBTC_WETH", "5bp")] == (8, 18, False)
    # The corrected USDC/USDT venue is the 1bp pool, not the vestigial 5bp one.
    assert ("USDC_USDT", "1bp") in by_key
    assert ("USDC_USDT", "5bp") not in by_key


def test_every_pair_carries_one_convention():
    """All fee tiers of a pair are the same two tokens, so decimals and
    orientation must agree across them — a mismatch means a config typo."""
    by_pair: dict[str, set] = {}
    for pair, _fee, _spacing, _path, d0, d1, invert in _build_jobs():
        by_pair.setdefault(pair, set()).add((d0, d1, invert))
    for pair, conventions in by_pair.items():
        assert len(conventions) == 1, f"{pair} has conflicting conventions: {conventions}"


if __name__ == "__main__":
    test_build_jobs_shape_and_decimals()
    print("PASS test_build_jobs_shape_and_decimals")
    test_every_pair_carries_one_convention()
    print("PASS test_every_pair_carries_one_convention")
    print("ALL PASS")
