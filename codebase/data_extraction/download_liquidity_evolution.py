"""
download_liquidity_evolution.py
-------------------------------
Multi-pool, multi-threaded liquidity evolution downloader.

For every selected pool in config.POOLS, fetches:
    1. Per-block initialized ticks (paginated full coverage)
    2. Per-block pool slot0 state (curr_tick, curr_liquidity)

across the shared block grid returned by config.load_block_grid() — read back
from the original download rather than re-resolved from `latest`. That is what
keeps every pool, including ones added long after the first run, on identical
blocks: alignment is a property of the stored grid, not of fetch order.

Parallelism is at pool level (one thread per pool). Tick pagination within each
pool remains sequential (cursor-based). A shared threading.Lock ensures each
progress line is written atomically.

Output layout (several fee tiers share one pair folder):
    data/raw/liquidity/{PAIR}/{fee}bp_ticks.parquet
    data/raw/liquidity/{PAIR}/{fee}bp_pool_states.parquet

Pools whose output already exists are skipped unless --force, so an interrupted
run resumes cheaply and already-downloaded pools are never refetched.

Usage
-----
    python download_liquidity_evolution.py                          # all pools
    python download_liquidity_evolution.py --pools USDC_USDT@1bp
    python download_liquidity_evolution.py --pools WETH_USDC@5bp --force
"""

import argparse
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import requests

import config

# Shared lock — every print call acquires this so multi-threaded lines are atomic.
_print_lock = threading.Lock()


def _print(*args, **kwargs) -> None:
    with _print_lock:
        print(*args, **kwargs)


# ── GraphQL helpers ───────────────────────────────────────────────────────────

def graphql(query: str) -> dict:
    for attempt in range(config.HTTP_RETRIES):
        try:
            r = requests.post(
                config.ENDPOINT,
                json={"query": query},
                timeout=config.HTTP_TIMEOUT,
            )
            r.raise_for_status()
            payload = r.json()
            if "errors" in payload:
                raise ValueError(payload["errors"])
            return payload["data"]
        except Exception as e:
            if attempt == config.HTTP_RETRIES - 1:
                raise
            wait = config.HTTP_BACKOFF * (2 ** attempt)
            _print(f"  [retry {attempt+1}] {e} — waiting {wait:.1f}s")
            time.sleep(wait)


def fetch_latest_block() -> int:
    return graphql("{ _meta { block { number } } }")["_meta"]["block"]["number"]


def fetch_ticks(pool_addr: str, block: int) -> list[dict]:
    ticks: list[dict] = []
    cursor = -887272
    while True:
        q = f"""{{
          ticks(
            first: 1000, block: {{number: {block}}},
            where: {{pool: "{pool_addr}", tickIdx_gt: {cursor}}},
            orderBy: tickIdx, orderDirection: asc
          ) {{ tickIdx liquidityNet liquidityGross }}
        }}"""
        page = graphql(q)["ticks"]
        ticks.extend(page)
        if len(page) < 1000:
            break
        cursor = page[-1]["tickIdx"]
        time.sleep(config.TICK_PAGE_SLEEP)
    return ticks


def fetch_pool_state(pool_addr: str, block: int) -> dict | None:
    q = f'{{ pool(id: "{pool_addr}", block: {{number: {block}}}) {{ tick liquidity }} }}'
    return graphql(q).get("pool")


# ── File I/O ──────────────────────────────────────────────────────────────────

def save(path: Path, df: pd.DataFrame) -> None:
    tmp = path.with_suffix(".tmp.parquet")
    df.to_parquet(tmp, index=False)
    tmp.replace(path)


# ── Per-pool download routines ────────────────────────────────────────────────
# `label` is the pool key ("WETH_USDC@1bp") and is used for logging only.

def _download_ticks(label: str, pcfg: dict, blocks: list[int], out_dir: Path) -> None:
    path = out_dir / f"{pcfg['file_basename']}_ticks.parquet"
    pool_addr = pcfg["pool_addr"]
    frames: list[pd.DataFrame] = []
    n_new = 0

    # Resume: keep whatever a previous run flushed and refetch only the gap.
    done = _blocks_present(path)
    if done:
        frames.append(pd.read_parquet(path))
        _print(f"[{label}|ticks] resuming — {len(done)} blocks already stored")

    for i, block in enumerate(blocks):
        if block in done:
            continue
        ticks = fetch_ticks(pool_addr, block)
        _print(f"[{label}|ticks] {i+1}/{len(blocks)}  block={block} → {len(ticks)} ticks")
        if not ticks:
            continue
        n_new += 1
        df = pd.DataFrame(ticks).rename(columns={
            "tickIdx": "tick_idx",
            "liquidityNet": "liquidity_net",
            "liquidityGross": "liquidity_gross",
        })
        df["block_number"] = block
        df = df.astype({"tick_idx": "int64", "block_number": "int64"})
        df["liquidity_net"] = df["liquidity_net"].astype(str)
        df["liquidity_gross"] = df["liquidity_gross"].astype(str)
        frames.append(df[["block_number", "tick_idx", "liquidity_net", "liquidity_gross"]])

        if n_new % config.FLUSH_EVERY == 0:
            save(path, pd.concat(frames, ignore_index=True).sort_values(["block_number", "tick_idx"]))
            _print(f"  [{label}|ticks] flushed (+{n_new} new blocks)")

    if frames:
        save(path, pd.concat(frames, ignore_index=True).sort_values(["block_number", "tick_idx"]))
    _print(f"[{label}|ticks] done → {path}")


def _download_pool_states(label: str, pcfg: dict, blocks: list[int], out_dir: Path) -> None:
    path = out_dir / f"{pcfg['file_basename']}_pool_states.parquet"
    pool_addr = pcfg["pool_addr"]
    rows: list[dict] = []
    n_new = 0

    # Resume: keep whatever a previous run flushed and refetch only the gap.
    done = _blocks_present(path)
    if done:
        rows = pd.read_parquet(path).to_dict("records")
        _print(f"[{label}|state] resuming — {len(done)} blocks already stored")

    for i, block in enumerate(blocks):
        if block in done:
            continue
        state = fetch_pool_state(pool_addr, block)
        if state is None:
            _print(f"[{label}|state] {i+1}/{len(blocks)}  block={block} → null")
        else:
            _print(f"[{label}|state] {i+1}/{len(blocks)}  block={block} → tick={state['tick']}")
            rows.append({
                "block_number": block,
                "curr_tick": int(state["tick"]),
                "curr_liquidity": str(state["liquidity"]),
            })
            n_new += 1
        time.sleep(config.TICK_PAGE_SLEEP)

        if n_new % config.FLUSH_EVERY == 0 and rows:
            save(
                path,
                pd.DataFrame(rows)
                  .astype({"block_number": "int64", "curr_tick": "int64"})
                  .sort_values("block_number"),
            )
            _print(f"  [{label}|state] flushed (+{n_new} new states)")

    if rows:
        save(
            path,
            pd.DataFrame(rows)
              .astype({"block_number": "int64", "curr_tick": "int64"})
              .sort_values("block_number"),
        )
    _print(f"[{label}|state] done → {path}")


def _blocks_present(path: Path) -> set[int]:
    """Blocks already stored in an output parquet — empty if it does not exist."""
    if not path.exists():
        return set()
    return set(pd.read_parquet(path, columns=["block_number"])["block_number"].tolist())


def _is_downloaded(pcfg: dict, grid: set[int]) -> bool:
    """
    True only when both parquets cover the WHOLE grid.

    Existence is not sufficient: the downloader flushes every FLUSH_EVERY
    snapshots, so an interrupted run leaves valid-but-truncated parquets. Testing
    existence alone would skip those on the next run and yield a silently
    incomplete dataset.
    """
    out = config.out_dir(pcfg["pair"])
    basename = pcfg["file_basename"]
    return all(
        grid <= _blocks_present(out / f"{basename}_{suffix}.parquet")
        for suffix in ("ticks", "pool_states")
    )


def _download_pool(label: str, pcfg: dict, blocks: list[int]) -> None:
    """Entry point for each thread: ticks then pool_states for one pool."""
    out = config.out_dir(pcfg["pair"])
    out.mkdir(parents=True, exist_ok=True)
    _print(f"\n=== {label} (pool {pcfg['pool_addr']}, spacing {pcfg['tick_spacing']}) ===")
    _download_ticks(label, pcfg, blocks, out)
    _download_pool_states(label, pcfg, blocks, out)


# ── Main ──────────────────────────────────────────────────────────────────────

def main(pool_keys: list[str], force: bool = False) -> None:
    # ── Load the shared grid — never re-resolve it from `latest` ──────────────
    # Re-deriving the grid would silently misalign every new pool against the
    # existing data, which is the whole property this dataset depends on.
    blocks = config.load_block_grid()

    grid = set(blocks)
    if not force:
        skipped = [k for k in pool_keys if _is_downloaded(config.POOLS[k], grid)]
        pool_keys = [k for k in pool_keys if k not in skipped]
        if skipped:
            print(f"Already downloaded (skipped): {skipped}")
    if not pool_keys:
        print("Nothing to download — every selected pool is already present.")
        return

    n_workers = min(len(pool_keys), 4)
    print(
        f"Pools    : {pool_keys}\n"
        f"Workers  : {n_workers}\n"
        f"Snapshots: {len(blocks)}  ({blocks[0]}..{blocks[-1]})"
    )

    # ── Dispatch one future per pool ──────────────────────────────────────────
    succeeded: list[str] = []
    failed: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=n_workers) as pool:
        futures = {
            pool.submit(_download_pool, key, config.POOLS[key], blocks): key
            for key in pool_keys
        }
        for future in as_completed(futures):
            key = futures[future]
            try:
                future.result()
                succeeded.append(key)
            except Exception as exc:
                failed[key] = str(exc)
                _print(f"\n[{key}] FAILED: {exc}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"DONE  ✓ {len(succeeded)} succeeded  ✗ {len(failed)} failed")
    if succeeded:
        print(f"  OK  : {succeeded}")
    if failed:
        print(f"  ERR : {list(failed.keys())}")
        for key, msg in failed.items():
            print(f"    [{key}] {msg}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download multi-pool Uniswap v3 liquidity evolution parquets."
    )
    parser.add_argument(
        "--pools",
        nargs="+",
        choices=list(config.POOLS.keys()),
        default=None,
        metavar="POOL",
        help=(
            "Pools to fetch (space-separated), e.g. USDC_USDT@1bp. "
            f"Choices: {list(config.POOLS.keys())}. "
            "Default: all pools."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download pools whose output parquets already exist.",
    )
    args = parser.parse_args()
    selected = args.pools if args.pools is not None else list(config.POOLS.keys())
    main(selected, force=args.force)
