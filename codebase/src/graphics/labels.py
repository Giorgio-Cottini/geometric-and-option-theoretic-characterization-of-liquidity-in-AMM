"""
Axis labels shared by the liquidity and price-impact plotters.

Both families of plots draw the same x-array and must name it the same way, so
the mapping lives here rather than being duplicated (and drifting) between
graphics/liquidity_profile.py and graphics/price_impact.py.
"""

# The surface builders fix one x-array for every pool:
#     x = (curr_tick - tick_idx) * log(1.0001)
# Whether that array IS log(K/S) depends on which way human price runs with
# tick, which is exactly what `invert` selects in _price_from_tick. With
# S = P(curr_tick) the spot and K = P(tick_idx) the strike:
#
#   invert=True   P(t) = 10**(d1-d0) / 1.0001**t     (decreasing in tick)
#                 log(K/S) = (curr_tick - tick_idx) * log(1.0001) = x
#
#   invert=False  P(t) = 1.0001**t * 10**(d0-d1)     (increasing in tick)
#                 log(K/S) = (tick_idx - curr_tick) * log(1.0001) = -x
#                 so x = log(S/K)
#
# The array is identical either way — only its name changes.
_LM_LABEL = {True: "log(K / S)", False: "log(S / K)"}


def lm_xlabel(invert: bool) -> str:
    """Log-moneyness axis label for a pool of the given orientation."""
    return _LM_LABEL[invert]
