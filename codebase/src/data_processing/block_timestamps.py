"""
block_timestamps.py
-------------------
Loader utility for the persisted block → UTC timestamp lookup table produced
by fetch_block_timestamps.py.

Public API
----------
load_block_timestamps(path) -> pd.Series
    Returns a pd.Series indexed by block_number (int64) with UTC pd.Timestamp
    values.  Pass this directly to the block_ts parameter of any plot function.
"""

from pathlib import Path

import pandas as pd

_REPO_ROOT    = Path(__file__).resolve().parent.parent.parent  # codebase/
_DEFAULT_PATH = _REPO_ROOT / "data" / "block_timestamps.parquet"


def load_block_timestamps(path: Path | None = None) -> pd.Series:
    """
    Load the block → UTC timestamp lookup as a pd.Series.

    Args:
        path : path to block_timestamps.parquet.
               None → codebase/data/block_timestamps.parquet (default).
    Returns:
        pd.Series[datetime64[ns, UTC]] indexed by block_number (int64).
        Example usage:
            block_ts = load_block_timestamps()
            ts = block_ts.loc[22_224_860]   # → Timestamp('2024-01-05 ...', tz='UTC')
    Raises:
        FileNotFoundError if the parquet does not exist.  Run
        fetch_block_timestamps.py first.
    """
    p = Path(path) if path is not None else _DEFAULT_PATH
    if not p.exists():
        raise FileNotFoundError(
            f"Block timestamp file not found:\n  {p}\n"
            "Run:  python codebase/src/data_processing/fetch_block_timestamps.py"
        )
    df = pd.read_parquet(p)
    return df.set_index("block_number")["timestamp"]
