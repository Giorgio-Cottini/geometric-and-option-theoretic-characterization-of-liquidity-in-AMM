---
title: Liquidity Surface
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Liquidity Surface

The liquidity surface is a two-dimensional object L_t(x) that describes the amount of liquidity available at each relative tick x around the current pool price, evolving over block-time t. It generalizes a single scalar liquidity number into a full cross-sectional shape observed and re-observed at every block.

## Details
- Two indices: block-time t (when) and relative tick offset x from the current price (where in price space).
- Naturally analogized to an implied-volatility surface: a smooth field over two coordinates whose dynamics are the modelling target.
- Modelled with a low-rank functional-PCA basis: a small number of factors reconstruct the whole cross-section L_t(·) at each t.
- The FPCA basis is aligned to Legendre polynomials, giving interpretable level/slope/curvature-style loadings across the tick axis.
- Factor dynamics are time series: AR(1) mean reversion with GARCH conditional variance and heavy-tailed innovations, capturing volatility clustering and fat tails in liquidity movements.
- Low rank means the surface lives in a small effective dimension, so a handful of factor paths reproduce the observed liquidity landscape.

## Appears in
- [[source-liquidity-surfaces-uniswap-v3]] — introduces and estimates the surface object, its FPCA basis, and the factor time-series model on Uniswap v3 pools.
- [[source-wang-bocconi-2]] — treats the concentrated-liquidity landscape as the controlled state in an optimal-provision problem, complementing the descriptive surface view.

## Related
- [[concept-functional-pca]] — supplies the low-rank basis used to represent the surface cross-section.
- [[concept-liquidity-profile]] — the single-time snapshot L_t(·) whose stacked history forms the surface.
- [[concept-uniswap-v3-ticks]] — defines the relative-tick x axis on which the surface is indexed.
- [[concept-concentrated-liquidity]] — the mechanism that makes liquidity vary across ticks, giving the surface its shape.
- [[concept-volatility-surface-dynamics]] — the implied-volatility-surface analogue whose modelling techniques the liquidity surface borrows.
- [[concept-volatility-stylized-facts]] — the clustering and heavy-tail features the GARCH factor dynamics reproduce.
