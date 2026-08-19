---
title: Iv Term Structure Arbitrage
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# IV Term-Structure Arbitrage (HJM-Style Drift Restrictions)

The continuous-time, dynamic counterpart of static no-arbitrage for implied volatilities: modeling implied vols across all maturities as Ito processes and requiring the absence of arbitrage forces HJM-style drift restrictions linking their coefficients. The construction is built on forward implied volatilities, the maturity-derivative analogue of forward interest rates.

## Details
- Market model: one stock, one bank account, and European options for all maturities T > 0 with a fixed convex payoff h; the stock and every implied volatility follow Ito processes driven by a common multi-dimensional Brownian motion.
- Dynamics: dS_t/S_t = mu_t dt + sigma_t dW_t and d·sigma_hat_t(T, K) = u_t(T, K) dt + v_t(T, K) dW_t.
- Forward implied volatility: X(t, T) = d/dT [(T - t)·sigma_t^2(T)], the analogue of the instantaneous forward rate; its positivity X(t, T) >= 0 is necessary for absence of arbitrage (unlike interest-rate HJM, where forward-rate positivity is only desirable).
- Absence of arbitrage ⇔ existence of a common equivalent local martingale measure for the stock and all options; this is equivalent to a stock-volatility specification plus drift restrictions expressing mu, sigma, and the forward-vol drift in terms of the pricing function's Greeks (the drift is quadratic in the forward-vol volatility v). The free input is the term structure of vol-of-vol v(·, T); v = 0 recovers Black–Scholes with deterministic time-dependent volatility.
- The hard part is solvability: the no-arbitrage conditions yield an infinite-dimensional system of SDEs, and existence of solutions is proved only for specific payoff families (a fixed power of terminal price; a call with fixed strike).

## Appears in
- [[source-iv-term-structures-arbitrage]] — sets up the market model of stochastic implied volatility, derives the HJM-style drift restrictions on forward implied volatilities, and proves existence for two concrete payoff families.

## Related
- [[concept-static-arbitrage]] — the static (single-date) no-arbitrage conditions this dynamic theory generalizes.
- [[concept-implied-volatility-surface]] — the object whose arbitrage-free evolution is characterized.
- [[concept-volatility-surface-dynamics]] — the empirical, statistical description of surface motion that this no-arbitrage theory complements.
- [[concept-svi-parametrization]] — a static cross-sectional fit that these term-structure models could equip with arbitrage-free dynamics.
- [[concept-stochastic-control]] — the SDE/martingale-measure machinery underlying the framework.
