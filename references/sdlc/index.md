# Agentic SDLC: implementation & technical patterns

This is a small notes area -- **not** the wiki-book. It digests the
**technical/implementation** content of one external source, on its
own terms. It deliberately excludes that source's leadership/
organisational chapters (business case, governance, team structures,
the transition plan) -- this project has no use for those, only for
concrete agentic-engineering technique.

That keeps this folder's subject distinct from `references/harnesses/`,
which documents the internals of specific agent harnesses (Claude
Code, Copilot CLI, OpenCode) and general agent-engineering concepts
grounded in official docs/repos and the general agent-engineering
literature. This folder is a single-source digest instead; treat its
claims as "the handbook says," not as independently cross-verified the
way the wiki-book's claims are.

`airchon-author` is the writer for this area (as it is for
`references/harnesses/` and `references/rag/`); `airchon-mentor` reads
it but does not write it. Every page's claims are attributed inline to
the specific chapter/section of the handbook they came from, and
"verification" here means re-fetching that chapter from the live site
this session and checking the digest against the source text directly
-- not cross-checking against harness docs or any other independent
authority, which is out of scope for this single-source area by
design.

## Source

**The Agentic SDLC Handbook**, Daniel Meppiel --
https://danielmeppiel.github.io/agentic-sdlc-handbook/. A prior
research pass (recorded in
[`references/harnesses/deterministic-orchestration.md`](../harnesses/deterministic-orchestration.md)'s
Sources section) fetched this handbook while scoping it for the
wiki-book and ruled it out as a primary source there -- it is
"overwhelmingly an organisational methodology/process guide," not a
documented account of any harness's internals. The one exception
already extracted into the wiki-book is GitHub Agentic Workflows'
`safe-outputs:` mechanism, independently re-verified against GitHub's
own docs. This folder captures the handbook's technical chapters on
their own terms instead of leaving them undocumented.

**Verification status (2026-08-24).** `airchon-author` took over
authorship of this area this session and re-fetched the live chapter
pages for a representative sample across the corpus (Ch. 4, Ch. 13,
Ch. 16, and the full Part III/IV/Appendix table of contents) to check
the existing pages against the source text directly, rather than
trusting the prior digest on faith. Every chapter and appendix listed
below resolved at its cited URL and the sampled pages' claims, quotes,
and figures matched the live text; no corrections were needed. The
chapter-URL slugs below are exactly the ones that return HTTP 200 on
`danielmeppiel.github.io/agentic-sdlc-handbook/handbook/` as of this
verification pass.

## Pages -- Part III: For Practitioners

1. [Part III preface & the practitioner's mindset](09-10-part-iii-preface-and-practitioners-mindset.md) (Ch. 9-10) -- eight terms practitioners cannot avoid, the five-layer supply chain restated, the four composition patterns (Panel/Wave/Scatter-Gather/Subagent), the autocomplete trap, the Architect/Reviewer/Escalation-Handler triplet, and a timestamped worked example
2. [The agentic runtime machine](11-the-runtime-machine.md) (Ch. 11) -- the four parts (Model/Harness/Agent Source Code/Client), "the harness is the compiler," cross-harness file-naming incompatibility, markdown as code, and the inference-per-thread/filesystem-shared asymmetry
3. [The instrumented codebase](12-the-instrumented-codebase.md) (Ch. 12) -- seven primitive types, load modes, the instrumentation audit, before/after walkthrough
4. [The PROSE framework](prose-framework.md) (Ch. 13) -- five constraints for making AI-agent output reliable, verifiable, and maintainable
5. [The load lifecycle](14-the-load-lifecycle.md) (Ch. 14) -- the four-phase Resolve/Materialize/Bind/Activate pipeline, the three binding modes, deterministic-vs-probabilistic factors in Activate, and the phantom-dependency/bundle-leakage anti-patterns
6. [Attention and context economy](15-attention-and-context-economy.md) (Ch. 15) -- window vs. attention, the U-shaped attention curve, the three levers (progressive disclosure, subagent isolation, plan-write-then-reload), and the five access mechanisms
7. [The deterministic/probabilistic boundary](16-deterministic-probabilistic-boundary.md) (Ch. 16) -- the seam between the two computers, strong- vs. weak-form supervised execution, named substrate patterns (safe-outputs, CI Lambda gating, Argo/Temporal), hallucination as a system property, and the four kinds of quality gate
8. [Multi-agent orchestration](17-multi-agent-orchestration.md) (Ch. 17) -- Panel/Wave/Scatter-Gather/Subagent composition patterns, the one-file-one-agent rule, wave-based parallelism, the four-level escalation protocol, and the PR #394 coordination-tax numbers
9. [The execution meta-process](18-the-execution-meta-process.md) (Ch. 18) -- the five-phase AUDIT/PLAN/WAVE/VALIDATE/SHIP methodology, the four-part checkpoint, the ADAPT loop, wave sizing, and the PR #394 worked example
10. [Architectural patterns: a Rosetta Stone](19-architectural-patterns-rosetta-stone.md) (Ch. 19) -- the four-layer substrate (Foundation/Assembly/Composition/Execution), a Gang-of-Four/distributed-systems pattern catalogue for agentic runtimes, and the decision matrix for which pattern to reach for
11. [Anti-patterns and failure modes](20-anti-patterns-and-failure-modes.md) (Ch. 20) -- 19 named anti-patterns mapped onto the five PROSE constraints, each with symptom, root cause, fix, and recovery
12. [Primitives as code](21-primitives-as-code.md) (Ch. 21) -- packages over files, the lockfile, overrides, versioning, three authoring concerns
13. [The reference architecture, earned](22-the-reference-architecture-earned.md) (Ch. 22) -- composition as a recursive Skill-Persona-Context triplet, eval-and-plan-persistence as the governance mechanism, and a Panel walked end to end (Maya's PR #4711)

## Pages -- reference architecture

- [The Agentic SDLC reference architecture](04-the-reference-architecture.md) (Ch. 4) -- Part II, but architectural rather than organisational; Part III's practitioner chapters build directly on it and Ch. 22 revisits it "earned"

## Pages -- Part IV: Case Studies

- [Case study: the APM auth + logging overhaul](23-case-study-apm-overhaul.md) (Ch. 23) -- PR #394: 75 files, 6-agent audit panel, 8 plan iterations, 5 waves, 5 named escalations, and the "context remains finite," "output remains probabilistic," "human judgment is the differentiator" lessons
- [Case study: writing a ~68,000-word book with agent fleets](24-case-study-handbook-writing.md) (Ch. 24) -- 11 personas in 4 pods (3 created dynamically mid-project) writing the handbook itself via APM-packaged agent orchestration
- [Case study: the publishing pipeline](25-case-study-publishing-pipeline.md) (Ch. 25) -- converting the manuscript to HTML/PDF/EPUB via Quarto + GitHub Pages, the five-fix PDF rendering cascade, and the four-iteration CI/CD build-out
- [Case study: building a growth engine](26-case-study-growth-engine.md) (Ch. 26) -- 15 personas across 7 panels building email capture and launch infrastructure, a genuine platform-limitation escalation, and a persona-drift incident

## Pages -- Appendices

- [Appendix A: the cross-harness reference](appendix-a-cross-harness-reference.md) -- a master comparison table mapping ten primitive concepts to their concrete file/config convention across five harnesses (Copilot, Claude Code, Cursor, Codex CLI, OpenCode)
- [Appendix B: Genesis worked example -- panel re-architecture](appendix-b-genesis-worked-example.md) -- a panel-in-one-thread anti-pattern diagnosed and fixed into fan-out-with-arbiter, from the author's own open-source Genesis tool

## Out of scope, on purpose

Ch. 1 (The Agentic SDLC Thesis), Ch. 2 (The AI-Native Landscape),
Ch. 3 (The Business Case), Ch. 5 (Governance for AI-Assisted
Delivery), Ch. 6 (Team Structures), Ch. 7 (The Agentic SDLC Bill),
Ch. 8 (Planning the Transition), and Ch. 27 (What Comes Next) are
leadership/organisational chapters, not implementation content, and
are not documented here.
