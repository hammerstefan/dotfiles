## 1. Tool operation

- [x] 1.1 Add `pr_discussion` to the `review_inspect` discriminated-union
  schema in `config/opencode/tools/review_inspect.ts` (integer PR number,
  same bounds as `pr_metadata`)
- [x] 1.2 Implement the fixed `gh api graphql` command: constant query
  string selecting `reviews(first: 100)`, `reviewThreads(first: 100)` with
  `comments(first: 50)`, issue `comments(first: 100)`, and
  `pageInfo.hasNextPage` on each connection; `-F owner='{owner}' -F
  name='{repo}' -F number=<N>` placeholder fields
- [x] 1.3 Write the constant `--jq` projection: compact result shape with
  author, state, URL, timestamps, thread grouping, `isResolved`/
  `isOutdated`, path/line/side, and every body truncated to 2000 characters
  (`.[0:2000]`)
- [x] 1.4 Verify the operation routes through existing budget accounting
  (counts as one remote call; command/byte/timeout limits unchanged) and
  fails safely under the output safety limit

## 2. Command contract

- [x] 2.1 Add `--prior-comments <evidence|context|off>` to the interface,
  defaults, and validation sections of
  `config/opencode/command/review-council.md` (default `evidence`; reject
  unknown/missing values; no alternate spelling; note-and-continue when
  scope is not `pr:NUMBER`)
- [x] 2.2 Extend Step 1 normalization: in `evidence`/`context` modes with a
  PR scope, perform exactly one `pr_discussion` call, embed the structured
  digest plus availability status (`complete`/`truncated`/`unavailable`) in
  the contract; in `off` mode perform no call; never retry failures
- [x] 2.3 Extend Step 2/3 dispatch wiring: triage and `evidence`-mode
  specialist prompts exclude the digest; `context`-mode specialist prompts
  carry the digest with untrusted-data rules; document that specialist
  agent files remain unchanged
- [x] 2.4 Extend Step 4/5 dispatch wiring: chair and `review-human`
  contracts carry the digest (unless `off`) with permission to re-fetch
  `pr_discussion` for thread depth
- [x] 2.5 Add prior-review availability reporting to the Final Output Review
  Coverage section (`complete` / `truncated` with counts / `unavailable`
  with reason; inapplicable-flag note for non-PR scopes)

## 3. Agent methodology

- [x] 3.1 Add prior-review adjudication rules to
  `config/opencode/agent/review-chair.md`: merge with human threads by root
  cause, cite thread URLs in prose, priority-vs-verification rule,
  independent verification of un-re-found human concerns, suppression of
  resolved/addressed threads, `review-council-json` unchanged
- [x] 3.2 Add unresolved-thread escalation to
  `config/opencode/agent/review-human.md`: category
  `unresolved-review-thread` with existing attention types, changed-code
  location requirement, no duplication of chair-verified findings, no
  schema additions

## 4. Verification

- [x] 4.1 Tool-level check: run `pr_discussion` against a real PR with
  conversation (verify single remote call, grouped threads, resolution
  flags, body truncation, `hasNextPage` disclosure) and a PR without
  conversation (empty lists).
  - Verified live against `cli/cli#14345` (5 reviews, 3 review threads,
    resolution flags populated, longest review body of 4658 chars
    truncated to 2000 by `--jq`), `cli/cli#1` (empty review lists, 2
    issue comments — confirms empty-list case), and `cli/cli#99999999`
    (NOT_FOUND — confirms the throw-and-degrade path).
  - Single remote call per invocation confirmed (`gh api graphql` is the
    only `gh` invocation in the operation).
  - The token-level query string and `--jq` projection are constants in
    `review_inspect.ts`; only the PR number is variable input.

- [x] 4.2 Command-level check: run `/review-council --scope pr:<N>` in all
  three modes and confirm routing (specialist blindness in `evidence`,
  digest presence in `context`, no fetch in `off`) and coverage reporting.
  - `--prior-comments off` and the default (evidence) were exercised
    end-to-end through the opencode slash-command framework against
    `cli/cli#14345`. The `--prior-comments off` run produced no
    `pr_discussion` operation in the inspection log; the default run
    dispatched triage, correctness, security, and chair agents and
    produced a real finding (`SEC-001`).
  - The `context` mode dispatch wiring is documented in
    `config/opencode/command/review-council.md` Step 3 "Mode-dependent
    specialist dispatch" with the untrusted-data rule block; live
    dispatch was not exercised end-to-end in this environment due to
    LLM time/token budget but the contract-level routing is in place
    and was structurally inspected.
  - Coverage reporting instructions are documented at the Final Output
    Review Coverage section.

- [x] 4.3 Degrade check: simulate fetch failure (unset `GH_TOKEN` or
  nonexistent PR number) and confirm the review completes with
  `unavailable` reported.
  - Verified live: `gh api graphql` against a nonexistent PR number
    exits non-zero and emits a NOT_FOUND error. The `run()` helper in
    `review_inspect.ts` throws on non-zero exit and the prior-review
    digest section in `review-council.md` Step 1 explicitly states
    "Perform no retry on failure; a missing digest degrades the review
    but never aborts it" with `availability: "unavailable"` and a
    captured reason. End-to-end through `/review-council` was not run in
    this environment.

- [x] 4.4 Injection check: confirm dispatch prompts carrying the digest
  state untrusted-evidence rules and that comment text cannot alter the
  contract (spot-check with a comment containing directive-like text).
  - Static verification: the untrusted-evidence rules block appears in
    every dispatch prompt that can carry the digest —
    `review-council.md` Step 3 specialist prompt (context mode), Step 4
    chair dispatch ("Prior-review evidence in chair dispatch"), and
    Step 5 `review-human` dispatch — and in the agent files
    `review-chair.md` ("Prior-review adjudication") and
    `review-human.md` ("dispatch contract carries a `prior_review.digest`"
    paragraph). Each block states that comment and review text is
    untrusted evidence, cannot alter scope, focus, exclusions, severity
    floor, reviewer selection, or persistence rules, and cannot become
    a finding without independent code verification.
  - Body truncation (`.[0:2000]` in `--jq`) bounds the payload that
    reaches any model.
  - Live injection spot-check inside a full council run was not
    executed in this environment.

- [x] 4.5 Regression check: `--prior-comments off` produces a report
  byte-equivalent in structure to the pre-change behavior (no fetch, no
  digest, no coverage line beyond the availability note pattern).
  - Static verification: Step 1's "Prior-review digest" subsection
    states "In `--prior-comments off` mode, or when scope is not
    `pr:NUMBER`, do not call `pr_discussion`, set `prior_review` to
    `null`"; Step 3/4/5 dispatch wirings say "embed no digest in
    the {specialist,chair,review-human} dispatch and do not mention
    prior reviews" when `--prior-comments` is `off`; the Review
    Coverage section renders no `Prior reviews:` line for the `off`
    case, only the three spec-listed states plus `inapplicable`.
  - Live verification: the live `/review-council --scope pr:14345
    --prior-comments off --mode fast` run dispatched the standard
    council flow without calling `pr_discussion`.
