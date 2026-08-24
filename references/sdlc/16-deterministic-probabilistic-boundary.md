# The deterministic/probabilistic boundary

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Ch. 16 --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch16-deterministic-probabilistic-boundary.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

The chapter's opening example: an agent fabricates a customer name and
creates a GitHub issue with no validation gate in front of it, causing
production impact because there was "no place in the system where a
deterministic process could have said *no*." The chapter's thesis:
"The placement of the seam -- not the choice of model, not the size of
the context window, not the elegance of the prompt -- is the single
most important architectural decision in any agentic design."

## Two computers, one program

The chapter frames an agentic system as two machines with different
failure ergonomics, not one unified system:

**The deterministic computer** -- "the machine you already know how to
program. It executes the harness, runs the test suite, applies the
lockfile, calls the GitHub API, writes to the filesystem, emits the
audit trail. Given the same inputs it produces the same outputs. When
it fails it fails loudly: a non-zero exit code, an exception, a schema
violation, a CI red light."

**The probabilistic computer** -- "the model. It takes a prompt and
emits a sample from a distribution. Given the same inputs it produces
*similar* outputs, not identical ones. When it fails it fails quietly:
confident, plausible, wrong."

**The seam** is the boundary between them, where controlled data
exchange happens: the probabilistic side may only *propose* actions;
the deterministic side *executes* them under declared policy. Core
operational rule: "the model proposes; the gate disposes."

## Consequential side effects belong on the deterministic side

Anything with real-world consequence -- a write, a spend, an
externally visible action -- must sit behind the deterministic seam,
not inside the probabilistic side. The chapter distinguishes two
supervision strengths:

- **Strong-form supervised execution** -- "the substrate denies the
  write capability to the agent. The agent emits buffered outputs; a
  deterministic post-stage applies them under filters the agent cannot
  bypass."
- **Weak-form supervised execution** -- "the prompt tells the agent to
  plan, then call a tool, then verify, and the agent is asked to
  comply. It is adequate for inner-loop work on a developer's laptop,
  where the operator is the auditor and a misstep is recoverable."

Rule of preference: "When the client offers strong-form, use it.
Weak-form is a fallback for environments without runtime
capability-based security, not a stylistic alternative." An agent that
calls the `gh` CLI to comment on a PR from inside a `gh-aw` workflow
that already offers a `safe-outputs:` block is "leaving substrate-level
safety on the table" by choosing weak-form when strong-form was
available.

### Named substrate patterns implementing the seam

- **The safe-outputs block** (GitHub Agentic Workflows) -- "the
  `safe-outputs:` block declares ahead of time the only kinds of side
  effect this workflow may produce: *create-issue*, *add-issue-comment*,
  *create-pull-request*, each with a typed schema and an optional
  allowlist for labels, target repositories, and issue assignees. The
  agent emits a JSON artifact during its run; it never holds a token
  that can call the GitHub API directly. When the agent finishes, a
  deterministic post-stage reads the artifact, validates each entry
  against its declared schema, applies the allowlist filter, and only
  then calls the API."
- **CI Lambda gating** -- "the agent runs in a sandboxed CI job. Its
  tool surface is restricted to a narrow set of read-only commands
  plus a single `propose-change` command that writes to a buffered
  artifact. After the agent exits, a separate Lambda function --
  running with a different IAM role -- reads the artifact, validates
  it, and applies the change against the system of record. The
  agent's role has no write permissions. The Lambda's role does."
- **Buildkite job-level secrets** -- "the agent runs in a job that has
  no access to the production deploy secret. It produces a pipeline
  manifest. A second job, pipeline-triggered and gated on a passing
  schema check, holds the secret and applies the manifest."
- **Argo Workflow with manual approval** -- "the agent's step in the
  DAG is `propose-manifest`. The next step is a `Suspend` template
  that waits for human approval; only the resumption transitions into
  the deterministic `apply-manifest` step. The seam here is reified as
  a node in the DAG, not as a buffer between processes."
- **Temporal workflow with schema-checked activities** -- "the agent
  participates as a workflow step that returns a typed result.
  Activities -- the things that have side effects -- are separately
  registered, separately versioned, and called by the workflow only
  when the agent's typed result satisfies the activity's input schema.
  Replay-determinism is the substrate property that makes the seam
  auditable."

### The seam in operation (diagram)

The chapter includes a flowchart of the deterministic post-stage: the
model emits a structured proposal -> schema validation (valid/invalid
branches) -> allowlist filter (allowed/denied branches) -> audit log
-> side effect applied (only on the valid-and-allowed path); the
invalid or denied paths reject and surface instead. The agent never
holds the externalization capability at any point in this flow.

## Property comparison: deterministic side vs. probabilistic side

| Property | Deterministic side | Probabilistic side |
|---|---|---|
| What it does | File I/O, tool calls, schema validation, test execution, lockfile resolution, allowlist enforcement, audit emission | Reads code, drafts prose, proposes diffs, summarises intent, picks among options, generates plans |
| Failure mode | Crash, exception, validation error -- loud and traceable | Confident plausible wrong -- silent and unfalsifiable from inside the model |
| What you trust | The exact output, byte for byte | A distribution of outputs, conditioned on a prompt |
| What it costs | Engineering hours per gate | Tokens per call, plus the cost of every failure that crosses the seam unverified |
| What crosses in | Structured prompts, declared tool schemas, file contents grounded by compile-time loaders | Proposed actions (text), proposed writes (text), structured tool-call requests |
| What crosses out | Parsed outputs validated against schema, writes filtered through an allowlist, flagged escalations to humans | Nothing direct: every probabilistic output passes through deterministic validation before it has consequences |

## Hallucination as a system property

"A pretrained model encodes a frozen distribution over text. When you
ask it about a region of the distribution that is densely represented
in training -- a popular library, a well-documented API, a standard
pattern -- it samples confidently and usually correctly. When you ask
it about a thin region -- a specific customer's account configuration,
a private codebase's internal helper, a fact that exists nowhere on
the public web -- it still samples confidently."

Critical insight: "Hallucination cannot be eliminated at the model
layer. It must be managed at the system layer." Two complementary
disciplines address it:

- **Grounding** reduces hallucination *rate*. The bounded-scope rule
  is central: "every external grounding lookup is justified by a
  specific decision the agent has to make in this turn, not loaded as
  ambient context" -- this keeps the model's queries inside the dense
  regions of its prompt.
- **Verification** reduces hallucination *consequence*: it "assumes
  hallucination happened anyway and catches it before it externalizes.
  This is what the gate does."

"A team that responds to a hallucination incident by tightening the
prompt and skipping the gate is making the wrong fix."

## The four kinds of quality gate

A 2x2 matrix distinguishes gates by **who** renders the verdict (agent
internally, or an external party) and **how** (a programmatic check,
or a judgement call):

| | Programmatic verdict | Judgement verdict |
|---|---|---|
| **Internal** | Schema validation, lint, test pass/fail, type check, diff applied cleanly, JSON parsed | Agent reviews its own plan against the goal; a goal-steward thread re-reads the spec and asks "are we still on goal?" |
| **External** | A fresh-context cold reader applies a deterministic rubric, emits pass/fail | A human checkpoint -- review, approval, sign-off -- required before the workflow continues |

### Anti-pattern: four common gate mismatches

1. **Programmatic-internal used to catch goal drift.** "The test suite
   is green. The lint passes. The type checker is happy. The agent has
   implemented the wrong feature. Programmatic-internal gates verify
   *form*; they cannot verify that the form is the form you wanted."
2. **Judgement-internal used to catch a schema violation.** "The
   goal-steward thread says 'yes, we are still implementing the rate
   limiter.' The agent's emitted JSON has a misspelled field name. The
   downstream consumer crashes. Goal stewards are LLM judgement; they
   read for intent, not for byte-level conformance."
3. **Programmatic-external used to catch a hallucinated external
   fact.** "The cold reader, given a rubric that checks structural
   correctness, sign-offs on an issue body that contains a fabricated
   customer name. The rubric never asked whether 'Acme Robotics' was a
   real customer."
4. **Judgement-external used to catch a typo in 200 lines of YAML.**
   "The human reviewer eyeballs the diff, sees that it looks
   plausible, approves. The typo ships. Humans do not read 200 lines
   of YAML carefully; the review becomes a rubber stamp."

Selection rule: "Pick the cell that matches the failure mode you are
guarding against, not the first gate that fits."

## The architect's discipline (three habits)

1. **Draw the line on the diagram.** "Before you write the prompt or
   the workflow, sketch the system and label which boxes are
   deterministic and which are probabilistic. Anything consequential
   on the probabilistic side is a design defect; redraw until
   consequential side effects sit on the deterministic side, behind a
   gate."
2. **Pick the gate before you pick the model.** "For each consequential
   effect, name the failure mode you fear and pick the gate cell --
   programmatic-internal, judgement-internal, programmatic-external,
   judgement-external -- that catches it. Then implement the gate. The
   model choice is downstream."
3. **Refuse the write token.** "When a vendor or a tool offers the
   agent a credential that allows direct externalization, ask whether
   the client offers a strong-form alternative. If it does, take it.
   If it does not, document why you accepted weak-form and what the
   compensating control is."

## Compliance and auditability

Strong-form execution "allows you to make a defensible claim about
agent-driven changes. The claim is not 'we trust the model'; the model
is in the threat model, not outside it. The claim is 'the model can
propose any change; the substrate enforces what gets applied; the
audit trail records every proposal, every accept, every reject, and
the policy that was in force at the time.'" This is "the same
compliance posture as a human-on-prod-with-PR-required workflow,
expressed in agent-aware vocabulary. Compliance reviewers who reject
'the agent has a write token' will accept 'the agent emits proposals;
the substrate applies them under declared policy.'"

## How this connects to neighbouring chapters

The "agent is a junior engineer" mindset metaphor (Ch. 10) is paired
here with the architectural two-computers metaphor. The bounded-scope
grounding rule is detailed further in Section 19.8. Chapter 20
catalogues the taxonomy of failures that follow from missing or
misplaced gates. Chapter 17 (multi-agent orchestration) places the
seam between agents as well as between model and substrate. Chapter 19
(architectural patterns) catalogues recurring shapes of the seam under
classical names.

Closing principle: "The model proposes. The gate disposes. Everything
else is detail."

## Source

Ch. 16, Part III (For Practitioners), *The Agentic SDLC Handbook* --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch16-deterministic-probabilistic-boundary.html
