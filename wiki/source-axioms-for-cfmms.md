---
title: Axioms for Constant Function Market Makers
layer: core
type: source
origin: thesis
source_path: "articles/optimal shape/curve-design/Axioms for Constant Function Market Makers.pdf"
source_kind: paper
date: 2026-08-04
---

# Axioms for Constant Function Market Makers

The paper builds an axiomatic theory of constant function market makers (CFMMs). It states a
small set of properties a trading function can satisfy (independence, scale invariance,
translation invariance, aversion to permanent loss, sufficient funds, symmetry) and proves which
combinations force which functional form. The two headline results characterize the constant
product market maker (CPMM) family used in DeFi and the logarithmic scoring rule market maker
(LMSR) used in prediction markets, both from the same independence axiom paired with a different
invariance property. The paper does not optimize a curve; it proves which curve families exist
under stated economic requirements.

**Authors / venue / year:** Jan Christoph Schlegel, Mateusz Kwaśnicki, Akaki Mamageishvili;
arXiv:2210.00048; ACM EC.

## Key points

- A CFMM is a trading function $f: \mathbb{R}_+^{\mathcal{A}} \to \mathbb{R}$ mapping an
  inventory $I$ of assets $\mathcal{A}$ to its value in a numéraire. $f$ is strictly increasing
  and continuous. A trade $r$ with $I \geq r$ moves the inventory to $I - r$ and costs
  $f(I) - f(I-r)$ units of numéraire.
- Without fees, swaps trace a **liquidity curve**: the set of inventories $I - r$ with
  $f(I-r) = f(I)$. Liquidity addition/removal scales the inventory by $\lambda \geq -1$.
- The **marginal exchange rate** between assets $A, B$ is
  $p_{A,B}(I) = (\partial f/\partial I_A) / (\partial f/\partial I_B)$, defined once $f$ is
  differentiable (**Existence of Marginal Prices** axiom).
- **Aversion to Permanent Loss**: for each $J$, the set $\{I : f(I) \geq f(J)\}$ is convex.
  Equivalently, the relative marginal price is decreasing along each liquidity curve. This is
  the axiom that forces liquidity curves to be convex.
- **Sufficient Funds**: for each $I, J$ with $f(I) = f(J)$, $I > 0 \Rightarrow J > 0$. This rules
  out concentrated liquidity: the AMM can absorb a trade of any size. Violating it, as Uniswap
  V3 does, means liquidity curves intersect the axes at finite inventory.
- **Scale invariance**: $f(I) = f(J) \Rightarrow f(\lambda I) = f(\lambda J)$ for $\lambda > 0$.
  Liquidity curves at different total liquidity levels are rescaled copies of each other. A
  stronger form, **Homogeneity in Liquidity** ($f(\lambda I) = \lambda f(I)$), makes pooled
  liquidity tokenizable and fungible, the DeFi "composability" property. Uniswap V3 and the LMSR
  both violate scale invariance.
- **Independence** (introduced descriptively in Section 1, formalized later in the paper beyond
  the read range): the terms of trade for a subset of traded assets do not depend on the
  inventory levels of assets not involved in the trade. Independence is the axiom common to both
  characterization results below. The Curve AMM violates it because it correlates prices across
  all pooled assets.
- **Translation invariance** (Section 1): a risk-less trade of the same amount of every asset
  costs the same regardless of AMM state; equivalently marginal prices in the numéraire sum to
  one. It is the natural invariance for prediction markets, where assets are Arrow-Debreu
  securities and the numéraire is external currency, as opposed to scale invariance, the natural
  invariance for DeFi, where the numéraire is the pooled LP token itself.
- **Constant Inventory Elasticity (CEMM)** family, parameterized by $\gamma \in \mathbb{R}$:
  $$f(I) = c\Big(\sum_{A} \alpha_A I_A^\gamma\Big)^{1/\gamma}, \quad \gamma \neq 0, \qquad
  f(I) = c\prod_A I_A^{\alpha_A}, \quad \gamma = 0,$$
  with $\alpha_A > 0$, $\sum_A \alpha_A = 1$. The **inventory elasticity** is $1/(1-\gamma)$: at
  the margin, a 1% change in inventory ratio changes the marginal exchange rate by
  $(1-\gamma)$%. $\gamma = 0$ is the weighted geometric mean; the symmetric case
  ($\alpha_A$ equal across assets) is the CPMM, with elasticity 1. $\gamma = 1$ is the weighted
  arithmetic mean (constant sum); $\gamma \to \infty$ is the LMSR limit ($b \to \infty$).

## Notable claims & data

- **Theorem 1**: Independence + Scale invariance $\iff$ the trading function is a CEMM, for more
  than two assets. This is the general class containing weighted geometric means, weighted
  arithmetic means, and CPMM as special cases.
- **Corollary 1**: adding Aversion to Permanent Loss to Theorem 1 forces positive elasticity
  ($\gamma < 1$); adding Sufficient Funds (non-concentrated liquidity) instead forces elasticity
  $\leq 1$ ($\gamma \geq 0$). Combined, elasticity lies in $(0, 1]$, i.e. $\gamma \in [0, 1)$: the
  span from the weighted geometric mean ($\gamma = 0$, elasticity 1) toward the weighted
  arithmetic mean, excluding it.
- **Theorem 2**: within the class of scale-invariant, independent, symmetric AMMs with
  non-concentrated liquidity, the members can be fully ranked by the curvature of their liquidity
  curves, which determines how favorable the terms of trade are to traders. The CPMM is the
  **trader-optimal** point of this class, meaning the extremal element by curvature.
- **Theorem 3**: Independence + Translation invariance $\iff$ the trading function is an LMSR
  rule or a constant sum market maker, for more than two assets.
  $$f_{LMSR}(I) = -b \log\Big(\sum_{A} e^{(c_A - I_A)/b}\Big), \quad b \neq 0.$$
- **Corollary 3**: adding convexity of liquidity curves to Theorem 3 forces the liquidity
  parameter $b$ non-negative, pinning the class down to the LMSR specifically (constant sum is
  the $b \to \infty$ limit).
- Reference trading functions collected in Section 2: weighted geometric mean
  $f_{product}(I) = \prod_A I_A^{\alpha_A}$ (Balancer); constant sum
  $f_{mean}(I) = \sum_A c_A I_A$; Uniswap V3,
  $f_{V3}(I_A, I_B) = \sqrt{(I_A+\alpha)(I_B+\beta)}$, $\alpha,\beta \geq 0$; Curve's implicit
  invariant; LMSR as above.
- For exactly two assets, Independence is trivially satisfied, so the two-asset case yields a
  strictly larger class of trading functions that cannot be fully ranked by curvature (Theorem
  4). Restricting to separable two-asset CFMMs recovers the same characterizations as the
  multi-asset case (Theorems 5, 7 and Corollaries 5, 7), plus the same optimality result for the
  CPMM (Theorem 6). Separability in two dimensions follows from an added Liquidity Additivity
  axiom for liquidity provision.

## Connections

This paper defines the feasible set that any optimization over curve shape must search within.
It proves which trading functions exist under stated economic axioms (independence, invariance,
convexity, non-concentrated liquidity, symmetry); it does not optimize anything. A computational
study of optimal liquidity shape, such as this thesis, needs exactly that feasible set: without
it, an optimizer searching over "all possible curves" has no principled boundary and cannot
distinguish an economically admissible AMM design from an arbitrary increasing function. The
CEMM family (Theorem 1, Corollary 1) is the natural parametric family — indexed by elasticity —
over which a shape optimization can be run, with the CPMM ($\gamma=0$, symmetric) and the
geometric mean market maker ($\gamma=0$, general weights) sitting at its boundary, and Theorem 2
already establishes a trader-optimality ranking by curvature inside that family, a result any
numerical optimizer should reproduce as a special case.

- [[concept-optimal-liquidity-provision]]: the axioms fix the search space this problem
  optimizes over.
- [[concept-bonding-curve]]: the trading function $f$ and its induced liquidity curve are the
  object every axiom constrains.
- [[concept-constant-function-market-maker]]: the general model this paper axiomatizes.
- [[concept-constant-product-market-maker]]: characterized as the trader-optimal, symmetric
  boundary case of the CEMM family (Theorem 2).
- [[concept-geometric-mean-market-maker]]: the $\gamma=0$ member of the CEMM family (Theorem 1,
  Corollary 1), generalizing the CPMM to asymmetric weights.
- [[concept-liquidity-profile]]: convexity (Aversion to Permanent Loss) and non-concentration
  (Sufficient Funds) are axioms directly about the shape of the liquidity curve.
- [[concept-concentrated-liquidity]]: the negation of the Sufficient Funds axiom; Uniswap V3 is
  the paper's running counterexample.
- [[concept-marginal-price-impact]]: marginal exchange rates $p_{A,B}$ and their elasticity are
  the quantities the invariance and independence axioms constrain directly.
- [[entity-balancer]]: cited as the practical instance of the weighted geometric mean trading
  function.
- [[entity-uniswap-v2]]: the CPMM's practical origin, referenced as the focal DeFi example
  throughout.
- [[synthesis-optimal-liquidity-shape]]: this source supplies the axiomatic feasible set that
  the synthesis's optimization problem is defined over.

## Open questions

- The independence axiom is only introduced descriptively within the read range (pages 1-12);
  its formal statement and the separability results it implies for more than two assets appear
  later in the paper and are not recorded here.
- The paper treats trading functions without transaction fees. How the axioms and
  characterizations change once fees are added is not addressed in the read range and matters
  for a thesis that models realistic CFMM economics.
- Corollary 1 pins elasticity to the interval $(0, 1]$, not to a single point. Whether the
  computational study needs a further axiom (or an explicit optimality criterion beyond
  Theorem 2's curvature ranking) to select a unique shape within that interval is open.
- Two-asset CFMMs (the case most relevant to pairwise liquidity pools) are not fully ranked by
  curvature (Theorem 4); the paper restricts further results to separable two-asset CFMMs. It is
  unclear whether the thesis's target pools are separable in this technical sense.
