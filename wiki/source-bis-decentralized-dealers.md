---
title: Bis Decentralized Dealers
layer: core
type: source
origin: thesis
source_path: "articles/LPs/BIS_decentralized_dealers.pdf"
source_kind: paper
date: 2026-07-19
---

# Decentralised Dealers? Examining Liquidity Provision in Decentralised Exchanges

Using data from Uniswap V3, the paper shows that despite DEXs' promise to democratise liquidity provision, most liquidity is in fact supplied by a small group of sophisticated participants who behave like traditional market makers and extract substantially higher profits than retail LPs.

**Authors / venue / year:** Matteo Aquilina, Sean Foley, Leonardo Gambacorta, William Krekel (Bank for International Settlements, Macquarie University, CEPR); BIS Working Papers No 1227, Monetary and Economic Department; November 2024.

## Key points
- DEXs (e.g. Uniswap) let anyone commit assets to a liquidity pool and earn fees, so liquidity provision is "democratised" in theory; the paper tests whether this holds empirically.
- It does not: liquidity provision is confined predominantly to a small group of sophisticated participants who submit orders mimicking bids and asks close to the prevailing price, analogous to dealers/market makers in traditional finance.
- Sophisticated LPs provide the vast majority of liquidity (65-85%), manage positions actively (more pools, tighter ranges, more frequent adjustments), and capture most trading fees; retail LPs are far more passive.
- Retail participants capture only 10-25% of fees and earn substantially lower returns on invested capital, despite suffering less adverse selection (impermanent loss).
- Retail LPs show much lower skill: less profitable in volatile periods and do not adapt liquidity provision to changing market conditions, while sophisticated LPs extract higher profits during high volatility.
- The paper documents four LP strategies enabled by Uniswap V3 concentrated liquidity: concentrated, unconcentrated (V2-like), range order (limit-order-like), and just-in-time (JIT) liquidity.
- Sophisticated participation is both substantial and increasing over time (share of interactions grew from 40-50% at V3 launch to 70-80% by end 2023).

## Notable claims & data
- Sample: raw Uniswap V3 transaction logs from launch (5 May 2021) to 1 January 2024, top 250 pools = 96% of trading volume; 430,799 liquidity positions created by 88,299 distinct wallet addresses.
- Classification: wallets flagged sophisticated via six criteria (max mint value 95th percentile, mint >= USD 1m, #positions/#interactions/#pools 95th percentile, and tagged labels from Etherscan/Arkham Intelligence). "At least two criteria" => 6,124 sophisticated wallets (~7% of addresses); adjusting for multi-wallet ownership (avg 3.5 wallets/agent), sophisticated agents are only ~2-3% of participants.
- Concentrated-liquidity mechanics: TickRangeSpread = (upperBound - lowerBound) / (0.5*(upperBound+lowerBound)); positions earn fees only while price is within their tick range; at bounds the position converts fully to the less valuable asset (impermanent/divergence loss).
- Summary stats: average position size >USD 2.1m but median only ~USD 26,000 (strong positive skew); average (median) accrued fees 1,758 (129) USD; average lifetime 66 days (median 2.8); positions active 86% of lifetime on average. Stable/stable pools have tightest tickrange spreads (2.9%) vs stable/token (35%) and token/token (46%).
- Regression (retail vs sophisticated): a sophisticated LP creates ~41 positions across ~5 pools vs a retail LP's ~2 positions across ~1.4 pools; sophisticated position size ~USD 3.7m vs retail ~USD 29,000 (two orders of magnitude); sophisticated tickrange spread 23% vs retail 63%.
- Participation: ~80% of TVL and accrued fees attributed to sophisticated LPs despite them holding ~20-30% of positions and being ~7% of LPs.
- Logistic regressions: an e-fold increase in TVL raises odds of sophisticated TVL dominance by 60% (exp(0.62)=1.6) and in volume by 28%; sophisticated dominance falls with volatility (16% lower odds per e-fold). Where daily volume exceeds USD 10m, sophisticated LPs provide essentially all liquidity.
- Profitability: net return R_net = FeeYield + ImpermanentLoss - GasFees = (F + V_liq - V_hold - G) / V_hold. IL = (V_liq - V_hold)/V_hold in [-1, 0]. Retail positions earn ~USD 263/day less than sophisticated per position; retail daily fee yield ~3.5bps lower (~14 pp lower annual relative fee revenue); retail total return ~3.4bps lower on average (~2.9bps after gas). Retail experience ~0.2bps lower impermanent loss but lower fees outweigh this.
- Excess returns (net of 4-week T-bill rate, FRED DTB4K): sophisticated LPs achieve mean daily excess return of 8.4bps vs 2.7bps for retail; median daily excess return is negative for both (they lose money on most days on a risk-adjusted basis, positive mean driven by skew).
- JIT liquidity is highly concentrated: <1% of trades are JIT; ~40% of JIT transactions occur in the single most active pool (ETH/USDC 5bps); only ten wallet addresses account for ~half of all JIT transactions.

## Open questions
- Directly relevant to CFMM liquidity provision: quantifies the fee-yield vs impermanent-loss vs gas trade-off (R_net decomposition) that a thesis on CFMM LP profitability must model.
- Provides an empirical benchmark for LP heterogeneity (sophisticated vs retail) and the drivers of dominance (TVL, volume, volatility) that could inform models of strategic/concentrated liquidity provision.
- The tickrange-spread metric and the four LP strategies (concentrated, unconcentrated, range order, JIT) offer a taxonomy of LP behaviour that a CFMM liquidity study could extend or formalise.
- Open: whether the impermanent-loss / fee-yield equilibrium differs across CFMM designs beyond Uniswap V3's concentrated-liquidity AMM; how sophisticated LPs' active-management skill in volatility could be modelled rather than just measured.
- Ties to the thesis replication (RTW26) via the same impermanent-loss / predictable-loss and pricing-of-liquidity-provision framing (Cartea, Drissi et al. cited).
