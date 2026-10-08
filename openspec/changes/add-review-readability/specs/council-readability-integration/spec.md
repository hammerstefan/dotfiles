## ADDED Requirements

### Requirement: Consistent readability selection
The council SHALL accept `readability` in `--only`. Explicit reviewer selection SHALL override modes and focus-driven selection. For non-empty scopes after exclusions, fixed `fast`, `standard`, and `full` modes SHALL dispatch readability. Auto mode SHALL select readability exactly when relevant human-facing text remains, inspecting content rather than extensions. A readability focus SHALL require the reviewer under automatic selection when relevant text remains. Readability SHALL be outside the three-specialist low-budget limit; `--no-human` SHALL skip only the post-chair human pass.

#### Scenario: Fixed modes and low budget
- **WHEN** any fixed mode reviews a non-empty machine-only scope with low budget
- **THEN** readability is dispatched and can return an empty result

#### Scenario: Auto relevance
- **WHEN** only generated, third-party, machine-only, or excluded human-facing content exists
- **THEN** auto mode does not select readability

#### Scenario: Explicit selection
- **WHEN** `--only security` or `--only readability` is supplied
- **THEN** exactly the named specialist is selected regardless of mode, budget, or readability focus

#### Scenario: Empty scope
- **WHEN** scope is empty after exclusions
- **THEN** no reviewer is dispatched and no artifact is created

### Requirement: Dispatch and failure isolation
The coordinator SHALL permit readability dispatch, pass the normalized contract, and validate findings and editorial channels independently. It SHALL pass both successful channels and any coverage limitations to the chair. Severity and finding limits SHALL apply only to substantive findings. Existing prior-review routing and untrusted-data rules SHALL apply to the new reviewer. Failures or malformed editorial output SHALL be disclosed without invalidating unrelated successful reviewers or valid finding output.

#### Scenario: Malformed editorial block
- **WHEN** readability returns valid findings but a malformed editorial block
- **THEN** findings remain eligible for chair verification and editorial coverage is marked failed with the reason

#### Scenario: Prior-review blindness
- **WHEN** prior-comments mode is evidence
- **THEN** readability receives no prior-review digest, like every other specialist

### Requirement: Independent editorial adjudication
The chair SHALL independently verify source existence, exact scope/exclusions, genuine readability value, meaning preservation, terminology, and duplicates. It SHALL reject unnecessary preferences and meaning-changing edits. Editorial suggestions duplicating a verified substantive finding from any reviewer SHALL be dropped before substantive filtering/limits. The chair SHALL extend `review-council-json` with separate `readability_suggestions` and `readability_coverage` fields without changing finding fields or verdict rules.

#### Scenario: Duplicate across reviewers
- **WHEN** a security finding and an editorial suggestion identify the same text and problem
- **THEN** the verified substantive finding is retained subject to normal filters and the editorial duplicate is dropped

#### Scenario: Editorial-only approval
- **WHEN** only verified editorial suggestions remain and no material substantive disagreement exists
- **THEN** the verdict is APPROVE and suggestions do not contribute to substantive counts

#### Scenario: Chair rejects invalid edits
- **WHEN** a suggestion changes MUST to SHOULD, cites excluded text, or chooses between equally clear alternatives
- **THEN** the chair rejects that suggestion

### Requirement: Separate presentation and persistence
Council and shared review templates SHALL render a `Readability Suggestions` section with exact locations, original excerpts, problems, and edits. Coverage SHALL disclose skipped, failed, incomplete, or complete readability review and preserve limitations. Human-attention dispatch SHALL forbid converting editorial items into human-attention items. The writer SHALL accept `review-readability` in selected/failed reviewer lists while retaining its existing persistence fields and rejecting editorial collections.

#### Scenario: Readability in council summary
- **WHEN** a non-empty human-attention report has readability among selected or failed reviewers
- **THEN** its summary is accepted with only existing fields and substantive finding IDs/counts

#### Scenario: Independent human review
- **WHEN** `/review-human` is invoked independently
- **THEN** it dispatches only the human-attention agent and persists no editorial collection
