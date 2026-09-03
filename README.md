<div align="center">

<img src="airchon.png" alt="AIrchon" width="480"/>

# ⚡ AIrchon

**The Sovereign Mentor of Agentic Topologies**

*"Burn the black boxes. The fire belongs to all."*

[![Status: Source-Forged](https://img.shields.io/badge/Status-Source--Forged-0077ff.svg)]()
[![Topology: Unified](https://img.shields.io/badge/Topology-Harness%20Mastery-00e5ff.svg)]()

</div>

---

## 🏛️ Why "AIrchon"

The name fuses **AI** with **Archon** (Greek *árchōn*, ἄρχων --
"ruler," "first one," the one who governs). In the old mythic sense,
an Archon is a gatekeeper: a power that stands between people and
higher knowledge and hoards it. AIrchon takes that authority and turns
it inside out -- it is the archon that opens the gate instead of
guarding it.

The Promethean framing is the honest ambition, not a claim already
earned: AIrchon does not know anything the internet doesn't already
know. Claude Code's docs, Copilot CLI's docs, OpenCode's own source,
the HuggingFace Cookbook, the Agentic SDLC Handbook -- all of it is
already public. The actual problem is that it's scattered across
dozens of pages, changelogs, and repos, written for different
audiences, and most of it goes unread end to end. AIrchon's job is
narrower than "reveal hidden truth": fetch it live, cite it plainly,
organize it into one progressively-readable place, and teach it back
in order. Authority earned by citation, not by gatekeeping -- but the
fire was never actually locked away, just scattered and under-read.

---

## 👑 What this is honestly good for, and what it isn't

**What's actually been tested and holds up:** asking `airchon-mentor`
about your own harness's real, current tool surface, rather than
trusting a model's memory of it. A model's own knowledge of the tool
it's running inside is a documented blind spot -- training data goes
stale fast for a CLI that ships continuously, and a model will fill
gaps with plausible-sounding invented behavior rather than admit it
doesn't know. Checking a claim against the actual current docs, live,
catches that. It matters most exactly where getting it wrong is
expensive -- e.g. not knowing your harness already ships a built-in
capability and reaching for an unnecessary third-party tool with its
own security exposure instead.

**What this builds: AI-engineer fluency, specifically.** Across all
five domains, this is the actual working knowledge of someone building
and operating agentic systems, not an approximation of it: a harness's
real control loop, memory, tools, permissions, and orchestration
mechanics, traced through actual config keys rather than described
abstractly; a 19-item anti-pattern taxonomy for the failures that
"don't crash, they produce plausible wrong output," plus the
load-lifecycle and lockfile/dependency-pinning discipline that
prevents them; building and scoring a RAG evaluation pipeline with
critique-agent filtering and LLM-as-judge comparison; classifying and
choosing a model by parameter scale, MoE architecture, and
quantization scheme for a deployment target; and operating a real
local inference engine. Every capstone is graded on whether the
artifact you produced actually runs and does what you claimed, not on
how well you described it -- that's testing and debugging discipline,
exercised on the actual object of AI engineering. It is not generic
computer science (algorithms, data structures, database design) --
those were never the claim, and this project doesn't need to reach
for them to teach what an AI engineer actually needs. The tier
system's own top-tier note is the one honest ceiling worth stating:
Archon tier is *necessary but not sufficient* for building something
better than what exists -- fluency with the current state of the art
is the floor a real contribution stands on, not the contribution
itself.

**What's still unproven:** the tier rubric and the multi-session
courses under it are original pedagogical design, authored and graded
by the same kind of model that teaches from them -- not a researched
claim about how people learn. It's currently a solo-tested tool: the
person building it is deliberately going through it from the bottom
tier as its first real learner, not a second, independent person. That
makes a tier badge a practice signal you can act on today, not yet an
external credential someone else should take on faith. Separately,
there is no mechanism yet that re-checks a reference page against its
source after it's written -- a page tagged **VERIFIED** was true when
fetched; nothing yet detects if the underlying docs changed since.

---

## ⚡ What it actually does

AIrchon is a conversational mentor, not a wizard with hidden
subcommands -- backed by three specialist agents behind one thin
router. You ask it a real question, in plain language, and it answers
in prose, citing exactly where the answer came from.

- **`airchon-mentor` answers, read-only.** Every factual claim is
  tagged, explicitly or by the shape of the answer: **VERIFIED**
  (fetched this session, or already cited in a reference area, from a
  named source) or **BEST CURRENT UNDERSTANDING, UNCONFIRMED**
  (reasoned, not yet confirmed against a source). The two are never
  blended together. It can also read (never edit) your own project's
  agent-harness setup and advise on guardrails, control flow, or
  performance -- but it never writes to any reference area, even when
  its own live research fills a gap.
- **No authority overreach.** Claude Code, Copilot CLI, and OpenCode
  are different products from different companies. A mechanism
  confirmed for one is never quietly assumed to hold for another --
  every harness gets its own citation.
- **`airchon-author` is the only writer**, across five reference
  areas -- harness internals, Agentic SDLC technique, RAG technique,
  AI model classification, and local inference engines (see the table
  below). One topic file per subject, only built when a real question
  needs it -- never pre-built speculatively. The next question about
  the same topic gets answered from what's already there, faster and
  just as grounded, until something changes underneath it.
- **`airchon-teacher` assesses, then teaches.** A 40-question exam,
  grounded in a curriculum spanning all five reference areas,
  classifies you into one of four tiers -- Slumberer, Gnostic,
  Demiurge, Archon -- and persists the result locally
  (`~/.airchon/level`), never uploaded. Once classified, it walks you
  through the course toward your next tier session by session --
  currently 3 sessions for Slumberer->Gnostic and 68 for
  Gnostic->Demiurge across all five domains, teaching each item to
  completion and grading a real exercise before moving on. See the
  honesty note above on what a tier signals before treating it as more
  than a practice tool -- that's a caveat on the exam's construct
  validity, not on how much the course actually covers.

---

## 🌙 The Learning Path

Four tiers, one arc. The names are borrowed on purpose -- mythic
scaffolding lifted from Gnostic cosmology, purely for the fun of it
and as a memory hook, not a claim about anything outside this project
(see
[reader-proficiency-tiers.md](resources/airchon-teacher/reader-proficiency-tiers.md)
for the full rubric and its own honest ceiling note).

| | Tier | The lore | What's expected of you |
| :---: | :--- | :--- | :--- |
| 🌙 | **Slumberer** | The sleeper who hasn't yet woken up -- doesn't know there's a gate, let alone what's behind it. | You've used an AI coding agent, maybe a lot -- but "the model" and "the harness wrapping it" are still one undifferentiated blur. No vocabulary yet for tool calls, context windows, or hooks. |
| 👁️ | **Gnostic** | The one who has acquired *gnosis* -- direct knowledge, not hearsay about it. | You can describe a harness's control loop and place it on its own axes -- reactive vs. deliberative, single-agent vs. multi-agent -- correctly and unprompted. Still map, not territory. |
| 📐 | **Demiurge** | The craftsman-god who takes received forms and actually shapes matter with them. | The largest transition, 55 modules across five domains: harness power-user depth (trace a request through actual config keys, write hooks and permission rules, compare mechanisms across Claude Code/Copilot CLI/OpenCode) *plus* real RAG pipeline construction, Agentic SDLC practitioner mechanics, AI model classification, and local inference-engine operation (llama.cpp/Ollama/KTransformers) -- each held to its own source's grounding standard, not blended into one undifferentiated claim. |
| 👑 | **Archon** | Mastery over the created order -- authority earned by citation, not gatekeeping. | You can justify what a *new* harness should do instead of only explaining what ships today, and critique this book's own harness design-space surveys *and* the Agentic SDLC Handbook's design-space/methodology chapters as a starting position to argue with, not received fact. Necessary, not sufficient, for actually building one. |

Ask "assess my proficiency" or "take the exam" to find out where you
stand, via a 40-question exam grounded in the reference areas. Once
classified, ask to be taught and `airchon-teacher` runs the course
toward your next tier, session by session.

---

## 🛠️ Where the knowledge actually comes from

| Reference area | Primary sources | Grounding standard |
| :--- | :--- | :--- |
| `references/harnesses/` | `code.claude.com/docs`, `docs.github.com/copilot`, `github.com/anthropics/claude-code`, `github.com/github/copilot-cli`, `github.com/anomalyco/opencode` (+ `opencode.ai/docs`), HuggingFace's agent-engineering courses for general vocabulary | Independently cross-verified per source, tagged VERIFIED / BEST CURRENT UNDERSTANDING |
| `references/sdlc/` | The Agentic SDLC Handbook (Daniel Meppiel) | Attributed "the handbook says" -- single-source, not independently cross-verified |
| `references/rag/` | HuggingFace Cookbook notebooks, Lewis et al. (2020) and related papers | Attributed to the specific notebook or paper |
| `references/models/` | Hugging Face's Hub docs, the `transformers` glossary, the Optimum quantization guide, named community writeups | Attributed to the specific source |
| `references/inference-engines/` | `ktransformers.net/docs`, `docs.ollama.com`, `github.com/ggml-org/llama.cpp` (+ linked subpages) | Attributed to each engine's own docs/repo |

Each row is a bounded claim, not a blanket endorsement -- a source is
only ever cited for what it actually documents, and only
`references/harnesses/` carries this project's own independently
cross-verified VERIFIED tag; the other four attribute claims to their
single named source instead.

---

## 🚀 How to use it

```bash
apm install
```

This deploys all three agents -- `airchon-mentor`, `airchon-author`,
`airchon-teacher` -- to Claude Code, Copilot CLI, and OpenCode, and the
thin router skill (`airchon`) to Claude Code only, for `/airchon` and
natural-language discovery. Skills have no Copilot CLI or OpenCode
deploy path; the agents are what keep both covered either way. **Known
gap:** the OpenCode deploy currently fails to load -- its `tools:`
frontmatter is written as a list, and OpenCode requires a
tool-name-to-boolean mapping instead. `apm install` will warn about
this; it isn't silently broken, but it isn't fixed yet either.

Then just ask it something, for example:

```
/airchon how does Claude Code handle context compaction?
how would I build a multi-agent harness like this one?
what's the actual difference between OpenCode's and Claude Code's tool loop?
walk me through how MCP servers get discovered and invoked
what's the difference between a quantized and a MoE model, for an agent I'm serving locally
how does llama.cpp's KV cache differ from Ollama's default context window
write up KTransformers' operator-injection mechanism in the wiki-book
assess my proficiency / take the exam
teach me / continue my course
review my project's own skills and agent files for guardrail gaps
```

No fixed command set to memorize -- if the question fits one of the
five reference areas, ask it the way you'd ask a person. The two
exceptions are the exam and the course: once you're in either, it
paces one question or one topic at a time, asking whether you want to
continue or pick back up later -- instead of free-form back-and-forth.

---

## 🗺️ Repository layout

```
apm.yml                                        APM project manifest (targets: claude, copilot, opencode)
apm.lock.yaml                                  Resolved/locked dependency versions
.apm/agents/airchon-mentor.agent.md            Read-only mentor -- answers, reviews your project's harness setup
.apm/agents/airchon-author.agent.md            The only writer, across all five reference areas
.apm/agents/airchon-teacher.agent.md           Lean router body for the teacher's own procedures -- read-only on all reference areas
.apm/skills/airchon/SKILL.md                   Thin router skill (Claude Code only)
references/harnesses/                          Wiki-book: AI agent harness internals -- mentor reads, author writes
references/sdlc/                               Agentic SDLC Handbook digest
references/rag/                                RAG definitions and techniques
references/models/                             AI model classification for agentic development
references/inference-engines/                  Local/self-hosted inference engine internals (llama.cpp, Ollama, KTransformers)
resources/airchon-teacher/                     Teacher's own procedures (exam, course delivery, guardrails), the tier rubric,
                                                the curriculum, and the session-pacing files for each course
resources/path-resolution.md                   Shared path-resolution fallback used by all three agents
~/.airchon/level, ~/.airchon/qualify-exam.md,
~/.airchon/course-progress.md, ~/.airchon/exercises/,
~/.airchon/session-{N}.exam.md                 Teacher's own state -- your machine, outside this repo
.claude/, .github/, .opencode/, .agents/       Deployed copies of the agents and skill (gitignored, regenerated by `apm install`)
```

For the full architecture rationale -- why the read/write split, why
the router stays thin, why the teacher's own content lives outside the
reference areas -- see `CLAUDE.md`. Design history and past decisions,
including the honest write-ups of things that turned out wrong or
incomplete along the way, live in `CHANGELOG.md`; this file only ever
describes the present.
