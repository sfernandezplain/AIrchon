# Handoff: DeepSeek Harness per-harness coverage rollout

Written 01/09/2026, mid-session. Scratch/planning doc at the project
root, same convention as the prior `HANDOFF-harness-coverage-followup.md`
(deleted once resolved) and `HANDOFF-missing-topics.md` before it.
Delete this file once the remaining items below are either done or
explicitly deprioritized -- it is not part of the wiki-book itself and
nothing under `references/harnesses/` should depend on it existing.

## Origin

A continuation of the per-harness parity project documented in the
now-deleted `HANDOFF-harness-coverage-followup.md`. That handoff
brought pi (9/29 -> 29/29) and Hermes Agent (7/29 -> 29/29) to full
parity across the book's 29 per-harness comparison pages. DeepSeek
Harness was left at its original 5/29 coverage, explicitly noted in
`index.md` as "not-yet-scheduled follow-up work." This session picked
up DeepSeek.

### The coverage-model correction

The prior handoff used a simple "grep for the harness name anywhere
in the file" audit. That was insufficient for DeepSeek Harness because
several pages have **passing mentions** (e.g. "DeepSeek" listed as a
model provider name in an OpenCode/Copilot context) without a dedicated
per-harness section. This session's first step was to re-audit using
heading patterns (`^#{2,4}.*DeepSeek`) instead of bare string matches,
which revealed that the real starting count was **5 pages with dedicated
sections** (fan-out, hooks-lifecycle-extensibility, permissions-and-
sandboxing, llm-api-contract, session-persistence -- all from the
2026-08-20 Hermes batch), not the 14 the coarse grep implied. The
initial 24-missing-page list from the old handoff was correct; the
coarse "OK" flags on 9 of those 24 were false positives.

## What this session did

1. Re-audited all 29 per-harness pages using heading patterns, not
   string matches, to build an accurate coverage matrix.
2. Dispatched 16 parallel `airchon-author` agent calls (Agent tool,
   `subagent_type: airchon-author`), one per page that the heading-
   pattern audit confirmed was missing a dedicated DeepSeek section,
   each told to: read the target page first to match existing section-
   numbering/style, research DeepSeek Harness live from its own repo
   (`github.com/deepseek-ai/deepseek-harness`, `master` branch) and
   docs for that page's specific topic, add the new section + fold
   DeepSeek into the page's closing synthesis table/prose + Sources,
   and **explicitly not touch `index.md`**.
3. The operator issued STOP mid-batch. Some agents had already written
   their sections before the cancellation took effect; others were
   cancelled before writing.
4. The `index.md` consolidation step (updating each affected row with
   a "new §N DeepSeek Harness" annotation + the Coverage note, same
   pattern as the pi and Hermes rollouts) was **not run** -- it touches
   only `index.md`, is idempotent, and should be the final step once
   all pages are complete.

### Coverage matrix at session end

| State | Count | Pages |
|---|---|---|
| **DONE** (dedicated heading, verified on disk) | 19 | agent-loop-implementations, mcp-integration, instruction-context-budget, built-in-tools, context-compression, permissions-and-sandboxing (pre-existing), hooks-lifecycle-extensibility (pre-existing), session-persistence (pre-existing), built-in-skills, tool-schema-and-interface-design, context-retrieval-and-agentic-search, retries, orchestration, fan-out (pre-existing), inter-agent-messaging, observability-and-self-diagnostics, tui-cli-application-architecture, mcp-supply-chain-trust, llm-api-contract (pre-existing) |
| **PARTIAL** (passing mention only, no dedicated section) | 8 | memory-management, model-routing-and-selection, auth-and-usage-accounting, system-prompt-design-as-craft, caching, evals-and-testing-a-harness, handoff-mechanism, configuration |
| **MISSING** (dispatched but cancelled before writing) | 2 | packaging-distribution-and-self-update, streaming-and-incremental-rendering |
| **Total** | 29 | |

Pre-existing sections (5, from the 2026-08-20 Hermes batch):
fan-out, hooks-lifecycle-extensibility, permissions-and-sandboxing,
llm-api-contract, session-persistence.

New sections written this session (14):
agent-loop-implementations (§6), built-in-tools (§6), built-in-skills (§6),
context-compression (§6), context-retrieval-and-agentic-search (§7),
instruction-context-budget (§6), inter-agent-messaging (§6),
mcp-integration (§6), mcp-supply-chain-trust (§10), observability-and-self-
diagnostics (§6), orchestration (§7), retries (§6), tool-schema-and-
interface-design (§1.8/§2.7/§3.7/§4.8 woven subsections), tui-cli-
application-architecture (§6).

### A side-effect worth noting

DeepSeek Harness is a Cordis-plugin-architecture harness -- "everything
is a plugin" -- with a remarkably structured `docs/` tree (per-subsystem
docs pages, `.agents/notes/implemented/` architectural decision records,
machine-generated `docs/config-catalog.md`). Three of the 14 completed
agents independently surfaced the same architectural distinctive: DSH
factors capabilities (compaction, subagents, MCP, retry, tool execution,
messaging, orchestration) into individually loadable Cordis plugins
rather than core-loop code -- a composition-time-not-runtime-discovery
design that is strictly stronger than any other harness's on/off config
switch. Several agents also surfaced a durable, log-backed event-sourcing
model with invariant-validated companion events, a pattern no other
harness on any page exhibits to the same degree.

## Remaining work

### Step 1 -- remaining pages -- TASK LIST (tracked 01/09/2026, updated same day)

Each needs a dedicated DeepSeek Harness section, same dispatch pattern as
the 14 that landed originally. Worked sequentially, one page at a time,
with `index.md` updated after each page lands (not deferred to a single
final pass).

**Done this continuation (4):**
- [x] **memory-management.md** -- turned out to already have a §6 DeepSeek
  section from the original interrupted batch, just with a broken/
  incomplete synthesis table (missing DeepSeek column data across all 18
  rows); fixed rather than re-written from scratch.
- [x] **model-routing-and-selection.md** -- new §6: named-route model
  resolution (`GenerateOptions.provider`/`.model`, no precedence stack),
  two coexisting first-class LLM adapters (`dsh-llm-deepseek`,
  `dsh-llm-pi-ai` wrapping `@earendil-works/pi-ai`), the `agent/request`/
  `llm/stream` Cordis waterfall hooks as the real routing seam.
- [x] **auth-and-usage-accounting.md** -- new §6: disjoint `CredentialRef`/
  `CredentialKey` spaces, `.credentials.yaml` store, `dsh-authorization`
  OAuth seam, `ctx.tokenMeter` accounting, and a real negative finding --
  no in-core spend ceiling (`subagent-claude-code` only *classifies*
  Claude Code's own budget error, doesn't enforce one itself).
- [x] **system-prompt-design-as-craft.md** -- new §7: system prompt is
  itself a Cordis-plugin registry assembled per turn
  (`ctx.systemPrompt.section()`/`.assemble()`), per-tool `tool:<name>`
  prompt-section convention, two governing ADRs (ownership,
  sparse-order-allocation/cache-invalidation).

**Still missing (6) -- next up:**
1. [ ] **caching.md** -- server-side prefix reuse; DeepSeek's explicit
   `cacheRetention` enum across provider protocols is already mentioned
   in passing -- needs a full section. Open question worth checking first:
   whether this enum is literally shared code with pi's own (via the
   `dsh-llm-pi-ai` adapter wrapping `@earendil-works/pi-ai`, confirmed in
   model-routing-and-selection.md §6) or a separate DSH-specific
   implementation.
2. [ ] **evals-and-testing-a-harness.md** -- how a from-scratch harness's own
   correctness gets validated; DeepSeek's CI/test infrastructure.
3. [ ] **handoff-mechanism.md** -- agent-to-agent context transfer; DSH's
   continuable children, fork semantics, and durable session log.
4. [ ] **configuration.md** -- the general settings/config-file system;
   DeepSeek's Cordis overlay composition (profiles -> bundles -> patches)
   is a distinct config model.
5. [ ] **packaging-distribution-and-self-update.md** -- (dispatched twice
   now, cancelled before writing both times) -- the npm `@deepseek-ai/dsh`
   package, PyPI SDK distribution, node-addon Landlock launcher; a partial
   intro mention already exists at lines 51-59 but no dedicated section.
6. [ ] **streaming-and-incremental-rendering.md** -- (dispatched, cancelled
   before writing) -- client/UI-side buffering/reassembly; DeepSeek's
   rendering architecture.

Note: this continuation session's agents were briefly downloading fetched
DeepSeek docs pages to scratch files at the project root
(`_tmp_*.md`/`tmp_docs_*.md`) instead of the proper scratchpad directory --
those were found and deleted 01/09/2026. If future dispatches do this
again, redirect them to the session scratchpad, not the repo root.

### Step 2 -- index.md consolidation

Once all 10 pages above are complete, run a single final
`airchon-author` call to update `index.md`:
- Update each affected row with a "new §N DeepSeek Harness" annotation
  in the existing "written/updated YYYY-MM-DD (new §N...)" style.
- Update the Coverage note (currently line 92-108) from "DeepSeek Harness
  remains partial" to a full-parity statement matching the pi and Hermes
  notes.
- This is the only step that touches the shared file, so it's safe to
  run once, last.

### Caveat (carried forward from the prior handoff)

`index.md`'s own opening paragraph states the book is written "LAZY,
on demand, as real questions need each topic -- not pre-built
speculatively." The operator already made the explicit choice to pursue
full per-harness parity rather than strict lazy/on-demand, one harness
at a time. DeepSeek is the last harness on the list; completing it
brings the book to full 6-harness parity across all 29 per-harness
pages.

## Reproducing the audit

```powershell
# Accurate audit: check for dedicated section headings, not string matches
$pages = @(
    "agent-loop-implementations.md", "mcp-integration.md",
    "memory-management.md", "instruction-context-budget.md",
    "built-in-tools.md", "context-compression.md",
    "llm-api-contract.md", "permissions-and-sandboxing.md",
    "hooks-lifecycle-extensibility.md", "session-persistence.md",
    "streaming-and-incremental-rendering.md", "built-in-skills.md",
    "model-routing-and-selection.md", "auth-and-usage-accounting.md",
    "tool-schema-and-interface-design.md", "system-prompt-design-as-craft.md",
    "context-retrieval-and-agentic-search.md", "caching.md",
    "retries.md", "orchestration.md", "fan-out.md",
    "inter-agent-messaging.md", "packaging-distribution-and-self-update.md",
    "observability-and-self-diagnostics.md", "tui-cli-application-architecture.md",
    "handoff-mechanism.md", "mcp-supply-chain-trust.md",
    "evals-and-testing-a-harness.md", "configuration.md"
)
foreach ($name in $pages) {
    $path = "references\harnesses\$name"
    $headings = Select-String -LiteralPath $path -Pattern "^#{2,4}.*DeepSeek" -Quiet
    if (-not $headings) { Write-Output "MISSING: $name" }
}
```

Pages excluded by design (no per-harness sections, not counted in the
29): agent-topology.md, agent-loop.md, multi-agent-coordination-design-
space.md (GENERAL-CONCEPTS pages); advanced-planning-and-execution-
architectures.md (ORIGINAL DESIGN-SPACE SURVEY); deterministic-
orchestration.md, middleware-composed-agent-harnesses.md (orchestrator-
category pages).
