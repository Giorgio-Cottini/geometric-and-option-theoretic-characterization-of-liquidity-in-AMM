---
title: Uniswap V3
layer: core
type: entity
origin: thesis
date: 2026-07-19
---

# Uniswap v3

A concentrated-liquidity automated market maker (decentralized exchange) on Ethereum, and the empirical backbone of the thesis's AMM analysis.

## Role
- The dominant concentrated-liquidity DEX: liquidity providers allocate capital to bounded price ranges (ticks) rather than the full price axis, producing a non-uniform liquidity profile.
- Its on-chain data supplies the empirical liquidity surfaces, trader behavior, and microstructure the thesis studies, and its tick mechanism is the concrete instance of the CLMM theory.

## Appears in
- [[source-clmm-mathematical-framework]] — the protocol whose mechanism the CLMM framework formalizes.
- [[source-liquidity-surfaces-uniswap-v3]] — the source of the empirical liquidity surfaces.
- [[source-bis-decentralized-dealers]] — analyzed as the venue in the BIS decentralized-dealers study.
- [[source-clustering-v3-traders]] — the venue whose traders are clustered.
- [[source-wang-bocconi-2]] — the focus of the second Bocconi lecture.
- [[source-rtw26-cfmm-liquidity-pricing-hedging]] — used for empirical grounding of the pricing/hedging framework.

## Related
- [[entity-uniswap-v2]] — the constant-product predecessor protocol.
- [[concept-concentrated-liquidity]] — the mechanism it pioneered.
- [[concept-uniswap-v3-ticks]] — its discrete price-range structure.
- [[concept-liquidity-profile]] — the non-uniform liquidity distribution it produces.
- [[concept-liquidity-surface]] — the empirical object built from its data.
- [[concept-just-in-time-liquidity]] — a strategic behavior enabled by its design.
