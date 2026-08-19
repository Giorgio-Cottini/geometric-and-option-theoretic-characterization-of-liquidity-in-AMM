from dataclasses import dataclass, field
from typing import Dict
from pathlib import Path


@dataclass(frozen=True)
class Config:
    tick_spacing: Dict[int, int] = field(default_factory=lambda: {5: 10, 30: 60})
    decimal_adj: float = 1e12
    max_price_ratio: float = 100.0
    data_raw_path: Path = (
        Path(__file__).parent.parent.parent.parent / "data" / "raw" / "snapshot"
    )


CFG = Config()
