---
title: Iv Term Structures Arbitrage
layer: core
type: source
origin: thesis
source_path: "articles/vol surface/TERM STRUCTURES OF IMPLIED VOLATILITIES - ABSENCE OF ARBITRAGE AND EXISTENCE RESULT.pdf"
source_kind: paper
date: 2026-07-19
---

# Term Structures of Implied Volatilities: Absence of Arbitrage and Existence Results

Studies market models of stochastic implied volatility in continuous time, characterizing absence of arbitrage through HJM-style drift restrictions on the forward implied volatilities and, crucially, proving existence/solvability of the resulting infinite system of SDEs for two concrete payoff families.

**Authors / venue / year:** Martin Schweizer and Johannes Wissel (ETH Zurich). Mathematical Finance, Vol. 18, No. 1 (January 2008), pp. 77-114.

## Key points
- Sets up a market model with one stock, one bank account, and a family of European options for ALL maturities T > 0 with a single fixed convex payoff function h; the stock and all implied volatilities follow Ito processes driven by a multi-dimensional Brownian motion.
- Analogizes to the Heath-Jarrow-Morton (HJM) framework for interest rates: introduces forward implied volatilities `X(t,T) = d/dT [(T-t) sigma_t^2(T)]` as the counterpart of forward rates; absence of arbitrage forces drift restrictions linking the coefficients (they cannot be specified arbitrarily).
- First main contribution: precisely characterizes absence of arbitrage (existence of a common equivalent local martingale measure for the stock and all options) in terms of a stock-volatility specification plus drift restrictions on the forward implied volatilities, expressed via the option Greeks of the payoff pricing function.
- Second (and emphasized) contribution: addresses solvability of the resulting infinite-dimensional SDE system — a genuinely nontrivial question that prior work (Schonbucher 1999, Brace et al., Ledoit et al.) left open with no examples guaranteeing solvability.
- Specializes to two payoff families and provides classes of volatility coefficients for which a unique solution exists: (i) a fixed power of the terminal stock price, and (ii) a call with a fixed strike (recovering, in more explicit form, Schonbucher's 1999 results).
- Notes that positivity of forward implied volatility X(t,T) >= 0 is necessary for absence of arbitrage (unlike interest-rate HJM, where forward-rate positivity is desirable but not required).
- Discusses market completeness/hedging in forward-implied-vol models, handling the complication that options expire and drop out of the hedging instrument set over time.

## Notable claims & data
- Model dynamics (Eq. 1.1-1.2): `dS_t/S_t = mu_t dt + sigma_t dW_t`, `d sigma_hat_t(T,K) = u_t(T,K) dt + v_t(T,K) dW_t`.
- Stock-volatility specification (Eq. 2.12) and drift restrictions (Eq. 2.13-2.14) express mu_t, sigma_t, and the forward-vol drift alpha(t,T) in terms of the pricing function's Greeks (c_Y, c_YY, c_SY) — the HJM-analogue conditions. The drift alpha is quadratic in the forward-vol volatility v.
- Theorem 2.1: characterizes when a common equivalent local martingale measure exists (parts a/b give necessary and sufficient conditions); measure given by a stochastic exponential of the market price of risk.
- Interest rates set to zero throughout; all price processes are discounted.
- Free input is the term structure of volatilities-of-volatility v(.,T); choosing v = 0 recovers the Black-Scholes model with deterministic time-dependent volatility.
- Notes independent, similar results by Jacod and Protter (2006) using a C^2 payoff and a countable family of Brownian motions plus a Poisson random measure.

## Open questions
- Restricted to a single fixed payoff/strike for all maturities (Remark 2.1); extending to a full surface with several strikes and maturities simultaneously is flagged as substantially harder and beyond the paper's scope — an open modeling frontier directly relevant to modeling a full arbitrage-free IV surface.
- Provides the arbitrage-free-dynamics theory that the purely empirical factor models (Cont-da Fonseca) lack; the two together bracket the descriptive and the no-arbitrage sides of surface dynamics.
- Connection to CFMM liquidity provision: the anchor paper (RTW26) prices impermanent loss as a European-style claim and defines implied volatilities for liquidity profiles; a term-structure-consistent, arbitrage-free model of how those liquidity-profile implied volatilities evolve would build on exactly these HJM-style drift restrictions.
