from dataclasses import dataclass
from pathlib import Path

# Anchor to codebase/ directory (same mechanism as data_processing/config.py)
_BASE: Path = Path(__file__).parent.parent.parent / "results"


@dataclass(frozen=True)
class Config:
    # Colours — call side (blue) / put side (red)
    C_color: str = "#1f77b4"
    P_color: str = "#d62728"
    ATM_color: str = "#2ca02c"

    # Colours — LVR / I decomposition plots
    LVR_color: str = "#2ca02c"  # green  — LVR proxy region
    hedge_color: str = "#98df8a"  # light green — hedging cost region

    # Fixed spatial window for the liquidity surface, keyed by fee tier:
    #   tick_radius = (liquidity_M // 2) * tick_spacing
    # The values are chosen so every tier lands on a comparable LOG-MONEYNESS
    # half-width, which is what makes the surfaces visually comparable across
    # fee tiers:
    #    1bp: (25000//2)*1  = 12500 raw ticks -> +/-1.25
    #    5bp: ( 2500//2)*10 = 12500 raw ticks -> +/-1.25
    #   30bp: (  500//2)*60 = 15000 raw ticks -> +/-1.50
    # (M is not literally an initialized-tick count for any tier — the 1bp pools
    # carry ~330 initialized ticks per block in total, not 12500 per side.)
    liquidity_M = {"1bp": 2500, "5bp": 1500, "30bp": 500}

    # Zoom factor for the LvsP tick window.
    # Window = [a - (b-a)*ZOOM, b + (b-a)*ZOOM] where a=min(curr_tick), b=max(curr_tick).
    ZOOM: float = 1.1

    # Default x-axis limits for liquidity profile plots (log-moneyness)
    l_x_min: float = -0.2
    l_x_max: float = 0.2

    # Default x-axis limits for IL and IL-price plots (log-moneyness)
    il_x_min: float = -0.2
    il_x_max: float = 0.2

    # Default x-axis limits for IV plots (log-moneyness)
    iv_x_min: float = -0.2
    iv_x_max: float = 0.2

    # Output directories (anchored to codebase/results/)
    liq_out_dir: Path = _BASE / "liquidity-pipeline"
    IL_out_dir: Path = _BASE / "impermanent-loss"
    IL_price_out_dir: Path = _BASE / "priced-impermanent-loss"
    iv_out_dir: Path = _BASE / "implied-volatility"

    # Output directory for the marginal price-impact plots (cycle 2).
    impact_out_dir: Path = _BASE / "price-impact"

    # Output directory for the CEV shape-elasticity diagnostics (cycle 3).
    cev_out_dir: Path = _BASE / "cev-elasticity"

    # Output directory for the R5 LVR-consequence results (cycle 3, checkpoint 4).
    lvr_out_dir: Path = _BASE / "cev-elasticity" / "lvr"

    # Output directory for the cycle-4 functional-PCA / CPVE results.
    fpca_out_dir: Path = _BASE / "liquidity-pipeline" / "functional-pca"


CFG = Config()
