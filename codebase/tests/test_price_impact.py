"""
Standalone tests for the price-impact surfaces (cycle 2).

No pytest dependency (the project invokes bare `python`): each test is a plain
function asserting an invariant; the __main__ block runs them all and prints PASS.

Run:  python codebase/tests/test_price_impact.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_CODEBASE = Path(__file__).resolve().parents[1]   # codebase/
sys.path.insert(0, str(_CODEBASE))

from src.math_core.price_impact import impact_from_PL, build_impact_surface
from src.math_core.liquidity_vs_price import build_lvsp_surface


def _synthetic_df() -> pd.DataFrame:
    """Two blocks, ticks on a spacing-10 grid, strictly positive liquidity."""
    rows = []
    for block, curr in ((100, 0), (200, 10)):
        for tick, liq in ((-20, 1e6), (-10, 2e6), (0, 4e6), (10, 3e6), (20, 1e6)):
            rows.append((block, tick, liq, curr))
    return pd.DataFrame(
        rows, columns=["block_number", "tick_idx", "liquidity", "curr_tick"]
    )


def test_impact_from_PL_values():
    P = np.array([1.0, 4.0]); L = np.array([2.0, 8.0])
    assert np.allclose(impact_from_PL(P, L, "absolute"), 2 * P ** 1.5 / L)
    assert np.allclose(impact_from_PL(P, L, "relative"), 2 * P ** 0.5 / L)


def test_reciprocal_ratio_equals_P():
    P = np.array([1.0, 2.5, 9.0]); L = np.array([3.0, 7.0, 11.0])
    ratio = impact_from_PL(P, L, "absolute") / impact_from_PL(P, L, "relative")
    assert np.allclose(ratio, P)


def test_surface_mask_matches_liquidity():
    # Window wider than the data (-40..40) → cells below the lowest tick (-20)
    # are NaN in BOTH the liquidity surface and the impact surface, identically.
    df = _synthetic_df(); tw = (-40, 40)
    _g, _t, log_liq, _c, _b = build_lvsp_surface(df, tw[0], tw[1], 10, 50)
    _x, _t2, log10_imp, _c2, _b2 = build_impact_surface(
        df, 10, "absolute-ticks", "absolute", 0, 0, False,
        tick_window=tw, n_time_samples=50,
    )
    assert np.array_equal(np.isnan(log10_imp), np.isnan(log_liq))


def test_absolute_over_relative_recovers_P():
    df = _synthetic_df(); tw = (-40, 40)
    x, _t, la, _c, _b = build_impact_surface(
        df, 10, "absolute-ticks", "absolute", 0, 0, False,
        tick_window=tw, n_time_samples=50,
    )
    _x, _t2, lr, _c2, _b2 = build_impact_surface(
        df, 10, "absolute-ticks", "relative", 0, 0, False,
        tick_window=tw, n_time_samples=50,
    )
    # d0=d1=0, invert=False → P = 1.0001**tick ; ratio 10**la / 10**lr == P per cell.
    P = 1.0001 ** x.astype(float)
    ratio = 10 ** la / 10 ** lr
    finite = np.isfinite(ratio)
    expected = np.broadcast_to(P[None, :], ratio.shape)
    assert np.allclose(ratio[finite], expected[finite])


def test_plotters_write_pngs():
    import matplotlib
    matplotlib.use("Agg")
    from src.graphics.price_impact import (
        plot_impact_profile, plot_impact_surface, plot_impact_heatmap,
    )
    df = _synthetic_df()
    out = _CODEBASE / "tests" / "_impact_smoke"
    p1 = out / "profile.png"; p2 = out / "surface.png"; p3 = out / "heatmap.png"
    # The label must be BASE_QUOTE: the plotters resolve units through
    # impact_units(), which raises on a label it cannot split.
    plot_impact_profile(df, "SYN_QUO", "5bp", 10, p1, "absolute", 0, 0, False,
                        axis="log-moneyness", n_time_samples=50)
    plot_impact_surface(df, "SYN_QUO", "5bp", 10, p2, "relative", 0, 0, False,
                        axis="absolute-ticks", n_time_samples=50)
    plot_impact_heatmap(df, "SYN_QUO", "5bp", 10, p3, "absolute", 0, 0, False,
                        n_time_samples=50)
    for p in (p1, p2, p3):
        assert p.exists() and p.stat().st_size > 0


def test_impact_units_splits_pair_label():
    from src.math_core.price_impact import impact_units
    assert impact_units("WETH_USDC") == ("USDC", "WETH")
    assert impact_units("WBTC_WETH") == ("WETH", "WBTC")
    assert impact_units("USDC_USDT") == ("USDT", "USDC")


def test_base_token_is_the_impact_denominator():
    """The base token (first half of the pair label) must be token1 for an
    inverted pool and token0 for a native one — that is the invariant which
    makes 2*P**1.5/L denominate the trade in the base token."""
    from src.math_core.price_impact import impact_units
    from price_impact_study import _build_jobs  # _CODEBASE already on sys.path

    decimals = {"WETH": 18, "USDC": 6, "USDT": 6, "WBTC": 8}
    for pair, _fee, _spacing, _path, d0, d1, invert in _build_jobs():
        quote, base = impact_units(pair)
        assert decimals[base] == (d1 if invert else d0), pair
        assert decimals[quote] == (d0 if invert else d1), pair


def test_inverted_pool_price_convention():
    """First invert=True numeric coverage. absolute/relative must recover the
    INVERTED price Q = 10**(d1-d0) / 1.0001**tick (token0 per token1)."""
    df = _synthetic_df(); tw = (-40, 40)
    d0, d1 = 6, 18
    x, _t, la, _c, _b = build_impact_surface(
        df, 10, "absolute-ticks", "absolute", d0, d1, True,
        tick_window=tw, n_time_samples=50,
    )
    _x, _t2, lr, _c2, _b2 = build_impact_surface(
        df, 10, "absolute-ticks", "relative", d0, d1, True,
        tick_window=tw, n_time_samples=50,
    )
    Q = 10.0 ** (d1 - d0) / 1.0001 ** x.astype(float)
    ratio = 10 ** la / 10 ** lr
    finite = np.isfinite(ratio)
    expected = np.broadcast_to(Q[None, :], ratio.shape)
    assert np.allclose(ratio[finite], expected[finite], rtol=1e-9)


def test_lm_xlabel_follows_orientation():
    from src.graphics.labels import lm_xlabel
    assert lm_xlabel(True)  == "log(K / S)"
    assert lm_xlabel(False) == "log(S / K)"


def test_labels_carry_units_and_axis_sign():
    import matplotlib
    matplotlib.use("Agg")
    from src.graphics.price_impact import _cbar_label, _xlabel
    # Absolute impact names both tokens; the denominator is the base token.
    assert _cbar_label("absolute", "WETH_USDC") == "log10(Δ(USDC/WETH) per WETH)"
    assert _cbar_label("relative", "WETH_USDC") == "log10(Δln P per WETH)"
    assert _cbar_label("absolute", "WBTC_WETH") == "log10(Δ(WETH/WBTC) per WBTC)"
    # x holds (curr_tick - tick)*log(1.0001): log(K/S) only when inverted.
    assert _xlabel("log-moneyness", True) == "log(K / S)"
    assert _xlabel("log-moneyness", False) == "log(S / K)"
    # Non-price axes are unaffected by invert.
    assert _xlabel("relative-ticks", True) == _xlabel("relative-ticks", False)
    assert _xlabel("absolute-ticks", True) == "Absolute Tick"


if __name__ == "__main__":
    for _name, _fn in sorted(globals().items()):
        if _name.startswith("test_") and callable(_fn):
            _fn(); print(f"PASS {_name}")
    print("ALL PASS")
