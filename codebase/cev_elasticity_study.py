"""
cev_elasticity_study.py
-----------------------
Cycle 3, R1: the shape diagnostic.  Answers one question — does the observed
liquidity profile behave like the RTW26 Example 3.3 power law over any
contiguous band of price — and produces the coverage table that fixes the
headline half-width for R2 through R5.

Jobs = data_extraction.config.POOLS, the same eleven jobs as
price_impact_study.py, each carrying its own (d0, d1, invert) so that the price
is in the project's human-unit convention.

Output : results/cev-elasticity/diagnostic/
             band_sweep.csv          one row per (pool, block, w, branch)
             coverage.csv            one row per (pool, w, branch)
             full_support_fit.csv    one row per (pool, block)
             headline_w.csv          the C7 verdict and the qualifying pools
             local_slope.csv         one row per (pool, x_centre)
             {fee}bp_{PAIR}_band-dependence.png
             {fee}bp_{PAIR}_local-slope.png

Usage
-----
    python codebase/cev_elasticity_study.py       (from repo root)
    python cev_elasticity_study.py                (from codebase/)
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # non-interactive backend — must precede pyplot import

import numpy as np
import pandas as pd

# ── Path bootstrap (so data_extraction.config is importable) ─────────────────
_HERE = Path(__file__).parent  # codebase/
sys.path.insert(0, str(_HERE))

from data_extraction import config as ext_config  # noqa: E402

from src.graphics import plot_band_dependence, plot_local_slope  # noqa: E402
from src.graphics.config import CFG  # noqa: E402
from src.math_core.profile_measure import block_profile  # noqa: E402
from src.math_core.cev_elasticity import (  # noqa: E402
    W_GRID,
    coverage_table,
    full_support_fit,
    headline_w,
    local_slope_profile,
    sweep_pool,
)

_PROCESSED_ROOT = _HERE / "data" / "processed" / "liquidity"
_OUT = CFG.cev_out_dir / "diagnostic"

# Window centres for the local slope profile.  +/- 0.5 matches the widest band
# in W_GRID; the 0.01 step gives 101 centres, and the +/- 0.02 half-window is
# the narrowest band in W_GRID, so the two diagnostics share a scale.
_X_CENTRES = np.round(np.arange(-0.50, 0.5001, 0.01), 4)


def _build_jobs() -> list[tuple[str, str, int, Path, int, int, bool]]:
    """
    Assemble (pair, fee_label, tick_spacing, parquet_path, d0, d1, invert) jobs.

    Copied from graph:price_impact_study_build_jobs.  One job per pool in
    config.POOLS, each carrying that pool's own decimals and orientation, so
    that no call site can inherit the wrong frame (C3).
    """
    jobs: list[tuple[str, str, int, Path, int, int, bool]] = []
    for pcfg in ext_config.POOLS.values():
        pair = pcfg["pair"]
        jobs.append((
            pair,
            f"{pcfg['fee_bps']}bp",
            pcfg["tick_spacing"],
            _PROCESSED_ROOT / pair / f"{pcfg['file_basename']}_ticks.parquet",
            pcfg["token0_decimals"],
            pcfg["token1_decimals"],
            pcfg["invert_price"],
        ))
    return jobs


def main() -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    sweeps: list[pd.DataFrame] = []
    fulls: list[pd.DataFrame] = []
    locals_: list[pd.DataFrame] = []

    for pair, fee_label, spacing, path, d0, d1, invert in _build_jobs():
        pool = f"{fee_label}_{pair}"
        if not path.exists():
            raise FileNotFoundError(f"{pool}: missing processed parquet at {path}")
        df = pd.read_parquet(path, columns=["block_number", "tick_idx",
                                            "liquidity", "curr_tick"])
        print(f"[{pool}] {df['block_number'].nunique()} blocks", flush=True)

        sweep = sweep_pool(df, spacing, d0, d1, invert)
        sweep.insert(0, "pool", pool)
        skipped = sweep.attrs.get("skipped_blocks", 0)
        if skipped:
            print(f"[{pool}] skipped {skipped} blocks with < 2 surviving ticks",
                  flush=True)
        sweeps.append(sweep)

        rows = []
        for block, grp in df.groupby("block_number", sort=True):
            try:
                bp = block_profile(grp, spacing, d0, d1, invert, max(W_GRID))
            except ValueError:
                continue
            rows.append({"pool": pool, "block_number": int(block),
                         **full_support_fit(bp)})
        fulls.append(pd.DataFrame(rows))

        prof = local_slope_profile(df, spacing, d0, d1, invert, _X_CENTRES)
        prof.insert(0, "pool", pool)
        locals_.append(prof)

        stem = f"{fee_label}_{pair}"
        plot_band_dependence(sweep, pair, fee_label,
                             _OUT / f"{stem}_band-dependence.png")
        plot_local_slope(prof, pair, fee_label, _OUT / f"{stem}_local-slope.png")

    sweep_all = pd.concat(sweeps, ignore_index=True)
    sweep_all.to_csv(_OUT / "band_sweep.csv", index=False)

    cov = coverage_table(sweep_all)
    cov.to_csv(_OUT / "coverage.csv", index=False)

    pd.concat(fulls, ignore_index=True).to_csv(_OUT / "full_support_fit.csv", index=False)
    pd.concat(locals_, ignore_index=True).to_csv(_OUT / "local_slope.csv", index=False)

    w, qual = headline_w(cov)
    qual = qual.copy()
    qual["headline_w"] = w if w is not None else float("nan")
    qual.to_csv(_OUT / "headline_w.csv", index=False)
    if w is None:
        print("C7: no half-width in the grid qualifies for all pools. "
              "Per-w qualifying sets are in headline_w.csv.", flush=True)
    else:
        print(f"C7: headline w = {w}", flush=True)

    print(f"done -> {_OUT}", flush=True)


if __name__ == "__main__":
    main()
