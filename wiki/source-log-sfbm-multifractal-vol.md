---
title: Log Sfbm Multifractal Vol
layer: core
type: source
origin: thesis
source_path: "articles/vol surface/roughness/From rough to multifractal volatility (The log S-fBM model).pdf"
source_kind: paper
date: 2026-07-19
---

# From rough to multifractal volatility: The log S-fBM model

Introduces the log S-fBM (log stationary-fractional-Brownian-motion) family of random measures, a unified framework that continuously bridges rough volatility (Hurst exponent H > 0) and multifractal volatility (the H -> 0 limit, recovering the Multifractal Random Measure), and proposes a reliable GMM estimation method for its parameters.

**Authors / venue / year:** Peng Wu (Universite Paris-Dauphine PSL), Jean-Francois Muzy (Universite de Corse), and Emmanuel Bacry (Universite Paris-Dauphine). Physica A 604 (2022) 127919.

## Key points
- Defines a family of random measures `M_{H,T}(dt) = e^{omega_{H,T}(t)} dt` where omega is a stationary Gaussian process — a stationary version of an H-fractional Brownian motion (the "S-fBM"), whose covariance is exactly the small-time approximation of the fractional Ornstein-Uhlenbeck correlation used in the RFSV rough-volatility model.
- Unifies two popular stochastic-volatility classes under one construction: the Rough Fractional Stochastic Volatility (RFSV) model for H > 0, and the Multifractal Random Measure (MRM) / Multifractal Random Walk (MRW) recovered in the weak limit H -> 0.
- Shows that direct estimation of the roughness exponent H from the scaling of moments of the log-measure increments (the method advocated in the original rough-volatility literature) can strongly over-estimate H due to a systematic bias; provides an explicit bias analysis.
- Proposes a better GMM (generalized method of moments) estimation, based on the explicit covariance of the log S-fBM process (or its logarithm), shown to be valid even in the high-frequency asymptotic regime where data cover an interval smaller than the correlation scale T (no ergodicity assumption).
- Empirical finding on a large panel of equity volatility data: stock indices have H around 0.1, while individual stocks have H that can be very close to 0 (thus well modeled by a multifractal MRM). The correlation scale T of realized volatility appears to be very large (decades), which supports the high-frequency-regime analysis.
- Argues that the widely-used "intermittency coefficient" lambda^2 = H(1-2H) v^2 (product of the log-volatility variance v^2 and the Hurst exponent) is far more reliably estimated than v^2 alone, giving values that seem universal across individual stocks and across indices respectively.

## Notable claims & data
- S-fBM covariance (Eq. 8): `Cov(omega_{H,T}(t), omega_{H,T}(t+tau)) = (v^2/2)[T^{2H} - tau^{2H}]` for |tau| < T, and 0 for |tau| >= T (correlation exactly vanishes beyond lag T).
- Log S-fBM measure (Eq. 12-14): `M_{H,T}(dt) = e^{omega_{H,T}(t)} dt`, with unit-interval variance `sigma^2 = e^{m + v^2/2}`.
- MRM limit (Proposition 2): with lambda^2 = H(1-2H) v^2 and sigma^2 fixed, as H -> 0 (so v^2 -> inf, m -> -inf) the measure converges weakly to a log-normal MRM with intermittency lambda^2 and integral scale T.
- Scaling of generalized moments (Eq. 11): `E[|delta_tau omega_{H,T}(t)|^q] = C_q tau^{qH}`, so log-moments are linear in log(tau) with slope qH.
- Bias of the naive moment-scaling H estimate (Eq. 36): `H_hat = H + B_H/2`, biased upward (e.g. true H = 0.002 estimated as ~0.08).
- Provides explicit analytic formulas for the correlation function of the integrated measure and its logarithm (Propositions 3-5), and two GMM estimators (GMM_M on the measure, GMM_lnM on its logarithm) validated on simulations.

## Open questions
- Estimation of the correlation scale T and variance sigma^2 is unreachable in the high-frequency regime (they get absorbed into a redefinition of sigma^2); only H and lambda^2 are identifiable there.
- Whether the observed near-universality of the intermittency coefficient lambda^2 holds across other asset classes (e.g. crypto) is left open.
- Connection to CFMM liquidity provision: this supplies the empirically-grounded model of the roughness/multifractality of the volatility that drives asset prices. In the anchor paper (RTW26) the LP's impermanent loss and LVR are integrals against the quadratic variation d<P> of the pool price — so the roughness of the volatility process directly shapes LVR and the liquidity-profile implied-vol fine structure, making log S-fBM a candidate driving process for extending the CFMM framework to realistic (rough/multifractal) crypto-price dynamics.
