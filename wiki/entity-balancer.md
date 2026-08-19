---
title: Balancer
layer: core
type: entity
origin: thesis
date: 2026-07-19
---

# Balancer

A geometric-mean market maker (G3M) that generalizes the constant-product design to weighted, multi-asset pools.

## Role
- Implements a weighted geometric-mean invariant, letting a pool hold several assets with configurable weights rather than a 50/50 pair.
- Provides the thesis's canonical example of a geometric-mean market maker beyond the two-asset constant-product case, extending the CFMM/bonding-curve taxonomy.

## Appears in
- [[source-clmm-mathematical-framework]] — cited as a G3M instance within the market-maker framework.
- [[source-wang-math-in-amm]] — used as the geometric-mean example in the AMM-mathematics survey.
- [[source-rtw26-cfmm-liquidity-pricing-hedging]] — referenced as a CFMM variant the pricing theory covers.

## Related
- [[entity-uniswap-v2]] — the constant-product special case of the geometric-mean family.
- [[entity-curve]] — another CFMM variant specialized for correlated assets.
- [[concept-geometric-mean-market-maker]] — the invariant class it implements.
- [[concept-constant-function-market-maker]] — the general family it belongs to.
- [[concept-bonding-curve]] — the trading curve its invariant defines.
