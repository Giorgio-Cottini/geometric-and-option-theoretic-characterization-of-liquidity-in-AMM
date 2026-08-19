# AI workflow and the wiki

This repository was developed with AI coding assistants (Claude Code and OpenAI Codex) as
part of the day-to-day workflow. This document states what those assistants touched, what the
`wiki/` folder is, and how a reader who did not write either can check a claim against its
source.

## Scope of AI involvement

The assistants wrote and edited code under `codebase/`, under the author's direction and
review, following the contract in `CLAUDE.md` (Claude Code) and `AGENTS.md` (Codex). Both
files are tracked in this repository and state the actual rules the assistants worked under:
vectorized, numerically stable implementations, type-annotated signatures, and an explicit
requirement to report confidence and name uncertainty before a non-trivial change.

The assistants did not write thesis prose. `AGENTS.md` states the boundary directly: the
author writes the thesis text under `latex/chapters/`, and an assistant edits it only on an
explicit request. `.claude/agents/computational-research-coder.md` and
`computational-research-observer.md` are the two project-specific agents that carried out and
checked coding tasks. Both are tracked and readable in full.

## The wiki

`wiki/` is the author's curated reading and synthesis, not a static bibliography and not a live
AI system. Every page is plain Markdown: a `source-*.md` page summarizes one paper, a
`concept-*.md` page defines one recurring idea, an `entity-*.md` page profiles one author or
organization, and a `synthesis-*.md` page connects several of the above into one argument.
Pages cross-reference each other with `[[wikilinks]]`, in the convention Obsidian and most
static-site wiki tools already read.

`wiki/index.md` is the entry point. It lists every page by type and links to
`synthesis-thesis-map.md`, which weaves the sources and concepts into the thesis's own
argument. A reader checking one claim in the thesis text follows the citation to the relevant
`wiki/source-*.md` page, reads the paper summary and its stated scope, and follows the
`[[wikilinks]]` from there outward as far as the claim needs.

The wiki was built and is maintained with AI assistance, under the author's review, as a
structured alternative to scattered reading notes. Its purpose is to keep a paper's claim, the
paper's own scope, and the thesis's use of that claim visibly distinct, so a reader can tell
which parts are the source's and which are the author's synthesis.

## What this repository does not include

Two pieces of the author's broader private tooling shaped how the wiki was built but are not
part of this repository and are not needed to read it. `codebase/graphify-out/`, a structural
graph of the codebase's own call structure, is regenerable from the code and is excluded as
build output, the same way a compiled artifact is. A small number of `wiki/concept-*.md` pages
cite it by name. The code under `codebase/` remains the ground truth for structure whether or
not that graph is present.

The author's task-planning ledger for AI-assisted coding sessions is local to the author's
machine and is excluded for the same reason `codebase/graphify-out/` is: it is process
scaffolding, not a claim this thesis depends on. Nothing in `latex/` or `wiki/` requires it to
be checked.

## Checking a claim

1. Start at `latex/chapters/`, or at `wiki/synthesis-thesis-map.md` for the reading as a whole.
2. Follow a `@citekey` to `latex/assets/bibliography.bib` for the full reference, or a
   `[[wikilink]]` to the matching `wiki/source-*.md`, `concept-*.md`, or `entity-*.md` page.
3. Each `source-*.md` page states what the cited paper claims and, where relevant, what it does
   not claim. Treat the underlying paper, not the wiki page, as the authority on both.
