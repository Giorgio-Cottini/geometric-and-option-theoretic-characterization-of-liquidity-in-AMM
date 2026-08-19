---
title: Constant Power Root Market Makers
layer: core
type: source
origin: thesis
source_path: "articles/optimal shape/curve-design/Constant Power Root Market Makers.pdf"
source_kind: paper
date: 2026-08-04
---

# Constant Power Root Market Makers

The paper defines a one-parameter family of [[concept-constant-function-market-maker|constant function market makers]], the constant power root market maker, and shows that constant sum, constant product, constant reserve (HODL), and constant harmonic mean are special cases of it. It derives the value function for liquidity providers, the marginal price function, the price impact function, the impermanent loss function, and the greeks for the whole family, all in closed form as functions of the single parameter. The central result is that this parameter sets a single dial between price slippage for traders and impermanent loss for liquidity providers: pushing it toward one side lowers slippage and raises loss, pushing it toward the other raises slippage and lowers loss.

**Authors / venue / year:** Wu and McTighe; arXiv 2205.07452

## Key points

- The value function for two reserves $a,b$ is $V_{\mathrm{pow}}(a,b,p) = (a^p + b^p)^{1/p}$ for a fixed constant $p \le 1$. $p$ need not be an integer. As $p \to 1$, $V_{\mathrm{pow}} \to a+b$ (constant reserve / arithmetic form). As $p \to 0$, $V_{\mathrm{pow}} \to \sqrt{ab}$ (constant product, geometric mean). As $p \to -\infty$, $V_{\mathrm{pow}} \to \min\{a,b\}$ (constant sum). The paper proves $V_{\mathrm{pow}}$ is concave, non-decreasing, non-negative, and 1-homogeneous for $p \le 1$, i.e. consistent, so it is a valid liquidity-provider payoff function.
- Taking the Fenchel conjugate of $V_{\mathrm{pow}}$ gives the trading function itself, expressed in a second parameter $q = p/(p-1)$ (self-inverse: $p = q/(q-1)$). For $n$ tokens with reserves $\mathbf{x}$, $\psi_{\mathrm{pow}}(\mathbf{x}) = 0$ if $\left(\sum_i x_i^q\right)^{1/q} \le k$, and $-\infty$ otherwise. For two tokens: $\psi_{\mathrm{pow}}(x,y) = 0$ if $(x^q+y^q)^{1/q} \le k$, else $-\infty$. This is the exact one-parameter family, with $q$ the single knob and $q \le 1$ its domain.
- Interpolation across $q$: $q=0$ recovers the constant product / geometric mean rule ([[concept-constant-product-market-maker]], [[concept-geometric-mean-market-maker]]) used by [[entity-uniswap-v2|Uniswap]] and [[entity-balancer|Balancer]]. $q=1$ recovers the constant sum (arithmetic) rule used by mStable, which has zero slippage and a fixed price ratio but no protection against full reserve depletion. $q \to -\infty$ recovers the constant reserve (HODL) rule, $\psi_{\mathrm{rsv}}$, which forbids trading away from a fixed point. $q=-1$ recovers the constant harmonic mean rule, with value function $V_{\mathrm{har}}(a,b) = (a^{1/2}+b^{1/2})^2$ (i.e. $p=1/2$); the paper notes no market maker had implemented this curve before.
- Marginal price: $M_{\mathrm{pow}}(q) = x^{q-1} y^{1-q}$ (Eq. 4). At $q=1$, $M=1$ (fixed ratio, constant sum). At $q=0$, $M = y/x$ (constant product).
- Impermanent loss for a marginal-price change $M' = \alpha M$: $I_{\mathrm{proot}}(q) = \left(\dfrac{1+M^{q/(1-q)}}{1+(\alpha M)^{q/(1-q)}}\right)^{1/q}\left(\dfrac{\alpha M + (\alpha M)^{1/(1-q)}}{\alpha M + M^{1/(1-q)}}\right) - 1$ (Eq. 5, Theorem 4.5). This reduces to the known constant-product loss $I_{\mathrm{prod}} = \frac{2\sqrt{\alpha}}{\alpha+1}-1$ as $q\to 0$, and to $I_{\mathrm{sum}}=0$ as $q\to 1$.
- Price impact (change in marginal price per unit trade size): $\dfrac{d\Delta y}{d\Delta x} = (x^q+y^q-(x-\Delta x)^q)^{(1-q)/q}\cdot(x-\Delta x)^{q-1}$ (Eq. 6). It reduces to the known constant sum and constant product price-impact functions at $q=1$ and $q=0$.

## Notable claims & data

- The abstract states the headline tradeoff directly: "as the power $q$ varies from the range of $-1$ to $1$, the power root function interpolates between the harmonic ($q=-1$), geometric ($q=0$), and arithmetic ($q=1$) means. This provides a toggle that trades off between price slippage for traders and impermanent loss for liquidity providers. As the power $q$ approaches 1, slippage is low and impermanent loss is high. As $q$ approaches $-1$, price slippage increases and impermanent loss decreases."
- Figure 3 plots impermanent loss against price change for $q \in \{-100,-10,-5,-4,-3,-2,-1,0,0.2,0.4,0.6,0.8\}$ against constant sum, constant reserve, and constant product (Uniswap) as fixed reference points; loss increases monotonically as $q$ moves from $-\infty$ toward $1$, matching prior work that flatter curvature implies higher loss.
- Value functions correspond to named production functions from economic theory: $V_{\mathrm{prod}}$ (constant product) is Cobb-Douglas, $V_{\mathrm{rsv}}$ (constant reserve) is the perfect-substitute (linear) form, $V_{\mathrm{sum}}$ (constant sum) is Leontief, and $V_{\mathrm{pow}}$ generally is the constant elasticity of substitution (CES) function, of which the other three are special cases.
- Reserve depletion: $q \le 0$ guarantees no reserve can be fully depleted, as in constant product. For $0 < q \le 1$, depletion is possible at $x=k$, the same depletion point as constant sum, though the price rises toward infinity as depletion is approached for $q$ near 0.
- Section 4.7 and Figure 6 show that for $0 < q < 1$ the relative price is better than constant product on small trades but worse on large trades (formalized for small trades only by prior work, Clipper); for $q < 0$ prices are bounded above by the constant product price, so traders always face a higher cost than constant product.

## Connections

A one-parameter curve family is the cheapest possible numerical sweep for a computational study of curve shape: the search space is one-dimensional, so a grid or line search over $q$ (or equivalently $p$) covers the entire family exhaustively at a cost linear in the number of samples, with no combinatorial blow-up from additional shape parameters. Every quantity this thesis needs from a candidate curve, marginal price, price impact, impermanent loss, greeks, is available here in closed form as a function of $q$, which removes numerical differentiation or root-finding from the sweep entirely.

The family sits directly on the axis this thesis studies: [[concept-optimal-liquidity-provision]] and [[concept-liquidity-profile]]. It is a concrete instance of a parametrized [[concept-bonding-curve]] and of the general [[concept-constant-function-market-maker]] class. Its two named endpoints are the [[concept-constant-product-market-maker]] ($q=0$) and the constant-sum rule; the geometric case is also studied on its own as [[concept-geometric-mean-market-maker]]. Its outputs feed directly into [[concept-marginal-price-impact]] and [[concept-impermanent-loss]], both derived here in closed form as functions of $q$. It complements [[source-replicating-market-makers]] (Angeris, Evans, Chitra 2021), whose value-function and trading-function duality this paper explicitly borrows and extends to a parametrized family, and [[source-geometry-of-cfmms]], which treats curve shape more generally. It is one candidate curve family for [[synthesis-optimal-liquidity-shape]] and complements the pricing and hedging framework of [[source-rtw26-cfmm-liquidity-pricing-hedging]] by supplying a tractable one-dimensional family over which that framework's quantities can be swept.

## Open questions

- The paper's own preface flags reserve depletion and round-trip arbitrage under the power root family as open issues left to follow-up research; neither is resolved in this paper.
- No trading-fee analysis is included; impermanent loss and price impact are both derived assuming zero fees, which is a gap for any comparison to live pools.
- The paper stops at two tokens for most derivations. The $n$-token trading function is given but not carried through impermanent loss, price impact, or the greeks; extending the closed forms to more than two assets is unaddressed.
- No empirical or simulated order-flow data is used; all curves are analytic and illustrated on synthetic price paths, so the tradeoff is established structurally, not against realized trading data.
