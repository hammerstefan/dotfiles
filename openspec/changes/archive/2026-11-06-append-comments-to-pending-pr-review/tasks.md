## 1. Update the safety boundary in SKILL.md

- [x] 1.1 Replace the bullet "Never delete or replace a review that existed before this invocation, not even one the authenticated user owns" with the additive-only wording that permits the append path while keeping no-delete, no-edit, and no-submit invariants.
- [x] 1.2 Add a new bullet to the safety boundary that describes the append path: the skill may add new top-level comments to a single pending review the authenticated user owns on this PR and head SHA, and never edits, replies to, or deletes pre-existing comments, never updates the review summary, and never submits.
- [x] 1.3 Preserve the existing "Never delete or replace another user's review" and "Never touch a submitted review" bullets unchanged.

## 2. Add the mode-detection decision to step 2 of the workflow

- [x] 2.1 Update the step-2 snapshot section to define the candidate-set filter: `user.login == $login`, `state == "PENDING"`, canonical `pull_request_url` matches the resolved PR, and `commit_id == $head_sha`.
- [x] 2.2 Replace the existing "If one or more exist, do not create another" rule with three explicit outcomes: zero => create mode, exactly one => append mode, two or more => refuse and list each id.
- [x] 2.3 State that on the exactly-one path the skill records the target review's numeric id and `node_id`, and snapshots every pre-existing comment (id, path, line, side, start_line, start_side, body) into the scratch directory for the post-mutation unchanged check.
- [x] 2.4 State that wrong-owner and stale-head-SHA pending reviews are excluded from the candidate set and do not, by themselves, trigger refuse mode.

## 3. Add the append-mode workflow steps

- [x] 3.1 Add a new sub-section "Append mode" after the existing step 5 (review payload construction) describing: pre-mutation re-fetch of the PR and the target review, the seven invariant checks, and the abort conditions.
- [x] 3.2 Add a worked GraphQL example for the `addPullRequestReviewThread` mutation showing the variables, the `input` payload (including `subjectType: "LINE"` and optional `startLine`/`startSide`), and the response query that returns id, databaseId, path, line, side, startLine, startSide, body.
- [x] 3.3 State that one mutation is sent per appended comment, in order, and that a failed mutation stops the workflow and is reported without retrying or deleting.
- [x] 3.4 State that the mutation payload is built with `jq` and `--arg` / `--argjson`, exactly as the create-mode payload is, so multi-line bodies round-trip through real newlines.
- [x] 3.5 Reference the existing `validate_comments.py` and `anchor_text.py` scripts as unchanged, so a maintainer reads them once for both modes.

## 4. Update step 7 verification for append mode

- [x] 4.1 State that in append mode `verify_review.py` is run twice: once to verify each appended comment against the request and the live diff, and once to compare every pre-existing comment against the pre-mutation snapshot by id, path, line, side, start_line, start_side, and body.
- [x] 4.2 Add a sub-check that distinguishes the two failure modes in the report: appended-comment failures vs pre-existing-comment changes, so the user can act on each independently.
- [x] 4.3 Require a fresh PR and review fetch immediately before the verification so the snapshot and the mutation are compared against the same remote view.

## 5. Update step 8 recovery rules for append mode

- [x] 5.1 State that the create-mode recovery (delete the review that this invocation created, then rebuild) does not apply to append mode: the target review was not created by this invocation and is not deletable.
- [x] 5.2 State that on any verification failure in append mode the skill stops, makes no further API mutation, does not retry the failed mutation, and reports the actual remote state.
- [x] 5.3 Spell out the report fields: appended comments that landed, appended comments that did not, pre-existing comments that are unchanged, pre-existing comments that changed (with the field that changed), the target review id, and the GitHub Files-changed URL.

## 6. Update the Final response wording

- [x] 6.1 Add an "append mode" branch to the final response that names the target review id (numeric and node), the count of appended comments that verified, the count of pre-existing comments that verified unchanged, and the GitHub Files-changed URL with `/files#pullrequestreview-<id>`.
- [x] 6.2 State in the final response that the skill made no submission, no approval, no merge, no summary-body update, and no edit or delete of pre-existing comments.
- [x] 6.3 Warn in the final response that a partial append (where some but not all comments verified) cannot be undone by the skill, and the user must clean up the partial state in the GitHub UI.

## 7. Write the reference doc

- [x] 7.1 Create `config/opencode/skill/github-pending-pr-review/references/append-to-pending-review.md` documenting: the auto-detect decision rule, the pre-mutation invariant checks, the GraphQL mutation shape, the per-comment send loop, the dual verification (appended vs pre-existing), the stop-and-report recovery stance, and the explicit list of REST and GraphQL endpoints the append path never calls.
- [x] 7.2 Cross-link from the new reference doc to `references/edit-session-review.md` so a reader knows that body edits on a session-created review are a separate workflow.

## 8. Update evals 2 and 6

- [x] 8.1 Amend eval 2 ("Put these review notes into an editable GitHub review, but I may already have a pending review on that PR. If so, don't create duplicates or remove anything without asking me.") so the expected output and expectations reflect auto-detect: when exactly one matching review exists, the skill appends; when zero or more than one exist, it refuses or creates without deleting.
- [x] 8.2 Amend eval 6 ("I already left a pending review on that PR yesterday. Delete it and put these new comments there instead.") so the expected output reflects auto-detect: the skill appends to that review rather than deleting it; the explicit "delete" instruction is refused because the review is not one the skill created in this invocation.

## 9. Add new evals for the append path

- [x] 9.1 Add an eval where the prompt says "add these comments to the pending review I left on this PR" with exactly one matching review, and the expected output is auto-append through GraphQL with verified comments and unchanged siblings.
- [x] 9.2 Add an eval where two PENDING reviews owned by the authenticated user exist on the PR; the skill refuses, names both ids, and asks the user to delete the unwanted ones in the UI.
- [x] 9.3 Add an eval where a PENDING review owned by another login exists; the skill ignores it and either creates a new review (if zero of the user's own match) or appends to the user's own matching review (if exactly one matches).
- [x] 9.4 Add an eval where the PR's head SHA has moved since the matching pending review was opened; the skill refuses and reports the head SHA drift.
- [x] 9.5 Add an eval where the append mutation succeeds but a pre-existing comment was edited in the UI between the snapshot and the post-mutation verification; the skill stops and reports the changed comment by id and field.
- [x] 9.6 Add an eval where one appended comment fails verification; the skill reports it as unverified, names the pre-existing comments that are unchanged, and does not delete the review.

## 10. Verify the existing test suite still passes

- [x] 10.1 From the skill directory, run `python3 -m unittest discover -s tests` and confirm 110 tests pass with no script change.
- [x] 10.2 Run `ruff check scripts tests references SKILL.md` (or the project's lint command) and confirm no new warnings.
