---
title: Liquidity Profile
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Liquidity Profile

The distribution L(p) of liquidity across price for a CFMM — how much depth the pool offers at each price level. In a concentrated-liquidity pool it is the superposition of all active positions; the pool's reserves and value are linear functionals of this profile.

## Details
- L(p) ≥ 0 is a density over price; a full-range CPMM has L(p) = const, while concentrated pools have peaked, arbitrary profiles.
- Linearity: pool reserves x(P), y(P) and pool value V(P) are obtained by integrating simple per-price kernels against L(p), so aggregating positions is additive. This makes the profile the natural state variable for CLMM analysis.
- Adverse-selection costs are also linear in L(p): LVR and impermanent loss at price P accrue in proportion to the local liquidity there, so where an LP places liquidity determines where it bears risk and earns fees.
- Choosing L(p) is the LP's core decision; it can be tuned to replicate target payoffs (e.g. an option-like profile) via the reserve–option duality.

## Appears in
- [[source-wang-math-in-amm]] — introduces L(p) and shows reserves and value are linear in it.
- [[source-wang-bocconi-2]] — advanced lecture developing liquidity profiles and their design.
- [[source-rtw26-cfmm-liquidity-pricing-hedging]] — prices and hedges positions specified by a liquidity profile.

## Related
- [[concept-concentrated-liquidity]] — profiles arise from concentrated positions.
- [[concept-intrinsic-liquidity]] — the local, reparametrization-invariant density underlying L(p).
- [[concept-liquidity-surface]] — the liquidity profile evolving through time.
- [[concept-bonding-curve]] — profile determines the effective aggregate curve.
- [[concept-reserve-option-duality]] — profiles chosen to replicate option payoffs.
- [[concept-loss-versus-rebalancing]] — accrues linearly in the profile.
- [[concept-impermanent-loss]] — localized by the profile.
- [[concept-optimal-liquidity-provision]] — the problem of choosing this profile against a stated
  objective.
- [[concept-optimal-curve-design]] — the same choice posed at the level of the curve.

## Normalization warning

Two definitions of `L` circulate in this region under the same name, and they are not the same
object. [[source-rtw26-cfmm-liquidity-pricing-hedging]], the anchor paper, uses
`L(q) = ell(q) / (2 q^{3/2})`, derived from the curvature of the bonding curve.
[[source-finding-the-right-curve]] uses `L(p) = dY(p) / d ln(p)`, the capital deployed per unit
log price. Convert before comparing any two results that both speak of the liquidity profile. A
numerical comparison that skips the conversion will be wrong by a price-dependent factor, not by a
constant.
