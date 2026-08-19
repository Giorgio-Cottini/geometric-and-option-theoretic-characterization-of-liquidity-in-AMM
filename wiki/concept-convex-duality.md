---
title: Convex Duality
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Convex Duality

Convex duality, in the CFMM setting, is the Fenchel conjugacy between a liquidity provider's
payoff function and the market maker's bonding curve. A payoff function V(c), the arbitrageur's
optimal-value function over reserves at external price c, and a trading function ψ(R) are
conjugates of one another: ψ(R) = -sup_c(-c^T R - (-V)(c)) = -(-V)*(-R). Given either object, the
other is recoverable in closed form whenever the conjugate integral or supremum can be evaluated.
This correspondence is the formal license to treat curve shape as a free design variable: any
target payoff, subject to a small set of shape conditions, corresponds to an explicit bonding
curve, and conversely.

## Details

- **The one-to-one correspondence.** [[source-replicating-market-makers]] proves that the space
  of concave, nonnegative, nondecreasing, 1-homogeneous payoff functions is equivalent to the
  space of convex CFMM trading sets. A payoff function with these four properties is called
  consistent; every CFMM's payoff function is consistent, and every consistent payoff function
  has a corresponding CFMM trading function that produces it exactly.
- **The recovery formula.** Given a desired payoff V, the trading function is
  ψ_V(R) = inf_c (c^T R - V(c)), the negative Fenchel conjugate of -V with negated arguments.
  This is closed-form whenever the conjugate can be computed; worked cases include linear payoffs
  (asset holding), quadratic payoffs, and power payoffs (Balancer weights).
- **Economic reading of the four conditions.** Concavity is forced by path independence and is
  the formal statement that impermanent loss ("negative gamma") is intrinsic to any CFMM.
  Nonnegativity is solvency. Monotonicity says LP value does not fall as coin prices rise.
  1-homogeneity is scale invariance of the numéraire.
- **Generalization beyond homogeneity and differentiability.** [[source-geometry-of-cfmms]]
  rebuilds the same correspondence from three purely geometric axioms on a reachable reserve set
  (nonnegative, closed and convex, upward closed), proves it via conic duality instead of Fenchel
  conjugacy, and shows every CFMM, even one defined by a non-differentiable, non-homogeneous
  trading function, has a canonical trading function that is concave, nondecreasing, and
  1-homogeneous. Differentiability and homogeneity of the starting object are therefore not
  needed for the correspondence to exist, only for it to be given in closed form.
- **Closed form versus numerical.** The correspondence guarantees existence, not tractability:
  [[source-geometry-of-cfmms]] states explicitly that the canonical trading function may have no
  closed form, and gives bisection or Newton's method as the general-purpose way to evaluate it.
  Whether a curve-shape question has a closed-form answer or needs a numerical program is
  therefore a property of the specific payoff or reachable set chosen, not of the theory itself.
- **License for design.** Because any admissible payoff has a curve and any admissible curve has
  a payoff, choosing "what payoff do liquidity providers want" and choosing "what bonding curve
  shape should the pool use" are the same design decision, viewed from two sides. This is what
  makes curve shape a legitimate object of optimization rather than a fixed implementation
  choice.

## Appears in

- [[source-replicating-market-makers]]: the origin of the correspondence, proved via Fenchel
  conjugacy under differentiability and 1-homogeneity, with worked linear, quadratic, and Balancer
  examples.
- [[source-geometry-of-cfmms]]: generalizes the correspondence to a purely geometric, axiomatic
  setting with no differentiability or homogeneity assumption, proved via conic duality on the
  liquidity cone, and flags the general case as a numerical root-finding problem.
- [[source-constant-power-root-mm]]: exercises the correspondence on a concrete one-parameter
  family of payoffs, using it to derive a new trading function (constant harmonic mean) rather
  than only reverse-engineering known ones.

## Related

- [[concept-reserve-option-duality]]: the region's own statement that a CFMM position is a short
  option book, arrived at from stochastic pricing and hedging rather than convex analysis. Both
  concepts assert the same underlying fact, that reserves and payoff determine each other, from
  independent routes; convex duality gives the general, model-free (no probability measure)
  version of that determination.
- [[concept-bonding-curve]]: the object convex duality assigns to a payoff function.
  [[concept-constant-power-root-family]]: the family that exercises this correspondence across a
  full parameter sweep.
- [[concept-impermanent-loss]]: identified, under convex duality, as a structural consequence of
  the concavity requirement on any consistent payoff function, rather than an incidental cost of
  a particular curve.
- [[concept-optimal-curve-design]]: convex duality is the formal precondition that makes searching
  over curve shapes a well-posed optimization rather than an unconstrained guess.
