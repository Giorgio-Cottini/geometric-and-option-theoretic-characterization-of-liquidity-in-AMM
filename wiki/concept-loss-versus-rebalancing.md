---
title: Loss Versus Rebalancing
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Loss-Versus-Rebalancing (LVR)

The adverse-selection cost a passive CFMM liquidity provider incurs because arbitrageurs trade against stale AMM quotes whenever the external price moves. It is the performance gap between the AMM LP and a rebalancing strategy that holds the same risky position but trades at the true market price. LVR is non-negative, non-decreasing, and predictable — a "Black–Scholes formula for AMMs".

## Details
- Instantaneous LVR: ℓ(P) = (1/2)·σ²·P²·(−V''(P)) ≥ 0, equivalently dLVR = −(1/2)·V''(P) d⟨P⟩, where ⟨P⟩ is the quadratic variation of price and V is the pool value function (V is concave, so −V'' ≥ 0).
- Depends only on instantaneous price variance and marginal liquidity (slope of the demand curve) at the current price — it grows with volatility and with how aggressively the AMM trades.
- Cumulative LVR_t = ∫₀ᵗ ℓ(P_s) ds is monotone and predictable; unlike impermanent loss it does not revert.
- Once market risk is hedged (short the rebalancing strategy), LP P&L = trading fee income − LVR, isolating the economic cost of providing liquidity.
- In expectation under a martingale price, LVR coincides with expected impermanent loss; it is the unique benchmark that removes market-risk differences.

## Appears in
- [[source-amm-loss-versus-rebalancing]] — the paper that introduces and derives LVR.
- [[source-quantifying-loss-in-amms]] — workshop version quantifying the same loss.
- [[source-amm-arbitrage-profits-fees]] — LVR rescaled by a probability-of-trade once fees are added.
- [[source-clmm-mathematical-framework]] — LVR for concentrated positions.
- [[source-wang-math-in-amm]] — LVR from value-function curvature.
- [[source-wang-bocconi-1]] — lecture derivation of LVR.
- [[source-rtw26-cfmm-liquidity-pricing-hedging]] — LVR within the pricing/hedging framework.

## Related
- [[concept-rebalancing-strategy]] — the benchmark LVR is measured against.
- [[concept-impermanent-loss]] — equals LVR in expectation under a martingale price.
- [[concept-adverse-selection]] — the economic mechanism generating LVR.
- [[concept-arbitrage-with-fees]] — fees introduce a no-trade region that rescales LVR.
- [[concept-lp-pnl-decomposition]] — LVR is the negative term in LP P&L.
- [[concept-reserve-option-duality]] — LVR as the cost of the embedded short gamma.
- [[concept-intrinsic-liquidity]] — local liquidity that scales LVR.
- [[entity-jason-milionis]] — co-author of the LVR framework.
- [[entity-ciamac-moallemi]] — co-author.
- [[entity-tim-roughgarden]] — co-author.
- [[entity-anthony-lee-zhang]] — co-author.
- [[concept-predictable-loss]] — the concentrated-liquidity sibling of this cost, which adds the
  opportunity cost of capital confined to a range.
- [[concept-optimal-liquidity-provision]] — the problem of choosing a profile to trade this cost
  against fee income.
- [[concept-optimal-range-width]] — the closed-form width that results from making that tradeoff.
- [[machine-prose-and-the-thesis-wiki]] — cites this page as the measured instance of the prose
  rule this region does not yet meet.
