---
title: Equilibrium Reward for Liquidity Providers in Automated Market Makers
layer: core
type: source
origin: thesis
source_path: "articles/optimal shape/equilibrium/Equilibrium Reward for Liquidity Providers in Automated Market Makers.pdf"
source_kind: paper
date: 2026-08-04
---

# Equilibrium Reward for Liquidity Providers in Automated Market Makers

The paper models the interaction between an AMM venue and its liquidity providers as a
Stackelberg stochastic game and solves for the reward contract that maximizes order flow to the
venue. The venue is the leader and chooses a contract paid to a representative liquidity
provider (LP); the LP is the follower and chooses how fast to add or remove liquidity from the
pool. The authors reduce both control problems to Hamilton-Jacobi-Bellman (HJB) equations, prove
existence and uniqueness of the LP's best response for any admissible contract, and derive
approximate closed-form solutions for the venue's optimal contract via a quadratic ansatz that
turns the HJB PDE into a matrix Riccati ODE system. They calibrate the order-arrival intensities
and volatility to Binance and Uniswap V2 ETH-USDC data and simulate the resulting equilibrium.

**Authors / venue / year:** Alif Aqsha, Philippe Bergault, Leandro Sanchez-Betancourt; arXiv
2503.22502, Mathematical Finance 2025.

## Key points

- **Players and choices.** Two agents. The venue (a constant-product AMM, CPM, with trading
  function f(x,y) = xy) is the leader; it chooses a reward contract ℜ paid to the LP, a
  random variable measurable at the terminal time T. The representative LP is the follower; it
  chooses a liquidity-provision speed process ν = (ν_t), bounded by |ν_t| ≤ ν_∞, that sets
  the rate at which it adds to or withdraws from the pool's Y-asset reserve. Both problems are
  solved by backward induction: first the LP's optimal response ν*(ℜ) is computed for a given
  contract, then the venue optimizes the contract knowing the LP will best-respond.
- **Representative agent, not a population.** The LP side is a single representative agent that
  aggregates the collective behavior of all LPs, following Fukasawa et al. (2025). Other LPs'
  activity enters the reserve dynamics only as an exogenous Brownian noise term η dB_t^ν, not as
  competing optimizers. The formulation is **not** mean-field: there is one strategic LP, not a
  distribution of interacting agents, and no fixed-point condition over an LP population appears
  anywhere in the model.
- **Market structure.** Trading happens in the CFM pool and in an external limit order book
  (LOB) venue with midprice S_t = S_0 + σW_t. Liquidity takers (LTs) arrive to the pool as two
  Poisson counting processes N^- (buys) and N^+ (sells) of fixed size ξ, with intensities that
  depend on the venue's reference price Z_t, the pool depth Y_t, and the price gap S_t - Z_t.
  Arbitrageurs are implicit in this price-gap term: they trade the pool back toward the external
  price.
- **Existence and uniqueness.** For the follower's problem, Theorem 1 proves that every
  admissible contract ℜ has a unique representation ℜ = P_T^{P_0,A} in terms of a constant
  P_0 and a predictable process A, and Theorem 2 proves existence and uniqueness of the LP's
  optimal response ν*_t = ν̄(A_t), with value function -exp(-γ P_0). This part of the
  equilibrium is proved, not assumed. The leader's problem is harder: the venue's HJB PDE
  (Proposition 1 for a risk-neutral venue, Proposition 2 for a risk-averse venue) is stated as a
  **verification theorem**, i.e. existence of a smooth solution v is assumed, not proved, for the
  exact HJB. The authors instead solve an *approximate* version obtained via a Laurent-series
  expansion in ξ/Y (trade size small relative to pool depth) and a quadratic ansatz for the value
  function. For the risk-averse venue this ansatz reduces the PDE to a 3x3 matrix Riccati
  equation, a linear ODE, and a scalar ODE; existence of a solution to that Riccati equation on
  (-∞, T] is proved (via Theorem 3.6.6 of Abou-Kandil et al. 2012, using that a matrix Θ + Θ^T
  built from the coefficients is negative semi-definite). So uniqueness/existence is rigorous for
  the follower and for the reduced (approximate) leader problem, but not for the full leader HJB.
- **Algorithm.** The equilibrium is not computed by a PDE grid solve. The quadratic ansatz
  v(t,Z,Y,S) = g_11 + 2η^T G_1(t) + η^T G_2(t) η, with η = (Z, Y, S)^T, turns the 4-dimensional
  HJB PDE into a finite ODE system: a 3x3 matrix Riccati equation for G_2(t) (terminal condition
  G_2(T) = 0), a linear ODE for G_1(t) given G_2, and a scalar ODE for g_11(t). This system is
  cheap to integrate backward in time with standard ODE methods; the cost is that of a
  low-dimensional Riccati integration, not a multi-dimensional PDE solve. The risk-neutral venue
  case is solved similarly with a polynomial ansatz ĥ(t,Z,Y,S) = h_0 + h_1 Z + h_2 S + h_3 Z^2 +
  h_4 ZS + h_5 S^2 whose coefficients solve a linear ODE system.
- **Calibration to real data.** The order-arrival intensity model λ^±(Z,Y,S) = max{a_0, a_1 +
  a_2 Y ± a_3(S-Z)} is calibrated by linear regression on Binance and Uniswap V2 ETH-USDC data
  (1 Jan 2022 to 30 Apr 2022), bucketed in 10-minute windows, giving â_1 = 142.7 and â_3 = 13.6
  (â_2 set to 0 for tractability in this calibration). The same data validates that the model's
  positivity assumption on λ^± holds in 99.63% of the 17,131 observed buckets. The numerical
  section then simulates the equilibrium with S_0 = Z_0 = 2820 (ETH-USDC), daily volatility
  σ = 0.0569 × S_0, average trade size ξ = 300, venue fee 𝔯 = 0.01 × ξ × Z_0, initial pool
  position Y_0 = 50,000 ETH, and stress-tests the external price-impact parameter 𝔞.

## Notable claims & data

- Trading function and level function: f(x,y) = xy (constant product market, CPM), with level
  function φ_c(y) = c/y, so the pool reserves trade off along a hyperbola of constant product
  c_t = X_{t-} Y_{t-}.
- Order-arrival intensity model: λ^±(Z,Y,S) = max{a_0, a_1 + a_2 Y ± a_3(S-Z)}, a_0 > 0,
  a_1, a_2, a_3 ≥ 0. a_2 is the coefficient linking pool depth Y to LT order flow: a_2 = 0 means
  higher liquidity does not attract more trading, and in that case the LP has no incentive to add
  liquidity in equilibrium.
- LP's objective: V_t(ℜ) = sup_{ν ∈ A} E_t^ν[-exp{-γ(ℜ + Q_{t,T}^ν)}], a CARA (exponential)
  utility over reward plus trading P&L Q, where Q accrues mark-to-market gains, financing costs
  of adding/removing X and Y, and a quadratic price-impact cost 𝔞 ν_t^2 for trading in the
  external LOB.
- Venue's objective: E^{ν*(ℜ)}[-exp{-ζ(𝔯(N_T^- + N_T^+) - ℜ)}], maximized over contracts ℜ
  subject to the LP's participation constraint V_0(ℜ) ≥ R (R < 0 is the LP's reservation
  utility level), where 𝔯 is the per-trade fee the venue collects.
- Low-noise, risk-neutral limit (Remark 2): as the LP's liquidity-provision noise η → 0, the
  optimal speed converges to ν̂*_t → a_2 𝔯 (T-t) / 𝔞. Liquidity provision is proportional to
  the fee 𝔯 and to a_2 (how much depth attracts order flow), and inversely proportional to the
  external price-impact cost 𝔞. If a_2 = 0, ν̂*_t = 0: the LP never adds or removes liquidity.
- Calibrated values: â_1 = 142.7, â_3 = 13.6; σ = 0.0569 × S_0; ξ = 300; 𝔯 = 0.01 × ξ × Z_0;
  Y_0 = 50,000 ETH; η = 10^-10 ETH; LP risk aversion γ = 10^-18; venue risk aversion ζ = 10^-6;
  baseline external price impact 𝔞 = 10^-14.
- Simulation result: at the baseline 𝔞 = 10^-14 the LP's optimal strategy ν_t* is roughly
  centered on zero with volatility-driven oscillation (Figure 4-5); raising 𝔞 to 10^-13 or
  10^-12 collapses the cumulative liquidity change toward zero (Figure 6), showing that the
  LP's ability to respond to the contract is bounded by external trading costs.

## Connections

This paper is a computational, closed-form-via-approximation companion to
[[concept-optimal-liquidity-provision]]: instead of solving for an LP's optimal static or
dynamic liquidity profile taking fees and volatility as given, it solves for the *contract* a
venue should offer so that a [[concept-lp-behavior|self-interested LP]] chooses to supply
liquidity at all. The follower's control problem is a standard [[concept-stochastic-control]]
problem (CARA utility, HJB equation, verification theorem), reduced here by ansatz and
Laurent-series approximation to a solvable Riccati system rather than solved by numerical PDE
methods. The order-arrival intensity model, arbitrageur alignment of pool and external prices,
and LT/LP separation place the paper squarely in [[concept-market-microstructure]] rather than
pure AMM curve design. It belongs with [[synthesis-optimal-liquidity-shape]] and with
[[source-game-theoretic-clmm-provisioning]] as one of the few papers that treats LP liquidity
choice as a strategic, game-theoretic object rather than a static or exogenously-driven policy;
unlike that paper's provider-vs-provider game, this one is a single representative LP responding
to a venue-designed contract. It contrasts with [[source-rtw26-cfmm-liquidity-pricing-hedging]],
which prices and hedges a given liquidity position rather than deriving the equilibrium contract
that induces it, and it is consistent in spirit with the predictable-loss framing of
[[source-cartea-predictable-loss-optimal-lp]], since both treat LP compensation as something
that must be structured against a well-understood loss profile rather than assumed away.

## Open questions

- The pool is a plain constant-product market (Uniswap V2 style); the paper does not extend the
  equilibrium contract to concentrated liquidity (Uniswap V3/V4-style) pools, where the LP also
  chooses a price range.
- The representative-agent formulation leaves open how the equilibrium contract would change
  under a population of heterogeneous LPs with a genuine mean-field coupling, rather than one
  aggregate follower.
- Existence and uniqueness of a classical solution to the venue's *exact* HJB equation (not the
  Laurent-series-approximated, ansatz-reduced version) is left as an assumption via the
  verification theorems (Propositions 1 and 2), not proved.
- The calibration sets a_2 = 0 for the intensity regression, which by the paper's own Remark 2
  implies zero equilibrium liquidity provision; the paper does not calibrate a_2 itself from
  data, so the regime in which the contract actually incentivizes liquidity provision is
  illustrated only via parameter stress tests, not fitted to observed venue behavior.
- No comparison is made against actual observed Uniswap V2/V3 LP reward or fee-tier design, so
  it is unclear how close real venues are to this equilibrium contract.
