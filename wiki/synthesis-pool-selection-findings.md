---
title: Pool Selection Findings
layer: core
type: synthesis
origin: thesis
date: 2026-07-22
---

# What Measuring the Pool Universe Found

Before cycle 2 the empirical dataset was four pools, all at the 5bp fee tier, chosen without ever
being measured against the alternatives. Running an explicit discovery pass over the *exact block
grid the existing data sits on* turned up three defects and one structural opportunity. The code
that performed the measurement is described in [[concept-pool-selection-code]]; this page records
what it found and why the findings matter for the thesis.

## The measurement

Aggregate day-level volume and TVL per pool across every fee tier of each candidate pair, over the
1641-block grid the study already occupies (blocks 21102263 to 25038263, spacing 2400, spanning
2024-11-06 to 2026-05-07). The window matters: cumulative lifetime volume, the field a naive query
would reach for, is dominated by whichever tier was liveliest in 2021 and says nothing about which
venue carries flow during the period under study.

Tiers below roughly one percent of both pair volume and pair TVL were dropped as vestigial.
Wherever that cut falls the drop-off is an order of magnitude or more, so the exact threshold is
not load-bearing.

## Finding 1 — one pool was the wrong venue

`USDC_USDT` had been configured at 5bp. Over the study window that pool carries **0.6%** of the
pair's volume; the 1bp pool carries **99.4%**. Every `USDC_USDT` result computed before this cycle
described a vestigial venue rather than the market. This is the most consequential of the three
findings, because nothing in the pipeline would have flagged it: the wrong pool still produces a
well-formed liquidity surface, and the figures look plausible.

`USDC_USDT` is genuinely single-tier once measured. Every other pair in the study is not.

## Finding 2 — fee tiers were never surveyed, and the contrast is the subject

Three of five pairs trade materially on two or three tiers. Restricting the study to one tier per
pair was discarding exactly the comparison the thesis is about: within a single pair the tiers
share one price process but present opposite liquidity-provision economics. In the sharpest case
the 1bp tier runs on the order of 4000 times turnover against roughly 1% of the pair's TVL while
the 30bp tier runs about 28 times turnover against roughly 43% of it. Same asset, same volatility,
same arbitrage flow; very different fee income per unit of capital and very different exposure to
[[concept-adverse-selection]] and [[concept-loss-versus-rebalancing]].

The measured shares now recorded in the configuration:

| Pair | Tiers kept | Volume share |
|---|---|---|
| WETH/USDC | 5bp, 1bp, 30bp | 69.2 / 24.1 / 6.6 |
| WETH/USDT | 1bp, 5bp, 30bp | 49.0 / 29.5 / 21.5 |
| WBTC/WETH | 5bp, 30bp | 84.1 / 15.4 |
| WBTC/USDT | 5bp, 30bp | 71.1 / 28.7 |
| USDC/USDT | 1bp | 99.4 |

Eleven pools across five pairs, every one on the identical block grid.

## Finding 3 — a duplicate masquerading as a distinct pool

`ETH_USDC` was a second dataset over the same pool address as `WETH_USDC`, collected on an
unaligned block window by the older snapshot-era pipeline. It named a *dataset*, not a token
difference: ETH is native, the pool holds WETH, and both have eighteen decimals. Two of the six
plotting jobs were therefore duplicates of two others, rendered over a different and
non-comparable window. It was removed rather than realigned.

## Finding 4 — a candidate that does not exist in practice

`PRIME_USDC` was investigated as a possible fifth pair and excluded: **$653** of total volume
across the entire window. Recorded here so the exclusion is a measurement rather than an omission.

## Why grid alignment is now structural

The dataset's defining property is that every pool sits on the *same* block set. That is what makes
surfaces comparable across pairs and across tiers of one pair; without it, differences between two
heatmaps could be differences in when they were sampled. Two changes make the property hold by
construction rather than by luck: the grid is read back from the stored download instead of being
recomputed from the chain's latest block, and a dedicated verification pass asserts set identity
per pool, plus completeness, sanity, and the absence of orphaned parquets from superseded
selections.

## Consequences for the thesis

- Any `USDC_USDT` result predating this cycle should be treated as void, not as an earlier estimate.
- The unit of analysis is now the pool, not the pair. Comparisons should be stated as
  within-pair-across-tier or across-pair, and the two say different things.
- Fee-tier heterogeneity is available as an axis for the extension work: the tiers of one pair are
  a natural controlled comparison for liquidity-profile shape, price impact, and eventual
  LP-strategy questions.

## Connections

- The code that measured and now guards this: [[concept-pool-selection-code]].
- What is computed on the resulting dataset: [[concept-liquidity-pipeline-code]],
  [[concept-price-impact-code]], [[concept-marginal-price-impact]].
- Theory the tier contrast bears on: [[concept-adverse-selection]],
  [[concept-loss-versus-rebalancing]], [[concept-arbitrage-with-fees]],
  [[concept-concentrated-liquidity]].
- Project map: [[synthesis-thesis-map]].
