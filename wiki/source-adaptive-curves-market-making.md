---
title: Adaptive Curves for Optimally Efficient Market Making
layer: core
type: source
origin: thesis
source_path: "articles/optimal shape/equilibrium/Adaptive Curves for Optimally Efficient Market Making.pdf"
source_kind: paper
date: 2026-08-04
---

# Adaptive Curves for Optimally Efficient Market Making

Derives, from a Glosten-Milgrom market-microstructure model of a CFMM facing traders with
varying information, a differential equation that the market maker's demand curve must
satisfy to hold expected arbitrage loss to zero while staying competitive. Solves this
equation in closed form for Gaussian and lognormal external-price models using a Kalman
filter to track the hidden external price from trade history alone, extends the solution to
unknown market parameters with an EM-based adaptive Kalman filter, and shows the resulting
curves are robust to up to 50% adversarial trader manipulation. Also derives the dynamical
model implicitly assumed by static curves such as Uniswap, and shows it is optimal only in
the limit of zero inter-block time and infinite CFMM liquidity relative to the external
market.

**Authors / venue / year:** Viraj Nadkarni, Sanjeev Kulkarni, Pramod Viswanath (Princeton
University). 6th Conference on Advances in Financial Technologies (AFT 2024), LIPIcs Vol.
316, Article 1. arXiv:2406.13794.

## Key points
- Players: a market maker holding an asset/numeraire pool and a sequence of traders, one per
  discrete time step t. The market maker publishes a demand curve g_t(p) before each trade;
  g_t(p) gives the amount of asset held when the curve's operating point is at price p, and
  is constrained non-increasing for incentive compatibility. Equivalently the maker may be
  described by a canonical bonding curve phi_t(x,y).
- External price process: p_ext^{t+1} = p_ext^t + Delta p_ext^t, a discrete-time random walk
  with i.i.d. jumps parametrized by volatility sigma. The maker never observes p_ext; there
  is no price oracle.
- Trader observation: each trader sees a noisy version of the external price,
  p_trad^t = p_ext^t + Delta p_trad^t, with i.i.d. noise parametrized by eta. eta measures
  the "toxicity" (informedness) of the trader population, generalizing Glosten-Milgrom's
  binary informed/uninformed split to a continuous spectrum.
- Trade mechanics: a trader moves the operating point of the maker's curve from its prior
  value p_0^t to the observed p_trad^t, exactly as if arbitraging against a market quoting
  p_trad^t.
- Optimality objective: p^t = E[p_ext^t | H_{t-1}, p_trad^t] for all p_trad^t, where H_{t-1}
  is the history of trades and past curves. This condition makes the expected per-trade loss
  E[(p_ext^t - p^t) | H_{t-1}] vanish: the maker balances losses to informed (toxic) flow
  against gains from uninformed (noise) flow, without ever pricing above expectation (which
  would make it uncompetitive against rival market makers).
- The paper explicitly excludes price oracles: the maker must infer the hidden external
  price from trade history alone, which is the same "no oracle" posture the thesis already
  takes for curve-shape questions via [[concept-marginal-price-impact]] and
  [[concept-intrinsic-liquidity]].

## Notable claims & data
- **The core differential equation (Theorem 1).** Let x_0^t, y_0^t be the maker's asset and
  numeraire reserves at operating point p_0^t. The optimal demand curve g_t(p) obeys

  (beta_t(p) - p) g_t'(p) + beta_t'(p) g_t(p) - beta_t'(p) x_0^t = 0

  where beta_t(p_trad) = [integral_0^infty p f_eta(p_trad - p) f_t(p) dp] /
  [integral_0^infty f_eta(p_trad - p) f_t(p) dp], with f_t(p) the maker's current belief
  (pdf) about the external price and f_eta the trader-noise density. The equation is solved
  separately for p > p_0^t and p < p_0^t (a discontinuity in g_t at p_0^t is allowed), with
  boundary constraints lim g(p_0^t + delta) >= x_0^t and lim integral pdg(p) >= y_0^t as
  delta to 0-. The initial operating point itself must solve the fixed-point equation
  p = beta_t(p). After each trade the maker updates its belief by Bayes' rule,
  f_{t+1}(p) = f_eta(p_trad^t - p) f_t(p) / integral f_eta(p_trad^t - p) f_t(p) dp, closing
  the loop between curve shape and belief update.
- **Gaussian case, solved by Kalman filter (Theorem 2).** If Delta p_ext^t ~ N(0, sigma^2)
  and Delta p_trad^t ~ N(0, eta^2) with sigma, eta known, the fixed point p_0^t = beta_t(p_0^t)
  has the unique solution p_0^t = E[p_ext^t | H_{t-1}], the Kalman filter estimate. The
  differential equation then has the closed-form family of solutions
  g_t(p) = x_0^t + y_0^t/p_0^t for p <= p_0^t, and
  g_t(p) = max(0, x_tilde_0^t - C_t (p - p_0^t)^{K_t/(1-K_t)}) for p > p_0^t,
  where K_t is the Kalman gain and C_t, x_tilde_0^t are non-negative constants with
  x_tilde_0^t <= x_0^t. The simplest member of this family (x_tilde_0^t = C_t = 0) is a
  constant-sum curve y + p_0^t x = k whose slope is reset every step to the Kalman estimate
  of the external price.
- **Lognormal case (Theorem 3).** If log(p_ext^t/p_ext^{t-1}) ~ N(0, sigma^2) and
  log(p_trad^t/p_ext^t) ~ N(0, eta^2), the fixed point is
  p_0^t = exp(E[log p_ext^t | H_{t-1}] + P_{t|t} / (2(1 - K_t))), where P_{t|t} is the
  variance of the Kalman estimate of log p_ext^t and K_t the Kalman gain, with an analogous
  piecewise closed form for g_t(p) parametrized by C_t, kappa_t, x_tilde_0^t.
- **Algorithm 1** runs the Kalman recursion each step: theta_t is read off the current
  reserves as x_{t-1}^{theta_t} y_{t-1}^{1-theta_t}; the curve x^{theta_t} y^{1-theta_t} is
  published; the Kalman gain K_t = P_{t-1|t-1} + sigma^2 / (P_{t-1|t-1} + sigma^2 + eta^2)
  updates the price estimate p_ext^{t|t} = (1-K_t) p_ext^{t-1|t-1} + K_t p_trad^t and the
  uncertainty P_{t|t} = (1-K_t)(P_{t-1|t-1} + sigma^2). Per-trade cost is O(1): one Kalman
  update, independent of trade history length.
- **Unknown parameters: Adaptive Kalman Filter (Algorithm 2).** When sigma, eta are unknown,
  the maker maximizes the trade-history log-likelihood log L_t via an EM algorithm: the
  E-step runs a forward Kalman pass plus a Rauch-Tung-Striebel backward smoother to compute
  sufficient statistics A_tau, B_tau over all tau <= t; the M-step sets
  sigma* = sqrt(2 sum A_tau / t), eta* = sqrt(2 sum B_tau / t). Cost grows **linearly** with
  the number of trades t, since each new trade adds a term to both the forward and backward
  passes; the paper mitigates this by truncating to a recent window of trade history at the
  cost of losing older refinement, trading estimation quality for a bounded per-step cost
  under non-stationary sigma, eta.
- **Adversarial robustness.** With a fraction alpha < 0.5 of traders adversarially pushing
  p_trad away from p_ext, a reweighted EM assigns each past observation a learnable weight
  w_tau, with closed-form update w_tau* = eta^2 / (2 B_tau) (Eq. 27); this down-weights
  outlier trades and keeps the adaptive curve profitable (rather than lossy) against
  adversaries the static curve cannot detect.
- **Error decay versus static curves (Theorem 4).** Over a block of T trades starting from
  external price p_ext, E[(p_ext - p_KF^T)^2] = eta^2 sigma^2 / (T sigma^2 + eta^2) for the
  Kalman-filtered curve, decaying to 0 as T grows, against a constant
  E[(p_ext - p_SC^T)^2] = eta^2 for a static curve, which never improves within the block.
- **Implied dynamics of static curves (Theorem 5).** Any static curve g(p) implicitly
  assumes some beta_t(p) via (g_t(p) - x_0^t) beta_t'(p) + beta_t(p) g_t'(p) - p g_t'(p) = 0.
  For a constant-product maker (theta = 1/2), the implied beta_t(p) = sqrt(p_0^t p)
  corresponds to log p_ext^t = log p_trad^{t-1} + eps_sigma, log p_trad^t = log p_ext^t +
  eps_eta with sigma << 1 and eta = sigma sqrt(1/theta - 1). This forces near-zero inter-block
  price volatility (sigma to 0, i.e. inter-block time to 0) and requires the CFMM to hold
  more liquidity than the external market for the implied model to be consistent; static
  curves are therefore provably suboptimal outside that limit.
- Empirically (Section 7), both the Kalman-filter and adaptive Kalman-filter curves show
  much lower percentage monetary loss per trade than a static Uniswap constant-product curve
  across a swept range of volatility sigma and trader noise eta, for both Gaussian and
  lognormal price models, and the adaptive filter tracks the known-parameter Kalman filter
  closely once it converges.

## Connections
- This is the market-microstructure route to optimal curve shape: the curve is derived from
  a Glosten-Milgrom informed/uninformed trading game and a zero-expected-loss condition, not
  from an option-replication or hedging argument. It sits alongside, and is structurally
  distinct from, the option-pricing route to curve shape the thesis already develops via
  [[source-rtw26-cfmm-liquidity-pricing-hedging]] and [[concept-reserve-option-duality]];
  both routes converge on the same object, the optimal liquidity profile, from different
  first principles.
- The zero-expected-loss objective (Eq. 3-4) is a microstructure restatement of the
  no-arbitrage-loss target that [[concept-loss-versus-rebalancing]] and
  [[source-amm-loss-versus-rebalancing]] quantify for static curves against continuous
  arbitrage; this paper instead builds the curve so the loss vanishes by construction against
  discrete, partially informed order flow.
- Directly extends [[concept-adverse-selection]] and [[concept-market-microstructure]] from
  qualitative framing to a solvable optimal-curve theorem, and gives
  [[concept-optimal-liquidity-provision]] a second, non-hedging construction method.
- The implied-dynamics result (Theorem 5) reframes [[concept-constant-function-market-maker]]
  and [[concept-bonding-curve]] shape choices (constant product, constant mean) as each
  encoding a specific, usually unrealistic, assumption about price and trader-noise dynamics,
  sharpening what [[concept-liquidity-profile]] and [[concept-marginal-price-impact]] mean
  for a static curve.
- [[concept-arbitrage-with-fees]] and [[concept-intrinsic-liquidity]] are absent from this
  model: the maker holds no oracle and charges no explicit fee, so the entire adverse-
  selection cost is absorbed into curve shape rather than into a fee schedule; a thesis
  extension bridging the two routes would need to reconcile fee-based and shape-based loss
  mitigation.
- Feeds [[synthesis-optimal-liquidity-shape]] as the entry in the equilibrium batch that
  supplies a closed-form differential equation and a real-time (Kalman) numerical solution
  method, complementing the game-theoretic equilibrium of
  [[source-game-theoretic-clmm-provisioning]] and the loss quantification of
  [[source-quantifying-loss-in-amms]].

## Open questions
- The core theorem holds under a single trader per time step and a maker with no inventory
  constraints; how the differential equation changes under batched or concurrent trades
  (relevant to CFMMs receiving many trades per block) is not derived.
- The EM-based adaptive filter assumes stationary sigma, eta except via ad hoc truncation to
  a recent window; no principled rule is given for the window length, leaving open how a
  thesis implementation should tune it against realistic non-stationary crypto volatility.
- The paper's on-chain implementation (Uniswap v4 hooks plus an off-chain ML co-processor,
  Section 8) is sketched but not benchmarked for gas or latency cost, which bears on whether
  this route is computationally practical for the thesis's own numerical study.
- Robustness is proved only for adversarial fractions alpha < 0.5; behavior at or above that
  threshold, and interaction with the lognormal (Theorem 3) rather than Gaussian case, is not
  covered.
