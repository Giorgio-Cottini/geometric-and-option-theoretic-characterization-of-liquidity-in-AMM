# Thesis Research Router

This repository is Giorgio's University of Padova master's thesis on pricing and hedging
liquidity provision in CFMMs, with emphasis on Uniswap v3. Work from the smallest relevant
set of files and preserve the distinction between research evidence, computation, structural
planning, and prose written by the author.

## Route the task

| Intent | Start here |
| --- | --- |
| Understand the project or results | `README.md`, then the named code or chapter |
| Work on research code | `codebase/`, its tests, and relevant `codebase/graphify-out/` nodes |
| Answer from curated thesis knowledge | `$query`, inherited from GeorgOS core |
| Work under `latex/` | Also obey the nearer `latex/AGENTS.md` |

Treat `CLAUDE.md` and `.claude/` as historical implementation material. Read them only when
the user explicitly asks for comparison or migration; they are not Codex instructions.

The only GeorgOS core skill inherited here is `$query`. Its project-local entry is a relative
symlink to the canonical root skill. Do not copy or fork it, and do not expose `$ingest` or
`$lint` as Thesis skills.

## Research boundaries

- Do not invent results, citations, numerical values, or paper support. Name uncertainty.
- Enter the knowledge layer through `wiki/index.md`; follow only relevant wikilinks.
- Do not bulk-read `articles/`. Open a paper only when the task requires primary evidence.
- Never write raw API responses or unprocessed market data to disk.
- Never expose or commit secrets, credentials, `.env` contents, or API keys.
- Do not edit generated LaTeX outputs or compile `latex/main.tex`.
- Preserve unrelated working-tree changes and all existing paths.

## Code contract

- Inspect the relevant code graph for navigation, then verify claims against source and tests.
- Prefer vectorized NumPy or PyTorch implementations and stable numerical formulations.
- Use semantic names with units, type-annotate function signatures, and fail loudly on invalid
  inputs or ill-conditioned operations.
- Profile before optimizing. Prefer algorithmic improvements over micro-optimizations.
- Before or alongside an edit, state the file and symbol or section, the reason, and any changed
  tolerance, grid size, seed, or other numerical parameter.
- For a bug diagnosis or non-trivial implementation, report confidence and the concrete source
  of remaining uncertainty before changing code. Ask first if confidence is low.

## Thesis writing contract

- Giorgio writes thesis prose. Codex may plan structure, audit evidence, diagnose LaTeX, or edit
  prose only when explicitly asked.
- Keep source claims distinct from synthesis and attach evidence at the point of use.
- Use `@citekey` values that exist in `latex/assets/bibliography.bib`.
- Use `[[wikilinks]]` only for grounding artifacts; they never enter `.tex` files.

## Finish

Run the narrowest relevant checks. Report files changed, verification performed, unresolved
evidence gaps, and whether generated artifacts were intentionally left untouched.
