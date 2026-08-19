---
title: Constant Power Root Family
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Constant Power Root Family

The constant power root family is a one-parameter family of CFMM value functions,
V_pow(a,b,p) = (a^p + b^p)^(1/p) for p ≤ 1, that interpolates continuously between the harmonic
mean, geometric mean, and arithmetic mean curves. Constant reserve, constant sum, constant
product, and constant harmonic mean market makers are all special or limiting cases of this one
family, obtained by varying the single scalar p (or its trading-function reparametrization
q = p/(p-1)). Every quantity of interest, value function, marginal price, impermanent loss, is
closed-form in this parameter, which makes the family the cheapest possible object on which to
run a numerical sweep over curve shape.

## Details

- **The family.** V_pow(a,b,p) = (a^p + b^p)^(1/p), p ≤ 1. Limiting cases: p=1 gives V_rsv=a+b
  (constant reserve / HODL); p→0 gives V_prod=√(ab) (constant product, e.g. Uniswap); p→-∞ gives
  V_sum=min{a,b} (constant sum, e.g. mStable-style stableswap). At q→-1 (p=1/2) the family gives
  the constant harmonic mean, V_har(a,b)=(√a+√b)^2, a curve with higher curvature than constant
  product and, prior to this family's paper, not implemented in any deployed AMM.
- **Economic reading.** The family is the constant elasticity of substitution (CES) production
  function; its three named boundary cases are exactly the perfect-substitute (linear), Leontief,
  and Cobb-Douglas production functions of classical economic theory.
- **The single dial.** As p increases toward 1 (equivalently q toward 1), curvature falls, price
  slippage for traders falls, and impermanent loss for liquidity providers rises. As p decreases
  (q toward -1), curvature rises, slippage rises, and impermanent loss falls. One scalar therefore
  spans the entire slippage-versus-impermanent-loss tradeoff, from the LP's side and the trader's
  side simultaneously.
- **Closed-form throughout.** Because V_pow is provably consistent (concave, nonnegative,
  nondecreasing, 1-homogeneous, see [[concept-convex-duality]]) for every p ≤ 1, the Fenchel
  conjugacy method gives its trading function ψ_pow in closed form, and marginal price and
  impermanent loss follow in closed form from that. No case in the family requires numerical
  root-finding to evaluate.
- **Cost of a design sweep.** A computational study of "which curve shape is best" faces, in
  general, a search over an infinite-dimensional space of admissible payoff functions. Restricting
  to this family collapses that search to a 1-D scan over p (or q) with closed-form objective
  values at every grid point, the cheapest possible numerical experiment design for the question,
  and a natural first pass before any higher-dimensional curve search.

## Appears in

- [[source-constant-power-root-mm]]: the origin of the family; derives V_pow, its trading
  function, marginal price, and impermanent loss, all closed-form in p, and proves the four named
  special cases sit on the same continuum.
- [[source-replicating-market-makers]]: supplies the Fenchel-conjugacy machinery
  ([[concept-convex-duality]]) that the family's trading function is derived from.

## Related

- [[concept-convex-duality]]: the theoretical license that makes the family's payoff-to-curve map
  valid; consistency of V_pow for all p ≤ 1 is what allows the closed-form trading function to
  exist.
- [[concept-geometric-mean-market-maker]], [[concept-constant-product-market-maker]]: both sit at
  p→0 inside this family, so the family formally subsumes them as one boundary case rather than
  treating them as separate designs.
- [[concept-impermanent-loss]]: given in closed form as a function of the family's parameter,
  I_pow(q), generalizing the standard constant-product formula.
- [[concept-optimal-curve-design]]: the family is a natural first target for optimal curve design
  because its low dimensionality turns "search over curve shapes" into a tractable scalar
  optimization.
- [[concept-loss-versus-rebalancing]]: the family's slippage-versus-impermanent-loss tradeoff is a
  static, curve-parametrized analogue of the dynamic loss-versus-rebalancing tradeoff studied in
  the RTW26 line; both quantify the cost LPs bear for supplying convexity, from different
  starting assumptions (deterministic curve family versus stochastic price process).
