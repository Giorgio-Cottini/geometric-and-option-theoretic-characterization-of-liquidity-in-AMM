---
title: Uniswap V2
layer: core
type: entity
origin: thesis
date: 2026-07-19
---

# Uniswap v2

A constant-product automated market maker (decentralized exchange) whose `x * y = k` invariant is the canonical simple CFMM.

## Role
- The reference constant-product market maker: liquidity is spread uniformly across all prices, giving a clean closed form for reserves, prices, and LP payoffs.
- Serves as the baseline CFMM against which the thesis frames impermanent loss, loss-versus-rebalancing, and the concentrated-liquidity generalization.

## Appears in
- [[source-amm-loss-versus-rebalancing]] — the constant-product setting in which LVR is derived.
- [[source-wang-math-in-amm]] — the canonical example in the AMM-mathematics survey.

## Related
- [[entity-uniswap-v3]] — its concentrated-liquidity successor.
- [[concept-constant-product-market-maker]] — the invariant it implements.
- [[concept-constant-function-market-maker]] — the general class it belongs to.
- [[concept-bonding-curve]] — the trading curve defined by its invariant.
- [[concept-impermanent-loss]] — the LP cost first illustrated on this design.
- [[concept-loss-versus-rebalancing]] — the refined LP cost derived in this setting.
