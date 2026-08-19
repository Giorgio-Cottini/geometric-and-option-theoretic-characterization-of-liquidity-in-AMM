---
title: Wang Math in Amm
layer: core
type: source
origin: thesis
source_path: "articles/Geometry (Wang)/9879Lecture06-2025-MathInAMM.pdf"
source_kind: note
date: 2026-07-19
---

# Mathematics behind AMM in DeFi (MTH 9879, Lecture 6)

Baruch MFE course lecture that develops the mathematical theory of Automated Market Making in DeFi, from constant-function bonding curves through a canonical parametrization by liquidity (inverse hyperbolic curvature), impermanent loss, loss-versus-rebalance, and concentrated liquidity provision recast as a portfolio of options.

**Authors / venue / year:** Tai-Ho Wang, MTH 9879 Market Microstructure Models, Baruch College (CUNY), Spring 2025, Lecture 6.

## Key points
- AMMs are algorithms powering decentralized exchanges (DEXs): they replace order books with liquidity pools and set prices from the ratio of pooled assets. Compared to central limit order books (CLOBs) they are computation- and storage-efficient (closed-form, constant-time matching), permissionless, always available, and better suited to long-tail illiquid assets that lack active market makers.
- Two trader types in a pool: liquidity providers (LPs), who add both coins simultaneously without moving the pool price and collect fees, and swappers/traders, who exchange coins along the bonding curve and pay fees.
- Constant Function Market Making (CFMM) sets pool state on a level curve f(x,y)=L (the bonding curve); pricing is nonlinear and the implied y(x) must be decreasing for viability. Examples: Constant Product (CPMM, Uniswap v2), Geometric Mean (G3M / Balancer), and Curve.
- A canonical parametrization expresses any bonding curve in terms of the marginal price p and an intrinsic "liquidity" quantity; this liquidity equals the inverse of the hyperbolic curvature of the curve.
- Impermanent Loss (IL, aka divergence loss / loss-versus-holding) and Loss-Versus-Rebalance (LVR) are derived via Ito calculus; IL decomposes into a martingale (delta-hedgeable) term plus the non-negative LVR drift.
- Concentrated Liquidity Provision (CLP, Uniswap v3) lets LPs allocate liquidity to a chosen price interval; the resulting market-induced liquidity profile L(p) frees pricing from a single dictated bonding curve, and pool reserves reduce to payoffs of a portfolio of call options.

## Notable claims & data
- Bonding curve: f(x,y)=L with marginal/pool price P := -dy/dx = f_x / f_y (implicit function theorem). Trading occurs along the curve, so dy = -P dx.
- CPMM: f(x,y)=sqrt(xy)=L, giving P = y/x; equivalently xy = L^2. Transformations: L=sqrt(xy), P=y/x; x=L/sqrt(P), y=L*sqrt(P); pool value V = Px + y = 2L*sqrt(P). Reserves x,y are proportional to L.
- G3M/Balancer: f(x,y)=x^w y^(1-w)=L for w in (0,1); CPMM is the w=1/2 case. Curve: f(x,y)=beta(x+y) - xy/... (stableswap-type invariant).
- Price impact of trading Δx: to leading order Δy/Δx ≈ -L^2/x0^2 = -y0/x0 (CPMM), showing impact depends on traded amount AND on level L / current reserve.
- Price impact via line integral: ΔP = ∫(P_x - P·P_y)dx = ∫ 2P^{3/2} h dx along the bonding curve, where h is the hyperbolic curvature.
- Hyperbolic curvature h = (y''x' - x''y') / (2(-x'y')^{3/2}); for hyperbola y=L^2/x, h = 1/L, so liquidity λ = 1/h = L. Liquidity λ is invariant under translation, reflection, and the coordinate scaling (x,y)→(αx, y/α).
- Canonical parametrization: x(p) = ∫_p^∞ λ(q)/(2 q^{3/2}) dq, y(p) = ∫_0^p λ(q)/(2 sqrt(q)) dq, with λ (or h) viewed as a function of price p.
- Value of pool V = Px + y; regarding V as a function of P, V'(P)=x(P) and V''(P)=x'(P) = -λ(P)/P^{3/2} ≤ 0, so V is increasing and concave.
- IL: with held position H_t = x0 P_t + y0 and pool value V_t = V(P_t), IL_t = H_t - V_t = ∫_0^t {x(P0)-x(P_s)}dP_s - ∫_0^t (1/2)V''(P_s)d⟨P⟩_s. If P_t is a martingale, E[IL_t] = -E[∫ (1/2)V'' d⟨P⟩] ≥ 0 — on average the LP is better off holding than depositing (absent fees). Geometrically H(P) is the tangent line to concave V(P) at P0, so H ≥ V.
- LVR: with self-financing rebalancing strategy R_t (holds x(P_t) in the risky asset), dLVR_t = dR_t - dV_t = -(1/2)V''(P_t)d⟨P⟩_t ≥ 0, and IL_t = ∫_0^t{x(P0)-x(P_s)}dP_s + LVR_t. CPMM: dLVR_t = (L/(4 P_t^3)) d⟨P⟩_t.
- CLP reserves for range [p_l, p_r]: for P in range x = L(1/sqrt(P) - 1/sqrt(p_r)), y = L(sqrt(P) - sqrt(p_l)); above range x=0, below range y=0. In-range bonding curve: (x + L/sqrt(p_r))(y + L*sqrt(p_l)) = L^2 — a shifted CPMM hyperbola that intersects the axes (unlike CPMM), so swaps are impossible beyond the range endpoints.
- Liquidity profile L(p): superposing LP positions gives L(p) = Σ L_i 1_{[p_l^i, p_r^i]}(p). Via change of variable s=1/sqrt(p), pool reserve x(1/s^2) is the payoff of a portfolio of call options (long/short calls at the range endpoints); expressed as a Lebesgue-Stieltjes integral against a signed measure dL.
- Conversion liquidity profile ↔ reserves: x(P) = (1/2)∫_P^∞ L(p)p^{-3/2}dp, y(P) = (1/2)∫_0^P L(p)p^{-1/2}dp; then dy/dx = -P (canonical parametrization) and d²y/dx² = 2P^{3/2}/L(P) > 0, so the reserve curve is decreasing and convex.
- Worked examples: piecewise-constant profile L(p)=k1·1_{[a,b)}+k2·1_{[b,c)} yields closed-form x(P),y(P); continuous profile via chi-squared pdf; a Python `LiquidityReservePlot` class numerically integrates the profile into reserve curves (CPMM = constant profile).

## Open questions
- IL and LVR under a general liquidity profile L(p): the lecture begins deriving dV_t via Ito's formula for time-varying L_t(p), including terms in L_t'(P_t) — full characterization is left in progress.
- Model calibration: fit to the liquidity profile or to the bonding curve; if both are observable they must be consistent, otherwise arbitrage may exist.
- Problems to be done (course exercises): implement the profile/reserve conversion class and extend the IL/LVR analysis to concentrated / market-induced liquidity profiles.
