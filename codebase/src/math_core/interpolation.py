import numpy as np
import pandas as pd

# ———————————————————————————————————————————————————————————————————————————————————————————— #


"""
Note on the following function:
RTW26 uses linear interpolation for O^mkt(K) between the filtered, parity-extended strikes.
This is an efficient choice that allows for a closed-form antiderivative of L(K)*O^mkt(K) on each sub-interval.
Keep for BS model, definitively revisit if using a more complex ODE solver that can handle non-piecewise proxies (e.g. splines, kernel regression).
# (but beware of potential isseus caused by higher order approaches)
"""


def linear_interpolation(df: pd.DataFrame) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """
    Build piecewise-affine market proxy O^mkt(K) for each option type via linear interpolation between observed (post-filter, post-parity) strikes.

    This representation is the direct input to the integration step; on each sub-interval [K_i, K_{i+1}] the affine coefficients are:

        a1 = (prices[i+1] - prices[i]) / (strikes[i+1] - strikes[i])
        a0 = prices[i] - a1 * strikes[i]

    which feed into the closed-form antiderivative of L(K) * O^mkt(K).

    Args:
        df: single-expiry slice, sorted by (type, strike), output of fill_ITM_gaps.
    Returns:
        dict with keys "C" and "P", values are tuples (strikes, prices) of numpy arrays.
    """
    result = {}
    for opt_type, grp in df.groupby("type"):
        g = grp.sort_values("strike")
        result[opt_type] = (
            g["strike"].to_numpy(dtype=float),
            g["mid_price"].to_numpy(dtype=float),
        )
    return result


# ———————————————————————————————————————————————————————————————————————————————————————————— #
