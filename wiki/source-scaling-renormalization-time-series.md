---
title: Scaling Renormalization Time Series
layer: core
type: source
origin: thesis
source_path: "articles/scaling and renorm/Scaling symmetry, renormalization, and time series modeling.pdf"
source_kind: paper
date: 2026-07-19
---

# Scaling symmetry, renormalization, and time series modeling

A stochastic model of financial-asset return dynamics built by inverting the renormalization-group flow, using time-scaling symmetry to fine-grain elementary returns into a tractable process that reproduces the empirical stylized facts of the S&P500.

**Authors / venue / year:** Marco Zamparo (HuGeF, Torino); Fulvio Baldovin, Michele Caraglio, Attilio L. Stella (Dipartimento di Fisica, INFN/CNISM, Università di Padova). arXiv:1305.3243v3 [q-fin.ST], dated June 7 2018 (v3 posted 27 Sep 2013).

## Key points
- Proposes an "inverse renormalization group" strategy: instead of coarse-graining to a fixed point, it inverts the RG flow — taking the known scaling properties of aggregated returns as input and fine-graining to find probabilistic rules for elementary increments consistent with that scaling.
- The model factorizes each return as the product of two components: an endogenous auto-regressive (ARCH-like) long-memory component {Y_t} of memory order M, and a rescaling/modulating short-memory factor {a_{I_t}} driven by a Markov-chain "time-restart" mechanism.
- Built to embody a time-scaling (Hurst) symmetry at least approximately over finite time windows; distinguishes long-memory (endogenous) and short-memory (endogenous + exogenous) contributions to volatility.
- Provable mathematical properties: increments' stationarity, ergodicity, strong mixing, time-reversal asymmetry, and martingale (efficient-market) character of the return process.
- Low parameter count (typically 5: M plus D, ν for long-memory and α, β for short-memory), enabling calibration via a generalized method of moments rather than intractable maximum likelihood.
- Calibrated on daily S&P500 data 1950–2010; reproduces volatility clustering, power-law-decaying volatility autocorrelation, fat-tailed return PDF, multiscaling of aggregated returns, time-reversal-symmetry breaking, and leverage effects (with generalizations).
- Analytical tractability opens applications to derivative pricing (closed-form perspectives) and risk evaluation; can make contact in limits with standard auto-regressive (ARCH/GARCH, SWARCH) models.

## Notable claims & data
- Simple-scaling symmetry: t^H g_t(t^H x) = g(x) for the aggregated-increment PDF, giving moment scaling E[|X_1+...+X_t|^q] = t^{qH} E[|X_1|^q] (Eqs. 1–2); Gaussian g with H=1/2 is normal scaling, non-Gaussian g and/or H≠1/2 is anomalous; q-dependent H_q is multiscaling (generalized Hurst exponent).
- Schoenberg's theorem is invoked to characterize admissible scaling functions g as Gaussian mixtures, g(x) = ∫ dσ ρ(σ) N_σ(x) (Eqs. 8–9), with ρ a PDF on the positive real axis; joint PDF given as a mixture over ρ of products of centered Gaussians (Eq. 10).
- Rescaling factors take the form a_i = sqrt(i^{2D} − (i−1)^{2D}) (Eq. 19), with model parameter D replacing the Hurst exponent H; D<1/2 gives decaying factors (finance-relevant), D=1/2 gives a_i=1, D>1/2 diverging.
- Markov-chain time-restart: chain {I_t} with P[I_1=i]=ν(1−ν)^{i−1} and transition probabilities restarting (I=1) with probability ν or advancing with probability 1−ν (Eqs. 16–17); yields a stationary Markov-switching (regime-switching) volatility.
- Choosing ρ as an inverse-gamma distribution (Eq. 20, parameters α, β) makes the endogenous component a genuine ARCH process of order M with Student's-t-distributed return residuals (Eqs. 21–22, degrees α_n = α + min{n−1,M}); reconciles the model with the Hamilton–Susmel SWARCH category.
- Single-variable PDF is a Gaussian mixture with power-law tails: f_1^X(x) ~ |x|^{−α−1} tail index α when ρ decays as σ^{−α−1} (Eqs. 25–26).
- Joint PDF f_t^X does not depend on memory range M for time scales t ≤ M+1 (Eqs. 23–24): models with different M but same other parameters are indistinguishable at short times.
- Empirical validation: multiscaling exponent q H_q computed via least squares over windows up to t=31, M≥30 (Fig. 1, parametrized by (D,ν)); compared against S&P500 daily log-returns across sub-periods 1950–2010, 1950–1970, 1970–1990, 1990–2010 (Fig. 2), showing simple-scaling for q≲3 and sample-dependent multiscaling for q≳3.
- Volatility autocorrelation r_q^X(t) (Eq. 28) decays exponentially fast on scales ≫ M, controlled by the ratio of time-independent coefficients u_q/v_q; short-scale (t ≤ M+1) behavior set by the short-memory component alone.

## Open questions
- How to cleanly separate exogenous from endogenous volatility mechanisms in market dynamics using the long-memory / short-memory decomposition — the paper treats short-memory as mixing endogenous and exogenous influences.
- Proper description of correct scaling and multiscaling of aggregated increments in FIGARCH-type approaches remains an open issue that this framework aims to address.
- The direct link between the Hurst exponent H and the model parameter D is lost when long- and short-memory processes are combined, motivating the reparametrization via D; the precise relation is application-dependent.
- Extension to include skewness in the return PDF and leverage effects (only sketched here) for consistent recovery of those stylized facts.
- Relevance to volatility modeling in finance: the ARCH/SWARCH/multiscaling connection suggests using anomalous temporal scaling to obtain analytically tractable auto-regressive models on limited time horizons — of direct interest to derivative pricing and volatility forecasting.
