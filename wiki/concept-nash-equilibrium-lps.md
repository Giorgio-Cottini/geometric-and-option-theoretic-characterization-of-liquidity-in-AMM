---
title: Nash Equilibrium Among Liquidity Providers
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Nash Equilibrium Among Liquidity Providers

In a concentrated-liquidity pool, every provider draws fees from the same shared pool and
absorbs impermanent loss on the same price path, so no provider's return can be computed in
isolation. A Nash equilibrium is the liquidity placement at which no single provider can raise
its own utility by moving its liquidity, given where every other provider has placed theirs. It
is a fixed point of the whole population's mutual best response, not the result of one provider
solving [[concept-optimal-liquidity-provision]] against a fixed, given market.

## Details
- Players and strategy space: N budget-constrained LPs, each choosing a liquidity vector across
  price ranges subject to a dollar budget. Payoff is fee income minus expected impermanent loss,
  with fee income split across the LPs active on a range by a tunable exponent; at exponent 1 the
  split is proportional to liquidity size, matching [[entity-uniswap-v3]]'s own fee-sharing rule.
- Uniqueness: the general game, where LPs choose liquidity over arbitrary price ranges, has at
  least one equilibrium but not a unique one. Restricting each LP to choosing liquidity per
  single-tick ("atomic") range shrinks the action space from quadratic to linear in the number of
  ticks and makes the game strictly diagonally concave for a fee-sharing exponent between 0 and 1,
  which gives a unique equilibrium by Rosen's theorem. A companion theorem shows the atomic
  equilibrium and every equilibrium of the general game induce the same liquidity histogram, so
  the atomic game's unique answer is also the general game's answer.
- Computation: no closed form exists for the equilibrium. It is found numerically, by Rosen's
  relaxation algorithm; mirror descent and no-regret learning converge to the same point under
  repeated play.
- Distance from equilibrium in practice: on Uniswap v3, real LP placements sit far from the Nash
  equilibrium in risky pairs, with 75th-percentile overlap under 9%, but much closer in the one
  stable pair tested, with 40% median overlap. The gap tracks price risk: it shrinks toward zero
  exactly where active repositioning has the least value.
- The distinction this concept draws: a single-agent optimum answers what one LP should do,
  holding the rest of the pool fixed. A Nash equilibrium answers what every LP does when each is
  solving that problem at once. The two answers coincide only when no provider's placement can
  move another provider's payoff, which does not hold in a pool with shared fees.

## Appears in
- [[source-game-theoretic-clmm-provisioning]] — proves existence and uniqueness of the atomic
  equilibrium for fee-sharing exponent in (0,1], supplies the relaxation algorithm that computes
  it, and reports the pool-by-pool overlap findings stated above.
- [[synthesis-optimal-liquidity-shape]] — places this equilibrium concept among the other
  accounts of what shape an LP's liquidity should take.

## Related
- [[concept-optimal-liquidity-provision]] — the single-provider optimum this concept generalizes
  to a population; the source paper positions its game as this framework's multi-provider
  setting.
- [[concept-lp-behavior]] — documents what real providers empirically do; this concept supplies
  the equilibrium benchmark that behavior can now be measured against.
- [[concept-just-in-time-liquidity]] — the narrow-range, high-frequency-update strategy the
  equilibrium favors in risky pools, and which most real LPs do not execute; this concept names
  the gap between the two.
- [[concept-concentrated-liquidity]] — the pool mechanism, discrete price ranges with shared fee
  accrual, that makes providers' payoffs interdependent in the first place.
- [[concept-uniswap-v3-ticks]] — the atomic price ranges the equilibrium is defined over once the
  game is reduced from general ranges to per-tick liquidity.
- [[entity-uniswap-v3]] — the protocol whose proportional fee-sharing rule the game's payoff
  function matches at exponent 1, and whose pools supply the calibration data.
