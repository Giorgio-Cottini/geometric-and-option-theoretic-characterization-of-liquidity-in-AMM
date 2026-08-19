---
title: Deribit
layer: core
type: entity
origin: thesis
date: 2026-07-19
---

# Deribit

A leading centralized crypto derivatives exchange, dominant in Bitcoin and Ether options, used as the source of option-market data in the thesis.

## Role
- The main venue for liquid ETH option quotes, from which implied-volatility information is drawn.
- Supplies the market-implied volatility benchmark against which the thesis compares the implied volatility of impermanent loss derived from the CFMM pricing/hedging framework.

## Appears in
- [[source-rtw26-cfmm-liquidity-pricing-hedging]] — source of ETH option quotes for the impermanent-loss implied-volatility empirics.

## Related
- [[entity-uniswap-v3]] — the on-chain AMM whose LP payoffs are compared against Deribit option pricing.
- [[concept-implied-volatility-surface]] — the market-implied object read from its quotes.
- [[concept-impermanent-loss]] — the AMM payoff whose implied volatility is benchmarked against its options.
- [[concept-lp-pnl-decomposition]] — the payoff decomposition the benchmark validates.
