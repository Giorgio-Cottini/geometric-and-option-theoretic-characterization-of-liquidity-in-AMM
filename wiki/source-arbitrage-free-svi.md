---
title: Arbitrage Free Svi
layer: core
type: source
origin: thesis
source_path: "articles/vol surface/Arbitrage-free SVI volatility surfaces.pdf"
source_kind: paper
date: 2026-07-19
---

# Arbitrage-free SVI volatility surfaces

Shows how to calibrate the widely-used SVI (stochastic-volatility-inspired) parametrization of the implied-volatility smile so as to guarantee absence of static arbitrage, exhibiting a large class of arbitrage-free "SSVI" surfaces with a simple closed-form representation.

**Authors / venue / year:** Jim Gatheral (Baruch College, CUNY) and Antoine Jacquier (Imperial College London). arXiv:1204.0646v4 [q-fin.PR], dated November 27, 2024 (originally 2013/2014, Quantitative Finance).

## Key points
- Static arbitrage decomposes into two conditions: absence of calendar-spread arbitrage (total variance non-decreasing in maturity) and absence of butterfly arbitrage (non-negative risk-neutral density in each maturity slice).
- Recalls three equivalent single-slice SVI parametrizations of total implied variance `w(k) = sigma_BS^2(k) t`: raw SVI (params a,b,rho,m,sigma), natural SVI (Delta,mu,rho,omega,zeta), and SVI-Jump-Wings (SVI-JW, trader-intuitive: ATM variance, ATM skew, put/call wing slopes, minimum variance), with explicit maps between them.
- Calendar-spread arbitrage between two raw-SVI slices reduces to checking whether a certain quartic polynomial has no real root (a sufficient condition, closed-form via Ferrari/Cardano).
- Butterfly arbitrage in a slice is governed by a function g(k) (Eq. 2.1): the slice is butterfly-free iff g(k) >= 0 for all k and d_+(k) -> -inf as k -> inf. Raw SVI has no simple general parameter conditions to preclude butterfly arbitrage; the authors give a counterexample (Vogt smile).
- Introduces SSVI ("Surface SVI"), extending the natural parametrization: `w(k,theta_t) = (theta_t/2){1 + rho phi(theta_t) k + sqrt((phi(theta_t)k + rho)^2 + 1 - rho^2)}`, where theta_t is the ATM total variance and phi a smooth function. This expresses the surface in terms of ATM variance time.
- Gives precise necessary-and-sufficient calendar-spread conditions (Theorem 4.1) and sufficient butterfly conditions (Theorem 4.2) for SSVI, plus a static-arbitrage-free corollary (Corollary 4.1). Provides concrete phi choices: a Heston-like parametrization and a power-law parametrization.
- Provides a practical calibration recipe (square-root SVI initial guess, then slice-by-slice fit with a crossedness penalty) and shows how to interpolate/extrapolate calibrated slices while keeping the whole surface static-arbitrage-free.

## Notable claims & data
- Raw SVI (Eq. 3.1): `w(k) = a + b{rho(k-m) + sqrt((k-m)^2 + sigma^2)}`, with `a + b sigma sqrt(1-rho^2) >= 0` ensuring non-negativity; asymptotically linear in |k| consistent with Roger Lee's moment formula.
- Butterfly function (Eq. 2.1): `g(k) = (1 - k w'(k)/(2 w(k)))^2 - (w'(k)^2/4)(1/w(k) + 1/4) + w''(k)/2`; density `p(k) = g(k)/sqrt(2 pi w(k)) exp(-d_-(k)^2/2)`.
- SSVI calendar-spread (Theorem 4.1): free iff `d_t theta_t >= 0` and `0 <= d_theta(theta phi(theta)) <= (1/rho^2)(1 + sqrt(1-rho^2)) phi(theta)`.
- SSVI butterfly (Theorem 4.2): free if `theta phi(theta)(1+|rho|) < 4` and `theta phi(theta)^2 (1+|rho|) <= 4`. Condition 1 is necessary (matches Lee's asymptotic slope bound of 2); Condition 2 is tight.
- Vogt counterexample (Example 3.1): raw SVI params (a,b,m,rho,sigma) = (-0.0410, 0.1331, 0.3586, 0.3060, 0.4153), t=1, exhibits negative density.
- Numerical example calibrates SVI to recent SPX options data with high-quality fits.

## Open questions
- SVI is a static, cross-sectional smile parametrization; it does not specify dynamics of the surface over time (contrast: Cont-da Fonseca dynamics, Schweizer-Wissel term-structure existence).
- Connection to CFMM liquidity provision: the anchor paper (RTW26) defines an implied-volatility smile for liquidity profiles and observes a smile consistent with crypto-asset dynamics — SVI provides the arbitrage-free surface machinery that could parametrize and constrain such liquidity-profile-implied smiles, ensuring the "price of liquidity" surface is itself arbitrage-free.
- Leaves open whether rough-volatility-generated smiles (with power-law ATM skew) can always be represented within the arbitrage-free SSVI class, and how to link SVI parameters to a generating stochastic (or rough) volatility model.
