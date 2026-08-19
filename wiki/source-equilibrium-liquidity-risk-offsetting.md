---
title: Equilibrium Liquidity and Risk Offsetting in Decentralised Markets
layer: core
type: source
origin: thesis
source_path: "articles/optimal shape/equilibrium/Equilibrium Liquidity and Risk Offsetting in Decentralised Markets.pdf"
source_kind: paper
date: 2026-08-04
---

# Equilibrium Liquidity and Risk Offsetting in Decentralised Markets

The paper builds a structural model of DEX liquidity provision in which market outcomes are endogenous rather than assumed. A representative liquidity provider (LP) chooses how much liquidity to deposit and how to hedge the resulting inventory risk in a centralised exchange (CEX), price-sensitive noise traders choose trade sizes against the pool, and arbitrageurs keep the DEX price aligned with the fundamental. The model is solved by backward induction across three stages and yields existence of equilibrium liquidity for general convex trading functions, with closed-form results for constant-product markets such as Uniswap.

**Authors / venue / year:** Cartea, Drissi and coauthors; arXiv 2512.19838, December 2025.

## Key points

- Three agent types, three stages, solved backward: stage three (noise LTs pick trade size given liquidity depth κ), stage two (LP picks a dynamic CEX trading strategy given κ), stage one (LP picks κ anticipating stages two and three).
- The LP is a monopolist supplier of liquidity, not one of several competing LPs. There is no strategic interaction among LPs in this model, so "equilibrium" here means a rational-expectations fixed point across the three stages under arbitrageur price alignment, not a Nash equilibrium among liquidity providers.
- Liquidity depth κ is the DEX risk-management instrument, on par with dynamic hedging. Deeper κ lowers execution costs for traders and raises fee revenue, but it also enlarges the LP's inventory exposure and loss-versus-rebalancing (LVR).
- Risk offsetting is costly dynamic replication in the CEX, not frictionless hedging. The LP trades a CEX position \(Q_t\) against the DEX reserve \(Y_t\); perfect offsetting requires \(Q_t = -Y_t\), but convex CEX trading costs make full replication suboptimal.
- The intensity of replication is governed by the ratio of risk aversion to trading costs: higher risk aversion pushes toward full offsetting, higher trading costs push away from it. For a fixed ratio, higher absolute levels of both parameters shrink the optimal liquidity supply.
- Private information about the price drift adds a speculative component to the CEX strategy and has a non-monotonic effect on equilibrium liquidity: it raises liquidity for moderate anticipated price moves (speculative benefit dominates) and lowers it for large ones (anticipated adverse selection and replication costs dominate).
- Existence of equilibrium DEX liquidity in stage one is established for general convex trading functions. Closed-form expressions are derived for constant-product markets, decomposing equilibrium liquidity into a component balancing fee revenue, adverse selection, and price risk, and a speculative component driven by private information.

## Notable claims & data

- DEX reserves satisfy the iso-liquidity condition \(f(X_t,Y_t)=\kappa^2\); reserves in the reference asset are \(X_t=\varphi(Y_t,\kappa)\) via the level function \(\varphi\), and the marginal price is \(-\partial_1\varphi(Y_t,\kappa)\).
- Trading-cost decomposition of DEX wealth (Itô):
  \[
  d(X_t+Y_tF_t) = Y_t\,dF_t - \tfrac{1}{2}\,\partial_{11}\varphi(h(F_t,\kappa),\kappa)\,(\partial_1 h(F_t,\kappa))^2\,d[F]_t,
  \]
  where the first term is exposure to fundamental price moves and the second is the LVR term, the predictable adverse-selection cost from the convexity of the pricing curve.
- Noise-LT optimal trade size: \(\delta_t^\star = F_t\,\dfrac{|V|-\pi}{\partial_{11}\varphi(Y_t,\kappa)}\), where \(V\) is symmetric private utility on \([-1,1]\) with \(|V|\) supported on \([\pi,1]\) and π is the proportional DEX fee.
- Expected fee revenue anticipated by the LP in stage one:
  \[
  \mathbb{E}\!\left[\int_0^T \pi\,\delta_t^\star F_t\,dN_t\right] = \lambda\pi(v-\pi)\,\mathbb{E}\!\left[\int_0^T \frac{F_t^2}{\partial_{11}\varphi(h(F_t,\kappa),\kappa)}\,dt\right],
  \]
  with Poisson arrival intensity λ and \(v=\mathbb{E}[|V|]\).
- Fundamental price follows \(dF_t = A_tF_t\,dt + \sigma F_t\,dW_t\), with \(A_t\) the LP's private signal about drift; results are stated to be agnostic to the information structure of \(A_t\) (fully observable, partially observable, or latent).
- The LP's optimal replication problem in the CEX reduces, via variational tools, to a coupled forward-backward SDE system with a closed-form representation under general convex trading functions and stochastic price signals. Under sufficiently large CEX price impact, the optimal replication strategy instead solves a differential Riccati equation (DRE) whose solution is shown to exist, be unique, and be computable efficiently.
- Two limiting cases for equilibrium liquidity under risk aversion: as risk aversion relative to trading costs grows large, the CEX strategy approaches perfect replication and DEX liquidity falls to the lowest level consistent with nonnegative expected returns; under risk neutrality, the LP allocates its full budget to liquidity provision whenever expected fee revenue exceeds expected adverse-selection cost, otherwise the DEX collapses.
- Pages read (1-12 of the PDF) cover the introduction, the general DEX mechanics, and stages one and two of the model (fee revenue and risk offsetting); no calibration to real decentralised-market data appears in this range, and no numerical results are reported yet. The constant-product closed-form equilibrium and numerical experiments are described as living in Section 6, past the reviewed pages.

## Connections

This paper shares its author lineage with [[source-cartea-predictable-loss-optimal-lp]] but answers a different question: that paper solves a single LP's optimal control problem under predictable loss, while this paper embeds that kind of control problem inside a three-stage structural model to determine the equilibrium level of liquidity itself, jointly with trading volumes and fee revenue. It builds directly on [[concept-loss-versus-rebalancing]] as the adverse-selection channel and treats [[concept-optimal-range-width]] questions as downstream of the liquidity-depth choice κ rather than as the primary object. The LVR-driven trade-off between fee revenue and adverse selection connects to [[concept-adverse-selection]] and [[concept-market-microstructure]]; the LP's CEX hedge is a [[concept-stochastic-control]] problem analogous to [[concept-rebalancing-strategy]]; and the constant-product closed-form results in the unread later sections apply directly to [[entity-uniswap-v3]]. The paper's framing of κ as risk-management instrument bears on [[concept-optimal-liquidity-provision]] and on the broader question tracked in [[synthesis-optimal-liquidity-shape]].

## Open questions

- Is the equilibrium of stage one unique for general trading functions, or only shown to exist? The introduction states existence but does not, in the pages read, claim uniqueness outside the constant-product case.
- How does this single-LP structural equilibrium relate to genuine multi-LP strategic settings, such as [[concept-nash-equilibrium-lps]] or [[source-game-theoretic-clmm-provisioning]], where LPs compete over the same pool?
- What functional form does the closed-form constant-product decomposition take, and does it map onto a [[concept-waterfilling-allocation]] or a [[concept-liquidity-profile]] shape once Section 6 is read?
- Is there empirical calibration to real DEX data later in the paper, and if so, does it validate the fee-revenue and LVR formulas against observed Uniswap pools, connecting to [[source-rtw26-cfmm-liquidity-pricing-hedging]]?
- How does the transient-impact extension (Appendix B, DRE-based) change the equilibrium liquidity result relative to the frictionless-impact base case?
