"""
Functional PCA of one pool's log-liquidity surface, on a rolling window over a rank-
standardized nearest-jump-tick grid (paper Risk/Tung/Wang, "Dynamics of Liquidity Surfaces in
Uniswap V3," Fig. 4 bottom; grid construction per Appendix B).

Sibling module. No I/O, no CFG import (math_core stays pure-computation) -- closer in shape to
profile_measure.py than to liquidity_profile.py: the rank-standardized grid needs per-block
variable-tick selection that build_liquidity_surface cannot produce, so this module does NOT
call build_liquidity_surface at all.

Method:
    Per block: sort ticks ascending, locate the anchor position (the last initialized tick at
    or before curr_tick -- clean_parquet.py's own convention), take the M ticks nearest-rank to
    that anchor (M//2 on each side), log-transform. Column j of the resulting row always means
    "j-th nearest-rank tick" consistently across a pool's rows -- this consistency is what makes
    the column-wise covariance meaningful. A block that lacks M//2 initialized ticks on either
    side of its own anchor, or that selects any non-positive liquidity value, is dropped and the
    surviving sequence is re-indexed (order preserved) -- "drop the block, keep rolling".

    Per rolling window of T consecutive qualifying blocks (step=10, full windows only):
        Y (T x M): rows = time, cols = rank-standardized grid, values = log L_t(x).
        Column-center: Yc = Y - mean_t(Y).
        Sigma_hat = (1/T) Yc^T Yc  (M x M, symmetric PSD by construction).
        Sigma_hat = U Lambda U^T, lambda_1 >= ... >= lambda_M >= 0.
        PVE_j = lambda_j / sum(lambda).  CPVE_K = sum_{j<=K} PVE_j.

    No NaN-trim: build_qualifying_matrix already guarantees every qualifying row is fully
    populated (M is fixed and every selected value is checked > 0), so there is nothing to trim
    -- unlike the old uniform-log-moneyness-grid version of this module, whose NaN-proneness on
    sparse pools this rank-standardized construction avoids by design.
"""
from __future__ import annotations

from typing import NamedTuple

import numpy as np
import pandas as pd

M_GRID = 201


class QualifyingResult(NamedTuple):
    """
    One pool's qualifying-block log-liquidity matrix -- built once per pool, before any
    rolling-window-length (T) sweep, since a pool's feasible-block set does not depend on T.

    log_liq          : (n_qualifying, M) log-liquidity, one row per qualifying block, ascending
                        block order. Column j is consistently the j-th nearest-rank tick to that
                        block's own anchor, across every row.
    qualifying_blocks: (n_qualifying,) int64 block numbers, ascending, row-aligned with log_liq.
    n_total_blocks    : distinct block count in the input df, before the feasibility/positivity
                        filter.
    n_qualifying      : len(qualifying_blocks) -- kept as an explicit field so callers don't
                        recompute it from an array shape.
    """
    log_liq: np.ndarray
    qualifying_blocks: np.ndarray
    n_total_blocks: int
    n_qualifying: int


class WindowResult(NamedTuple):
    """
    One rolling window's functional-PCA spectrum (full M-length, K sliced at plot time).

    window_start_block: block number of the window's first (earliest) row -- the caller
                         resolves this to a calendar date via block_timestamps, not here.
    eigenvalues        : (M,) descending, clipped >= 0.
    eigenvectors       : (M, M) columns u_1..u_M (same descending order as eigenvalues),
                         sign-fixed by _fpca_core's convention -- see that function's docstring
                         for what the convention is and its known limit (correct for one window
                         at a time; not yet sign-consistent ACROSS windows).
    cpve               : (M,) cumulative proportion of variance explained, ascending,
                         cpve[-1] == 1.
    T                   : window length (row count).
    M                   : grid width (column count).
    """
    window_start_block: int
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    cpve: np.ndarray
    T: int
    M: int


def _select_rank_standardized_row(
    tick_idx: np.ndarray,
    liquidity: np.ndarray,
    curr_tick: int,
    M: int = M_GRID,
) -> np.ndarray | None:
    """
    One block's rank-standardized log-liquidity row: the M liquidity values nearest-rank to the
    block's own anchor tick, ascending tick order (Appendix B).

    Anchor convention (verbatim from clean_parquet.py:136): the position, in the block's own
    ascending tick_idx array, of the last initialized tick at or before curr_tick --
    `searchsorted(curr_tick, side="right") - 1`.

    Args:
        tick_idx : (n,) this block's initialized tick indices, any order.
        liquidity: (n,) matching reconstructed liquidity values.
        curr_tick: pool's current tick for this block.
        M        : window width (M_GRID=201 -- (M-1)//2 ticks on each side of the anchor).
    Returns:
        (M,) log-liquidity row (ascending tick order), or None if infeasible -- fewer than
        (M-1)//2 initialized ticks on either side of the anchor, or any selected liquidity
        value <= 0 (disqualifies the block outright; no partial/NaN row is ever returned).
    """
    order = np.argsort(tick_idx, kind="stable")
    tick_sorted = tick_idx[order]
    liq_sorted = liquidity[order]

    anchor_pos = int(tick_sorted.searchsorted(curr_tick, side="right")) - 1
    half = (M - 1) // 2
    n = tick_sorted.shape[0]

    if anchor_pos < half or anchor_pos > n - 1 - half:
        return None

    window = liq_sorted[anchor_pos - half : anchor_pos + half + 1]
    if np.any(~np.isfinite(window) | (window <= 0.0)):
        return None
    return np.log(window)


def build_qualifying_matrix(df: pd.DataFrame, M: int = M_GRID) -> QualifyingResult:
    """
    One pool's qualifying-block log-liquidity matrix. Called once per pool, before any
    rolling-window T-sweep (not once per T-value).

    Args:
        df: processed parquet DataFrame, columns [block_number, tick_idx, liquidity, curr_tick]
            (output of clean_parquet.py). Every row present for a block is already an
            initialized (liquidity-changing) tick -- no additional filtering needed here.
        M : grid width, forwarded to _select_rank_standardized_row.
    Returns:
        QualifyingResult -- see its own docstring.
    """
    if M % 2 == 0:  # finding #5: half = (M-1)//2 only yields M elements for odd M
        M += 1

    n_total_blocks = int(df["block_number"].nunique())

    qualifying_rows: list[np.ndarray] = []
    qualifying_blocks: list[int] = []

    for block_number, block_df in df.groupby("block_number", sort=True):
        tick_idx = block_df["tick_idx"].to_numpy(dtype=np.int64)
        liquidity = block_df["liquidity"].to_numpy(dtype=np.float64)
        curr_tick = int(block_df["curr_tick"].iloc[0])

        row = _select_rank_standardized_row(tick_idx, liquidity, curr_tick, M=M)
        if row is None:
            continue
        qualifying_rows.append(row)
        qualifying_blocks.append(int(block_number))

    log_liq = np.vstack(qualifying_rows) if qualifying_rows else np.empty((0, M))
    return QualifyingResult(
        log_liq=log_liq,
        qualifying_blocks=np.array(qualifying_blocks, dtype=np.int64),
        n_total_blocks=n_total_blocks,
        n_qualifying=len(qualifying_blocks),
    )


def _fpca_core(Y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Pure-array FPCA arithmetic core: column-center, eigendecompose, PVE/CPVE. No NaN-trim --
    build_qualifying_matrix already guarantees every row is fully populated and every column
    consistently the j-th nearest-rank tick, so there is nothing to trim.

    Sign convention (decided [H] 2026-08-17, option 1 of three discussed at framing time):
    eigh fixes each eigenvector only up to sign, so every column is flipped, independently, to
    make its own largest-magnitude entry positive. Deterministic, and more robust than flipping
    on a fixed grid position (e.g. the leftmost column), which can sit arbitrarily close to a
    zero-crossing for some k and make the flip numerically unstable.

    NOTE 1 (planned follow-up): this module currently surfaces eigenvectors for exactly one
    window at a time -- rolling_cpve's windows are read independently of each other, and the
    only other caller, select_single_window, returns a single WindowResult. The max-|entry|
    rule is correct as far as that goes.
    NOTE 2 (limit of NOTE 1): it stops being sufficient the moment eigenvectors from two or
    more windows are plotted together (planned -- see graphics.functional_pca.
    plot_eigenvectors_grid's own docstring) — the same per-column rule applied independently to
    each window can flip one window's u_k relative to another's for no economic reason, unlike
    the reference figure this project is replicating, whose multi-window curves are
    consistently oriented. Fixing that means switching this rule to (2) (sign-align every
    window against a fixed reference window's eigenvector, by the sign of their inner product)
    or (3) (a manual per-plot flip) -- neither is implemented here.

    Args:
        Y: (T, M) log-liquidity window -- T rows (time), M columns (rank-standardized ticks).
    Returns:
        eigenvalues : (M,) descending, clipped >= 0.
        eigenvectors: (M, M) columns u_1..u_M, same descending order as eigenvalues, sign-fixed
                      per the convention above.
        cpve        : (M,) cumulative proportion of variance explained, ascending, cpve[-1] == 1.
    Raises:
        ValueError: total variance is <= 0 (degenerate covariance -- the surface is constant
                    over this window after centering).
    """
    T = Y.shape[0]

    # Column-wise centering: subtract each grid point's temporal mean over this window.
    Yc = Y - Y.mean(axis=0, keepdims=True)

    # Sample covariance, M x M. eigh (not generic eig): Sigma is symmetric PSD by
    # construction, so eigh is numerically stable and returns real eigenvalues natively --
    # no complex-part discard, no sorting surprises from a non-symmetric solver.
    Sigma = (Yc.T @ Yc) / T
    eigvals_asc, eigvecs_asc = np.linalg.eigh(Sigma)

    # Descending, per lambda_1 >= ... >= lambda_M. Clip float roundoff on a rank-deficient
    # Sigma (T < M is the common case here) to 0 -- true PSD eigenvalues are >= 0, a small
    # negative one is numerical noise, not signal.
    eigenvalues = np.clip(eigvals_asc[::-1], a_min=0.0, a_max=None)
    eigenvectors = eigvecs_asc[:, ::-1]  # same index reversal, column-for-column with eigenvalues.

    # Sign convention (1): flip each column so its own largest-magnitude entry is positive.
    peak_idx = np.argmax(np.abs(eigenvectors), axis=0)
    peak_val = eigenvectors[peak_idx, np.arange(eigenvectors.shape[1])]
    eigenvectors = eigenvectors * np.where(peak_val < 0.0, -1.0, 1.0)

    total_var = float(eigenvalues.sum())
    if not np.isfinite(total_var) or total_var <= 0.0:
        raise ValueError(
            f"_fpca_core: total variance is {total_var} (degenerate or non-finite covariance) "
            "-- surface is constant over this window after centering, or a NaN reached this "
            "window despite the upstream feasibility guarantee."
        )
    pve = eigenvalues / total_var
    cpve = np.cumsum(pve)
    return eigenvalues, eigenvectors, cpve


def effective_rank(eigenvalues: np.ndarray) -> float:
    """
    Shannon-entropy effective rank of a window's eigenvalue spectrum: exp(H), H = -sum(p_i *
    log(p_i)), p_i = lambda_i / sum(lambda). Continuous companion to "K needed for X% CPVE" --
    reads as the average number of modes the window's variance spreads across, with no
    threshold to choose. Degenerates to 1 when one eigenvalue carries all the variance, to M
    (the grid width) when the spectrum is perfectly flat.

    Zero eigenvalues (the common case here -- T < M makes Sigma_hat rank-deficient) are
    excluded from the sum rather than left in: p_i*log(p_i) -> 0 in the limit p_i -> 0, so
    dropping the exact zeros is the correct limit, not an approximation, and avoids a log(0)
    warning for no numerical benefit.

    Args:
        eigenvalues: (M,) descending, >= 0 -- a WindowResult.eigenvalues array (already
                     clipped and validated finite/positive-sum by _fpca_core).
    Returns:
        Effective rank, in [1, M].
    Raises:
        AssertionError: total variance is <= 0 -- should not reach here for eigenvalues that
                        came out of _fpca_core, which already raises on this case first.
    """
    total_var = float(eigenvalues.sum())
    assert total_var > 0.0, f"effective_rank: total variance is {total_var}, expected > 0"

    p = eigenvalues / total_var
    positive = p > 0.0
    entropy = -float(np.sum(p[positive] * np.log(p[positive])))
    return float(np.exp(entropy))


def rolling_cpve(
    log_liq: np.ndarray,
    qualifying_blocks: np.ndarray,
    window_T: int,
    step: int = 10,
) -> list[WindowResult]:
    """
    Slide a fixed-length window over a pool's qualifying-block sequence, running _fpca_core on
    each full window. Full windows only -- no partial trailing window. Returns the full M-length
    spectrum per window; K=1..6 is sliced at plot time, not here (keeps this module generic and
    independent of a display-only choice -- eigh on a 201x201 matrix is cheap regardless).

    Args:
        log_liq          : (n_qualifying, M) from build_qualifying_matrix.
        qualifying_blocks: (n_qualifying,) block numbers, ascending, row-aligned with log_liq.
        window_T          : window length in rows.
        step              : row stride between consecutive window starts (paper value: 10).
    Returns:
        List of WindowResult, one per full window, in ascending window_start order.
    """
    n_qualifying, M = log_liq.shape

    windows: list[WindowResult] = []
    for start in range(0, n_qualifying - window_T + 1, step):
        Y = log_liq[start : start + window_T, :]
        eigenvalues, eigenvectors, cpve = _fpca_core(Y)
        windows.append(WindowResult(
            window_start_block=int(qualifying_blocks[start]),
            eigenvalues=eigenvalues,
            eigenvectors=eigenvectors,
            cpve=cpve,
            T=window_T,
            M=M,
        ))
    return windows


def select_single_window(
    log_liq: np.ndarray,
    qualifying_blocks: np.ndarray,
    start: int = 0,
    window_T: int | None = None,
) -> WindowResult:
    """
    One caller-chosen window's FPCA result -- not a rolling sweep. Default (start=0,
    window_T=None) runs on the WHOLE qualifying-block sequence, a single window covering the
    full sample; this is the "run on the whole window" mode. Passing an explicit (start,
    window_T) selects a sub-window instead, using the same slicing rolling_cpve applies
    internally -- this is that same one-window computation, pulled out standalone so a caller
    that wants exactly one window (e.g. for an eigenvector plot) doesn't have to fake it through
    a rolling_cpve(window_T=..., step=huge) call that returns a length-1 list.

    This is the seam for the planned future extension to comparing up to four caller-chosen
    windows side by side (paper Fig. 5's "Window 1/2/3" panels): call this once per window and
    hand the resulting list of WindowResult to
    graphics.functional_pca.plot_eigenvectors_grid. See that function's docstring, and
    _fpca_core's, for the sign-convention limitation that extension will run into.

    Args:
        log_liq          : (n_qualifying, M) from build_qualifying_matrix.
        qualifying_blocks: (n_qualifying,) block numbers, ascending, row-aligned with log_liq.
        start             : row index of the window's first block. Default 0.
        window_T          : window length in rows. Default None -> n_qualifying - start (the
                             whole remaining sequence from `start`; with the default start=0,
                             the whole dataset).
    Returns:
        WindowResult for the selected window (eigenvalues, eigenvectors, and cpve all present).
    Raises:
        ValueError: start < 0, window_T <= 0, or start + window_T exceeds n_qualifying (an
                    explicit range/index-shape check, not delegated to a numpy slice that would
                    silently return a shorter-than-requested window instead of failing loud);
                    or (from _fpca_core) degenerate covariance over the selected window.
    """
    n_qualifying = log_liq.shape[0]
    if window_T is None:
        window_T = n_qualifying - start
    if start < 0 or window_T <= 0 or start + window_T > n_qualifying:
        raise ValueError(
            f"select_single_window: invalid window (start={start}, window_T={window_T}) for "
            f"n_qualifying={n_qualifying}"
        )

    Y = log_liq[start : start + window_T, :]
    eigenvalues, eigenvectors, cpve = _fpca_core(Y)
    return WindowResult(
        window_start_block=int(qualifying_blocks[start]),
        eigenvalues=eigenvalues,
        eigenvectors=eigenvectors,
        cpve=cpve,
        T=window_T,
        M=Y.shape[1],
    )


def rank_standardized_x_grid(M: int = M_GRID) -> np.ndarray:
    """
    The rank-standardized grid coordinate, affine-mapped to [-1, 1] (Appendix B). Column j of
    any log_liq / eigenvector matrix this module produces is consistently the j-th nearest-rank
    tick to a block's own anchor, so this one coordinate array indexes every one of them.

    Mirrors the identical rank-affine construction already used for the (separate)
    liquidity-surface relative-tick plots (math_core/liquidity_profile.py's `relative_tick_M`
    branch) -- restated here rather than imported, since that module's version is fill-not-drop
    and keyed to its own M convention (CFG.liquidity_M, not M_GRID); the formula itself is a
    one-liner, cheaper to restate than to couple the two modules over.

    Args:
        M: grid width. Must be odd for the M-th point to land exactly on the anchor
           (build_qualifying_matrix bumps an even M up by one for the same reason) -- stays
           consistent by construction as long as the caller passes the same M it built log_liq
           with; M_GRID=201 (the default) already satisfies this.
    Returns:
        (M,) ascending, x[0] == -1.0, x[-1] == 1.0.
    """
    return np.linspace(-1.0, 1.0, M)
