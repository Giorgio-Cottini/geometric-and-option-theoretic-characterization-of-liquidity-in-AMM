"""
functional_pca_eigenvectors_study.py
-------------------------------------
Cycle 4, backlog item 3: eigenvectors u_1..u_4 of the rank-standardized log-liquidity surface's
functional PCA, vs. the rank-standardized grid coordinate -- Fig. 5 companion to
functional_pca_study.py's Fig. 4 (bottom) replication (Risk/Tung/Wang, "Dynamics of Liquidity
Surfaces in Uniswap V3").

Default mode: ONE window per pool, spanning the pool's entire qualifying-block sequence
(src.math_core.functional_pca.select_single_window's default start=0, window_T=None) -- not
functional_pca_study.py's rolling T-sweep. WINDOW_LABEL / the single select_single_window call
below is the seam for the planned future extension to up to 4 caller-chosen windows per pool
(paper Fig. 5's "Window 1/2/3" panels); see plot_eigenvectors_grid's own docstring for the
sign-convention limitation that extension will run into.

Input  : data/processed/liquidity/{PAIR}/{file_basename}_ticks.parquet
Output : results/liquidity-pipeline/functional-pca/{fee}bp/{PAIR}_eigenvectors.png
             one PNG per pool with >= 2 qualifying blocks (fewer makes the window's own
             covariance degenerate); coverage recorded the same way functional_pca_study.py
             does -- skipped pools listed with a reason, not silently dropped
         results/liquidity-pipeline/functional-pca/eigenvectors_coverage.csv

Usage
-----
    python codebase/functional_pca_eigenvectors_study.py   (from repo root)
    python functional_pca_eigenvectors_study.py             (from codebase/)
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # non-interactive backend -- must precede pyplot import

import pandas as pd

# ── Path bootstrap (so data_extraction.config is importable) ─────────────────
_HERE = Path(__file__).parent  # codebase/
sys.path.insert(0, str(_HERE))

from data_extraction import config as ext_config  # noqa: E402

from src.math_core.functional_pca import (  # noqa: E402
    build_qualifying_matrix,
    select_single_window,
    rank_standardized_x_grid,
)
from src.graphics import plot_eigenvectors_grid  # noqa: E402
from src.graphics.config import CFG  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────
_PROCESSED_ROOT = _HERE / "data" / "processed" / "liquidity"
_OUT = CFG.fpca_out_dir

# Default single-window label. Extending to multiple windows means replacing the single
# select_single_window call in main() with one call per (label, start, window_T) spec and
# passing the resulting list straight to plot_eigenvectors_grid, which already accepts up to 4.
WINDOW_LABEL = "Whole dataset"

# Below this, the window's own covariance is degenerate (T=1 has zero temporal variance;
# T=0 cannot form a window at all) -- caught here with a specific reason instead of falling
# through to select_single_window's more generic ValueError.
MIN_QUALIFYING_BLOCKS = 2


def _build_jobs() -> list[tuple[str, str, Path]]:
    """One job per pool in config.POOLS -- same assembly as functional_pca_study.py's."""
    jobs: list[tuple[str, str, Path]] = []
    for pcfg in ext_config.POOLS.values():
        pair = pcfg["pair"]
        jobs.append((
            pair,
            f"{pcfg['fee_bps']}bp",
            _PROCESSED_ROOT / pair / f"{pcfg['file_basename']}_ticks.parquet",
        ))
    return jobs


def main() -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    jobs = _build_jobs()
    print(f"Jobs    : {[(p, f) for p, f, _ in jobs]}")

    x_grid = rank_standardized_x_grid()
    coverage_rows: list[dict] = []

    for pair, fee_label, path in jobs:
        pool_label = f"{pair}@{fee_label}"

        if not path.exists():
            print(f"[SKIP] {path} not found -- run clean_parquet.py first.")
            coverage_rows.append({
                "pool": pool_label, "outcome": "skipped",
                "n_total_blocks": pd.NA, "n_qualifying_blocks": pd.NA,
                "reason": "parquet not found",
            })
            continue

        print(f"\n=== {pool_label} ===")
        df = pd.read_parquet(
            path, columns=["block_number", "tick_idx", "liquidity", "curr_tick"]
        )
        qual = build_qualifying_matrix(df)
        print(f"  n_total_blocks={qual.n_total_blocks}  n_qualifying={qual.n_qualifying}")

        if qual.n_qualifying < MIN_QUALIFYING_BLOCKS:
            reason = (
                f"only {qual.n_qualifying} qualifying blocks, need >= "
                f"{MIN_QUALIFYING_BLOCKS} for a non-degenerate covariance"
            )
            print(f"  [SKIP] {reason}")
            coverage_rows.append({
                "pool": pool_label, "outcome": "skipped",
                "n_total_blocks": qual.n_total_blocks,
                "n_qualifying_blocks": qual.n_qualifying, "reason": reason,
            })
            continue

        try:
            window = select_single_window(qual.log_liq, qual.qualifying_blocks)
        except ValueError as exc:
            # Defensive: MIN_QUALIFYING_BLOCKS should already exclude the degenerate case
            # (T=1, zero temporal variance after centering), but this stays fast-loud-and-
            # caught rather than letting an unanticipated degenerate window halt the whole
            # pool loop -- same posture as functional_pca_study.py's rolling_cpve guard.
            reason = f"select_single_window raised {exc}"
            print(f"  [SKIP] {reason}")
            coverage_rows.append({
                "pool": pool_label, "outcome": "skipped",
                "n_total_blocks": qual.n_total_blocks,
                "n_qualifying_blocks": qual.n_qualifying, "reason": reason,
            })
            continue

        bps_dir = _OUT / fee_label
        bps_dir.mkdir(parents=True, exist_ok=True)
        out_path = bps_dir / f"{pair}_eigenvectors.png"
        plot_eigenvectors_grid(
            windows=[window],
            window_labels=[WINDOW_LABEL],
            x_grid=x_grid,
            pool_label=pool_label,
            out_path=out_path,
        )
        coverage_rows.append({
            "pool": pool_label, "outcome": "produced",
            "n_total_blocks": qual.n_total_blocks,
            "n_qualifying_blocks": qual.n_qualifying, "reason": "",
        })

    coverage_df = pd.DataFrame(coverage_rows)
    coverage_df.to_csv(_OUT / "eigenvectors_coverage.csv", index=False)

    n_produced = int((coverage_df["outcome"] == "produced").sum())
    n_skipped = int((coverage_df["outcome"] == "skipped").sum())
    print(f"\nCoverage: {n_produced} produced, {n_skipped} skipped, {len(coverage_df)} total "
          f"pools -- eigenvectors_coverage.csv written to {_OUT}")


if __name__ == "__main__":
    main()
