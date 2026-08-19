---
title: Impermanent Loss
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Impermanent Loss (IL)

The shortfall of a liquidity provider's pool value relative to simply holding the initial basket of assets: IL = V_pool − V_hold (loss-versus-holding). It is non-positive whenever the price moves and reflects the convexity (concavity of V) of the CFMM value function. It is "impermanent" because it reverts to zero if the price returns to its starting level.

## Details
- Definition: at price P, IL(P) = V(P) − (P·x₀ + y₀), where (x₀, y₀) is the initial (held) basket; ≤ 0 for any P ≠ P₀ under a convex CFMM.
- CPMM closed form: for a price ratio move r = P/P₀, IL fraction = 2·sqrt(r)/(1+r) − 1 ≤ 0 (e.g. −5.7% at a 2× move).
- Under a martingale (risk-neutral) price process, the expected IL is non-negative as a cost — it equals, in expectation, the loss-versus-rebalancing benchmark plus a mean-zero market-risk term.
- Path independence vs. dependence: IL depends only on the current price (state function), whereas LVR is a running, path-dependent integral. IL can revert; realized LVR cannot.
- Concentrated positions amplify IL within their range because liquidity — and hence value curvature — is locally larger.

## Appears in
- [[source-amm-loss-versus-rebalancing]] — contrasts IL (loss-versus-holding) with the LVR benchmark.
- [[source-quantifying-loss-in-amms]] — decomposes LP loss including the IL component.
- [[source-clmm-mathematical-framework]] — IL for concentrated positions.
- [[source-bis-decentralized-dealers]] — IL as the cost dealers bear.
- [[source-wang-math-in-amm]] — IL from value-function convexity.
- [[source-wang-bocconi-1]] — introductory treatment of IL.
- [[source-rtw26-cfmm-liquidity-pricing-hedging]] — IL priced via the option-replication view.

## Related
- [[concept-loss-versus-rebalancing]] — the running-cost counterpart; equals IL in expectation under a martingale.
- [[concept-rebalancing-strategy]] — alternative benchmark to holding.
- [[concept-lp-pnl-decomposition]] — IL/rebalancing terms net against fees.
- [[concept-reserve-option-duality]] — IL as a short-option (short-gamma) payoff.
- [[concept-constant-product-market-maker]] — cleanest IL closed form.
- [[concept-concentrated-liquidity]] — amplifies IL in-range.
- [[concept-adverse-selection]] — economic source of the loss.
