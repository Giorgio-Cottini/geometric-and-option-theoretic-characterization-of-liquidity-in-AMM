---
title: Rough Volatility
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Rough Volatility

A class of stochastic-volatility models in which log-volatility behaves as a fractional Brownian motion with a small Hurst exponent H ~ 0.1 — so volatility sample paths are much rougher than Brownian motion. The empirical driver is a power-law term structure of at-the-money skew, which conventional Markovian models cannot reproduce but rough models with a power-law kernel do.

## Details
- RFSV (Rough Fractional Stochastic Volatility): sigma_t = exp{X_t} with X_t a fractional Ornstein–Uhlenbeck process, dX_t = nu dW_t^H - alpha(X_t - m) dt, and reversion so slow (alpha·T << 1) that locally X looks like a fractional Brownian motion; fBm paths are (H - epsilon)-Hölder, rougher than Brownian motion for H < 1/2.
- Physical-measure regularity: log sigma_{t+Delta} - log sigma_t = nu(W^H_{t+Delta} - W^H_t), found to hold across ~21 equity indices plus Bund, crude oil and gold — possibly universal, with H of order 0.1.
- Power-law ATM skew: the term structure of ATM volatility skew psi(tau) = |d/dk sigma_BS(k, tau)| at k=0 follows psi(tau) ~ tau^{-alpha} with 0 < alpha < 1/2 (e.g. an SPX fit psi(tau) = A·tau^{-0.407}). Markovian (exponential-kernel) models give constant short-date skew; rough models with a power-law/Volterra kernel reproduce the observed blow-up.
- rBergomi (rough Bergomi): a non-Markovian forward-variance model obtained by replacing the exponential kernels of the Bergomi variance curve with a power-law Volterra kernel (H = 1/2 - gamma); it fits the SPX surface better than two-factor Bergomi and with fewer parameters. Works in forward-variance-curve form xi_t(u) = E[v_u | F_t].
- Roughness matters for CFMMs because impermanent loss and LVR are integrals against the pool-price quadratic variation d<P>, so the fine structure of volatility shapes them directly.

## Appears in
- [[source-pricing-under-rough-vol]] — develops RFSV and the rBergomi model, showing rough volatility reproduces the power-law ATM skew and fits the SPX surface parsimoniously.
- [[source-log-sfbm-multifractal-vol]] — treats rough volatility (H > 0) as one end of the log S-fBM family and analyzes/estimates the roughness exponent H, warning of upward bias in naive estimates.

## Related
- [[concept-multifractal-volatility]] — the H -> 0 limit of the same log S-fBM construction; rough and multifractal volatility are two ends of one bridge.
- [[concept-scaling-renormalization]] — Hurst/time-scaling symmetry underlying both roughness and multiscaling.
- [[concept-implied-volatility-surface]] — the object whose skew term structure motivates rough models.
- [[concept-svi-parametrization]] — open question whether rough smiles embed in the arbitrage-free SSVI class.
- [[concept-volatility-stylized-facts]] — roughness sits alongside clustering, fat tails and leverage as an empirical feature.
- [[entity-jim-gatheral]] — co-author of the rough Bergomi model.
