---
title: Uniswap V3 Ticks
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Uniswap v3 Ticks

Ticks are the discretization of price space in Uniswap v3, where each tick index i corresponds to a price P(i) = 1.0001^i. Liquidity providers deposit into ranges bounded by ticks, and total pool liquidity at any price equals the sum of the per-range positions active there.

## Details
- Price at tick i: P(i) = 1.0001^i, so consecutive ticks differ by one basis point in price.
- LP positions are opened between a lower and upper tick, providing liquidity only while the price stays inside that range.
- Range endpoints must be multiples of the tick spacing, which is set per fee tier (larger spacing for higher-fee, more volatile pools).
- The active (in-range) liquidity at a given price is the sum over all positions whose range straddles that price.
- This per-range aggregation produces a piecewise-constant liquidity profile across the tick axis — the object sampled to build the liquidity surface.
- Ticks make the price axis discrete and finite-support, which is what allows liquidity to be concentrated rather than spread uniformly as in a constant-product pool.

## Appears in
- [[source-liquidity-surfaces-uniswap-v3]] — uses the tick grid as the x-axis over which the liquidity surface is sampled and reconstructed.
- [[source-rtw26-cfmm-liquidity-pricing-hedging]] — builds pricing and hedging results on the tick-based concentrated-liquidity structure of CFMMs.

## Related
- [[concept-concentrated-liquidity]] — the feature ticks enable: LPs place capital in bounded ranges rather than the whole curve.
- [[concept-liquidity-profile]] — the piecewise-constant profile formed by summing per-tick-range positions.
- [[concept-liquidity-surface]] — the tick-indexed cross-sections stacked over block-time.
- [[concept-constant-product-market-maker]] — the v2 baseline whose single continuous curve ticks discretize and refine.
- [[entity-uniswap-v3]] — the protocol that introduced tick-based concentrated liquidity.
