---
title: Intrinsic Liquidity
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Intrinsic Liquidity

A reparametrization-invariant measure of local liquidity for a CFMM, defined from the geometry of the bonding curve rather than from any particular coordinate or invariant scaling. It captures "how much depth" the pool offers at a given price independent of how the curve is written down.

## Details
- Motivation: the invariant constant L and the raw reserves depend on how f is parametrized (e.g. sqrt(xy) vs xy give different L), so they are not intrinsic. A coordinate-free quantity is needed to compare designs.
- Defined via the curvature κ of the bonding curve at the operating point; intrinsic liquidity is essentially the inverse hyperbolic curvature — large where the curve is flat (deep book) and small where it is sharply bent (thin book).
- It ties marginal liquidity (slope of the demand curve dx/dP) to the geometric curvature, giving the quantity that enters slippage, LVR, and value-function second derivatives in a parametrization-free way.
- Provides the natural local scale for the liquidity profile L(p): concentrated liquidity is, in this language, a locally boosted intrinsic liquidity over a chosen price band.

## Appears in
- [[source-rtw26-cfmm-liquidity-pricing-hedging]] — uses a curvature/intrinsic notion of liquidity to price and hedge LP positions.
- [[source-wang-math-in-amm]] — formalizes intrinsic liquidity as the reparametrization-invariant curvature quantity.

## Related
- [[concept-bonding-curve]] — curvature of this curve defines intrinsic liquidity.
- [[concept-liquidity-profile]] — the price-indexed distribution built on intrinsic liquidity.
- [[concept-concentrated-liquidity]] — local amplification of intrinsic liquidity over a range.
- [[concept-loss-versus-rebalancing]] — LVR scales with local liquidity / curvature.
- [[concept-constant-function-market-maker]] — the object whose liquidity is being measured.
