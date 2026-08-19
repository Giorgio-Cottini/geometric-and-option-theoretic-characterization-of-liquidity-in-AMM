---
title: Reserve Option Duality
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Reserve–Option Duality

The equivalence between a CFMM / concentrated-liquidity LP position and a (short) portfolio of vanilla options. Because the pool value V(P) is a convex function of price, it can be spanned by call and put payoffs via the Carr–Madan formula, so being an LP is economically the same as being short a strip of options — most simply, a short straddle.

## Details
- Carr–Madan spanning: any twice-differentiable payoff V(P) = V(P₀) + V'(P₀)(P−P₀) + ∫ V''(K)·(K−P)₊ dK (puts) + ∫ V''(K)·(P−K)₊ dK (calls). The LP's value curve is reproduced by holding options with weights V''(K) — its second derivative.
- Since −V'' ≥ 0 for a CFMM, the LP holds a short-gamma (short-convexity) position: it loses when price moves either way, exactly the short-straddle / short-option payoff.
- A concentrated-liquidity position maps to options struck within its price range; the liquidity profile L(p) is (up to a kernel) the option-weight density V''(K), so choosing L(p) is choosing an option book.
- Consequences: impermanent loss = the option position's negative payoff; LVR = the running cost of the embedded short gamma (its "theta"); LP positions can be priced and hedged with option-replication techniques.

## Appears in
- [[source-rtw26-cfmm-liquidity-pricing-hedging]] — prices and hedges LP positions by mapping them to option portfolios.
- [[source-wang-math-in-amm]] — develops the spanning / option-replication correspondence for CFMMs.
- [[source-wang-bocconi-2]] — advanced lecture on the option-portfolio and liquidity-profile duality.
- [[source-quantifying-loss-in-amms]] — short-straddle analogy for the LP payoff.

## Related
- [[concept-liquidity-profile]] — profile plays the role of the option-weight density.
- [[concept-impermanent-loss]] — the short-option payoff realized.
- [[concept-loss-versus-rebalancing]] — cost of the embedded short gamma.
- [[concept-bonding-curve]] — convexity of the value curve enables spanning.
- [[concept-implied-volatility-surface]] — options view links LP pricing to IV.
- [[concept-concentrated-liquidity]] — maps to options struck within a range.
- [[concept-stochastic-control]] — hedging the replicated option book.
