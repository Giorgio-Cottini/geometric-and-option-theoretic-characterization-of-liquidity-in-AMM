---
title: Optimal Range Width
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Optimal Range Width

The closed-form spread that maximizes a concentrated-liquidity provider's expected log utility of terminal wealth, derived by solving a Hamilton-Jacobi-Bellman equation over the range width and skew. It balances fee income, predictable loss, and a concentration-risk penalty, and it is small when fees are high relative to volatility and large otherwise.

## Details
- Closed form (Theorem 1): `delta*_s = (2 gamma + mu_s^2 sigma^2) / (4(pi_s - eta_s) + epsilon)`, with `eta_s = sigma^2/8 - (mu_s/4)(mu_s - sigma^2/2) + epsilon/4`. In the symmetric case `mu = 0` this reduces to `delta* = 4 gamma / (8 pi_t - sigma^2)`: narrower as the fee rate `pi` rises, wider as volatility `sigma` or the concentration cost `gamma` rises.
- Three inputs drive the width: fee income (pulls the range narrower, toward the current price), predictable loss (pulls it wider as volatility rises, see [[concept-predictable-loss]]), and a concentration-risk cost `gamma` (a reduced-form penalty for narrow ranges, calibrated by regressing `delta^2` times fee revenue on `delta`).
- When the price drift `mu` is nonzero, the range skews asymmetrically, via `rho_t = 1/2 + mu_t/delta_t`, to capture expected directional flow.
- Viability condition: LP activity is only profitable if `4 pi_t - sigma^2/2 >= epsilon > 0`, equivalently `pi - gamma/8 >= sigma^2/8`; the source proposes `sigma^2/8` as a rule-of-thumb minimum required pool fee rate.
- No PDE grid or simulation is needed to evaluate the control: the spread is a closed-form function of the calibrated state variables `pi`, `sigma`, `mu`, `gamma`, recomputed at each rebalancing step.
- Empirical finding: on Uniswap v3 ETH/USDC data (5 May 2021 to 18 August 2022), historical LPs trade at a loss on average (mean position-value change -1.64% per matched deposit/withdraw pair, fee income +0.155%, net -1.49%), which shows most observed providers sit far from the optimal width. The closed-form strategy, backtested out of sample, returns +0.0047% per minute net of transaction costs against a -0.00067% observed market average and a -0.00016% passive hold.

## Appears in
- [[source-cartea-predictable-loss-optimal-lp]] — derives the closed-form optimal spread (Theorem 1) and its empirical validation against observed Uniswap v3 LP behavior.

## Related
- [[concept-predictable-loss]] — the loss term the optimal width trades off against fee income.
- [[concept-concentrated-liquidity]] — the mechanism whose range parameter is being optimized.
- [[concept-uniswap-v3-ticks]] — the discrete tick grid the continuous spread maps onto in practice.
- [[concept-optimal-liquidity-provision]] — the broader stochastic-control setting this closed-form result instantiates.
- [[concept-lp-behavior]] — the empirical LP behavior the optimal width is measured against.
- [[concept-stochastic-control]] — the dynamic-programming method (HJB equation) used to derive the width.
