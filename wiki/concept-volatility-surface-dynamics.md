---
title: Volatility Surface Dynamics
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Volatility Surface Dynamics

The empirical description of how an implied-volatility surface deforms over time: daily variation of the surface treated as a fluctuating random field driven by a few orthogonal, mean-reverting factors — a "level" factor, a "skew"/twist factor, and a "butterfly"/convexity factor — rather than as a deterministic byproduct of the underlying's moves.

## Details
- The surface is a state variable modeled directly. Applying functional PCA to daily log-variations of implied volatility yields a low-dimensional factor model: the first three eigenmodes account for ~98% of daily variance.
- Factor interpretation (SP500, Cont–da Fonseca): mode 1 (~94% of variance) is an all-positive "level" shock, strongly negatively correlated with the underlying (the leverage effect); mode 2 (~3%) changes sign at the money — a "skew"/twist factor; mode 3 (~0.8%) is a "butterfly"/convexity factor.
- Each principal-component process is highly autocorrelated and mean-reverting (Ornstein–Uhlenbeck / AR(1)-like), with reversion times near one month (e.g. mode 1 ~28 days, AR(1) ≈ 0.965; mode 2 ~12.6 days).
- Representation: I_t(m, tau) = I_0(m, tau)·exp(sum_k x_k(t)·f_k) with eigenmodes f_k and uncorrelated scores x_k(t); scores show excess kurtosis but only mild deviation from normality.
- Practical consequences: refutes deterministic "sticky moneyness"/"sticky strike" rules — the surface has non-negligible own-randomness that must enter Vega hedging; enables Monte Carlo scenario generation and a decomposition of Vega risk into identifiable factors. The picture is descriptive (physical-measure) and coarse-timescale, not by itself arbitrage-free.

## Appears in
- [[source-dynamics-implied-vol-surfaces]] — the empirical study establishing the fluctuating-random-field, few-factor, mean-reverting description of the IV surface.

## Related
- [[concept-functional-pca]] — the method that extracts the level/skew/butterfly factors and their scores.
- [[concept-implied-volatility-surface]] — the object whose day-to-day motion is described.
- [[concept-iv-term-structure-arbitrage]] — the arbitrage-free-dynamics theory this descriptive model complements (it does not itself guarantee no-arbitrage).
- [[concept-volatility-stylized-facts]] — the leverage effect and heavy-tailed factor scores appear here.
- [[concept-liquidity-surface]] — the CFMM analogue whose factor scores follow AR(1)-GARCH dynamics, decomposed by the same method.
- [[concept-rough-volatility]] — the small-time roughness this coarse OU picture does not capture.

## Connections
- [[markets-worldview]] — cross-region (personal): names "mean reversion of the volatility surface" as a market property worth trading; this page is the quantitative description of that same object's dynamics.
