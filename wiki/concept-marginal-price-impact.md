---
title: Marginal Price Impact
layer: core
type: concept
origin: thesis
date: 2026-07-22
---

# Marginal Price Impact of a CFMM

How far a trade moves the pool price, per unit traded, at a given price and time. For a
concentrated-liquidity pool this is a pointwise function of the active liquidity and the price
alone, so it can be read directly off the historical liquidity surface with no new data and no new
reconstruction. It is the first extension quantity the thesis derives beyond the replicated
surfaces. The code that computes and renders it is described in [[concept-price-impact-code]].

## Definition

With `P` the pool price and `L` the active in-range liquidity at that price and time:

- **Absolute** marginal impact: `dP/dx = 2 · P^{3/2} / L` — price movement per unit traded.
- **Relative** marginal impact: `d ln P/dx = 2 · P^{1/2} / L` — fractional price movement per unit
  traded.

Both follow from the constant-product invariant in its concentrated form, where `x = L/√P` is the
reserve of the base asset along the active range. Their ratio is exactly `P`, which is one of the
numerical checks on the implementation. Only magnitudes are plotted; the direction of the swap is
not the subject.

Impact is the reciprocal of depth, so everything the liquidity surface says about
[[concept-concentrated-liquidity]] carries over inverted: where LPs have concentrated capital,
impact is low; where the book thins out, impact rises. What the transform adds is that it puts
the depth on an economically meaningful scale — price units per unit of asset traded — rather than
the `√(token0·token1)` units of `L` itself.

## The denominator is always the base token

The formulas are derived in the AMM-native frame, where `P` is token1 per token0 and `x` is the
token0 reserve, so "per unit `x`" means per unit of token0. Roughly half the pools in the dataset
are stored with the opposite on-chain ordering and their human-facing price is the reciprocal
`Q = 1/P`. Substituting `Q` into the same expression is nonetheless correct, because the invariant
is symmetric under the flip:

```
dy = (L/2) P^{-1/2} dP,     dQ = -dP/P^2     =>     dQ/dy = -2 Q^{3/2} / L
```

Identical functional form, with the trade now denominated in token1 instead of token0. `L` itself
is unchanged: `L = √(x·y)` is symmetric, and its decimal normalisation by `10^{(d0+d1)/2}` is a
geometric mean, hence symmetric too. The orientation flag flips the quoted price *and* the reserve
leg together, so the trade denominator is always the **base** token — the denominator of the quote.

For `WETH/USDC` the absolute impact is therefore `d(USDC per WETH) / d(WETH)`: dollars of
ETH-price movement per ETH traded. This was verified empirically rather than assumed: the
at-the-money absolute impact for `WETH_USDC` at 5bp reads about `-1.19` in `log10`, that is
roughly `0.064` USDC per WETH per WETH traded. Had the quantity been denominated per USDC instead,
the same figure would sit near `-11`. The gap is large enough that the check is unambiguous.

## Log-moneyness axes depend on pool orientation

The surface builders fix one x-array for every pool, `x = (curr_tick − tick_idx) · log(1.0001)`.
Whether that array *is* log-moneyness `log(K/S)` depends on which way human price runs with tick,
which is exactly what the orientation flag selects. When price falls as tick rises the array is
`log(K/S)`; when price rises with tick, the identical array is `log(S/K)`. The numbers do not
move, only the name does.

The distinction was invisible on the near-symmetric log-liquidity surfaces and became visible on
impact, which is genuinely asymmetric in price: absolute impact scales as `P^{3/2}` against
relative impact's `P^{1/2}`, so the two sides of the money are steeper and flatter respectively
rather than mirror images. Before this was fixed, every figure in the study was labelled `log(K/S)`
while eight of the eleven pools were native-ordered and should have read `log(S/K)`.

## What the figures show

Rendered as profiles, three-dimensional surfaces, and heatmaps, on log-moneyness, relative-tick,
and absolute-tick axes, per pool, in `log10`:

- The profile is V-shaped with its minimum at the money — impact is cheapest where liquidity is
  concentrated, and rises away from spot in both directions.
- The absolute quantity is visibly steeper on the upside than the downside, the `P^{3/2}` against
  `P^{1/2}` asymmetry noted above; the relative quantity is much closer to symmetric.
- No clipping, no percentile normalisation, and no artificial rescaling is applied, so magnitudes
  are comparable across pools and across fee tiers of one pair.

Across fee tiers of a single pair the quantity becomes a direct measure of what the tier structure
costs a trader: the same price process, priced through very different books. That comparison
became available only once the dataset covered every materially traded tier; see
[[synthesis-pool-selection-findings]].

## Connections

- The code path: [[concept-price-impact-code]].
- The surface it transforms: [[concept-liquidity-surface]], [[concept-liquidity-profile]],
  [[concept-intrinsic-liquidity]].
- Pool mechanics behind the tick arithmetic: [[concept-uniswap-v3-ticks]],
  [[concept-bonding-curve]], [[concept-constant-product-market-maker]].
- Which pools it is computed on: [[synthesis-pool-selection-findings]].
- Anchor paper: [[source-rtw26-cfmm-liquidity-pricing-hedging]].
- Project map: [[synthesis-thesis-map]].
