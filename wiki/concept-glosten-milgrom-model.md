---
title: Glosten-Milgrom Model
layer: core
type: concept
origin: thesis
date: 2026-08-04
---

# Glosten-Milgrom Model

The Glosten-Milgrom model is a market-microstructure model in which a market maker sets bid and
ask prices from observed order flow while facing a mix of informed and uninformed traders. The
maker cannot tell which type it is trading against on any single order, so it prices from the
posterior belief that order flow induces, updating that belief after every trade. Prices are set
under a zero-expected-profit condition: the maker's expected loss to informed traders is offset
by its expected gain from uninformed traders, so it never prices above what the order flow
justifies, which would make it uncompetitive against rival makers.

## Details

- The adaptation to an automated market maker replaces the maker's discrete bid-ask quote with a
  demand curve. The curve gives the amount of asset held at each price and must be
  non-increasing for incentive compatibility. Traders no longer split into a fixed informed and
  uninformed pair; instead each trader observes a noisy version of the true external price, with
  the noise level parametrizing how informed, or toxic, the trader population is. This
  generalizes Glosten-Milgrom's binary split to a continuous spectrum of informedness.
- The optimal curve must satisfy a differential equation that makes the maker's belief about the
  external price, conditioned on the trade just observed, equal the price at which the curve is
  currently priced. This is the zero-expected-loss condition restated as a fixed point: the
  maker's posted price must already equal its own posterior expectation of the true price, for
  every possible trade the curve could receive next.
- The differential equation is solved in closed form under a Gaussian external-price model and
  under a lognormal external-price model. In both cases the fixed point that pins down the
  curve's operating point is exactly the estimate a Kalman filter would produce from the trade
  history: the maker runs a Kalman recursion after every trade to update its belief about the
  hidden external price, and republishes a curve derived from that updated belief. When the
  noise parameters themselves are unknown, an expectation-maximization-based adaptive Kalman
  filter estimates them from the same trade history, at a cost that grows with the length of
  that history unless it is truncated to a recent window.
- This is the market-microstructure route to optimal curve shape: the curve follows from an
  order-flow inference and a zero-expected-loss condition, not from an option-replication or
  hedging argument. It sits alongside, and is structurally distinct from, the option-pricing
  route to curve shape that this region already develops through
  [[source-rtw26-cfmm-liquidity-pricing-hedging]] and [[concept-reserve-option-duality]]; both
  routes converge on the same object, the optimal liquidity profile, from different first
  principles.
- The Kyle model is the other classical microstructure equilibrium in this family. Where
  Glosten-Milgrom prices from discrete, sequential trades and a binary or continuous
  informedness split, Kyle models a single informed trader submitting continuous order flow
  against a market maker who sets a linear price-impact schedule. Uniqueness of the equilibrium
  in Kyle's original model is a longstanding open problem: multiple equilibria are known to
  coexist under some parameter ranges, and a general uniqueness proof has not been established.

## Appears in

- [[source-adaptive-curves-market-making]] — supplies the adaptation of Glosten-Milgrom to an
  automated market maker: the differential equation the optimal demand curve must satisfy, its
  closed-form solution by Kalman filtering under Gaussian and lognormal price models, and the
  expectation-maximization-based adaptive filter for unknown noise parameters.

## Related

- [[concept-market-microstructure]] — the broader field this model belongs to; the model is one
  concrete equilibrium construction within that field.
- [[concept-adverse-selection]] — the risk the zero-expected-loss condition is built to offset:
  informed traders extract value from the maker unless the curve prices against them correctly.
- [[concept-stackelberg-equilibrium]] — a different equilibrium concept applied to liquidity
  provision, built on sequential commitment rather than on order-flow inference.
- [[concept-lp-behavior]] — describes what liquidity providers empirically do; the
  microstructure route developed here gives curve shape a theoretical account that behavior
  alone does not.
- [[concept-marginal-price-impact]] — the demand curve's slope is exactly what governs marginal
  price impact, so the differential equation derived here pins down that quantity directly.
