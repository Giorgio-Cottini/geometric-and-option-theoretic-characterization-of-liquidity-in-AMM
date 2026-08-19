---
title: Longstaff-Schwartz Method
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Longstaff-Schwartz Method

A regression-based Monte Carlo scheme for optimal-stopping problems. At each time step it regresses the continuation value on a polynomial basis in the state variables, then stops as soon as the fitted continuation value falls to or below zero. It trades the curse of dimensionality that a finite-difference grid pays for simulation variance and a discrete-time exit bias.

## Details
- Mechanism: at each time step, regress the continuation value on a degree-`d` polynomial in the state variables (here price `S` and reserve `Y`); a path stops the first time the fitted continuation value is non-positive.
- Validated against an implicit Euler finite-difference scheme on a 3D grid (time, reserve, price) with operator splitting: an explicit step for the jump terms, an implicit step for the diffusion term, subject to a CFL stability condition.
- Calibration in the source: `n = 1,440` time steps, `m = 5,000` simulated paths for the grid comparison, `m = 10,000` paths for the comparative-statics tables, polynomial regression degree `d = 3`.
- The two numerical methods agree on the shape of the exit region. Longstaff-Schwartz slightly underestimates the value function because it can only exit at discrete grid times, while the grid method is exact up to discretization but pays the curse of dimensionality across three state variables.
- Framed as a numerical method the thesis could reimplement directly: it needs only a payoff simulator and a polynomial regression at each step, no PDE solver, so it generalizes to other CFMM exit-time or stopping-boundary problems the thesis might pose beyond the specific AMM model of the source.

## Appears in
- [[source-bergault-optimal-exit-time]] — applies Longstaff-Schwartz to the LP withdrawal optimal-stopping problem and validates it against an implicit Euler grid scheme.

## Related
- [[concept-optimal-stopping-withdrawal]] — the optimal-stopping problem this method solves numerically.
- [[concept-stochastic-control]] — Longstaff-Schwartz is a simulation-based alternative to grid-based dynamic programming for control problems.
- [[source-rtw26-cfmm-liquidity-pricing-hedging]] — its last-passage-time withdrawal result is the
  stopping problem this method is applied to, and the paper notes that a last passage time is not
  a stopping time, which is what makes a numerical exit boundary necessary.
- [[concept-impermanent-loss]] — the quantity that resets at the entry price, and so defines the
  payoff the regression estimates.
- [[concept-rebalancing-strategy]] — the action set an exit decision sits inside.
- [[concept-liquidity-profile]] — the position whose value the continuation estimate prices.
