---
title: Optimal Liquidity Shape — Research Direction
layer: core
type: synthesis
origin: thesis
date: 2026-08-04
---

# Optimal Liquidity Shape — Research Direction

The closing slide of [[source-wang-math-in-amm]], titled "Pandora's box opened", lists the
optimal or equilibrium shape of the liquidity profile as its first open problem. This page
records what that question contains, which literature attacks which part of it, and how far the
thesis can take it. The raw survey behind this page is
`research-note-optimal-liquidity-shape.md` at the region root.

The direction under consideration is a **computational** exploration of that shape. The thesis
is grounded in mathematics but its contribution is expected to be numerical and empirical, not a
new closed-form theorem.

## 1. Why the question is well-posed

Reserves, pool value, fee income and loss are all linear in the liquidity profile `L`:

```
x(P) = integral from P to infinity of  L(q) / (2 q^(3/2))  dq
y(P) = integral from 0 to P of         L(q) / (2 sqrt(q))  dq
V(P) = P x(P) + y(P)
```

Linearity is the structural fact the whole optimization rests on. Choosing where liquidity goes
is choosing the function `L`, and every downstream quantity responds linearly to that choice.
See [[concept-liquidity-profile]] and [[concept-intrinsic-liquidity]].

The objective is fixed across every setting. Fee income rises with liquidity placed where price
trades. Loss-versus-rebalancing rises with the same liquidity, as
`LVR_t = integral ell(P_s) sigma(P_s)^2 P_s^2 / 2 ds`. Concentration raises both terms at once,
so the optimum balances them. See [[concept-loss-versus-rebalancing]] and
[[concept-lp-pnl-decomposition]].

## 2. Six settings, not one problem

[[concept-optimal-liquidity-provision]] carries the full taxonomy. In short:

| Setting | Chooses | Solution object | Curated under |
|---|---|---|---|
| Stochastic control | range, timing, or `L` | HJB equation, free boundary | [[concept-stochastic-control]], [[concept-optimal-range-width]], [[concept-optimal-stopping-withdrawal]] |
| Convex duality | the bonding curve itself | Fenchel conjugate, convex program | [[concept-optimal-curve-design]], [[concept-convex-duality]] |
| Mechanism design | the demand curve | virtual value, closed-form spread | [[concept-myersonian-mechanism-design]] |
| Nash equilibrium | one provider against the rest | fixed point | [[concept-nash-equilibrium-lps]], [[concept-waterfilling-allocation]] |
| Stackelberg | leader commits, follower responds | bilevel program | [[concept-stackelberg-equilibrium]] |
| Kyle / Glosten-Milgrom | trade intensity against a maker | differential equation | [[concept-glosten-milgrom-model]] |

A single-agent optimum answers what one provider should do. An equilibrium answers which
distribution survives every provider acting that way at once. The lecture's phrase, "optimal or
equilibrium", names two different questions.

## 3. What the region now holds

Before this ingest the region held the geometric and loss vocabulary but no optimization or
equilibrium vocabulary at all. Sixteen papers were added in three batches.

**Control and range width.** [[source-cartea-predictable-loss-optimal-lp]] derives a closed-form
optimal range width and shows empirically that most providers trade far from it.
[[source-bergault-optimal-exit-time]] continues the last-passage-time withdrawal result of
[[source-rtw26-cfmm-liquidity-pricing-hedging]] with a full optimal-stopping treatment, solved
numerically two ways. [[source-powers-tick-by-tick]] and
[[source-zeller-stochastic-concentration]] pose per-tick allocation as an optimization problem
directly over the tick grid the thesis already extracts. See [[concept-predictable-loss]] and
[[concept-longstaff-schwartz]].

**Curve design.** [[source-replicating-market-makers]] and [[source-geometry-of-cfmms]] prove the
correspondence between payoffs and curves, which licenses treating shape as a design variable.
[[source-finding-the-right-curve]] turns a price belief into a curve through a convex program.
[[source-myersonian-optimal-liquidity]] characterizes the profit-maximizing demand curve and sits
closest to the region's existing cost model. [[source-bergault-gueant-mean-variance]],
[[source-constant-power-root-mm]] and [[source-axioms-for-cfmms]] supply a tractable objective, a
one-parameter curve family, and the admissible shape set. See
[[concept-cfmm-axioms]] and [[concept-constant-power-root-family]].

[[source-fukasawa-utility-indifference]] needs a correction against the survey that preceded this
ingest. The survey recorded it as the closest match to the literal words of the open problem.
Reading the paper shows its optimality claim is narrower. Its Remark 7 states that the Uniswap v3
construction is optimal in the sense that fee income distributed in proportion to each provider's
depth follows from the optimal allocation across subpools. That is allocative optimality, not
shape optimality. The paper does not claim the concentrated-liquidity range is the best choice
for a provider's risk-return objective. See [[concept-utility-indifference]].

**Equilibrium.** [[source-game-theoretic-clmm-provisioning]] reduces provider competition to a
game with a unique Nash equilibrium and fits it to real pools.
[[source-equilibrium-reward-lps]] solves a leader-follower game between the venue and a
representative provider. [[source-adaptive-curves-market-making]] derives the differential
equation an optimal adaptive curve satisfies from a microstructure model.
[[source-equilibrium-liquidity-risk-offsetting]] treats equilibrium liquidity and risk offsetting
in the same lineage as the control batch. These pages give
[[concept-lp-behavior]] and [[concept-just-in-time-liquidity]] their first equilibrium
counterparts. See [[concept-mean-field-game]].

## 4. What the thesis can actually compute

The region's advantage is an existing empirical pipeline: liquidity-profile extraction, implied
volatility fitting, and the pool measurement recorded in [[synthesis-pool-selection-findings]].
Most of the curve-design and equilibrium literature is theoretical or simulation-based. The
computational contribution therefore lies in confronting the theory with extracted profiles.

Three candidate experiments fit the pipeline as it stands:

1. **Shape comparison.** Test whether extracted Uniswap v3 profiles resemble the
   LVR-neutral profile `L(q) = C / (q^2 sigma^2(q))` of
   [[source-rtw26-cfmm-liquidity-pricing-hedging]], using the fitted volatility the pipeline
   already produces.
2. **Width comparison.** Test whether observed positions sit near the closed-form optimal width
   of [[source-cartea-predictable-loss-optimal-lp]]. See [[concept-optimal-range-width]].
3. **Equilibrium distance.** Compute the Nash profile of
   [[source-game-theoretic-clmm-provisioning]] for the measured pools and report how far the
   observed profile sits from it. See [[concept-waterfilling-allocation]].

Each is bounded, data-matched, and cites a result the region already owns. Experiment 3 is the
one that uses the vocabulary this ingest minted rather than the vocabulary that preceded it.

## 5. Assessment

The question earns a place in the thesis. It does not earn the role of primary directive in the
form the lecture states it, because that form commits to six structurally different settings at
once.

The defensible path keeps pricing and hedging for liquidity provision as the spine, described in
[[synthesis-thesis-map]], and adds one bounded computational chapter that tests a stated shape
prediction against extracted data.

Two risks stand against the direction. The field is crowded, with more than fifteen competing
papers dated 2022 through 2026, so a contribution must differ from
[[source-myersonian-optimal-liquidity]], [[source-cartea-predictable-loss-optimal-lp]] and
[[source-finding-the-right-curve]] specifically. The inherited open problems are also hard on
their own terms rather than merely unexplored, and the instructor's own group has solved only a
narrow special case.

## 6. Material not obtained

Two surveyed papers have no open preprint and are not in the region:

- Cartea and coauthors (2023), *Predictable Losses of Liquidity Provision in Constant Function
  Markets and Concentrated Liquidity Markets*, Applied Mathematical Finance. It is the companion
  to [[source-cartea-predictable-loss-optimal-lp]] and splits predictable loss into a convexity
  cost and an opportunity cost.
- Bayraktar and coauthors (2024), *DEX Specs: A Mean-Field Approach to DeFi Currency Exchanges*,
  SSRN. It is the mean-field paper calibrated to Uniswap data with a Stackelberg layer against
  just-in-time bots.

[[concept-mean-field-game]] is therefore thinner than the other equilibrium pages. Obtaining the
Bayraktar paper through the university library would close that gap.

## Related
- [[concept-optimal-liquidity-provision]] — the hub for the six settings.
- [[synthesis-thesis-map]] — the thesis argument this direction would extend.
- [[source-wang-math-in-amm]] — where the open problem is stated.
- [[source-wang-bocconi-2]] — the region's existing treatment of optimal provision as control.
