---
title: Clmm Mathematical Framework
layer: core
type: source
origin: thesis
source_path: "articles/liquidity/A MATHEMATICAL FRAMEWORK FOR MODELLING CLMM.pdf"
source_kind: paper
date: 2026-07-19
---

# A Mathematical Framework for Modelling CLMM Dynamics in Continuous Time

A rigorous continuous-time, measure-theoretic framework that models Concentrated Liquidity Market Maker (CLMM) liquidity profiles as measure-valued processes and derives closed-form optimal arbitrage strategies, showing that trading fees preclude diffusion terms in the admissible price process.

**Authors / venue / year:** Shen-Ning Tung and Tai-Ho Wang; arXiv:2412.18580v1 [q-fin.MF], dated December 25, 2024.

## Key points
- Develops a unified continuous-time mathematical framework for Concentrated Liquidity Market Makers (CLMMs, introduced by Uniswap V3), which generalize Constant Function Market Makers (CFMMs) by letting liquidity providers concentrate capital within chosen price ranges rather than uniformly over the whole price line.
- Reviews CFMM fundamentals: bonding function f(x,y) = ell as a level set, trade validity via preserving the bonding function, required properties (monotonicity, convexity, scaling/homogeneity), spot price from the implicit function theorem P = f_x/f_y, and pool value V = Px + y.
- Models liquidity profiles as measure-valued processes (Equations 16 and 19) to precisely characterize how concentrated liquidity affects market behavior and trading outcomes.
- Analyzes arbitrageur strategic behavior under three arbitrage models — myopic, finite-horizon, and infinite-horizon with discounted and ergodic controls — deriving closed-form solutions for optimal arbitrage strategies in each scenario using stochastic analysis and control theory.
- Central theoretical finding: the presence of trading fees fundamentally constrains admissible price processes; including fees precludes diffusion (Brownian) terms in the price process, otherwise fee generation would be infinite. This has design and market-efficiency implications for CLMMs.
- Frames the impermanent loss / loss-versus-rebalancing (LVR) decomposition and the analogy between CLMM liquidity provision and covered-call option payoffs.

## Notable claims & data
- Trading fee parameter gamma in (0,1); 1 - gamma is the fee fraction, with common gamma values from 99% to 99.99%. Fees create an infinitesimal bid-ask spread P_bid = gamma^{-1} P, P_ask = gamma P.
- Impermanent loss defined as IL_t = H_t - V_t (hold value minus LP position value); with martingale price process, E[IL_t] = -E[integral of (1/2) V''(P_s) d<P>_s] >= 0, so LPs are on average worse off than holding.
- Loss-versus-rebalancing LVR_t := R_t - V_t with dLVR_t = -(1/2) V''(P_t) d<P>_t >= 0; IL decomposes (Eq. 8) into a hedgeable martingale component plus a non-negative LVR drift.
- Geometric Mean Market Makers (G3Ms, e.g. Balancer) use bonding function f(x,y) = x^w y^{1-w}; Constant Product Market Maker (CPMM, Uniswap V2) is the special case w = 1/2 giving xy = ell^2.
- CLMM position defined by pair (ell, [p_l, p_u]); reserve functions x(p), y(p) resemble bull-spread payoffs (Eq. 9); LP value function V(P) is piecewise (Eq. 10) with a covered-call representation V(k) in the price-ratio domain k = P/p_m, p_m = sqrt(p_l p_u), r = p_u/p_l (Eq. 11).
- Key theoretical result claimed via joint work with C.-Y. Lee [LTW24]: fees impose that admissible price processes cannot contain diffusion terms.

## Open questions
- How the no-diffusion-under-fees constraint reconciles with empirically observed (diffusive) crypto price dynamics, and what price-process class is actually admissible for a fee-bearing CLMM.
- Practical calibration of the measure-valued liquidity-profile process to real Uniswap V3 tick data, connecting this theory to the empirical liquidity-surface work (RTW-style).
- Extending the covered-call analogy for optimal LP range selection, fee-structure design, and hedging of impermanent loss / LVR in live pools.
- Connection to CFMM liquidity provision: how optimal arbitrage strategies and the fee constraint should inform LP capital allocation, range width r, and pool fee-tier design.
