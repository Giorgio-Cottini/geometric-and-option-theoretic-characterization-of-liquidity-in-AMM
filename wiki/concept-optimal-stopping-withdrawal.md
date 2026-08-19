---
title: Optimal Stopping for LP Withdrawal
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Optimal Stopping for LP Withdrawal

The formulation of a liquidity provider's withdrawal decision as an optimal-stopping problem: choose a single stopping time that maximizes expected mark-to-market position value plus accumulated fees, rather than continuously re-optimizing a range or a per-tick allocation. The value function solves a Hamilton-Jacobi-Bellman quasi-variational inequality (HJB QVI), and the optimal policy is a free exit boundary in price-reserve space.

## Details
- Objective: `sup_{tau in T} E[P^X_tau + S_tau P^Y_tau + R_tau]`, over stopping times `tau <= T`, equivalent to minimizing expected impermanent loss net of accumulated fees.
- HJB QVI (Eq. 3.4): `min{-partial_t v - (1/2) sigma^2 partial_SS v - jump terms, v} = 0`, with terminal condition `v(T,y,S) = 0`. The value function is the unique viscosity solution in the class of non-negative functions with quadratic growth.
- The jump terms model arbitrageurs and noise traders as counting processes with state-dependent intensities that rise with the misalignment between the pool's internal price and the external price.
- Exit boundary: the value function is maximized when the AMM price equals the external price and declines as the two diverge. The LP withdraws when the misalignment grows too large, because impermanent loss is realized only once arbitrageurs trade to close the gap; a pre-emptive exit avoids bearing a loss the LP would otherwise absorb.
- Comparative statics: both expected fees and expected impermanent loss are concave in volatility; higher arbitrageur intensity raises both fees and realized loss up to a volatility-implied ceiling; higher noise-trader intensity raises fees with loss essentially unchanged. At five times baseline volatility the optimal policy is immediate exit; at one-fifth baseline volatility it is to hold to the full horizon.
- This continues the last-passage-time withdrawal result of [[source-rtw26-cfmm-liquidity-pricing-hedging]]: RTW26 gives a closed-form, distributional answer to a structurally related question (the last time the price visits a given level), while this formulation treats exit as a genuine optimal-stopping control problem with a numerically-solved free boundary rather than a closed-form passage-time law.
- The problem is distinct from range-width control: the only decision is when to withdraw once, not how to reposition a range continuously. See [[concept-optimal-range-width]] for the continuous-control sibling.

## Appears in
- [[source-bergault-optimal-exit-time]] — poses the optimal-stopping problem, proves the HJB QVI characterization (Theorem 1), and solves it numerically.

## Related
- [[source-rtw26-cfmm-liquidity-pricing-hedging]] — the last-passage-time withdrawal result this problem continues and generalizes into a full stochastic control.
- [[concept-loss-versus-rebalancing]] — the same fee-versus-adverse-price trade-off, priced here through a discrete arbitrage-driven exit rather than continuous accounting.
- [[concept-impermanent-loss]] — the loss term the stopping problem minimizes net of fees.
- [[concept-arbitrage-with-fees]] — the order-flow mechanism (arbitrageur intensity rising with price misalignment) that drives the exit boundary.
- [[concept-stochastic-control]] — optimal stopping is a control problem with a single binary decision (stop or continue) rather than a continuous action.
- [[concept-longstaff-schwartz]] — the regression Monte Carlo method used to solve this problem numerically, alongside a finite-difference Euler scheme.
