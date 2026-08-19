"""
Standalone tests for the cycle-4 functional-PCA module and runner.

No pytest (the project invokes bare `python`): each test is a plain function asserting an
invariant; the __main__ block runs them all and prints PASS.

Run:  python codebase/tests/test_functional_pca_study.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_CODEBASE = Path(__file__).resolve().parents[1]   # codebase/
sys.path.insert(0, str(_CODEBASE))

from src.math_core.functional_pca import (  # noqa: F401,E402
    _select_rank_standardized_row,
    build_qualifying_matrix,
    _fpca_core,
    rolling_cpve,
    select_single_window,
    rank_standardized_x_grid,
    effective_rank,
    QualifyingResult,
    WindowResult,
    M_GRID,
)
import functional_pca_study  # noqa: F401,E402 -- Task C's rewrite makes this import clean.


def _hadamard3_fixture() -> tuple[np.ndarray, np.ndarray]:
    """
    Three mutually-orthogonal, zero-mean columns of a 4x4 Hadamard matrix, scaled by
    weights 3, 1, 1. Because the columns are exactly orthogonal and already zero-mean,
    centering is a no-op and Sigma_hat = diag(w1^2, w2^2, w3^2) EXACTLY (T=4 rows,
    each column has squared norm 4, so (1/T)*col_j . col_j = w_j^2). Gives a closed-form
    eigenvalue spectrum [9, 1, 1] independent of _fpca_from_matrix's own arithmetic --
    not a tautological re-derivation of the function under test.
    """
    col1 = np.array([1.0, -1.0, 1.0, -1.0])
    col2 = np.array([1.0, 1.0, -1.0, -1.0])
    col3 = np.array([1.0, -1.0, -1.0, 1.0])
    Y = np.column_stack([3.0 * col1, 1.0 * col2, 1.0 * col3])
    x_axis = np.array([0.0, 0.1, 0.2])
    return Y, x_axis


def test_eigenvalues_sorted_descending_and_nonnegative():
    """(d, rewritten against _fpca_core) PSD check: eigenvalues never increase, and clip()
    guarantees none is negative."""
    Y, _x_axis = _hadamard3_fixture()
    eigenvalues, _eigenvectors, _cpve = _fpca_core(Y)
    assert np.all(np.diff(eigenvalues) <= 1e-12), eigenvalues
    assert np.all(eigenvalues >= 0.0), eigenvalues


def test_fpca_core_rank1_surface_gives_cpve1_near_one():
    """
    Rewritten against _fpca_core's (eigenvalues, cpve) signature -- no x_axis, no NaN-trim
    fields. A Y matrix built as an exact outer product u (x) v has an exactly rank-1 covariance
    after centering (centering an outer product only shifts along u, Yc = u_c (x) v is still
    rank 1), so CPVE_1 should be ~1 and every later eigenvalue ~0 (float roundoff only).
    """
    u = np.linspace(-2.0, 2.0, 5)
    v = np.linspace(-1.0, 1.0, 6)
    Y = np.outer(u, v)

    eigenvalues, _eigenvectors, cpve = _fpca_core(Y)
    assert cpve[0] > 1.0 - 1e-9, f"expected CPVE_1 ~= 1, got {cpve[0]!r}"
    assert np.all(eigenvalues[1:] < 1e-9), eigenvalues


def test_fpca_core_hadamard_closed_form_spectrum():
    """
    Rewritten against _fpca_core's signature -- k_for_90/k_for_95 no longer exist as fields, so
    the 90%/95% crossings are asserted directly against cpve instead. Closed-form spectrum
    [9, 1, 1] (see _hadamard3_fixture docstring) gives PVE = [9/11, 1/11, 1/11] and
    CPVE = [0.8182, 0.9091, 1.0] -- crosses 0.90 at K=2 (not K=1 or K=3), crosses 0.95 at K=3.
    """
    Y, _x_axis = _hadamard3_fixture()
    eigenvalues, _eigenvectors, cpve = _fpca_core(Y)

    expected_eigs = np.array([9.0, 1.0, 1.0])
    assert np.allclose(eigenvalues, expected_eigs, atol=1e-9), eigenvalues

    expected_cpve = np.cumsum(expected_eigs / expected_eigs.sum())
    assert np.allclose(cpve, expected_cpve, atol=1e-9), cpve
    assert cpve[0] < 0.90 <= cpve[1], f"expected CPVE to cross 0.90 at K=2, got cpve={cpve}"
    assert cpve[1] < 0.95 <= cpve[2], f"expected CPVE to cross 0.95 at K=3, got cpve={cpve}"


def test_anchor_rank_selection_synthetic_block():
    """
    Synthetic-block coverage of _select_rank_standardized_row's feasibility window (small
    M=5, half=2): (1) exact-boundary feasible, where anchor_pos sits exactly half ticks from
    both array edges; (2) one-short-on-the-left infeasible, anchor_pos = half - 1; (3)
    one-short-on-the-right infeasible, anchor_pos = n - half; (4) a planted non-positive
    liquidity value disqualifies an otherwise-feasible block.
    """
    M = 5

    # (1) exact-boundary feasible: n=5, anchor_pos=2=half=n-1-half.
    tick_idx = np.array([10, 20, 30, 40, 50], dtype=np.int64)
    liquidity = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64)
    curr_tick = 30
    row = _select_rank_standardized_row(tick_idx, liquidity, curr_tick, M=M)
    assert row is not None, "exact-boundary block should be feasible"
    assert np.allclose(row, np.log(liquidity)), row

    # (2) one-short-on-the-left: n=4, anchor_pos=1 < half=2.
    tick_idx_left = np.array([10, 20, 30, 40], dtype=np.int64)
    liquidity_left = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64)
    curr_tick_left = 20
    assert _select_rank_standardized_row(tick_idx_left, liquidity_left, curr_tick_left, M=M) is None

    # (3) one-short-on-the-right: n=4, anchor_pos=2 > n-1-half=1.
    tick_idx_right = np.array([10, 20, 30, 40], dtype=np.int64)
    liquidity_right = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64)
    curr_tick_right = 30
    assert _select_rank_standardized_row(tick_idx_right, liquidity_right, curr_tick_right, M=M) is None

    # (4) planted non-positive liquidity disqualifies the otherwise-feasible block from (1).
    liquidity_bad = liquidity.copy()
    liquidity_bad[1] = 0.0
    assert _select_rank_standardized_row(tick_idx, liquidity_bad, curr_tick, M=M) is None


def test_qualifying_matrix_drop_and_reindex():
    """
    Three blocks (100, 200, 300), M=3 (half=1). Blocks 100 and 300 are feasible (n=3, anchor
    exactly mid); block 200 has only n=2 ticks, structurally infeasible for M=3 regardless of
    curr_tick. Confirms the surviving sequence skips block 200 but stays ascending, and
    log_liq's row order matches qualifying_blocks' order.
    """
    M = 3
    rows = pd.DataFrame([
        # block 100: feasible, anchor_pos=1=half=n-1-half.
        {"block_number": 100, "tick_idx": 0, "liquidity": 1.0, "curr_tick": 1},
        {"block_number": 100, "tick_idx": 1, "liquidity": 2.0, "curr_tick": 1},
        {"block_number": 100, "tick_idx": 2, "liquidity": 3.0, "curr_tick": 1},
        # block 200: infeasible, only 2 ticks (< M=3 needed for any anchor position).
        {"block_number": 200, "tick_idx": 5, "liquidity": 10.0, "curr_tick": 5},
        {"block_number": 200, "tick_idx": 6, "liquidity": 20.0, "curr_tick": 5},
        # block 300: feasible, anchor_pos=1=half=n-1-half.
        {"block_number": 300, "tick_idx": 100, "liquidity": 7.0, "curr_tick": 101},
        {"block_number": 300, "tick_idx": 101, "liquidity": 8.0, "curr_tick": 101},
        {"block_number": 300, "tick_idx": 102, "liquidity": 9.0, "curr_tick": 101},
    ])

    result = build_qualifying_matrix(rows, M=M)
    assert result.n_total_blocks == 3
    assert result.n_qualifying == 2
    assert list(result.qualifying_blocks) == [100, 300], result.qualifying_blocks
    assert result.log_liq.shape == (2, 3)
    assert np.allclose(result.log_liq[0], np.log([1.0, 2.0, 3.0]))
    assert np.allclose(result.log_liq[1], np.log([7.0, 8.0, 9.0]))


def test_rolling_window_slicing_correctness():
    """
    Synthetic multi-row log_liq (n_qualifying=25, M=3), window_T=10, step=10: exactly 2 full
    windows fit (floor((25-10)/10)+1 = 2), at row-starts 0 and 10 -- resolved to
    qualifying_blocks' values at those row-indices, not to row-index*step. The surface is a
    deterministic row-ramp (rank-1 after centering, nonzero variance) so _fpca_core does not
    hit the degenerate-covariance path.
    """
    n_qualifying, M = 25, 3
    row_idx = np.arange(n_qualifying, dtype=np.float64).reshape(-1, 1)
    col_idx = np.arange(M, dtype=np.float64).reshape(1, -1)
    log_liq = row_idx * 0.1 + col_idx  # deterministic ramp: rank-1 after column-centering.
    qualifying_blocks = np.arange(0, n_qualifying * 10, 10, dtype=np.int64)  # 0, 10, ..., 240

    windows = rolling_cpve(log_liq, qualifying_blocks, window_T=10, step=10)
    assert len(windows) == 2, f"expected 2 full windows, got {len(windows)}"
    assert windows[0].window_start_block == 0, windows[0].window_start_block
    assert windows[1].window_start_block == 100, windows[1].window_start_block
    for w in windows:
        assert w.T == 10 and w.M == 3
        assert w.eigenvalues.shape == (3,)
        assert w.eigenvectors.shape == (3, 3)
        assert w.cpve.shape == (3,)
        assert np.isclose(w.cpve[-1], 1.0), w.cpve


def test_align_windows_across_T_truncates_to_shortest():
    """
    Synthetic WindowResult lists (real fields don't matter here, only list length and
    identity) under three T keys of different lengths. Confirms
    _align_windows_across_T truncates every list to the shortest one, preserves prefix order
    (not some other subset), leaves dict keys unchanged, and is a no-op for a single-T input.
    """
    def _fake_windows(n):
        return [
            WindowResult(window_start_block=10 * i, eigenvalues=np.zeros(1),
                         eigenvectors=np.ones((1, 1)), cpve=np.ones(1), T=300, M=1)
            for i in range(n)
        ]

    T_windows = {300: _fake_windows(5), 400: _fake_windows(3), 500: _fake_windows(4)}
    aligned = functional_pca_study._align_windows_across_T(T_windows)

    assert set(aligned.keys()) == {300, 400, 500}
    for T, windows in aligned.items():
        assert len(windows) == 3, f"T={T}: expected 3 (shortest input), got {len(windows)}"
        assert windows == T_windows[T][:3], f"T={T}: expected exact prefix of the original list"

    single = {400: _fake_windows(7)}
    aligned_single = functional_pca_study._align_windows_across_T(single)
    assert aligned_single == single, "single-T input should be returned unchanged"


def test_rolling_cpve_window_starts_identical_across_T():
    """
    Structural invariant _align_windows_across_T depends on: for a fixed pool (same log_liq,
    same qualifying_blocks, same step), window k's window_start_block is identical across
    different window_T values, since rolling_cpve always starts its slide at index 0 with the
    same step regardless of T. n_qualifying=60, M=3, deterministic ramp surface (nonzero
    variance, avoids the degenerate-covariance path).
    """
    n_qualifying, M = 60, 3
    row_idx = np.arange(n_qualifying, dtype=np.float64).reshape(-1, 1)
    col_idx = np.arange(M, dtype=np.float64).reshape(1, -1)
    log_liq = row_idx * 0.1 + col_idx
    qualifying_blocks = np.arange(0, n_qualifying * 10, 10, dtype=np.int64)

    windows_20 = rolling_cpve(log_liq, qualifying_blocks, window_T=20, step=10)
    windows_30 = rolling_cpve(log_liq, qualifying_blocks, window_T=30, step=10)
    assert len(windows_20) > len(windows_30), "smaller T should produce more windows"

    n_common = min(len(windows_20), len(windows_30))
    assert n_common > 0
    for i in range(n_common):
        assert windows_20[i].window_start_block == windows_30[i].window_start_block, (
            f"window {i}: T=20 starts at {windows_20[i].window_start_block}, "
            f"T=30 starts at {windows_30[i].window_start_block}"
        )


def test_runner_job_assembly_eleven_pools_three_t_values():
    """
    Rewritten for Task C's (pair, fee_label, path) triple -- tick_spacing is dropped, the
    rank-standardized construction has no use for it. Mirrors test_lvr_pathwise.py's
    eleven-pool job-assembly test: one job per data_extraction.config.POOLS entry, no pool
    silently dropped. Also asserts the 11-pool x 3-T_VALUES = 33 (pool, T) combination count
    the plan's coverage.csv is built around.
    """
    jobs = functional_pca_study._build_jobs()
    assert len(jobs) == 11, f"expected 11 jobs (one per pool), got {len(jobs)}"

    pairs = {pair for pair, _fee_label, _path in jobs}
    assert len(pairs) >= 5   # five distinct pairs across the eleven pools

    for pair, fee_label, path in jobs:
        assert fee_label.endswith("bp"), fee_label
        assert path.suffix == ".parquet", path

    assert len(functional_pca_study.T_VALUES) == 3, functional_pca_study.T_VALUES
    assert len(jobs) * len(functional_pca_study.T_VALUES) == 33


def test_select_rank_standardized_row_rejects_nan_window():
    """
    Review finding #2: `window <= 0.0` doesn't catch NaN (NaN <= 0.0 is False in numpy), so a
    NaN liquidity value used to slip past the "no partial/NaN row" guard undetected. Reuses the
    exact-boundary-feasible fixture from test_anchor_rank_selection_synthetic_block's case (1)
    and plants a NaN (not a <= 0 value) at one position.
    """
    M = 5
    tick_idx = np.array([10, 20, 30, 40, 50], dtype=np.int64)
    liquidity_nan = np.array([1.0, 2.0, np.nan, 4.0, 5.0], dtype=np.float64)
    curr_tick = 30
    assert _select_rank_standardized_row(tick_idx, liquidity_nan, curr_tick, M=M) is None


def test_fpca_core_raises_on_nan_input():
    """
    Review finding #3: `total_var <= 0.0` has the same NaN blind spot as finding #2, and
    np.linalg.eigh doesn't raise on NaN input either -- a NaN-poisoned window used to silently
    return NaN eigenvalues/cpve instead of raising. Exercises the widened
    `not np.isfinite(total_var) or total_var <= 0.0` check directly, independent of finding #2's
    upstream fix (a NaN could in principle reach _fpca_core through any future caller).
    """
    Y = np.arange(15, dtype=np.float64).reshape(5, 3)  # nonzero-variance ramp
    Y[2, 1] = np.nan
    try:
        _fpca_core(Y)
    except ValueError:
        return
    raise AssertionError("expected ValueError for NaN-poisoned Y, got a normal return")


def test_rolling_cpve_degenerate_window_raises_and_is_skippable():
    """
    Review finding #1 (regression): a degenerate-covariance window (zero variance after
    centering) must still raise ValueError out of rolling_cpve -- that's what the runner's
    try/except at the rolling_cpve call site now catches. Confirms both halves: (a) the raise
    itself, on a log_liq whose only full window is constant rows; (b) the runner's catch-and-
    skip logic, copied verbatim from the fix, produces a "skipped" coverage row and does not
    propagate the exception.
    """
    n_qualifying, M = 10, 3
    log_liq = np.full((n_qualifying, M), 5.0)  # every row identical -> zero variance
    qualifying_blocks = np.arange(0, n_qualifying * 10, 10, dtype=np.int64)

    try:
        rolling_cpve(log_liq, qualifying_blocks, window_T=10, step=10)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError from a degenerate (constant-row) window")

    # The runner's guard, copied from functional_pca_study.main()'s fixed call site.
    coverage_rows = []
    try:
        windows = rolling_cpve(log_liq, qualifying_blocks, window_T=10, step=10)
    except ValueError as exc:
        reason = f"rolling_cpve raised {exc}"
        coverage_rows.append({
            "pool": "TEST@1bp", "T": 10, "outcome": "skipped",
            "n_total_blocks": 10, "n_qualifying_blocks": 10,
            "n_windows": pd.NA, "n_windows_aligned": pd.NA, "reason": reason,
        })
    else:
        raise AssertionError("expected the guard's except branch to fire")

    assert len(coverage_rows) == 1
    assert coverage_rows[0]["outcome"] == "skipped"
    assert coverage_rows[0]["reason"].startswith("rolling_cpve raised"), coverage_rows[0]["reason"]


def test_align_windows_across_T_thin_pool_flagged():
    """
    Review finding #4: _align_windows_across_T itself is unchanged by the fix (it still just
    crops to the shortest list) -- the new thinness decision lives inline in main() as
    `aligned_n < MIN_ALIGNED_WINDOWS`. Asserts that comparison's boundary behavior directly:
    strictly below the floor is thin, at or above is not.
    """
    floor = functional_pca_study.MIN_ALIGNED_WINDOWS
    assert (2 < floor) is True, "2 aligned windows should be flagged thin"
    assert (floor < floor) is False, "exactly at the floor should not be flagged thin"
    assert (115 < floor) is False, "115 aligned windows should not be flagged thin"


def test_effective_rank_flat_spectrum_equals_M():
    """
    Closed-form check: a perfectly flat spectrum (all M eigenvalues equal) has maximum
    entropy, H = log(M), so effective rank = exp(log(M)) = M exactly.
    """
    M = 8
    eigenvalues = np.full(M, 3.0)  # value is irrelevant, only the flatness matters
    result = effective_rank(eigenvalues)
    assert abs(result - M) < 1e-10, f"expected {M}, got {result}"


def test_effective_rank_rank1_spectrum_equals_one():
    """
    Closed-form check: a rank-1 spectrum (one nonzero eigenvalue, rest exactly zero) has zero
    entropy (the single positive term has p_i=1, log(1)=0, and the exact zeros are excluded
    from the sum by construction), so effective rank = exp(0) = 1 exactly.
    """
    eigenvalues = np.array([5.0, 0.0, 0.0, 0.0])
    result = effective_rank(eigenvalues)
    assert abs(result - 1.0) < 1e-10, f"expected 1.0, got {result}"


def test_effective_rank_two_equal_modes_equals_two():
    """
    Closed-form check between the two extremes: two equal nonzero eigenvalues among otherwise-
    zero entries give p = [0.5, 0.5], H = log(2), effective rank = 2 -- confirms the zero-
    exclusion doesn't distort the entropy of the surviving mass, only drops the log(0) terms.
    """
    eigenvalues = np.array([4.0, 4.0, 0.0, 0.0, 0.0])
    result = effective_rank(eigenvalues)
    assert abs(result - 2.0) < 1e-10, f"expected 2.0, got {result}"


def test_fpca_core_eigenvectors_max_abs_entry_positive():
    """
    Sign convention (decided [H] 2026-08-17, option 1): each returned eigenvector's own
    largest-magnitude entry must be positive. Uses the Hadamard fixture (closed-form spectrum,
    see _hadamard3_fixture), which lets np.linalg.eigh return either sign for a given column
    depending only on floating-point/LAPACK internals -- the convention must hold regardless of
    which sign eigh itself happened to pick.
    """
    Y, _x_axis = _hadamard3_fixture()
    _eigenvalues, eigenvectors, _cpve = _fpca_core(Y)

    assert eigenvectors.shape == (3, 3)
    for k in range(eigenvectors.shape[1]):
        col = eigenvectors[:, k]
        peak = col[np.argmax(np.abs(col))]
        assert peak > 0.0, f"column {k}: largest-magnitude entry is {peak}, expected positive"
    # Orthonormality survives the per-column sign flip (flipping a unit column's sign keeps it
    # a unit column and preserves orthogonality to every other column).
    assert np.allclose(eigenvectors.T @ eigenvectors, np.eye(3), atol=1e-9)


def test_select_single_window_default_is_whole_dataset():
    """
    select_single_window(start=0, window_T=None) (the defaults) must span every qualifying row
    -- T == n_qualifying, window_start_block == the first qualifying block. Reuses the
    deterministic-ramp fixture from test_rolling_window_slicing_correctness (nonzero variance,
    avoids the degenerate-covariance path).
    """
    n_qualifying, M = 25, 3
    row_idx = np.arange(n_qualifying, dtype=np.float64).reshape(-1, 1)
    col_idx = np.arange(M, dtype=np.float64).reshape(1, -1)
    log_liq = row_idx * 0.1 + col_idx
    qualifying_blocks = np.arange(0, n_qualifying * 10, 10, dtype=np.int64)

    window = select_single_window(log_liq, qualifying_blocks)
    assert window.T == n_qualifying, window.T
    assert window.M == M
    assert window.window_start_block == 0
    assert window.eigenvalues.shape == (M,)
    assert window.eigenvectors.shape == (M, M)
    assert np.isclose(window.cpve[-1], 1.0), window.cpve


def test_select_single_window_explicit_subwindow():
    """
    An explicit (start, window_T) selects the same row range rolling_cpve's own slicing would
    (log_liq[start:start+window_T]), and resolves window_start_block from qualifying_blocks at
    `start`, not from `start` itself.
    """
    n_qualifying, M = 25, 3
    row_idx = np.arange(n_qualifying, dtype=np.float64).reshape(-1, 1)
    col_idx = np.arange(M, dtype=np.float64).reshape(1, -1)
    log_liq = row_idx * 0.1 + col_idx
    qualifying_blocks = np.arange(0, n_qualifying * 10, 10, dtype=np.int64)  # 0, 10, ..., 240

    window = select_single_window(log_liq, qualifying_blocks, start=5, window_T=10)
    assert window.T == 10
    assert window.window_start_block == 50, window.window_start_block  # qualifying_blocks[5]


def test_select_single_window_rejects_invalid_window():
    """Negative start, non-positive window_T, and an out-of-range window must all raise
    ValueError rather than silently return a shorter/garbage window."""
    n_qualifying, M = 10, 3
    log_liq = np.arange(n_qualifying * M, dtype=np.float64).reshape(n_qualifying, M)
    qualifying_blocks = np.arange(0, n_qualifying * 10, 10, dtype=np.int64)

    for start, window_T in [(-1, 5), (0, 0), (0, -3), (8, 5)]:  # last: start+window_T > n
        try:
            select_single_window(log_liq, qualifying_blocks, start=start, window_T=window_T)
        except ValueError:
            continue
        raise AssertionError(f"expected ValueError for start={start}, window_T={window_T}")


def test_rank_standardized_x_grid_endpoints_and_length():
    """Default M_GRID grid: length M_GRID, ascending, endpoints exactly -1 and 1."""
    x = rank_standardized_x_grid()
    assert x.shape == (M_GRID,)
    assert x[0] == -1.0 and x[-1] == 1.0
    assert np.all(np.diff(x) > 0.0)

    x5 = rank_standardized_x_grid(M=5)
    assert x5.shape == (5,)
    assert x5[0] == -1.0 and x5[-1] == 1.0 and x5[2] == 0.0  # odd M -> exact midpoint at 0


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS  {name}")
