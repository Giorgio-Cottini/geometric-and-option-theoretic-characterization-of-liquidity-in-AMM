---
title: Amm Arbitrage Profits Fees
layer: core
type: source
origin: thesis
source_path: "articles/LVR/Automated Market Making and Arbitrage Profits in the Presence of Fees.pdf"
source_kind: paper
date: 2026-07-19
---

# Automated Market Making and Arbitrage Profits in the Presence of Fees

Extends the LVR framework to add trading fees and discrete (Poisson) block arrivals, deriving closed-form arbitrage profits and showing that fees rescale LVR by the fraction of blocks that contain a profitable arbitrage.

**Authors / venue / year:** Jason Milionis, Ciamac C. Moallemi, Tim Roughgarden (Columbia University / a16z Crypto); arXiv:2305.14604, initial version Feb 2023, current version July 2025.

## Key points
- Generalizes Milionis et al. (2022) LVR model to a broad class of two-asset AMMs by adding (i) a proportional trading fee γ ≥ 0 and (ii) discrete arbitrageur arrivals via a Poisson process with rate λ (block generation), with mean interblock time Δt = 1/λ.
- Motivation: naively adding fees to the continuous-monitoring model gives the pathology that arbitrage profits are zero for any non-zero fee (the mispricing behaves like a reflected random walk that spends ~no time at the no-trade boundary). Modeling discrete blocks is therefore essential.
- Arbitrageurs trade myopically at each block arrival, pushing the pool mispricing (AMM vs. market log-price difference) to the nearest edge of a **no-trade region** of width set by the fee γ. Between arrivals the mispricing is a diffusion driven by the GBM market price.
- Main result: the mispricing process is an ergodic Markovian jump-diffusion; expected arbitrage profit in the presence of fees ≈ frictionless LVR scaled down by P_trade, the fraction of blocks that present a profitable arbitrage. Introducing fees is essentially a "rescaling of time".
- Key practical insight: **faster blockchains (higher λ, smaller interblock time) reduce LP losses to arbitrageurs**; with fees, arbitrage profit per unit time scales like √(interblock time). Lower gas (fixed) fees also lead to smaller LP losses.
- Adds gas/fixed fees (Section 6): when both trading and gas fees are small in the fast-block regime, all LP losses leak to validators as gas fees — validators are the true recipients of the informational loss from stale AMM prices.

## Notable claims & data
- Market price GBM: dP_t/P_t = μ dt + σ dB_t, volatility σ > 0. AMM is a CFMM with feasible set C = {f(x,y)=L}; pool value V(P) = min Px + y s.t. f(x,y)=L; Lemma 1: V'(P)=x*(P), V''(P)=x*'(P)=−P·y*'(P) ≤ 0.
- **Theorem 1 (P_trade):** steady-state probability an arriving block has a profitable arbitrage = 1 / (1 + √(2λ)·γ/σ). With composite parameter η ≜ γ/(σ√(1/λ)/2), P_trade ≈ η⁻¹ when η is large (high fee, low volatility, or frequent blocks).
- **Frictionless base case (Eq. 1):** LVR-bar = lim E[LVR_T]/T = (σ²P/2)·y*''(P) (marginal liquidity at current price).
- **Theorem 2 / Eq. 2 (fast-block, fees):** ARB-bar = (σ²P/2)·[y*'(Pe^−γ)+e^γ y*'(Pe^γ)]/2 · P_trade + o(√(1/λ)); i.e. ARB-bar ≈ LVR-bar × P_trade for small γ. Averages marginal liquidity over the no-trade price interval [Pe^−γ, Pe^γ].
- Scaling with fees (γ>0): ARB-bar ∝ √(interblock time), σ³, and γ⁻¹ — consistent with Nezlobin and Tassy (2025). Phase transition: γ=0 gives ARB-bar = LVR-bar + o(1) = Θ(1) (interblock-time-independent); γ>0 gives Θ(√(interblock time)).
- **Theorem 4 (fees):** instantaneous arbitrage-fee rate FEE-bar ≈ LVR-bar × (1 − P_trade) for small γ; hence ARB-bar + FEE-bar ≈ LVR-bar — LVR is split between arbitrageur profit and fees paid to the pool according to P_trade.

## Open questions
- Directly answers a limitation of the base LVR paper (which assumed zero fees and continuous monitoring); connects LP losses to blockchain design parameters (block time, gas).
- Nezlobin and Tassy (2025) generalize to arbitrary block-time distributions and prove ARB-bar is minimized by deterministic block arrivals; reconciling the two methodologies is noted as open.
- For CFMM liquidity provision: gives a realistic, closed-form LP P&L that accounts for fee-paying arbitrageurs and discrete arrivals, enabling AMM fee-setting to balance noise-trader fee income against arbitrage loss — central to modeling real LP profitability.
