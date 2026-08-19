---
title: Trader Clustering
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Trader Clustering

Trader clustering groups Uniswap v3 liquidity takers into a small number of interpretable behavioural species, learned from their activity across multiple pools. It turns raw on-chain transaction histories into a taxonomy of trader types.

## Details
- Input is multi-pool activity: each address's swaps across many pools, not a single-pool footprint.
- Each trader is represented as a feature/embedding vector, then partitioned by unsupervised clustering into discrete groups.
- Clusters are meant to be interpretable — e.g. arbitrageurs, retail swappers, high-frequency routers — rather than opaque partitions.
- The species view exposes the heterogeneity of the taker side of the DEX, mirroring the maker-side split among LPs.
- Provides a data-driven behavioural map that can feed downstream models of flow, adverse selection, and liquidity demand.

## Appears in
- [[source-clustering-v3-traders]] — the core study that embeds and clusters Uniswap v3 traders into behavioural species.

## Related
- [[concept-graph-embedding]] — the representation step that turns each trader into a vector before clustering.
- [[concept-market-microstructure]] — the heterogeneous-agent frame trader clustering makes concrete on the taker side.
- [[concept-lp-behavior]] — the analogous maker-side heterogeneity between sophisticated and retail participants.
- [[concept-adverse-selection]] — informed trader types the clustering can help identify.
- [[entity-uniswap-v3]] — the exchange whose traders are clustered.
