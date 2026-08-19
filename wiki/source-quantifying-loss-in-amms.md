---
title: Quantifying Loss in Amms
layer: core
type: source
origin: thesis
source_path: "articles/LVR/Quantifying Loss in Automated Market Makers.pdf"
source_kind: paper
date: 2026-07-19
---

# Quantifying Loss in Automated Market Makers

The DeFi '22 workshop paper that first introduces loss-versus-rebalancing (LVR) as a running adverse-selection cost for CFMM liquidity providers, decomposing LP P&L into rebalancing P&L, LVR, and trading-fee income.

**Authors / venue / year:** Jason Milionis, Ciamac C. Moallemi, Tim Roughgarden, Anthony Lee Zhang (Columbia University / a16z Crypto / University of Chicago Booth); Proceedings of the 2022 ACM CCS Workshop on Decentralized Finance and Security (DeFi '22), Nov 11 2022, Los Angeles. Short version of arXiv:2208.06046.

## Key points
- Studies constant function market makers (CFMMs, e.g. Uniswap) in a frictionless continuous-time Black-Scholes setting from the perspective of passive LPs; aims to answer three questions: residual value after hedging market risk, cost of committing to a payoff/demand curve, and fair trading-fee generation.
- Decomposes LP P&L: **LP P&L = (Rebalancing P&L) − LVR + (Trading Fee Income)**.
- The rebalancing strategy holds the same risky position as the CFMM but trades at CEX prices; an arbitrageur trading against it makes zero profit, so it carries only (hedgeable) market risk, no systematic loss.
- **LVR** is the shortfall of CFMM reserve value (excluding fees) relative to the rebalancing strategy: a non-negative, non-decreasing, predictable running cost. It is the adverse-selection / information cost of stale prices.
- Distinguishes LVR from "impermanent loss" / "divergence loss": that older metric is really "loss-versus-holding" (LVH), which can revert and is not a true running cost. An LP position resembles a short straddle — short volatility without collecting the premium.
- Practical use: once market risk is hedged, what remains is fee income versus LVR; comparing them gives a tradeable, ex-ante and ex-post metric for LP investment decisions and CFMM fee design.

## Notable claims & data
- Price P_t follows a Q-martingale GBM: dP_t/P_t = σ dB_t^Q, volatility σ > 0.
- Feasible set C = {(x,y) ∈ R²₊ : f(x,y)=L}; pool value function V(P) = min Px + y s.t. f(x,y)=L.
- Rebalancing portfolio R_t = V₀ + ∫₀ᵗ x*(P_s) dP_s; LVR_t = R_t − V_t.
- **Theorem 3.1:** LVR_t = ∫₀ᵗ ℓ(P_s) ds, with instantaneous LVR ℓ(P) = −(σ²P²/2)·V''(P) ≥ 0 (scaled product of price variance and marginal liquidity −V''); non-negative, non-decreasing, predictable.
- Loss-versus-holding: LVH_t = LVR_t + ∫₀ᵗ [x*(P₀) − x*(P_s)] dP_s; the extra term is a zero-mean market-risk component, so LVH can be positive or negative ("impermanent").
- No numerical dataset in this short version (defers empirics to the full arXiv paper); assumes passive LPs (no mints/burns), ignores gas fees and block discreteness.

## Open questions
- Frictionless, zero-fee, continuous-monitoring idealization; fee income and arbitrageur frictions are treated only qualitatively here.
- Suggests redesigning CFMMs to reduce/eliminate LVR (e.g. oracle-quoting) and variance-scaled fee mechanisms, but leaves mechanism design open.
- Core reference for CFMM liquidity-provision theory: provides the closed-form running cost that a thesis must weigh against fee revenue to judge LP profitability.
