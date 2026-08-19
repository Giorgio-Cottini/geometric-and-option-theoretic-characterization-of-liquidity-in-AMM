---
title: Rebalancing Strategy
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Rebalancing Strategy

A self-financing trading strategy that holds, at every instant, the same risky-asset position as a CFMM liquidity provider, but executes its trades at the external market (CEX) price rather than at the AMM's stale quote. It is the benchmark against which loss-versus-rebalancing is measured; shorting it delta-hedges the LP position.

## Details
- Construction: mirror the AMM's risky holding x*(P) as the market price P moves, financing every adjustment at the true price P (no slippage, no stale quote).
- Value dynamics: R_t = V₀ + ∫₀ᵗ x*(P_s) dP_s — a stochastic integral of the AMM's position against the price process.
- LVR_t = R_t − V_t is the gap between this rebalancing portfolio and the actual pool value; it is exactly what arbitrageurs extract by trading at the stale AMM price.
- Hedging use: an LP who shorts the rebalancing strategy cancels the market-risk (delta) component, leaving P&L = fee income − LVR. Empirically the hedged P&L has only ~1%–6% of the standard deviation of the unhedged LP return, showing most LP variance is plain market exposure.

## Appears in
- [[source-amm-loss-versus-rebalancing]] — defines the rebalancing strategy and uses it to derive and empirically validate LVR.

## Related
- [[concept-loss-versus-rebalancing]] — defined as LP value minus the rebalancing strategy.
- [[concept-impermanent-loss]] — a different (hold) benchmark for LP performance.
- [[concept-adverse-selection]] — the loss the rebalancing benchmark isolates.
- [[concept-lp-pnl-decomposition]] — rebalancing P&L is the leading term.
- [[concept-stochastic-control]] — hedging and rebalancing as a control problem.
- [[concept-constant-function-market-maker]] — the LP position being mirrored.
- [[entity-jason-milionis]] — co-author of the framework.
- [[entity-ciamac-moallemi]] — co-author.
