"""
Marginal price-impact surfaces derived from the historical liquidity surface.

Pointwise transforms of L(P, t) — no new data, no new reconstruction:
    absolute marginal impact :  dP/dx      = 2 * P**1.5 / L
    relative marginal impact :  d ln P/dx  = 2 * P**0.5 / L

P is the pool price in the project's human-unit convention (token0Price lineage),
computed from the tick via clean_parquet._price_from_tick; L is the parquet
`liquidity` column (already decimal-normalised) recovered from the existing
liquidity-surface builders as exp(log_liq). Magnitudes only.

Frame convention (why the inverted pools are correct)
-----------------------------------------------------
The formulas above are derived in the AMM-native frame, where P is token1 per
token0 and x = L/sqrt(P) is the token0 reserve — so "per unit x" means per unit
of token0. For an inverted pool `_price_from_tick` returns Q = 1/P instead, and
substituting it into the same expression is nonetheless correct, because the
invariant is symmetric under the flip:

    dy = (L/2) P**-0.5 dP,  dQ = -dP/P**2   =>   dQ/dy = -2 Q**1.5 / L

Identical functional form, with the trade now denominated in token1 rather than
token0. L is unchanged by the flip: L = sqrt(x*y) is symmetric, and its decimal
normalisation 10**((d0+d1)/2) is a geometric mean, hence symmetric too.

Net effect: `invert` flips the quoted price AND the reserve leg together, so the
trade denominator is always the BASE token — the denominator of the quote. For
WETH_USDC (token0=USDC, token1=WETH, invert=True) the absolute impact is
therefore d(USDC per WETH) / d(WETH): dollars of ETH-price movement per ETH
traded. See impact_units().

This module is a *sibling* of the frozen replication builders
(build_liquidity_surface, build_lvsp_surface): it CALLS them read-only and never
alters their behaviour or outputs.

Public API
----------
impact_from_PL(P, L, quantity) -> ndarray
impact_units(pair) -> (quote_token, base_token)
build_impact_surface(df, tick_spacing, axis, quantity, d0, d1, invert,
                     tick_radius, tick_window, n_time_samples, relative_tick_M)
    -> (x_axis, times, log10_impact, curr_ticks, sampled_blocks)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .liquidity_profile import build_liquidity_surface
from .liquidity_vs_price import build_lvsp_surface
from ..data_processing.liquidity.clean_parquet import _price_from_tick

_LOG1P = np.log(1.0001)


def impact_from_PL(
    P: np.ndarray, L: np.ndarray, quantity: str
) -> np.ndarray:
    """
    Marginal price impact from price P and active liquidity L (elementwise).

        quantity="absolute" : 2 * P**1.5 / L   (units: price per unit qty)
        quantity="relative" : 2 * P**0.5 / L   (units: 1 per unit qty)

    NaN in L (liquidity absent) propagates to NaN impact; P is always defined.
    """
    P = np.asarray(P, dtype=np.float64)
    L = np.asarray(L, dtype=np.float64)
    if quantity == "absolute":
        return 2.0 * P ** 1.5 / L
    if quantity == "relative":
        return 2.0 * P ** 0.5 / L
    raise ValueError(
        f"quantity must be 'absolute' or 'relative'; got {quantity!r}"
    )


def impact_units(pair: str) -> tuple[str, str]:
    """
    Resolve (quote_token, base_token) from a pool label.

    Pair labels are BASE_QUOTE (e.g. "WETH_USDC" = WETH quoted in USDC), and
    the project's price convention returns quote-per-base:

        invert=False -> price = token1 per token0  -> base = token0
        invert=True  -> price = token0 per token1  -> base = token1

    The impact denominator is ALWAYS the base token (see module docstring).
    Verified against every configured pool by
    tests/test_price_impact.py::test_base_token_is_the_impact_denominator.
    """
    base, quote = pair.split("_", 1)
    return quote, base


def build_impact_surface(
    df: pd.DataFrame,
    tick_spacing: int,
    axis: str,
    quantity: str,
    d0: int,
    d1: int,
    invert: bool,
    tick_radius: int | None = None,
    tick_window: tuple[int, int] | None = None,
    n_time_samples: int = 200,
    relative_tick_M: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Build a dense log10(marginal price impact) surface by transforming the
    existing liquidity surface pointwise.

    The liquidity builders are called read-only; L is recovered as exp(log_liq)
    (round-trip is exact to float precision and preserves the NaN mask). P is
    computed per cell from that cell's absolute tick via _price_from_tick, then
    impact = f(P, L), returned as log10.

    Axis geometry (mirrors the liquidity plotters, passed in by the caller):
        "log-moneyness" / "relative-ticks" : require `tick_radius`; the absolute
            tick of each cell is curr_tick(t) − x/log(1.0001)  (log-moneyness) or
            curr_tick(t) + x  (relative-ticks).
        "absolute-ticks" : requires `tick_window=(lower, upper)`; P depends only
            on the column (fixed absolute tick grid), broadcast over rows.

    Returns:
        x_axis        : 1-D array — log-moneyness / relative tick / absolute tick.
        times         : 1-D float64 normalized block numbers in [0, 1].
        log10_impact  : 2-D float64 (n_time × n_x). NaN = liquidity's NaN mask.
        curr_ticks    : 1-D float64 pool curr_tick per sampled block (spot line).
        sampled_blocks: 1-D int64 block numbers, one per time row.
    """
    if axis in ("log-moneyness", "relative-ticks"):
        if tick_radius is None:
            raise ValueError(f"axis={axis!r} requires tick_radius")
        use_lm = axis == "log-moneyness"
        x_axis, times, log_liq, sampled_blocks = build_liquidity_surface(
            df, tick_radius, n_time_samples, 0.0, use_lm,
            relative_tick_M=relative_tick_M,
        )
        liquidity = np.exp(log_liq)  # (n_time, n_x); NaN preserved

        # curr_tick per sampled block (same groupby "first" the builder uses).
        curr_tick_map = df.groupby("block_number")["curr_tick"].first()
        curr_ticks = curr_tick_map.loc[sampled_blocks].to_numpy(dtype=np.float64)

        # Absolute tick of each cell → price per cell.
        if use_lm:
            abs_tick = curr_ticks[:, None] - x_axis[None, :] / _LOG1P
        else:
            abs_tick = curr_ticks[:, None] + x_axis[None, :]
        price = _price_from_tick(abs_tick, d0, d1, invert)  # (n_time, n_x)

    elif axis == "absolute-ticks":
        if tick_window is None:
            raise ValueError("axis='absolute-ticks' requires tick_window=(lo, hi)")
        tick_lower, tick_upper = tick_window
        abs_tick_grid, times, log_liq, curr_ticks_i, sampled_blocks = (
            build_lvsp_surface(
                df, tick_lower, tick_upper, tick_spacing, n_time_samples
            )
        )
        liquidity = np.exp(log_liq)
        x_axis = abs_tick_grid
        curr_ticks = curr_ticks_i.astype(np.float64)
        price_col = _price_from_tick(
            abs_tick_grid.astype(np.float64), d0, d1, invert
        )  # (n_x,)
        price = np.broadcast_to(price_col[None, :], liquidity.shape)

    else:
        raise ValueError(
            "axis must be 'log-moneyness', 'relative-ticks', or "
            f"'absolute-ticks'; got {axis!r}"
        )

    impact = impact_from_PL(price, liquidity, quantity)  # NaN where L NaN
    with np.errstate(invalid="ignore", divide="ignore"):
        log10_impact = np.log10(impact)

    return x_axis, times, log10_impact, curr_ticks, sampled_blocks
