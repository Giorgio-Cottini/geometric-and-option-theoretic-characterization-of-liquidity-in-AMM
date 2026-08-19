---
title: Multifractal Volatility
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Multifractal Volatility

A model of volatility as a multifractal random measure (MRM) / multifractal random walk (MRW), in which the generalized Hurst exponent depends on the moment order q — the signature of multiscaling. In the unified log S-fBM framework it is recovered as the H -> 0 limit of rough volatility, so multifractal and rough volatility are two ends of a single continuous family.

## Details
- Multifractality means the q-th moment of aggregated log-volatility increments scales as tau^{q·H_q} with a q-dependent generalized Hurst exponent H_q, rather than a single H (monofractal/simple scaling); q-dependence encodes intermittency and heavy-tailed volatility bursts.
- Log S-fBM measure: M_{H,T}(dt) = e^{omega_{H,T}(t)} dt with omega a stationary Gaussian process (a stationary version of H-fractional Brownian motion), covariance Cov(omega(t), omega(t+tau)) = (v^2/2)[T^{2H} - tau^{2H}] for |tau| < T and exactly 0 beyond lag T.
- MRM limit (Proposition 2 of the source): holding the intermittency coefficient lambda^2 = H(1 - 2H)·v^2 and the unit-scale variance fixed, as H -> 0 (v^2 -> inf, m -> -inf) the log S-fBM converges weakly to a log-normal MRM with intermittency lambda^2 and integral scale T.
- Empirically, stock indices have H ~ 0.1 (rough regime), while individual stocks have H very close to 0 — well described by a multifractal MRM. The intermittency coefficient lambda^2 is far more reliably estimated than v^2 alone and appears near-universal within each class.
- Connects to the inverse-renormalization time-series construction, which is explicitly built to reproduce multiscaling (q-dependent Hurst exponent) of aggregated returns.

## Appears in
- [[source-log-sfbm-multifractal-vol]] — defines the log S-fBM family, recovers the multifractal MRM/MRW as its H -> 0 limit, and provides GMM estimation of H and the intermittency coefficient.
- [[source-scaling-renormalization-time-series]] — builds a return model exhibiting multiscaling (q-dependent generalized Hurst exponent H_q) via an inverse renormalization-group construction.

## Related
- [[concept-rough-volatility]] — the H > 0 end of the same log S-fBM bridge; multifractal volatility is its H -> 0 limit.
- [[concept-scaling-renormalization]] — the time-scaling symmetry and RG machinery from which multiscaling emerges.
- [[concept-volatility-stylized-facts]] — multiscaling and intermittency are among the robust empirical features of returns.
- [[concept-implied-volatility-surface]] — the surface fine structure such volatility models would ultimately drive.
