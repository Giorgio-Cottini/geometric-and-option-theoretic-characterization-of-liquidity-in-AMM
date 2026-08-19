"""
discover_pools.py
-----------------
Exploratory, read-only pool discovery for the dataset expansion.

Answers the questions the downloader config cannot currently express:
  - which Uniswap v3 pools exist for each candidate token pair
  - which fee tiers actually carry volume *over the existing block grid*
    (not over pool lifetime — `Pool.volumeUSD` is cumulative since deployment
    and would let a 2021-dominant tier outrank a currently-dominant one)
  - whether each pool was deployed early enough to span that grid
  - the token decimals and token0/token1 ordering needed for `invert_price`

Prints a report; writes nothing. The output is meant to make the fee-tier cut
point visible (volume share, cumulative share, TVL share per tier) rather than
to apply a threshold chosen in advance.

Usage
-----
    python discover_pools.py        (from codebase/data_extraction/)
"""

import statistics
from typing import Any

import pandas as pd

import config
from download_liquidity_evolution import graphql

# ── Candidate universe ────────────────────────────────────────────────────────
# Lowercase — the subgraph indexes token ids in lowercase.
TOKENS: dict[str, str] = {
    "WETH":  "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "USDC":  "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "USDT":  "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "WBTC":  "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
    "PRIME": "0xb23d80f5fefcddaa212212f028021b41ded428cf",
}

# (label, token_a, token_b) — order here is display only; the query covers both
# on-chain orderings, since token0/token1 is fixed by address comparison.
PROBE_PAIRS: list[tuple[str, str, str]] = [
    ("WETH_USDC",  "WETH",  "USDC"),   # held
    ("WETH_USDT",  "WETH",  "USDT"),   # held
    ("WBTC_WETH",  "WBTC",  "WETH"),   # held
    ("USDC_USDT",  "USDC",  "USDT"),   # held — suspected single-tier
    ("WBTC_USDT",  "WBTC",  "USDT"),   # candidate add
    ("PRIME_USDC", "PRIME", "USDC"),   # candidate add — youngest, may not span grid
]

# Uniswap v3 fee tier (units of 1e-6) → tick spacing. Replaces the hand-typed
# `tick_spacing` field, which is only correct for the current all-5bp selection.
TICK_SPACING: dict[int, int] = {100: 1, 500: 10, 3000: 60, 10000: 200}

# Grid reference — any existing pool_states parquet carries the shared block grid.
_GRID_REF = config.out_dir("WETH_USDC") / "5bp_pool_states.parquet"

_SEC_PER_BLOCK = 12  # post-Merge slot time, fixed by protocol


# ── Grid + time anchor ────────────────────────────────────────────────────────

def load_block_grid() -> pd.Series:
    """The shared block grid, recovered from the existing download."""
    blocks = pd.read_parquet(_GRID_REF, columns=["block_number"])["block_number"]
    return pd.Series(sorted(blocks.unique()), name="block_number")


def fetch_chain_anchor() -> tuple[int, int]:
    """Latest indexed (block_number, unix_timestamp) — anchors block → time."""
    meta = graphql("{ _meta { block { number timestamp } } }")["_meta"]["block"]
    return int(meta["number"]), int(meta["timestamp"])


def block_to_unix(block: int, anchor_block: int, anchor_unix: int) -> int:
    """Extrapolate a block's timestamp at the fixed post-Merge slot time."""
    return anchor_unix - (anchor_block - block) * _SEC_PER_BLOCK


# ── Subgraph queries ──────────────────────────────────────────────────────────

def fetch_pools(addr_a: str, addr_b: str) -> list[dict[str, Any]]:
    """Every pool holding exactly these two tokens, either on-chain ordering."""
    q = f"""{{
      pools(
        where: {{token0_in: ["{addr_a}","{addr_b}"], token1_in: ["{addr_a}","{addr_b}"]}},
        orderBy: volumeUSD, orderDirection: desc, first: 20
      ) {{
        id feeTier createdAtBlockNumber totalValueLockedUSD
        token0 {{ symbol decimals }}
        token1 {{ symbol decimals }}
      }}
    }}"""
    return graphql(q)["pools"]


def fetch_window_stats(pool_id: str, unix_start: int, unix_end: int) -> dict[str, float]:
    """Volume / TVL / coverage for one pool, restricted to the grid's time span."""
    q = f"""{{
      poolDayDatas(
        where: {{pool: "{pool_id}", date_gte: {unix_start}, date_lte: {unix_end}}},
        orderBy: date, first: 1000
      ) {{ volumeUSD tvlUSD }}
    }}"""
    days = graphql(q)["poolDayDatas"]
    if not days:
        return {"volume_usd": 0.0, "tvl_usd_median": 0.0, "n_days": 0}
    return {
        "volume_usd": sum(float(d["volumeUSD"]) for d in days),
        "tvl_usd_median": statistics.median(float(d["tvlUSD"]) for d in days),
        "n_days": len(days),
    }


# ── Report ────────────────────────────────────────────────────────────────────

def _fmt_usd(x: float) -> str:
    for unit, scale in (("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(x) >= scale:
            return f"{x / scale:.2f}{unit}"
    return f"{x:.0f}"


def report_pair(label: str, rows: list[dict[str, Any]], grid_days: int) -> None:
    """One pair's tier table, sorted by window volume, with shares."""
    total_volume = sum(r["volume_usd"] for r in rows) or 1.0
    total_tvl = sum(r["tvl_usd_median"] for r in rows) or 1.0
    rows = sorted(rows, key=lambda r: r["volume_usd"], reverse=True)

    print(f"\n=== {label} ===")
    print(f"  {'tier':>7} {'vol(window)':>12} {'vol%':>6} {'cum%':>6} "
          f"{'TVLmed':>10} {'TVL%':>6} {'days':>5} {'spans':>6}  pool")
    cumulative_pct = 0.0
    for r in rows:
        volume_pct = 100.0 * r["volume_usd"] / total_volume
        cumulative_pct += volume_pct
        print(
            f"  {str(r['fee_bps']) + 'bp':>7} {_fmt_usd(r['volume_usd']):>12} "
            f"{volume_pct:>5.1f}% {cumulative_pct:>5.1f}% "
            f"{_fmt_usd(r['tvl_usd_median']):>10} "
            f"{100.0 * r['tvl_usd_median'] / total_tvl:>5.1f}% "
            f"{r['n_days']:>5} {str(r['spans_grid']):>6}  {r['pool_addr']}"
        )
    head = rows[0]
    print(f"  tokens: token0={head['token0']} (d={head['d0']})  "
          f"token1={head['token1']} (d={head['d1']})  | grid spans {grid_days} days")


def main() -> None:
    grid = load_block_grid()
    anchor_block, anchor_unix = fetch_chain_anchor()
    unix_start = block_to_unix(int(grid.iloc[0]), anchor_block, anchor_unix)
    unix_end = block_to_unix(int(grid.iloc[-1]), anchor_block, anchor_unix)
    grid_days = (unix_end - unix_start) // 86_400

    print(
        f"Grid    : {len(grid)} blocks  {grid.iloc[0]}..{grid.iloc[-1]}  "
        f"(spacing {int(grid.diff().median())})\n"
        f"Window  : {pd.to_datetime(unix_start, unit='s').date()} .. "
        f"{pd.to_datetime(unix_end, unit='s').date()}  ({grid_days} days)\n"
        f"Anchor  : block {anchor_block} @ {anchor_unix}"
    )

    for label, sym_a, sym_b in PROBE_PAIRS:
        pools = fetch_pools(TOKENS[sym_a], TOKENS[sym_b])
        rows: list[dict[str, Any]] = []
        for pool in pools:
            stats = fetch_window_stats(pool["id"], unix_start, unix_end)
            if stats["n_days"] == 0:
                continue  # never traded inside the window — not a candidate
            fee_tier = int(pool["feeTier"])
            rows.append({
                "pool_addr": pool["id"],
                "fee_bps": fee_tier // 100,
                "tick_spacing": TICK_SPACING.get(fee_tier),
                "token0": pool["token0"]["symbol"],
                "token1": pool["token1"]["symbol"],
                "d0": int(pool["token0"]["decimals"]),
                "d1": int(pool["token1"]["decimals"]),
                "created_block": int(pool["createdAtBlockNumber"]),
                "spans_grid": int(pool["createdAtBlockNumber"]) <= int(grid.iloc[0]),
                **stats,
            })
        if rows:
            report_pair(label, rows, grid_days)
        else:
            print(f"\n=== {label} ===\n  no pool traded inside the window")


if __name__ == "__main__":
    main()
