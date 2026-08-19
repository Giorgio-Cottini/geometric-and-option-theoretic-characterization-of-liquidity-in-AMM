---
title: Decentralised Finance and Automated Market Making - Predictable Loss and Optimal Liquidity Provision
layer: core
type: source
origin: thesis
source_path: "articles/optimal shape/control/Decentralised Finance and Automated Market Making - Predictable Loss and Optimal Liquidity Provision.pdf"
source_kind: paper
date: 2026-08-04
---

# Decentralised Finance and Automated Market Making - Predictable Loss and Optimal Liquidity Provision

Derives the continuous-time wealth dynamics of a strategic liquidity provider (LP) in a constant product market with concentrated liquidity (CL), then solves in closed form for the optimal width and skew of the LP's liquidity range under log utility. Uses Uniswap v3 ETH/USDC data to show that observed LPs trade at a loss on average and that the derived strategy outperforms them out of sample.

**Authors / venue / year:** Alvaro Cartea, Faycal Drissi, Marcello Monga. Forthcoming in SIAM Journal on Financial Mathematics. arXiv:2309.08431v3, dated June 13, 2024.

## Key points
- Defines predictable loss (PL), the component of an LP's wealth decay caused by the convexity of the CL trading function and by the opportunity cost of locking assets in a range. PL is the CL analogue of loss-versus-rebalancing (LVR): see [[concept-loss-versus-rebalancing]].
- Parametrizes the LP's range by a spread `delta = delta^u + delta^l` and an asymmetry `rho = delta^u / delta`, where `delta^u`, `delta^l` control the upper and lower tick boundaries via `(Z^u)^{1/2} = Z^{1/2}/(1 - delta^u/2)` and `(Z^l)^{1/2} = Z^{1/2}(1 - delta^l/2)`. This reparametrization linearizes the CL constant-product formulae and turns range choice into a one-dimensional control.
- Models three wealth components: position value (subject to PL), fee income (subject to a stochastic pool fee rate `pi` with CIR-type dynamics, and to a concentration cost that penalizes narrow spreads), and rebalancing cost. See [[concept-predictable-loss]].
- Solves the resulting stochastic control problem via the Hamilton-Jacobi-Bellman equation for a log-utility LP maximizing expected utility of terminal wealth in units of the reference asset. Obtains the value function in closed form (Proposition 1) and the optimal spread in closed form (Theorem 1).
- The optimal spread balances three forces: fee revenue (pushes the range narrower, toward the current rate), predictable loss and concentration risk (push the range wider). When the drift of the marginal rate is stochastic, the strategy skews the range asymmetrically to capture expected directional flow and to profit from the expected rate move.
- Empirically, using Uniswap v3 ETH/USDC data (5 May 2021 to 18 August 2022), historical LPs lose value on average (Table 2: mean position-value change -1.64% per matched deposit/withdraw pair, fee income +0.155%, net -1.49%). The paper's optimal strategy, backtested out of sample, delivers a positive average per-minute return net of transaction costs (+0.0047%) against the observed market average (-0.00067%) and a passive hold (-0.00016%).

## Notable claims & data
- **Objective functional:** `u(t, x~, z, pi, mu) = sup_{delta in A_t} E[U(x~_T^delta)]`, with `U(x) = log(x)`, terminal wealth `x~_T` marked to market in the reference asset. This is the objective the thesis would reimplement first: a stochastic-control problem over the range spread, solved by dynamic programming.
- **What is chosen:** the pair `(delta^l_t, delta^u_t)`, equivalently `(delta_t, rho_t)` — the width and skew of the liquidity range, continuously re-optimized. Not a static range; not per-tick allocation. The asymmetry is pinned to the observed drift via `rho_t = 1/2 + mu_t/delta_t` (Eq. 14), reducing the control to the one-dimensional spread `delta`.
- **Wealth dynamics (Eq. 16):** `d x~_t = (1/delta_t)(4 pi_t - sigma^2/2) x~_t dt + mu_t rho(delta_t,mu_t) x~_t dt + sigma rho(delta_t,mu_t) x~_t dW_t - (gamma/delta_t^2) x~_t dt`, where `gamma` is the concentration cost parameter (calibrated by regression, Eq. 12) and `pi` follows CIR dynamics `d(pi_t - eta_t) = Gamma(pi_bar + eta_t - pi_t) dt + psi sqrt(pi_t - eta_t) dB_t` around a profitability threshold `eta`.
- **Closed-form optimal spread (Theorem 1, Eq. 23):** `delta*_s = (2 gamma + mu_s^2 sigma^2) / (4(pi_s - eta_s) + epsilon)`, with `eta_s = sigma^2/8 - (mu_s/4)(mu_s - sigma^2/2) + epsilon/4`. In the symmetric case `mu=0` this reduces to `delta* = 4 gamma / (8 pi_t - sigma^2)` (Eq. 24): narrower as fee rate `pi` rises, wider as volatility `sigma` or concentration cost `gamma` rises.
- **Profitability condition (Eq. 19, Eq. 26):** LP activity is viable only if `4 pi_t - sigma^2/2 >= epsilon > 0`, equivalently `pi - gamma/8 >= sigma^2/8`; the paper proposes `sigma^2/8` as a rule-of-thumb minimum required pool fee rate.
- **Numerical method:** closed-form solution, no PDE grid or simulation needed for the control itself. The empirical calibration uses a rolling one-day in-sample window (one-minute rate returns for `sigma`, realized LT fee flow for `pi`, linear regression of `delta^2 * fee-revenue` on `delta` for `gamma = 5e-7`), then applies the closed-form spread out of sample at one-minute rebalancing frequency.
- **Empirical calibration:** 331,858 individual LP operations, 5,156 distinct LPs, ETH/USDC pool, 1 January to 18 August 2022 for the backtest window (5 May 2021 to 18 August 2022 for the full history). Average gas cost of 84.8 USD per full reposition cycle implies the strategy needs > 1.8 million USD deposited to be profitable net of gas at observed activity levels.

## Connections
- Builds directly on the loss/hedging accounting of [[source-rtw26-cfmm-liquidity-pricing-hedging]]: PL is the CL-specific sibling of that paper's LVR decomposition, both rooted in the same curvature-driven depreciation of LP wealth. See [[concept-loss-versus-rebalancing]] and [[concept-lp-pnl-decomposition]].
- Concretizes [[concept-concentrated-liquidity]] and [[concept-uniswap-v3-ticks]] into a one-dimensional stochastic control problem, an explicit instance of the "stochastic control" setting surveyed by [[concept-optimal-liquidity-provision]].
- The empirical loss finding parallels [[source-quantifying-loss-in-amms]] and [[source-amm-loss-versus-rebalancing]], both of which document systematic LP losses in CFMMs from an outside vantage point; this paper's contribution is a strategy that turns the same data into an outperforming policy.
- Complements [[concept-adverse-selection]] and [[concept-market-microstructure]]: the concentration-cost term is a reduced-form price for the same range-exit risk that microstructure models of informed flow treat structurally.

## Open questions
- The model assumes continuous rebalancing and zero gas fees for the control derivation; profitability net of gas and of blockchain latency (block time, transaction ordering, sandwich risk) is treated only as a post-hoc adjustment, not folded into the control.
- The asymmetry function `rho_t = 1/2 + mu_t/delta_t` is a fitted approximation to the empirically observed optimal skew (Figure 4), not derived from the control problem itself; the paper flags a richer, jointly-optimized asymmetry as future work.
- Assumes constant volatility `sigma`; the authors note the extension to stochastic volatility is straightforward but do not carry it out.
- The fee rate `pi` and rate `Z` are assumed independent; the paper's own correlation test (Table 1) finds a small but non-zero and frequency-dependent correlation, left unmodeled.
