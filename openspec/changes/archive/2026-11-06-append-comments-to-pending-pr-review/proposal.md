## Why

`@github-pending-pr-review` refuses to do anything when a `PENDING` review already exists on the PR, even when that review belongs to the authenticated user and was opened in this or a previous session. The maintainer has to open GitHub, delete the pending review, and re-run the skill to add more comments, which loses the review summary body and any comments already in flight. The maintainer came back to the skill, so the natural next step is "add these comments to the review I left open", not "delete it first."

## What Changes

- Add an **append** workflow to the skill that adds new inline comments to an existing `PENDING` review the authenticated user owns on the same PR and head SHA, instead of refusing. Comments are added one at a time through the modern GraphQL mutation `addPullRequestReviewThread` (REST cannot add to a pending review; the older `addPullRequestReviewComment` GraphQL mutation was deprecated on 2023-10-01).
- The decision is **auto-detected** from the remote review snapshot:
  - 0 matching reviews => create a new pending review (current behavior).
  - exactly 1 matching review (login match, state `PENDING`, same PR, same head SHA, `viewerCanUpdate`) => append to it.
  - 2 or more matching reviews, or a single review owned by someone else, or a review on a stale head SHA => refuse and ask the user which review to keep or which to delete.
- The validator, suggestion-block contract, anchor check, and live-diff verifier are unchanged. Appended comments go through the same `validate_comments.py` and `verify_review.py` paths, with the same body and anchor rules.
- Verification also confirms every pre-existing comment on the target review is unchanged (same id, body, and anchor), so a successful append is reported as "the review now has these new comments, and the previous ones are still where they were."
- A failed append stops and reports. The skill never deletes the target review and never tries to remove individual comments (GitHub has no API for that), so a partial append remains so the user can fix or delete it themselves in the UI.
- Update evals that currently expect the skill to refuse on a pre-existing pending review (evals 2 and 6): with auto-detect, the skill now appends in those scenarios. Add new evals covering: exactly-one match appends; 2+ matches refuse; other-owner pending review refuses; stale head SHA refuses; pre-existing comments remain unchanged after an append; a failed append stops without deleting the review.
- Update the safety boundary to allow the append path while keeping the no-delete and no-submit rules intact. The other boundaries (no submission, no approval, no merge, no token handling, no edit of pre-existing comments, no commenting on someone else's review) are preserved.

## Capabilities

### New Capabilities

- `pending-pr-review-append`: The skill can detect a single pending review the authenticated user owns on the same PR and head SHA and append new inline comments to it through GraphQL, without touching the pre-existing comments and without submitting the review. The decision is auto-detected from the review snapshot.

### Modified Capabilities

<!-- No existing capability covers the create flow's spec-level behavior, so no existing spec needs a delta. -->

## Impact

- `config/opencode/skill/github-pending-pr-review/SKILL.md` — adds the append workflow path, updates the safety boundary, updates step 2 (mode detection), extends step 7 (verify pre-existing comments unchanged), updates step 8 (append recovery is stop-and-report, not delete-and-recreate), updates the Final response wording.
- `config/opencode/skill/github-pending-pr-review/references/` — new reference doc describing the append workflow (provenance, pre-mutation checks, the `addPullRequestReviewThread` mutation, verification of pre-existing comments).
- `config/opencode/skill/github-pending-pr-review/evals/evals.json` — replace or amend evals 2 and 6 (currently expect refusal on a pre-existing pending review); add new evals for the append path.
- No changes to `scripts/validate_comments.py`, `scripts/anchor_text.py`, `scripts/diff_positions.py`, or `scripts/verify_review.py` — the append path uses the existing scripts unchanged. The existing tests continue to pass.
- The skill is consumed by the dotfiles opencode config; no new dependencies. `gh api graphql` is already used by `references/edit-session-review.md`, so GraphQL invocation is a known capability of the environment.
- No external API other than GitHub's REST and GraphQL PR review endpoints, already in use.
