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
guarding it. Sovereign not because it withholds the source, but
because it always names one.

That inversion is the axiom the whole project stands on: **true
intelligence is not a proprietary privilege, it is a universal
birthright.** Every claim AIrchon makes is traceable back to a name, a
document, a repository -- authority earned by citation, never by
gatekeeping. The name is the motto, compressed to one word.

---

## 👑 The Manifesto

AIrchon was born from a refusal to accept shallow docs, walled
gardens, and hype-driven gatekeeping. Every harness worth understanding
-- Claude Code, GitHub Copilot CLI, OpenCode -- hides its real
behavior behind marketing copy and scattered blog posts. AIrchon
refuses to guess. It goes to the actual docs, the actual changelogs,
the actual open-source code, fetches them live, and only then speaks.

It does not free-associate from training data and call that
knowledge. If it hasn't fetched a source *this conversation* -- or the
wiki-book hasn't already fetched and cited it -- it will tell you
plainly that what it's about to say is reasoned, not verified. That
distinction is the whole point. True understanding isn't a vibe; it's
a claim you can trace back to a named source.

AIrchon does not write your code for you, and it does not run a
formal audit process on your project -- that discipline (diagrams,
severity findings, a persisted redesign plan) belongs to a separate
tool, `genesis`. What it will do, on request, is read (never edit)
your own project's agent-harness setup -- skills, agent/persona
files, hooks, permission and sandboxing config, orchestration
definitions -- and advise on guardrails, control flow, or performance
against the same sourced corpus it mentors from. Either way its
purpose stays singular: to turn you into someone who understands how
the machine you're standing on actually works, not to do the work
for you.

---

## ⚡ What it actually does

AIrchon is a conversational mentor, not a wizard with hidden
subcommands -- backed by three specialist agents behind one thin
router. You ask it a real question about harness internals, in plain
language, and it answers in prose -- citing exactly where the answer
came from.

- **`airchon-mentor` answers, read-only.** Every factual claim is
  tagged, explicitly or by the shape of the answer: **VERIFIED**
  (fetched this session, or already cited in the wiki-book, from a
  named source) or **BEST CURRENT UNDERSTANDING, UNCONFIRMED**
  (reasoned, not yet confirmed against a source). The two are never
  blended together. It can also read (never edit) your own project's
  agent-harness setup and advise on guardrails, control flow, or
  performance -- but it never writes to the wiki-book, even when its
  own live research fills a gap.
- **No authority overreach.** Claude Code, Copilot CLI, and OpenCode
  are different products from different companies. A mechanism
  confirmed for one is never quietly assumed to hold for another --
  every harness gets its own citation.
- **`airchon-author` is the only writer.** Answers worth keeping get
  written down at `references/harnesses/`, one topic file per subject,
  only built when a real question needs it -- never pre-built
  speculatively. The next question about the same topic gets answered
  from what's already there, faster and just as grounded.
- **`airchon-teacher` assesses proficiency.** A 40-question exam,
  grounded in the wiki-book's own curriculum, classifies you into one
  of four tiers -- Slumberer, Gnostic, Demiurge, Archon -- and
  persists the result locally (`~/.airchon/level`), never uploaded and
  never a substitute for actually reading the material.

---

## 🌙 The Learning Path

Four tiers, one arc: from not knowing you're asleep, to holding the
crown. The names are borrowed on purpose -- mythic scaffolding lifted
from Gnostic cosmology, purely for the fun of it and as a memory hook,
not a claim about anything outside this project (see
[reader-proficiency-tiers.md](references/harnesses/reader-proficiency-tiers.md)
for the fine print on that distinction).

| | Tier | The lore | What's expected of you |
| :---: | :--- | :--- | :--- |
| 🌙 | **Slumberer** | The sleeper who hasn't yet woken up -- doesn't know there's a gate, let alone what's behind it. | You've used an AI coding agent, maybe a lot -- but "the model" and "the harness wrapping it" are still one undifferentiated blur. No vocabulary yet for tool calls, context windows, or hooks; a surprise gets fixed by re-phrasing the prompt, not by a hypothesis about which mechanism caused it. Nothing to read yet -- waking up *is* the first assignment. |
| 👁️ | **Gnostic** | The one who has acquired *gnosis* -- direct knowledge, not hearsay about it. | You can describe a harness's control loop (Thought → Action → Observation) and place it on its own axes -- reactive vs. deliberative, single-agent vs. multi-agent, tool-augmented vs. fully autonomous -- correctly and unprompted. Still map, not territory: you haven't yet traced any of it through one real harness's actual documented machinery. |
| 📐 | **Demiurge** | The craftsman-god who takes received forms and actually shapes matter with them -- doesn't invent the blueprint, but nothing gets built without someone doing this. | You operate real harnesses at power-user depth: trace a concrete request through actual config keys, file paths, and documented limits; write hooks and permission rules and know why an approval prompt did or didn't fire; compare the same mechanism across harnesses and say precisely where they converge or diverge. |
| 👑 | **Archon** | The ruling power with mastery over the created order -- the same inversion the project's own name makes: authority earned by citation, not by gatekeeping. | You don't just explain what ships today -- you can justify what a *new* harness should do instead, including where no shipped harness has a settled answer yet. You read this book's own design-space surveys critically, as a starting position to argue with, not as received fact. |

Ask "assess my proficiency" or "take the exam" any time to find out
where you actually stand, via a 40-question exam grounded in the same
wiki-book -- not where the vibe says you stand. The full rubric,
reading lists per tier, and this book's own honest ceiling note (it's
necessary but not sufficient at Archon tier) live at
[reader-proficiency-tiers.md](references/harnesses/reader-proficiency-tiers.md).

---

## 🛠️ Where the knowledge actually comes from

| Source | What it's authoritative for |
| :--- | :--- |
| `code.claude.com/docs`, `docs.github.com/copilot` | Documented behavior, configuration, tool names, hooks, MCP support for each product |
| `github.com/anthropics/claude-code`, `github.com/github/copilot-cli` | Real CHANGELOG history, README, examples, issues -- **not** implementation source; neither repo ships one |
| `github.com/anomalyco/opencode` (`dev` branch) + `opencode.ai/docs` | Documented behavior **and** real, genuinely open-source implementation |
| `huggingface.co/learn/agents-course`, `.../context-course` | General, framework-agnostic agent-engineering concepts and vocabulary -- never a substitute for a harness's own citation |

Each row is a bounded claim, not a blanket endorsement -- a source is
only ever cited for what it actually documents.

---

## 🚀 How to use it

```bash
apm install
```

This deploys all three agents -- `airchon-mentor`, `airchon-author`,
`airchon-teacher` -- to both Claude Code and Copilot CLI, and the thin
router skill (`airchon`) to Claude Code only, for `/airchon` and
natural-language discovery. Skills have no Copilot CLI deploy path;
the agents are what keep Copilot covered either way.

Then just ask it something, for example:

```
/airchon how does Claude Code handle context compaction?
how would I build a multi-agent harness like this one?
what's the actual difference between OpenCode's and Claude Code's tool loop?
walk me through how MCP servers get discovered and invoked
write up OpenCode's permission model in the wiki-book
assess my proficiency / take the exam
review my project's own skills and agent files for guardrail gaps
```

No fixed command set to memorize -- if the question is about harness
internals, ask it the way you'd ask a person. The one exception is
taking the exam: once you're in it, it paces one question at a time
instead of free-form back-and-forth, since that's a real assessment,
not a chat.

---

## 🗺️ Repository layout

```
apm.yml                                        APM project manifest
apm.lock.yaml                                  Resolved/locked dependency versions
.apm/agents/airchon-mentor.agent.md            Read-only mentor -- answers, reviews your project's harness setup
.apm/agents/airchon-author.agent.md            The only writer to the wiki-book
.apm/agents/airchon-teacher.agent.md           Read-only proficiency-exam administrator
resources/airchon-teacher/                     Teacher's own tier-domain content -- not the wiki-book
.apm/skills/airchon/SKILL.md                   Thin router skill (Claude Code only)
references/harnesses/                          The wiki-book -- mentor reads, author writes
~/.airchon/level, ~/.airchon/qualify-exam.md   Teacher's own state -- your machine, outside this repo
.claude/agents/, .github/agents/               Deployed copies of the three agents (gitignored)
.claude/skills/airchon/, .agents/skills/airchon/   Deployed copies of the router skill (gitignored)
```

For the full architecture rationale -- why the read/write split, why
the router stays thin, why the teacher's own content lives outside
the wiki-book -- see `CLAUDE.md`.

---

## Provenance

AIrchon began as `xray-mentor`, the 11th agent in the
[AgentXRay](https://github.com/sfernandezplain/AgentXRay) project, and
was split into its own repo once its scope -- mentoring on harness
internals generally -- outgrew xray's own mission of profiling a
single agent execution. It grew from that one read-only mentor into
the current three-agent, one-router shape: mentor stayed read-only,
`airchon-author` took over writing to the wiki-book, and
`airchon-teacher` was added for proficiency assessment. Full history
lives in `CHANGELOG.md`; this file only ever describes the present.
