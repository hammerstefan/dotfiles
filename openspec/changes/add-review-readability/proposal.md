## Why

The review council has no dedicated lens for human-facing language. Add the approved readability reviewer so unclear prose gets concrete, meaning-preserving feedback without treating editorial improvements as blocking defects or human-judgment requests.

## What Changes

- Add `review-readability` using `github-copilot/claude-opus-5.5` with read-only permissions and audience-aware sentence and document review.
- Include readability in every non-empty fixed-mode review; use content-based auto selection, respect `--only`, and exempt readability from the low-budget three-specialist limit.
- Keep substantive findings in the existing channel and introduce separately verified readability suggestions, unaffected by severity and finding limits or approval verdicts.
- Group above 50 suggestions, cap at 200 suggestions or file groups, and disclose incomplete coverage.
- Extend coordinator, triage, chair, and output templates; preserve prior-review routing and human-attention semantics.
- Add the reviewer name to the human-attention writer's accepted reviewer set, without adding editorial fields to persisted reports.

## Capabilities

### New Capabilities

- `review-readability`: Readability scope, criteria, safeguards, and separate substantive/editorial output contracts.
- `council-readability-integration`: Selection, dispatch, adjudication, rendering, failure isolation, and persistence compatibility.

### Modified Capabilities

None. Existing prior-review routing and retrieval requirements remain intact.

## Impact

Changes affect `config/opencode/agent/review-*.md`, council and review templates under `config/opencode/command/`, and the reviewer allowlist in `config/opencode/script/write-review-human-report.py`. Fixed fast-mode and low-budget reviews incur the accepted cost of an additional specialist. The chair result gains separate editorial and coverage collections; human-attention report fields stay unchanged. Validation combines executable persistence-contract checks with prompt-contract and behavior evaluations.
