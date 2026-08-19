---
title: Stackelberg Equilibrium
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Stackelberg Equilibrium

A Stackelberg equilibrium is the solution of a leader-follower game. One player, the leader,
commits to a strategy first. The other player, the follower, observes the leader's commitment
and best-responds to it. The leader anticipates the follower's best response and chooses its own
strategy to optimize its objective under that anticipated response. The game is solved by
backward induction: the follower's problem is solved first, as a function of the leader's
choice, then the leader's problem is solved holding that response fixed.

## Details

- Two pairings of this structure recur for liquidity provision. In the first, the venue leads by
  setting a reward contract, and a representative liquidity provider follows by choosing a
  liquidity-provision speed. In the second, a liquidity provider leads by posting a position, and
  a just-in-time bot follows by deciding whether and how to front-run it.
- In the venue-leader pairing, the venue chooses a reward contract paid to the provider, and the
  provider chooses a liquidity-provision speed process bounded by an admissible range. Both
  problems reduce to Hamilton-Jacobi-Bellman equations under backward induction: the provider's
  best response is computed first for a fixed contract, then the venue optimizes the contract
  knowing the provider will best-respond to it.
- Existence and uniqueness are proved for the follower's problem: every admissible contract has a
  unique representation, and the provider's optimal response is unique. Existence and uniqueness
  for the leader's exact problem are not proved. The venue's Hamilton-Jacobi-Bellman equation is
  stated as a verification theorem, which assumes a smooth solution exists rather than proving it.
- The venue's problem is instead solved through an approximation. A Laurent-series expansion in
  the ratio of trade size to pool depth, combined with a quadratic ansatz for the value function,
  turns the venue's partial differential equation into a finite system: a matrix Riccati ordinary
  differential equation for the quadratic term, a linear ordinary differential equation for the
  linear term, and a scalar ordinary differential equation for the constant term. This system
  integrates backward in time at the cost of a low-dimensional Riccati integration, not a
  multi-dimensional partial differential equation grid solve.
- The provider side in this model is a single representative provider, not a population. Other
  providers' activity enters only as an exogenous noise term in the reserve dynamics, not as
  competing optimizers, and no fixed-point condition over a provider population appears anywhere.
  The model is therefore a Stackelberg game, not a mean-field game. [[concept-mean-field-game]]
  records the same distinction from the population side: a mean-field game requires a
  distribution of interacting agents and a fixed-point condition over that distribution, neither
  of which this model has.

## Appears in

- [[source-equilibrium-reward-lps]] — supplies the venue-leader, representative-provider
  Stackelberg structure: the two players and their choices, the proof of existence and
  uniqueness for the follower against the assumed verification theorem for the leader, and the
  reduction of the venue's problem to a matrix Riccati ordinary differential equation rather than
  a partial differential equation grid solve.

## Related

- [[concept-mean-field-game]] — the population-of-agents counterpart this model deliberately is
  not; both pages record the same representative-agent-versus-population distinction.
- [[concept-nash-equilibrium-lps]] — a simultaneous-move equilibrium concept among competing
  providers, contrasted with the sequential commitment structure of a Stackelberg game.
- [[concept-just-in-time-liquidity]] — the empirical behavior that gives the second
  leader-follower pairing its content: a provider posts a position and a just-in-time bot
  front-runs it in response.
- [[concept-lp-behavior]] — describes what providers empirically do; this page gives that
  behavior an equilibrium counterpart in the venue-leader game.
- [[concept-stochastic-control]] — the follower's liquidity-provision-speed problem is a standard
  stochastic control problem solved by a Hamilton-Jacobi-Bellman equation.
