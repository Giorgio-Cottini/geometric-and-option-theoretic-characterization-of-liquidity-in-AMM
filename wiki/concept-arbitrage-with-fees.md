---
title: Arbitrage With Fees
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Arbitrage with Fees

The extension of AMM arbitrage analysis to include trading fees and discrete block times. Fees create a no-trade region: the external price must move beyond a fee-determined threshold before arbitrage is profitable, so trades happen only intermittently. This rescales the loss-versus-rebalancing LPs bear by a probability of trade.

## Details
- No-trade band: with proportional fee γ, the AMM price can drift within a bid–ask corridor of relative width ~γ before an arbitrageur trades; inside the band the LP is not picked off.
- Block arrivals are modelled discretely (e.g. Poisson block times), so between blocks price may move freely and only the accumulated deviation matters.
- Effective LP loss ≈ P_trade · (fee-less LVR), where P_trade is the probability that price exits the no-trade band within a block — fees and faster blocks both shrink P_trade and hence the loss.
- Fast-block regime: as block time → 0, the per-block deviation shrinks, arbitrage is triggered less often per unit LVR, and LP loss falls — a design argument for lower latency and appropriately set fees.
- Nets against fee income: fees both deter adverse trades and compensate the LP, so the optimal fee balances deterrence against volume.

## Appears in
- [[source-amm-arbitrage-profits-fees]] — derives arbitrage profits and LP loss under fees and discrete blocks, and the probability-of-trade rescaling of LVR.

## Related
- [[concept-loss-versus-rebalancing]] — rescaled by the probability of trade under fees.
- [[concept-adverse-selection]] — fees bound the adverse-selection loss.
- [[concept-lp-pnl-decomposition]] — fee income is the offsetting term.
- [[concept-market-microstructure]] — block timing and fees are microstructure levers.
- [[concept-constant-function-market-maker]] — the venue where the arbitrage occurs.
- [[entity-jason-milionis]] — co-author of the fees analysis.
- [[entity-ciamac-moallemi]] — co-author.
- [[entity-tim-roughgarden]] — co-author.
- [[entity-anthony-lee-zhang]] — co-author.
