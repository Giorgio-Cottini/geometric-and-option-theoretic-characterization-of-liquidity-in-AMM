---
title: Volatility Stylized Facts
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Volatility Stylized Facts

The robust, cross-market empirical regularities of financial-asset returns that any credible return/volatility model must reproduce: volatility clustering, fat-tailed (heavy) return distributions, the leverage effect, and time-reversal asymmetry (a broken time-reversal symmetry). They serve as the acceptance test for the return models built via scaling/renormalization and as descriptive facts about the surfaces studied in the thesis.

## Details
- Volatility clustering: large moves tend to follow large moves; the autocorrelation of |returns| or squared returns decays slowly (often power-law-like), while raw returns are nearly uncorrelated.
- Fat tails: the return PDF has power-law tails, f(x) ~ |x|^{-alpha-1}, so extreme moves are far more frequent than Gaussian; tail index alpha ties directly to the scaling-function/mixing-density decay in the renormalization model.
- Leverage effect: negative correlation between returns and future volatility — volatility rises more after price drops. In the implied-vol surface this appears as the "level" factor being strongly negatively correlated with the underlying.
- Time-reversal asymmetry: return dynamics are not statistically invariant under time reversal (past and future are distinguishable), a property provably held by the inverse-RG return model and generally violated by simple symmetric GARCH.
- Multiscaling (a q-dependent generalized Hurst exponent) is a further, finer stylized fact linking to multifractal volatility.
- The return process is (near-)martingale/efficient-market consistent while still exhibiting all the above nonlinear dependence.

## Appears in
- [[source-scaling-renormalization-time-series]] — the inverse-RG model is calibrated to reproduce clustering, fat tails, multiscaling, leverage and time-reversal-symmetry breaking on S&P500 data.
- [[source-dynamics-implied-vol-surfaces]] — the leverage effect appears empirically as the strong negative correlation of the surface's level factor with the underlying, and factor scores show excess kurtosis.

## Related
- [[concept-scaling-renormalization]] — the construction engineered to reproduce these facts from scaling symmetry.
- [[concept-multifractal-volatility]] — multiscaling and intermittency as higher-order stylized facts.
- [[concept-rough-volatility]] — path roughness of volatility as an additional empirical regularity.
- [[concept-volatility-surface-dynamics]] — where the leverage effect manifests in surface factors.
