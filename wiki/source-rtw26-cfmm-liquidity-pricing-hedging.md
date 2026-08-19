---
title: Rtw26 Cfmm Liquidity Pricing Hedging
layer: core
type: source
origin: thesis
source_path: "articles/vol surface/Pricing and Hedging for Liquidity Provision in Constant Function Market Making.pdf"
source_kind: paper
date: 2026-07-19
---

# Pricing and Hedging for Liquidity Provision in Constant Function Market Making

Develops a robust mathematical framework that re-coordinatizes Constant Function Market Makers (CFMMs) in terms of price and an intrinsic liquidity profile, showing that a liquidity provider's position is equivalent to a short strip of vanilla options and thereby enabling arbitrage-free pricing, hedging (Greeks), and an implied-volatility characterization of impermanent loss.

**Authors / venue / year:** Jimmy Risk, Shen-Ning Tung, and Tai-Ho Wang. Preprint arXiv:2603.01344v1 [q-fin.MF], dated March 3, 2026 (the thesis's anchor paper, "RTW26").

## Key points
- Reframes CFMMs from token-reserve coordinates to a coordinate system defined by the spot price `p` and a dimensionally-consistent, reparametrization-invariant "intrinsic liquidity" `ell`, defined via curvature of the bonding curve `f(x,y)=K`. This resolves the fact that the level constant `K` is not a consistent proxy for market depth across protocols (CPMM vs G3M/Balancer).
- Establishes a canonical parametrization (Theorem 2.2): reserves `x(p)`, `y(p)` are recovered as integrals of the liquidity profile `L(q) = ell(q)/(2 q^{3/2})` over the price spectrum. Reserves and value functions are LINEAR in the liquidity profile `L`, which is the structural backbone of the whole framework.
- The pool's mark-to-market value `V_L(p)` equals a strip of weighted covered calls; via the Carr-Madan spanning formula the LP position decomposes into an initial holding minus a continuously-weighted strip of OTM puts and calls. In a complete market this is perfectly replicable by a self-financing strategy in the underlying plus vanillas.
- Impermanent Loss (IL) is characterized as a weighted strip of vanilla option payoffs, linear in `L`; risk-neutral pricing of IL is the expectation-weighted sum of market put/call prices, and IL Greeks (Delta, Gamma, Vega) are the corresponding weighted sums of vanilla Greeks. Notably the Gamma of realized IL equals the liquidity profile density `L(P_t)` at the current price.
- Dynamic decomposition splits IL into a hedgeable "hedging cost" term (a stochastic integral, replicable by trading) plus the non-hedgeable Loss-Versus-Rebalancing (LVR), expressed via local times / occupation-time as `LVR_t = (1/2) integral L(P_s) d<P>_s`. This unifies and generalizes prior gamma-swap / variance-swap results.
- Defines a Black-Scholes (and Bachelier) implied volatility for a liquidity profile by equating the model IL price to the option-implied IL price; implied vol is homogeneous of degree zero in `L`, giving a standardized "price of liquidity." Introduces a fine structure of implied volatility over price segments for non-uniform (Uniswap v3 tick) liquidity.
- A last-passage-time valuation: because IL resets to zero whenever price revisits the LP's entry level, the optimal withdrawal is the final revisit of the entry price. Under GBM this yields transiency analysis, an optimal log-exit level, and closed-form conditions (unique interior maximizer when drift >= discount rate, else supremum attained by never withdrawing).
- Empirical validation on Uniswap v3 ETH/USDC pools (5bp and 30bp fee tiers) using Deribit ETH option quotes, confirming a volatility smile consistent with crypto-asset dynamics.

## Notable claims & data
- Local intrinsic liquidity (Eq. 1): `ell := -2 (f_x f_y)^{3/2} / (f_yy f_x^2 - 2 f_xy f_x f_y + f_xx f_y^2)`, always carrying dimension sqrt(ETH x USDC).
- Canonical parametrization (Eq. 2/4): `x(p) = integral_p^inf L(q) dq`, `y(p) = integral_0^p q L(q) dq`; slippage identity `dp = -(1/L(p)) dx`.
- Value as covered-call strip (Eq. 6): `V_L(p) = integral_0^inf min{p,q} L(q) dq`.
- IL replication (Eq. 10/11): `IL(p_T|p_0,L) = integral_0^{p_0} L(q)(q-p_T)^+ dq + integral_{p_0}^inf L(q)(p_T-q)^+ dq = integral_{p_0}^{p_T} (p_T-q) L(q) dq`.
- LVR (Eq. 15/16): `LVR_t = (1/2) integral_0^inf L_t^q(P) L(q) dq = (1/2) integral_0^t L(P_s) d<P>_s`, derived via the Tanaka formula.
- Recovers known special cases: bonding curve `x + ln y = K` gives IL equal to an entropy/gamma-swap payoff (`L(q)=1/q`); `ln x + y = K` gives a log-contract / variance-swap payoff (`L(q)=1/q^2`).
- CEV LVR-neutral profile (Example 3.3): choosing `L(q) = C/(q^2 sigma^2(q))` makes LVR deterministic and linear in time (`C t / 2`); for CEV `sigma(p)=nu p^{beta-1}` this gives explicit bonding curves parametrized by elasticity `beta`, reducing to G3M form when 1/2 < beta < 1.
- LVR can be priced as a static European claim: `E^Q[LVR_T] = E^Q[Psi(P_T)] - Psi(P_0)` where `Psi'' = L`.
- Risk-neutral IL price (Eq. 18): `Pi_t^IL = integral_0^{p_0} L(q) P_t(q,T) dq + integral_{p_0}^inf L(q) C_t(q,T) dq`, with `Pi_t^IL >= IL` by Jensen. Delta-hedge holds `Delta_t^{Pi IL}` units of the underlying.
- Empirical setup: Deribit ETH options, quarterly expiries (Dec 2025, Mar/Jun/Sep 2026), hourly snapshots; on-chain Uniswap v3 liquidity reconstructed from signed tick deltas (liquidityNet). Main results use the November 17, 2025 snapshot; `r=0` interest convention. Multi-resolution IV computed by bisection over partition bins; Black-Scholes and normalized Bachelier IV reported. Data-cleaning uses CBOE-style no-arbitrage filters and put-call parity fill-in; synthetic pricing threshold at 500 USD strike gaps; Bachelier IL integrals use 32-point Gauss-Legendre on the smooth remainder.

## Open questions
- This IS the CFMM-liquidity-provision anchor: the thesis replicates its framework, then extends it. The other five volatility-surface sources feed the extension — the implied-volatility-surface machinery (SVI arbitrage-freeness, IV surface dynamics, term-structure existence, rough/multifractal volatility) that the thesis brings to bear on the "fine structure of implied volatility" the paper defines for liquidity profiles.
- The paper defines an implied vol per liquidity profile but notes there is no simple relation between the aggregate implied vol and its fine-structure segment components — an open modeling gap.
- Leaves open how to impose realistic (arbitrage-free, possibly rough) dynamics on the liquidity-profile-implied volatility surface; connects to whether crypto-pool implied vol surfaces obey the same static-arbitrage and roughness constraints as equity index surfaces.
- Last-passage-time withdrawal is not a stopping time, complicating real-time implementation; distributional properties are characterized but practical strategy design is left open.
