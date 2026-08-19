---
title: Implied Volatility Surface
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Implied Volatility Surface

The Black–Scholes implied volatility of a European option viewed as a function of two coordinates — log-strike (or moneyness) and time-to-maturity — so that the whole cross-section of option prices at a given date is summarized by a single two-dimensional surface. Treated dynamically, this surface is a state variable: an observable random field that fluctuates in time rather than a byproduct of an underlying-asset model.

## Details
- For each strike K and maturity T, the implied volatility sigma_BS(k, tau) is the unique volatility that, plugged into the Black–Scholes formula, reproduces the market option price; here k = log(K/F) is log-moneyness and tau = T - t is time-to-maturity.
- Equivalent representations: implied volatility sigma_BS(k, tau), or total implied variance w(k, tau) = sigma_BS^2(k, tau) · tau (the natural coordinate for arbitrage analysis and SVI).
- A single maturity slice is the "smile"/"skew"; stacking slices across maturities gives the full surface. Equity index surfaces typically show a downward skew in k and a term structure in tau.
- As a state variable, the surface can be modeled directly (Cont–da Fonseca factor dynamics, Schweizer–Wissel term-structure models) rather than derived from a spot-volatility process; option markets are treated as autonomous, carrying option-specific randomness.
- In the CFMM setting the same object is repurposed: an implied volatility is attached to a liquidity profile by equating model impermanent loss to option-implied impermanent loss, yielding a "price of liquidity" surface with its own smile and a fine structure over price segments.

## Appears in
- [[source-rtw26-cfmm-liquidity-pricing-hedging]] — defines an implied volatility (Black–Scholes and Bachelier) for a liquidity profile and a fine structure of implied volatility over price segments, exhibiting a smile consistent with crypto-asset dynamics.
- [[source-arbitrage-free-svi]] — the surface (in total-variance coordinates) is the object the SVI/SSVI parametrization is designed to fit while ruling out static arbitrage.
- [[source-dynamics-implied-vol-surfaces]] — the surface is treated as a randomly fluctuating state variable and decomposed empirically into a few orthogonal factors.

## Related
- [[concept-svi-parametrization]] — a parametric functional form for the surface's total-variance slices.
- [[concept-static-arbitrage]] — the shape constraints (calendar + butterfly) a valid surface must satisfy.
- [[concept-iv-term-structure-arbitrage]] — arbitrage-free dynamics of the surface across maturities.
- [[concept-volatility-surface-dynamics]] — how the surface deforms day to day as a random field.
- [[concept-functional-pca]] — the method that reduces the surface's variations to a few factors.
- [[concept-liquidity-surface]] — the CFMM analogue; a liquidity-profile implied vol surface is its option-language image.
- [[entity-jim-gatheral]] — co-author of the SVI/rough-volatility machinery for the surface.
- [[entity-deribit]] — source of the ETH option quotes used to build the liquidity-profile implied vol surface.
