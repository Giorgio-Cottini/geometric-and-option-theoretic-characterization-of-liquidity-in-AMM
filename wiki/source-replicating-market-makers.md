---
title: Replicating Market Makers
layer: core
type: source
origin: thesis
date: 2026-08-04
source_path: "articles/optimal shape/curve-design/Replicating Market Makers.pdf"
source_kind: paper
---

# Replicating Market Makers

This paper solves the inverse problem of CFMM design: given a desired liquidity provider (LP)
payoff function, construct a trading function whose portfolio value matches that payoff. The
authors prove that the space of concave, nonnegative, nondecreasing, 1-homogeneous payoff
functions is equivalent to the space of convex CFMM trading sets, and give an explicit
construction, based on Fenchel conjugacy, that recovers a trading function from any payoff in
that class. Static replication by a CFMM avoids the on-chain oracle updates and dynamic
rebalancing that continuous replication of a payoff would otherwise require.

**Authors / venue / year:** Guillermo Angeris, Alex Evans, Tarun Chitra. arXiv:2103.14769,
March 2021.

## Key points

- A path-independent CFMM is defined by a trading function ψ and reserves R. A trade is
  admissible only if ψ(R') ≥ ψ(R) for the new reserves R'.
- The LP portfolio value at price vector c is V(c) = inf{c^T R | ψ(R) ≥ k}, the arbitrageur's
  optimal-value function over the reserve set. This is the payoff function of the CFMM.
- A payoff function V is called **consistent** if it is concave, nonnegative, nondecreasing, and
  1-homogeneous (V(ηc) = ηV(c) for η ≥ 0). Every CFMM payoff function is consistent, and, the
  paper's central result, every consistent payoff function has a corresponding CFMM trading
  function that produces it.
- The feasible reserve set for a payoff V is S = {R ∈ R+^n | V(c) ≤ c^T R for all c}, the
  intersection of a family of halfspaces indexed by price c. The proof that this set yields
  payoff exactly V uses only a lower bound (feasibility) and an upper bound (supergradient
  construction), a strong-duality argument from convex analysis.
- Impermanent loss is identified as a structural consequence, not an incidental cost: concavity
  of V is forced on any path-independent CFMM, and concavity is exactly "negative gamma."
- The construction is closed-form whenever the Fenchel conjugate of the target payoff can be
  computed or bounded in closed form; the paper works two closed-form cases (linear, quadratic)
  and one series of practical cases (Balancer weights, covered calls, perpetual puts) that reduce
  to known trading functions.

## Notable claims & data

- Trading-function construction (equation 5), the paper's core formula:
  ψ_V(R) = inf_c (c^T R − V(c)), which the authors identify explicitly as the negative Fenchel
  conjugate of −V with negated arguments: ψ_V(R) = −(−V)*(−R). This is the formal statement that
  **trading function and payoff function are Fenchel conjugates of each other.**
- Linear payoff V(c) = a^T c reproduces the trivial CFMM that only allows the null trade at
  reserves R = a: ψ_V(R) = 0 if R = a, −∞ otherwise. Confirms the method against a known case.
- Linear-offset rule: if V'(c) = V(c) + a^T c, then ψ_V'(R) = ψ_V(R − a). A payoff offset by a
  fixed linear term corresponds to a reserve shift by a, useful for building composite payoffs.
- Quadratic payoff U(c') = −½(c')^T A c' + b^T c' + d, A positive definite, replicated (within a
  compact price region) by ψ_V(R', R_n) = 0 if ½(R'−a)^T A^{-1}(R'−a) ≤ R_n − b, −∞ otherwise.
  The authors note no such CFMM had previously appeared in the literature; the derivation is
  closed-form via the perspective transform.
- Balancer recovery: for the power payoff U(c1) = c1^w, 0 < w < 1, the reduced payoff is the
  weighted geometric mean V(c1,c2) = c1^w c2^{1-w}, and the recovered trading function is
  ψ_V(R1,R2) = 0 if (R1/w)^w (R2/(1-w))^{1-w} ≥ 1, −∞ otherwise. This is exactly the constant-mean
  invariant used by Balancer, recovered from a payoff specification rather than posited directly.
- The paper also replicates Black-Scholes covered-call and perpetual American put payoffs (later
  sections, not read here), extending the method to standard financial derivatives.

## Connections

- [[concept-convex-duality]]: this paper is the primary source for that concept. The equivalence
  theorem and equation (5) are its exact statement of the Fenchel-conjugacy correspondence.
- [[concept-reserve-option-duality]]: the RTW26 line reaches "a CFMM position is a short option
  book" from stochastic pricing and hedging. This paper reaches the same short-option-payoff
  reading of a CFMM (see the Limitations discussion on resting limit orders as short options)
  from convex duality, with no stochastic calculus at all. The two are independent derivations of
  one underlying correspondence between reserves and payoff.
- [[concept-impermanent-loss]]: identified here as forced by concavity of any path-independent
  CFMM's payoff function, an intrinsic-liquidity-style argument reached through convexity
  instead of arbitrage-loss accounting.
- [[concept-constant-function-market-maker]], [[concept-geometric-mean-market-maker]]: the
  Balancer/constant-mean trading function is recovered here as a special case of the general
  method rather than assumed.
- [[source-rtw26-cfmm-liquidity-pricing-hedging]]: shares the CFMM/reserves/trading-function
  vocabulary but works in a stochastic pricing and hedging setting; this paper is purely convex
  analysis with no probability measure.

## Open questions

- The method requires V to be exactly consistent (concave, nonnegative, nondecreasing,
  1-homogeneous) for the equivalence to hold with equality; the paper flags dropping
  1-homogeneity or monotonicity as open, addressed in part by the follow-up geometry paper.
  See [[source-geometry-of-cfmms]].
- Replicating convex payoffs (e.g. long option positions) requires shorting shares in the CFMM or
  external price oracles, outside the scope of the pure static-replication method.
- The quadratic-payoff construction only matches the target payoff within a compact set of price
  vectors; outside it the CFMM payoff saturates at 0, an unresolved boundary-behavior gap.
