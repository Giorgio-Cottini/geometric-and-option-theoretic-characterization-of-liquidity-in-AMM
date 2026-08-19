---
title: Waterfilling Allocation
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Waterfilling Allocation

At the unique Nash equilibrium of the atomic CLMM liquidity game, each price range has a common
water level. Providers with budget left over all bring their liquidity on that range up to the
level; providers who run out of budget first invest less than the level there and spend the rest
of their budget on other ranges. The name comes from the classical waterfilling problem: pour a
fixed amount of water over vessels of unequal depth and it settles at one level, with shallow
vessels filling before the level can rise further. Here the vessels are price ranges and depth is
set by how much budget each provider has left to spend on a range before running out.

## Details
- The allocation rule: for a fee-sharing exponent between 0 and 1, every atomic range m has a
  common level h_m such that any LP with unspent budget sets its liquidity on m to exactly h_m,
  and any LP that has exhausted its budget sets its liquidity below h_m there. Each LP's total
  spend equals the smaller of a single common threshold and that LP's own budget.
- Why low-budget providers spend everything: a budget-constrained LP's marginal utility per
  dollar never reaches zero before its budget runs out, so its optimum spends every dollar it has.
  Only a provider with enough capital left over drives its marginal utility to zero before hitting
  its budget, and stops short of the common level, holding the rest in reserve.
- Budget dominance and coverage: richer providers invest at least as much as poorer providers on
  every range, and for a fee-sharing exponent strictly between 0 and 1 every provider holds
  strictly positive liquidity on every range. No range is left completely uncontested.
- The analogy: this is the same structure as power allocation across parallel communication
  channels, or water poured over vessels of unequal depth. A fixed resource rises to one common
  level, and only the entities shallow enough for their budget, here the ranges a provider can
  fully fund, get filled to capacity before the resource runs out.
- Why it matters computationally: waterfilling is not only a description of the equilibrium, it
  is close to the equilibrium's algorithm. The relaxation procedure that computes the unique
  equilibrium proceeds by finding this common level, so a computational study reimplementing the
  model gets a concrete, tractable target instead of a generic black-box fixed-point solve.

## Appears in
- [[source-game-theoretic-clmm-provisioning]] — proves the waterfilling proposition (common level
  h_m, budget dominance, strict positivity for exponent in (0,1)) and computes it with Rosen's
  relaxation algorithm.
- [[synthesis-optimal-liquidity-shape]] — situates waterfilling among the other candidate shapes
  for how liquidity should sit across price ranges.

## Related
- [[concept-optimal-liquidity-provision]] — the single-provider allocation problem waterfilling
  replaces once every other provider's placement also matters.
- [[concept-liquidity-profile]] — the across-range liquidity distribution shape; waterfilling
  gives that shape concrete numeric content, a common level capped by each provider's budget.
- [[concept-lp-behavior]] — documents what real providers do instead; most real placements do not
  follow the waterfilling shape, which is the gap this concept makes measurable.
- [[concept-just-in-time-liquidity]] — an extreme, narrow-range strategy that is not the
  waterfilling shape, and which most real LPs approximate in practice rather than a smoothed
  common level.
- [[concept-concentrated-liquidity]] — the tick-range structure waterfilling allocates liquidity
  across.
- [[concept-uniswap-v3-ticks]] — the atomic ranges that each carry their own water level h_m.
