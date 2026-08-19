import pandas as pd
from .utils import _sep, load_ticks, load_pool_state
from .config import CFG

# ———————————————————————————————————————————————————————————————————————————————————————————— #


def run_liquidity_pipeline(fee_bps: int, verbose: bool = True) -> pd.DataFrame:
    """
    Reconstruct ℓ(q) for one fee tier.
    Returns the DataFrame from reconstruct_liquidity_cumsum.
    """
    ticks = load_ticks(fee_bps)
    if verbose:
        _sep()
        print(f"LIQUIDITY PIPELINE — ETH/USDC {fee_bps}bp")
        print(f"  ticks loaded : {len(ticks)} rows (all pages)")

    state = load_pool_state(fee_bps)
    curr_liquidity = int(state["liquidity"])
    curr_tick = int(state["tick"])
    spot_price = float(state["token0Price"])  # token0Price = ETH price in USDC

    if verbose:
        print(
            f"  pool state   : tick={curr_tick}, ℓ_curr={curr_liquidity}, P0={spot_price:.2f} USDC"
        )

    # Reconstruct_liquidity_cumsum
    liq_df = reconstruct_liquidity_cumsum(ticks, fee_bps, curr_liquidity, curr_tick)

    if verbose:
        active = liq_df[liq_df["liquidity"] > 0]
        print(f"  tick intervals: {len(liq_df)} total, {len(active)} with ℓ > 0")
        print(
            f"  price range   : [{active['price_lower'].min():.4f}, {active['price_upper'].max():.2f}] USDC"
        )

        # Anchor check: the interval containing P0 should carry ℓ_curr.
        # price_upper decreases with tickIdx, so the last row where price_upper >= P0 is the active interval.
        at_spot = liq_df[liq_df["price_upper"] >= spot_price].iloc[-1]
        print(
            f"  anchor check  : ℓ at P0 interval = {at_spot['liquidity']:.2f} "
            f"(expected {curr_liquidity / CFG.decimal_adj:.2f})"
        )

        print("\n  Top-5 most-liquid tick intervals (liquidity > 0):")
        top5 = (
            liq_df[liq_df["liquidity"] > 0]
            .sort_values("liquidity", ascending=False)
            .head(5)[["tickIdx", "price_lower", "price_upper", "liquidity"]]
        )
        print(top5.to_string(index=False))

    if not verbose:
        print(
            "\n"
            + "—— Liquidity pipeline complete, set verbose=True for details ——"
            + " \n"
        )
    return liq_df


# ———————————————————————————————————————————————————————————————————————————————————————————— #


def reconstruct_liquidity_cumsum(
    ticks: list[dict], fee_bps: int, curr_liquidity: int, curr_tick: int
) -> pd.DataFrame:
    """
    Reconstruct ℓ(q) from ticks using cumulative sum, anchored to ℓ_curr at curr_tick.
    Args:
        ticks: list of dicts with keys "tickIdx" and "liquidityNet"
        fee_bps: fee tier in basis points (e.g. 5 or 30)
        curr_liquidity: current liquidity at curr_tick
        curr_tick: current tick index
    Returns:
        pd.DataFrame: Processed tick data with reconstructed liquidity
    """
    df = pd.DataFrame(ticks, dtype=object)
    df["tickIdx"] = df["tickIdx"].astype(int)
    df["liquidityNet"] = df["liquidityNet"].map(int)

    # Drop uninitialized ticks (liquidityGross == 0).
    if "liquidityGross" in df.columns:
        df["liquidityGross"] = df["liquidityGross"].map(int)
        df = df[df["liquidityGross"] > 0].reset_index(drop=True)

    df = df.sort_values("tickIdx").reset_index(drop=True)

    # Reconstruct ℓ(q): cumsum anchored to ℓ_curr at curr_tick
    anchor_idx = df["tickIdx"].searchsorted(curr_tick, side="right") - 1
    cumsum = df["liquidityNet"].cumsum()
    # Normalize to human units: raw ℓ is in √(USDC_wei × WETH_wei); dividing by
    # decimal_adj converts to √(USDC × ETH), consistent with human-unit prices.
    df["liquidity"] = (
        cumsum - cumsum.iloc[anchor_idx] + curr_liquidity
    ) / CFG.decimal_adj

    # Price bounds in USDC/ETH (inverted because token0=USDC, token1=WETH).
    spacing = CFG.tick_spacing[fee_bps]
    df["price_lower"] = CFG.decimal_adj / (1.0001 ** (df["tickIdx"] + spacing))
    df["price_upper"] = CFG.decimal_adj / (1.0001 ** df["tickIdx"])

    # Drop tick intervals outside the economically relevant price range.
    # Some genuine LP positions sit at extreme ticks (e.g. tickLower = −198060 for the
    # 30 bp pool → price_upper ≈ 4 × 10²⁰ USDC/ETH, ~1.9 × 10¹⁷ × spot).  Their
    # liquidityGross is non-zero so the zero-gross filter does not remove them, and their
    # reconstructed L is mathematically correct but orders of magnitude larger than
    # curr_liquidity, making them dominate top-liquidity rankings and corrupt downstream
    # integrals over the price axis.
    spot = CFG.decimal_adj / (1.0001**curr_tick)
    df = df[
        (df["price_upper"] >= spot / CFG.max_price_ratio)
        & (df["price_lower"] <= spot * CFG.max_price_ratio)
    ].reset_index(drop=True)

    return df[["tickIdx", "price_lower", "price_upper", "liquidity"]]


# ———————————————————————————————————————————————————————————————————————————————————————————— #
