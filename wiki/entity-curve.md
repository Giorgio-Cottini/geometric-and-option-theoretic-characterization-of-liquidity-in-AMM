---
title: Curve
layer: core
type: entity
origin: thesis
date: 2026-07-19
---

# Curve

A stableswap automated market maker whose invariant is tuned for trading between highly correlated assets such as stablecoins.

## Role
- Blends constant-sum and constant-product behavior so that liquidity concentrates near a target parity, giving low slippage for correlated pairs.
- Rounds out the thesis's CFMM taxonomy as the specialized "stableswap" invariant distinct from constant-product and geometric-mean designs.

## Appears in
- [[source-wang-math-in-amm]] — presented as the stableswap example in the AMM-mathematics survey.

## Related
- [[entity-uniswap-v2]] — the constant-product design Curve interpolates toward off-parity.
- [[entity-balancer]] — another CFMM variant in the taxonomy.
- [[concept-constant-function-market-maker]] — the general family it belongs to.
- [[concept-bonding-curve]] — the specialized trading curve it uses.
- [[concept-liquidity-profile]] — the concentration-near-parity shape it produces.
