---
title: Stochastic Control
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Stochastic Control

Stochastic control is the mathematical framework for optimizing decisions in a randomly evolving system, built on the value function, the dynamic programming principle, and the Hamilton–Jacobi–Bellman (HJB) equation. It supplies the tools — LQ problems, optimal stopping, bang-bang controls — used to derive optimal concentrated-liquidity provision strategies.

## Details
- Value function: the best achievable expected objective (e.g. fees minus risk/costs) from any state, treated as the central unknown.
- Dynamic programming principle: optimality is recursive — an optimal policy is optimal from every intermediate state onward.
- HJB equation: the PDE the value function satisfies in continuous time; solving it yields the optimal feedback control.
- LQ (linear-quadratic) problems: a tractable special case with closed-form controls, often a first modelling approximation.
- Optimal stopping: choosing when to act (e.g. when to reposition or withdraw liquidity), solved via free-boundary/variational problems.
- Bang-bang control: optimal actions jump between extremes rather than varying smoothly, arising when the objective is linear in the control — relevant to discrete reposition/withdraw decisions.
- Applied to LPs: state is the price and liquidity position; controls are range placement and rebalancing; the solution characterizes optimal provision.

## Appears in
- [[source-wang-bocconi-2]] — formulates optimal concentrated-liquidity provision as a stochastic-control problem and derives the associated value function / HJB and stopping/bang-bang structure.

## Related
- [[concept-concentrated-liquidity]] — the controlled object whose provision the framework optimizes.
- [[concept-liquidity-surface]] — the state landscape over which the control problem is posed.
- [[concept-rebalancing-strategy]] — the repositioning actions the optimal control prescribes.
- [[concept-loss-versus-rebalancing]] — the risk/cost term entering the control objective.
- [[entity-tai-ho-wang]] — author of the stochastic-control treatment of liquidity provision.
- [[concept-optimal-liquidity-provision]] — the hub that places this framework as one of six
  settings for the shape question.
- [[concept-optimal-range-width]] — the closed-form control result, a range width from an HJB
  equation.
- [[concept-predictable-loss]] — the cost term that control result trades against fee income.
- [[concept-optimal-stopping-withdrawal]] — the stopping half of the framework, applied to the
  withdrawal decision.
- [[concept-longstaff-schwartz]] — the simulation-based alternative to a grid solve for that
  stopping problem.
- [[concept-stackelberg-equilibrium]] — the two-player extension, where one agent's control
  problem is solved against another's commitment.
- [[concept-mean-field-game]] — the continuum extension, where the control problem is solved
  against an aggregate that must reproduce itself.
