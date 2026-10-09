## ADDED Requirements

### Requirement: Canonical shared readability criteria
Repository and ticket readability workflows SHALL load one canonical instruction document covering audience, sentence/document readability, and meaning-preservation safeguards before reviewing. Failure to load it SHALL stop review. Source-specific scopes, citations, permissions, result shapes, and volume limits SHALL remain in their respective contracts.

#### Scenario: Ticket reviewer reads canonical criteria directly
- **WHEN** the ticket coordinator dispatches a supplied source snapshot
- **THEN** the reviewer reads only the installed canonical criteria file before reviewing, rather than depending on a manually forwarded copy

#### Scenario: Installed invocation outside the repository
- **WHEN** either workflow runs from a directory unrelated to the dotfiles repository
- **THEN** it loads the installed shared criteria independently of the working directory and untrusted input

#### Scenario: Shared file unavailable
- **WHEN** the canonical criteria cannot be read
- **THEN** the workflow reports the missing prerequisite instead of improvising or reviewing with stale duplicated rules

### Requirement: Existing repository behavior remains compatible
Extraction SHALL preserve the repository reviewer's configured model, scope boundaries, read-only permissions, finding/editorial schemas, grouping/cap rules, council selection and adjudication, and human-attention persistence semantics. It SHALL NOT grant Jira access to council agents.

#### Scenario: Existing council review
- **WHEN** `/review-council --only readability` reviews repository text after extraction
- **THEN** it returns the existing repository-specific channels and file/line citations under unchanged rules

### Requirement: Shared meaning and audience safeguards
Both workflows SHALL preserve technical meaning, MUST/SHOULD obligations, qualifications, exceptions, code, identifiers, useful passive voice/fragments, and deliberate warnings. They SHALL use the intended audience, reject personal-preference changes, avoid fabricated facts and AI-authorship claims, and limit missing-explanation feedback to understanding the scoped text rather than enforcing a general documentation or design audit.

#### Scenario: Already-clear text
- **WHEN** text is clear for the intended audience
- **THEN** the reviewer does not demand definitions of ordinary vocabulary or preference-only rewrites

#### Scenario: Missing technical fact
- **WHEN** a correction requires a fact the source does not establish
- **THEN** the reviewer asks for clarification instead of inventing a requirement or example
