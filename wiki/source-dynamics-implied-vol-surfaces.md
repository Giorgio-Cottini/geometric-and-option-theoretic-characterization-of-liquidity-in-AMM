---
title: Dynamics Implied Vol Surfaces
layer: core
type: source
origin: thesis
source_path: "articles/vol surface/Dynamics of Implied Volatility Surfaces.pdf"
source_kind: paper
date: 2026-07-19
---

# Dynamics of Implied Volatility Surfaces

An empirical study showing that the implied-volatility surface of index options deforms over time as a randomly fluctuating surface driven by a small number of orthogonal random factors, identified and interpreted via a Karhunen-Loeve (functional PCA) decomposition of daily implied-volatility variations.

**Authors / venue / year:** Rama Cont (Ecole Polytechnique) and Jose da Fonseca (Ecole Superieure d'Ingenierie Leonard de Vinci). Quantitative Finance, Vol. 2 (2002), pp. 45-60.

## Key points
- Treats the implied-volatility surface as a state variable (an observable market quantity) rather than deriving it from an underlying-asset model; argues option markets have become autonomous, so option-specific randomness must be modeled directly.
- Constructs a daily time series of smooth implied-vol surfaces from SP500 and FTSE index option data via non-parametric Nadaraya-Watson kernel smoothing in (moneyness, time-to-maturity) coordinates.
- Applies a Karhunen-Loeve decomposition (generalization of PCA to random fields) to daily log-variations of implied volatility; numerically solved as a Fredholm eigenvalue problem via a Galerkin method with spline basis functions.
- Finds that a low-dimensional factor model captures the dynamics: the first three eigenmodes account for ~98% of the daily variance. Each principal-component process is highly autocorrelated and mean-reverting (Ornstein-Uhlenbeck / AR(1)-like) with mean-reversion time near one month.
- Interprets the eigenmodes: first mode (~94% variance) is a "level" factor (all-positive shock, strongly negatively correlated with the underlying — the leverage effect); second mode (~3%) changes sign at the money (a skew/"twist" factor); third mode (~0.8%) is a "butterfly"/convexity factor.
- Refutes the practitioner "sticky moneyness" / "sticky strike" deterministic rules: the surface has a non-negligible standard deviation that must be accounted for in Vega hedging of option portfolios.
- Proposes a parsimonious stochastic factor model of the surface (stationary random field with empirically-matched covariance) enabling Monte Carlo scenario generation and a decomposition of Vega risk into empirically identifiable factors.

## Notable claims & data
- Data: end-of-day European call/put prices on SP500 (CBOE, Mar 2000-Feb 2001) and FTSE 100 (LIFFE, ~2 years to Aug-Sep 2001); moneyness filtered to [0.5, 1.5], tau from ~2 weeks to over a year.
- Karhunen-Loeve representation (Eq. 21): `I_t(m,tau) = I_0(m,tau) exp(sum_k x_k(t) f_k)` with eigenmodes f_k and uncorrelated principal-component processes x_k(t).
- SP500 summary statistics (Table 1): eigenmode 1 — 94% of variance, mean-reversion 28 days, correlation with underlying -0.66; eigenmode 2 — 3% variance, mean-reversion 12.6 days, correlation ~0; eigenmode 3 — 0.8% variance, mean-reversion 22 days, correlation 0.27. All series show excess kurtosis but mild deviation from normality.
- First eigenmode ~80% of daily variance, AR(1) autoregression constant 0.965 (28-day mean reversion); second mode AR(1) 0.924 (12.6-day).
- Eigenvalues decay quickly with rank, justifying the low-dimensional truncation.

## Open questions
- The proposed factor model is descriptive/statistical (fitted to physical-measure dynamics); it does not by itself guarantee absence of arbitrage in the modeled surface dynamics (contrast Schweizer-Wissel, which derives the drift restrictions required for arbitrage-free implied-vol term structures).
- Does not address the small-time roughness of volatility later documented by rough-volatility models; the mean-reverting OU picture of the factors is a coarse-timescale view.
- Connection to CFMM liquidity provision: provides the empirical, market-based description of how an implied-vol surface actually moves — relevant to the anchor paper's (RTW26) liquidity-profile implied-vol surface, where an LP is exposed to Vega risk from forward-looking volatility shifts and would need a factor model to hedge that surface risk.
