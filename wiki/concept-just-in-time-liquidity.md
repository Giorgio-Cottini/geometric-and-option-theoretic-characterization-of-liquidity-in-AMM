---
title: Just in Time Liquidity
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Just-in-Time Liquidity

Just-in-time (JIT) liquidity is a sophisticated LP strategy in which a provider adds a large, tightly concentrated position immediately before a big incoming trade to capture its fees, then withdraws the liquidity in the same or next block. It converts a passive fee-earning role into an active, event-driven one.

## Details
- Mechanics: on seeing a large pending swap, the LP mints a narrow-range position around the current price, earns the swap's fee, then burns the position — often within one block.
- Requires sophistication: mempool monitoring, tight range placement, and fast execution, so it is the domain of professional players.
- Effect on other LPs: JIT providers dilute the fee share of passive in-range LPs precisely on the most profitable trades.
- Minimizes inventory risk: capital is exposed to price movement for a minimal window, so impermanent loss is nearly eliminated while fees are still collected.
- A concrete illustration of the sophisticated-versus-retail divide and of DEX dealer-like behaviour.

## Appears in
- [[source-bis-decentralized-dealers]] — presents JIT liquidity as a hallmark tactic of the sophisticated LPs that dominate provision.

## Related
- [[concept-lp-behavior]] — JIT is the extreme case of sophisticated-LP behaviour.
- [[concept-concentrated-liquidity]] — the tick/range mechanism JIT exploits to place capital exactly at the price.
- [[concept-impermanent-loss]] — the cost JIT nearly eliminates by holding for a single block.
- [[concept-market-microstructure]] — the dealer-market frame in which JIT market-making sits.
- [[concept-uniswap-v3-ticks]] — the tick grid enabling the narrow JIT ranges.
