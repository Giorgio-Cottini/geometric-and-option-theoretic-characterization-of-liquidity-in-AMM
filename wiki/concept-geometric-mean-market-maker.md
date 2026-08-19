---
title: Geometric Mean Market Maker
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Geometric Mean Market Maker (G3M)

A CFMM whose invariant is a weighted geometric mean of reserves: f(x, y) = x^w · y^(1−w) = L, with weight w ∈ (0, 1). Used by Balancer to build pools with arbitrary target value splits. The constant-product market maker is the special case w = 1/2.

## Details
- Bonding function: f = x^w y^(1−w) = L (weighted-power invariant), extends to n assets as ∏ x_i^{w_i}, Σ w_i = 1.
- Spot price: P = (w / (1−w)) · (y / x); the weight w sets the target portfolio value share of asset x (constant w·V in x).
- CPMM ⇔ w = 1/2, recovering P = y/x and f = sqrt(xy).
- Value function inherits the CFMM structure V(P) = min (P·x + y) on the invariant; the weights tilt exposure and reshape the impermanent-loss profile.

## Appears in
- [[source-clmm-mathematical-framework]] — G3M appears as a CFMM family the concentrated-liquidity framework generalizes.
- [[source-wang-math-in-amm]] — develops the weighted geometric-mean invariant and derives CPMM as its w = 1/2 case.

## Related
- [[concept-constant-function-market-maker]] — G3M is a CFMM sub-family.
- [[concept-constant-product-market-maker]] — the equal-weight (w = 1/2) member.
- [[concept-bonding-curve]] — the weighted-power level set.
- [[concept-liquidity-profile]] — weights reshape the liquidity distribution.
- [[concept-impermanent-loss]] — weight-dependent IL profile.
- [[entity-balancer]] — the reference G3M protocol.
