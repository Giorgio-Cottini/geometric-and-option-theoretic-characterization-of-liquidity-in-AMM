from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # Number of evenly-spaced points on the fixed x-axis grid used by
    # build_liquidity_surface. Controls spatial resolution of the surface.
    N_GRID: int = 500


CFG = Config()
