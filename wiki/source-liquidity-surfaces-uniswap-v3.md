---
title: Liquidity Surfaces Uniswap V3
layer: core
type: source
origin: thesis
source_path: "articles/liquidity/DYNAMICS OF LIQUIDITY SURFACES IN UNISWAP V3.pdf"
source_kind: paper
date: 2026-07-19
---

# Dynamics of Liquidity Surfaces in Uniswap V3

An empirical study modelling Uniswap V3 liquidity as a time-tick surface L_t(x) and analyzing it with functional principal component analysis (FPCA) and dynamic factor methods, finding a stable low-rank structure that aligns with a low-order Legendre polynomial basis and factor coefficients well captured by AR(1)-GARCH with heavy tails.

**Authors / venue / year:** Jimmy Risk, Shen-Ning Tung, and Tai-Ho Wang; arXiv:2509.05013v1 [q-fin.TR], dated September 8, 2025.

## Key points
- Models aggregated Uniswap V3 liquidity as a two-dimensional liquidity surface L_t(x), indexed by block-time t and (standardized) relative tick distance x from the current price, filling a gap left by prior work that focused on static range-allocation or fee-tier optimization.
- Applies functional principal component analysis (FPCA) and dynamic factor models to obtain a parsimonious, interpretable low-rank factor representation of the surface — decomposing y_t(x) = log L_t(x) into K factors (loadings/basis u_k(x) and time-varying coefficients/scores beta_{t,k}) plus a residual, decoupling spatial (x) and temporal (t) structure.
- Motivated by the analogy with the (Dynamic) Nelson-Siegel term-structure model for yield curves, whose level/slope/curvature factors align with principal components; the authors seek a similar interpretable low-dimensional structure for the liquidity surface.
- Finds that the nonparametric empirical eigenmode basis consistently aligns well with the Legendre polynomial basis, providing a portable, interpretable fixed basis for dimension reduction; eigenmode structure remains stable across time windows (quantified via subspace distance metrics).
- Temporal factor coefficients beta_{t,k} exhibit persistent AR(1)-type dynamics with GARCH-style conditional heteroskedasticity and heavy-tailed innovations; forecasting the surface reduces to forecasting the factor scores.
- Analyzes dynamics via rolling-window metrics and studies the effect of volatility shocks through the orthogonal Legendre/eigenmode components; robustness verified across preprocessing schemes.

## Notable claims & data
- Three pools analyzed: Ethereum Mainnet 5bps ETH-USDC (primary, deep liquidity), Ethereum Mainnet 30bps ETH-USDC (fee-tier / tickSpacing comparison), and Arbitrum 5bps ARB-USDC (cross-environment robustness check). Data sourced from an internal Teahouse Finance API.
- Dataset ranges (Table 1): ARB5 ARB-USDC blocks 124163200 to 278646400 (Aug 23, 2023 - Nov 26, 2024), block spacing 115200 (~8.39 h); ETH5/ETH30 ETH-USDC blocks 12940529 to 21274529 (Aug 1, 2021 - Nov 26, 2024), block spacing 2400 (~8.26 h). Both target ~8-hour time spacing.
- For the 5bps pools, leading empirical eigenfunctions explain the majority of cross-tick variation and remain stable, aligning closely with a low-order Legendre polynomial basis (parallel to the Nelson-Siegel factors for yield curves).
- Tick grid: price at integer tick i is P(i) = 1.0001^i (each tick = 0.01% = 1 bp); liquidity ranges set at tick-spacing multiples s (e.g., s = 10 for a 0.05% fee tier); total liquidity L_total(p) = sum_i L_i * 1_{[p_l,i, p_r,i]}(p).
- Main analysis uses M = 201 ticks, so x = 0 is the current price and x spans {-1.0,...,-0.01} and {0.01,...,1.0} (100 log-prices each side); relative-tick coordinate normalizes the current pool price tick to 0.
- Stylized facts confirmed: a large fraction of liquidity mass lies near the current price (large L near x = 0, possibly with peaks further out); surface shape varies with LP risk preferences; high volatility widens LP ranges and lowers the central peak, low volatility tightens/steepens concentration.

## Open questions
- Whether the low-rank Legendre/eigenmode structure and AR(1)-GARCH temporal dynamics generalize to other pools, fee tiers, and asset pairs beyond ETH-USDC and ARB-USDC.
- How to connect this empirical, statistical description of the liquidity surface to structural/theoretical CLMM models of liquidity provision (e.g., the measure-valued liquidity-profile framework), bridging data-driven and mechanistic views.
- Using the factor decomposition for forecasting, risk assessment, and impermanent-loss / LP-return estimation; extracting actionable capital-efficiency and optimal range-allocation strategies for liquidity providers.
- Impact of block-time vs clock-time indexing and cross-chain block-rate differences (Ethereum ~12 s vs Arbitrum ~0.25 s per block) on the estimated surface dynamics.
