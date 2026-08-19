---
title: Automated Market Makers — Mean-Variance Analysis of LPs Payoffs and Design of Pricing Functions
layer: core
type: source
origin: thesis
source_path: "articles/optimal shape/curve-design/Automated Market Makers - Mean-Variance Analysis of LPs Payoffs and Design of Pricing Functions.pdf"
source_kind: paper
date: 2026-08-04
---

# Automated Market Makers — Mean-Variance Analysis of LPs Payoffs and Design of Pricing Functions

The paper compares AMM designs from the liquidity provider's point of view using a mean-variance framework modeled on Markowitz portfolio theory, with the Hodl (buy-and-hold) strategy as the benchmark. It first recovers the classical result that a fee-free CFMM gives LPs a concave, nonpositive payoff relative to Hodl, then goes beyond CFMMs to propose an oracle-based AMM in which the pricing function is not fixed by the reserves alone but built from a markup applied around an external market price. The markup is chosen as the solution to a stochastic optimal control problem, producing an efficient frontier of risk and return for liquidity provision that is analogous to the Markowitz efficient frontier, and that stays close to optimal even when the oracle is lagged and arbitrageurs exploit adverse selection.

**Authors / venue / year:** Philippe Bergault, Louis Bertucci, David Bouba, Olivier Guéant; arXiv:2212.00336 (q-fin.TR); Digital Finance, 2022.

## Key points

- A CFMM sets its exchange rate purely from reserves via a decreasing, strictly convex level-set function ψ, with $q^0_t = \psi(q^1_t)$. Convexity of ψ rules out arbitrage inside the pool. The no-fee payoff of an LP relative to Hodl is
$$\text{PnL}_t - \text{PnL}_t^{\text{Hodl}} = \psi^*(-S_0) - \psi^*(-S_t) - (S_t-S_0)\psi^{*\prime}(-S_0) \le 0,$$
where $\psi^*$ is the Legendre-Fenchel transform of ψ, with equality only at $S_t=S_0$. This is the impermanent-loss result: price discovery in a CFMM is delegated entirely to arbitrageur liquidity takers, who extract value from LPs, so a positive fee floor is required for CFMMs to be worth providing liquidity to.
- Itô's formula splits the excess PnL into a hedgeable martingale term and a nonincreasing, nonpositive quadratic-variation term $-\tfrac12\int_0^t \psi^{*\prime\prime}(-S_s)\,d\langle S\rangle_s$, called loss-versus-rebalancing (LVR), following the decomposition used in [[source-rtw26-cfmm-liquidity-pricing-hedging]].
- The paper's alternative design does not use a static bonding curve. It builds an oracle-based AMM in which the reserves follow an exogenous mid-price $S_t$ (a GBM with drift μ and volatility σ) and the AMM's exchange rate is $S_t$ marked up (or down) by a bid/ask markup pair $(\delta^{0,1}, \delta^{1,0})$ applied to each trade of size z. The markup process is the decision variable, i.e. the object the paper "designs," playing the role that ψ plays in a CFMM.
- Liquidity-taker demand is modeled through marked point processes with logistic intensity kernels $\Lambda^{0,1}, \Lambda^{1,0}$, giving the markups a market-microstructure interpretation as the dealer's bid/ask quote construction in classical market-making models.

## Notable claims & data

- Full mean-variance objective (a stochastic optimal control problem over admissible markups $\mathcal{A}$, for a risk-aversion parameter $\gamma>0$):
$$\sup_{(\delta^{0,1},\delta^{1,0})\in\mathcal{A}} \mathbb{E}\Big[\int_0^T\Big\{\int_{z} \big(z\delta^{0,1}\Lambda^{0,1}(z,\delta^{0,1})\mathbb{1}_{\{q^1_{t-}\ge z/S_t\}} + z\delta^{1,0}\Lambda^{1,0}(z,\delta^{1,0})\mathbb{1}_{\{q^0_{t-}\ge z\}}\big)m(dz) + \mu Y^1_t - \tfrac{\gamma}{2}\sigma^2(Y^1_t)^2\Big\}dt\Big].$$
This is a genuine mean-variance objective in the sense that the quadratic term penalizes exposure of $Y^1_t$ (the LP's currency-1 position deviation from Hodl) to the Brownian variance of the excess PnL, decomposed in Eq. (1); it is not the full variance of the PnL but a tractable proxy dominated by the Brownian term.
- With no-depletion constraints dropped as superfluous for moderate μ, the problem collapses to one state variable $Y^1_t$ and is solved via a Hamilton-Jacobi-Bellman equation for a value function θ:
$$0 = \partial_t\theta(t,y) + \mu y(1+\partial_y\theta(t,y)) - \tfrac{\gamma}{2}\sigma^2 y^2 + \tfrac12\sigma^2 y^2 \partial^2_{yy}\theta(t,y) + \int_{\mathbb{R}_+^*}\Big(zH^{0,1}\big(z,\tfrac{\theta(t,y)-\theta(t,y-z)}{z}\big) + zH^{1,0}\big(z,\tfrac{\theta(t,y)-\theta(t,y+z)}{z}\big)\Big)m(dz),$$
with $\theta(T,y)=0$, where $H^{i,j}(z,p) = \sup_{\delta\ge -C}\Lambda^{i,j}(z,\delta)(\delta-p)$.
- The optimal markups are recovered from θ via the first-order conditions $\delta^{0,1*}(t,z) = \bar\delta^{0,1}(z, \tfrac{\theta(t,Y^1_{t-})-\theta(t,Y^1_{t-}-z)}{z})$ and symmetrically for $\delta^{1,0*}$, where $\bar\delta^{i,j}(z,p) = (\Lambda^{i,j})^{-1}(z,-\partial_p H^{i,j}(z,p))$.
- **No closed form.** The HJB equation is a nonlocal PIDE with 4 state variables in the unreduced problem, reduced to 1 (after dropping the no-depletion constraints and jump-drift terms) but still solved numerically: an implicit finite-difference scheme for the differential part with Neumann boundary conditions at $\pm\bar y$, coupled with a discretized measure m and a Newton-Raphson solve of the nonlocal integral term at each time step. The optimal pricing function is therefore a numerical program's output, not an analytic formula, in contrast to closed-form curve-design results.
- Numerical example: currency 0 = USD, currency 1 = ETH, $S_0=1600$, $\mu=0$, $\sigma=1\,\text{year}^{-1/2}$, transaction size fixed at 4000 USD, logistic intensities with $\lambda^{0,1}=\lambda^{1,0}=100\,\text{day}^{-1}$, $\alpha^{0,1}=\alpha^{1,0}=-1.8$, $\beta^{0,1}=\beta^{1,0}=1300\,\text{bps}^{-1}$ (about 86 trades/day at the market rate), initial inventory 2,000,000 USD and 1250 ETH, horizon $T=0.5$ day.
- The Monte-Carlo efficient frontier (1000 paths, parameterized by γ) shows CFMMs (with or without fees) and naive constant-markup strategies strictly inside the frontier, both in expected excess PnL and in standard deviation; optimized oracle-based markups trace the frontier itself.
- Under misspecification of λ or σ (e.g. simulated $\lambda=100\,\text{day}^{-1}$ vs. strategy computed with $\lambda=50\,\text{day}^{-1}$, or simulated $\sigma=1\,\text{year}^{-1/2}$ vs. strategy computed with $\sigma=1.2\,\text{year}^{-1/2}$), the misspecified strategy stays close to the true efficient frontier, shifted toward a different effective risk aversion. This follows because, absent drift and with $\lambda^{0,1}=\lambda^{1,0}=:\lambda$, the HJB solution depends only on the ratio $\lambda/(\gamma\sigma^2)$: misspecifying λ or σ is equivalent to choosing a different γ.

## Connections

This paper's decision variable is a dynamic bid/ask markup around an oracle price, not a static bonding curve $\psi(q^1)$: it belongs to the oracle-based market-making tradition rather than the constant-function or concentrated-liquidity curve family, but its method (solve a control problem to choose the shape of the exchange-rate function that liquidity takers face) makes it a computational curve-design precedent, distinct from [[concept-concentrated-liquidity]] range selection. It reuses the [[concept-convex-duality]] / Legendre-Fenchel machinery and the impermanent-loss decomposition of [[concept-lp-pnl-decomposition]] and [[concept-loss-versus-rebalancing]] from [[source-rtw26-cfmm-liquidity-pricing-hedging]], and it frames its objective in the language of [[concept-stochastic-control]] and [[concept-market-microstructure]] rather than closed-form [[concept-bonding-curve]] design. Its markup process is a specific instance of what [[concept-optimal-curve-design]] and [[synthesis-optimal-liquidity-shape]] treat as the pricing-function decision variable, complementary to the static [[concept-liquidity-profile]] approach of [[source-finding-the-right-curve]] and [[source-constant-power-root-mm]]. Adverse selection by informed arbitrageurs, handled in Section 4 of the paper, connects to [[concept-adverse-selection]] and to [[concept-intrinsic-liquidity]] as the property CFMMs lack when they rely solely on liquidity takers for price discovery. It contrasts with the fixed-curve baseline of [[entity-uniswap-v2]], which is the CPMM case recovered when the markup collapses to the constant-product spread. The paper is co-authored by [[entity-olivier-gueant]], whose dealer market-making program supplies the control formulation used here, and its optimal-stopping companion in this region is [[source-bergault-optimal-exit-time]].

## Open questions

- Whether the value function θ and the resulting markups admit any closed-form approximation in special cases (e.g. small γ or Gaussian intensity kernels) beyond the numerical scheme presented, and whether such an approximation could be mapped back onto an equivalent static bonding-curve shape for comparison with [[concept-bonding-curve]] designs.
- How the oracle-based markup framework generalizes to concentrated liquidity or multi-asset pools, where [[concept-concentrated-liquidity]] and [[concept-marginal-price-impact]] introduce additional state variables beyond the single $Y^1_t$ used here.
- Whether the efficient frontier's dependence on the ratio $\lambda/(\gamma\sigma^2)$ generalizes to asymmetric intensity kernels ($\lambda^{0,1}\ne\lambda^{1,0}$), and how robust the result is outside the zero-drift assumption.
