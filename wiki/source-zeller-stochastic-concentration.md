---
title: Automated Market Makers — A Stochastic Optimization Approach for Profitable Liquidity Concentration
layer: core
type: source
origin: thesis
source_path: "articles/optimal shape/control/Automated Market Makers - A Stochastic Optimization Approach for Profitable Liquidity Concentration.pdf"
source_kind: paper
date: 2026-08-04
---

# Automated Market Makers — A Stochastic Optimization Approach for Profitable Liquidity Concentration

The paper formalizes the choice of a liquidity provider's (LP) provision interval width in a Uniswap-v3-style constant-product AMM as a tractable stochastic optimization problem. It models the trade-off between liquidity rewards, divergence loss, and reallocation costs, solves the resulting mixed-integer nonlinear program with sample average approximation (SAA) and Gurobi, and validates the approach on hourly on-chain data from a USDC/ETH 0.05% Uniswap v3 pool. The central finding is that, on the tested period, wide or full-range positions outperform narrow concentrated ones once reallocation costs and divergence loss are priced in correctly.

**Authors / venue / year:** Simon Caspar Zeller, Paul-Niklas Ken Kandora, Daniel Kirste, Niclas Kannengießer, Steffen Rebennack, Ali Sunyaev (Karlsruhe Institute of Technology and Technical University of Munich); arXiv 2504.16542, IEEE ICBC 2025.

## Key points

- An LP position is described by a triple $(L, \pi^l, \pi^u)$ of liquidity and lower/upper square-root price bounds. Real reserves $(x^r, y^r)$ are recovered from virtual reserves via a closed form (eq. 1) that is piecewise in whether the current square-root price $\pi$ is below, inside, or above the interval.
- The provision interval is parameterized as $[\frac{1}{\alpha}\pi, \alpha\pi]$ for a single scalar $\alpha > 1$ centered on the current price, so the optimization has one continuous decision variable per reallocation event: the relative interval width $\alpha$.
- The token price is modeled as a driftless geometric Brownian motion (GBM) with constant volatility $\sigma$ ("forecasting price trends is beyond the scope of this work").
- Reallocation is triggered whenever the price leaves the current interval ($\pi_t \notin [\pi^l_{t-1}, \pi^u_{t-1}]$), following the ULRA-style rule of Fan et al. A modified variant adds a threshold $\gamma$ that delays or hastens reallocation by a margin around the interval bound.
- Objective (eq. 2a): maximize expected terminal wealth,
  $$\mathbf{P}:\ \max_\alpha\ \mathbb{E}\big[\mathbf{Y}_T(\pi_T;\, L_{T-1},\pi^l_{T-1},\pi^u_{T-1},\Sigma^f_{T-1})\big]$$
  subject to the reallocation-trigger logic (2b), interval-update rules $\pi^l_t = z_t\cdot\frac{1}{\alpha}\pi_t + (1-z_t)\pi^l_{t-1}$ and $\pi^u_t = z_t\cdot\alpha\pi_t + (1-z_t)\pi^u_{t-1}$ (2c–2d), accrued-and-unclaimed liquidity-reward bookkeeping $\Sigma^f_t$ (2e), the real-reserve mapping $L_t$ (2f, via eq. 1), and a numerical lower bound $\alpha \geq 1+\epsilon$ (2g).
- Formulation (2a)–(2g) is a mixed-integer nonlinear program (MINLP); an equivalent, solver-ready formulation with Big-M linearization of the binary–continuous products is given in the appendix (eqs. 3a–3s) for use with commercial solvers such as Gurobi 12.
- The stochastic objective is estimated by sample average approximation (SAA): simulate $S$ GBM price paths over $T$ hourly steps, hand them to the MINLP, and solve for the terminal-wealth-maximizing $\alpha$; the problem is re-solved across random seeds for reliability.

## Notable claims & data

- Empirical setup: hourly on-chain data from the Uniswap v3 USDC/ETH 0.05% pool, 2023-01-11 to 2024-11-30, ETH price moving from about $1,350 to $3,725. Liquidity-reward rate per unit of virtual liquidity, $\overline{c^f}_t$, is estimated from `feeGrowthGlobal0X128`/`feeGrowthGlobal1X128` and held at its (robust) median value. Transaction cost per reallocation is estimated at \$109.8 (\$84.8 base cost plus \$25 to claim rewards); the AMM trading fee is $c^{tr} = 0.05\%$.
- $\alpha$ is bounded to $[1.01, 4]$: below $\approx 1.02$ the used data consistently produces $-100\%$ profit; above $\approx 1.73$ no reallocation occurs at all over the whole sample, and at $\alpha = 4$ the interval already spans $1/16\times$ to $16\times$ the initial price, so wider bounds do not change the outcome.
- Table II: across $T \in \{5,10\}$ and $S \in \{5,10,20,30\}$, the optimizer consistently selects $\alpha \approx 4$ (median 4.00 in nearly every configuration; mean 3.57–4.00), i.e. it converges to the widest allowed, effectively full-range, interval. Table III reports solve times from a few tenths of a second up to about 51 seconds (mean $\approx$ 30s at $T=10, S=30$) on a MacBook Air M1 with 8 GB RAM.
- For an LP starting with \$100,000, narrow $\alpha$ produces high liquidity rewards but net losses down to about $-100\%$, because divergence loss and frequent reallocation costs dominate; profitability turns positive only once $\alpha \gtrsim 1.11$.
- At the optimizer's chosen $\alpha \approx 4$ (no reallocation needed over the horizon), terminal profit is about 65% of the initial \$100,000 (the marked optimization result for $\gamma=0$ in Fig. 3). A hypothetical unbounded, truly full-range position would have reached about 71%, because divergence loss keeps shrinking as the interval widens further, past the paper's numerical bound of $\alpha=4$.
- Delaying reallocation with a positive threshold $\gamma$ (rather than reallocating immediately on exit) sharply reduces the number of reallocations for small $\alpha$ and materially raises profitability there, despite collecting fewer liquidity rewards; a negative $\gamma$ (reallocate slightly before the price actually exits) raises liquidity rewards for very small $\alpha$ but increases reallocation frequency and costs, which erodes profitability more than it helps.
- Since ETH price nearly tripled over the sample, the paper flags that its profitability ranking (full-range beating narrow concentration) is conditional on that appreciation; a price decline could change divergence loss enough to alter the ranking, though the *number* of reallocations is driven mainly by volatility, not price direction.
- Limitations stated by the authors: no price impact of the LP's own trades, a finite horizon $T$ (so $\alpha$ may not be optimal for an infinite-horizon problem), liquidity rewards interpolated linearly across time steps (Brownian-bridge estimation suggested as an alternative), a zero-drift GBM, and no forecasting of volatility, fees, or price trends.

## Connections

- [[concept-optimal-liquidity-provision]] — this paper is a direct computational instance of the general optimal-provision problem, cast as a scalar-$\alpha$ MINLP.
- [[concept-optimal-range-width]] — the entire optimization is over one width parameter $\alpha$; the paper's central result (optimizer converges to near-full-range) is a data point for this concept.
- [[concept-stochastic-control]] — SAA-based stochastic optimization under GBM price dynamics, with a discrete-time reallocation control ($z_t$).
- [[concept-rebalancing-strategy]] — the reallocation-trigger rule (exit-triggered, optionally $\gamma$-delayed) is a specific rebalancing policy with explicit transaction and rebalancing costs.
- [[concept-predictable-loss]] — "divergence loss" in this paper is the same phenomenon studied under predictable-loss/loss-versus-rebalancing framings elsewhere in this wiki.
- [[source-cartea-predictable-loss-optimal-lp]] — cited directly (ref. [6]) as the closed-form, continuous-reallocation counterpart this paper contrasts with discrete, cost-aware reallocation.
- [[synthesis-optimal-liquidity-shape]] — a concrete counter-data-point: on the tested Uniswap v3 pool and period, wide/full-range beats narrow concentration once reallocation costs are modeled.
- [[entity-uniswap-v3]] — the AMM design and dataset (constant-product, tick/interval-based liquidity concentration) that the model and empirical validation target.

## Open questions

- How sensitive is the "full range wins" result to the sample period's strong ETH appreciation? The authors flag but do not test a declining-price scenario.
- The paper bounds $\alpha \le 4$ for numerical tractability; would a solver with a genuinely unbounded or larger action space, or a longer horizon $T$, still select nearly-full-range, or would optimal width shrink under different volatility regimes?
- The liquidity-reward interpolation assumption ($c^f_t = \overline{c^f}_t$ constant between steps) may overestimate rewards for small $\alpha$; the suggested Brownian-bridge correction is not implemented here.
- No comparison is made against Cartea et al.'s closed-form continuous strategy or against Fan et al.'s SAA approach on the same dataset, despite both being cited as directly related.
- Runtime (up to ~51s per solve, per seed) is reported as a scaling concern; the paper defers algorithms like Nested Benders Decomposition or Stochastic Dual Dynamic Programming to future work for larger $S$ and $T$.
