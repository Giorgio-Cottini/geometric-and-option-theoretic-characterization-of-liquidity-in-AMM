# CEV elasticity diagnostic (R1): discussion of the figures

This file discusses the two plots that `cev_elasticity_study.py` writes per pool,
`{fee}bp_{PAIR}_band-dependence.png` and `{fee}bp_{PAIR}_local-slope.png`, with the 30bp
WETH/USDC pair as the worked example. The reading generalizes to ten of the eleven pools in the
panel. The 1bp USDC/USDT pool behaves differently, for a reason stated in section 2.

## 1. Explanation

RTW26 Example 3.3 states a Constant Elasticity of Variance (CEV) price process,
`dP_t = nu P_t^beta dW_t`, and derives the liquidity profile that makes loss-versus-rebalancing
(LVR) deterministic under it: `L(q) = C / (nu^2 q^{2 beta})`. This profile is a power law, and
its exponent is exactly `-2 beta`. At `beta = 1` the profile reduces to `L(q) proportional to
q^{-2}`, the log-contract and variance-swap bonding curve.

R1 tests one question on the eleven-pool panel. Does the liquidity profile of a real Uniswap V3
pool belong to this family, over any contiguous band of price around spot? The two figures
answer that question from two angles.

The band-dependence fit measures `beta_shape = -slope/2` by ordinary least squares of `log L` on
`log q`, inside a band `|log(q/spot)| <= w`. It repeats the fit at every `w` in the grid
`{0.02, 0.05, 0.10, 0.15, 0.22, 0.35, 0.50}`. A power law has no characteristic scale, so a
profile that genuinely belongs to the CEV family returns the same `beta_shape` at every `w`. A
flat line is the null. A line that moves with `w` says that the fitted exponent depends on how
far from spot the band reaches. That means it is not a structural property of the pool.

The local-slope fit runs the same regression in a narrow rolling `+/-0.02` window, centred at
each point of `log(K/S)`. It does not commit to any band width in advance. It shows directly
where the profile peaks and how the local exponent changes on each side of that peak. Its
reference line sits at `slope = -2`, the same `beta = 1` null restated on the derivative scale,
since `beta_shape = -slope/2` makes `slope = -2` and `beta_shape = 1` the same statement.

Two conventions fix both figures. The fit always runs separately below and above spot. The
profile peaks near spot, and a single fit across that peak would measure the peak's position
rather than the shape on either side of it. And the bands are fixed log-moneyness, identical
across pools and snapshots, not quantile bands drawn from each pool's own liquidity mass. A
quantile band would erase the concentration difference between fee tiers that later research
questions in this cycle exist to measure.

The diagnostic serves two purposes at once. It decides whether the CEV family describes the
panel. That gates whether the downstream elasticity comparisons proceed at a shared band width
or report a bounded negative result instead. And its companion table, `coverage.csv`, fixes the
smallest `w` at which every pool carries enough surviving liquidity ticks to trust a fit. This is
the band width the rest of the cycle would reuse.

## 2. Comment on results

For 30bp WETH/USDC, the band-dependence fit shows neither branch is flat. The above-spot
`beta_shape` rises from 0.68 at `w = 0.02` to 2.36 at `w = 0.5`, and flattens from `w = 0.35`
onward. The below-spot `beta_shape` starts at 0.43, crosses zero near `w = 0.07`, reaches its
lowest value of -1.77 at `w = 0.22`, then partly recovers to -1.4 at `w = 0.5`. The two branches
disagree in sign across most of the grid. A CEV profile is symmetric in `log q` by construction,
so a real structural elasticity would give the same `beta_shape`, same sign, on both sides. A
sign disagreement rules out a single global power law before the flatness question is even
asked.

The local-slope figure for the same pool shows why the band fit behaves as it does. The local
derivative is positive just below spot, close to +1.0 around `log(K/S) = -0.05` to `-0.11`, and
crosses zero near `log(K/S) = -0.02`. The profile peaks about two percent below the pool's own
spot price, not at it. Above spot, the local slope falls through the `-2` reference near
`log(K/S) = 0.05` and reaches -2.85 around `log(K/S) = 0.10`. It then holds, noisily, between
-2.3 and -3.1 out to `log(K/S) = 0.5`. Below spot, past the peak, the local slope does the
opposite. It decays back toward zero and sits between -0.4 and +0.3 from `log(K/S) = -0.5` to
`-0.2`, well short of the profile's positive-side steepness.

The two figures connect because the above-spot band average stays near -2.5 to -3 for every
window beyond `log(K/S) = 0.10`. A wider `w` past that point averages over a roughly stable
region, which is exactly the flattening seen from `w = 0.35` in the band-dependence plot. The
below-spot band mixes the near-peak region, where the local slope is positive, with the far
region, where it decays toward zero. The fit averages a positive number with a near-zero number
over a widening window. That pushes the fitted below-spot `beta_shape` from positive, through
negative, and partway back, without the profile itself doing anything more complicated than
sitting on one side of an off-centre peak.

Across the rest of the panel, the two WBTC/WETH pools carry the highest full-support fit quality.
Median R-squared runs 0.83 at 30bp and 0.65 at 5bp, against 0.10 to 0.28 for the other eight
non-stablecoin pools. Their band-dependence is not flatter for it. The 30bp pool's above-spot
`beta_shape` runs from 2.58 to 5.75 across the grid and its below-spot branch runs from 1.22 to
-1.08. The 5bp pool swings further, 3.83 to 6.51 above and 0.41 to -3.87 below. A higher
full-support R-squared measures how well one line crosses the peak, not whether the exponent is
stable with scale. It is not evidence for the power-law family here.

The 1bp USDC/USDT pool is the exception. It differs because its price barely moves over the
block grid. At `w = 0.02` the median in-band mass fraction is already 0.97 to 1.0, against 0.06
to 0.15 for 30bp WETH/USDC at the same `w`. Nearly all of the pool's liquidity sits inside the
narrowest band regardless of how wide the sweep goes. `log q` carries almost no spread for the
regression to use. The fitted `beta_shape` swings from roughly -90 to +85 at the narrowest
bands, an order of magnitude beyond every other pool in the panel. This swing is an estimation
artifact of a near-frozen price series, not evidence of a steeper or more stable profile shape.

For the cycle, no half-width in the sweep grid gives every pool at least ten distinct surviving
ticks on both branches. `headline_w.csv` records an empty headline column, and 5bp WBTC/USDT
never clears the floor at any `w`. Combined with the band-dependence reading above, the panel
falls in the outcome the spec names as "no power law at any scale" for most of the panel.

## 3. Conclusion

R1 answers its own question, and the answer is no. Across the ten pools where an elasticity is
identifiable, `beta_shape` is not a scale-free property of the observed liquidity profile. It
moves with the band width used to measure it, by roughly one to six beta units depending on the
pool. The direction of that movement differs between the two sides of spot. A profile whose
fitted exponent depends on the width of the window used to fit it is not the power law RTW26
Example 3.3 predicts. That holds whatever value gets reported at any single `w`.

The direction of the disagreement between branches is itself a panel-wide result, not a property
of one pool. In every one of the ten identifiable pools, the above-spot median `beta_shape` stays
positive across the entire `w` grid. In every one of the same ten pools, the below-spot median
`beta_shape` crosses into negative territory somewhere on that grid. Liquidity thins faster above
the current price than below it, consistently across five pairs and three fee tiers. A CEV price
process assigns one elasticity to both sides of spot by construction. The panel assigns two,
opposite in sign, and that is a property of how these pools are actually provisioned, not of the
estimator.

This asymmetry changes what a fixed-`w` estimate from R2 would mean. R2 was scoped to compare a
shape-implied elasticity against a price-implied elasticity at one headline band width. R1 shows
that the shape-implied number is a band average, not a structural constant. An R2 estimate
describes the pool's behavior inside one chosen band and nothing beyond it. Whatever `w` and pool
subset GATE 1 fixes in section 9.0, that qualification has to travel with any number R2 through
R4 report. Otherwise the comparison misstates a band-dependent quantity as a structural one.

R5 asks what a liquidity provider pays for this departure, in realized LVR variability against
the LVR-neutral counterfactual. R1 shows the departure is not a marginal case that appears only
at extreme band widths. It holds at the narrowest band tested and it holds at the widest, on both
branches, for ten of eleven pools. R5 does not need `beta_shape` to be well defined, and R1 shows
that it is not. The LVR-cost question stops being a robustness check on a shape hypothesis. It
becomes the direct measure of a cost this panel's providers are already carrying.

The eleventh pool, 1bp USDC/USDT, supports neither reading. Its price series carries almost no
variation over the block grid. `log q` carries too little spread for the regression to identify a
slope. Its `beta_shape` values are a symptom of that missing variation. They are not evidence
that its profile sits closer to, or further from, the CEV family than the rest of the panel.
