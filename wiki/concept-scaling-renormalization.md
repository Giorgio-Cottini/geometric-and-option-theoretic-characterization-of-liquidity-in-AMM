---
title: Scaling Renormalization
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Scaling Symmetry and (Inverse) Renormalization

The use of time-scaling (Hurst) symmetry — the property that aggregated returns rescale in law under a time-and-amplitude transformation — together with an inverse renormalization-group construction that fine-grains elementary increments from the known scaling of their aggregates, to build tractable return models that reproduce the empirical stylized facts.

## Details
- Simple-scaling symmetry: t^H·g_t(t^H·x) = g(x) for the aggregated-increment PDF, giving moment scaling E[|X_1 + ... + X_t|^q] = t^{q·H}·E[|X_1|^q]. Gaussian g with H = 1/2 is normal diffusive scaling; non-Gaussian g and/or H != 1/2 is anomalous; a q-dependent H_q is multiscaling (the generalized Hurst exponent).
- Inverse renormalization group: instead of coarse-graining toward a fixed point, invert the RG flow — take the observed scaling of aggregated returns as input and fine-grain to recover probabilistic rules for elementary increments consistent with that scaling.
- Schoenberg's theorem characterizes admissible scaling functions g as Gaussian mixtures, g(x) = ∫ dsigma·rho(sigma)·N_sigma(x); the joint PDF is a mixture over rho of products of centered Gaussians.
- Model structure: each return factorizes into an endogenous long-memory ARCH-like component {Y_t} of memory order M and a short-memory rescaling factor {a_{I_t}} driven by a Markov-chain "time-restart" mechanism; rescaling factors a_i = sqrt(i^{2D} - (i-1)^{2D}) with parameter D replacing the Hurst exponent H (D < 1/2 decaying, finance-relevant).
- Low parameter count (typically 5) allows calibration by generalized method of moments; choosing rho inverse-gamma makes the endogenous part a genuine ARCH process with Student-t residuals, connecting to the SWARCH family.

## Appears in
- [[source-scaling-renormalization-time-series]] — constructs the return model by inverting the RG flow under time-scaling symmetry and calibrates it on S&P500 daily data 1950–2010.

## Related
- [[concept-multifractal-volatility]] — multiscaling (q-dependent H_q) is exactly the anomalous-scaling regime this framework targets.
- [[concept-rough-volatility]] — shares the Hurst/fractional-scaling language; roughness is a small-H scaling of volatility.
- [[concept-volatility-stylized-facts]] — the empirical features (clustering, fat tails, time-reversal asymmetry) the construction is calibrated to reproduce.
