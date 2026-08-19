---
title: Concentrated Liquidity
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Concentrated Liquidity

A CFMM design (Uniswap v3 / concentrated liquidity market maker, CLMM) in which each LP allocates capital to a chosen finite price range [p_a, p_b] rather than the whole (0, ∞) axis. Within its range a position behaves like a constant-product pool; outside it holds a single asset. Concentration raises capital efficiency for a given depth.

## Details
- A position with liquidity L active on [p_a, p_b] provides the same marginal depth as a full-range CPMM using far less capital, because reserves are only committed where they can trade.
- Reserves for a position at price p ∈ [p_a, p_b]: x = L(1/sqrt(p) − 1/sqrt(p_b)), y = L(sqrt(p) − sqrt(p_a)); the position is fully in y at p ≥ p_b and fully in x at p ≤ p_a.
- Range boundaries are discretized into ticks (price = 1.0001^i), and the aggregate pool is the superposition of many overlapping positions — a liquidity profile L(p).
- Trade-off: higher fee income per dollar while in range, but no fees and full inventory exposure when price leaves the range, plus concentrated impermanent loss and LVR.

## Appears in
- [[source-clmm-mathematical-framework]] — the mathematical framework for concentrated / per-tick liquidity.
- [[source-liquidity-surfaces-uniswap-v3]] — empirical liquidity surfaces built from v3 concentrated positions.
- [[source-bis-decentralized-dealers]] — v3 LPs analysed as decentralized dealers choosing ranges.
- [[source-wang-math-in-amm]] — concentrated liquidity as a locally amplified liquidity profile.
- [[source-wang-bocconi-2]] — advanced lecture on concentrated liquidity and profiles.
- [[source-rtw26-cfmm-liquidity-pricing-hedging]] — pricing/hedging of concentrated LP positions.

## Related
- [[concept-constant-function-market-maker]] — CLMM is a CFMM restricted to a range.
- [[concept-constant-product-market-maker]] — in-range behaviour matches a CPMM.
- [[concept-liquidity-profile]] — aggregate of concentrated positions over price.
- [[concept-uniswap-v3-ticks]] — the discretized range boundaries.
- [[concept-liquidity-surface]] — liquidity profile through time.
- [[concept-impermanent-loss]] — concentrated and amplified within a range.
- [[concept-loss-versus-rebalancing]] — magnified by concentration.
- [[concept-just-in-time-liquidity]] — extreme single-block concentration.
- [[entity-uniswap-v3]] — the reference CLMM.
- [[concept-liquidity-pipeline-code]] — how the codebase reconstructs and plots `ℓ(q)`.
