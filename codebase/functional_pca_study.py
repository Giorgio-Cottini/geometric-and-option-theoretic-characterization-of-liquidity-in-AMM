"""
functional_pca_study.py
------------------------
Cycle 4 (corrected): functional PCA of the log-liquidity surface, rolling-window replication
of Fig. 4 (bottom), Risk/Tung/Wang, "Dynamics of Liquidity Surfaces in Uniswap V3."

Method (full derivation in src.math_core.functional_pca):
    Per pool, build the rank-standardized (Appendix B, M=201) qualifying-block log-liquidity
    matrix once. Per window length T in T_VALUES, slide a T-row window (step=10, full windows
    only) over the qualifying blocks and run functional PCA on each window, producing the
    cumulative proportion of variance explained (CPVE) at ranks K=1..8. Two PNGs per (pool, T),
    both vs. rolling-window start date: per-component PVE (stacked), and a two-row spectral-
    diagnostics figure -- effective rank (continuous companion to "K needed for X% CPVE") over
    total variance (its level-shift companion -- catches a period boundary where raw variance
    moves but spectral shape doesn't), sharing the x-axis.

    Date-range alignment across a pool's own T variants: rolling_cpve always starts its slide
    at qualifying-block index 0 with the same step regardless of T, so window k starts at the
    same qualifying block for every T -- each T's window list is an exact prefix of any
    shorter-T list. _align_windows_across_T exploits this to crop every T-curve for a pool down
    to the window count of that pool's shortest produced T, giving an exact (start, end) match
    across the pool's T=300/400/500 plots with no recomputation. Applied unconditionally, even
    when it leaves a thin pool with very few plotted points.

Jobs = data_extraction.config.POOLS, the same 11 (pair, fee-tier) jobs every other runner in
this pipeline iterates. 11 pools x 3 T values = 33 (pool, T) combinations per run; not every
combination produces a plot -- a pool is skipped for a given T if it has fewer than T
qualifying blocks (see coverage.csv).

Input  : data/processed/liquidity/{PAIR}/{file_basename}_ticks.parquet
         data/block_timestamps.parquet (block_number -> UTC timestamp; fatal if missing, since
         the x-axis of every plot this module produces is calendar-date only)
Output : results/liquidity-pipeline/functional-pca/
             {fee}bp/{PAIR}_{T}_pve.png       -- per-component PVE, stacked
             {fee}bp/{PAIR}_{T}_spectral.png  -- effective rank (top) / total variance
                                                  (bottom), two rows, shared x-axis
                 two per produced (pool, T) combination, date-range aligned across that
                 pool's own T variants
             coverage.csv              -- one row per (pool, T) combination, produced or
                                          skipped; produced rows carry both n_windows (before
                                          the alignment crop) and n_windows_aligned (after)

Usage
-----
    python codebase/functional_pca_study.py          (from repo root)
    python functional_pca_study.py                   (from codebase/)
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # non-interactive backend -- must precede pyplot import

import numpy as np
import pandas as pd

# ── Path bootstrap (so data_extraction.config is importable) ─────────────────
_HERE = Path(__file__).parent  # codebase/
sys.path.insert(0, str(_HERE))

from data_extraction import config as ext_config  # noqa: E402

from src.math_core.functional_pca import build_qualifying_matrix, rolling_cpve  # noqa: E402
from src.graphics import (  # noqa: E402
    plot_pve_stacked_vs_window_start,
    plot_spectral_diagnostics_vs_window_start,
)
from src.graphics.config import CFG  # noqa: E402
from src.data_processing.block_timestamps import load_block_timestamps  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────
_PROCESSED_ROOT = _HERE / "data" / "processed" / "liquidity"
_OUT = CFG.fpca_out_dir

# ── Sweep parameters (locked in by the plan) ──────────────────────────────────
T_VALUES: tuple[int, ...] = (300, 400, 500)
STEP: int = 10
# Floor below which a pool's aligned window count is flagged "produced-thin" in coverage.csv
# rather than blended in silently with healthy "produced" pools. 10 was chosen against the live
# dataset: the thinnest currently-produced pool is WBTC_USDT@5bp at 2 aligned windows, the next-
# thinnest healthy pool is WBTC_WETH@5bp at 21 -- 10 catches the former without reclassifying the
# latter. Tune if a future coverage.csv shows false positives/negatives.
MIN_ALIGNED_WINDOWS: int = 10


def _build_jobs() -> list[tuple[str, str, Path]]:
    """
    Assemble the (pair, fee_label, parquet_path) jobs.

    One job per pool in config.POOLS -- no tick_spacing: the rank-standardized grid construction
    (build_qualifying_matrix) selects ticks by rank around each block's own anchor, not by a
    tick-spacing-derived radius, so this runner has no use for it (unlike the old uniform-grid
    version).
    """
    jobs: list[tuple[str, str, Path]] = []
    for pcfg in ext_config.POOLS.values():
        pair = pcfg["pair"]
        jobs.append((
            pair,
            f"{pcfg['fee_bps']}bp",
            _PROCESSED_ROOT / pair / f"{pcfg['file_basename']}_ticks.parquet",
        ))
    return jobs


def _align_windows_across_T(T_windows: dict) -> dict:
    """
    Crop every T variant's window list to the same window count, giving an exact common
    (start, end) date range across a pool's T-variant plots with no recomputation.

    Relies on rolling_cpve always starting its slide at qualifying-block index 0 with the same
    step regardless of window_T (src/math_core/functional_pca.py, rolling_cpve) -- window k
    therefore starts at the same qualifying block for every T, so every T's window list is an
    exact prefix of the window list produced by any smaller T. Truncating every list to the
    shortest one (produced by this pool's largest T) aligns all of them exactly.

    Args:
        T_windows: {T: [WindowResult, ...]} for one pool, one entry per T that produced at
                   least one window. Not mutated.
    Returns:
        {T: [WindowResult, ...]} with every list truncated to the same length -- the minimum
        length across the input. A single-entry input is returned unchanged (nothing to align
        against).
    """
    aligned_n = min(len(windows) for windows in T_windows.values())
    return {T: windows[:aligned_n] for T, windows in T_windows.items()}


def main() -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    jobs = _build_jobs()
    print(f"Jobs    : {[(p, f) for p, f, _ in jobs]}")

    # No fallback: this module's plots are calendar-date-only on the x-axis, so a missing
    # timestamp table must halt the whole run loudly rather than silently produce nothing (or
    # worse, a plot with a wrong axis).
    try:
        block_ts = load_block_timestamps()
    except FileNotFoundError as exc:
        print(f"[FATAL] block timestamp table missing -- cannot resolve any window's calendar "
              f"date, halting the whole run.\n{exc}")
        raise
    print(f"Block timestamps loaded  ({len(block_ts):,} blocks)")

    coverage_rows: list[dict] = []

    for pair, fee_label, path in jobs:
        pool_label = f"{pair}@{fee_label}"

        if not path.exists():
            print(f"[SKIP] {path} not found -- run clean_parquet.py first.")
            for T in T_VALUES:
                coverage_rows.append({
                    "pool": pool_label, "T": T, "outcome": "skipped",
                    "n_total_blocks": pd.NA, "n_qualifying_blocks": pd.NA,
                    "n_windows": pd.NA, "n_windows_aligned": pd.NA, "reason": "parquet not found",
                })
            continue

        print(f"\n=== {pool_label} ===")
        df = pd.read_parquet(
            path, columns=["block_number", "tick_idx", "liquidity", "curr_tick"]
        )
        qual = build_qualifying_matrix(df)
        print(f"  n_total_blocks={qual.n_total_blocks}  n_qualifying={qual.n_qualifying}")

        bps_dir = _OUT / fee_label
        bps_dir.mkdir(parents=True, exist_ok=True)

        T_windows: dict[int, list] = {}
        for T in T_VALUES:
            if qual.n_qualifying < T:
                reason = f"only {qual.n_qualifying} qualifying blocks, need >= {T}"
                print(f"  [SKIP] T={T}: {reason}")
                coverage_rows.append({
                    "pool": pool_label, "T": T, "outcome": "skipped",
                    "n_total_blocks": qual.n_total_blocks,
                    "n_qualifying_blocks": qual.n_qualifying,
                    "n_windows": pd.NA, "n_windows_aligned": pd.NA, "reason": reason,
                })
                continue

            try:
                windows = rolling_cpve(
                    qual.log_liq, qual.qualifying_blocks, window_T=T, step=STEP
                )
            except ValueError as exc:
                # Regression guard: 5605b8e added this around the old single-call compute_cpve
                # (degenerate-variance windows are real on this data, 4/11 pools hit it);
                # 9f289cc's rewrite to rolling_cpve dropped the guard by omission. Restored here
                # at the same whole-(pool, T) granularity as the original -- _fpca_core raises on
                # the first degenerate window inside rolling_cpve's own loop, so there is no
                # partial-window result to salvage from this call.
                reason = f"rolling_cpve raised {exc}"
                print(f"  [SKIP] T={T}: {reason}")
                coverage_rows.append({
                    "pool": pool_label, "T": T, "outcome": "skipped",
                    "n_total_blocks": qual.n_total_blocks,
                    "n_qualifying_blocks": qual.n_qualifying,
                    "n_windows": pd.NA, "n_windows_aligned": pd.NA, "reason": reason,
                })
                continue

            if not windows:
                # Defensive: rolling_cpve itself guards this (n_qualifying >= T already
                # ensures at least one full window), but the check stays fast-loud rather
                # than silently falling through to an empty plot call below.
                reason = "rolling_cpve returned no windows"
                print(f"  [SKIP] T={T}: {reason}")
                coverage_rows.append({
                    "pool": pool_label, "T": T, "outcome": "skipped",
                    "n_total_blocks": qual.n_total_blocks,
                    "n_qualifying_blocks": qual.n_qualifying,
                    "n_windows": pd.NA, "n_windows_aligned": pd.NA, "reason": reason,
                })
                continue

            T_windows[T] = windows

        if not T_windows:
            continue

        # Crop every T variant's window list to the same window count -- exact (start, end)
        # date-range match across this pool's own T=300/400/500 plots, no recomputation.
        aligned = _align_windows_across_T(T_windows)
        aligned_n = len(next(iter(aligned.values())))
        is_thin = aligned_n < MIN_ALIGNED_WINDOWS
        if is_thin:
            print(f"  [WARN] {pool_label}: aligned window count {aligned_n} < "
                  f"MIN_ALIGNED_WINDOWS={MIN_ALIGNED_WINDOWS} -- plots will still be produced "
                  f"but are too thin to trust visually.")

        for T, windows in T_windows.items():
            aligned_windows = aligned[T]

            # Every qualifying block is a member of the shared 1641-block grid, so it must be
            # present in block_ts -- assert rather than silently produce a plot with missing
            # or misaligned x-values.
            window_start_blocks = np.array(
                [w.window_start_block for w in aligned_windows], dtype=np.int64
            )
            missing = ~np.isin(window_start_blocks, block_ts.index.to_numpy())
            assert not missing.any(), (
                f"functional_pca_study: {missing.sum()} window_start_block(s) for {pool_label} "
                f"T={T} not found in block_ts -- e.g. {window_start_blocks[missing][:5].tolist()}"
            )
            window_dates = [block_ts.loc[b] for b in window_start_blocks]

            pve_out_path = bps_dir / f"{pair}_{T}_pve.png"
            plot_pve_stacked_vs_window_start(aligned_windows, window_dates, pool_label, T, pve_out_path)

            spectral_out_path = bps_dir / f"{pair}_{T}_spectral.png"
            plot_spectral_diagnostics_vs_window_start(
                aligned_windows, window_dates, pool_label, T, spectral_out_path
            )

            coverage_rows.append({
                "pool": pool_label, "T": T,
                "outcome": "produced-thin" if is_thin else "produced",
                "n_total_blocks": qual.n_total_blocks,
                "n_qualifying_blocks": qual.n_qualifying,
                "n_windows": len(windows),
                "n_windows_aligned": len(aligned_windows),
                "reason": (
                    f"aligned window count {aligned_n} < "
                    f"MIN_ALIGNED_WINDOWS={MIN_ALIGNED_WINDOWS}"
                    if is_thin else ""
                ),
            })

    coverage_df = pd.DataFrame(coverage_rows)
    coverage_df.to_csv(_OUT / "coverage.csv", index=False)

    n_produced = int((coverage_df["outcome"] == "produced").sum())
    n_thin = int((coverage_df["outcome"] == "produced-thin").sum())
    n_skipped = int((coverage_df["outcome"] == "skipped").sum())
    print(f"\nCoverage: {n_produced} produced, {n_thin} produced-thin, {n_skipped} skipped, "
          f"{len(coverage_df)} total (pool, T) combinations -- coverage.csv written to {_OUT}")


if __name__ == "__main__":
    main()
