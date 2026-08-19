---
title: Pricing Under Rough Vol
layer: core
type: source
origin: thesis
source_path: "articles/vol surface/roughness/Pricing Under Rough Volatility.pdf"
source_kind: paper
date: 2026-07-19
---

# Pricing under rough volatility

Shows how the Rough Fractional Stochastic Volatility (RFSV) model — in which log-variance behaves as a fractional Brownian motion with Hurst exponent H ~ 0.1 — can be used to price claims on the underlying and on integrated variance, developing the "rough Bergomi" (rBergomi) model that fits the SPX volatility surface markedly better than conventional Markovian stochastic-volatility models, and with fewer parameters.

**Authors / venue / year:** Christian Bayer (WIAS Berlin), Peter Friz (TU Berlin and WIAS Berlin), and Jim Gatheral (Baruch College, CUNY). Preprint dated September 18, 2015 (SSRN abstract 2554754; published Quantitative Finance 2016).

## Key points
- Builds on Gatheral-Jaisson-Rosenbaum: the logarithm of realized variance behaves essentially as a fractional Brownian motion with H of order 0.1 at any reasonable time scale, motivating the stationary RFSV model in which log-volatility is a fractional Ornstein-Uhlenbeck process with very long reversion time (alpha T << 1), so log-variance locally looks like an fBm.
- Motivated by the stylized fact that the overall shape of the equity volatility surface is roughly time-homogeneous, arguing for modeling volatility as a time-homogeneous process whose parameters are independent of price and time.
- The key empirical driver is the term structure of ATM volatility skew `psi(tau) = |d/dk sigma_BS(k,tau)|` at k=0, which is observed to follow a power law `psi(tau) ~ tau^{-alpha}` with 0 < alpha < 1/2 over a wide range of expiries — a feature conventional (Markovian, exponential-kernel) stochastic-volatility models cannot reproduce (they give constant short-date skew), but rough models with a power-law kernel do.
- Derives the rBergomi model as a non-Markovian generalization of the Bergomi forward-variance model: replace the exponential kernels of the n-factor Bergomi variance curve with a power-law (Volterra) kernel, giving instantaneous volatility driven by a Volterra fractional Brownian motion of Hurst parameter H = 1/2 - gamma.
- Works in forward-variance-curve form `xi_t(u) = E[v_u | F_t]`; the change of measure from physical P to pricing Q is deterministic in this special case, and the conditional variance forecast is the natural state variable.
- Demonstrates that rBergomi-simulated volatility surfaces are remarkably consistent with observed SPX surfaces on the sample days, and that market variance-swap curves are consistent with model forecasts from historical realized variance — with dramatic examples from the Lehman Brothers collapse weekend and the Flash Crash.

## Notable claims & data
- RFSV model (Eq. 1.1): `dS_t/S_t = mu_t dt + sigma_t dZ_t`, `sigma_t = exp{X_t}`, with X_t a fractional Ornstein-Uhlenbeck process `dX_t = nu dW_t^H - alpha(X_t - m) dt`; fBm sample paths are (H - epsilon)-Holder, rougher than Brownian motion for H < 1/2.
- Simple physical-measure regularity (Eq. 2.1): `log sigma_{t+Delta} - log sigma_t = nu (W_{t+Delta}^H - W_t^H)`, found to hold across 21 equity indices, Bund, Crude Oil and Gold futures — possibly universal.
- Bergomi-Guyon expansion (Eq. 1.3-1.4): first-order-in-vol-of-vol smile via the autocorrelation functional C^{x xi}; power-law kernel gives skew `psi(tau) ~ tau^{-gamma}` for small tau (per Alos/Fukasawa).
- Empirical SPX ATM skew power-law fit: `psi(tau) = A tau^{-0.407}` (Aug 14, 2013 data).
- Final model under P (Eq. 2.5): `v_u = v_t exp{eta W_tilde_t^P(u) + 2 nu C_H Z_t(u)}` with W_tilde a Volterra/Brownian semi-stationary process; interest rates set to zero WLOG.
- rBergomi is more parsimonious than the two-factor Bergomi model (which is found to be over-parameterized).

## Open questions
- Notes rBergomi is in general NOT consistent with the VIX options market (examined in the full paper).
- The second-order Bergomi-Guyon asymptotic expansion of rBergomi does not converge for parameters of practical interest; numerical/Monte Carlo methods for the Brownian-semi-stationary process are needed, and applying advanced numerical techniques from that literature remains to be explored.
- Connection to CFMM liquidity provision: rBergomi/RFSV supply the concrete pricing model under rough volatility. The anchor paper (RTW26) prices impermanent loss and LVR as claims driven by the pool-price quadratic variation and defines liquidity-profile implied volatilities exhibiting a smile; pricing CFMM liquidity provision under rough volatility — with its power-law ATM skew and rough forward variance — is a natural extension direction, especially if crypto pool prices share the near-universal roughness H ~ 0.1.
