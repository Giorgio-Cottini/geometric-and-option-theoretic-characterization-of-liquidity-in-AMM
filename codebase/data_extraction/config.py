"""
config.py
---------
Configuration for the multi-pool liquidity evolution downloader.

Single source of truth for:
  - Per-pool address, fee tier, token decimals, and price-inversion flag
  - The shared block grid, read from the existing download (never recomputed)
  - Output directory layout: data/raw/liquidity/{PAIR}/{fee}bp_{ticks|pool_states}.parquet

Keyed per POOL, not per pair
----------------------------
A token pair trades across several Uniswap v3 fee tiers, and the tiers are not
interchangeable: within one pair the 1bp tier can run ~4000x turnover on ~1% of
the TVL while the 30bp tier runs ~28x turnover on ~43% of it. Both are needed.
Entries are therefore keyed "{PAIR}@{fee}bp"; several tiers of one pair share a
`data/raw/liquidity/{PAIR}/` folder, distinguished by `file_basename`.

Pair label convention: BASE_QUOTE matching the user-facing price direction, not
the on-chain token0/token1 ordering. The on-chain ordering is captured by
token0_decimals / token1_decimals and by `invert_price`.

Pool selection (measured, not assumed)
--------------------------------------
Addresses, decimals, token ordering and `volume_share_pct` come from
`discover_pools.py` (run 2026-07-21), which aggregated `poolDayDatas` over the
exact block grid below. Tiers below ~1% of both pair volume and pair TVL were
dropped as vestigial; wherever the cut falls the drop-off is an order of
magnitude or more.
"""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# ── API ───────────────────────────────────────────────────────────────────────
API_KEY = os.environ["GRAPH_API_KEY"]  # The Graph API key from env
SUBGRAPH_ID = (
    "5zvR82QoaXYFyDEKLZ9t6v9adgnptxYpKpSbxtgVENFV"  # Uniswap v3 subgraph on The Graph
)
ENDPOINT = f"https://gateway.thegraph.com/api/{API_KEY}/subgraphs/id/{SUBGRAPH_ID}"

# ── Repo anchor ───────────────────────────────────────────────────────────────
_CODEBASE = Path(__file__).resolve().parent.parent  # codebase/

# ── Fee tier → tick spacing ───────────────────────────────────────────────────
# Fixed by the Uniswap v3 factory. Derived rather than hand-written: the old
# hardcoded `tick_spacing=10` was correct only because every pool was 5bp, and
# would be silently wrong for the 1bp and 30bp tiers added here.
TICK_SPACING_BY_FEE_BPS: dict[int, int] = {1: 1, 5: 10, 30: 60, 100: 200}

# ── Pools ─────────────────────────────────────────────────────────────────────
#   pair              : pair label — also the output folder name
#   pool_addr         : lowercase pool address (no checksum)
#   fee_bps           : fee tier in basis points
#   token0_decimals   : ERC-20 decimals of token0 (lower hex address)
#   token1_decimals   : ERC-20 decimals of token1 (higher hex address)
#   invert_price      : True  → output price = token0 per token1
#                               (token0 is the natural quote, e.g. USDC in WETH/USDC)
#                       False → output price = token1 per token0
#   volume_share_pct  : share of the pair's traded volume over the block grid
#                       below. Measured; recorded as provenance for why each
#                       tier was kept, not consumed by any code path.
#
# `tick_spacing` and `file_basename` are derived below — do not add them here.
POOLS: dict[str, dict] = {
    # ── WETH/USDC — three live tiers; 100bp dropped (0.0% vol / 1.5% TVL) ─────
    "WETH_USDC@5bp": dict(
        pair="WETH_USDC",
        pool_addr="0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
        fee_bps=5,
        token0_decimals=6,   # USDC
        token1_decimals=18,  # WETH
        invert_price=True,   # output: USDC per WETH
        volume_share_pct=69.2,
    ),
    "WETH_USDC@1bp": dict(
        pair="WETH_USDC",
        pool_addr="0xe0554a476a092703abdb3ef35c80e0d76d32939f",
        fee_bps=1,
        token0_decimals=6,
        token1_decimals=18,
        invert_price=True,
        volume_share_pct=24.1,
    ),
    "WETH_USDC@30bp": dict(
        pair="WETH_USDC",
        pool_addr="0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8",
        fee_bps=30,
        token0_decimals=6,
        token1_decimals=18,
        invert_price=True,
        volume_share_pct=6.6,
    ),

    # ── WETH/USDT — three live tiers, the sharpest volume/TVL inversion ───────
    "WETH_USDT@1bp": dict(
        pair="WETH_USDT",
        pool_addr="0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b",
        fee_bps=1,
        token0_decimals=18,  # WETH
        token1_decimals=6,   # USDT
        invert_price=False,  # output: USDT per WETH
        volume_share_pct=49.0,
    ),
    "WETH_USDT@5bp": dict(
        pair="WETH_USDT",
        pool_addr="0x11b815efb8f581194ae79006d24e0d814b7697f6",
        fee_bps=5,
        token0_decimals=18,
        token1_decimals=6,
        invert_price=False,
        volume_share_pct=29.5,
    ),
    "WETH_USDT@30bp": dict(
        pair="WETH_USDT",
        pool_addr="0x4e68ccd3e89f51c3074ca5072bbac773960dfa36",
        fee_bps=30,
        token0_decimals=18,
        token1_decimals=6,
        invert_price=False,
        volume_share_pct=21.5,
    ),

    # ── WBTC/WETH — two live tiers; 1bp dropped (0.6% vol / 0.1% TVL) ─────────
    "WBTC_WETH@5bp": dict(
        pair="WBTC_WETH",
        pool_addr="0x4585fe77225b41b697c938b018e2ac67ac5a20c0",
        fee_bps=5,
        token0_decimals=8,   # WBTC
        token1_decimals=18,  # WETH
        invert_price=False,  # output: WETH per WBTC
        volume_share_pct=84.1,
    ),
    "WBTC_WETH@30bp": dict(
        pair="WBTC_WETH",
        pool_addr="0xcbcdf9626bc03e24f779434178a73a0b4bad62ed",
        fee_bps=30,
        token0_decimals=8,
        token1_decimals=18,
        invert_price=False,
        volume_share_pct=15.4,
    ),

    # ── WBTC/USDT — two live tiers ───────────────────────────────────────────
    "WBTC_USDT@5bp": dict(
        pair="WBTC_USDT",
        pool_addr="0x56534741cd8b152df6d48adf7ac51f75169a83b2",
        fee_bps=5,
        token0_decimals=8,   # WBTC
        token1_decimals=6,   # USDT
        invert_price=False,  # output: USDT per WBTC
        volume_share_pct=71.1,
    ),
    "WBTC_USDT@30bp": dict(
        pair="WBTC_USDT",
        pool_addr="0x9db9e0e53058c89e5b94e29621a205198648425b",
        fee_bps=30,
        token0_decimals=8,
        token1_decimals=6,
        invert_price=False,
        volume_share_pct=28.7,
    ),

    # ── USDC/USDT — genuinely single-tier. The 5bp pool previously configured
    #    here carries 0.6% of the pair's volume; 1bp carries 99.4%. ───────────
    "USDC_USDT@1bp": dict(
        pair="USDC_USDT",
        pool_addr="0x3416cf6c708da44db2624d63ea0aaef7113527c6",
        fee_bps=1,
        token0_decimals=6,   # USDC
        token1_decimals=6,   # USDT
        invert_price=False,  # output: USDT per USDC
        volume_share_pct=99.4,
    ),
}

# ── Derived per-pool fields ───────────────────────────────────────────────────
for _cfg in POOLS.values():
    _cfg["tick_spacing"] = TICK_SPACING_BY_FEE_BPS[_cfg["fee_bps"]]
    _cfg["file_basename"] = f"{_cfg['fee_bps']}bp"


# There is deliberately no per-pair view here. An earlier `PAIRS` shim exposed
# each pair's highest-volume tier so the study runners could keep iterating one
# pool per pair; every consumer now reads POOLS directly, and a derived argmax
# that silently re-points an analysis when volume shares shift is worse than no
# shim at all. Iterate POOLS and key on cfg["pair"].

# ── Block grid ────────────────────────────────────────────────────────────────
# The grid is a stored artifact, not a runtime derivation. Every pool must land
# on the *same* blocks for the surfaces to be comparable across pairs and tiers,
# so it is read back from the original download rather than re-resolved from
# `latest` (which would drift with every run).
BLOCK_SPACING: int = 2400  # blocks between snapshots (~8 h) — for grid extension
GRID_REF: Path = (
    _CODEBASE / "data" / "raw" / "liquidity" / "WETH_USDC" / "5bp_pool_states.parquet"
)


def load_block_grid() -> list[int]:
    """
    The shared block grid, recovered from the existing download.

    Returns 1641 ascending block numbers spanning 21102263..25038263 (~8 h
    spacing, 2024-11-06 .. 2026-05-07). Note this is three short of the 1644 the
    old N_SNAPSHOTS formula produced — the grid on disk is authoritative.
    """
    if not GRID_REF.exists():
        raise FileNotFoundError(
            f"Block grid reference not found: {GRID_REF}\n"
            "The grid is read from the original download; it cannot be recomputed "
            "without breaking alignment with the existing data."
        )
    blocks = pd.read_parquet(GRID_REF, columns=["block_number"])["block_number"]
    return sorted(blocks.unique().tolist())


# ── Output ────────────────────────────────────────────────────────────────────
RAW_ROOT: Path = _CODEBASE / "data" / "raw" / "liquidity"
PROCESSED_ROOT: Path = _CODEBASE / "data" / "processed" / "liquidity"


def out_dir(pair: str) -> Path:
    """Raw output directory for a given pair label (e.g. 'WETH_USDC')."""
    return RAW_ROOT / pair


def processed_dir(pair: str) -> Path:
    """Processed output directory for a given pair label."""
    return PROCESSED_ROOT / pair


# ── HTTP ──────────────────────────────────────────────────────────────────────
HTTP_RETRIES = 5       # Max retry attempts per GraphQL request
HTTP_BACKOFF = 2.0     # Base backoff seconds; actual wait = backoff * 2^attempt
HTTP_TIMEOUT = 30      # Request timeout in seconds
TICK_PAGE_SLEEP = 0.2  # Polite delay between paginated tick requests (seconds)

# ── Write behaviour ───────────────────────────────────────────────────────────
FLUSH_EVERY = 50  # Flush accumulated frames to parquet every N snapshots
