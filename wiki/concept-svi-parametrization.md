---
title: Svi Parametrization
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# SVI / SSVI Parametrization

The Stochastic-Volatility-Inspired (SVI) family of closed-form functional forms for the implied-variance smile, and its surface-level extension SSVI ("Surface SVI"). SVI fits a single maturity slice of total implied variance with five parameters; SSVI ties the slices together as a low-parameter, tractable model of the whole surface expressed in terms of at-the-money total variance.

## Details
- Raw SVI (single slice): w(k) = a + b{rho(k - m) + sqrt((k - m)^2 + sigma^2)}, with parameters (a, b, rho, m, sigma). Non-negativity requires a + b·sigma·sqrt(1 - rho^2) >= 0; the wings are asymptotically linear in |k|, consistent with Roger Lee's moment formula.
- Three equivalent single-slice forms with explicit maps: raw SVI (a, b, rho, m, sigma), natural SVI (Delta, mu, rho, omega, zeta), and SVI-Jump-Wings (SVI-JW), the trader-intuitive form parametrized by ATM variance, ATM skew, put/call wing slopes and minimum variance.
- SSVI: w(k, theta_t) = (theta_t/2){1 + rho·phi(theta_t)·k + sqrt((phi(theta_t)k + rho)^2 + 1 - rho^2)}, where theta_t is the ATM total variance and phi a smooth positive function; concrete choices include a Heston-like and a power-law phi.
- SSVI makes static-arbitrage control explicit: calendar-spread-free and butterfly-free conditions become closed-form inequalities on theta and phi (Theorems 4.1–4.2 of the source), giving a large tractable class of arbitrage-free surfaces.
- Practical calibration: square-root-SVI initial guess, then slice-by-slice fit with a crossedness penalty, interpolating/extrapolating while preserving whole-surface arbitrage-freeness.

## Appears in
- [[source-arbitrage-free-svi]] — introduces raw/natural/SVI-JW slices and the SSVI surface, and derives the parameter conditions that guarantee absence of static arbitrage.

## Related
- [[concept-implied-volatility-surface]] — the object SVI/SSVI parametrizes (in total-variance coordinates).
- [[concept-static-arbitrage]] — the constraints SVI calibration is designed to respect (calendar + butterfly).
- [[concept-rough-volatility]] — an open question is whether rough-volatility smiles (power-law ATM skew) always sit inside the arbitrage-free SSVI class.
- [[concept-iv-term-structure-arbitrage]] — SVI is a static cross-sectional fit; term-structure models supply the missing arbitrage-free dynamics.
- [[entity-jim-gatheral]] — co-author of the SVI/SSVI framework.
