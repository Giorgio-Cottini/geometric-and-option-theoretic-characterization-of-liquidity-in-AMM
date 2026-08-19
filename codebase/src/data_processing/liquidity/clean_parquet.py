"""
clean_parquet.py
----------------
Preprocesses raw Uniswap V3 tick evolution parquets produced by
data_extraction/download_liquidity_evolution.py, applying the same
reconstruct_liquidity_cumsum logic as snapshot/liquidity_pipeline.py but in a
pool-agnostic way driven by data_extraction/config.POOLS.

Input  : data/raw/liquidity/{PAIR}/{fee}bp_ticks.parquet
         data/raw/liquidity/{PAIR}/{fee}bp_pool_states.parquet
Output : data/processed/liquidity/{PAIR}/{fee}bp_ticks.parquet

Schema (output)
---------------
    block_number  int64    — Ethereum block of the snapshot
    tick_idx      int64    — Uniswap V3 tick index
    price_lower   float64  — lower price bound of the tick interval
    price_upper   float64  — upper price bound of the tick interval
    liquidity     float64  — reconstructed ℓ
    curr_tick     int64    — pool slot0 tick at this block

Per-pool conventions
--------------------
Each pool in config.POOLS specifies:
  - token0_decimals, token1_decimals
  - tick_spacing
  - invert_price flag

Price formula (driven by invert_price):
    invert=True  → price = 10^(d1−d0) / 1.0001^tick     (token0 per token1)
    invert=False → price = 1.0001^tick * 10^(d0−d1)     (token1 per token0)

Liquidity reconstruction (anchored cumsum, identical to snapshot pipeline):
    ℓ[i] = (cumsum[i] − cumsum[anchor] + curr_liquidity) / 10^((d0+d1)/2)
where anchor = rightmost initialized tick ≤ curr_tick.

Usage
-----
    python codebase/src/data_processing/liquidity/clean_parquet.py
    python codebase/src/data_processing/liquidity/clean_parquet.py --pool WETH_USDC@1bp
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ── Path bootstrap ────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # codebase/
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "data_extraction"))

from data_extraction import config as ext_config  # noqa: E402

# ── Constants ─────────────────────────────────────────────────────────────────
MAX_PRICE_RATIO: float = 100.0  # drop ticks whose price interval lies outside
                                # [spot/MAX_PRICE_RATIO, spot*MAX_PRICE_RATIO]


def _dirs(pair: str) -> tuple[Path, Path]:
    """Return (raw_dir, processed_dir) for the given pair label."""
    return ext_config.out_dir(pair), ext_config.processed_dir(pair)


def _decimal_adj(token0_decimals: int, token1_decimals: int) -> float:
    """
    Geometric-mean decimal adjustment used in the liquidity reconstruction.

    Uniswap V3 raw L is in units of √(token0_smallest × token1_smallest);
    converting to √(token0_unit × token1_unit) requires dividing by
    10^((d0 + d1) / 2).
    """
    return 10.0 ** ((token0_decimals + token1_decimals) / 2.0)


def _price_from_tick(
    tick: np.ndarray | int | float,
    token0_decimals: int,
    token1_decimals: int,
    invert: bool,
) -> np.ndarray | float:
    """
    Convert Uniswap v3 tick(s) to human-readable price.

    See module docstring for the formula. Vectorised over `tick`.
    """
    if invert:
        return (10.0 ** (token1_decimals - token0_decimals)) / (1.0001 ** tick)
    return (1.0001 ** tick) * (10.0 ** (token0_decimals - token1_decimals))


# ── Core reconstruction ───────────────────────────────────────────────────────


def _reconstruct_block(
    group: pd.DataFrame,
    pcfg: dict,
    curr_tick: int,
    curr_liquidity: int,
) -> pd.DataFrame:
    """
    Apply reconstruct_liquidity_cumsum logic to one block's tick data using the
    pair config.

    Anchored cumsum (matching snapshot/liquidity_pipeline.py):
        ℓ[i] = (cumsum[i] − cumsum[anchor] + curr_liquidity) / decimal_adj
    where anchor = rightmost initialized tick ≤ curr_tick.

    Args:
        group          : per-block tick rows, unsorted (must have liquidity_net,
                         liquidity_gross as Python int after conversion).
        pcfg           : entry from config.POOLS for this pool.
        curr_tick      : pool slot0 tick at this block.
        curr_liquidity : pool slot0 liquidity at this block (raw uint128 int).
    Returns:
        DataFrame with [tick_idx, price_lower, price_upper, liquidity, curr_tick],
        filtered to the economically relevant price range. Empty if no ticks survive.
    """
    spacing = pcfg["tick_spacing"]
    d0, d1 = pcfg["token0_decimals"], pcfg["token1_decimals"]
    invert = pcfg["invert_price"]
    decimal_adj = _decimal_adj(d0, d1)

    df = group.sort_values("tick_idx").reset_index(drop=True)

    # ── Step 1: drop uninitialized ticks (liquidityGross == 0) ───────────────
    df = df[df["liquidity_gross"] > 0].reset_index(drop=True)
    if df.empty:
        return pd.DataFrame(
            columns=["tick_idx", "price_lower", "price_upper", "liquidity", "curr_tick"]
        )

    # ── Step 2: reconstruct ℓ via anchored cumsum ────────────────────────────
    _raw_anchor = int(df["tick_idx"].searchsorted(curr_tick, side="right")) - 1
    if _raw_anchor < 0:
        print(
            f"[WARN] anchor clamp: curr_tick={curr_tick} below all ticks "
            f"(min={df['tick_idx'].iloc[0]}), block={df['block_number'].iloc[0]}"
        )
    anchor_idx = max(0, _raw_anchor)
    cumsum = df["liquidity_net"].cumsum()
    df["liquidity"] = (cumsum - cumsum.iloc[anchor_idx] + curr_liquidity) / decimal_adj

    # ── Step 3: price bounds (per-pair invert flag) ──────────────────────────
    # When invert=True, price decreases with tick → swap (lower, upper) bounds.
    if invert:
        df["price_lower"] = _price_from_tick(df["tick_idx"] + spacing, d0, d1, invert)
        df["price_upper"] = _price_from_tick(df["tick_idx"],           d0, d1, invert)
    else:
        df["price_lower"] = _price_from_tick(df["tick_idx"],           d0, d1, invert)
        df["price_upper"] = _price_from_tick(df["tick_idx"] + spacing, d0, d1, invert)

    # ── Step 4: drop ticks outside the economically relevant price range ─────
    spot = _price_from_tick(curr_tick, d0, d1, invert)
    df = df[
        (df["price_upper"] >= spot / MAX_PRICE_RATIO)
        & (df["price_lower"] <= spot * MAX_PRICE_RATIO)
    ].reset_index(drop=True)

    if df.empty:
        return pd.DataFrame(
            columns=["tick_idx", "price_lower", "price_upper", "liquidity", "curr_tick"]
        )

    df["curr_tick"] = curr_tick
    return df[["tick_idx", "price_lower", "price_upper", "liquidity", "curr_tick"]]


# ── Pipeline entry point ──────────────────────────────────────────────────────


def clean_parquet(pool_key: str, verbose: bool = True) -> None:
    """
    Preprocess the raw tick evolution parquet for one pool and write the
    cleaned result to data/processed/liquidity/{pair}/.

    Requires the pool_states parquet produced by
    data_extraction/download_liquidity_evolution.py. Each block's liquidity is
    anchored using the actual pool slot0 tick and liquidity from that parquet.

    Args:
        pool_key : pool label, must be a key of config.POOLS (e.g. 'WETH_USDC@1bp').
                   Several fee tiers of one pair share a folder and are told apart
                   by `file_basename`.
        verbose  : print progress information.
    """
    if pool_key not in ext_config.POOLS:
        raise KeyError(f"Unknown pool '{pool_key}'. Available: {list(ext_config.POOLS)}")
    pcfg = ext_config.POOLS[pool_key]

    raw_dir, processed_dir = _dirs(pcfg["pair"])
    basename = pcfg["file_basename"]
    raw_path = raw_dir / f"{basename}_ticks.parquet"
    pool_states_path = raw_dir / f"{basename}_pool_states.parquet"
    out_path = processed_dir / f"{basename}_ticks.parquet"

    if not raw_path.exists():
        raise FileNotFoundError(f"Raw parquet not found: {raw_path}")
    if not pool_states_path.exists():
        raise FileNotFoundError(
            f"Pool states parquet not found: {pool_states_path}\n"
            "Run data_extraction/download_liquidity_evolution.py first."
        )

    if verbose:
        print(f"\n{'—' * 60}")
        print(f"CLEAN PARQUET — {pool_key}  (spacing={pcfg['tick_spacing']}, "
              f"invert={pcfg['invert_price']})")

    # ── Load ──────────────────────────────────────────────────────────────────
    raw = pd.read_parquet(raw_path)
    n_blocks = raw["block_number"].nunique()
    if verbose:
        print(f"  loaded   : {len(raw):,} rows  ({n_blocks} blocks)")

    # ── Load per-block pool state ─────────────────────────────────────────────
    pool_states = pd.read_parquet(pool_states_path)
    pool_states["curr_tick"] = pool_states["curr_tick"].astype("int64")
    pool_states["curr_liquidity"] = pool_states["curr_liquidity"].apply(int)
    pool_states = pool_states.set_index("block_number")
    if verbose:
        print(f"  pool states : {len(pool_states)} blocks with slot0 data")

    # ── Convert 128-bit string columns to Python int ──────────────────────────
    raw["liquidity_net"] = raw["liquidity_net"].apply(int)
    raw["liquidity_gross"] = raw["liquidity_gross"].apply(int)

    # ── Apply per-block reconstruction ────────────────────────────────────────
    frames: list[pd.DataFrame] = []
    skipped = 0

    for block, group in raw.groupby("block_number", sort=True):
        if block not in pool_states.index:
            skipped += 1
            continue
        state = pool_states.loc[block]
        result = _reconstruct_block(
            group,
            pcfg,
            curr_tick=int(state["curr_tick"]),
            curr_liquidity=int(state["curr_liquidity"]),
        )
        if result.empty:
            continue
        result.insert(0, "block_number", np.int64(block))
        frames.append(result)

    if skipped and verbose:
        print(f"  skipped  : {skipped} blocks with no pool state")

    if not frames:
        raise RuntimeError("No tick data survived preprocessing — output is empty.")

    processed = pd.concat(frames, ignore_index=True)
    processed["block_number"] = processed["block_number"].astype("int64")
    processed["tick_idx"] = processed["tick_idx"].astype("int64")
    processed["curr_tick"] = processed["curr_tick"].astype("int64")

    # ── Write ─────────────────────────────────────────────────────────────────
    processed_dir.mkdir(parents=True, exist_ok=True)
    processed.to_parquet(out_path, index=False)

    if verbose:
        active = processed[processed["liquidity"] > 0]
        print(
            f"  output   : {len(processed):,} rows  "
            f"({processed['block_number'].nunique()} blocks)"
        )
        print(f"  ℓ > 0    : {len(active):,} tick-intervals")
        if not active.empty:
            print(
                f"  price range (all blocks): "
                f"[{active['price_lower'].min():.6g}, {active['price_upper'].max():.6g}]"
            )
        ct = processed.groupby("block_number")["curr_tick"].first()
        print(f"  curr_tick range : [{ct.min()}, {ct.max()}]")
        print(f"  saved → {out_path}")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Preprocess raw tick evolution parquets into cleaned per-block "
                    "liquidity profiles, per pool."
    )
    parser.add_argument(
        "--pool",
        type=str,
        choices=list(ext_config.POOLS.keys()),
        default=None,
        help="Pool label to process (e.g. WETH_USDC@1bp). Omit to process all pools.",
    )
    args = parser.parse_args()

    pools = [args.pool] if args.pool is not None else list(ext_config.POOLS.keys())
    for key in pools:
        clean_parquet(key)
