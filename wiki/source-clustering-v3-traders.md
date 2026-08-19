---
title: Clustering V3 Traders
layer: core
type: source
origin: thesis
source_path: "articles/LPs/Clustering Uniswap v3 traders from their activity.pdf"
source_kind: paper
date: 2026-07-19
---

# Clustering Uniswap v3 Traders from Their Activity on Multiple Liquidity Pools, via Novel Graph Embeddings

The paper proposes a systematic filtration to extract a tractable sub-universe of highly interconnected Uniswap v3 liquidity pools, then introduces a novel weighted extension of the graph2vec embedding to cluster liquidity takers into seven interpretable behavioural "species".

**Authors / venue / year:** Deborah Miori, Mihai Cucuringu (Mathematical Institute & Department of Statistics, University of Oxford; The Alan Turing Institute; Oxford-Man Institute of Quantitative Finance); Digital Finance (2024) 6:113-143, Springer; received Jan 2023, published 30 Jan 2024. Open Access (CC BY 4.0).

## Key points
- Uniswap v3 has >6000 pools, most highly illiquid; analysing the full ecosystem is computationally intractable, so the paper first extracts a tractable, maximally interconnected sub-universe of pools.
- The filtration (Fig. 3) narrows >6000 pools -> 1,344 (>=1000 txns) -> 629 (tokens in >=3 pools) -> 282 (USD locked >=1,000,000) and then applies network-based (interconnectedness) filters to reach a final set of 34 pools for case A (Jan-June 2022).
- Interconnectedness is measured via common liquidity takers ("origins"), common smart contracts ("senders"), and "bridge" transactions (a token bought in one pool then sold in another within the same multi-swap transaction, indicating arbitrage/routing flow).
- Each liquidity taker (LT) is represented by a fully-connected weighted "transaction graph" whose nodes are the LT's executed swaps (labelled by pool) and whose edge weights encode elapsed time between transactions.
- The NLP-inspired graph2vec algorithm is extended to the weighted, complete-graph setting via a custom cut-value neighbour-sampling rule, producing an embedding per LT.
- k-means++ clustering (with elbow method) on the 16-dimensional embeddings yields seven clusters of LTs for case A, interpretable via trading attributes: preference for exotic assets vs stablecoins, trading frequency, and tolerance for higher fees.
- Clusters are stable across sub-periods (measured via Adjusted Rand Index), and the embeddings are agnostic to USD trade value (they depend only on time structure and pool labels).

## Notable claims & data
- Uniswap v3 constant-product mechanism: (x - Delta x) * (y + (1 - gamma/10^6) Delta y) = x*y = k; instantaneous exchange rate Z = x/y. feeTier gamma in {100, 500, 3000, 10000} basis-point-scaled values (i.e. 1, 5, 30, 100 bps).
- Data via The Graph (Uniswap v3 subgraph) and Etherscan; case A = 6-month window Jan-June 2022, plus sub-cases B1/B2 (3-month) and C1/C2/C3 (2-month).
- Final interconnected pool set for case A: 34 pools (out of the 282 candidates); 22-node giant component after adding bridge-transaction nodes; pools with highest eigenvector centrality are dominated by WETH-vs-stablecoin pairs (routing hubs); stablecoins, WETH and WBTC dominate the token landscape.
- Transaction graph G_txn = (S, T, W): complete weighted graph, node labels l_s from alphabet L identifying the pool of each swap; edge weight w_sr = elapsed seconds Delta t between swaps s, r.
- Cut-value C(w_sr) = H(f^scal(w_sr)) / H(f^scal(min W)) with H a half-normal (sqrt(2/pi) exp(-w^2/2)) and f^scal a shifted/scaled feature; shortest edges kept with probability 1, longer times dropped (e.g. ~40% probability at ~5 minutes apart). WL relabeling depth set to 1 (not 2).
- Embedding stability: ARIs ~0.75 for 8-vs-{16,32,64} dim clusterings, ~0.90 for 16-vs-{32,64}; 16-dimensional embedding chosen. Optimal number of LT clusters = seven for case A (six and seven for B1/B2).
- Final LT counts after thresholds (min 60, max 15,000 txns for case A): 3,415 LTs for case A; cluster sizes 304/142/512/978/379/186/914.
- Cluster interpretation (case A): groups 0/1 focus on exotic cryptocurrencies (group 1 accepts very high fees, high urgency); groups 2/3 trade stablecoins more than usual (routing/arbitrage across SS pools); groups 4/6 more active on ECOSYS pools (group 6 = cautious retail, low fee 500, waits longer, loses money; group 4 = ~16% also act as LPs, more professional); group 5 = eclectic, active, thrifty LTs concentrated in cheap feeTier 500, smallest median time between transactions ("smartest investors").
- Pool typology adapted from Heimbach et al.: "SS" (both stablecoins), "ECOSYS" (stablecoins or BTC/ETH-pegged), "EXOTIC" (remaining volatile tokens). A later pool-clustering analysis finds the SS/ECOSYS/EXOTIC split does not hold when full pool dynamics (consumption + provision + price) are considered.
- Only ~20% of addresses appear across all cases A/B1/B2 (agents reuse/rotate wallets, obscuring behaviour).

## Open questions
- Connection to CFMM LP behaviour: the paper mainly clusters liquidity takers (LTs), but identifies a cluster (group 4, ~16%) that also acts as LPs; explicit clustering of LP "species" and their profit/PnL is named as future work.
- Future work proposes leveraging full Ethereum blockchain data (multiple DEXs, flow of funds, borrowing) to approximate agents' PnL and study the "optimal routing problem" (Angeris et al.) across networks of CFMMs.
- The transaction-graph + weighted-graph2vec method is a candidate tool for characterising structural trading behaviour that a CFMM thesis could adapt to LP-side actions (mint/burn timing) rather than LT swaps.
- Open: whether the pool typology (SS/ECOSYS/EXOTIC) is meaningful for liquidity provision, given the finding that it fails to describe full pool dynamics; how feeTier and token composition jointly determine a pool's attractiveness for LPs (low volatility to avoid predictable loss, high feeTier for profit).
- Provides Miori & Cucuringu (2023) volume-forecasting and the interconnectedness/spillover framing that could complement a CFMM liquidity-provision model with cross-pool dynamics.
