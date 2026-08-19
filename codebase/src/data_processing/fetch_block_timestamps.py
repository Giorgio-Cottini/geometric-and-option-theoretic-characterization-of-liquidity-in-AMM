"""
fetch_block_timestamps.py
-------------------------
Fetches Ethereum block timestamps for every unique block number present in the
pool_states parquets (all pools in data_extraction.config.POOLS) via a single
JSON-RPC endpoint, using HTTP batch requests for efficiency.

Output : codebase/data/block_timestamps.parquet
         columns:
             block_number  int64
             timestamp     datetime64[ns, UTC]

The script is idempotent: if the output already exists, only blocks that are
not yet cached are fetched.  It is therefore safe to re-run after interruption.

All pools share the same grid: download_liquidity_evolution.py reads the block
list back from a stored parquet (config.load_block_grid) rather than resolving it
from `latest`, so the union of block numbers across pools equals one pool's block
list.  Blocks are post-Merge, so JSON-RPC timestamps are exact 12 s slot values.

Usage
-----
    python codebase/src/data_processing/fetch_block_timestamps.py
    python codebase/src/data_processing/fetch_block_timestamps.py --rpc-url https://rpc.ankr.com/eth
    python codebase/src/data_processing/fetch_block_timestamps.py --batch-size 50
"""

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

# ── Path bootstrap ────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # codebase/
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "data_extraction"))

from data_extraction import config as ext_config  # noqa: E402

# ── Constants ─────────────────────────────────────────────────────────────────
_DEFAULT_RPC   = "https://ethereum.publicnode.com"
_DEFAULT_BATCH = 100          # blocks per HTTP batch request
_HTTP_TIMEOUT  = 30           # seconds per request
_HTTP_RETRIES  = 3            # max retry attempts on transient errors
_HTTP_BACKOFF  = 2.0          # base backoff seconds (doubles each retry)
_OUT_PATH      = _REPO_ROOT / "data" / "block_timestamps.parquet"


# ── Block collection ──────────────────────────────────────────────────────────


def _collect_block_numbers() -> np.ndarray:
    """
    Collect all unique block numbers from pool_states parquets across every
    pool declared in data_extraction.config.POOLS.

    All pools share one stored grid, so the union of block numbers equals any
    single pool's block list; the union is taken anyway so a partially-downloaded
    pool cannot silently shrink the timestamp table.

    Returns:
        Sorted int64 array of unique block numbers.
    Raises:
        FileNotFoundError if no pool_states parquets are found.
    """
    raw_root = _REPO_ROOT / "data" / "raw" / "liquidity"
    blocks: set[int] = set()
    for pcfg in ext_config.POOLS.values():
        path = raw_root / pcfg["pair"] / f"{pcfg['file_basename']}_pool_states.parquet"
        if path.exists():
            df = pd.read_parquet(path, columns=["block_number"])
            blocks.update(df["block_number"].tolist())

    if not blocks:
        raise FileNotFoundError(
            "No pool_states parquets found under:\n"
            f"  {raw_root}\n"
            "Run data_extraction/download_liquidity_evolution.py first."
        )
    return np.array(sorted(blocks), dtype=np.int64)


# ── JSON-RPC batch fetch ──────────────────────────────────────────────────────


def _fetch_batch(
    blocks: list[int],
    rpc_url: str,
    session: requests.Session,
) -> dict[int, pd.Timestamp]:
    """
    Fetch block timestamps for one batch via a single JSON-RPC batch request.

    Uses eth_getBlockByNumber with full_transactions=false so only the block
    header (including timestamp) is returned — minimising payload size.

    Args:
        blocks  : list of Ethereum block numbers to query.
        rpc_url : JSON-RPC endpoint URL.
        session : requests.Session for TCP connection reuse.
    Returns:
        dict mapping block_number (int) → pd.Timestamp (UTC).
        Blocks whose result is null (rare reorg / pruned node) are omitted.
    Raises:
        requests.HTTPError on non-2xx responses after all retries.
    """
    payload = [
        {
            "jsonrpc": "2.0",
            "id": block,
            "method": "eth_getBlockByNumber",
            "params": [hex(block), False],  # False → no full transaction list
        }
        for block in blocks
    ]

    last_exc: Exception | None = None
    for attempt in range(_HTTP_RETRIES):
        try:
            resp = session.post(rpc_url, json=payload, timeout=_HTTP_TIMEOUT)
            resp.raise_for_status()
            break
        except Exception as exc:
            last_exc = exc
            if attempt < _HTTP_RETRIES - 1:
                wait = _HTTP_BACKOFF * (2 ** attempt)
                print(f"\n    [retry {attempt + 1}] {exc} — waiting {wait:.1f}s", end="")
                time.sleep(wait)
    else:
        raise RuntimeError(f"All {_HTTP_RETRIES} retries failed: {last_exc}") from last_exc

    result: dict[int, pd.Timestamp] = {}
    for item in resp.json():
        block_num = item.get("id")
        r = item.get("result")
        if r is None or block_num is None:
            continue
        ts_unix = int(r["timestamp"], 16)   # hex string → Unix seconds
        result[int(block_num)] = pd.Timestamp(ts_unix, unit="s", tz="UTC")
    return result


# ── Main pipeline ─────────────────────────────────────────────────────────────


def fetch_block_timestamps(
    rpc_url: str = _DEFAULT_RPC,
    batch_size: int = _DEFAULT_BATCH,
    verbose: bool = True,
) -> None:
    """
    Fetch and persist block → UTC timestamp mapping for all known blocks.

    Reads the existing output parquet (if present) and skips already-cached
    blocks, so the script is safe to re-run after partial completion.

    Args:
        rpc_url    : Ethereum JSON-RPC endpoint URL.  No authentication is
                     required for public nodes such as PublicNode or Ankr.
        batch_size : Number of blocks per HTTP batch request.  Larger values
                     reduce round-trips but increase per-request payload size.
        verbose    : Print progress lines to stdout.
    Writes:
        codebase/data/block_timestamps.parquet
    """
    all_blocks = _collect_block_numbers()
    if verbose:
        print(f"Unique block numbers across all pairs : {len(all_blocks):,}")

    # ── Skip already-cached blocks ────────────────────────────────────────────
    existing: pd.DataFrame | None = None
    if _OUT_PATH.exists():
        existing = pd.read_parquet(_OUT_PATH)
        fetched_set = set(existing["block_number"].tolist())
        need = np.array(
            [b for b in all_blocks if b not in fetched_set], dtype=np.int64
        )
        if verbose:
            print(
                f"Already cached  : {len(fetched_set):,}  "
                f"|  Still needed : {len(need):,}"
            )
    else:
        need = all_blocks

    if len(need) == 0:
        if verbose:
            print("All timestamps already cached — nothing to fetch.")
        return

    # ── Fetch in batches ──────────────────────────────────────────────────────
    n_batches = int(np.ceil(len(need) / batch_size))
    records: list[dict] = []

    with requests.Session() as session:
        session.headers.update({"Content-Type": "application/json"})

        for i in range(n_batches):
            batch = need[i * batch_size : (i + 1) * batch_size].tolist()
            if verbose:
                print(
                    f"  Batch {i + 1:>4}/{n_batches}  "
                    f"blocks {batch[0]}..{batch[-1]}",
                    end=" … ",
                    flush=True,
                )
            fetched = _fetch_batch(batch, rpc_url, session)
            records.extend(
                {"block_number": k, "timestamp": v} for k, v in fetched.items()
            )
            if verbose:
                print(f"{len(fetched)}/{len(batch)} ok")

    # ── Merge with existing cache and persist ─────────────────────────────────
    new_df = pd.DataFrame(records)
    new_df["block_number"] = new_df["block_number"].astype(np.int64)

    combined = (
        pd.concat([existing, new_df], ignore_index=True)
        if existing is not None
        else new_df
    )
    combined = (
        combined
        .drop_duplicates("block_number")
        .sort_values("block_number")
        .reset_index(drop=True)
    )

    _OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(_OUT_PATH, index=False)

    if verbose:
        ts_col = pd.to_datetime(combined["timestamp"], utc=True)
        print(
            f"\nSaved {len(combined):,} block timestamps → {_OUT_PATH}\n"
            f"  Date range : {ts_col.min().date()}  →  {ts_col.max().date()}"
        )


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Fetch Ethereum block timestamps via JSON-RPC and persist to parquet.\n"
            "Output: codebase/data/block_timestamps.parquet"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--rpc-url",
        default=_DEFAULT_RPC,
        help=f"Ethereum JSON-RPC endpoint (default: {_DEFAULT_RPC}).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=_DEFAULT_BATCH,
        help=f"Blocks per HTTP batch request (default: {_DEFAULT_BATCH}).",
    )
    args = parser.parse_args()
    fetch_block_timestamps(rpc_url=args.rpc_url, batch_size=args.batch_size)
