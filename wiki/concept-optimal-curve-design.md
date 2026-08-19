---
title: Optimal Curve Design
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Optimal Curve Design

Optimal curve design is the problem of choosing a CFMM's bonding curve, or equivalently its liquidity profile over exchange rates, as the design variable itself, rather than choosing a range or a weight inside a curve family fixed in advance. It is the umbrella concept for the convex-duality school of CFMM theory: the trading function and the LP payoff function determine each other, so a design problem posed on either side is a search over curve shape.

## Details

- The [[concept-reserve-option-duality]] and [[concept-convex-duality]] correspondences are the formal license for treating curve shape as a free variable. [[source-replicating-market-makers]] proves that every consistent payoff function (concave, nonnegative, nondecreasing, 1-homogeneous) corresponds to a unique CFMM trading function via Fenchel conjugacy, and [[source-geometry-of-cfmms]] reproves the same correspondence via conic duality on the liquidity cone, dropping the differentiability and homogeneity assumptions. Both results say the same thing: pick a payoff, and the curve is determined, or pick a curve, and the payoff is determined. Optimal curve design exploits this by posing the optimization on whichever side is more tractable.
- [[source-finding-the-right-curve]] states the belief-to-curve convex program directly. Given an LP's belief ψ about future exchange rates, the program minimizes expected CFMM inefficiency, or maximizes expected fee revenue net of divergence loss, over the liquidity allocation L(p), the amount of capital deployed at each exchange rate p. The decision variable is one number per exchange rate, so the program is infinite-dimensional, a Banach-space optimization rather than a finite-parameter search.
- The program is solved by KKT analysis. For several named belief functions, closed form: a uniform belief gives the constant product market maker, a belief uniform on a sub-range gives a concentrated liquidity position, a power-law-skewed belief gives the weighted product maker, and a specific rational belief gives the LMSR-based maker. For a belief with no closed form, the KKT conditions still characterize the optimum, and the paper supplies a numerical solver that computes L(p) directly from an arbitrary user-submitted belief function.
- Designing the curve is a different problem from designing the [[concept-liquidity-profile]] within a curve already fixed. Choosing a Uniswap V3 tick range or a Balancer weight vector optimizes a small number of parameters inside a trading function form that is given. Optimal curve design instead treats the trading function form as the unknown; a range or a weight choice is the special case where the search is restricted to a low-dimensional slice of the full space of curves.
- Whether a given instance of the problem is closed-form or numerical depends on the belief, not on the method. The KKT conditions in [[source-finding-the-right-curve]] hold in general; closed-form L(p) falls out only for beliefs whose functional form makes the stationarity condition invertible by hand. [[source-geometry-of-cfmms]] makes the same point from the axiomatic side: the canonical trading function φ(R) = sup{λ | (R, λ) ∈ K} is well-defined for any reachable set, but evaluating it is a root-finding problem in λ that in general has no closed form and is computed by bisection or Newton's method. Both papers converge on the same conclusion: curve design is a computational program by default, and a closed-form answer is the exception that a specific belief or a specific axiom set can produce.
- This computational character is the operative fact for a thesis built as a computational study. The object under study is not one optimal curve but a solver, closed-form where possible and numerical otherwise, that maps an input (a belief, or a target payoff) to an output curve.

## Appears in

- [[source-finding-the-right-curve]] states the belief-to-curve convex program (COP), proves its KKT structure, derives closed-form optimal liquidity allocations for named beliefs, and supplies a numerical solver for beliefs without closed form.
- [[source-replicating-market-makers]] proves the payoff-to-curve equivalence via Fenchel conjugacy and gives the closed-form construction for consistent payoffs, the duality that licenses treating curve shape as a free design variable.
- [[source-geometry-of-cfmms]] generalizes that equivalence via conic duality without differentiability or homogeneity assumptions, and states explicitly that the canonical trading function is in general a numerical root-finding problem, not a closed form.
- [[source-axioms-for-cfmms]] supplies the feasible set of curve shapes that any instance of this design problem must search within; see [[concept-cfmm-axioms]].

## Related

- [[concept-cfmm-axioms]] defines the feasible set of curve shapes; optimal curve design is the optimization run over that set.
- [[concept-convex-duality]] is the mathematical mechanism, Fenchel or conic, that lets curve shape and payoff shape stand in for each other.
- [[concept-reserve-option-duality]] is the finance-facing reading of the same correspondence: a CFMM position as a portfolio of options.
- [[concept-bonding-curve]] is the object being designed.
- [[concept-liquidity-profile]] is the object being designed when the trading function is held fixed and only its liquidity density over exchange rates varies.
- [[concept-optimal-liquidity-provision]] is the broader LP decision problem that curve design sits inside, alongside range and weight choices made within a fixed curve.
- [[concept-optimal-range-width]] is the fixed-curve special case: optimizing a scalar range rather than the full trading function.
- [[concept-constant-power-root-family]] is a parametric curve family that a curve-design search can be restricted to, trading generality for a finite-dimensional problem.
