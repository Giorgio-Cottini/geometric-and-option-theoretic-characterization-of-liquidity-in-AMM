---
title: Market Microstructure
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Market Microstructure

Market microstructure studies how the concrete trading mechanism — the agents, their roles, and the rules of exchange — shapes prices and liquidity. In decentralized exchanges, a dealer/market-maker structure and a population of heterogeneous agents emerge on-chain despite the absence of a centralized order book.

## Details
- Classic microstructure centres on dealers and market makers who post prices and absorb order flow; DEXs reproduce this division through liquidity providers (makers) and liquidity takers (traders).
- Agents are heterogeneous: they differ in sophistication, capital, information, and strategy, so aggregate behaviour is not a single representative trader.
- On-chain data makes the microstructure directly observable — every quote, position, and trade is recorded, unlike opaque dealer markets.
- A de facto dealer class arises: a small set of sophisticated market makers concentrates provision and captures most of the economics.
- The framework connects the mechanism (AMM curves, ticks, fees) to outcomes (spreads, adverse selection, provider profitability).

## Appears in
- [[source-bis-decentralized-dealers]] — documents how a dealer-like market-maker structure emerges among Uniswap v3 liquidity providers.
- [[source-clustering-v3-traders]] — reveals heterogeneous trader types, the taker side of the microstructure, via behavioural clustering.

## Related
- [[concept-lp-behavior]] — the maker-side behaviour that populates the DEX dealer structure.
- [[concept-trader-clustering]] — the taker-side heterogeneity made explicit as behavioural species.
- [[concept-just-in-time-liquidity]] — a dealer strategy that exemplifies sophisticated market-making on-chain.
- [[concept-adverse-selection]] — the informational cost dealers bear, central to microstructure theory.
- [[entity-bank-for-international-settlements]] — author of the decentralized-dealers study.
- [[entity-uniswap-v3]] — the venue whose microstructure is analyzed.
- [[concept-glosten-milgrom-model]] — the classical model of a maker pricing against informed
  order flow, adapted to yield a differential equation for the optimal curve.
- [[concept-myersonian-mechanism-design]] — the mechanism-design route to the same question,
  treating the provider as a monopolist setting a demand curve.
- [[concept-optimal-liquidity-provision]] — the hub in which microstructure is one of six routes
  to the shape of liquidity.
