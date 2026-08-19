"""
Execution order (mirrors section 5 of the paper):

  Liquidity sub-pipeline:
    load_ticks -> load_pool_state -> reconstruct_liquidity_cumsum

  Options sub-pipeline (per expiry):
    load_options_book -> process_options -> [per expiry]
    arbitrage_filter -> fill_ITM_gaps -> linear_interpolation

  IL price (eq. 18):
    run_IL_pipeline(liq_df, opt_res, P0, fee_bps, expiry) -> Π^IL

  Graphs saved to (directories configured in src/graphics/config.py):
    results/l/           (liquidity profile plots)
    results/IL/          (pathwise IL plots)
    results/price_IL/    (IL price integrand plots)

Run:  python codebase/tester.py           (from repo root)
      or:  python tester.py               (from codebase/)
"""

import matplotlib

matplotlib.use("Agg")  # non-interactive backend — must precede pyplot import

from src.data_processing import (
    _sep,
    load_pool_state,
    run_liquidity_pipeline,
    run_options_pipeline,
)
from src.math_core import (
    run_IL_pipeline,
    compute_BS_implied_vol,
    compute_BS_iv_fine_structure,
)
from src.graphics import (
    plot_IL,
    plot_IL_price,
    plot_IL_LVR,
    plot_IL_price_I,
    plot_liq,
    plot_iv,
)
from src.graphics.config import CFG as GRAPHICS_CFG

# ————————————————————————————————————————————————————————————————————————— #


def main(
    expiries: list[str] | None = None,
    il_x_min: float | None = GRAPHICS_CFG.il_x_min,
    il_x_max: float | None = GRAPHICS_CFG.il_x_max,
) -> None:
    """
    Run the full RTW26 replication pipeline for multiple expiries.

    Args:
        expiries : list of Deribit expiry labels, e.g. ["25SEP26", "25DEC26"].
                   Defaults to ["25SEP26", "25DEC26"] when None.
        il_x_min : left  x-axis limit for IL plots (log-moneyness).  None = auto.
        il_x_max : right x-axis limit for IL plots (log-moneyness).  None = auto.
    """
    if expiries is None:
        expiries = ["27MAR26", "26JUN26", "25SEP26", "25DEC26"]

    _sep()
    print("RTW26 REPLICATION — FULL PREPROCESSING PIPELINE")
    _sep()

    # --- Liquidity ---
    liq_5bp = run_liquidity_pipeline(fee_bps=5)
    liq_30bp = run_liquidity_pipeline(fee_bps=30)
    spot_P0 = float(load_pool_state(fee_bps=5)["token0Price"])

    # --- Options ---
    opt_res = run_options_pipeline(spot=spot_P0)

    # --- Build expiries_F: filter out any expiry missing from option data ---
    expiries_F: list[tuple[str, float]] = []
    for exp in expiries:
        if exp not in opt_res:
            print(f"[WARN] expiry '{exp}' not found in option data — skipped.")
            continue
        F = float(opt_res[exp]["filled"]["forward"].iloc[0])
        expiries_F.append((exp, F))

    if not expiries_F:
        available = sorted(opt_res.keys())
        print(f"[ERROR] No valid expiries. Available: {available}")
        return

    # --- Fee-tier inputs ---
    liq_inputs = [
        (liq_5bp, "5bp", 5),
        (liq_30bp, "30bp", 30),
    ]

    # --- IL replication prices (per fee tier, per expiry) ---
    il_per_tier: dict[str, list[dict | None]] = {}
    for liq_df, fee_label, fee_bps in liq_inputs:
        il_per_tier[fee_label] = [
            run_IL_pipeline(liq_df, opt_res, spot_P0, fee_bps=fee_bps, expiry=exp)
            for exp, _ in expiries_F
        ]

    # --- Liquidity profile plots ---
    _sep()
    print("LIQUIDITY PROFILE PLOTS")
    for liq_df, fee_label, _ in liq_inputs:
        plot_liq(
            liq_df,
            fee_label,
            spot_P0,
            expiries_F,
            x_min=il_x_min,
            x_max=il_x_max,
        )

    # --- Pathwise IL plots ---
    _sep()
    print("IMPERMANENT LOSS PLOTS")
    for liq_df, fee_label, _ in liq_inputs:
        plot_IL(
            liq_df,
            fee_label,
            spot_P0,
            il_per_tier[fee_label],
            expiries_F,
            x_min=il_x_min,
            x_max=il_x_max,
        )

    # --- IL price integrand plots ---
    _sep()
    print("IL PRICE INTEGRAND PLOTS")
    for liq_df, fee_label, _ in liq_inputs:
        plot_IL_price(
            liq_df,
            fee_label,
            spot_P0,
            il_per_tier[fee_label],
            expiries_F,
            opt_res,
            x_min=il_x_min,
            x_max=il_x_max,
        )

    # --- IL decomposition: LVR + hedging cost ---
    _sep()
    print("IL LVR DECOMPOSITION PLOTS")
    for liq_df, fee_label, _ in liq_inputs:
        plot_IL_LVR(
            liq_df,
            fee_label,
            spot_P0,
            expiries_F,
            il_results=il_per_tier[fee_label],
            x_min=il_x_min,
            x_max=il_x_max,
        )

    # --- IL price decomposition: LVR price + I remainder ---
    _sep()
    print("IL PRICE I-DECOMPOSITION PLOTS")
    for liq_df, fee_label, _ in liq_inputs:
        plot_IL_price_I(
            liq_df,
            fee_label,
            spot_P0,
            il_per_tier[fee_label],
            expiries_F,
            opt_res,
            x_min=il_x_min,
            x_max=il_x_max,
        )

    # --- Implied Volatility (BS) ---
    _sep()
    print("IMPLIED VOLATILITY (BS)")
    iv_per_tier: dict[str, list[dict]] = {}
    for liq_df, fee_label, fee_bps in liq_inputs:
        iv_list: list[dict] = []
        for exp, F in expiries_F:
            T = opt_res[exp]["T"]
            iv_fine = compute_BS_iv_fine_structure(
                liq_df, opt_res[exp]["interp"], F, T, spot_P0
            )
            iv_agg = compute_BS_implied_vol(
                liq_df, opt_res[exp]["interp"], F, T, spot_P0
            )
            iv_fine["sigma_BS_agg"] = iv_agg["sigma_BS"]
            iv_list.append(iv_fine)
            print(
                f"  [{fee_label:>4s}, {exp}]  σ_BS = {iv_agg['sigma_BS']:.4f}  "
                f"({iv_fine['converged'].sum()}/{len(iv_fine['converged'])} ticks converged)"
            )
        iv_per_tier[fee_label] = iv_list

    # --- IV plots ---
    _sep()
    print("IMPLIED VOLATILITY PLOTS")
    for liq_df, fee_label, _ in liq_inputs:
        plot_iv(
            liq_df,
            fee_label,
            spot_P0,
            iv_per_tier[fee_label],
            expiries_F,
        )

    # --- Summary ---
    _sep()
    print("PIPELINE SUMMARY")
    print(f"  Expiries processed  : {[exp for exp, _ in expiries_F]}")
    for fee_label, il_list in il_per_tier.items():
        for (exp, F), il in zip(expiries_F, il_list):
            if il is not None:
                print(
                    f"  Π^IL [{fee_label:>4s}, {exp}] : "
                    f"{il['IL_price']:>16.4f} USD  "
                    f"(put {il['put_total']:.4f} + call {il['call_total']:.4f})"
                )
    _sep()


if __name__ == "__main__":
    main()
