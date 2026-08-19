---
title: Bonding Curve
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Bonding Curve

The level set of reserves f(x, y) = L that a CFMM must stay on. Trades slide the reserve point along this curve, and its local slope gives the marginal (spot) price. The shape of the curve fully characterizes a CFMM's pricing and liquidity.

## Details
- Curve: {(x, y) : f(x, y) = L} in reserve space; monotone decreasing and (for standard CFMMs) convex.
- Marginal price: P = −dy/dx = f_x / f_y along the curve; moving along the curve traces the demand schedule.
- Curvature of the curve encodes how quickly price moves per unit traded — i.e. slippage / marginal liquidity. A flatter curve (near constant-sum) means deeper liquidity locally; a more curved one means thinner.
- Examples: hyperbola xy = k (CPMM), weighted-power x^w y^(1−w) = L (G3M), line x + y = k (constant sum).
- Reparametrizing the curve does not change its intrinsic geometry — the invariant local quantity is captured by the inverse of the curvature (see intrinsic liquidity).

## Appears in
- [[source-clmm-mathematical-framework]] — bonding curve segmented per tick to build concentrated liquidity.
- [[source-wang-math-in-amm]] — treats the bonding curve as the primitive object from which price and liquidity are derived.

## Related
- [[concept-constant-function-market-maker]] — the CFMM defined by its bonding curve.
- [[concept-intrinsic-liquidity]] — reparametrization-invariant liquidity from the curve's curvature.
- [[concept-liquidity-profile]] — how liquidity is distributed over price along the curve.
- [[concept-constant-product-market-maker]] — the xy = k bonding curve.
- [[concept-geometric-mean-market-maker]] — the weighted-power bonding curve.
- [[concept-reserve-option-duality]] — curve convexity underlies the option-portfolio view.
- [[concept-optimal-curve-design]] — the problem of choosing this curve as the design variable
  rather than taking it as given.
- [[concept-convex-duality]] — the Fenchel conjugacy that recovers a curve from a target payoff.
- [[concept-cfmm-axioms]] — the stated properties that bound which curves are admissible.
- [[concept-constant-power-root-family]] — a one-parameter family of curves spanning the
  harmonic, geometric and arithmetic mean cases.
