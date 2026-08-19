---
title: Optimal Exit Time for Liquidity Providers in Automated Market Makers
layer: core
type: source
origin: thesis
source_path: "articles/optimal shape/control/Optimal Exit Time for Liquidity Providers in Automated Market Makers.pdf"
source_kind: paper
date: 2026-08-04
---

# Optimal Exit Time for Liquidity Providers in Automated Market Makers

Characterizes the optimal withdrawal time of a representative liquidity provider (LP) from a constant function market (CFM) as an optimal stopping problem, proves the value function is the unique viscosity solution of a Hamilton-Jacobi-Bellman quasi-variational inequality (HJB QVI), and solves it numerically with an Euler scheme and a Longstaff-Schwartz regression method, calibrated to Uniswap v2/Binance ETH-USDC data.

**Authors / venue / year:** Philippe Bergault, Sebastien Bieber, Leandro Sanchez-Betancourt. arXiv:2509.06510v2, dated October 20, 2025.

## Key points
- Models an AMM with trading function `f(x,y) = xy` alongside an external limit order book with mid-price `S_t = S_0 + sigma W_t`. Arbitrageurs and noise traders arrive as counting processes `N^a`, `N^b` with state-dependent intensities `lambda^a = max(a_0, a_1 + a_2(S - c/y^2))`, `lambda^b = max(a_0, a_1 + a_2(c/y^2 - S))`: arbitrageur intensity rises with the misalignment between the pool's internal price `Z = c/y^2` and the external price `S`, noise-trader intensity is the floor `a_0`.
- Defines the LP's payoff as fees collected `R_t` minus impermanent loss `IL_t = -[X_t + Y_t S_t - (X_0 + Y_0 S_0)]`, and poses the optimal exit problem as `sup_{tau in T} E[P^X_tau + S_tau P^Y_tau + R_tau]` over stopping times `tau <= T`. This is optimal-stopping control, not a continuous re-optimization: the only decision is when to withdraw once, not how to reposition a range.
- Proves (Theorem 1) that the value function is the unique viscosity solution, in the class of non-negative functions with quadratic growth, to the HJB QVI `min{-partial_t v - (1/2) sigma^2 partial_SS v - jump terms, v} = 0` with terminal condition `v(T,y,S) = 0`.
- Solves the HJB QVI two ways: (a) an implicit Euler scheme on a 3D grid (time, reserve `Y`, price `S`) with operator splitting (explicit jump step, implicit diffusion step), subject to a CFL stability condition; (b) a Longstaff-Schwartz algorithm that regresses the continuation value on a degree-`d` polynomial in `(S, Y)` at each time step and stops when the fitted continuation value is non-positive. The two methods agree on the shape of the exit region; Longstaff-Schwartz slightly underestimates the value function because it can only exit at discrete grid times.
- The value function is maximized when the AMM price equals the external price (`S = c/Y^2 = Z`) and declines as the two diverge; the LP exits when the price misalignment grows too large, because IL is realized only once arbitrageurs trade to close the gap, so a pre-emptive exit avoids bearing a loss the LP would otherwise absorb.
- Comparative statics (Tables 1-4): both expected fees `E[R_tau]` and expected impermanent loss `E[IL_tau]` are concave in the price volatility `sigma`; higher arbitrageur intensity `a_2` increases fees but also increases realized IL up to the volatility-implied ceiling, while higher noise-trader intensity `a_1` raises fees with IL essentially unchanged; the performance criterion `E[R_tau - IL_tau]` grows roughly linearly with the fee level `r` beyond a threshold, because once fees are high enough the LP optimally stays until `T`.
- Extends the risk-neutral formulation to a risk-averse LP with exponential utility in Appendix A, treated with the same viscosity-solution machinery.

## Notable claims & data
- **Objective functional:** `sup_{tau in T_{t,T}} E[P^X_tau + S_tau P^Y_tau + R_tau]`, i.e. maximize expected mark-to-market position value plus accumulated fees at the (chosen) exit time; equivalently minimize expected impermanent loss net of fees.
- **What is chosen:** a single stopping time `tau`, not a range or per-tick weight. This is the "when to withdraw" instance of the six settings surveyed in [[concept-optimal-liquidity-provision]], distinct from the range-width control of [[source-cartea-predictable-loss-optimal-lp]].
- **HJB QVI (Eq. 3.4):** `min{-partial_t v - (1/2) sigma^2 partial_SS v - 1_{y+xi<=Ybar} lambdabar^b(y,S)[beta^b(y,S) + v(t,y+xi,S) - v(t,y,S)] - 1_{y-xi>=Yunderbar} lambdabar^a(y,S)[beta^a(y,S) + v(t,y-xi,S) - v(t,y,S)], v(t,y,S)} = 0`.
- **Numerical method and cost:** implicit Euler on a 3D `(t, Y, S)` grid with operator splitting (jump explicit, diffusion implicit); alternative Longstaff-Schwartz regression Monte Carlo with `n=1,440` time steps, `m=5,000` (grid comparison) or `m=10,000` (comparative statics) simulated paths, polynomial regression degree `d=3`. The grid method is exact up to discretization but pays the curse of dimensionality in 3 state variables; Longstaff-Schwartz trades that for simulation variance and a systematic downward bias from discrete-time exit.
- **Empirical calibration:** parameters from Aqsha et al. (2025), fit to Binance and Uniswap v2 ETH-USDC market data, 1 January to 30 April 2022: `S_0 = Z_0 = 2820` USDC/ETH, `sigma = 0.0569 S_0` per sqrt-day, `Y_0 = 50,000` ETH, `X_0 = Y_0 Z_0` USDC, baseline `a_0 = 1`/day, `a_1 = 8`/day, `a_2 = 10` per-USD-per-day, trade size `xi = 1`, fee `r = 0.01 x xi x S_0` (constant). Volatility stress table: at `sigma_new = 5*sigma`, expected exit time collapses to `E[tau] = 0.00 (0.00)` days (immediate exit) with `E[R_tau] = 532`, `E[IL_tau] = 420`, versus `sigma_new = sigma/5` giving `E[tau] = 1.00` (full horizon), `E[R_tau] = 161,765`, `E[IL_tau] = 4,364`.

## Connections
- Sits in the same "single-agent stochastic control" family as [[source-cartea-predictable-loss-optimal-lp]] but chooses a stopping time instead of a range width; both papers price the same trade-off between fee accrual and adverse price movement, one continuously re-hedged, one liquidated once. See [[concept-optimal-stopping-withdrawal]].
- The last-passage-time withdrawal result in [[source-rtw26-cfmm-liquidity-pricing-hedging]] is a closed-form, distributional answer to a structurally related question (when is it optimal to have exited); this paper instead treats exit as a genuine optimal-stopping control with a numerically-solved free boundary, and explicitly cites the closeness of its own problem to a concurrent tractable-but-static alternative (Capponi and Zhu) that assumes GBM without modeling arbitrageur order flow.
- Impermanent loss here is defined identically in spirit to [[concept-impermanent-loss]] and connects to [[concept-loss-versus-rebalancing]]: IL is realized discretely through arbitrageur trades rather than continuously, which is the paper's point of departure from the LVR literature's continuous-time accounting.
- The arbitrageur-intensity model that pulls the AMM price toward the external price is a concrete, order-flow-level instance of [[concept-arbitrage-with-fees]] and [[concept-market-microstructure]].
- The Longstaff-Schwartz regression method is the numerical tool the thesis would reuse most directly for its own exit-time or stopping-boundary computations; see [[concept-longstaff-schwartz]].

## Open questions
- The model fixes a single representative LP holding the entire pool's liquidity; it does not address the equilibrium among multiple LPs choosing exit times simultaneously and competing for the same fee flow.
- The fee level `r` and the arbitrageur/noise-trader intensity parameters `a_0, a_1, a_2` are treated as constant primitives; the paper's own robustness section shows a strong sensitivity of the optimal exit strategy to these values without proposing how an LP would estimate them online.
- The 3D grid Euler scheme is subject to a CFL stability constraint that the paper does not fully characterize quantitatively, leaving the practical grid resolution versus stability trade-off unresolved for larger state spaces.
- No comparison against Uniswap v3 concentrated-liquidity exit behavior is attempted; the calibration uses Uniswap v2 (full-range) data only.
