# Handoff: per-harness coverage follow-up

Written 01/09/2026, mid-session. Scratch/planning doc at the project
root, same convention as the prior `HANDOFF-missing-topics.md` (now
deleted once its list was resolved -- see `references/harnesses/observability-and-self-diagnostics.md`'s
and `packaging-distribution-and-self-update.md`'s own opening lines for
that precedent). Delete this file once the remaining items below are
either done or explicitly deprioritized -- it is not part of the
wiki-book itself and nothing under `references/harnesses/` should
depend on it existing.

## Origin

An audit (this session) of all 29 per-harness comparison pages in
`references/harnesses/` (the 6 GENERAL-CONCEPTS/survey pages and the 2
orchestrator-category pages -- `deterministic-orchestration.md`,
`middleware-composed-agent-harnesses.md` -- don't use per-harness
sections by design and are out of scope for this whole exercise) found
very uneven coverage of the book's six documented harnesses:

| Harness | Coverage at session start | Coverage now |
|---|---|---|
| Claude Code | 29/29 | 29/29 |
| Copilot CLI | 28/29 | 28/29 (unchanged) |
| OpenCode | 28/29 | 28/29 (unchanged) |
| Hermes Agent | 7/29 | 7/29 (unchanged) |
| DeepSeek Harness | 5/29 | 5/29 (unchanged) |
| **pi** | 9/29 | **29/29 (done this session)** |

The operator chose to bring harnesses to full parity **one at a time**
rather than a full sweep or just the two small Tier-1 gaps, and picked
**pi** first. That work is what this session did; Hermes Agent and
DeepSeek Harness are still exactly where they started.

## What this session actually did (for reference / to replicate)

1. Grepped `^#{2,4}.*<Harness Name>` across `references/harnesses/*.md`
   per harness to build the coverage matrix above -- fast, cheap,
   accurate enough (a heading match, not just a passing mention).
2. Dispatched 20 parallel `airchon-author` agent calls (Agent tool,
   `subagent_type: airchon-author`), one per page missing a pi section,
   each told to: read the target page first to match its existing
   section-numbering/style, research pi live from its own repo
   (`github.com/earendil-works/pi`) and docs for that page's specific
   topic, add the new section + fold pi into the page's closing
   synthesis table/prose + Sources, and **explicitly not touch
   `index.md`** (to avoid 20 agents racing on one shared file).
3. Dispatched one final `airchon-author` call, after all 20 finished,
   to update `index.md`'s per-page description rows for those 20 pages
   in the book's existing "written/updated YYYY-MM-DD (new §N
   <harness>...)" annotation style -- this is the only step that
   touches the shared file, so it's safe to run once, last.
4. **This last step's completion was not yet confirmed when this
   handoff was written** -- no `task-notification` for it had arrived
   yet. Whoever picks this up should check `references/harnesses/index.md`
   for a "pi" mention dated 01/09/2026 across those 20 pages' rows; if
   absent, the consolidation call needs to be (re)run. It touches only
   `index.md`, is idempotent to re-run, and does not need the 20 pages
   re-read from scratch by a human -- the agent prompt used is
   reproducible from this document's step 3 description plus the
   findings list each of the 20 agents already returned (see this
   session's transcript, or just re-derive by reading each page's new
   pi section directly).

A genuinely useful side-effect of this batch: it resolved a real,
recurring point of confusion in the existing book -- `pi` is not one
package inconsistently spelled two ways (`@earendil-works/pi-ai` vs.
`@earendil-works/pi-coding-agent`), it's a monorepo (`earendil-works/pi`,
formerly `badlogic/pi-mono` / `@mariozechner/pi-coding-agent` before an
acquisition) publishing **at least five** sibling packages: `pi-ai`
(LLM wire layer), `pi-coding-agent` (the actual CLI, `bin: pi`),
`pi-tui` (a from-scratch TUI framework, previously uncited), `pi-agent-core`
(a separate durable-runtime spec, previously uncited), and a private
`pi-evals`. Every one of the 20 agents independently re-verified this
from the packages' own `package.json` files rather than assuming the
book's prior citations were wrong.

## Remaining work

### Tier 1 -- two small, cheap gaps (original three-CLI core)

1. Add a **Copilot CLI** section to
   [tool-schema-and-interface-design.md](references/harnesses/tool-schema-and-interface-design.md)
2. Add an **OpenCode** section to
   [system-prompt-design-as-craft.md](references/harnesses/system-prompt-design-as-craft.md)
   (note: this page already *cites* an OpenCode source file --
   `packages/opencode/src/session/prompt/anthropic.txt` -- without
   having a dedicated OpenCode section; worth a quick look at why
   before assuming this is a simple oversight)

Each is a single `airchon-author` dispatch, same pattern as the batch
above, just aimed at one page/harness pair.

### Tier 2 -- Hermes Agent full rollout (7/29 -> 29/29, 22 pages missing)

instruction-context-budget.md, agent-loop-implementations.md,
context-retrieval-and-agentic-search.md, configuration.md,
auth-and-usage-accounting.md, llm-api-contract.md, context-compression.md,
session-persistence.md, built-in-tools.md, observability-and-self-diagnostics.md,
mcp-supply-chain-trust.md, packaging-distribution-and-self-update.md,
retries.md, tui-cli-application-architecture.md,
tool-schema-and-interface-design.md, system-prompt-design-as-craft.md,
evals-and-testing-a-harness.md, streaming-and-incremental-rendering.md,
inter-agent-messaging.md, handoff-mechanism.md, orchestration.md, caching.md

(Already has sections in: memory-management.md, mcp-integration.md,
model-routing-and-selection.md, fan-out.md, built-in-skills.md,
hooks-lifecycle-extensibility.md, permissions-and-sandboxing.md)

### Tier 2 -- DeepSeek Harness full rollout (5/29 -> 29/29, 24 pages missing)

memory-management.md, mcp-integration.md, instruction-context-budget.md,
agent-loop-implementations.md, context-retrieval-and-agentic-search.md,
model-routing-and-selection.md, built-in-skills.md, configuration.md,
auth-and-usage-accounting.md, context-compression.md, built-in-tools.md,
observability-and-self-diagnostics.md, mcp-supply-chain-trust.md,
packaging-distribution-and-self-update.md, retries.md,
tui-cli-application-architecture.md, tool-schema-and-interface-design.md,
system-prompt-design-as-craft.md, evals-and-testing-a-harness.md,
streaming-and-incremental-rendering.md, inter-agent-messaging.md,
handoff-mechanism.md, orchestration.md, caching.md

(Already has sections in: fan-out.md, hooks-lifecycle-extensibility.md,
permissions-and-sandboxing.md, llm-api-contract.md, session-persistence.md)

## A caveat worth re-raising before doing more of this

`index.md`'s own opening paragraph states the book is written "LAZY,
on demand, as real questions need each topic -- not pre-built
speculatively." A full systematic sweep to make every harness appear
on every page is a real change of posture from that -- it was the
operator's explicit choice to do the pi rollout anyway, one harness at
a time, but worth re-confirming intent before automatically continuing
into Hermes Agent and/or DeepSeek Harness rather than assuming the
same full-parity goal applies by default.
