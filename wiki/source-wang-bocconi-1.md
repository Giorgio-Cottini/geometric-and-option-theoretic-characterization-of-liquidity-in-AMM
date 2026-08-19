---
title: Wang Bocconi 1
layer: core
type: source
origin: thesis
source_path: "articles/Geometry (Wang)/Bocconi_Nov20-2024_1.pdf"
source_kind: note
date: 2026-07-19
---

# Introduction to Automated Market Making I: How it works and how to model

Seminar slides introducing Automated Market Making in DeFi and its mathematical modelling — CFMM bonding curves, constant product pricing, impermanent loss, loss-versus-rebalance, and the setup for concentrated liquidity provision.

**Authors / venue / year:** Tai-Ho Wang (Baruch College CUNY / Ritsumeikan University), joint with Jimmy Risk and Shen-Ning Tung; Dipartimento di Finanza, Università Bocconi, Milano, 20 November 2024.

## Key points
- Motivates AMMs as the solution to decentralized-exchange problems that arose from replicating central limit order books (CLOBs) on-chain (excessive fees, high latency, poor liquidity); AMMs are computationally cheap, storage-light, and rely on passive liquidity providers.
- Distinguishes the two pool participants: liquidity providers (add both coins without moving price, earn fees) and swappers (trade along the bonding curve, pay fees).
- Formalizes Constant Function Market Making (CFMM): the pool state lives on a level curve f(x,y)=L, with pool price P the negative slope of the tangent.
- Works out the Constant Product Market Making (CPMM) special case in the pool-reserve (x,y) and liquidity-price (L,P) coordinates.
- Derives impermanent loss (IL) and loss-versus-rebalance (LVR) using Ito's formula, showing an LP holding coins statically beats depositing them on average (absent fees).
- Introduces Concentrated Liquidity Provision (CLP) as the bridge from CFMM toward a free-market, limit-order-like mechanism (Uniswap v3).

## Notable claims & data
- Notation: x_t risky asset (e.g. ETH), y_t numéraire (e.g. USDC), (x_t,y_t) reserves, L liquidity depth, P := -dy/dx pool price, V_t pool value / LP wealth, f bonding curve.
- Bonding curve f(x,y)=L; by the implicit function theorem P = -dy/dx = f_x/f_y. Viability requires y(x) decreasing.
- Pool value V = Px + y; reserves can be viewed as functions of P by solving f(x,y)=L, giving P = f_x(φ(y,L),y)/f_y(φ(y,L),y).
- CPMM bonding curve f(x,y)=sqrt(xy)=L, so P = y/x. Coordinate transforms: L=sqrt(xy), P=y/x; x=L/sqrt(P), y=L*sqrt(P). Pool value V = Px+y = 2y = 2L*sqrt(P); reserves proportional to liquidity depth L.
- IL (divergence loss / loss-versus-holding): held value H_t = x0 P_t + y0 with dH_t = x(P0)dP_t; pool value V_t = V(P_t) with dV_t = x(P_t)dP_t + (1/2)V''(P_t)d⟨P⟩_t since V'(P)=x. Then IL_t = H_t - V_t = ∫_0^t{x(P0)-x(P_s)}dP_s - ∫_0^t (1/2)V''(P_s)d⟨P⟩_s. Since V''(P)=x'(P) ≤ 0, E[IL_t] ≥ 0 when P_t is a martingale.
- LVR: self-financing strategy R_t holding x(P_t) in the risky asset, R_0 = x0 P0 + y0, dR_t = x(P_t)dP_t. Define LVR_t = R_t - V_t; then dLVR_t = -(1/2)V''(P_t)d⟨P⟩_t ≥ 0 and IL_t = ∫_0^t{x(P0)-x(P_s)}dP_s + LVR_t. IL = a delta-hedgeable martingale component (hold x(P0)-x(P_t) shares) plus a positive LVR drift.
- References the framework of "Quantifying Loss in Automated Market Makers" (Milionis, Moallemi, Roughgarden, Zhang) for the IL/LVR decomposition.
- CLP: LPs allocate liquidity only to a designated price interval [p_l,p_r], producing a market-induced liquidity profile that liberates pricing from a single dictated bonding curve.

## Open questions
- The slides frame CLP as the next step (detailed in Part II): how to convert a chosen liquidity profile into reserves and how IL/LVR behave under concentrated liquidity.
- Empirical validation of the CLP liquidity profile against on-chain (Uniswap v3) data is flagged as future work.
