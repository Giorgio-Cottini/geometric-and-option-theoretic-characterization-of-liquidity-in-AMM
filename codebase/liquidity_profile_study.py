"""
liquidity_profile_study.py
--------------------------
Produces the liquidity-pipeline plots (profile, surface, liquidity-VS-price) for
each (pair, fee-tier) job from the cleaned historical tick parquets.

Jobs = data_extraction.config.POOLS — one job per pool, so several fee tiers of
one pair each get their own figure (distinguished by the {fee}bp_ filename stem).

Input  : data/processed/liquidity/{PAIR}/{file_basename}_ticks.parquet
Output : results/liquidity-pipeline/
             profile/{log-moneyness,relative-ticks,absolute-ticks}/{fee}bp_{PAIR}.png
             surface/{log-moneyness,relative-ticks,absolute-ticks}/{fee}bp_{PAIR}.png
             liquidity-VS-price/{fee}bp_{PAIR}.png

Usage
-----
    python codebase/liquidity_profile_study.py          (from repo root)
    python liquidity_profile_study.py                   (from codebase/)
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
    plot_liquidity_surface,
    plot_liquidity_surface_absolute,
    plot_lvsp,
    plot_liquidity_shape,
)
from src.graphics.config import CFG  # noqa: E402
from src.data_processing.block_timestamps import load_block_timestamps  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────
_PROCESSED_ROOT = _HERE / "data" / "processed" / "liquidity"
_OUT_ROOT       = CFG.liq_out_dir  # results/liquidity-pipeline

# Axis variants shared by the profile/ and surface/ subtrees.
_AXES = ("log-moneyness", "relative-ticks", "absolute-ticks")


def _build_jobs() -> list[tuple[str, str, int, Path, bool]]:
    """
    Assemble the (pair, fee_label, tick_spacing, parquet_path, invert) plot jobs.

    One job per pool in config.POOLS.  Several tiers of one pair share a folder
    and are told apart by `file_basename`, so the {fee}bp_{PAIR}.png output stem
    is unique without any path redesign.

    `invert` rides along because the log-moneyness axis label depends on the
    pool's token ordering — it does not affect a single plotted value.
    """
    jobs: list[tuple[str, str, int, Path, bool]] = []
    for pcfg in ext_config.POOLS.values():
        pair = pcfg["pair"]
        jobs.append((
            pair,
            f"{pcfg['fee_bps']}bp",
            pcfg["tick_spacing"],
            _PROCESSED_ROOT / pair / f"{pcfg['file_basename']}_ticks.parquet",
            pcfg["invert_price"],
        ))
    return jobs


def main() -> None:
    jobs = _build_jobs()
    print(f"Jobs    : {[(p, f) for p, f, *_ in jobs]}")

    # ── Load block timestamps once (shared across all jobs and plots) ─────────
    try:
        block_ts = load_block_timestamps()
        print(f"Block timestamps loaded  ({len(block_ts):,} blocks)")
    except FileNotFoundError as exc:
        print(f"[WARN] {exc}\n  Monthly x-axis labels disabled — time axis will be normalised [0, 1].")
        block_ts = None

    for pair, fee_label, spacing, path, invert in jobs:
        if not path.exists():
            print(f"[SKIP] {path} not found — run clean_parquet.py first.")
            continue

        print(f"\n=== {pair} ({fee_label}) ===")
        print(f"  loading {path}")
        df = pd.read_parquet(
            path,
            columns=["block_number", "tick_idx", "liquidity", "curr_tick"],
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

        # profile/ — time-averaged 2-D shape, one file per axis.
        for axis in _AXES:
            plot_liquidity_shape(
                df, pair, fee_label, spacing,
                _OUT_ROOT / "profile" / axis / stem,
                invert,
                axis=axis, block_ts=job_block_ts,
            )

        # surface/ — 3-D log-liquidity surface, one file per axis.
        plot_liquidity_surface(
            df, pair, fee_label, spacing,
            _OUT_ROOT / "surface" / "log-moneyness" / stem,
            invert,
            use_log_moneyness=True, block_ts=job_block_ts,
        )
        plot_liquidity_surface(
            df, pair, fee_label, spacing,
            _OUT_ROOT / "surface" / "relative-ticks" / stem,
            invert,
            use_log_moneyness=False, block_ts=job_block_ts,
        )
        plot_liquidity_surface_absolute(
            df, pair, fee_label, spacing,
            _OUT_ROOT / "surface" / "absolute-ticks" / stem,
            block_ts=job_block_ts,
        )

        # liquidity-VS-price/ — top-down LvsP heatmap.
        plot_lvsp(
            df, pair, fee_label, spacing,
            _OUT_ROOT / "liquidity-VS-price" / stem,
            block_ts=job_block_ts,
        )


if __name__ == "__main__":
    main()
