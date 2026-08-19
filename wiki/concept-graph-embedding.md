---
title: Graph Embedding
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Graph Embedding

Graph embedding represents each Uniswap v3 trader as a weighted transaction graph and maps that graph to a fixed-length vector using a modified graph2vec, in the node2vec / word2vec lineage. The embedding places behaviourally similar traders near one another so they can be clustered.

## Details
- Per-trader graph: nodes are tokens/pools/counterparties and weighted edges encode the trader's transaction relationships and volumes.
- graph2vec learns a vector for a whole graph (here, one graph per trader), extending node2vec's per-node embeddings.
- Lineage: word2vec (skip-gram over word contexts) → node2vec (random-walk contexts over a graph) → graph2vec (document-analogy over rooted subgraphs) → the modified variant used here.
- The modification adapts the standard scheme to the weighted, financial structure of transaction graphs.
- Output embeddings are the feature space in which unsupervised clustering discovers behavioural species.

## Appears in
- [[source-clustering-v3-traders]] — introduces the modified graph2vec pipeline that embeds trader transaction graphs prior to clustering.

## Related
- [[concept-trader-clustering]] — the downstream task the embeddings enable.
- [[concept-market-microstructure]] — the heterogeneous-agent structure the embeddings help quantify.
- [[entity-uniswap-v3]] — the source of the transaction graphs being embedded.
