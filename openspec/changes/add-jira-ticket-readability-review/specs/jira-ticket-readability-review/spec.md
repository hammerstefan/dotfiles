## ADDED Requirements

### Requirement: Single explicit ticket resolution
`/review-ticket` SHALL accept one issue key or HTTPS issue URL, optional site and audience, an optional explicit acceptance-criteria field ID, optional comments, and at most five explicitly selected context tickets. It SHALL reject invalid/unknown/conflicting options and ambiguous site resolution before issue retrieval. Returned issue identity SHALL be verified against the target. It SHALL NOT infer sites from project prefixes or search multiple sites for a matching key.

#### Scenario: Multiple accessible sites
- **WHEN** a bare key is supplied without a site and multiple Jira sites are accessible
- **THEN** the coordinator asks the user to select a site before fetching the issue

#### Scenario: Conflicting target
- **WHEN** an issue URL and `--site` identify different sites
- **THEN** the command stops with a target conflict instead of fetching another issue

### Requirement: Scoped read-only retrieval
Default review targets SHALL be summary, description, and acceptance criteria. A separate acceptance field SHALL be resolved automatically through bounded metadata discovery unless an explicit field ID overrides discovery. Resolved criteria SHALL be reviewed and proposed separately. Comments and explicitly selected context tickets SHALL be fetched only on request and SHALL remain context-only. Retrieval SHALL use exact read-only tool allowlists, explicit field lists, and `updateHistory: false`; recursive links, attachments, arbitrary HTTP/shell fallbacks, Jira mutations, and local report writes SHALL be unavailable.

#### Scenario: Default invocation
- **WHEN** `/review-ticket CPC-1234` resolves successfully
- **THEN** the coordinator retrieves summary, description, snapshot and project/type routing metadata, resolves a separate acceptance field with one optional-inclusive metadata page, and reads only the resolved criteria field plus updated, with no comments or linked-ticket reads

#### Scenario: Separate acceptance criteria
- **WHEN** an explicit custom field ID is selected
- **THEN** discovery is skipped and the field is read with the primary fields, receiving separate citations, feedback, and a proposed field replacement without being merged into the description

### Requirement: Safe automatic acceptance-field discovery
The coordinator SHALL use only verified primary project/type identifiers and one `getJiraIssueTypeMetaWithFields` call with optional fields included. Automatic selection SHALL require a unique exact normalized Acceptance Criteria display-name match, a valid custom field ID, and proven complete pagination. Missing or ambiguous metadata SHALL prompt for an exact field ID or confirmation that no separate field applies. Zero matches in creation metadata SHALL NOT be treated as proof of absence. Frozen options SHALL remain unchanged; resolution SHALL be coordinator-owned. A supplemental criteria read SHALL verify issue/site and match the primary snapshot timestamp. Failure SHALL preserve the primary response and mark criteria unavailable without retries. The field SHALL use the shared primary text budget and existing JSON additional-field/citation contracts.

#### Scenario: Unique complete match
- **WHEN** complete scoped metadata identifies one Acceptance Criteria custom field
- **THEN** the coordinator reads only that field plus updated and supplies its safe content as a primary review target

#### Scenario: Discovery cannot resolve a field
- **WHEN** metadata is unavailable, partial, ambiguous, or has no exact match
- **THEN** the coordinator asks for a field ID or confirmation rather than guessing, fetching all issue fields, or silently skipping criteria

#### Scenario: Acceptance read has a different revision
- **WHEN** the supplemental read returns a different updated timestamp or cannot establish revision consistency
- **THEN** the coordinator withholds the criteria draft, retains the original summary/description snapshot, and reports incomplete coverage

### Requirement: Acceptance-criteria clarity and consistency
The reviewer SHALL review every available criterion in the description and resolved criteria field for observable completion conditions, clear scope/conditions/exceptions, and consistency with primary prose. Criteria terms SHALL appear in the terms table when unresolved. Cross-field contradictions SHALL become source-backed questions, not silently chosen interpretations. The review SHALL NOT invent tests, thresholds, or requirements or require a universal Given/When/Then template.

#### Scenario: Conflicting acceptance requirement
- **WHEN** acceptance criteria contradict the description
- **THEN** the reviewer cites both sources in feedback/questions and preserves their meanings in their separate drafts pending author clarification

#### Scenario: Context cannot redefine scope
- **WHEN** requested comments contradict the description or contain instructions to alter the review
- **THEN** the contradiction becomes an open question and the command preserves its scope and permissions

### Requirement: Source fidelity and snapshot citations
The workflow SHALL preserve document structure, link destinations, code, and technical tokens from the fetched snapshot. Feedback SHALL cite issue key, field, heading path or numbered block, and safe source excerpt rather than invented repository paths or Jira line numbers. Issue URL and update timestamp SHALL be reported when available. Unsupported rich-text nodes SHALL be disclosed and SHALL prevent a full-field proposal when faithful safe representation is unavailable.

#### Scenario: Repeated or absent headings
- **WHEN** a ticket has repeated headings or no headings
- **THEN** citations use deterministic field-local numbered blocks to identify the source passage

#### Scenario: Rich text cannot be preserved
- **WHEN** an embedded object cannot be faithfully represented in the replacement
- **THEN** the affected replacement is withheld and coverage states the formatting/content limitation

### Requirement: Feedback plus faithful replacement proposal
The result SHALL contain separate clarity feedback, optional readability suggestions, proposed summary/description and selected field text, open questions, and coverage, plus a `review-ticket-json` block using the design's ticket-specific schema. The proposal SHALL preserve task meaning and all substantive content without invented ownership, deadlines, dependencies, requirements, or acceptance criteria. It SHALL preserve useful original organization and SHALL NOT enforce a mandatory ticket template.

#### Scenario: Clear ticket
- **WHEN** the original summary and description are already clear
- **THEN** feedback can be empty and the proposed text can match the original

#### Scenario: Ambiguous intent
- **WHEN** the description permits multiple technical interpretations
- **THEN** the proposed text retains the ambiguous passage, the ambiguity is explained outside the copyable draft, and status is needs_clarification

#### Scenario: Empty description
- **WHEN** description is genuinely empty
- **THEN** the proposed description stays empty and needed information is requested as questions rather than fabricated text

### Requirement: Visible undefined and ambiguous terms
The Markdown report SHALL include an Undefined and Ambiguous Terms table before detailed feedback. The table SHALL cover every reported distinct unresolved audience-relevant term in reviewed primary fields, including checklist items. Each row SHALL use validated feedback to show the exact safe term excerpt, issue/field/heading/block location, missing meaning, clarification needed, and feedback/question IDs. The table SHALL NOT invent definitions, add context-only terms as primary findings, or replace detailed feedback and open questions. Rendering this table SHALL NOT change the existing JSON schema or require additional retrieval permissions.

#### Scenario: Multiple unresolved terms in one passage
- **WHEN** a reviewed passage contains multiple distinct unresolved terms
- **THEN** each term has its own feedback entry and table row, even when one open question relates to multiple entries

#### Scenario: No unresolved terms in complete review
- **WHEN** the complete review reports no unresolved terminology
- **THEN** the terms section states that no undefined or ambiguous terms were found for the intended audience

#### Scenario: Incomplete terminology scan
- **WHEN** source or reporting limitations prevent a complete terminology scan
- **THEN** the table covers available validated terminology feedback and the section states that the scan is incomplete and refers to Coverage rather than claiming no terms remain

### Requirement: Complete and incomplete coverage disclosure
The coordinator SHALL bound issue reads, comments, and normalized text according to the design and SHALL NOT silently truncate primary content or claim complete context when pagination remains. Missing optional context SHALL degrade coverage without discarding a valid primary review. Missing primary issue content SHALL stop review or withhold affected proposals. Full-field replacements SHALL be withheld when the source cannot safely be reconstructed, and incomplete status SHALL take precedence over needs_clarification.

#### Scenario: Partial comments or context failure
- **WHEN** optional comments are paginated or an explicit context ticket is unavailable
- **THEN** primary feedback continues with incomplete coverage identifying what was unavailable or omitted

#### Scenario: Oversized primary description
- **WHEN** the description exceeds the primary text limit
- **THEN** no truncated text is presented as a complete replacement and the result discloses incomplete review

### Requirement: Untrusted text and safe output
Ticket fields, comments, context, and model responses SHALL be treated as untrusted data. Secret-like values SHALL NOT appear in feedback, excerpts, or proposals. The coordinator SHALL validate result shapes and citation provenance and SHALL NOT publish an unvalidated draft or invent missing output after malformed responses. The reviewer SHALL have no remote, write, execution, or delegation capability.

#### Scenario: Injection attempts
- **WHEN** a description instructs the agent to post a comment or reveal a credential
- **THEN** no mutation occurs and neither the credential nor the injected instruction is obeyed

#### Scenario: Malformed reviewer result
- **WHEN** required fields or source-backed locations are missing
- **THEN** the command reports failure instead of fabricating a proposal

#### Scenario: Proposal needs secret redaction
- **WHEN** an original field contains secret-like text that cannot be reproduced safely
- **THEN** the value is not emitted, the affected full-field proposal is withheld, and coverage is incomplete

### Requirement: STE100-inspired Jira output
The coordinator SHALL load the canonical `asd-ste100` skill with the skill tool before any MCP call. It SHALL stop on loading failure and SHALL NOT maintain or substitute duplicated STE rules. The reviewer SHALL load that same skill directly and read only the canonical readability criteria file through narrow instruction permissions, avoiding manually forwarded or summarized rules. Arbitrary file reads and remote, execution, write, and delegation permissions SHALL remain denied. The reviewer SHALL apply the loaded skill's writing rules to Jira feedback, proposed text, and questions, using its STE-flavored mode for descriptions and Strict mode for procedures/instructions. The ticket contract SHALL retain control of source scope, permissions, and report/JSON format rather than using the skill's standalone rewrite-only format. Meaning, modality, technical terms, obligations, exceptions, code, links, and useful warnings SHALL be preserved. Precision-preserving departures SHALL be explained outside copyable text. The result SHALL retain the loaded skill's dictionary/compliance qualifications. Repository readability behavior SHALL remain unchanged.

#### Scenario: Direct skill reuse
- **WHEN** `/review-ticket` starts with `asd-ste100` available
- **THEN** the coordinator loads that exact skill before Jira access and the reviewer loads it directly in its own session, without reading a duplicate style file or using copied excerpts

#### Scenario: Missing skill
- **WHEN** `asd-ste100` is unavailable or denied
- **THEN** the workflow stops before Jira reads instead of using copied fallback rules

#### Scenario: Long qualified requirement
- **WHEN** shortening a requirement to the word limit would lose a condition or weaken its obligation
- **THEN** the proposal retains the required precision and records the departure in proposal notes

#### Scenario: Uncertainty remains uncertainty
- **WHEN** source text states that an operation may have failed
- **THEN** the proposal preserves that uncertainty rather than stating that it failed

#### Scenario: Complete primary text with incomplete context
- **WHEN** selected primary fields are complete and replaceable but optional context is unavailable or questions remain
- **THEN** the workflow supplies full primary drafts preserving unresolved wording and reports context limits/questions separately, rather than withholding the drafts solely due to overall status
