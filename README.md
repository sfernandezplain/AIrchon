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

AIrchon does not write your code for you, and it does not audit your
project. It exists for one purpose: to turn you into someone who
understands how the machine you're standing on actually works.

---

## ⚡ What it actually does

AIrchon is a conversational mentor, not a wizard with hidden
subcommands. You ask it a real question about harness internals, in
plain language, and it answers in prose -- citing exactly where the
answer came from.

- **Grounding discipline.** Every factual claim is tagged, explicitly
  or by the shape of the answer: **VERIFIED** (fetched this session,
  or already cited in the wiki-book, from a named source) or **BEST
  CURRENT UNDERSTANDING, UNCONFIRMED** (reasoned, not yet confirmed
  against a source). The two are never blended together.
- **No authority overreach.** Claude Code, Copilot CLI, and OpenCode
  are different products from different companies. A mechanism
  confirmed for one is never quietly assumed to hold for another --
  every harness gets its own citation.
- **A growing wiki-book.** Answers get written down at
  `references/harnesses/`, one topic file per subject, only built
  when a real question needs it -- never pre-built speculatively. The
  next question about the same topic gets answered from what's
  already there, faster and just as grounded.

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

This deploys the mentor agent (`airchon-mentor`) to both Claude Code
and Copilot CLI, and a thin router skill (`airchon`) to Claude Code
for `/airchon` and natural-language discovery.

Then just ask it something, for example:

```
/airchon how does Claude Code handle context compaction?
how would I build a multi-agent harness like this one?
what's the actual difference between OpenCode's and Claude Code's tool loop?
walk me through how MCP servers get discovered and invoked
```

No fixed command set to memorize -- if the question is about harness
internals, ask it the way you'd ask a person.

---

## 🗺️ Repository layout

```
apm.yml                              APM project manifest
apm.lock.yaml                        Resolved/locked dependency versions
.apm/agents/airchon-mentor.agent.md  The mentor agent -- does the real work
.apm/skills/airchon/SKILL.md         The thin router skill
references/harnesses/                The wiki-book airchon-mentor writes/reads
.claude/agents/, .github/agents/     Deployed copies of the agent (gitignored)
.claude/skills/airchon/              Deployed copy of the router skill (gitignored)
```

---

## Provenance

AIrchon began as `xray-mentor`, the 11th agent in the
[AgentXRay](https://github.com/sfernandezplain/AgentXRay) project, and
was split into its own repo once its scope -- mentoring on harness
internals generally -- outgrew xray's own mission of profiling a
single agent execution. Full history lives in `CHANGELOG.md`; this
file only ever describes the present.
