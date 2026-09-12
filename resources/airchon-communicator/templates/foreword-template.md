# Foreword Template -- The Road to Agentic Archon

Use for `/book/foreword.md`.

```markdown
# Foreword -- The Road to Agentic Archon

## Who this book is for

One paragraph per tier (Slumberer -> Gnostic -> Demiurge -> Archon) in the voice of Beck/Fowler: what each reader already knows and what this book will give them next. Inherit tier names from `resources/airchon-teacher/reader-proficiency-tiers.md`; do not rename them.

## How to read this book

- Front-to-back in `index.md` order is the designed path. Prerequisites are explicit per chapter; skipping breaks them.
- Harness-by-harness pages (`harnesses/*.md`) are reference after the general-concept chapters -- read the general chapter first, then the harness synthesis for that harness.
- Glossary is last for a reason. Terms are introduced where they are first needed and linked there.

## Voice and conventions

- **Beck/Fowler prose:** concrete first, abstraction after; smallest example before mechanism; no jargon without a glossary link.
- **Mermaid legend:** `flowchart` = structure, `sequenceDiagram` = flow/turns, `stateDiagram-v2` = states. Every diagram sits above the prose it illustrates.
- **Grounding tags:** VERIFIED vs BEST CURRENT UNDERSTANDING inherited from the wiki; citations name the wiki source page (`references/...`), not pretraining.

## What this book is, and what the wiki is for

The wiki (`references/**`) is the verified research shelf, written LAZY as questions arose. The book is the ordered, distilled, pedagogical counterpart. The wiki remains canonical for source truth; the book is canonical for learning order. When a chapter cites `references/...`, it means that wiki page's own sources were already fetched and cited -- this book does not re-cite them from pretraining.

## Navigation

- Index: [index.md](index.md) -> Ch.01 -> ... -> Glossary
- Every chapter footer: `Prev | Index | Next | Glossary` -- all links must resolve (S4 gate).
```
