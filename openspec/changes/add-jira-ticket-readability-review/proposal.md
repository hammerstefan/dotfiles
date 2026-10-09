## Why

Technical Jira tickets need the same audience-aware clarity checks as repository documentation, but the current readability reviewer requires repository scopes and file/line citations. Provide feedback and a ready-to-paste replacement without silently changing task intent or granting Jira write access.

## What Changes

- Add `/review-ticket` for a single Jira issue key or URL, returning clarity feedback, proposed summary and description, open questions, and coverage.
- Fetch summary, description, and acceptance criteria read-only through the configured Atlassian MCP connection. Discover a separate criteria field from scoped metadata by default; retain an explicit field-ID override and ask when discovery is unresolved.
- Use comments and explicitly selected linked tickets only as opt-in context, not as rewrite targets or authoritative new requirements.
- Share readability criteria with the existing repository reviewer through a common instruction document and a ticket-specific reviewer using `github-copilot/claude-opus-5.5`.
- Cite ticket fields, headings, and numbered paragraphs with safe excerpts, not invented file paths or Jira line numbers.
- Preserve requirements, qualifications, links, and code; keep unresolved details outside the proposed text and never fabricate missing task facts.
- Load the canonical `asd-ste100` skill directly for Jira feedback and drafts only. The coordinator checks availability before Jira access; the reviewer loads it as its only allowed tool instead of receiving manually copied rules. Preserve meaning, uncertainty, and the skill's compliance qualifications.
- Keep the workflow read-only: no Jira edits/comments, no local report artifacts, and no coupling to council verdicts or human-attention persistence.

## Capabilities

### New Capabilities

- `jira-ticket-readability-review`: Single-ticket resolution, scoped read-only retrieval, clarity feedback, replacement proposal, citations, coverage, and safety.
- `shared-readability-criteria`: Shared audience, readability, and meaning-preservation instructions for repository and ticket review, retaining source-specific contracts.

### Modified Capabilities

None. Existing main specs cover PR discussion retrieval and routing, which remain unchanged. The completed, unarchived `add-review-readability` change is an implementation dependency; its council contracts remain unchanged.

## Impact

New command and ticket coordinator/reviewer definitions under `config/opencode/`, one shared instruction document, and a narrow refactor of `agent/review-readability.md`. The configured Atlassian MCP service is already present. Add fixture-based contract and behavior evaluations; no Jira schema, persistence schema, council reviewer lists, new service, or dependency changes are required.
