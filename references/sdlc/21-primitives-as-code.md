# Primitives as code

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Part III (For
Practitioners), Ch. 21 --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch21-primitives-as-code.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

## The problem it addresses

Two skills, edited by two teammates three months apart, each carry
their own copy of the team's review checklist. They have drifted. On a
pull request to the payments service, they disagree: `python-review`
says the change is acceptable; `pr-description`, loaded moments later
on the same diff, says it _needs revision_ and lists a different set of
concerns. Nothing in either skill is wrong on its own. What is wrong is
structural: a piece of content that two skills both depend on is
_embedded_ in each, instead of _declared_ by each. There is no single
source of truth for the team's review checklist, even though both
authors believe there is one.

Chapter 12 catalogued seven primitive types and named their load modes.
This chapter is what changes when you stop treating those files as
documents and start treating them as packages.

## From file to package

The mental model Chapter 12 establishes is one primitive, one file.
That model is correct for the smallest useful primitives. It stops
being sufficient the moment a primitive needs more than its body to do
its job — when a code-review skill needs example diffs, when a
security-audit skill needs a checklist that another skill also wants,
when an orchestration spec needs a sub-step authored by a different
team.

The unit that handles those needs is the **package**. A skill is the
runtime's analogue of a Module / Facade (Ch. 19): one named
entrypoint, one stable description, hidden internal structure. A
bundle — a skill that contains other skills or carries asset files
alongside its body — is the runtime's Composite. A dependency edge
from one skill to another is a Package Reference, the same shape npm
and Maven settled on three decades ago.

> **Author disclosure on tooling.** This chapter uses
> [APM](https://github.com/microsoft/apm) (`apm.yml`, `apm install`,
> `apm.lock.yaml`) as its reference implementation. APM is one of
> several efforts working the same ground — GitHub's Spec-Kit and the
> Squad CLI are two others worth tracking — and the package-management
> _discipline_ this chapter argues for is not specific to any of them.
> Read every `apm install` below as "your team's package-manager
> equivalent." The mechanics port; the file paths do not.

## Modules over monoliths

A `SKILL.md` body that crosses a few hundred lines is almost always a
hint that the primitive has accreted concerns that should belong to
neighbours. The same instinct that makes a senior engineer extract a
function from a 400-line method applies here; the test is the same:
_does this section have its own reason to change?_ If yes, it wants to
be its own primitive.

| Artifact | Role | Visibility |
|---|---|---|
| `SKILL.md` (entrypoint) | Description-driven activation contract; the body the agent reads when the skill binds | Public. The `description` is the API. |
| `assets/` | Reference material the body cites — example diffs, decision tables, checklists too long to inline | Loaded transitively when the body links them |
| Sub-skills | A child `SKILL.md` under the same bundle directory, activated independently or via a parent reference | Public if the parent re-exports; private otherwise |
| `apm.yml` (or equivalent) | Declared dependencies, version, license, ownership | Public. Drives the lockfile. |
| Tests | Activation tests, link-integrity checks, schema validation against the manifest | Internal to the package; CI gate |

Two principles hold across the table. First, the entrypoint is
_small_: a skill body that lists every consideration the team has ever
cared about is a monolith; the same skill that names two or three
load-bearing decision rules and links to assets for the rest is a
module. Second, the content a skill _imports_ is named, not pasted.

## Separation of concerns, by dependency

The fix for the drifted checklists: extract the duplicated content into
a new skill, `code-review-rubric`, with its own `SKILL.md` and its
own version history. Both `python-review` and `pr-description` declare
a dependency on it in their manifests:

```yaml
# .github/skills/python-review/apm.yml
name: python-review
version: 1.4.0
dependencies:
  apm:
    - org/code-review-rubric#v1.2
    - org/style-guide-python#v2.0
```

The body of `python-review/SKILL.md` no longer contains the checklist.
It points at the dependency: _apply the rubric in `code-review-rubric`,
then add the Python-specific concerns below._ One source of truth; two
consumers; zero drift. The cost is one new package and two manifest
edits. The benefit is structural: the team's checklist now has the same
status as any other piece of code they ship — one owner, one history,
one place to land a change.

Two kinds of duplication: **coincidental** overlap (two unrelated skills
that happen to use a similar phrase) is fine; it carries no expectation
of synchronization. **Essential** overlap (content that is supposed to
be the same in both places because the team has one position on it) is
not. The cure for essential overlap is always the same: extract a
package, declare a dependency, delete the copy.

## The lockfile and what it pins

A dependency declaration is an intent (_I want the rubric, version
1.2_). A lockfile is a fact (_on the date of this install, the rubric
resolved to commit `9d10…`, content hash `sha256:9d10…`, fetched from
this source URL_). The two are different and both are necessary, for
the same reasons npm's `package.json` and `package-lock.json` are
different.

| | Manifest | Lockfile |
|---|---|---|
| Records | What the project depends on, by version range | What was actually resolved on a given date, by content hash |
| Edited by | Humans, on every dependency change | The CLI, on every install |
| Answers | "What does this project want?" | "What did this project see, last time it built?" |
| Breaks if | A consumer adds an undeclared dependency | A resolved file is republished under the same version with different content |

The lockfile is what makes a primitive set _reproducible_ across
machines and across time. Without it, last week's `apm install` and
this week's `apm install` will produce different agent behavior on the
same project — different transitive closure, different content,
different output — with no diff on the consumer's branch to point at.
The wave protocol (Ch. 17) depends on this kind of reproducibility: a
wave's verdict is honest only if the next wave can be re-run against an
identical context.

A second function: every resolved entry carries a content hash.
Republishing a tag with different content is a supply-chain attack; the
lockfile is the local check that catches it. Pinning is therefore not
bureaucracy — it is the only mechanism by which the transitive closure
of a primitive is observable, diff-able, and reviewable.

## Overrides without forking

The cleanest way to compose a dependency is to use it unchanged. The
next-cleanest way is to override one named section without taking
ownership of the rest (Template Method from Ch. 19): the base module
defines an invariant skeleton with named slots; a consumer replaces a
slot in their own project without rewriting the skeleton.

Two practical disciplines make overrides safe to live with.

**Slot stability.** The names of overrideable sections are part of the
skill's public contract. Renaming `Style guide` to `Style conventions`
in a minor version is a breaking change for every downstream override
that points at the old name. The same engineering caution that applies
to renaming a public function applies here.

**The override is the smallest unit you own.** A consumer who finds
themselves overriding three slots, then four, then six, has crossed the
threshold where forking the dependency is more honest. When most of the
module is local, the dependency edge is no longer paying for itself.

Override is what lets the payments team use `code-review-rubric` as it
ships from the central platform team while still reflecting the
payments-team house style on the one section where the two genuinely
differ. Without overrides, the choice is binary — adopt the upstream
rubric in full, or fork it and inherit nothing future.

## Versioning: the description is the API

The public surface of a skill is the description in the `SKILL.md`
frontmatter, plus any slot names a consumer might override. The body of
the skill is implementation; the description is the API. This is not a
rhetorical flourish: the description is exactly what the harness reads
when deciding whether to activate the skill on a given task. A consumer
who installs the skill is buying that activation contract.

| Change | Bump | Why |
|---|---|---|
| Edit the body without changing the description or slot names | Patch | Safe by construction |
| Add a new slot or new asset; existing consumers unaffected | Minor | Strictly additive |
| Reword the description's activation criteria | Major | Bindings shift; consumers must re-evaluate |
| Rename or remove an overrideable slot | Major | Existing overrides break |
| Change a transitive dependency's resolved version | Reflected in the lockfile, not the package version | The package version describes _this_ package; the lockfile describes the closure |

The last row is the one teams get wrong most often. When
`code-review-rubric@v1.2` depends on `style-guide-python@v2.0` and
the style guide ships a breaking v3.0, the rubric's published version
does not change — _because the rubric did not change_. What changes is
the lockfile of any project that re-runs `apm install`. This separation
of concerns — package versioning describes the package; lockfile
snapshotting describes the closure — is what keeps the system tractable
as the dependency tree grows.

## A walkthrough: from one file to one package

The full lifecycle for `code-review-rubric`, from extraction to
consumption and audit:

1. **Single file.** The rubric lives inline in `python-review/SKILL.md`.
   It is a heading and forty lines.
2. **Extracted bundle.** The platform team creates
   `org/code-review-rubric/`. Inside: a `SKILL.md` with description
   and body factored into named slots; an `assets/` directory with
   `examples/good-vs-bad.md`; an `apm.yml` declaring `version: 1.0.0`,
   no further dependencies, MIT license, the platform team as owner.
3. **Published.** The bundle is tagged `v1.0.0`. The publish workflow
   runs schema validation, link-integrity on the body, and an
   activation test that loads the description into a sandboxed harness
   and checks it activates on a synthetic review task.
4. **Consumed.** A maintainer edits `python-review`'s `apm.yml` to
   add `org/code-review-rubric#v1.0.0` to its dependencies. `apm
   install` resolves the dependency, downloads the bundle, writes a
   content hash into `apm.lock.yaml`, and stages the rubric's files.
5. **Overridden.** A second team adopts `python-review` but has its
   own house style. They add an override file replacing the rubric's
   _Style guide_ slot with their own. The rest flows through unchanged.
6. **Iterated.** A postmortem motivates a sharper rubric line. The
   owner edits `code-review-rubric/SKILL.md`, bumps to `v1.0.1`,
   publishes. Both consuming projects pick it up on the next install.
   No drift.
7. **Audited.** An enterprise security review asks: _which version of
   the rubric was loaded into the agent that approved PR #4711?_ The
   answer is one lockfile lookup against the commit on which the PR was
   approved. The closure is reconstructible.

Step 7 is what turns the package layer from an aesthetic choice into a
governance one. Reproducibility, integrity, and provenance are the same
property viewed from three angles — and all three are properties of the
lockfile. A team that runs primitives without a manifest and a lockfile
cannot answer step 7 honestly. A team that runs them with both can —
which is, ultimately, what _primitives as code_ means.

## Three concerns when authoring a skill

Chapter 6 names three roles at the team level: **Domain Specialist**,
**Agentic Workflow Engineer**, **Agent Operations Specialist**. The
same triplet appears one zoom level down when a single skill is being
authored. Each role owns one of three concerns:

| Concern | Owner | Question it answers |
|---|---|---|
| **WHAT the skill encodes** | Domain Specialist (SME / Domain Owner) | "When this skill runs to completion, what observable outcome counts as a pass?" |
| **HOW the skill composes** | Agentic Workflow Engineer | "Given the WHAT, which personas does this skill dispatch in which order, and what is the bound on the dispatch tree?" |
| **OPERATIONS once the skill runs** | Agent Operations Specialist | "What telemetry tells us it is still doing the WHAT, within budget?" |

Two notes. **The roles are concerns, not headcount.** In a small team
one engineer wears all three hats; the value of the triplet is that
each concern is _named_, so the reviewer knows which question to ask
first. **The triplet is recursive across the dispatch tree.** A skill
that dispatches personas inherits the triplet for each dispatched unit;
the parent skill's recursion bound (the HOW concern) caps the depth at
which this recursion terminates.

The package layer and the triplet are complementary. The package layer
is what makes a skill _shippable, reproducible, and auditable_. The
triplet is what makes it _correct, composable, and operable_. A skill
that satisfies one without the other is the failure mode this chapter
exists to prevent.

## TL;DR

1. **A skill is a module, not a file.** Entrypoint + body + assets +
   manifest. The Module / Facade pattern from Ch. 19, made concrete on
   disk.
2. **Don't duplicate; declare.** When two skills share content, extract
   a third skill they both depend on. Essential overlap is a missing
   dependency edge.
3. **Manifest declares intent; lockfile records fact.** The lockfile
   pins the transitive closure with content hashes. Without it, agent
   behavior is not reproducible across machines or weeks.
4. **The description is the API.** Rewording the activation contract is
   a breaking change. So is renaming an overrideable slot. Bump major;
   ship a release note.
5. **Override before forking.** Specialize one slot; inherit the rest.
   When most of the module is local, the dependency is no longer paying
   for itself.
