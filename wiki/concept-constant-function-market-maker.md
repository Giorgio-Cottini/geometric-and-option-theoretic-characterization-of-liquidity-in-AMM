---
title: Constant Function Market Maker
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Constant Function Market Maker (CFMM)

An automated market maker whose reserves (x, y) are constrained to a level set of a bonding function, f(x, y) = L. Every trade must keep the pool on this curve, so the function f alone defines the exchange behaviour. CFMMs are the dominant on-chain liquidity mechanism.

## Details
- Feasible set: C = {(x, y) ∈ R²₊ : f(x, y) = L}, with invariant (liquidity) constant L.
- f is typically assumed monotone increasing in each reserve, concave (or its level set convex), and positively homogeneous / scaling: f(λx, λy) = λ f(x, y), so doubling reserves doubles L.
- Spot (marginal) price of x in units of y: P = f_x / f_y (ratio of partial derivatives), i.e. minus the slope of the bonding curve.
- Pool value function: V(P) = min over (x, y) ∈ C of (P·x + y); its convexity in P drives impermanent loss and loss-versus-rebalancing.
- Special cases: constant-product (f = sqrt(xy)), geometric-mean / weighted (f = x^w y^(1−w)), constant-sum, and stableswap curves.

## Appears in
- [[source-amm-loss-versus-rebalancing]] — CFMM feasible set and value function V(P) are the base objects for defining LVR.
- [[source-quantifying-loss-in-amms]] — same CFMM formalism used to quantify LP loss.
- [[source-amm-arbitrage-profits-fees]] — extends CFMM arbitrage analysis to include fees.
- [[source-clmm-mathematical-framework]] — CFMM generalized to concentrated (per-tick) liquidity.
- [[source-wang-math-in-amm]] — develops the full mathematical theory of CFMMs (bonding curve, price, liquidity).
- [[source-wang-bocconi-1]] — lecture treatment of CFMM fundamentals.
- [[source-rtw26-cfmm-liquidity-pricing-hedging]] — pricing and hedging of LP positions within the CFMM framework.

## Related
- [[concept-constant-product-market-maker]] — the canonical CFMM instance (f = sqrt(xy)).
- [[concept-geometric-mean-market-maker]] — weighted-power CFMM generalization.
- [[concept-bonding-curve]] — the level set f(x,y)=L that defines a CFMM.
- [[concept-concentrated-liquidity]] — CFMMs restricted to price ranges.
- [[concept-liquidity-profile]] — distribution of L across prices.
- [[concept-impermanent-loss]] — loss induced by V(P) convexity.
- [[concept-loss-versus-rebalancing]] — running adverse-selection cost for a CFMM LP.
- [[concept-reserve-option-duality]] — CFMM reserves as an option portfolio.
- [[entity-uniswap-v2]] — reference constant-product CFMM.
- [[entity-balancer]] — reference geometric-mean CFMM.
