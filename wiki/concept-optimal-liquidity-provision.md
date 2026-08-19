---
title: Optimal Liquidity Provision
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Optimal Liquidity Provision

The problem of choosing the liquidity profile `L(p)` — how much depth a liquidity provider
places at each price level — to optimize a stated objective. Because reserves, pool value, fee
income and loss are all linear in `L`, the choice of `L` is a choice of a function, not of a
scalar. This page is the hub for the settings in which that choice is posed, and for the
distinction between a single-agent optimum and a multi-agent equilibrium.

## The objective

Every setting trades the same two quantities against each other, at every price level at once:

- **Fee income** rises with liquidity placed where price actually trades.
- **Loss-versus-rebalancing** rises with the same liquidity, as
  `LVR_t = integral ell(P_s) sigma(P_s)^2 P_s^2 / 2 ds`. See
  [[concept-loss-versus-rebalancing]].

Concentration raises both terms together. The optimum is the profile that balances them, and it
is not the profile that puts all depth at the current price. See
[[concept-lp-pnl-decomposition]] for the accounting identity the objective rests on.

## Six settings

The phrase "optimal or equilibrium shape" names six structurally different problems, not one
problem with six names.

1. **Stochastic control.** One provider picks `L`, or a range and a repositioning rule, against
   an expected-value objective. Tools are the value function, the dynamic programming principle
   and the Hamilton-Jacobi-Bellman equation. See [[concept-stochastic-control]].
2. **Convex duality and curve design.** The bonding curve itself is the design variable. Fenchel
   conjugacy maps a target payoff to a unique trading function. See [[concept-bonding-curve]].
3. **Nash equilibrium among providers.** Several providers share one fee pool, so each one's
   return depends on every other one's placement. The equilibrium profile is a fixed point.
4. **Stackelberg equilibrium.** A leader commits first and a follower best-responds. The venue
   can lead against providers, or a provider can lead against a just-in-time bot. See
   [[concept-just-in-time-liquidity]].
5. **Mean-field games.** The provider population is a continuum, so only the aggregate profile
   enters any one provider's payoff, and the aggregate must reproduce itself.
6. **Kyle and Glosten-Milgrom equilibria.** An informed trader chooses trade intensity against a
   maker who sets prices from observed order flow. This is the market-microstructure route,
   distinct from the option-pricing route. See [[concept-market-microstructure]].

## Optimum against equilibrium

A single-agent optimum answers what one provider should do. An equilibrium answers which
liquidity distribution survives every provider acting that way at once. The two answers differ,
and settings 1 and 2 above give the first while settings 3 through 6 give the second.

## The instance the thesis already holds

[[source-rtw26-cfmm-liquidity-pricing-hedging]] constructs an LVR-neutral profile
`L(q) = C / (q^2 sigma^2(q))`, chosen so that loss-versus-rebalancing becomes deterministic and
linear in time. Under a constant-elasticity-of-variance volatility model this yields an explicit
bonding curve indexed by the elasticity parameter. This is one worked instance of choosing the
shape of `L` to optimize a stated property, and it is the anchor paper's own.

## Related
- [[concept-liquidity-profile]] — the object being chosen.
- [[concept-intrinsic-liquidity]] — the reparametrization-free scale the profile generalizes.
- [[concept-concentrated-liquidity]] — the mechanism that makes a non-constant profile possible.
- [[concept-reserve-option-duality]] — why the profile is also an option-weight density.
- [[concept-lp-behavior]] — what providers do in practice, against which any optimum is measured.
- [[synthesis-optimal-liquidity-shape]] — the survey of how the six settings are attacked.
