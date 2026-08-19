---
title: Mean-Field Game
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Mean-Field Game

A game with a continuum of small players, in which no single player moves the aggregate state.
Each player solves a control problem against the aggregate, and the aggregate must reproduce
itself. That consistency requirement is a fixed point in the space of distributions, so the
equilibrium object is infinite-dimensional.

Applied to liquidity provision, the state is the aggregate liquidity profile. Each provider
places depth against the profile everyone else has placed, and the profile that results must
equal the one each provider assumed. This is the fifth of the six settings listed in
[[concept-optimal-liquidity-provision]].

## Details

- The standard formulation couples two equations. A Hamilton-Jacobi-Bellman equation runs
  backward for the representative player's value function. A Fokker-Planck equation runs forward
  for the population distribution. The pair is solved together, not in sequence. See
  [[concept-stochastic-control]].
- The fixed point is over a measure, not a number. A liquidity profile is already a density over
  price, so a mean-field equilibrium for liquidity provision is a distribution over distributions.
- The setting fits liquidity provision because the provider population on a public venue is large
  and heterogeneous, and because [[concept-lp-behavior]] records that most providers are small
  while a few are not. A model with a continuum of small players plus one or more large players
  is a major-minor mean-field game.
- Adding a large player that reacts to pending trades gives the just-in-time case recorded in
  [[concept-just-in-time-liquidity]], which pairs a mean-field layer with a Stackelberg layer.
  See [[concept-stackelberg-equilibrium]].

## What this region does not yet hold

This page defines the setting. No source curated in this region solves a mean-field game for
liquidity provision, so the page is deliberately thinner than its siblings.

- [[source-equilibrium-reward-lps]] is **not** a mean-field model. It uses one representative
  provider as the follower against the venue, and other providers enter only as exogenous noise
  in the reserve dynamics. No fixed point over a provider distribution appears in it. A
  representative agent and a continuum of agents are different objects, and the distinction
  matters for which equilibrium the model actually characterizes.
- Two mean-field papers identified in the survey were not obtainable. Bayraktar and coauthors
  (2024), *DEX Specs: A Mean-Field Approach to DeFi Currency Exchanges*, is on SSRN with no open
  preprint, and it is the one calibrated to Uniswap data with a Stackelberg layer against
  just-in-time bots. The Munoz Gonzalez series (2024, 2026) builds a major-minor game extending
  the arbitrage and loss-versus-rebalancing models, and its most recent installment states that
  it is a research proposal rather than a closed result, with existence and uniqueness for the
  full three-agent model still open.

Closing this gap requires obtaining the Bayraktar paper through the university library. Until
then the region's equilibrium coverage is Nash and Stackelberg, not mean-field. See
[[synthesis-optimal-liquidity-shape]] for the material-not-obtained record.

## Appears in
- [[source-equilibrium-reward-lps]] — a representative-provider Stackelberg model, recorded here
  because it is the nearest thing the region holds and because it is commonly mistaken for a
  mean-field formulation.

## Related
- [[concept-optimal-liquidity-provision]] — the hub listing all six settings.
- [[concept-nash-equilibrium-lps]] — the finite-player equilibrium a mean-field game approximates.
- [[concept-stackelberg-equilibrium]] — the leader-follower layer that mean-field models of this
  market usually add.
- [[concept-liquidity-profile]] — the object the fixed point ranges over.
- [[concept-lp-behavior]] — the empirical population the continuum is meant to represent.
