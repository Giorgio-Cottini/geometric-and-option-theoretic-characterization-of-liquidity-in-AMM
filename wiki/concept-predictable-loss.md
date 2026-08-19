---
title: Predictable Loss
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Predictable Loss

Predictable loss (PL) is the component of a concentrated-liquidity provider's wealth decay caused by the convexity of the constant-product trading function and by the opportunity cost of locking assets inside a bounded price range. It is the concentrated-liquidity analogue of loss-versus-rebalancing: both quantities isolate the curvature-driven depreciation of LP wealth from the fee income that offsets it.

## Details
- PL sits inside a three-way wealth decomposition: position value (subject to PL), fee income (subject to a stochastic pool fee rate `pi` with CIR-type dynamics and a concentration cost that penalizes narrow spreads), and rebalancing cost.
- Wealth dynamics (Eq. 16 of the source): `d x~_t = (1/delta_t)(4 pi_t - sigma^2/2) x~_t dt + mu_t rho(delta_t,mu_t) x~_t dt + sigma rho(delta_t,mu_t) x~_t dW_t - (gamma/delta_t^2) x~_t dt`. The term `sigma^2/(2 delta_t)` is the predictable-loss drag; it grows as the range narrows and as volatility rises.
- The optimal range width balances fee revenue, which pushes the range narrower, against predictable loss and concentration risk, which push it wider. See [[concept-optimal-range-width]] for the closed-form spread that results.
- PL extends impermanent loss to concentrated liquidity: full-range impermanent loss becomes a strict lower bound, and PL adds the extra opportunity cost of committing capital to a bounded range that the price can exit.
- PL is deterministic in expectation given the volatility path, the same "predictable" property that gives loss-versus-rebalancing its name: it accrues at a known rate rather than being realized only at discrete arbitrage trades.

## Appears in
- [[source-cartea-predictable-loss-optimal-lp]] — defines PL, derives the wealth dynamics that contain it, and solves for the range that trades it off against fee income.

## Related
- [[concept-loss-versus-rebalancing]] — the full-range analogue; PL is its concentrated-liquidity sibling, both rooted in the same curvature-driven depreciation of LP wealth.
- [[concept-impermanent-loss]] — PL generalizes impermanent loss by adding the opportunity cost of range confinement.
- [[concept-concentrated-liquidity]] — the mechanism (bounded price range) that makes PL distinct from full-range LVR.
- [[concept-lp-pnl-decomposition]] — PL is the loss term in the LP wealth decomposition alongside fee income and rebalancing cost.
- [[concept-optimal-range-width]] — the control problem that PL enters as one of the three balancing forces.
- [[concept-stochastic-control]] — PL is derived inside a stochastic-control problem over the range spread.
