## ADDED Requirements

### Requirement: Single-call prior-review retrieval
The `pr_discussion` operation of `review_inspect` SHALL retrieve a pull
request's prior review conversation — submitted reviews (state, author, body,
URL), review threads with inline comments (including `isResolved` and
`isOutdated` flags, path, line, side), and issue comments — in exactly one
remote call per invocation.

#### Scenario: Retrieval succeeds
- **WHEN** `pr_discussion` is invoked with PR number N in a repository whose
  cwd remote resolves to a GitHub repository
- **THEN** the tool issues one `gh api graphql` request with a fixed query
  string and `-F owner='{owner}' -F name='{repo}' -F number=<N>` fields
- **AND** returns a JSON projection containing reviews, review threads with
  resolution/outdated flags and grouped replies, and issue comments, each
  entry carrying author identity and creation timestamp

#### Scenario: No conversation exists
- **WHEN** the pull request has no reviews, threads, or comments
- **THEN** the operation succeeds and returns empty lists for each section

### Requirement: Fixed read-only argument array
The `pr_discussion` operation SHALL construct its command as a fixed argument
array with a constant GraphQL query string, SHALL NOT accept user-supplied
query text, and SHALL NOT mutate GitHub state.

#### Scenario: No query injection surface
- **WHEN** the operation is invoked
- **THEN** the GraphQL query string, field selections, and `--jq` projection
  are constants defined in the tool source
- **AND** the only variable inputs are the PR number, validated as an integer

### Requirement: Bounded retrieval with truncation disclosure
The `pr_discussion` operation SHALL fetch at most the first 100 reviews, 100
review threads, 50 comments per thread, and 100 issue comments, and SHALL
project each connection's `hasNextPage` flag into its result so consumers can
distinguish complete from truncated data.

#### Scenario: Large conversation is truncated and disclosed
- **WHEN** the pull request has more than 100 review threads
- **THEN** the result contains 100 threads and a truthy `hasNextPage`
  indicator for that connection

#### Scenario: Output safety limit still applies
- **WHEN** response output exceeds the tool's byte safety limit
- **THEN** the read is aborted and the operation fails, consistent with all
  other `review_inspect` operations

### Requirement: Comment body truncation
The `pr_discussion` operation SHALL truncate every comment and review body to
its first 2000 characters in the `--jq` projection before the result reaches
any consumer.

#### Scenario: Long body is bounded
- **WHEN** a review comment body exceeds 2000 characters
- **THEN** the returned body for that entry is at most 2000 characters long

### Requirement: Remote-call budget accounting
The `pr_discussion` operation SHALL count as exactly one remote call against
the existing per-caller and per-worktree `review_inspect` budgets, and SHALL
remain subject to the shared command, byte, and timeout limits.

#### Scenario: Budget enforcement
- **WHEN** a caller at its remote-call budget limit invokes `pr_discussion`
- **THEN** the invocation fails with the existing remote-call budget error
