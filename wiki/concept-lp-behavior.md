---
title: Lp Behavior
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# LP Behavior

LP behavior describes how liquidity providers act on a concentrated-liquidity DEX, split between sophisticated players and retail providers. A provider's profitability is fee yield minus impermanent loss minus gas costs, and the sophisticated minority captures most of the positive economics.

## Details
- Profitability decomposition: fees earned − impermanent loss (value lost to price moves versus holding) − gas/transaction costs.
- Sophisticated LPs actively manage ranges, rebalance, and time entry/exit; retail LPs tend to set wide passive ranges and leave them.
- Sophisticated players dominate: they concentrate liquidity tightly around the price, harvest a disproportionate share of fees, and drive most volume-weighted provision.
- Retail providers frequently end up net-negative once impermanent loss and gas are netted against modest fee income.
- The behavioural split is a form of agent heterogeneity, making the LP side resemble a dealer market with a professional core.

## Appears in
- [[source-bis-decentralized-dealers]] — empirically separates sophisticated from retail LPs and shows the sophisticated group earns the profits while dominating provision.

## Related
- [[concept-just-in-time-liquidity]] — the archetypal sophisticated-LP tactic driving the dominance result.
- [[concept-impermanent-loss]] — the core cost term subtracted from fee yield in the profitability equation.
- [[concept-loss-versus-rebalancing]] — a sharper measure of the adverse-selection cost LPs incur.
- [[concept-market-microstructure]] — the dealer/heterogeneous-agent frame LP behaviour instantiates.
- [[concept-concentrated-liquidity]] — the mechanism sophisticated LPs exploit to concentrate fee capture.
- [[entity-bank-for-international-settlements]] — author of the study characterizing LP behaviour.
- [[concept-nash-equilibrium-lps]] — the equilibrium benchmark this page's empirical description
  had no counterpart for until 2026-08-04. It answers which distribution survives every provider
  optimizing at once, against which observed behaviour can be measured.
- [[concept-waterfilling-allocation]] — the structure that equilibrium takes, and a directly
  implementable allocation rule.
- [[concept-optimal-liquidity-provision]] — the hub for what a provider should do, as against what
  providers are observed to do here.

## Open tension

[[source-zeller-stochastic-concentration]] reports that its stochastic optimizer selects a
near-full-range position, and that narrow ranges lose heavily on the pool and window it tests.
This page records the opposite empirical pattern, that sophisticated providers concentrate tightly
and capture most fee income. The two claims are not adjudicated. They differ in population, in
objective, and in sample: the optimizer maximizes terminal wealth under one price model on one
pool over a period of strong appreciation, while the record here is revealed behaviour across the
venue. Neither page has been edited to agree with the other.
