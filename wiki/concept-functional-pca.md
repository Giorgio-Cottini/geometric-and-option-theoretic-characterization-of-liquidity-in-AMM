---
title: Functional Pca
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Functional PCA (Karhunen–Loève Decomposition)

The generalization of principal component analysis to a random field or random function: a Karhunen–Loève decomposition that separates a fluctuating surface into a small number of spatial eigenmodes (loadings/basis functions over the surface's coordinates) and uncorrelated temporal factor scores. It is the key methodological connector of the thesis — the same decomposition is applied to the Uniswap liquidity surface and to the implied-volatility surface, in each case reducing a high-dimensional surface to a few interpretable factors.

## Details
- Represents daily variations of a surface Z_t(·) as Z_t = Z_0 + sum_k x_k(t)·f_k, where f_k are orthogonal eigenmodes (spatial loadings) and x_k(t) are uncorrelated principal-component processes (temporal scores). Numerically it is a Fredholm eigenvalue problem, solved e.g. by a Galerkin method with a spline basis.
- Dimension reduction: eigenvalues decay quickly with rank, so a low-rank truncation (often 3 factors) captures the overwhelming majority of variance; forecasting/risk of the whole surface reduces to modeling a handful of factor scores.
- IV surface (Cont–da Fonseca): applied to daily log-variations of implied volatility in (moneyness, maturity); the first three eigenmodes explain ~98% of variance and are interpreted as level, skew/twist and butterfly/convexity factors.
- Liquidity surface (Risk–Tung–Wang): the same FPCA applied to y_t(x) = log L_t(x) over relative-tick distance x; the nonparametric empirical eigenbasis aligns closely with a low-order Legendre polynomial basis and is stable across time windows.
- The parallel with the (Dynamic) Nelson–Siegel yield-curve model — whose level/slope/curvature factors align with principal components — motivates both applications; the decoupling of spatial structure (loadings) from temporal dynamics (scores) is what makes the surface tractable.

## Appears in
- [[source-liquidity-surfaces-uniswap-v3]] — FPCA/dynamic-factor decomposition of the Uniswap V3 log-liquidity surface into Legendre-aligned loadings and AR(1)-GARCH factor scores.
- [[source-dynamics-implied-vol-surfaces]] — Karhunen–Loève decomposition of daily implied-volatility variations into level/skew/butterfly eigenmodes with mean-reverting scores.

## Related
- [[concept-liquidity-surface]] — one of the two surfaces FPCA decomposes (Uniswap V3 liquidity).
- [[concept-implied-volatility-surface]] — the other surface FPCA decomposes (option implied vol).
- [[concept-volatility-surface-dynamics]] — the factor picture of IV-surface motion that FPCA produces.
- [[concept-graph-embedding]] — a related low-dimensional-representation technique in the codebase.
- [[entity-jimmy-risk]] — co-author of the liquidity-surface FPCA study.
- [[entity-tai-ho-wang]] — co-author of the liquidity-surface FPCA study.
- [[entity-shen-ning-tung]] — co-author of the liquidity-surface FPCA study.
