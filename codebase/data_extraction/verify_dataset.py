"""
verify_dataset.py
-----------------
Read-only integrity check over the processed liquidity dataset.

The dataset's defining property is that every pool sits on the *same* block
grid — that is what makes surfaces comparable across pairs and across fee tiers
of one pair. Nothing else in the pipeline asserts it, so this does:

  1. GRID IDENTITY  — each pool's block set is identical to the reference grid,
                      not merely a subset or the same length.
  2. COMPLETENESS   — every pool in config.POOLS has a processed parquet.
  3. NO ORPHANS     — no processed parquet that config.POOLS does not name
                      (catches superseded tiers left behind on disk).
  4. SANITY         — non-empty, finite non-negative liquidity, one curr_tick
                      per block, positive prices with lower <= upper.

Prints a report and exits non-zero if any check fails. Writes nothing.

Usage
-----
    python verify_dataset.py        (from codebase/data_extraction/)
"""

import sys

import numpy as np
import pandas as pd

import config

_COLS = ["block_number", "tick_idx", "price_lower", "price_upper", "liquidity", "curr_tick"]


def _processed_path(pcfg: dict):
    return config.processed_dir(pcfg["pair"]) / f"{pcfg['file_basename']}_ticks.parquet"


def _check_pool(pool_key: str, grid: set[int]) -> list[str]:
    """Return a list of failure strings for one pool — empty means it passed."""
    pcfg = config.POOLS[pool_key]
    path = _processed_path(pcfg)
    if not path.exists():
        return [f"MISSING processed parquet: {path}"]

    df = pd.read_parquet(path, columns=_COLS)
    failures: list[str] = []

    if df.empty:
        return [f"EMPTY: {path}"]

    # ── 1. Grid identity — the property the dataset exists to guarantee ───────
    blocks = set(df["block_number"].unique().tolist())
    if blocks != grid:
        missing, extra = grid - blocks, blocks - grid
        failures.append(
            f"GRID MISMATCH: {len(missing)} blocks missing, {len(extra)} unexpected"
            + (f" (first missing {min(missing)})" if missing else "")
            + (f" (first extra {min(extra)})" if extra else "")
        )

    # ── 4. Sanity ────────────────────────────────────────────────────────────
    liq = df["liquidity"].to_numpy()
    if not np.isfinite(liq).all():
        failures.append(f"NON-FINITE liquidity in {int((~np.isfinite(liq)).sum())} rows")
    if (liq < 0).any():
        failures.append(f"NEGATIVE liquidity in {int((liq < 0).sum())} rows")

    if (df.groupby("block_number")["curr_tick"].nunique() > 1).any():
        failures.append("AMBIGUOUS curr_tick: more than one value within a block")

    if (df["price_lower"] > df["price_upper"]).any():
        failures.append("INVERTED price bounds: price_lower > price_upper")
    if (df["price_lower"] <= 0).any():
        failures.append("NON-POSITIVE price_lower")

    return failures


def _find_orphans() -> list[str]:
    """Processed parquets on disk that no config.POOLS entry claims."""
    expected = {_processed_path(pcfg).resolve() for pcfg in config.POOLS.values()}
    if not config.PROCESSED_ROOT.exists():
        return []
    found = {p.resolve() for p in config.PROCESSED_ROOT.glob("*/*.parquet")}
    return sorted(str(p) for p in found - expected)


def main() -> int:
    grid_list = config.load_block_grid()
    grid = set(grid_list)
    print(
        f"Reference grid : {len(grid_list)} blocks  "
        f"{grid_list[0]}..{grid_list[-1]}\n"
        f"Pools expected : {len(config.POOLS)}\n"
    )

    n_failed = 0
    for pool_key in config.POOLS:
        failures = _check_pool(pool_key, grid)
        if failures:
            n_failed += 1
            print(f"  FAIL  {pool_key}")
            for f in failures:
                print(f"          {f}")
        else:
            print(f"  ok    {pool_key}")

    orphans = _find_orphans()
    if orphans:
        print(f"\n  ORPHANS ({len(orphans)}) — on disk but not in config.POOLS:")
        for o in orphans:
            print(f"          {o}")

    print("\n" + "=" * 60)
    if n_failed or orphans:
        print(f"FAILED  — {n_failed} pool(s) with errors, {len(orphans)} orphan file(s)")
        return 1
    print(f"PASSED  — {len(config.POOLS)} pools, all on the identical {len(grid)}-block grid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
