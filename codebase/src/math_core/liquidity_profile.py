import numpy as np
import pandas as pd
from typing import Optional

from .config import CFG as _MATH_CFG

# ———————————————————————————————————————————————————————————————————————————————————————————— #
"""
Note on the following function:
After DECIMAL_ADJ normalization in reconstruct_liquidity_cumsum, ℓ values are ∼10⁷ —
well within float64's exact integer range (2⁵³ ≈ 9×10¹⁵).
"""


def piecewise_constant_liquidity_profile(
    liq_df: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Extract the piecewise-constant intrinsic liquidity ℓ(q) from tick data.

    ℓ(q) = liq_df["liquidity"]  on each interval [price_lower, price_upper].
    Rows with zero liquidity are dropped: they contribute nothing to the integral
    and would produce a 0/√q division in the antiderivative.

    Args:
        liq_df: output of reconstruct_liquidity_cumsum.
                Required columns: price_lower, price_upper, liquidity.
    Returns:
        q_lower [np.ndarray]: left  endpoints of tick intervals (ascending).
        q_upper [np.ndarray]: right endpoints of tick intervals (ascending).
        ell     [np.ndarray]: intrinsic liquidity ℓ on each interval (float64).
    """
    # Filter out zero-liquidity rows and sort by price_lower.
    active = liq_df[liq_df["liquidity"] > 0].sort_values("price_lower")

    q_lower = active["price_lower"].to_numpy(dtype=float)
    q_upper = active["price_upper"].to_numpy(dtype=float)
    ell = active["liquidity"].to_numpy(dtype=float)
    return q_lower, q_upper, ell


# ———————————————————————————————————————————————————————————————————————————————————————————— #


def _select_rank_standardized_row_filled(
    tick_idx: np.ndarray,
    liquidity: np.ndarray,
    curr_tick: int,
    M: int,
) -> np.ndarray:
    """
    One block's rank-standardized liquidity row (raw, not log-transformed), NaN-filled rather
    than dropped -- the fill-not-drop counterpart to
    functional_pca._select_rank_standardized_row (same anchor convention, same nearest-rank
    walk), used only by the relative-tick branch of build_liquidity_surface below.

    Anchor convention (matches functional_pca.py and clean_parquet.py): the position, in this
    block's own ascending tick_idx array, of the last initialized tick at or before curr_tick.
    From there, walk M//2 rank positions each side. Unlike the FPCA helper, a side that runs out
    of initialized ticks before reaching M//2 positions is left NaN instead of disqualifying the
    whole row, and a non-positive/non-finite selected value is NaN'd in place rather than
    rejecting the row -- so every block that has at least one initialized tick contributes a row,
    fully NaN only in the (rare, per the anchor's own search) case of zero initialized ticks.
    Column j is consistently "the j-th nearest-rank tick to this block's own anchor" when that
    rank position exists in this block, NaN when it doesn't. The caller applies the log-transform
    uniformly afterward, matching the log-moneyness branch's own convention.

    Args:
        tick_idx : (n,) this block's initialized tick indices, any order.
        liquidity: (n,) matching reconstructed liquidity values.
        curr_tick: pool's current tick for this block.
        M        : window width -- (M-1)//2 ticks on each side of the anchor; forced odd if
                   given even (mirrors build_qualifying_matrix's own fixup).
    Returns:
        (M,) raw liquidity row, ascending tick order (column 0 = lowest tick = furthest below
        the anchor, column M-1 = highest tick = furthest above). NaN where the rank position is
        unavailable in this block or the value there is non-positive/non-finite.
    """
    if M % 2 == 0:  # mirrors build_qualifying_matrix: half = (M-1)//2 only yields M elements for odd M
        M += 1
    half = (M - 1) // 2

    n = tick_idx.shape[0]
    if n == 0:
        return np.full(M, np.nan, dtype=np.float64)

    order = np.argsort(tick_idx, kind="stable")
    tick_sorted = tick_idx[order]
    liq_sorted = liquidity[order]

    anchor_pos = int(tick_sorted.searchsorted(curr_tick, side="right")) - 1

    positions = anchor_pos + np.arange(-half, half + 1)
    in_bounds = (positions >= 0) & (positions < n)
    safe_pos = np.clip(positions, 0, n - 1)
    vals = liq_sorted[safe_pos]
    valid = in_bounds & np.isfinite(vals) & (vals > 0.0)
    return np.where(valid, vals, np.nan)


# ———————————————————————————————————————————————————————————————————————————————————————————— #


def build_liquidity_surface(
    df: pd.DataFrame,
    tick_radius: int = 10000,
    n_time_samples: int = 200,
    log_scale_offset: float = 0.0,
    use_log_moneyness: bool = True,
    relative_tick_M: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Build a 2D log-liquidity surface from multi-block processed tick data.

    For each block, curr_tick is read from the 'curr_tick' column produced by
    clean_parquet.py (pool slot0 tick).  All tick indices are expressed relative
    to curr_tick and converted to log-moneyness:
        log_moneyness = rel_tick × log(1.0001)
    centring the liquidity profile at 0 (ATM) for every block.

    The surface is a regular grid:
        rows  — time, one per (downsampled) block, normalized to [0, 1].
        cols  — log-moneyness in [-tick_radius×log(1.0001),
                                   +tick_radius×log(1.0001)].

    Args:
        df             : processed parquet DataFrame with columns
                         [block_number, tick_idx, liquidity, curr_tick]
                         (output of clean_parquet).
        tick_radius    : half-width of the display window in raw tick units
                         (default ±10000 ≈ ±1.0 log-moneyness).
                         Ticks with |tick_idx − curr_tick| > tick_radius are
                         excluded.
        n_time_samples : number of evenly-spaced time slices to retain after
                         downsampling (default 200).
        tick_spacing   : fee-tier tick spacing (10 for 5 bp, 60 for 30 bp).
                         Stored in the output docstring for reference; the
                         x-axis conversion uses log(1.0001) regardless.
        log_scale_offset : additive offset applied to log_liq before returning
                         (default 0.0).  Pass np.log(1e12) to match the paper's
                         un-normalized y-scale.
        use_log_moneyness: if True (default), convert the x-axis to log-moneyness
                         log(K/S) = −rel_tick × log(1.0001), sorted ascending.
                         If False, use the rank-standardized construction below instead of a
                         geometric tick_radius grid -- tick_radius is unused in that case.
        relative_tick_M  : required when use_log_moneyness=False; ignored otherwise. Rank
                         window width -- (M-1)//2 nearest-rank initialized ticks each side of
                         the block's own anchor (Appendix B), not a raw tick-distance radius.
                         See _select_rank_standardized_row_filled.
    Returns:
        x_axis        : 1-D float64 array.  Log-moneyness ≈ [−1.0, +1.0] when
                        use_log_moneyness=True; rank-standardized axis affine-mapped to
                        [−1.0, +1.0] (column j = j-th nearest-rank tick to each block's own
                        anchor, not a shared geometric position) when False.
        times         : 1-D float64 array of normalized time values in [0, 1].
        log_liq       : 2-D float64 array (n_time × n_ticks) of ln(liquidity)
                        + log_scale_offset.  Cells with no tick data are NaN.
        sampled_blocks: 1-D int64 array of the actual Ethereum block numbers
                        corresponding to each row of log_liq / times.  Pass
                        this together with a block → timestamp Series to the
                        plot functions to enable calendar-month axis labels.
    """
    if "curr_tick" not in df.columns:
        raise ValueError(
            "'curr_tick' column missing from df — re-run "
            "src/data_processing/liquidity/clean_parquet.py"
        )

    _LOG1P = np.log(1.0001)
    N_GRID = _MATH_CFG.N_GRID

    # ── Fixed x-axis grid (same for every block) ──────────────────────────────
    # x_max is derived from tick_radius so both fee tiers are handled correctly:
    #   5bp:  tick_radius=12500 → x_max ≈ 1.25
    #   30bp: tick_radius=15000 → x_max ≈ 1.50
    # Sign convention: log(K/S) = (curr_tick − tick_idx) × log(1.0001),
    # so negative x = OTM puts (tick_idx > curr_tick), positive x = OTM calls.
    if use_log_moneyness:
        x_max = tick_radius * _LOG1P
        x_grid = np.linspace(-x_max, x_max, N_GRID)   # ascending log(K/S)
        n_cols = N_GRID
    else:
        if relative_tick_M is None:
            raise ValueError(
                "build_liquidity_surface: relative_tick_M is required when "
                "use_log_moneyness=False -- the rank-standardized construction has no fixed "
                "geometric tick_radius grid to fall back on."
            )
        rank_M = relative_tick_M + 1 if relative_tick_M % 2 == 0 else relative_tick_M
        x_grid = np.linspace(-1.0, 1.0, rank_M)   # rank-affine, not tick distance
        n_cols = rank_M

    # ── Read curr_tick per block ───────────────────────────────────────────────
    curr_tick_map = df.groupby("block_number")["curr_tick"].first()

    # ── Downsample block list ─────────────────────────────────────────────────
    all_blocks = np.sort(curr_tick_map.index.to_numpy())
    n_blocks = len(all_blocks)
    if n_blocks > n_time_samples:
        step = n_blocks / n_time_samples
        keep_idx = np.unique(np.round(np.arange(0, n_blocks, step)).astype(int))
        keep_idx = keep_idx[keep_idx < n_blocks]
        sampled_blocks = all_blocks[keep_idx]
    else:
        sampled_blocks = all_blocks

    # ── Normalize time axis to [0, 1] ─────────────────────────────────────────
    blocks_f = sampled_blocks.astype(float)
    times = (blocks_f - blocks_f.min()) / (blocks_f.max() - blocks_f.min())

    # ── Build dense surface row by row ────────────────────────────────────────
    rows: list[np.ndarray] = []

    for block in sampled_blocks:
        curr_tick = int(curr_tick_map.loc[block])

        blk = df.loc[df["block_number"] == block, ["tick_idx", "liquidity"]]

        if use_log_moneyness:
            blk = blk[(blk["tick_idx"] - curr_tick).abs() <= tick_radius].sort_values("tick_idx")

            if blk.empty:
                rows.append(np.full(n_cols, np.nan))
                continue

            tick_array = blk["tick_idx"].to_numpy(dtype=np.int64)
            liq_array = blk["liquidity"].to_numpy(dtype=np.float64)

            # Convert each grid point to an absolute tick query.
            # log(K/S) = (curr_tick − tick_idx) × LOG1P  →  tick_idx = curr_tick − x / LOG1P
            query = curr_tick - x_grid / _LOG1P

            # Piecewise-constant lookup: find the last initialized tick ≤ query.
            # searchsorted side="right" then -1 gives the active liquidity bin.
            i = np.searchsorted(tick_array, query, side="right") - 1

            valid = (i >= 0) & (i < len(tick_array))
            row = np.where(valid, liq_array[np.clip(i, 0, len(tick_array) - 1)], np.nan)
            row = np.where(row > 0, row, np.nan)   # guard against zero/negative ℓ
            rows.append(row)
        else:
            # Rank-standardized, fill-not-drop: no geometric pre-filter -- the walk goes
            # straight against this block's full initialized-tick set (see
            # _select_rank_standardized_row_filled).
            tick_array = blk["tick_idx"].to_numpy(dtype=np.int64)
            liq_array = blk["liquidity"].to_numpy(dtype=np.float64)
            row = _select_rank_standardized_row_filled(tick_array, liq_array, curr_tick, M=n_cols)
            rows.append(row)

    # ── Stack and log-transform ───────────────────────────────────────────────
    liq_values = np.vstack(rows)                       # (n_time, n_cols)
    log_liq    = np.log(liq_values) + log_scale_offset  # NaN propagates

    return x_grid, times, log_liq, sampled_blocks
