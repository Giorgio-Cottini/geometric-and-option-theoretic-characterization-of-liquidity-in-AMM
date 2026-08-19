---
title: Static Arbitrage
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# Static Arbitrage (of a Volatility Surface)

The condition that a cross-section of option prices (equivalently, an implied-volatility surface) admits no riskless profit from a static portfolio. It decomposes into two independent requirements — absence of calendar-spread arbitrage and absence of butterfly arbitrage — which together are equivalent to the existence of a non-negative martingale / non-negative risk-neutral density in every maturity slice.

## Details
- Calendar-spread arbitrage-free: total implied variance w(k, tau) = sigma_BS^2·tau is non-decreasing in maturity tau at every fixed log-strike k (variance slices do not cross).
- Butterfly arbitrage-free: each maturity slice implies a non-negative risk-neutral density; a butterfly spread cannot have negative cost. For SVI this is governed by a function g(k): the slice is butterfly-free iff g(k) >= 0 for all k and d_+(k) -> -inf as k -> inf.
- Butterfly function (SVI): g(k) = (1 - k·w'(k)/(2w(k)))^2 - (w'(k)^2/4)(1/w(k) + 1/4) + w''(k)/2; the density is p(k) = g(k)/sqrt(2·pi·w(k))·exp(-d_-(k)^2/2), so g(k) >= 0 is exactly non-negativity of the density.
- Equivalence: absence of static arbitrage across the surface ⇔ prices are consistent with a family of true martingale marginals (non-negative densities, monotone in tau) — a purely shape constraint, requiring no dynamic model.
- Raw SVI has no simple general parameter conditions precluding butterfly arbitrage (the Vogt smile is an explicit counterexample); SSVI supplies closed-form sufficient conditions instead.

## Appears in
- [[source-arbitrage-free-svi]] — decomposes static arbitrage into calendar + butterfly conditions and derives SVI/SSVI parameter constraints guaranteeing each.
- [[source-iv-term-structures-arbitrage]] — takes the no-arbitrage requirement into continuous time, characterizing it dynamically via drift restrictions rather than static slice conditions.

## Related
- [[concept-implied-volatility-surface]] — the object required to be arbitrage-free.
- [[concept-svi-parametrization]] — the parametric family whose calibration is constrained by these conditions.
- [[concept-iv-term-structure-arbitrage]] — the dynamic (HJM-style) counterpart of static no-arbitrage.
- [[entity-jim-gatheral]] — co-author of the SVI arbitrage-freeness analysis.
