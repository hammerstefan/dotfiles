## 1. Shared criteria and compatibility

- [x] 1.1 Extract audience, readability criteria, and meaning-preservation safeguards into `config/opencode/prompt/readability-criteria.md` without changing their behavior.
- [x] 1.2 Update the repository readability agent to load the installed shared criteria with narrow read access; preserve all repository scopes, channels, limits, model, and council contracts.
- [x] 1.3 Verify criteria loading from the installed/symlinked config directory and a non-repository working directory, including fail-closed behavior when unavailable.

## 2. Ticket command and retrieval

- [x] 2.1 Add the `/review-ticket` command interface and normalization rules for a single key/URL, site, audience, explicit custom field, comments, and up to five context tickets.
- [x] 2.2 Add a deny-by-default ticket coordinator with exact read-only MCP discovery/retrieval permissions, questions, criteria reads, and dispatch only to the ticket reviewer; verify runtime tool names.
- [x] 2.3 Implement primary target/site resolution and identity checks, explicit minimal fields, ADF retrieval, and `updateHistory: false`; stop on primary failure without retries or alternate-target lookup.
- [x] 2.4 Implement opt-in comments and explicit context-ticket retrieval with bounded issue-read, comment-count, and text budgets; keep context separate and disclose paging/failures. Task 3.7 adds one same-ticket acceptance read, increasing the issue-read ceiling from seven to eight.
- [x] 2.5 Define ADF/plain-text normalization, stable field-local citation blocks, empty/unavailable field handling, link/code preservation, unsupported-node coverage, and snapshot metadata.

## 3. Feedback and proposal

- [x] 3.1 Add `review-ticket-readability` using the approved readability model, supplied shared criteria, and no remote/write/execution/delegation permissions.
- [x] 3.2 Implement ticket-specific clarity/editorial feedback, faithful summary/description and selected-field proposals, open questions, and ready/needs_clarification/incomplete statuses.
- [x] 3.3 Specify and validate the complete `review-ticket-json` shape, IDs/references, source-backed citations, coordinator-owned metadata, null/empty proposals, and coverage; fail visibly on malformed output.
- [x] 3.4 Render copyable proposed text separately from notes/questions and include a no-Jira-changes statement; withhold unsafe or incomplete field replacements rather than fabricating content.
- [x] 3.5 Load the canonical `asd-ste100` skill in the coordinator before Jira access and directly in the reviewer, alongside its narrow canonical criteria read; remove duplicated STE rules while preserving ticket contracts and repository behavior.
- [x] 3.6 Display all reported undefined or ambiguous terms in a source-backed Markdown table derived from validated feedback, with empty/incomplete scan wording and unchanged JSON schema; add contract checks.
- [x] 3.7 Automatically discover a separate acceptance-criteria field through scoped read-only metadata, preserve explicit overrides, ask on unresolved discovery, review criteria and cross-field consistency, and validate permissions/retrieval/coverage with synthetic fixtures.

## 4. Validation

- [x] 4.1 Add fixtures for clear/bloated/ambiguous tickets, empty and absent descriptions, custom acceptance fields, repeated headings, code/links, ADF unsupported nodes, contradictory comments, and unavailable/oversized context.
- [x] 4.2 Validate parsing, site ambiguity, identity mismatches, minimal read calls, pagination and budget boundaries, schemas/citations, and malformed-output failures with mocked retrieval; no real mutation probes. Static/mocked versus live coverage limits are recorded in `validation.md`.
- [x] 4.3 Inspect effective V2 permissions and exercise denied Jira mutation, arbitrary fetch/shell, and persistence attempts only against safe mocks or local permission checks; stop if read-only enforcement is not verifiable.
- [x] 4.4 Run live fixture-based reviewer evaluations for useful feedback, faithful replacement text, preserved obligations/code/links, unresolved ambiguity, injection resistance, and synthetic secret redaction.
- [x] 4.5 Run existing repository readability/council and human-attention tests and behavior checks after criteria extraction; verify no Jira tools or ticket fields leaked into those contracts.
- [x] 4.6 Validate OpenSpec and record a validation report separating automated, mocked, live, and untested cases; optionally exercise one explicitly user-selected real ticket read-only with no writes. Results and remaining real-ticket/coverage limits are recorded in `validation.md`.
- [x] 4.7 Verify direct `asd-ste100` skill loading and evaluate ticket feedback/drafts for preserved obligations and uncertainty, precision notes, and unchanged report/JSON format.
