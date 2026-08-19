---
title: Thesis Map
layer: core
type: synthesis
origin: thesis
date: 2026-07-22
---

# Thesis Knowledge Map — CFMM Liquidity Provision

A synthesis of the thesis's reading and codebase: pricing and hedging for liquidity
provision in Constant Function Market Makers, applied to Uniswap V3. It threads the
literature into one argument and points at the code that implements it.

## The spine: an LP position is a short option portfolio

The organizing idea across the core papers is [[concept-reserve-option-duality]]: a
[[concept-constant-function-market-maker]] liquidity position, re-coordinatized by price
and [[concept-intrinsic-liquidity]], is a (short) strip of vanilla options. The anchor
paper [[source-rtw26-cfmm-liquidity-pricing-hedging]] (by [[entity-tai-ho-wang]],
[[entity-shen-ning-tung]], [[entity-jimmy-risk]]) builds arbitrage-free pricing, hedging,
and an implied-volatility characterization of impermanent loss from this duality — and is
what the [[source-thesis-codebase]] replicates and extends.

## Loss decomposition: IL, LVR, fees

[[concept-impermanent-loss]] (loss-versus-holding) splits into the non-negative running
cost [[concept-loss-versus-rebalancing]] plus a mean-zero market term. LVR was introduced
by [[source-quantifying-loss-in-amms]] and [[source-amm-loss-versus-rebalancing]]
([[entity-jason-milionis]], [[entity-ciamac-moallemi]], [[entity-tim-roughgarden]],
[[entity-anthony-lee-zhang]]) via the [[concept-rebalancing-strategy]] and
[[concept-adverse-selection]], giving the [[concept-lp-pnl-decomposition]]
(P&L = Rebalancing − LVR + Fees). [[source-amm-arbitrage-profits-fees]] adds fees and
discrete blocks ([[concept-arbitrage-with-fees]]). [[source-clmm-mathematical-framework]]
and the [[source-wang-math-in-amm]] / [[source-wang-bocconi-1]] / [[source-wang-bocconi-2]]
lectures generalize the geometry ([[concept-bonding-curve]],
[[concept-constant-product-market-maker]], [[concept-geometric-mean-market-maker]]) and add
optimal provision via [[concept-stochastic-control]].

## Two surfaces, one method

The thesis studies two surfaces that share a decomposition tool, [[concept-functional-pca]]:
- the [[concept-liquidity-surface]] over [[concept-uniswap-v3-ticks]]
  ([[source-liquidity-surfaces-uniswap-v3]]) under [[concept-concentrated-liquidity]];
- the [[concept-implied-volatility-surface]] ([[source-dynamics-implied-vol-surfaces]]),
  with arbitrage-free parametrizations ([[concept-svi-parametrization]],
  [[concept-static-arbitrage]], [[concept-iv-term-structure-arbitrage]]) and
  [[concept-rough-volatility]] / [[concept-multifractal-volatility]] /
  [[concept-scaling-renormalization]] models of its driver.

## Who provides liquidity

Empirically, provision is concentrated in sophisticated players ([[concept-lp-behavior]],
[[concept-just-in-time-liquidity]]) — [[source-bis-decentralized-dealers]]
([[entity-bank-for-international-settlements]]) — and takers cluster into behavioural
species ([[concept-trader-clustering]], [[concept-graph-embedding]]) per
[[source-clustering-v3-traders]]; both are facets of DeFi
[[concept-market-microstructure]] on [[entity-uniswap-v3]].

## From theory to code

[[source-thesis-codebase]] implements the pipeline: extract the
[[concept-liquidity-profile]] from tick data → build option proxies → compute pathwise IL,
the LVR proxy, and the IL replication price → invert to Black–Scholes implied volatility
(aggregate and fine-structure surface). The structural code graph is parked in
`graphify-out/` (query via the graphify skill; curate later with `ingest-graphify`).

## Code layer
- [[source-thesis-codebase]] — computational overview of the implementation.
- [[synthesis-codebase-architecture]] — structural call-graph spine (runners → pipelines →
  math_core → graphics), from the parked code graph.
- [[concept-liquidity-pipeline-code]] — the liquidity reconstruction / surface / LVsP code path.
- [[concept-price-impact-code]] — the marginal price-impact lane, a read-only sibling of the
  frozen builders.
- [[concept-pool-selection-code]] — pool discovery, pool-keyed configuration, and the grid
  integrity check that defines the dataset.

## Empirical layer
- [[synthesis-pool-selection-findings]] — which pools and fee tiers actually carry flow over the
  study window, and the three defects that measurement exposed in the earlier four-pool dataset.
- [[concept-marginal-price-impact]] — the first extension quantity derived beyond the replicated
  surfaces: impact as the reciprocal of depth, on an economically meaningful scale.

## Second pillar: the shape question

This map describes the region's original argument, pricing and hedging for liquidity provision.
On 2026-08-04 a second pillar was added, and this map is the spine it extends rather than
replaces. The question is the optimal or equilibrium shape of the liquidity profile, the first
open problem on the closing slide of [[source-wang-math-in-amm]], pursued as a computational
problem. Its entry point is [[synthesis-optimal-liquidity-shape]] and its hub is
[[concept-optimal-liquidity-provision]].

The connection to this map is direct. Everything above establishes that reserves, value, loss and
fee income are linear in the liquidity profile `L`. The second pillar asks which `L` to choose,
and by which criterion. [[source-rtw26-cfmm-liquidity-pricing-hedging]] already holds one worked
instance in its LVR-neutral profile, so the pillar starts from this map's own anchor paper rather
than from a blank page.

## Open threads
- Thesis prose (`latex/chapters/`) is still empty — the written narrative and results are pending.
- Extension to other CFMM designs ([[entity-balancer]], [[entity-curve]]) is open.
- Linking observed [[concept-rough-volatility]] of the underlying to the LP's implied-vol
  surface is a natural bridge between the two halves of the reading.
- Which of the three candidate experiments in [[synthesis-optimal-liquidity-shape]] becomes the
  extension chapter is undecided. All three run against the pipeline this map describes.
