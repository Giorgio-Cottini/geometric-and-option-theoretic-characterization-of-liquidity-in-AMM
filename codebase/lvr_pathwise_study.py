"""
lvr_pathwise_study.py
----------------------
Cycle 3, R5: what a liquidity provider pays, in LVR variability, for sitting outside the
LVR-neutral family — independent of R1 through R4 (spec section 10).

Jobs = data_extraction.config.POOLS, the same eleven jobs as cev_elasticity_study.py, each
carrying its own (d0, d1, invert).

Output : results/cev-elasticity/lvr/
             lvr_summary.csv       one row per pool: ratio, cv_obs, cv_neutral, totals
             lvr_increments.csv    one row per (pool, block): observed and counterfactual
             lvr_ratio.png
             {fee}bp_{PAIR}_lvr-increments.png

Usage
-----
    python codebase/lvr_pathwise_study.py       (from repo root)
    python lvr_pathwise_study.py                (from codebase/)
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

from src.graphics import plot_lvr_increments, plot_lvr_ratio  # noqa: E402
from src.graphics.config import CFG  # noqa: E402
from src.math_core.impermanent_loss import _reserve_integrals  # noqa: E402
from src.math_core.profile_measure import block_profile  # noqa: E402
from src.math_core.lvr_pathwise import (  # noqa: E402
    counterfactual_constant,
    counterfactual_lvr_series,
    lvr_ratio_and_cv,
    realized_lvr_series,
)

_PROCESSED_ROOT = _HERE / "data" / "processed" / "liquidity"
_OUT = CFG.lvr_out_dir


def _build_jobs() -> list[tuple[str, str, int, Path, int, int, bool]]:
    """
    Assemble (pair, fee_label, tick_spacing, parquet_path, d0, d1, invert) jobs.

    Identical shape and source to cev_elasticity_study.py._build_jobs, copied rather than
    imported: each *_study.py runner in this cycle carries its own copy, matching the existing
    duplication between price_impact_study.py and cev_elasticity_study.py.
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
    summaries = []
    increments = []

    for pair, fee_label, spacing, path, d0, d1, invert in _build_jobs():
        pool = f"{fee_label}_{pair}"
        if not path.exists():
            raise FileNotFoundError(f"{pool}: missing processed parquet at {path}")
        df = pd.read_parquet(path, columns=["block_number", "tick_idx",
                                            "liquidity", "curr_tick"])
        print(f"[{pool}] {df['block_number'].nunique()} blocks", flush=True)

        realized = realized_lvr_series(df, spacing, d0, d1, invert)

        first_block = df[df["block_number"] == df["block_number"].min()]
        bp0 = block_profile(first_block, spacing, d0, d1, invert, x_max=0.5)
        x0, y0 = _reserve_integrals(bp0.q_spot, bp0.q_lower, bp0.q_upper, bp0.ell)
        v_obs_p0 = x0 * bp0.q_spot + y0
        c_tilde = counterfactual_constant(bp0.q_lower[0], bp0.q_upper[-1], bp0.q_spot,
                                          v_obs_p0)

        neutral_incr = counterfactual_lvr_series(realized["q_spot"].to_numpy(), c_tilde)
        cmp_ = lvr_ratio_and_cv(realized["lvr_increment"].to_numpy(), neutral_incr,
                                label=pool)
        cmp_["pool"] = pool
        summaries.append(cmp_)

        pool_series = realized.copy()
        pool_series["lvr_neutral_increment"] = neutral_incr
        pool_series.insert(0, "pool", pool)
        increments.append(pool_series)

        stem = f"{fee_label}_{pair}"
        plot_lvr_increments(pool_series, pair, fee_label,
                            _OUT / f"{stem}_lvr-increments.png")

    summary_df = pd.DataFrame(summaries)[
        ["pool", "lvr_obs_total", "lvr_neutral_total", "ratio", "cv_obs", "cv_neutral"]
    ]
    summary_df.to_csv(_OUT / "lvr_summary.csv", index=False)
    plot_lvr_ratio(summary_df, _OUT / "lvr_ratio.png")

    pd.concat(increments, ignore_index=True).to_csv(_OUT / "lvr_increments.csv", index=False)

    print(f"done -> {_OUT}", flush=True)


if __name__ == "__main__":
    main()
