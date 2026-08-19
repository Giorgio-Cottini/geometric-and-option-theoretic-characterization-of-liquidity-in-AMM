from datetime import datetime, timezone

import numpy as np
import pandas as pd

from .utils import _sep, load_options_book
from ...math_core import linear_interpolation

# Deribit expiry settlement hour (08:00 UTC)
_DERIBIT_SETTLE_HOUR: int = 8


def _parse_expiry_datetime(expiry_label: str) -> datetime:
    """
    Convert a Deribit expiry label (e.g. '27MAR26') to a UTC datetime at settlement.

    Deribit settles at 08:00 UTC on the expiry date.
    """
    dt = datetime.strptime(expiry_label, "%d%b%y")
    return dt.replace(hour=_DERIBIT_SETTLE_HOUR, tzinfo=timezone.utc)

# ———————————————————————————————————————————————————————————————————————————————————————————— #
"""
Note on the following function:
RTW26 uses mid prices only as a proxy for moneyness.
A better approach could be to use the forward price (from the oracle or underlying_price) instead of mid price, to compute log moneyness as log(strike / forward).
"""


def parse_options(book) -> pd.DataFrame:
    """
    Process raw options book data into a DataFrame with relevant features.
    Args:
        book:list of dicts with keys including "instrument_name", "bid_price", "ask_price", "underlying_price", "mark_iv"
    Returns:
        pd.DataFrame: Processed options data
    """
    df = pd.DataFrame(book)
    # Parse instrument name: ETH-{expiry}-{strike}-{C/P}
    parsed = df["instrument_name"].str.extract(
        r"ETH-(?P<expiry>\w+)-(?P<strike>\d+)-(?P<type>[CP])"
    )
    df = pd.concat([df, parsed], axis=1)
    df["strike"] = df["strike"].astype(float)
    df["mid_price"] = (
        (df["bid_price"] + df["ask_price"]) / 2 * df["underlying_price"]
    )  # ETH → USD
    df["forward"] = df["underlying_price"]
    df["log_moneyness"] = np.log(df["strike"] / df["forward"])

    # Time-to-maturity in years (Deribit settles at 08:00 UTC)
    snapshot_ts = pd.to_datetime(df["creation_timestamp"], unit="ms", utc=True)
    expiry_dt = df["expiry"].map(_parse_expiry_datetime)
    df["T_years"] = (expiry_dt - snapshot_ts).dt.total_seconds() / (365.25 * 86400)

    keep = [
        "expiry",
        "strike",
        "type",
        "mid_price",
        "forward",
        "mark_iv",
        "log_moneyness",
        "T_years",
    ]
    return df[keep].sort_values(["expiry", "type", "strike"]).reset_index(drop=True)


# ———————————————————————————————————————————————————————————————————————————————————————————— #
"""
Note on the following function:
the function operates per option type; the caller is responsible for groupby(expiry) if passing a multi-expiry DataFrame.
"""


def arbitrage_filter(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply no-arbitrage filters to a single-expiry options DataFrame.
    Operates on calls and puts independently; ITM gaps are handled downstream by fill_ITM_gaps.

    Filters applied in order:
      1. Positive prices: remove rows with mid_price <= 0.
      2. Monotonicity: calls non-increasing in strike; puts non-decreasing in strike.
      3. Convexity (no butterfly arb): second difference in price w.r.t. strike >= 0.

    Args:
        df: single-expiry slice from parse_options, sorted by (type, strike).
            Must contain columns: strike, type, mid_price.
    Returns:
        Filtered DataFrame with the same columns, reset index.
    """
    parts = []
    for opt_type, grp in df.groupby("type"):
        g = grp.sort_values("strike").copy()

        # —————————————————————————————————— #
        # 1. Positive prices
        g = g[g["mid_price"] > 0]

        # —————————————————————————————————— #
        # 2. Monotonicity
        if (
            opt_type == "C"
        ):  # Calls: price must be non-increasing → keep only the running minimum
            g = g[g["mid_price"] == g["mid_price"].cummin()]
        else:  # Puts:  price must be non-decreasing → keep only the running maximum
            g = g[g["mid_price"] == g["mid_price"].cummax()]

        # —————————————————————————————————— #
        # 3. Convexity: second finite difference >= 0
        # For three consecutive strikes K_{i-1}, K_i, K_{i+1}:
        #   C(K_{i-1}) - 2*C(K_i) + C(K_{i+1}) >= 0
        # Implemented as an iterative forward pass: drop any point that creates a  negative second difference with its current neighbours.
        prices = g["mid_price"].to_numpy(dtype=float)
        strikes = g["strike"].to_numpy(dtype=float)
        keep_mask = np.ones(len(g), dtype=bool)
        for i in range(1, len(g) - 1):
            if not (keep_mask[i - 1] and keep_mask[i]):
                continue
            # find next kept index after i
            j = i + 1
            while j < len(g) and not keep_mask[j]:
                j += 1
            if j >= len(g):
                break
            # butterfly spread value (sign-convention: same for calls and puts)
            butterfly = prices[i - 1] - 2 * prices[i] + prices[j]
            if butterfly < 0:
                keep_mask[i] = False

        parts.append(g.iloc[keep_mask])

    return pd.concat(parts).sort_values(["type", "strike"]).reset_index(drop=True)


# ———————————————————————————————————————————————————————————————————————————————————————————— #
def fill_ITM_gaps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Synthesise missing OTM prices via put-call parity (r=0):
        C(K) = P(K) + F - K,  P(K) = C(K) - F + K

    Rather than a fixed-dollar gap threshold, coverage is extended by parity as long as
    the Breeden-Litzenberger density q(K) = d²C/dK² remains non-negative.  Stops at the
    first candidate strike where including the synthetic price would imply q(K) < 0 at
    its inner neighbour, signalling an arbitrage in the combined surface.

    Args:
        df:   single-expiry slice from arbitrage_filter.
              Columns required: strike, type, mid_price, forward, expiry, log_moneyness.
    Returns:
        DataFrame with same schema, sorted by (type, strike), index reset.
    """

    calls = df[df["type"] == "C"].sort_values("strike")
    puts = df[df["type"] == "P"].sort_values("strike")
    F = df["forward"].iloc[0]
    exp = df["expiry"].iloc[0]

    if calls.empty or puts.empty:
        return df.sort_values(["type", "strike"]).reset_index(drop=True)

    K_c = calls["strike"].to_numpy(dtype=float)
    P_c = calls["mid_price"].to_numpy(dtype=float)
    K_p = puts["strike"].to_numpy(dtype=float)
    P_p = puts["mid_price"].to_numpy(dtype=float)

    # ———————————————————————————————————————————————————————————————————————————————————— #
    def _density_positive(
        K0: float, P0: float, K1: float, P1: float, K2: float, P2: float
    ) -> bool:
        """Breeden-Litzenberger: q(K1) >= 0 iff this weighted second difference is non-negative (unequal spacing)."""
        dKl, dKr = K1 - K0, K2 - K1
        return P0 * dKr + P2 * dKl - P1 * (dKl + dKr) >= 0

    # ———————————————————————————————————————————————————————————————————————————————————— #
    def _synth(
        K: np.ndarray, donor_K: np.ndarray, donor_P: np.ndarray, target_type: str
    ) -> np.ndarray:
        """Interpolate donor prices onto K, apply put-call parity, floor at 0."""
        prices = np.interp(K, donor_K, donor_P)
        raw = prices + F - K if target_type == "C" else prices - F + K
        return np.maximum(raw, 0.0)

    # ———————————————————————————————————————————————————————————————————————————————————— #
    # Grab T_years from existing data (all rows share the same value)
    T_years_val = df["T_years"].iloc[0] if "T_years" in df.columns else np.nan

    def _make_df(K: np.ndarray, P: np.ndarray, opt_type: str) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "expiry": exp,
                "strike": K,
                "type": opt_type,
                "mid_price": P,
                "forward": F,
                "mark_iv": np.nan,
                "log_moneyness": np.log(K / F),
                "T_years": T_years_val,
            }
        )

    # ———————————————————————————————————————————————————————————————————————————————————— #
    def _extend_left(
        real_K: np.ndarray,
        real_P: np.ndarray,
        donor_K: np.ndarray,
        donor_P: np.ndarray,
        target_type: str,
    ) -> pd.DataFrame | None:
        """
        Add synthetic prices at donor strikes below real_K[0].
        Walks nearest-to-farthest; stops at the first strike where including it
        would make q < 0 at the current leftmost accepted point (K1).
        """
        cands = donor_K[donor_K < real_K[0]][::-1]  # descending: nearest real first
        if len(cands) == 0 or len(real_K) < 2:
            return None
        cand_P = _synth(cands, donor_K, donor_P, target_type)

        acc_K: list[float] = []
        acc_P: list[float] = []
        for K_new, P_new in zip(cands, cand_P):
            # K1: current leftmost accepted point; K2: its right neighbour
            K1 = acc_K[0] if acc_K else real_K[0]
            P1 = acc_P[0] if acc_P else real_P[0]
            K2 = acc_K[1] if len(acc_K) > 1 else (real_K[0] if acc_K else real_K[1])
            P2 = acc_P[1] if len(acc_P) > 1 else (real_P[0] if acc_P else real_P[1])
            if not _density_positive(K_new, P_new, K1, P1, K2, P2):
                break
            acc_K.insert(0, K_new)
            acc_P.insert(0, P_new)

        return (
            _make_df(np.array(acc_K), np.array(acc_P), target_type) if acc_K else None
        )

    # ———————————————————————————————————————————————————————————————————————————————————— #
    def _extend_right(
        real_K: np.ndarray,
        real_P: np.ndarray,
        donor_K: np.ndarray,
        donor_P: np.ndarray,
        target_type: str,
    ) -> pd.DataFrame | None:
        """
        Add synthetic prices at donor strikes above real_K[-1].
        Walks nearest-to-farthest; stops at the first strike where including it
        would make q < 0 at the current rightmost accepted point (K1).
        """
        cands = donor_K[donor_K > real_K[-1]]  # ascending: nearest real first
        if len(cands) == 0 or len(real_K) < 2:
            return None
        cand_P = _synth(cands, donor_K, donor_P, target_type)

        acc_K: list[float] = []
        acc_P: list[float] = []
        for K_new, P_new in zip(cands, cand_P):
            # K1: current rightmost accepted point; K0: its left neighbour
            K1 = acc_K[-1] if acc_K else real_K[-1]
            P1 = acc_P[-1] if acc_P else real_P[-1]
            K0 = acc_K[-2] if len(acc_K) > 1 else (real_K[-1] if acc_K else real_K[-2])
            P0 = acc_P[-2] if len(acc_P) > 1 else (real_P[-1] if acc_P else real_P[-2])
            if not _density_positive(K0, P0, K1, P1, K_new, P_new):
                break
            acc_K.append(K_new)
            acc_P.append(P_new)

        return (
            _make_df(np.array(acc_K), np.array(acc_P), target_type) if acc_K else None
        )

    # ———————————————————————————————————————————————————————————————————————————————————— #

    parts = [calls, puts]

    # Synthesise calls at low strikes (from puts) and puts at high strikes (from calls)
    synth_calls = _extend_left(K_c, P_c, K_p, P_p, "C")
    synth_puts = _extend_right(K_p, P_p, K_c, P_c, "P")

    if synth_calls is not None:
        parts.append(synth_calls)
    if synth_puts is not None:
        parts.append(synth_puts)

    result = pd.concat(parts).drop_duplicates(subset=["type", "strike"])
    return result.sort_values(["type", "strike"]).reset_index(drop=True)


# ———————————————————————————————————————————————————————————————————————————————————————————— #
def run_options_pipeline(spot: float, verbose: bool = True) -> dict[str, dict]:
    """
    Parse -> filter -> parity-extend -> interpolate.

    Args:
        book : raw Deribit book_summary result list.
        spot : Uniswap pool spot price P0 (used as ATM label in fill_ITM_gaps).

    Returns:
        dict keyed by expiry, each value:
            {
              "filtered" : post-arbitrage-filter DataFrame,
              "filled"   : post-fill_ITM_gaps DataFrame,
              "interp"   : {"C": (K_arr, P_arr), "P": (K_arr, P_arr)},
            }
    """

    book = load_options_book()
    # Step 1: process raw book
    options_df = parse_options(book)
    if verbose:
        _sep()
        print("OPTIONS PIPELINE")
        print(f"  raw quotes  : {len(book)}")
        print(f"  parsed      : {len(options_df)} rows")
        print(f"  expiries    : {sorted(options_df['expiry'].unique())}")

    results: dict[str, dict] = {}

    print(
        f"\n  {'Expiry':<12} {'Raw':>5} {'Filtered':>9} {'Synthetic':>10} "
        f"{'Final':>6}  {'Call range':>20}  {'Put range':>20}"
    )
    print("  " + "-" * 90)

    for expiry, group in options_df.groupby("expiry"):
        # Step 2: arbitrage filter
        filtered = arbitrage_filter(group.copy())

        # Step 3: fill ITM gaps via put-call parity (BL density criterion)
        filled = fill_ITM_gaps(filtered)

        # Step 4: piecewise-affine interpolation
        interp = linear_interpolation(filled)

        n_synth = len(filled) - len(filtered)

        if verbose:
            # Print summary statistics for this expiry
            c_range = p_range = "—"
            if "C" in interp:
                k = interp["C"][0]
                c_range = f"[{k[0]:.0f}, {k[-1]:.0f}]"
            if "P" in interp:
                k = interp["P"][0]
                p_range = f"[{k[0]:.0f}, {k[-1]:.0f}]"

            print(
                f"  {expiry:<12} {len(group):>5} {len(filtered):>9} {n_synth:>10} "
                f"{len(filled):>6}  {c_range:>20}  {p_range:>20}"
            )

        # T_years: use median to be robust (all rows in an expiry group share the same T)
        T_years = float(filled["T_years"].median())

        results[str(expiry)] = {
            "filtered": filtered,
            "filled": filled,
            "interp": interp,
            "T": T_years,
        }
    if not verbose:
        print(
            "\n"
            + "—— Options pipeline complete, set verbose=True for details ——"
            + " \n"
        )
    return results


# ———————————————————————————————————————————————————————————————————————————————————————————— #
