---
title: CFMM Axioms
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# CFMM Axioms

CFMM axioms are stated economic properties of a trading function, such as independence, scale invariance, translation invariance, aversion to permanent loss, and sufficient funds, and the characterization theorems that identify exactly which curve shapes satisfy a given combination of them. The axioms fix which trading functions can exist under the stated economics; they say nothing about which one is best under any objective.

## Details

- [[source-axioms-for-cfmms]] states the axiom set and proves two headline characterizations. Independence paired with scale invariance forces the trading function into the constant inventory elasticity (CEMM) family, f(I) = c(Σ α_A I_A^γ)^(1/γ), which contains the weighted geometric mean, the weighted arithmetic mean, and the constant product market maker as special cases indexed by the elasticity parameter γ. Independence paired with translation invariance forces the trading function into the LMSR family or the constant sum market maker.
- Aversion to permanent loss, convexity of the set {I : f(I) ≥ f(J)} for each J, forces liquidity curves to be convex and pins CEMM elasticity below 1 (γ < 1). Sufficient funds, the requirement that the AMM can absorb a trade of any size, rules out concentrated liquidity and pins elasticity to γ ≥ 0. Combined, the two axioms restrict CEMM elasticity to the interval (0, 1], the span from the weighted geometric mean toward, but excluding, the weighted arithmetic mean. Uniswap V3 violates sufficient funds by design, since its liquidity curves intersect the axes at finite inventory.
- Within the scale-invariant, independent, symmetric, non-concentrated class, the members are fully ranked by the curvature of their liquidity curves, and the constant product market maker sits at the trader-optimal extreme of that ranking. This is a characterization result, not an optimization: the ranking falls out of the axioms themselves, with no objective function stated or maximized.
- The two-asset case is materially weaker. Independence is trivially satisfied for two assets, so the resulting class of trading functions is strictly larger and cannot be fully ranked by curvature without an added separability assumption.
- Because the axioms are stated with no objective function, they define a feasible set rather than an optimum. An optimization problem over curve shape, such as [[concept-optimal-curve-design]], needs exactly this feasible set: without it, a search over "all increasing functions of reserves" has no principled boundary between an economically admissible AMM design and an arbitrary function that happens to be monotone. The axioms answer "which curves are candidates," and a separate objective, a belief-driven convex program or a payoff target, answers "which candidate is optimal."
- This is why the axioms matter to a computational study that optimizes nothing at the level of the axioms themselves. A solver that searches over curve shape needs its search space specified before it can run; the CEMM family, indexed by a single elasticity parameter and bounded to (0, 1] by aversion to permanent loss and sufficient funds, is a natural finite-dimensional space to search when the fully infinite-dimensional program of [[concept-optimal-curve-design]] is not tractable or not wanted.

## Appears in

- [[source-axioms-for-cfmms]] is the sole source for this concept: it states the axioms, proves the CEMM and LMSR characterization theorems, and derives the curvature ranking that places the constant product market maker at the trader-optimal extreme.

## Related

- [[concept-optimal-curve-design]] is the optimization problem that needs this feasible set as its search domain; the axioms constrain what a curve-design solver is allowed to output.
- [[concept-constant-power-root-family]] is close to, but not identical to, the CEMM family the axioms characterize: both are power-mean-indexed families of curve shapes.
- [[concept-bonding-curve]] and its induced liquidity curve are the object every axiom constrains directly.
- [[concept-constant-function-market-maker]] is the general model the axioms are stated over.
- [[concept-constant-product-market-maker]] is characterized here as the trader-optimal, symmetric boundary case of the CEMM family.
- [[concept-geometric-mean-market-maker]] is the γ = 0 member of the CEMM family, generalizing the constant product market maker to asymmetric weights.
- [[concept-concentrated-liquidity]] is the negation of the sufficient funds axiom; Uniswap V3 is the running counterexample used throughout the source.
- [[concept-marginal-price-impact]] is the quantity the invariance and independence axioms constrain directly, via the marginal exchange rate.
