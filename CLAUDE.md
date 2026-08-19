# CLAUDE.md — CFMM Liquidity Research Repository

## PURPOSE

Thesis on liquidity provision in Constant Function Market Makers (CFMMs), explored as
computational research: build from the anchor papers into areas they cover mathematically but
not computationally, plus continuations and new angles.

Anchor — the work of Tai-Ho Wang:

- `articles/liquidity/A MATHEMATICAL FRAMEWORK FOR MODELLING CLMM.pdf`
- `articles/liquidity/DYNAMICS OF LIQUIDITY SURFACES IN UNISWAP V3.pdf`
- `articles/vol surface/Pricing and Hedging for Liquidity Provision in Constant Function Market Making.pdf`
- `articles/Geometry (Wang)/9879Lecture06-2025-MathInAMM.pdf` (lecture)

---

## ENVIRONMENT

Machine specifics (OS, CPU, RAM, GPU, compute defaults) live in `.claude/machine.local.md`,
ignored under MACHINE-LOCAL — true of this laptop only, invalid in any other checkout.

---

## CODING PRIORITIES

Baseline — vectorization-first, numpy/pytorch-from-scratch by default, fast-loud errors — is
governed by L0 (`~/.claude` coding-preferences memory) and not restated here. Priorities
specific to this project, beyond that baseline:

1. **Efficiency** — prefer O(n log n) over O(n²); profile before micro-optimising
2. **Numerical stability** — use stable formulations (`log1p`, Cholesky over direct inversion, log-sum-exp); flag ill-conditioned ops explicitly
3. **Readability** — names encode units and semantics (`sigma_ann`, not `s`); nesting ≤ 2 levels; annotate every function signature with types

---

## CHANGE TRANSPARENCY

**Every modification to existing code must be explicitly stated before or alongside the edit**, including:

- which file and function/section is affected
- what changed and why
- any numerical parameters altered (tolerance, grid size, seed, etc.)

Silent changes are not acceptable. If a change is incidental (e.g. fixing a typo while editing logic), still name it.

---

## TERMINAL COMMANDS

Execution permission is governed by L0 (`~/.claude` coding-preferences memory) and the
harness's global `permissions.ask` default — not restated here.

---

## CONFIDENCE

When identifying or fixing a bug, or before any non-trivial implementation, state:

```txt
Confidence : HIGH | MEDIUM | LOW
Uncertainty: <what is unclear>
Resolves if: <what file or information would remove it>
```

If confidence is LOW, ask before proceeding.

---

## PLUGINS

| Plugin                              | Trigger                                                                  |
| ----------------------------------- | ------------------------------------------------------------------------ |
| `pr-review-toolkit:code-reviewer`   | After any non-trivial implementation, and before marking a task complete |
| `pr-review-toolkit:code-simplifier` | Function exceeds ~40 lines or cyclomatic complexity > 5                  |

---

## HARD CONSTRAINTS

- No raw API responses or unprocessed market data written to disk
- No secrets or API keys in any file
- Git operating rules: `core/os/git-discipline.md` in the GeorgOS vault this folder sits inside
- No plan or implementation at LOW confidence without asking first

---

## GEORGOS REGION

This folder also sits inside a GeorgOS vault, one directory below the root that carries the
shared layers (L0 preferences, `core/`, the personal region). The coding contract above is
authoritative for development; this block only points to the knowledge layer.

- **origin slug:** `thesis` — every curated page under `wiki/` is stamped `origin: thesis`.
- **layer:** `core` (inherited from the GeorgOS root vault).
- **Knowledge folder:** `wiki/` — curated pages, catalog (`wiki/index.md`), log
  (`wiki/log.md`); `wiki/graphs/` is reserved for `ingest-graphify`, not yet used.
- **Config:** `region.yml` (authoritative; ingest/lint read it). `raw: .` — in-place mode: the
  project files are the sources, nothing is copied into a separate `raw/` folder.
- **Tracked in this repo:** `region.yml` and `wiki/`. Untracked: `.obsidian/`,
  `codebase/graphify-out/` (the parked code graph).
- Re-onboard new files: `/graph-connect projects/Thesis --run` (from GeorgOS).
- Health-check: `/lint --target thesis`.

Scope onboarded (2026-07-14): 17 article PDFs, `latex/chapters/{abstract,introduction}.tex`,
`README.md`, and `codebase/` as a parked code graph. Excluded: data files (parquet/json/env),
generated images, boilerplate LaTeX/bib, `.claude/`/`AGENTS.md`/this file, and
`partial_summary.ipynb` (unsupported format, flagged for manual review).

---

<!-- planner:computational-research START -->

## Active planner: computational-research (type: computational-research)

This project runs the **computational-research** planner. Its instance lives in
`.planner-computational-research/` — the procedure in `workflow.md` and the ledger in
`progress.md` (frontmatter `status` / `current_phase`). The full definition (legend / flow /
cadence / reroute) is the plugin's bundled `planners/computational-research.md`.

**Cadence (bookkeeping).** Append a heavily-summarized entry (1–3 lines) to
`.planner-computational-research/progress.md` and advance `current_phase` when: reasoning
produces a spec (step 2); a plan is created (step 3); each plan task completes (step 4, one line
per task); new non-trivial knowledge is jointly approved (step 5). Detailed execution reports
stay in `.superpowers/sdd/`; the ledger only summarizes them.

**Coding reroute (scope for every coding agent / direct edit).**

- Before dispatching a coding agent (or coding directly), query `codebase/graphify-out/` via
  `/graphify` query mode (node / path / community) for the module(s)/file(s) the task touches.
  Treat the returned graph as the authoritative source of structure/dependencies — verify against
  it, don't guess.
- Dispatch coding agents enriched **only** by the relevant `codebase/graphify-out/` nodes the task
  touches, plus the active spec, active plan, and `.planner-computational-research/progress.md`.
  Instruct each agent to query and defer to the graph as its source of knowledge for the codebase.
- Dispatch step-4 coding through the `computational-research-coder` worker agent. For **long
  autonomous runs** (dynamic mode, or many chained tasks before the step-5 human review), pair it
  with the read-only `computational-research-observer` (Haiku, advisory-only): keep the worker's
  `observer:` field and launch with `CLAUDE_CODE_EXPERIMENTAL_OBSERVER_AGENTS=1`. For a short
  **static** one-task plan, skip the observer.
- Do **not** load personal (`GiorgIA/`) or `core/` knowledge unless explicitly queried.
- Graphify stays live via its own post-commit hook (`graphify hook install`, once per project):
  each task commit triggers an incremental rebuild automatically — no manual `/graphify` per task.
- Once a task is committed and the hook has rebuilt the graph, free stale context: a single
  dispatched coding agent ends with `/clear`; the orchestrator running across further tasks runs
  `/compact` instead.
- Update Obsidian only on an explicit `/ingest` (results) or `/ingest-graphify` (code) — gated to
end-of-cycle (step 6). Results flow to the planner folder and eventually to Obsidian — never
directly to graphify.
<!-- planner:computational-research END -->
