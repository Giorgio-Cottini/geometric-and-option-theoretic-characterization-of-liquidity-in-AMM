"""
price_impact_study.py
---------------------
Produces the marginal price-impact plots for each (pair, fee-tier) job from the
cleaned historical tick parquets — pointwise transforms of the liquidity
surface L(P, t):

    absolute impact = 2 * P**1.5 / L        relative impact = 2 * P**0.5 / L

Jobs = data_extraction.config.POOLS — the same jobs as liquidity_profile_study.py,
each carrying its (d0, d1, invert) so P is computed in the project's human-unit
convention.

Output : results/price-impact/{abs-impact,rel-impact}/
             profile/{log-moneyness,relative-ticks,absolute-ticks}/{fee}bp_{PAIR}.png
             surface/{log-moneyness,relative-ticks,absolute-ticks}/{fee}bp_{PAIR}.png
             impact-VS-price/{fee}bp_{PAIR}.png

Usage
-----
    python codebase/price_impact_study.py       (from repo root)
    python price_impact_study.py                (from codebase/)
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # non-interactive backend — must precede pyplot import

import pandas as pd

# ── Path bootstrap (so data_extraction.config is importable) ─────────────────
_HERE = Path(__file__).parent  # codebase/
sys.path.insert(0, str(_HERE))

from data_extraction import config as ext_config  # noqa: E402

from src.graphics import (  # noqa: E402
    plot_impact_profile,
    plot_impact_surface,
    plot_impact_heatmap,
)
from src.graphics.config import CFG  # noqa: E402
from src.data_processing.block_timestamps import load_block_timestamps  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────
_PROCESSED_ROOT = _HERE / "data" / "processed" / "liquidity"
_OUT_ROOT       = CFG.impact_out_dir  # results/price-impact

_AXES = ("log-moneyness", "relative-ticks", "absolute-ticks")
# quantity → output subdir. abs-impact/rel-impact name the QUANTITY (kept
# distinct from the 'relative-ticks' AXIS nested below).
_QDIR = {"absolute": "abs-impact", "relative": "rel-impact"}


def _build_jobs() -> list[tuple[str, str, int, Path, int, int, bool]]:
    """
    Assemble (pair, fee_label, tick_spacing, parquet_path, d0, d1, invert) jobs.

    One job per pool in config.POOLS, each carrying that pool's own decimals and
    orientation.  Several tiers of one pair share a folder and are told apart by
    `file_basename`, so the {fee}bp_{PAIR}.png output stem is unique.
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
    jobs = _build_jobs()
    print(f"Jobs    : {[(p, f) for p, f, *_ in jobs]}")

    try:
        block_ts = load_block_timestamps()
        print(f"Block timestamps loaded  ({len(block_ts):,} blocks)")
    except FileNotFoundError as exc:
        print(f"[WARN] {exc}\n  Monthly x-axis labels disabled — time axis will be normalised [0, 1].")
        block_ts = None

    for pair, fee_label, spacing, path, d0, d1, invert in jobs:
        if not path.exists():
            print(f"[SKIP] {path} not found — run clean_parquet.py first.")
            continue

        print(f"\n=== {pair} ({fee_label}) ===")
        print(f"  loading {path}")
        df = pd.read_parquet(
            path, columns=["block_number", "tick_idx", "liquidity", "curr_tick"]
        )
        print(f"  {len(df):,} rows  ·  {df['block_number'].nunique()} blocks")

        # Month-labelled axes need every block in the shared timestamp table.
        # Every pool now sits on the one stored grid, so this should never fire;
        # it stays as a guard because a silent fallback to the normalised axis is
        # far worse than a printed warning.
        job_block_ts = block_ts
        if block_ts is not None:
            blocks = df["block_number"].unique()
            if not pd.Index(blocks).isin(block_ts.index).all():
                print(f"  [WARN] block timestamps missing for {pair} {fee_label} — "
                      "using normalised time axis")
                job_block_ts = None

        stem = f"{fee_label}_{pair}.png"

        for quantity, qdir in _QDIR.items():
            print(f"  -- {quantity} impact --")
            # profile/ — time-collapsed shape, one file per axis.
            for axis in _AXES:
                plot_impact_profile(
                    df, pair, fee_label, spacing,
                    _OUT_ROOT / qdir / "profile" / axis / stem,
                    quantity, d0, d1, invert,
                    axis=axis, block_ts=job_block_ts,
                )
            # surface/ — 3-D surface, one file per axis.
            for axis in _AXES:
                plot_impact_surface(
                    df, pair, fee_label, spacing,
                    _OUT_ROOT / qdir / "surface" / axis / stem,
                    quantity, d0, d1, invert,
                    axis=axis, block_ts=job_block_ts,
                )
            # impact-VS-price/ — top-down heatmap.
            plot_impact_heatmap(
                df, pair, fee_label, spacing,
                _OUT_ROOT / qdir / "impact-VS-price" / stem,
                quantity, d0, d1, invert,
                block_ts=job_block_ts,
            )


if __name__ == "__main__":
    main()
