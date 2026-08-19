---
title: Amm Loss Versus Rebalancing
layer: core
type: source
origin: thesis
source_path: "articles/LVR/Automated Market Making and Loss-Versus-Rebalancing.pdf"
source_kind: paper
date: 2026-07-19
---

# Automated Market Making and Loss-Versus-Rebalancing

Introduces loss-versus-rebalancing (LVR), a "Black-Scholes formula for AMMs" that quantifies the adverse-selection cost passive liquidity providers incur when arbitrageurs pick off stale AMM prices.

**Authors / venue / year:** Jason Milionis, Ciamac C. Moallemi, Tim Roughgarden, Anthony Lee Zhang (Columbia University / a16z Crypto / University of Chicago Booth); arXiv:2208.06046, initial version July 2022, current version May 2024. This is the full-length version of the DeFi '22 workshop paper "Quantifying Loss in Automated Market Makers".

## Key points
- Models the market microstructure of automated market makers (AMMs) from the perspective of passive liquidity providers (LPs), analogous to how Black-Scholes analyzes option returns.
- Defines the **rebalancing strategy**: a self-financing strategy that holds the same risky-asset position as the AMM at every instant, but trades at external CEX/market prices rather than at (worse) AMM prices. Shorting the rebalancing strategy delta-hedges the LP position.
- **Loss-versus-rebalancing (LVR, "lever")** is the performance gap between the rebalancing strategy and the AMM LP position; it captures losses from **price slippage** — arbitrageurs "snipe" stale AMM quotes whenever CEX prices move (analogous to sniping in the Budish et al. 2015 HFT model). LVR applies to any AMM with mild regularity, not only CFMMs.
- Instantaneous LVR depends on only two parameters for locally-smooth AMMs: the instantaneous variance of asset prices, and the marginal liquidity (slope of the AMM's demand curve) at the current price. Losses grow with volatility and with how aggressively the AMM trades.
- Once market risk is hedged (by shorting the rebalancing strategy), LP profit-and-loss reduces to trading fee income minus LVR — isolating the economic cost of liquidity provision.
- Empirically validated on the Uniswap v2 ETH-USDC pair: model-predicted LVR closely matches returns from a delta-hedged LPing strategy; hedged LP P&L has only 1%–6% of the return standard deviation of unhedged LP P&L, showing most LP return variation is just market-risk exposure.

## Notable claims & data
- Assets: risky asset priced by geometric Brownian motion with volatility σ (possibly stochastic); infinitely deep CEX; arbitrageurs pay no fees so they keep AMM price equal to CEX price; noise traders contribute fees.
- CFMM feasible set C = {(x,y) ∈ R²₊ : f(x,y) = L} with bonding function f and invariant L; pool value function V(P) = min over reserves of Px + y subject to f(x,y)=L.
- Instantaneous LVR: ℓ(P) = -(σ²P²/2)·V''(P) ≥ 0; cumulative LVR_t = ∫₀ᵗ ℓ(P_s) ds is non-negative, non-decreasing, and predictable.
- Rebalancing portfolio value R_t = V₀ + ∫₀ᵗ x*(P_s) dP_s; LVR_t = R_t − V_t.
- Risk-neutral expectation of LVR equals that of impermanent loss (and any market-price benchmark); LVR is the unique benchmark that removes market-risk differences. Loss vs. any other benchmark = LVR plus a mean-zero market-risk noise term.
- Empirical data: Uniswap v2 WETH-USDC pool asset holdings plus CEX ETH-USDC price series; delta-hedged LP P&L standard deviation ~1%–6% of unhedged.

## Open questions
- Assumes arbitrageurs pay no fees and monitor continuously (relaxed by the follow-up "Arbitrage Profits in the Presence of Fees" paper, which adds trading fees and discrete Poisson block arrivals).
- AMM design implications: in competitive liquidity markets fees should balance LVR; suggests variance-scaled fee mechanisms, backward-looking fee adjustment, oracle-based re-quoting, or auctioning arbitrage rights to capture and redistribute LVR to LPs.
- Directly relevant to CFMM liquidity provision: gives a closed-form, empirically calibratable cost of providing liquidity that any thesis on LP profitability must net against fee income.
