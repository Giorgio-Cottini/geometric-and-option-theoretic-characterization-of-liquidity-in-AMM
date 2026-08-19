---
title: Myersonian Mechanism Design
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Myersonian Mechanism Design

Myersonian mechanism design, applied to AMM liquidity provision, models the liquidity provider
as a monopolist auctioneer choosing a demand curve over price rather than a range or a weight
inside a fixed curve. Incentive compatibility forces the curve to be non-increasing and pins its
payment rule uniquely; Myerson's virtual-value machinery, generalized to the provider's
Bayesian belief update, then characterizes the profit-maximizing curve directly. The result is a
three-region step function whose middle region is a no-trade gap, read as the AMM's bid-ask
spread and split into an adverse-selection component and a monopoly-pricing component.

## Details

- **Incentive compatibility fixes the curve's shape.** A demand curve `g(p)` paired with a
  payment rule `y(p̂)` is incentive-compatible only if `g` is non-increasing, the standard
  Myerson monotonicity condition carried over from single-parameter auctions. This alone rules
  out most curve shapes before any optimization begins.
- **Virtual-value transformation.** Classical Myerson virtual value is extended to account for
  the provider's belief update `π(p0, p̂)` after each price report. Two virtual-value functions
  result, `φ_u` for reports above the prior price and `φ_l` for reports below it, and expected
  profit equals expected virtual welfare under these two functions. They collapse to Myerson's
  classical virtual values when the belief update does not depend on the report.
- **Characterization of the profit-maximizing curve.** The optimal allocation buys the maximum
  amount in the lowest price interval, sells the maximum amount in the highest, and refuses to
  trade in a middle interval bounded by the roots of `φ_u` and `φ_l`. The curve is a three-region
  step function, not a smooth demand schedule.
- **Bid-ask spread as a two-part decomposition.** The no-trade gap is the AMM analogue of a
  central-limit-order-book bid-ask spread. It is dominated by the monopoly-pricing component
  when information asymmetry is small, and by the adverse-selection component when it is large;
  under a linear (Gaussian) belief-updating rule the paper gives a closed-form split between the
  two. Even with no adverse selection at all, a gap persists from the provider's monopoly
  position alone.
- **A route to the shape question with no stochastic calculus.** The demand curve, the virtual
  value functions, and the no-trade gap are all derived from incentive-compatibility and
  revenue-equivalence arguments, the standard toolkit of auction theory. No diffusion, no value
  function, no Hamilton-Jacobi-Bellman equation, and no convex-duality argument enters. This
  makes the mechanism-design route to curve shape independent of both the stochastic-control
  tradition and the [[concept-convex-duality]] tradition, arriving at a comparable object, a
  fully specified demand curve, from a third direction.
- **Recovers known curves as special cases.** Uniform noise trading gives closed-form
  thresholds; Uniswap v2's constant-product curve, `g(p) = c/√p`, is recovered as a special case
  of the incentive-compatible demand-curve family, not assumed.

## Appears in

- [[source-myersonian-optimal-liquidity]]: the origin of the framework, proving the
  incentive-compatibility characterization, generalizing Myerson's virtual value to a
  belief-updating setting, and characterizing the profit-maximizing demand curve as a
  three-region step function with a no-trade gap split into adverse-selection and
  monopoly-pricing components.

## Related

- [[concept-optimal-curve-design]]: the same umbrella question, choosing the curve itself as the
  design variable, reached here from auction theory instead of convex duality.
- [[concept-adverse-selection]]: one of the two forces, together with monopoly pricing, shown to
  drive the no-trade gap.
- [[concept-liquidity-profile]]: the demand curve `g(p)` is a liquidity profile in this region's
  terminology, restricted to the incentive-compatible, non-increasing subfamily.
- [[concept-bonding-curve]]: incentive-compatible demand curves generalize CFMM bonding curves,
  and Uniswap v2's bonding curve is recovered as a special case.
- [[concept-market-microstructure]]: the framework is positioned explicitly against the
  Glosten-Milgrom and Kyle market-microstructure literature, as a competing route to the same
  bid-ask-spread question.
- [[source-amm-loss-versus-rebalancing]]: the closest competing cost model in this region, also
  attributing part of LP cost to informed counterparties trading against a stale price, but
  isolating that cost through rebalancing-frequency accounting rather than monopoly virtual value.
- [[entity-jason-milionis]], [[entity-ciamac-moallemi]], [[entity-tim-roughgarden]]: authors of
  the source paper.
- [[synthesis-optimal-liquidity-shape]]: this framework is a key input to the region's synthesis
  on optimal curve shape.
