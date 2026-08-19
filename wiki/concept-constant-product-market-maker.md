---
title: Constant Product Market Maker
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Constant Product Market Maker (CPMM)

The canonical CFMM in which the product of reserves is held constant: x·y = k. Written in bonding-function form as f(x, y) = sqrt(xy) = L, the mechanism used by Uniswap v2. It provides liquidity across the entire price range (0, ∞).

## Details
- Invariant: x·y = k = L²; bonding function f = sqrt(xy) = L.
- Spot price: P = y/x (marginal price of x in units of y).
- Reserves as functions of price: x(P) = L/sqrt(P), y(P) = L·sqrt(P).
- Value function: V(P) = P·x(P) + y(P) = 2L·sqrt(P), which is concave in P — its concavity is exactly the source of impermanent loss / LVR for a v2 LP.
- Pool value scales with the square root of price, so an LP is implicitly short volatility relative to a 50/50 hold.

## Appears in
- [[source-wang-math-in-amm]] — CPMM derived as the base case of the general CFMM/G3M theory.
- [[source-wang-bocconi-1]] — CPMM (Uniswap v2) presented as the introductory market-maker model.

## Related
- [[concept-constant-function-market-maker]] — CPMM is the special case f = sqrt(xy).
- [[concept-geometric-mean-market-maker]] — CPMM is the equal-weight (w = 1/2) member.
- [[concept-bonding-curve]] — the xy = k hyperbola.
- [[concept-concentrated-liquidity]] — Uniswap v3 concentrates CPMM liquidity into ranges.
- [[concept-impermanent-loss]] — closed form is cleanest for the CPMM.
- [[concept-loss-versus-rebalancing]] — LVR has a simple form under CPMM.
- [[entity-uniswap-v2]] — the reference CPMM deployment.
