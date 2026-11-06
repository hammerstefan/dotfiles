## Context

`@github-pending-pr-review` currently treats every pre-existing pending review as a blocker: if any review owned by the authenticated user is in `PENDING` state on the target PR, the workflow refuses to create or modify anything and asks the user to delete the review manually in GitHub's UI before re-running. The maintainer came back to add more comments; they came back because they wanted to add more comments, not because they wanted to delete the review and start over. The delete-and-recreate round trip discards the review summary body and any inline comments already drafted, and the skill has no way to recover them.

The REST surface cannot add comments to an existing pending review. `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews` creates a new review with inline comments; `PUT /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}` only updates the review's summary body; `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events` is the submit endpoint (the skill never calls it). The only path is GraphQL. The historical mutation `addPullRequestReviewComment` was deprecated on 2023-10-01 and replaced by `addPullRequestReviewThread`, which takes the same fields the existing validator already produces (`path`, `line`, `side`, `startLine`, `startSide`, `body`).

The append path must preserve the existing safety invariants: no submission, no approval, no merge, no delete of the target review, no edit of pre-existing comments, no commenting on someone else's review, no commenting on a stale head SHA. The validator, the suggestion-block contract, and the live-diff verifier are reused unchanged.

## Goals / Non-Goals

**Goals:**

- Auto-detect a single pending review the authenticated user owns on this PR and head SHA, and append new inline comments to it through GraphQL.
- Keep the existing create-new path working exactly as it does today for the zero-match case.
- Reuse `validate_comments.py` and `verify_review.py` unchanged; the append path produces the same validated JSON and runs the same verifier.
- Verify every appended comment (anchor, body, position) against the live diff.
- Verify that every pre-existing comment on the target review is unchanged after the append (same id, body, anchor).
- Surface a clear, deterministic refusal in the multi-match, wrong-owner, and stale-head cases, with the matched review IDs and the reason.
- Stop and report on any verification failure; never delete the target review; never try to delete individual comments (the API does not allow it).

**Non-Goals:**

- A `--review-id` flag for explicit targeting of a specific pending review. v1 is auto-detect only; users with multiple pending reviews disambiguate by deleting the unwanted ones in the GitHub UI first.
- Editing or deleting pre-existing comments on the target review. The body-edit workflow already lives in `references/edit-session-review.md` for session-created reviews; appending is purely additive.
- Updating the target review's summary body. The summary body is owned by the user; the GitHub UI is the natural place.
- Submitting, approving, dismissing, requesting changes, or merging. Those endpoints stay out of bounds.
- A batched GraphQL mutation that adds multiple threads in one call. One mutation per appended comment keeps verification atomic per comment and makes a partial append easier to report.
- Recovering from a partial append. GitHub has no API to delete individual review comments; the user must clean up manually in the UI.

## Decisions

### Auto-detect mode in step 2 (snapshot existing reviews)

After fetching all reviews on the PR (today's step 2), filter by the four predicates the proposal locks in: `user.login == $login`, `state == "PENDING"`, the canonical PR URL matches, and `commit_id == $head_sha`. The result is the candidate set.

- Empty candidate set => the workflow continues to step 6 as today, creating a new pending review.
- Exactly one candidate => the workflow enters the append path. The target review's `id` (numeric) and `node_id` (from REST `GET /reviews/{id}`) are recorded. All existing comments on that review are snapshotted (id, path, line, side, start_line, start_side, body) for the post-mutation unchanged check.
- Two or more candidates => refuse and report. The user disambiguates by deleting in the UI.

Rationale: this decision is made before any comment payload is built, so the validator, anchor text, and reviewer tooling see one consistent comment list regardless of mode. The same set of comments is what gets validated and verified in both modes.

Alternatives considered:
- A `--review-id` flag for explicit targeting: deferred to a later change. Auto-detect covers the common case (one pending review) and the multi-match case is rare enough that asking the user to clean up in the UI is acceptable.
- Match by GraphQL `viewerCanUpdate` instead of login equality: `viewerCanUpdate` is the authoritative check, but the REST snapshot already filters by login and the append mutation will fail server-side if the caller cannot update the review. Adding the GraphQL field check would double the calls in the common path.

### GraphQL `addPullRequestReviewThread` per appended comment

Each appended comment is sent as its own GraphQL mutation:

```graphql
mutation($input: AddPullRequestReviewThreadInput!) {
  addPullRequestReviewThread(input: $input) {
    thread {
      id
      isResolved
      comments(first: 1) {
        nodes {
          id
          databaseId
          path
          line
          side
          startLine
          startSide
          body
        }
      }
    }
  }
}
```

The `input` carries `pullRequestReviewId` (Node ID, not numeric), `path`, `line`, `side`, `body`, `subjectType: "LINE"`, and `startLine`/`startSide` when the comment covers a range. The numeric review id never leaves the script; the Node ID comes from the REST `GET /reviews/{id}` call.

Rationale: one mutation per comment keeps verification atomic and per-comment. A failed mutation on the third comment does not invalidate the first two. The `verify_review.py` helper already merges the review-scoped and pull-request-scoped comment shapes, so the existing verifier handles the response without changes.

Alternatives considered:
- A single `addPullRequestReviewThread` call that creates a thread containing multiple comments: not supported by the mutation. Each call creates one thread with one initial comment; replies are added through `addPullRequestReviewThreadReply`.
- The deprecated `addPullRequestReviewComment` mutation: deprecated on 2023-10-01; we do not use deprecated APIs when a non-deprecated equivalent exists.

### Pre-mutation invariant checks

Immediately before the first GraphQL call, re-fetch the PR and the target review. Require:

- The PR's `head.sha` matches the recorded `$head_sha`.
- The review's `id` matches the recorded numeric id; `user.login == $login`; `state == "PENDING"`; `commit_id == $head_sha`; the canonical pull request URL matches.
- The review's `node_id` is present and well-formed.
- The pre-existing comment snapshot is complete and every comment has an id, a path, a body, and an anchor.

If any check fails, the workflow stops without mutation and reports the actual state.

Rationale: a separate re-fetch closes the race between the step-2 snapshot and the first mutation. The cost is one extra REST call; the benefit is that the workflow will not append to a review that has changed underneath it.

### Post-mutation verification runs two checks

`verify_review.py` is run twice over the post-mutation comment list:

1. For every requested appended comment: anchor, body, and position match the live diff (existing behavior).
2. For every pre-existing comment on the target review: id, path, line, side, start_line, start_side, and body match the pre-mutation snapshot byte for byte.

Any failure in either check stops the workflow and is reported. The report distinguishes "appended comments that landed correctly", "appended comments that did not land", and "pre-existing comments that changed" so the user can act.

Rationale: appending must not be a vehicle for accidentally editing pre-existing comments. The unchanged check is the only way the skill can prove it did not modify a review it did not create.

### No recovery path for appends

A failed append is reported, not recovered. The skill does not delete the target review (it is not ours to delete), does not try to remove individual comments (no API exists), and does not retry.

Rationale: the alternative (delete the target review on failure) destroys the user's work. The non-recovery stance is the only stance that respects the provenance boundary: the skill only deletes content it created in the current invocation, and in the append case the skill did not create the target review.

Alternatives considered:
- "Delete the review if any appended comment failed verification": rejected. The review contains pre-existing comments that survived the user's previous workflow and must be preserved.
- "Retry the failed mutation up to N times": rejected. The existing safety rules (eval 13, `references/edit-session-review.md`) already establish that mutations are not retried; the same rule applies here.

### Safety boundary wording

The bullet that today reads "Never delete or replace a review that existed before this invocation, not even one the authenticated user owns" becomes "Never delete, replace, or modify a review that existed before this invocation, not even one the authenticated user owns." A new bullet is added: "In the append path, the skill may add new comments to a single pending review the authenticated user owns on this PR and head SHA. The skill never edits, deletes, or replies to a pre-existing comment on that review and never submits the review."

Rationale: the append path is a deliberate exception to the "never touch a pre-existing review" rule, but only in the additive direction. The new wording makes the additive-only invariant explicit.

### No script changes

`validate_comments.py`, `anchor_text.py`, `diff_positions.py`, and `verify_review.py` are reused unchanged. The append path produces the same validated JSON the create path produces; the verifier consumes the same JSON and the same remote shapes.

Rationale: keeps the change focused on the workflow and the safety boundary. The existing 110 tests stay green.

## Risks / Trade-offs

- [Partial append remains on the review] → The user cleans up in the UI. The final response names the appended comments that landed, the ones that did not, and the unchanged-sibling status so the user has the full picture.
- [Pre-existing comments were edited in the UI between snapshot and mutation] → The unchanged check catches it. The workflow stops and reports; the user can decide whether the in-flight append should still go through.
- [GraphQL rate limits] → The append path makes one mutation per comment, same effective rate as the create path's one REST call followed by per-comment reads. Acceptable.
- [Target review's `viewerCanUpdate` is false] → The GraphQL mutation returns an error; the workflow stops and reports. `viewerCanUpdate` is not pre-checked to keep the common path simple; the server is the source of truth.
- [Comments appended to a stale head SHA] → Mitigated by the head-SHA check at the snapshot filter and the pre-mutation re-fetch. A pending review whose head matches but whose diff positions are stale against a later force-push is out of scope; GitHub marks such comments outdated, which is the same behavior as a comment left in the GitHub UI.
- [Auto-detect cannot disambiguate two pending reviews owned by the same user] → The workflow refuses and lists both ids. The user deletes one in the UI and re-runs.
- [The skill cannot undo a partial append] → Documented in the final response and in the new reference doc. The user must delete the target review or revert the appended comments in the GitHub UI.
