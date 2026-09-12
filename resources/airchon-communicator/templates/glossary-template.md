# Glossary Template -- The Road to Agentic Archon

Use for `/book/glossary.md`. One entry per term the book uses that a newcomer would need. Bidirectional links are mandatory.

```markdown
# Glossary

> Every term introduced in a chapter links here; every entry links back to the chapter that defines it.

## A

### {{term}} {#term-slug}

**One-line plain-language definition (Beck/Fowler), then one paragraph mechanism.**

- **See also:** [Ch. {{N}} -- {{Title}}](chapters/{{NN}}-{{slug}}.md), [Ch. {{M}} -- ...]
- **Source:** `references/harnesses/{{topic}}.md` -- § source section (VERIFIED).
- **Aliases:** {{alternative names if wiki uses more than one}}

## B
...

## Index back to chapters

- Glossary -> chapter backlinks must resolve. No orphan terms. Linter checks: every `glossary.md#{{term}}` anchor has a chapter that links to it, and every chapter's `Glossary: [terms]` footer has matching entries here.
```
