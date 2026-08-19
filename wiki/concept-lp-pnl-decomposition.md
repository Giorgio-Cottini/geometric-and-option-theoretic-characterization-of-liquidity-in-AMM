---
title: Lp Pnl Decomposition
layer: core
type: concept
origin: thesis
date: 2026-07-19
---

# LP P&L Decomposition

The clean accounting identity that splits a CFMM liquidity provider's profit-and-loss into three interpretable terms: LP P&L = Rebalancing P&L − LVR + Trading Fee Income. It separates market-risk exposure, adverse-selection cost, and compensation, and is the organizing framework for judging LP profitability.

## Details
- Terms:
  - Rebalancing P&L — the value change of holding the AMM's risky position while trading at true market prices; pure market-risk exposure, mean-zero-ish and hedgeable.
  - LVR — the non-negative adverse-selection cost from arbitrageurs sniping stale quotes (see loss-versus-rebalancing).
  - Trading Fee Income — fees paid mainly by uninformed noise traders, the LP's compensation.
- Hedged form: shorting the rebalancing strategy removes the first term, leaving LP P&L = Fee Income − LVR — the economic core of liquidity provision.
- Profitability condition: an LP is (in expectation) profitable only when accumulated fees exceed accumulated LVR; this is the inequality any thesis on LP returns must evaluate.
- The decomposition holds for general CFMMs and, term-by-term, for concentrated positions weighted by the liquidity profile.

## Appears in
- [[source-quantifying-loss-in-amms]] — states the Rebalancing − LVR + Fees decomposition of LP P&L.

## Related
- [[concept-loss-versus-rebalancing]] — the negative (cost) term.
- [[concept-rebalancing-strategy]] — source of the rebalancing P&L term.
- [[concept-impermanent-loss]] — related loss-versus-holding view.
- [[concept-arbitrage-with-fees]] — determines the fee-income vs. LVR balance.
- [[concept-adverse-selection]] — economic origin of the LVR term.
- [[concept-lp-behavior]] — how LPs act on this profitability calculus.
- [[concept-reserve-option-duality]] — option view of the same P&L.
