---
title: A Myersonian Framework for Optimal Liquidity Provision in Automated Market Makers
layer: core
type: source
origin: thesis
source_path: "articles/optimal shape/curve-design/A Myersonian Framework for Optimal Liquidity Provision in Automated Market Makers.pdf"
source_kind: paper
date: 2026-08-04
---

# A Myersonian Framework for Optimal Liquidity Provision in Automated Market Makers

The paper models an AMM liquidity provider as a monopolist auctioneer who sets a demand curve mapping price to risky-asset quantity, and who updates a Bayesian belief about the true asset price from each trader's submitted price bid. It proves that any incentive-compatible demand curve must be non-increasing and pins down its unique payment rule by a Myerson-style integral. It then generalizes Myerson's virtual-value machinery to this belief-updating setting and characterizes the profit-maximizing demand curve as a three-region step function: buy the maximum amount below a lower price, sell the maximum amount above an upper price, and refuse to trade in a middle "no-trade gap." That gap is interpreted as the AMM's bid-ask spread and is shown to arise from a combination of adverse selection and monopoly pricing.

**Authors / venue / year:** Milionis, Moallemi, Roughgarden; arXiv 2303.00208

## Key points

- **Setup.** The AMM is defined by a demand curve `g: (0,∞) → R+` (quantity of risky asset held at each price) and a payment rule `y(p̂)`. A trader reports a price bid `p̂`; the allocation is `x(p̂) = g(p0) − g(p̂)`, and the trader pays `y(p̂)`. The market maker updates its price belief from `p0` to `π(p0, p̂)` after observing the bid.
- **Incentive compatibility (Prop. 2.1).** An AMM demand curve `g(p)` can be paired with a payment rule to be incentive-compatible (truthful reporting is optimal for the trader) if and only if `g` is non-increasing, i.e. the allocation rule `x(p̂)` is non-decreasing. This is the standard Myerson monotonicity condition transplanted to AMMs.
- **Payments are pinned down (Cor. 2.2).** For an IC AMM, `y(p̂) = ∫_{p0}^{p̂} s dx(s) = −∫_{p0}^{p̂} p dg(p)`, exactly Myerson's single-parameter payment formula.
- **Objective.** The LP's expected profit is `E[Profit] = E[y(p̂) − π(p0, p̂)·x(p̂)]`, not just the payment received: the LP also marks its remaining inventory to its updated belief. This differs from classical auction revenue, which counts only the payment.
- **Virtual-value generalization (Thm. 3.1).** Expected profit equals expected virtual welfare, `E[Profit] = E[|x(p̂)|·(φ_u(p̂)·1{p̂≥p0} + φ_l(p̂)·1{p̂≤p0})]`, with virtual value functions
  `φ_u(s) = s − (1−F(s))/f(s) − π(p0,s)` and `φ_l(s) = π(p0,s) − s − F(s)/f(s)`,
  where `F, f` are the CDF/density of the trader's price-report distribution `D`. These reduce to Myerson's classical virtual values when `π` does not depend on `s`.
- **Optimal demand curve (Thm. 3.2).** The profit-maximizing allocation rule is
  `x*(p̂) = 1` for `p1 ≤ p̂ ≤ p_max`, `0` for `p2 < p̂ < p1`, `−1` for `p_min ≤ p̂ ≤ p2`,
  where `p1 ≥ p0` and `p2 ≤ p0` are roots of `φ_u` and `φ_l` respectively. The LP always buys the maximum in the lowest price interval, always sells the maximum in the highest, and refuses to trade in the middle interval, the **no-trade gap**.
- **No-trade gap = bid-ask spread.** The gap is the AMM analogue of the CLOB bid-ask spread. With neither transaction frictions nor adverse selection (pure monopoly), the gap still arises purely from the LP's monopoly position. With extreme adverse selection (all traders perfectly informed), the gap spans the entire price range.

## Notable claims & data

- Pure noise-trading, uniform `D` on `[p_min, p_max]`: closed-form thresholds `p_l = (p_min + p0)/2`, `p_h = (p0 + p_max)/2`.
- Pure noise-trading, exponential `D` with parameter `λ` on `[0,∞)`: the upper threshold is closed-form, `p_h = p0 + 1/λ`, but the lower threshold `p_l` has **no closed-form expression** and must be found numerically given `p0` and `λ`. The paper tabulates `p_l` for `λ ∈ {0.5, 1, 2}` and `p0 ∈ {0.25, ..., 2}` (e.g. `p0=1, λ=1 → p_l≈0.443`). So computing the optimal curve in general requires a numerical (root-finding) step, not a closed form, even in this simplified pure-noise special case.
- The general theory (Section 3, both informed and noise traders) states the two thresholds `p1, p2` as roots of the virtual value functions `φ_u`, `φ_l`, which is again a numerical characterization rather than a closed form in general.
- The paper states (abstract, §1.2) that the no-trade gap decomposes into an **adverse-selection component**, dominant when the degree of information asymmetry is large, and a **monopoly-pricing component**, dominant when asymmetry is small. Section 4 works out this decomposition explicitly for a linear Bayesian update rule (normally distributed prior and observation error) and gives a closed-form split between the two components; that section was outside the page range read for this note and is not reproduced here.
- Uniswap v2 (CPMM) recovered as a special case: `g(p) = c/√p`, `y(p̂) = c(√p̂ − √p0)`, matching the standard `xy=k` reserve curve with `k=c²`.

## Connections

This paper's adverse-selection cost model is close to the loss-versus-rebalancing model that this region already curates: both attribute part of the LP's cost to informed counterparties trading against a stale price. This is why [[source-myersonian-optimal-liquidity]] is the closest competitor to the thesis's own framing of LP cost, and it should be read against [[source-amm-loss-versus-rebalancing]] specifically on how each isolates the adverse-selection term from other cost sources (monopoly pricing here vs. rebalancing frictions there).

- [[concept-optimal-liquidity-provision]] — this paper is a primary source for the concept, giving the Myersonian characterization of the profit-maximizing demand curve.
- [[concept-adverse-selection]] — one of the two forces (with monopoly pricing) shown to drive the no-trade gap.
- [[concept-liquidity-profile]] — the demand curve `g(p)` / allocation rule `x(p̂)` is a liquidity profile in this region's terminology.
- [[concept-bonding-curve]] — the paper shows IC demand curves generalize CFMM bonding curves and recovers Uniswap v2 as a special case.
- [[concept-market-microstructure]] — the paper positions itself explicitly against the Glosten/Kyle market microstructure literature (§1.3).
- [[entity-jason-milionis]], [[entity-ciamac-moallemi]], [[entity-tim-roughgarden]] — authors.
- [[source-amm-loss-versus-rebalancing]] — closest competing cost model, see above.
- [[synthesis-optimal-liquidity-shape]] — this paper is a key input to the region's synthesis on optimal curve shape.

## Open questions

- What is the exact closed-form ratio between the adverse-selection and monopoly-pricing components of the no-trade gap under the linear (Gaussian) update rule of Section 4? This note covers only pages 1-12 (through Theorem 3.2); the closed-form split is stated to exist but was not read.
- How does the optimal demand curve of Theorem 3.2 map onto a discretized Uniswap v3 tick range in practice, and what is the numerical cost of the required root-finding relative to existing LP-shaping heuristics in this region?
- Does the model's risk-neutral, no-inventory-cost trader assumption change materially under the risk-averse LP framing this region also tracks (Glosten 1989, cited but rejected by the authors as unnecessarily restrictive)?
