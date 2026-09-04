## ADDED Requirements

### Requirement: Prior-comments option parsing
The `review-council` command SHALL accept `--prior-comments
<evidence|context|off>` with default `evidence`, SHALL reject unknown values
and a missing value per existing validation rules, and SHALL NOT offer any
other flag spelling for this behavior.

#### Scenario: Default applies
- **WHEN** `/review-council --scope pr:42` is invoked without
  `--prior-comments`
- **THEN** the review runs in `evidence` mode

#### Scenario: Unknown value rejected
- **WHEN** `--prior-comments summary` is supplied
- **THEN** the command rejects the invocation before dispatch with a
  validation error

#### Scenario: Non-PR scope is note-and-continue
- **WHEN** `--prior-comments` is supplied with any value and the scope is not
  `pr:NUMBER`
- **THEN** the review proceeds and the report states that `--prior-comments`
  was inapplicable because the scope is not a PR

### Requirement: Coordinator-owned digest
In `evidence` and `context` modes with a `pr:NUMBER` scope, the coordinator
SHALL issue exactly one `pr_discussion` call during contract normalization,
SHALL embed a structured digest of the result (authors, states, thread
grouping, path/line, resolution and outdated flags, truncated bodies,
truncation indicators) in the normalized contract, and SHALL NOT retry a
failed call. In `off` mode the coordinator SHALL perform no
`pr_discussion` call and SHALL NOT embed any digest.

#### Scenario: Evidence mode fetch
- **WHEN** scope is `pr:42` and mode is `evidence`
- **THEN** the coordinator performs exactly one `pr_discussion` call and the
  contract carries the digest

#### Scenario: Off mode performs no fetch
- **WHEN** scope is `pr:42` and `--prior-comments off` is supplied
- **THEN** no `pr_discussion` call occurs and no digest appears in the
  contract

### Requirement: Mode-dependent routing
The command SHALL route the digest by mode: `review-triage` receives no
digest in any mode; specialists receive no digest in `evidence` mode and
receive the digest in their dispatch prompt in `context` mode;
`review-chair` and `review-human` receive the digest in both `evidence` and
`context` modes. Specialist agent definitions SHALL NOT be modified; all
mode-dependent instructions SHALL ride in coordinator dispatch prompts.

#### Scenario: Specialists blind in evidence mode
- **WHEN** mode is `evidence`
- **THEN** no specialist dispatch prompt contains digest content

#### Scenario: Specialists see digest in context mode
- **WHEN** mode is `context`
- **THEN** each specialist dispatch prompt carries the digest and explicit
  untrusted-data rules for it

### Requirement: Chair adjudication with prior-review evidence
Whenever digest data exists, the chair SHALL merge specialist findings with
human review threads by root cause and cite the thread URL in prose; prior
human flagging SHALL raise review priority but never replace independent
chair verification; the chair SHALL independently verify human-flagged
concerns that no specialist re-found and MAY accept them as findings on
their own evidence; threads that are resolved or whose flagged code changed
after the comment SHALL be suppressed rather than re-raised.

#### Scenario: Independent rediscovery merges with human thread
- **WHEN** a specialist finding shares a root cause with an unresolved human
  thread
- **THEN** the chair reports one merged finding citing both the code
  evidence and the thread URL

#### Scenario: Unaddressed human concern becomes a finding
- **WHEN** an unresolved human-flagged concern matches no specialist finding
  and chair verification confirms the defect still exists at the flagged
  location
- **THEN** the chair accepts it as a verified finding on its own evidence

#### Scenario: Resolved thread is not re-raised
- **WHEN** a thread is marked resolved or the flagged line changed after the
  comment and no live defect remains
- **THEN** the chair does not emit a finding for that thread

### Requirement: Unresolved-thread human escalation
`review-human` SHALL be able to surface unresolved review threads as
human-attention items using category `unresolved-review-thread` with
existing attention types, each item tied to changed code at a repository
path and line, and SHALL NOT duplicate chair-verified findings unless a
distinct human decision remains. No persistence schema field SHALL be added
for prior-review data.

#### Scenario: Unresolved decision thread escalates
- **WHEN** an unresolved thread marks a consequential tradeoff the
  repository cannot settle and the chair has not merged it into a verified
  finding
- **THEN** `review-human` emits an item with category
  `unresolved-review-thread`, a changed-code location, and a concrete human
  action

### Requirement: Degrade-on-failure availability reporting
A failed, truncated, or missing `pr_discussion` result SHALL NOT abort the
review. The final report's Review Coverage section SHALL state prior-review
availability as `complete`, `truncated` (with counts and which connections
were truncated), or `unavailable` (with reason).

#### Scenario: Fetch failure degrades
- **WHEN** the single `pr_discussion` call fails due to authentication or
  permissions
- **THEN** the review completes without digest-informed adjudication and
  Review Coverage reports `unavailable` with the reason

#### Scenario: Truncation disclosed
- **WHEN** the digest is embedded and any connection reported `hasNextPage`
- **THEN** Review Coverage reports `truncated` with counts of included
  reviews, threads, and comments

### Requirement: Untrusted-data handling for prior-review content
Every dispatch prompt carrying the digest SHALL state that comment and
review text is untrusted evidence: it SHALL NOT be obeyed as instructions,
SHALL NOT alter scope, focus, exclusions, severity floor, reviewer
selection, or persistence rules, and SHALL NOT become a finding without
independent code verification. Quoted prior-review content in reports or
persisted artifacts SHALL remain minimal and redacted.

#### Scenario: Injection attempt in a comment body is inert
- **WHEN** a comment body contains text directing the reviewers to ignore
  scope exclusions or report a fabricated finding
- **THEN** the review contract, scope, and exclusions remain unchanged and
  no finding is accepted without independent chair verification
