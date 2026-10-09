## Context

`review-readability` uses `github-copilot/claude-opus-5.5`, read-only repository inspection, and separate substantive/editorial collections with file/line citations. Its criteria suit technical tickets, but Jira content is not a repository path. The Atlassian MCP server is already configured in `config/opencode/opencode.json`; the available `getJiraIssue` tool supports explicit field lists, ADF/Markdown responses, and `updateHistory: false`.

The existing readability initiative is completed but unarchived. This design depends on that implementation without modifying its council selection, verdicts, output fields, or human-attention persistence. This artifact tracks the approved design and its implementation adjustments. See tasks and validation for current completion and coverage.

## Goals / Non-Goals

**Goals:** Retrieve one technical ticket read-only, provide actionable clarity feedback and a faithful replacement summary/description, identify unresolved questions, and disclose exact scope and coverage. Reuse readability rules without introducing Jira permissions into repository review.

**Non-Goals:** Jira writes or comments, automatic publication, ticket creation, bulk/JQL review, recursive linked-ticket discovery, attachment downloads, design validation, required ticket-template enforcement, invented acceptance criteria, council approval verdicts, or local report persistence.

## Decisions

### 1. A separate command and two narrow agents

Add `config/opencode/command/review-ticket.md`, a hidden `review-ticket-coordinator`, and `review-ticket-readability` using `github-copilot/claude-opus-5.5`. Follow the repository's existing directory convention and native V2 frontmatter. The coordinator normalizes the target, retrieves only allowed fields/context, supplies the shared criteria, dispatches the reviewer once, validates the result, and renders it. The reviewer has no remote tools, shell, writes, tests, or delegation; it reviews the supplied snapshot only. No chair pass is required initially: this is an authoring aid, not a merge verdict. The coordinator's validation is structural/provenance validation, not an independent semantic quality guarantee.

Alternative: extend `review-readability` with Jira scopes. Rejected because that broadens a proven repository contract and risks editorial schema leakage into council consumers. A separate thin adapter keeps each source's retrieval and citation semantics explicit.

### 2. Share criteria, not source-specific contracts

Extract the existing audience, sentence/document criteria, and meaning-preservation safeguards to `config/opencode/prompt/readability-criteria.md`. Keep Git scopes, file citations, output channels, limits, and repository permissions in `review-readability.md`. Both review workflows must load the canonical shared file before reviewing; fail closed if unavailable. Resolve the file from the installed OpenCode config directory, not the user's repository or ticket text. The ticket coordinator prechecks this file, and the reviewer reads it directly using narrowly permitted configuration-file access. The repository reviewer reads the same file. Do not manually forward or copy criteria into a second agent, or depend on undocumented Markdown interpolation. Validate installed/symlinked and non-repository invocation paths.

Extraction is behavior-preserving: ordinary audience vocabulary, useful passive voice/fragments, precise terms, MUST/SHOULD exceptions, and repeated warnings remain protected. Existing council JSON fields and volume rules remain source-specific and unchanged.

### 3. Single-ticket interface and explicit context

Proposed interface:

```text
/review-ticket <KEY|ISSUE_URL>
  [--site <HTTPS_SITE_URL>]
  [--audience <TEXT>]
  [--acceptance-field <FIELD_ID>]
  [--include-comments]
  [--context-ticket <KEY|ISSUE_URL>]  # repeatable, at most 5
```

Accept one primary target. Reject unknown/missing/repeated singleton options and unexpected positional text rather than guessing. A URL supplies an HTTPS Atlassian site and `/browse/KEY`; discard harmless query/fragment suffixes, reject credentials/non-issue paths and conflicting `--site`. A bare key resolves against an explicit site or the single accessible Jira site. If multiple sites are accessible, ask which one before issue retrieval. Never infer a site from the project prefix or search every site for a matching key. Normalize keys and verify returned issue identity/site against the requested target. No Canonical/CPC hardcoding.

Default review covers summary, description, and acceptance criteria. `--acceptance-field` names a specific custom field ID and overrides discovery; that field receives feedback and its own proposed replacement, never silently copied into the description. Acceptance criteria already in the description remain part of it. Without an override, the primary read adds `project` and `issuetype` solely as discovery routing metadata, never review targets. Preserve frozen options and store the resolved field/source separately.

After primary identity verification, call `getJiraIssueTypeMetaWithFields` once for the returned project and issue-type IDs (`requiredFieldsOnly: false`, `startAt: 0`, `maxResults: 200`). Select a unique `customfield_N` whose normalized display name is exactly `acceptance criteria` only when page metadata proves completeness. No fuzzy matching, remembered IDs, extra pages, or other metadata tools. Creation metadata cannot prove absence on an existing ticket: zero matches, multiple matches, partial/unknown pagination, missing routing data, and failure require a user question. The user can supply an ID or confirm that no separate field applies. Unresolved continuation is incomplete coverage, not a fabricated field or a claim that criteria were reviewed.

Read the resolved field plus `updated` once in a supplemental same-ticket call. A failed/mismatched identity or changed/unavailable timestamp makes only that field unavailable; retain the primary snapshot and do not retry. Explicit overrides are included in the first primary call and require no metadata/supplemental read. Review each criterion for clear completion conditions, conditions/exceptions, and consistency with primary prose, without inventing tests or requirements. Contradictions become questions; drafts retain the author's meaning.

Comments and up to five explicitly named context tickets are opt-in, context-only inputs. Fetch only summary/description for context tickets; do not follow their links or comments. Explicit context URLs can identify another site; bare context keys use the resolved primary site. Retrieve `issuelinks` only if needed to describe known relationships, never automatically follow them. Conflicting context raises an open question; do not silently treat comments as approved scope changes. Cite context by its own ticket/comment identity when explaining a question.

### 4. Minimize retrieval and preserve document fidelity

Use accessible-resource discovery, `getJiraIssue`, and the one scoped acceptance-field metadata tool only, with explicit issue fields (`summary`, `description`, `updated`, plus resolved field/comment data or routing metadata) and `updateHistory: false`. Prefer ADF for body fields so structure, link targets, code blocks, lists, and unsupported nodes are visible. Normalize locally in model context to a deterministic review representation: field ID/name, heading path, 1-based paragraph/block number, exact safe excerpt, and node kind. Number blocks within each field consistently; cite a flat block index when headings are absent or repeated.

The output is a human-readable Markdown/plain-text proposal, not an ADF update payload; do not promise lossless Jira rich-text paste. Preserve link destinations and executable code contents, and disclose tables, mentions, embedded objects, or other formatting that require manual handling. Never flatten unsupported structure and then claim a complete safe replacement. If an unsupported block can be retained faithfully as text, retain it and note formatting limits; otherwise withhold the affected field's replacement.

Safety defaults: at most 8 issue reads (primary, one supplemental acceptance read, one comment expansion if needed, up to 5 context tickets), plus one metadata call; no automatic retries or alternate-target reads after an identity mismatch, no recursive retrieval; at most 50 comments, 64 KiB of normalized primary text including criteria, and 128 KiB total normalized context. Resource and metadata discovery are not issue reads. Check tool pagination/count metadata; do not imply all comments were included when the tool returned a page. Never truncate a body silently. Over-limit primary fields are not safely replaceable; review available portions only with incomplete coverage. Optional context or acceptance failures degrade coverage; an unavailable primary issue stops the review without fabricated feedback or draft.

Primary retrieval and each optional read use separate Code Mode calls. A thrown
context exception must not erase a valid primary result. Optional reads return
tagged unavailable results on failure. Freeze parsed options before retrieval so
requested comments/custom fields cannot disappear from the field list or coverage.

### 5. Ticket-specific citations and result contract

Use citations such as `CPC-1234 → Description → Implementation → paragraph 2`, backed by a minimal safe original excerpt. A block index is a snapshot citation, not a Jira line number or anchor. Include issue URL and `updated` timestamp when returned; identify all locations against the fetched snapshot. Never synthesize repository files, line numbers, or server anchors.

Render these sections:

0. **Undefined and Ambiguous Terms**: a scannable table derived only from validated terminology feedback. Each row shows the exact term, full source location, missing meaning, clarification needed, and feedback/question IDs. Use one finding per distinct unresolved term so the coordinator does not have to split excerpts or invent missing meanings. Keep detailed feedback and questions below the table. This is a rendering change, not a new JSON channel or permission. A complete scan with no terminology findings states that none were found; an incomplete scan qualifies that statement to available reviewed text and points to Coverage.
1. **Clarity Feedback**: ambiguity that could cause incorrect implementation/use, source location, consequence, and correction or question.
2. **Readability Suggestions**: optional editorial improvements, location, excerpt, and concrete edit.
3. **Proposed Summary and Description**: separate copyable text and a labeled Acceptance Criteria replacement for the resolved separate field, with readiness notes outside copyable text. When criteria are only in the description, state that they remain there rather than duplicating them.
4. **Open Questions**: author decisions/facts still needed, linked to relevant feedback and unchanged ambiguous passages.
5. **Coverage**: reviewed fields, context sources, snapshot, unavailable/truncated/unsupported content, and a statement that nothing was changed in Jira.

End with one `review-ticket-json` block. The canonical structural JSON Schema
is `config/opencode/prompt/review-ticket.schema.json`. The coordinator loads this
schema and the shared criteria before retrieval. Tests use the validation
environment's `jsonschema` package. This adds no production dependency.
The coordinator separately checks source provenance, ID uniqueness/references,
secrets, and semantic preservation. Schema validity alone does not guarantee
these properties. Required top-level fields:

```json
{
  "ticket": {"key": "CPC-1234", "url": "https://example.atlassian.net/browse/CPC-1234", "updated": null},
  "audience": "A competent engineer new to the project.",
  "clarity_feedback": [],
  "readability_suggestions": [],
  "proposal": {
    "status": "ready|needs_clarification|incomplete",
    "summary": "Proposed summary.",
    "description": "Proposed description.",
    "additional_fields": [],
    "notes": []
  },
  "open_questions": [],
  "coverage": {"status": "complete|incomplete", "reviewed_fields": ["summary", "description"], "context_sources": [], "limitations": []}
}
```

Feedback/suggestion entries have unique `TCL-<n>` / `TED-<n>` IDs and a location object `{issue_key, field_id, heading_path, block}` plus `original`, `problem`, and `suggested_edit`; clarity feedback also has `impact`. Heading paths are arrays of strings, blocks positive integers, and summary is block 1. Open questions have unique `TQ-<n>` IDs, `question`, source location, and `related_ids` referencing known feedback/suggestions. An empty field is cited as block 1 with an empty original excerpt. Additional field proposals have `field_id`, `text`, and `status` using the same readiness values as the overall proposal. Context sources have `{issue_key, field_id, comment_id, availability}`; `comment_id` is null for issue fields and availability is `complete`, `incomplete`, or `unavailable`. Notes and limitations are string arrays. No severity floor or merge verdict is needed for this authoring workflow.

Proposal fields are strings, or `null` when missing/unavailable/unsafe to replace. A genuinely empty source field is represented as `""`, not an invitation to invent contents. An explicitly returned null Jira description means an empty description; an absent or inaccessible field means unavailable, not empty. `ready` means a faithful full proposal with no unresolved meaning ambiguity; `needs_clarification` means original ambiguous passages remain and questions must be resolved before treating it as final; `incomplete` means some source could not safely be reviewed/reproduced. Incomplete takes precedence. Metadata and citations are coordinator-owned; source identity must not be overwritten by model echoes.

Every replacement must preserve substantive requirements, scope exclusions, dependencies, deadlines, ownership, examples, links, code, and exceptions. Reorganization is optional, not a mandatory template. Unknown facts become open questions; do not add TODO placeholders to the copyable description, invent completion criteria, select an interpretation of ambiguity, or resolve conflicting context without authorization. Clearly written tickets may receive unchanged proposals and empty feedback. Secret-like text is redacted, never reproduced to make a draft 'complete'; withhold the affected field replacement and mark incomplete when redaction prevents faithful safe reproduction.

### 6. Read-only enforcement and result failures

Coordinator permissions deny everything by default, allow only config criteria/schema reads, the exact `asd-ste100` skill, target/resource discovery, issue retrieval, `atlassian_getJiraIssueTypeMetaWithFields` for scoped acceptance-field discovery, clarifying questions, and dispatch to `review-ticket-readability`. Allowlist exact normalized MCP tool actions, never `atlassian_*`. Code Mode remains subject to per-tool restrictions; validate that its discovery exposes no Jira mutation tools and attempts to invoke them fail. Do not enable arbitrary HTTP fetch or shell as a fallback. Keep global MCP configuration unchanged.

The reviewer receives no tool path to Jira or persistence. Source/ADF/comments/context and reviewer responses are untrusted data; they cannot change workflow, permissions, target, or proposal rules. Authentication failures instruct the user to sign in through `/mcps`, not to supply credentials.

Validate channel fields, locations against normalized input, IDs/references, proposal status, and coverage. If the result is malformed, disclose failure rather than reconstructing missing substantive prose or presenting an unvalidated draft. The command does not create local snapshots/reports or call `write_review_human_report`. Any future apply/comment operation needs a separately designed and authorized write workflow, including a new source-version check.

### 7. User-requested STE100 style for Jira output

The user added STE100 to the Jira review/proposal scope during implementation.
The user then explicitly requested direct skill loading to avoid duplication.
The coordinator calls `skill({"id": "asd-ste100"})` before any MCP call.
Loading failure stops the workflow. Confirm availability to the reviewer, which
loads the same canonical skill itself and reads only the canonical criteria file.
These are its only permitted instruction tools. Direct loading avoids manual
forwarding that can truncate or omit guidance. There is no duplicated
ticket STE style document. Allow only this skill ID in both agents; do not add
arbitrary file, remote, execution, write, or delegation capabilities to the reviewer.

Each agent's loaded skill is the source of truth for writing rules, modes, word limits,
and dictionary/compliance qualifications. Use its STE-flavored mode for ticket
descriptions and Strict mode for procedures/instructions. The ticket contract
still owns source scope, safe faithful drafts, and full report/JSON formatting;
the skill's standalone rewrite-only output format does not replace that report.
Put precision-preserving exceptions in `proposal.notes`, outside copyable text.
The Jira-specific mode choice does not change repository readability behavior.
Style notes alone do not make source coverage incomplete. Complete primary
fields still receive full drafts when optional context fails or questions remain.
Preserve ambiguous wording rather than withholding a safe field merely because
overall status is incomplete.

## Risks / Trade-offs

- Shared instructions fail to load outside this repo → resolve installed config paths and test standalone/non-repository use; stop rather than silently fall back to duplicated criteria.
- Proposal changes technical intent → protected-content comparisons, ambiguous-source fixtures, explicit readiness status, and human approval; prompt-only semantic checks are not guarantees.
- ADF conversion loses rich structure → preserve links/code, disclose unsupported nodes, and withhold unsafe full-field replacements.
- Comments are partial or stale → explicit opt-in, snapshot metadata, count/pagination disclosure, and no automatic scope updates.
- MCP permissions vary across Code Mode/runtime versions → inspect effective permissions and test denied mutations before declaring the workflow read-only.
- Read-only review becomes a completeness/design audit → reuse the existing safeguards; demand only information needed to understand scoped text.

## Migration Plan

Ship shared criteria, repository reviewer extraction, and ticket command/agents together. Existing council outputs, selection, model, and writer stay unchanged. Run repository readability regressions before release. No Jira or report data migration is required. Roll back the ticket definitions and shared-criteria extraction together if loading fails.

## Open Questions

No product decisions block implementation. Validate the installed tool-action names, ADF response shape for comments/custom fields, and effective Code Mode permission enforcement during implementation. If the MCP provider cannot enforce the read-only allowlist, stop and propose a narrow validated retrieval tool rather than weakening permissions.
