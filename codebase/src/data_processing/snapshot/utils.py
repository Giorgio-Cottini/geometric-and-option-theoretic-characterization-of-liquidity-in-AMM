import numpy as np
import pandas as pd
import json
from .config import CFG

# ———————————————————————————————————————————————————————————————————————————————————————————— #
# Data loaders  (no processing logic)


def load_ticks(fee_bps: int) -> list[dict]:
    """Concatenate all paginated tick files for a given fee tier."""
    tag = f"eth_usdc_{fee_bps}bp"
    ticks: list[dict] = []
    i = 0
    while True:
        path = CFG.data_raw_path / "liquidity" / f"{tag}_ticks_page{i}.json"
        if not path.exists():
            break
        with open(path) as f:
            ticks.extend(json.load(f)["data"]["ticks"])
        i += 1
    return ticks


def load_pool_state(fee_bps: int) -> dict:
    """Load the single pool state snapshot for a given fee tier."""
    path = CFG.data_raw_path / "liquidity" / f"eth_usdc_{fee_bps}bp_pool_state.json"
    with open(path) as f:
        return json.load(f)["data"]["pool"]


def load_options_book() -> list[dict]:
    """Load the single options snapshot from data/raw/options/."""
    files = sorted((CFG.data_raw_path / "options").glob("*.json"))
    assert len(files) == 1, f"Expected 1 options file, found {len(files)}: {files}"
    with open(files[0]) as f:
        return json.load(f)["result"]


# ———————————————————————————————————————————————————————————————————————————————————————————— #
# Nice looking separator


def _sep(length=70) -> None:
    print("\n" + "—" * length)


# ———————————————————————————————————————————————————————————————————————————————————————————— #
