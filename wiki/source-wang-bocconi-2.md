---
title: Wang Bocconi 2
layer: core
type: source
origin: thesis
source_path: "articles/Geometry (Wang)/Bocconi_Nov20-2024_2.pdf"
source_kind: note
date: 2026-07-19
---

# Introduction to Automated Market Making II: Optimal liquidity provision in CLPMM

Seminar slides on optimal liquidity provision in concentrated-liquidity-provision market making (CLPMM), pairing the CLP reserve/profile theory with a stochastic-control crash course and casting optimal provision as an optimal stopping / bang-bang control problem.

**Authors / venue / year:** Tai-Ho Wang (Baruch College CUNY / Ritsumeikan University), joint with Shen-Ning Tung; Dipartimento di Finanza, Università Bocconi, Milano, 20 November 2024.

## Key points
- Reviews Concentrated Liquidity Provision (CLP): LPs contribute liquidity L to a chosen price range, and reserves are measured in liquidity units; superposing positions yields a general liquidity profile L(p).
- Converts a liquidity profile into pool reserves via integral formulas and shows the reserve/bonding curve is decreasing and convex.
- Presents empirical liquidity profiles from on-chain data (liquidity over ticks at various times; 3D liquidity surface over tick × time).
- Gives a crash course on stochastic control: value function, dynamic programming principle (DPP), Hamilton-Jacobi-Bellman (HJB) equation, and the linear-quadratic (LQ) problem.
- Frames optimal liquidity provision as a stochastic control problem: an optimal stopping problem and, in the relevant regime, a bang-bang control.

## Notable claims & data
- Notation adds transaction cost 1-γ (typically γ = 99.7%, i.e. the Uniswap 0.3% fee) and an exogenous reference price S_t for the risky asset, alongside x_t, y_t, L, P, V_t.
- CLP reserve contributions for range [p_l,p_r] (0<p_l<p_r<∞): for P in range x = L(1/sqrt(P) - 1/sqrt(p_r)), y = L(sqrt(P) - sqrt(p_l)); for P>p_r, x=0, y=L(sqrt(p_r)-sqrt(p_l)); for P<p_l, y=0, x=L(1/sqrt(p_l)-1/sqrt(p_r)).
- Combined profile x(p) = L(1/sqrt(p)-1/sqrt(p_r))^+ - L(1/sqrt(p)-1/sqrt(p_l))^+, y(p) = L(sqrt(p)-sqrt(p_l))^+ - L(sqrt(p)-sqrt(p_r))^+; in-range bonding curve (x+L/sqrt(p_r))(y+L*sqrt(p_l)) = L^2, equivalently (x/L + 1/sqrt(p_r))(y/L + sqrt(p_l)) = 1.
- Additivity: two positions give L(p) = L1·1_{[p_l^1,p_r^1]} + L2·1_{[p_l^2,p_r^2]}; reserves add as sums of positive-part (call-option) terms — no simple closed-form bonding curve by eliminating the parameter.
- Reserve as option-portfolio payoff: change of variable s=1/sqrt(p) makes x a payoff of long/short calls struck at the range endpoints; as a Lebesgue-Stieltjes integral x(1/s^2) = ∫_{[0,s]} (s-k)dL̃(k) against a signed Dirac measure dL̃.
- Profile-to-reserve formulas: x(P) = (1/2)∫_P^∞ L(p)p^{-3/2}dp, y(P) = (1/2)∫_0^P L(p)p^{-1/2}dp. Then dy/dx = -P (canonical parametrization) and d²y/dx² = 2P^{3/2}/L(P) > 0 → reserve curve decreasing and convex.
- Illustrations: discrete profile L(p)=L1·1_{[a,b]}+L2·1_{[b,c]} with (a,b,c)=(1,2,3), (L1,L2)=(10,50); continuous profile L = pdf of chi-squared with 3 degrees of freedom; empirical Uniswap liquidity surfaces.
- Stochastic control ingredients: value function, DPP, HJB PDE, LQ problem — supplied as the toolkit for the optimal-provision problem.
- Optimal liquidity provision posed as (i) an optimal stopping problem and (ii) a bang-bang control, i.e. the optimal policy switches liquidity fully on/off rather than taking interior values.

## Open questions
- Full solution of the optimal liquidity-provision control problem (bang-bang thresholds, optimal stopping boundary) under transaction cost γ and reference price S_t is the open direction.
- Connecting the theoretical liquidity profile to observed empirical profiles — calibration and consistency with the market-induced profile — remains to be developed.
- How fee income (γ) trades off against impermanent loss / loss-versus-rebalance in determining the optimal concentration range.
