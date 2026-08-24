# Case study: the publishing pipeline

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Part IV case study --
https://danielmeppiel.github.io/agentic-sdlc-handbook/case-study-publishing-pipeline.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

A worked example of the book's technical patterns applied to
converting the handbook itself -- a 15-chapter Markdown manuscript --
into a multi-format publishing pipeline (HTML, PDF, EPUB) with
automated CI/CD, run as "multiple waves within a single extended
session."

## The problem

Turn a plain Markdown manuscript into a deployable, multi-format book
without losing structure (37 Mermaid diagrams, 15 chapters) or
introducing brittle, hand-maintained build steps. The task split
cleanly into two kinds of decision: publishing *strategy* (licensing,
platform, pricing model) and *technical execution* (conversion,
rendering, CI/CD) -- and the case study treats that split as the
throughline: "Every design decision was human; every technical
execution was agent -- that division held throughout."

## Agentic techniques applied

**Multi-round deliberation with human veto.** The orchestrator's
first recommendation was an Open Core model (free web, paid
PDF/EPUB). The author pushed back, so a research agent investigated
Quarto, Leanpub, GitBook, and mdBook as alternatives; the final
recommendation was **Quarto + GitHub Pages**, "the pattern used by *R
for Data Science* and *Python for Data Analysis*." A separate
three-expert panel (IP Attorney, Publishing Strategist, Growth
Hacker) unanimously recommended a **CC BY-NC-ND 4.0** licence, on the
reasoning that it "invites sharing (reach), requires attribution
(authorship), prohibits commercial use (author's brand), prohibits
derivatives (one canonical version)."

**Single-wave bulk conversion.** "A single general-purpose agent
converted the entire manuscript in one wave": it created `_quarto.yml`
with a four-part book structure, converted 15 `.md` files to `.qmd`
via `git mv`, added YAML frontmatter, wrote an `index.qmd` reading
guide, and created `.github/workflows/publish.yml` for CI deployment.

**Checkpoint-per-fix discipline on the rendering cascade.** PDF
rendering broke in five sequential ways, each only visible once the
previous one was fixed -- named as **Anti-Pattern #15, "The 'Almost
Done' Trap"**, and tied back to **Anti-pattern #10, "Not Fixing the
Primitives"**. The prescribed discipline: "Treat each fix as its own
micro-wave with a checkpoint... This prevents speculative batching --
fixing three things at once when you don't yet know if fix #1 changes
the landscape for fixes #2 and #3." The five fixes, in order:

1. Switched document class from `scrbook` to `scrreprt` with explicit
   geometry (25mm left/right, 30mm top/bottom margins).
2. Converted GitHub-flavoured ` ```mermaid ` fences to the
   ` ```{mermaid} ` syntax Quarto's PDF renderer requires.
3. Stripped manually-typed chapter numbers from 25 headings across
   two chapters (they duplicated Quarto's auto-numbering).
4. Added `fig-width: 6.5`, `code-overflow: wrap`, and the LaTeX
   packages `fvextra` (code overflow) and `float` (figure placement).
5. Converted a table to a proper 9-column Markdown pipe table.

**Environment-split CI/CD architecture.** Four iterations were needed
before the pipeline was stable, each fixing a distinct failure:

| Iteration | Failure | Fix |
|---|---|---|
| 1 | Headless-Chromium Mermaid→PNG rendering hung in CI | Added `quarto install chromium --no-prompt` |
| 2 | Custom LaTeX packages (DejaVu fonts, `fvextra`) hung CI | Simplified PDF config, removed custom fonts |
| 3 | `render: "html"` parameter behaved wrong | Split into explicit `quarto render --to html` then `quarto publish` with `render: false` |
| 4 | HTML-only deploy overwrote PDF/EPUB already on `gh-pages` | Added a "Restore PDF and EPUB from gh-pages" step using `git show` |

The pipeline settled into two deliberately different paths: **CI
(49 seconds)** -- checkout, install Quarto, `render --to html`,
restore PDF/EPUB from `gh-pages`, `publish --no-render`; and **local
render (~15 minutes)** -- render to PDF, save it, render to EPUB, save
it, render to HTML, copy PDF+EPUB into `_book/`, then
`publish --no-render`. Rationale: "CI optimises for speed (HTML-only,
49 seconds), local optimises for completeness (all formats)... the
15-minute local render is a practical constraint -- Chromium-based
Mermaid rendering is too heavy for a fast CI feedback loop."

**Iterative UX refinement.** The download experience went through
seven iterations, each following the same human/agent split: "the
human spotted a UX friction, the agent fixed it in under a minute."

## Concrete numbers

| Metric | Value |
|---|---|
| Output formats | 3 (HTML, PDF, EPUB) |
| Source files converted | 15 `.md` → `.qmd` |
| Mermaid diagrams rendered | 37 (25 confirmed in the initial HTML pass) |
| Initial HTML render | 16 files, zero errors |
| PDF rendering fixes (cascade) | 5, applied one at a time |
| CI/CD iterations to stability | 4 |
| Download-UX iterations | 7 |
| Licensing expert-panel size | 3 (IP Attorney, Publishing Strategist, Growth Hacker) |
| PDF size growth | 686KB -> 3.8MB as diagram PNGs were rendered in |
| CI deploy time | 49 seconds |
| Local full-format render time | ~15 minutes |
| Book structure | 4 parts (Foundation, Leaders, Practitioners, Closing) |

## Lessons learned

- **Every design decision was human; every technical execution was
  agent -- that division held throughout the project**, from
  publishing-platform choice down to licence selection.
- **The "Almost Done" Trap (Anti-Pattern #15):** "Each fix revealed
  the next issue, creating a cascade where 'one more fix' repeated
  five times." Fix one thing per micro-wave, with its own checkpoint,
  rather than batching speculative fixes together.
- **Human judgment remains the bottleneck and differentiator:** "The
  agents surfaced options and trade-offs; the human chose the
  publishing philosophy."
- **Optimise CI and local builds for different goals rather than
  forcing one pipeline to serve both** -- speed in CI, completeness
  locally.
- **Checkpoint discipline generalises beyond code:** "The structural
  properties from the APM Overhaul held... checkpoint discipline
  prevents compounding rendering failures as effectively as it
  prevents compounding code failures."

## Source

Part IV case study, **The Agentic SDLC Handbook** by Daniel Meppiel --
https://danielmeppiel.github.io/agentic-sdlc-handbook/case-study-publishing-pipeline.html
