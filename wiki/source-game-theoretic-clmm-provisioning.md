---
title: Game Theoretic Liquidity Provisioning in Concentrated Liquidity Market Makers
layer: core
type: source
origin: thesis
source_path: "articles/optimal shape/equilibrium/Game Theoretic Liquidity Provisioning in Concentrated Liquidity Market Makers.pdf"
source_kind: paper
date: 2026-08-04
---

# Game Theoretic Liquidity Provisioning in Concentrated Liquidity Market Makers

Models liquidity provision in a concentrated-liquidity market maker (CLMM) as a one-shot
non-cooperative game among budget-constrained LPs, proves a unique Nash equilibrium in a
reduced form of the game, characterizes it as a waterfilling allocation, and compares it
against real LP behavior on five Uniswap v3 pools.

**Authors / venue / year:** Weizhao Tang, Rachid El-Azouzi, Cheng Han Lee, Ethan Chan,
Giulia Fanti (Carnegie Mellon University; Avignon University; Allium). Proc. ACM Meas.
Anal. Comput. Syst., Vol. 9, No. 1, Article 7, March 2025. arXiv:2411.10399.

## Key points
- Players: N LPs indexed by n. Each LP n chooses a liquidity vector L_n = (L_{n,(a,b)}) over
  general price ranges (a,b), subject to a dollar budget constraint
  sum_{(a,b)} L_{n,(a,b)} * eps_{a,b}(q) <= B_n, where eps_{a,b}(q) is the dollar price of a
  unit of liquidity over range (a,b) at pool price q.
- Payoff: utility U_n = fee reward F_n minus expected impermanent loss C_n. Fee reward uses
  a tunable exponent alpha > 0: F_n = sum_m f_m * K_{n,m}^alpha / sum_i K_{i,m}^alpha, where
  K_{n,m} is LP n's active liquidity on atomic price range m and f_m is that range's average
  fee pool. alpha = 1 matches Uniswap v3's proportional sharing; alpha to infinity gives
  winner-take-all; alpha = 0 gives equal sharing regardless of size.
- Equilibrium concept: Nash equilibrium of a static (one-shot) normal-form game, re-derived
  daily since the paper treats each day as an independent instance (justified empirically:
  most real LPs update daily or less often).
- Existence and uniqueness: existence of at least one Nash equilibrium holds in the original
  game (arbitrary price ranges) but uniqueness fails there. The paper introduces an
  **atomic game** in which each LP chooses active liquidity K_n per atomic (single-tick-pair)
  range instead of per general range, cutting the action space from quadratic in the number
  of ticks to linear. For 0 < alpha <= 1 the atomic game has a unique Nash equilibrium
  (diagonal strict concavity, Rosen 1965). A twin-games theorem shows the atomic equilibrium
  and the (non-unique) original-game equilibria always agree on the induced atomic-liquidity
  histogram, so the atomic game recovers everything of interest about the original game.
- Algorithm: the unique atomic equilibrium is computed by Rosen's relaxation algorithm; the
  paper also notes mirror-descent and no-regret learning converge to it under repeated play.
  No closed form is given.
- Equilibrium shape: **waterfilling**. At equilibrium there is, per atomic range, a common
  water level h_m; LPs with enough budget all invest up to h_m on every range, while
  budget-constrained ("poor") LPs exhaust their entire budget and invest less. Richer LPs
  (higher B_n) invest at least as much as poorer LPs on every range (budget dominance,
  Prop. 3.9), and for 0 < alpha < 1 every LP holds strictly positive liquidity on every range
  (Prop. 3.10).
- Calibration to Uniswap v3: five pools on Ethereum, Jan-Jun 2024 Mint/Burn history plus
  Jan-Jun 2024 Swap history — B30 (WBTC/USDC, 0.3%), E100 (USDC/WETH, 1%), E30 (USDC/WETH,
  0.3%), E5 (USDC/WETH, 0.05%), T5 (USDC/USDT, 0.05%, the only stable pool). LPs are
  filtered to "player" LPs (positions lasting a full day, among the top-30 by investment,
  covering >=99% of daily investment) versus non-player LPs.

## Notable claims & data
- Nash equilibrium definition (3.1): Z* is a Nash equilibrium iff U_n(Z*_n; Z*_{-n}) >=
  U_n(Z_n; Z*_{-n}) for all feasible Z_n and all n.
- Atomic-game utility: U_n^A = sum_m f_m * K_{n,m}^alpha / (sum_i K_{i,m}^alpha) - sum_m
  tau_m * K_{n,m}, with tau_m the expected impermanent-loss rate on atomic range m.
- Waterfilling (Prop. 3.8): for alpha in (0,1], for each atomic range m there exists h_m > 0
  such that every LP with unspent budget sets K_{n,m} = h_m, and every fully-spent LP sets
  K_{n,m} <= h_m; total spend A_n = min{h, B_n} for some common h.
- Finding 1: in the stable pool T5, real LPs' actions overlap the Nash equilibrium with
  40.4% median / 34.5% mean similarity (an overlap metric in [0,1] built from per-range
  dollar-liquidity total variation distance). In the four risky pools, the 75th-percentile
  overlap is below 9%.
- Finding 2: the naive "repeat yesterday" heuristic (YDay) matches real LP action with over
  99.5% overlap in mean and at the 25th percentile — most LPs barely update their positions
  day to day.
- Finding 3: an "inert" Nash equilibrium computed from a 7-day rolling window of historical
  parameters (I_NE) overlaps ground truth at least 28% more than either the true (same-day)
  equilibrium NE or a 1-day "reactive" equilibrium R_NE, in every risky pool. In the stable
  pool T5, the true NE has the highest overlap with ground truth, around 40%.
- Finding 4: in risky pools, switching to the I_NE strategy would raise real LPs' median
  daily utility by up to $116 (average daily utility by $222) and median daily ROI by
  0.009%. Moving all the way to the true daily Nash equilibrium would raise median ROI by
  0.855% and net daily profit by $13,352. In the stable pool T5, I_NE and R_NE utility is
  *lower* than ground truth: real LPs there are already close to optimal.
- Impermanent loss rate: tau_hat = eps_{a,b}(q) * [q'(Delta x - Delta x') + (Delta y - Delta
  y')] / (q Delta x + Delta y), non-negative by construction (Def. 2.2, Eq. 2.5).

## Connections
- Positions the thesis's [[concept-optimal-liquidity-provision]] "setting 3" (Nash
  equilibrium among providers) with a concrete, provably unique, computable instance; see
  [[concept-nash-equilibrium-lps]] and [[concept-waterfilling-allocation]], both minted from
  this paper.
- The utility split F_n - C_n mirrors the fee-minus-loss accounting already established by
  [[concept-lp-pnl-decomposition]] and [[source-amm-loss-versus-rebalancing]], but here the
  loss term is impermanent loss per Def. 2.2, not LVR; see [[concept-loss-versus-rebalancing]]
  and [[concept-impermanent-loss]] for the distinction the thesis already tracks.
- The empirical split between a small overlap in risky pools and near-Nash behavior in a
  stable pool sharpens [[concept-lp-behavior]]'s sophisticated-vs-retail divide: it shows the
  gap is not fixed but shrinks toward zero exactly where price risk (and hence the value of
  active management) is lowest.
- [[concept-just-in-time-liquidity]] is the extreme case of the "very few positions, narrow
  range, high-frequency update" behavior this paper's Nash equilibrium recommends but which
  most real LPs (per Finding 2) do not execute.
- Feeds [[synthesis-optimal-liquidity-shape]] as the paper with the sharpest existence/
  uniqueness/algorithm/calibration profile in the equilibrium batch.

## Open questions
- Uniqueness is proved only for 0 < alpha <= 1; behavior for alpha > 1 (which the paper notes
  sharpens competition toward winner-take-all) is left open.
- The model treats each day as an independent one-shot game; it does not model a dynamic
  game with carryover state, nor JIT LPs that act within a block.
- The paper does not give a closed form for the equilibrium liquidity levels h_m; it is
  computed numerically (relaxation algorithm), which bears on what a thesis reimplementation
  would need to budget computationally.
- Real LPs in risky pools sit far from the Nash equilibrium under same-day information but
  much closer under 7-day-stale information — an open question the paper poses for future
  work is how to design LP-side heuristics between these two extremes.
