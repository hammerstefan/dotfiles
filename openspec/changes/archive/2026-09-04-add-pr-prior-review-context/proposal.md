## Why

The review council can review a `pr:NUMBER` scope but is blind to the PR's
existing review conversation. Human reviewers' flagged concerns, unresolved
threads, approval states, and design discussions contain high-value evidence
that currently cannot inform adjudication, deduplication, or human-attention
escalation. The council sometimes re-derives findings a human already flagged,
misses unfixed concerns specialists did not re-find, and escalates nothing for
threads that still need a human decision.

## What Changes

- Add a `pr_discussion` operation to the read-only `review_inspect` tool: a
  single fixed GraphQL query fetching PR reviews (state, author, body), review
  threads (inline comments with `isResolved`/`isOutdated`), and issue comments,
  with body truncation and disclosed first-page bounds.
- Add a tri-state `--prior-comments <evidence|context|off>` option to the
  `review-council` command. Default `evidence`: specialists stay blind; the
  chair and `review-human` receive a prior-review digest and may re-fetch for
  depth. `context` additionally supplies the digest to specialists.
  `off` preserves current behavior and performs no fetch.
- Chair gains adjudication rules for prior-review evidence: merge specialist
  findings with human threads by root cause, cite thread URLs in prose,
  independently verify un-addressed human-flagged concerns, and suppress
  resolved or addressed threads.
- `review-human` gains an escalation path for unresolved review threads
  (category `unresolved-review-thread`) using existing attention types; no
  persistence schema change.
- Prior-review availability surfaces in the final report's Review Coverage
  section as `complete`, `truncated`, or `unavailable` (degrade, never abort).
- No changes to `review-council-json`, `review-human-json`, or
  `write_review_human_report` schemas; thread references are prose-only.

## Capabilities

### New Capabilities

- `pr-discussion-retrieval`: Bounded, read-only retrieval of a pull request's
  prior review conversation (reviews, review threads with resolution state,
  issue comments) via one fixed GraphQL call, with per-body truncation and
  explicit truncation disclosure.
- `council-prior-review-context`: Mode-dependent integration of the prior
  review conversation into the review council workflow — flag semantics,
  coordinator-owned digest, blindness routing across specialists, chair, and
  human-attention agents, untrusted-data handling, and degrade-on-failure
  coverage reporting.

### Modified Capabilities

(none — no existing specs)

## Impact

- `config/opencode/tools/review_inspect.ts`: new `pr_discussion` operation
  (GraphQL via `gh api graphql`, fixed argument array, `-F` placeholder
  fields). Remote-call budget: PR-scope coordinator flow grows from 2 to 3 of
  5 per-caller remote calls.
- `config/opencode/command/review-council.md`: flag parsing and validation,
  Step 1 fetch and digest embedding, mode-dependent dispatch wiring, coverage
  reporting.
- `config/opencode/agent/review-chair.md`: prior-review adjudication
  methodology.
- `config/opencode/agent/review-human.md`: unresolved-thread escalation class.
- Specialist agent files: unchanged (context-mode rules ride in the
  coordinator's dispatch prompt).
- Side effect: `review-human` independent command inherits agent-file
  escalation rules for free; wiring its own flag is out of scope.
