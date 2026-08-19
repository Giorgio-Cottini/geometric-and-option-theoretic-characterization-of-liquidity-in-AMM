---
title: A Tick-by-Tick Solution for Concentrated Liquidity Provisioning
layer: core
type: source
origin: thesis
source_path: "articles/optimal shape/control/A Tick-by-Tick Solution for Concentrated Liquidity Provisioning.pdf"
source_kind: paper
date: 2026-08-04
---

# A Tick-by-Tick Solution for Concentrated Liquidity Provisioning

The paper poses tick-by-tick liquidity provisioning as an allocation problem over a candidate set of ticks and solves it in two forms: a maximum-revenue problem with a closed-form water-filling solution, and a maximum-return problem (net of depreciation) that is a convex optimization problem solvable with standard software. The convex formulation is the paper's main result. It reports that concentrating liquidity around the current price is usually not the best allocation.

**Authors / venue / year:** Corinne Powers (Gadget Capital); arXiv 2405.18728; 2024.

## Key points

- The setting is tick-by-tick provisioning on an AMM ([[concept-uniswap-v3-ticks]]): capital is split across a candidate set of $n$ ticks drawn from any protocol, fee tier, or network, and each tick earns fees pro rata to the reserves provisioned to it.
- Two provisioning problems are solved. Maximum revenue (fees only) has a closed-form water-filling solution. Maximum return (fees net of reserve depreciation) is the paper's central, more relevant problem and is a convex program.
- Maximum-revenue objective: maximize $\sum_{i=1}^n a_i \frac{x_i}{x_i+b_i}$ subject to $x \ge 0$, $\mathbf{1}^T x = d$, where $a_i$ is estimated fee revenue at tick $i$, $b_i$ is that tick's existing liquidity, $d$ is total capital, and $x_i$ is the reserve value allocated to tick $i$.
- Maximum-return objective: maximize $\sum_{i=1}^n \left(a_i \frac{x_i}{x_i+b_i} + c_i x_i\right)$ subject to $x \ge 0$, $\mathbf{1}^T x = d$, where $c_i$ is the expected return factor on tick $i$'s reserves ($c_i<1$ depreciation, $c_i>1$ appreciation).
- Decision variable: $x \in \mathbb{R}^n$, the capital allocation across ticks, i.e. the liquidity profile over the tick grid rather than a single range choice.
- Per-tick liquidity choice is a convex optimization problem, not a heuristic. The maximum-return problem is a concave maximization over a scaled probability simplex; substituting $-x/(x+b) = b/(x+b) - 1$ rewrites it in standard convex form as minimize $\sum_i \left(\frac{a_i b_i}{x_i+b_i} - c_i x_i - a_i\right)$ subject to $-x \preceq 0$, $\mathbf{1}^T x = d$.
- Solver class: general-purpose convex solvers, not a custom algorithm. The paper's worked example uses `cvxpy` (Python), scaling $a, b, c, d$ near 1 for numerical conditioning, and notes the global solution can be certified to a given accuracy.
- Concentrating liquidity at the current price is not shown to be optimal. The abstract states this directly: "Surprisingly, early results show that concentrating liquidity around the current price is usually not the best strategy." This cuts against the common heuristic that maximal concentration at the mid-price maximizes returns, because the optimum trades earned fees against depreciation risk tick by tick, not against a fixed shape assumption.

## Notable claims & data

- Maximum-revenue solution (water-filling): $x_i = \max\{0, \sqrt{a_i b_i}(u - \sqrt{b_i/a_i})\}$ for $i=1,\dots,n$, with $u$ set by $\sum_i \max\{0, \sqrt{a_i b_i}(u-\sqrt{b_i/a_i})\} = d$. The left-hand side is piecewise linear and increasing in $u$, so the equation has a unique solution.
- Interpretation: ticks are mounds of height $\sqrt{b_i/a_i}$ and width $\sqrt{a_i b_i}$; flooding the landscape with $d$ units of water to level $u$ gives the optimal $x_i$ as the water volume above tick $i$. Ticks with large predicted revenue $a_i$ absorb capital faster; large existing liquidity $b_i$ is a hurdle that must clear before a tick earns a smaller marginal return.
- Parameter estimation guidance: $b_i$ (current liquidity) is read directly off AMM state; $a_i$ (predicted fee revenue) is estimated from historical swap volume by tick, scaled by the tick's fee tier (typically 1, 5, 30, or 100 bps); $c_i$ (expected reserve return) is to be predicted from price volatility (development continues past the pages reviewed here).
- Standing assumptions for the derivation: provisions are held for a fixed period, no liquidity is added or removed during that period, there are no transaction costs to open/close/rebalance, and deep order books/alternative markets rule out price-manipulation risk.

## Connections

This paper works directly on the tick grid that the thesis codebase already extracts ([[concept-liquidity-pipeline-code]]), so its convex allocation problem is among the most directly reimplementable results in the corpus: given a per-tick fee estimate ($a$), current liquidity ($b$), and a reserve-return estimate ($c$), the optimal profile falls out of a solver call. It relates to [[concept-optimal-liquidity-provision]] and [[concept-optimal-range-width]] as an alternative to range-shape parameterization: instead of choosing a band width and center, it chooses a weight per tick directly, which generalizes [[concept-concentrated-liquidity]] and produces a [[concept-liquidity-profile]] as its output. It bears on the [[synthesis-optimal-liquidity-shape]] question with a concrete counter-claim to naive concentration, and its objective functions (fee accrual net of reserve depreciation) sit in the same territory as [[source-rtw26-cfmm-liquidity-pricing-hedging]]'s P&L decomposition and [[entity-uniswap-v3]]'s tick mechanics, though this paper treats provisioning as a portfolio problem across a fixed period rather than a continuous-time hedging problem.

## Open questions

- How the volatility-based estimator for $c_i$ (expected reserve return per tick) is constructed was not covered in the pages read; the paper flags this as continuing in Section 4.
- Whether the water-filling and convex-optimization solutions were validated against on-chain Uniswap V3 data, and over what volume/volatility regimes "concentration is not optimal" holds, remains to be checked in the paper's numerics beyond page 6.
- No transaction costs and no manipulation risk are assumed; how sensitive the optimal profile is to relaxing either assumption is unaddressed in the sections reviewed.
