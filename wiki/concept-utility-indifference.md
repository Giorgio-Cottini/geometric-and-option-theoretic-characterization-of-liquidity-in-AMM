---
title: Utility Indifference
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Utility Indifference

Utility indifference is a pricing and design principle under which a liquidity provider accepts
a trade only if executing it leaves the provider's utility unchanged. A strictly concave utility
function over the pool's two reserves defines the trading rule directly: a trade is accepted
exactly when it keeps the provider's utility value at its pre-trade level. Applied to liquidity
provision, this construction generates a trading function, and with it a no-arbitrage argument
that pins the pool's implicit bid and ask prices against an external market.

## Details

- The utility-indifference trading function contains the constant product market maker and
  concentrated liquidity as special cases: setting the utility function to the product of the
  two reserves recovers a constant product market maker, and bounding the reserve ranges recovers
  a concentrated-liquidity position of the kind Uniswap v3 implements.
- The no-arbitrage argument follows directly from the utility function's derivative: the pool's
  ask and bid prices are read off the slope of the implicit reserve curve, and the pool is
  arbitrage-free exactly when those prices bracket the external price. When they do not, the
  arbitrageur's optimal trade size is available in closed form, and executing it restores the
  no-arbitrage bounds.
- The construction extends to a rigorous account of impermanent loss and loss-versus-rebalancing
  under concentrated liquidity: impermanent loss can be super-hedged by a model-free rebalancing
  strategy when the external price is continuous, and loss-versus-rebalancing vanishes under a
  nonzero fee under the same continuity condition.
- A precise and separate result concerns Uniswap v3. When multiple providers are reduced to
  subpools and a liquidity taker's order is optimally allocated across them, the optimal
  allocation collapses to a single aggregated constant-product pool with reserves proportional to
  each subpool's depth, so fee income accrues to each provider in proportion to that depth. The
  source page for this result states plainly that this optimality claim is **allocative, not
  about shape**: it is optimal in the sense that fee income distributed in proportion to each
  provider's depth follows from the optimal allocation of a taker's order across subpools. The
  paper does **not** claim that the concentrated-liquidity range itself is the best choice for a
  provider's risk-return objective. Which range and profile a provider should choose to optimize
  its own risk-return objective is left open.
- This distinction matters because an earlier survey of this literature overstated the claim as
  a direct answer to the open problem of optimal liquidity shape. It is not that answer. It
  answers how fee income should split across providers who have already chosen their ranges, not
  which range a provider should choose.

## Appears in

- [[source-fukasawa-utility-indifference]] — supplies the utility-indifference trading function,
  the no-arbitrage and optimal-arbitrage derivations, the impermanent-loss super-hedge and
  loss-versus-rebalancing results under concentrated liquidity, and the precisely-scoped Remark 7
  claim that Uniswap v3's construction is allocatively, not shape-, optimal.

## Related

- [[concept-optimal-liquidity-provision]] — the open problem of which liquidity profile a
  provider should choose; the allocative optimality result here does not answer it.
- [[concept-convex-duality]] — the pool value in this construction is a Legendre transform of the
  utility function, the same convex-duality machinery this region already uses for reserve and
  option-price relationships.
- [[concept-loss-versus-rebalancing]] — the quantity this construction proves vanishes under a
  nonzero fee and a continuous external price.
- [[concept-impermanent-loss]] — the quantity this construction proves can be super-hedged by a
  model-free rebalancing strategy.
- [[concept-concentrated-liquidity]] — the special case of the utility-indifference construction
  that the allocative-optimality result is about.

## Note on the region's earlier synthesis

The allocative-only scope of the Uniswap v3 optimality claim recorded here corrects an
overstatement in an earlier survey of this literature, which read the result as answering the
shape-optimality question directly. It does not. [[synthesis-optimal-liquidity-shape]] should be
checked against this page and corrected if it repeats the overstated version.
