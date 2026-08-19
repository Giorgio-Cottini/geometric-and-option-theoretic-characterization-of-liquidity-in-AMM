---
title: The Geometry of Constant Function Market Makers
layer: core
type: source
origin: thesis
date: 2026-08-04
source_path: "articles/optimal shape/curve-design/The Geometry of Constant Function Market Makers.pdf"
source_kind: paper
---

# The Geometry of Constant Function Market Makers

This paper rebuilds CFMM theory on a minimal geometric axiom set, the reachable set of reserves,
instead of an assumed analytic trading function. Dropping differentiability and homogeneity as
requirements, the authors show that every CFMM still has a unique canonical trading function
that is nondecreasing, concave, and homogeneous, and give a new proof, via conic duality, of the
equivalence between the portfolio value function and the trading function. The geometric
framing also yields composition rules, addition, scaling, matrix mapping, intersection, that let
CFMMs be combined and manipulated as convex objects independent of their coordinate
representation.

**Authors / venue / year:** Guillermo Angeris, Tarun Chitra, Theo Diamandis, Alex Evans, Kshitij
Kulkarni. arXiv:2308.08066, July 2023.

## Key points

- A reachable set S ⊆ R^n defines a fee-free CFMM if it satisfies three axioms: (1) nonnegative
  reserves, S ⊆ R+^n; (2) S is nonempty, closed, and convex; (3) S is upward closed, R ∈ S
  implies any R' ≥ R is in S. No differentiability, homogeneity, or trading-function form is
  assumed.
- Any set defined as a superlevel set of a quasiconcave, nondecreasing function satisfies these
  axioms, so the framework strictly generalizes prior homogeneity-assuming treatments (including
  the equivalence result in [[source-replicating-market-makers]]).
- Composition rules follow directly from convex-set calculus and require no extra assumptions:
  nonnegative scaling αS (adding or removing liquidity), set addition S + S' (combined holdings
  of two CFMMs), nonnegative matrix mapping AS + R+^n (basket/meta-asset construction, including
  projection onto a subset of traded assets), and intersection S ∩ S' (reserves common to both).
  Aggregate CFMMs over a network of m markets are built by summing matrix-mapped reachable sets,
  S̃ = Σ A_i S_i.
- The liquidity cone K = cl{(R, λ) | R/λ ∈ S, λ > 0} is a homogenized version of the reachable
  set: a convex cone whose λ-coordinate measures available liquidity at reserves R. It recovers S
  by S = {R/λ | (R, λ) ∈ K} for any λ > 0.
- The canonical trading function is φ(R) = sup{λ | (R, λ) ∈ K}, equivalently, if S is written via
  a nondecreasing quasiconcave ψ with ψ(R) ≥ k, φ(R) = sup{λ > 0 | ψ(R/λ) ≥ k}. This function is
  always nondecreasing, concave, and homogeneous of degree 1, even when the original ψ used to
  define S is none of those things.
- The paper extends many results to CFMMs that allow a single trade with no path-independence
  assumption, and shows path-independent CFMMs have a purely geometric description that needs no
  notion of trading history.

## Notable claims & data

- Axiom set for a reachable (fee-free) set S: S ⊆ R+^n; S nonempty, closed, convex; S upward
  closed. Interpreted respectively as solvency, "bigger trades do not get a better rate," and
  "the CFMM accepts more of any asset."
- Canonical trading function: φ(R) = sup{λ | (R, λ) ∈ K}, with φ(R) = 0 if the set is empty. When
  S is written as {ψ(R) ≥ k}, this is φ(R) = sup{λ > 0 | ψ(R/λ) ≥ k}, the largest positive root
  in λ of ψ(R/λ) = k when ψ is continuous.
- Uniswap: S = {R ∈ R+^2 | R1 R2 ≥ k}. Uniswap v3 tick: S = {R ∈ R+^2 | (R1+α)(R2+β) ≥ k}, α, β,
  k > 0, both shown as canonical instances of the reachable-set axioms.
- Explicit computational note: the canonical trading function (6) may have **no closed form**.
  Because evaluating φ(R) is a root-finding problem in λ, it can still be computed efficiently in
  practice by bisection, since ψ(R/λ) is nondecreasing in λ, or by Newton's method when ψ is
  differentiable. This is a direct statement that curve-shape questions in this framework are, in
  general, a **numerical program**, not a closed-form derivation, even when the underlying axioms
  are purely geometric.
- Positive reachability: (R++^n, 0) ⊆ K, meaning every strictly positive reserve basket is
  feasible at some large enough liquidity multiple, a consequence of nonemptiness of S rather
  than an added assumption (as it is treated in some prior papers).
- Extension to bounded debt: if S + S' need not stay closed under negative reserves in general,
  but if there exists x ∈ R+^n with x + S ⊆ R+^n (bounded debt), the closedness results carry
  over by a near-identical proof.

## Connections

- [[concept-convex-duality]]: this is the generalization referenced there. Where
  [[source-replicating-market-makers]] proves the payoff/curve equivalence for differentiable,
  1-homogeneous payoffs via Fenchel conjugacy, this paper reproves and extends the same
  equivalence via conic duality on the liquidity cone, without requiring differentiability or
  homogeneity of the starting trading function.
- [[concept-bonding-curve]], [[concept-constant-function-market-maker]]: the reachable-set axioms
  are a strict generalization of the standard "trading function invariant" definition; every
  invariant-based CFMM in the region's other sources is a special case.
- [[concept-liquidity-profile]], [[concept-liquidity-surface]]: the liquidity cone's λ coordinate
  formalizes "amount of liquidity available from reserves R," the same intuitive object those
  concepts describe from an empirical/AMM-parametrization angle.
- [[concept-uniswap-v3-ticks]]: the tick reachable set (R1+α)(R2+β) ≥ k is given here as a
  reachable-set example, matching the tick description in [[source-clmm-mathematical-framework]].
- [[concept-reserve-option-duality]]: both this paper's canonical-trading-function construction
  and RTW26's reserve-option duality are, at bottom, statements that a CFMM's reserves and its
  payoff determine each other; this paper supplies the most general (axiomatic, non-smooth)
  version of that determination.

## Open questions

- The paper's own computational note leaves open which classes of ψ admit closed-form canonical
  trading functions versus requiring bisection or Newton iteration; this boundary is exactly the
  design question a computational study of curve shape must map out.
- Extension of the composition rules (addition, matrix mapping) to CFMMs with fees is left open
  in the excerpted sections; the reachable-set framework here covers the fee-free case only.
- The single-trade (non-path-independent) generalization is developed later in the paper, not
  covered in the pages read here; how far the canonical-trading-function result survives outside
  path independence is not established in this summary.
