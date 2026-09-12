# Index Template -- The Road to Agentic Archon

Use for `/book/index.md`.

```markdown
# The Road to Agentic Archon -- Index

**One paragraph:** what this book is (ordered, distilled, easy-language version of the wiki), who it is for (Slumberer -> Archon progression), and how to read it (front-to-back in order; harness synthesis pages may be read as reference).

## Reading order -- the knowledge tree

| Ch. | Title | File | Prerequisites | Next | Mermaid | Sources |
|-----|-------|------|---------------|------|---------|---------|
| 0 | Foreword | foreword.md | -- | 01-... | -- | -- |
| 1 | {{Title}} | chapters/01-{{slug}}.md | -- | 02-... | flowchart | `references/harnesses/{{topic}}.md` |
| 2 | {{Title}} | chapters/02-... | 01 | 03-... | sequence | `...` |
| N | Glossary | glossary.md | all | -- | -- | all chapters |

- Every row's `File` link resolves. `Next` forms a single chain: `index -> ch.01 -> ch.02 -> ... -> glossary`.
- No chapter is orphaned. No `Next` dangles.

## How chapters, harness pages, and the glossary link

- Index -> chapter -> next page.
- Glossary terms are first introduced in a chapter with a link to `glossary.md#term`; each glossary entry links back to defining/using chapters.
- Harness-by-harness pages (`harnesses/*.md`) are reachable from the final general-concept chapters and from the index footer.

## Numbering contract

Chapters are `01` .. `NN` zero-padded two digits. Foreword is `00` conceptually but lives as `foreword.md` outside the numbered sequence. Glossary is last.
```
