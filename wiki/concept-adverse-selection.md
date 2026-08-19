---
title: Adverse Selection
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Adverse Selection

The loss passive liquidity providers suffer because informed arbitrageurs trade against them precisely when the AMM's quote is stale and mispriced. Because the AMM cannot update its price between blocks, arbitrageurs always take the profitable side, so the LP is systematically "picked off". It is the microstructure root of impermanent loss and LVR.

## Details
- Mechanism: when the external (CEX) price moves, the AMM quote lags; an arbitrageur buys the underpriced asset / sells the overpriced one until the AMM price re-aligns, capturing the difference. This is the AMM analogue of "sniping" in the Budish–Cramton–Shim HFT model.
- The LP's counterparty is, on the marginal trade, always better informed about the true price — the classic Glosten–Milgrom adverse-selection cost adapted to on-chain dealers.
- Aggregated over time, adverse selection accumulates as loss-versus-rebalancing; it is offset (fully or partially) only by fees paid by uninformed noise traders.
- Design responses: dynamic/variance-scaled fees, faster blocks, oracle re-quoting, or auctioning the right to arbitrage so LPs recapture the value.

## Appears in
- [[source-amm-loss-versus-rebalancing]] — frames LVR as the price of adverse selection against LPs.
- [[source-bis-decentralized-dealers]] — analyses v3 LPs as decentralized dealers bearing adverse selection.

## Related
- [[concept-loss-versus-rebalancing]] — the running measure of adverse-selection cost.
- [[concept-impermanent-loss]] — state-function view of the same loss.
- [[concept-arbitrage-with-fees]] — fees create a no-trade band that limits adverse selection.
- [[concept-market-microstructure]] — the field this cost belongs to.
- [[concept-lp-behavior]] — how LPs respond to adverse selection.
- [[concept-just-in-time-liquidity]] — a strategy that exploits fee capture around adverse selection.
- [[entity-bank-for-international-settlements]] — author of the decentralized-dealers analysis.
