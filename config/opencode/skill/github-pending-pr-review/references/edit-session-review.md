# Edit a comment on a session-created review

Use this workflow only when the user asks to edit an inline comment on a
pending review this session created. This is a body edit, not review creation
or transactional recovery. Do not delete and recreate the review.

## Check provenance

1. Find the successful creation response and verification in this session's
   own tool output. Record the host, repository, PR, review ID, owner, head
   SHA, and target comment ID. A user-supplied ID, a remote timestamp, or a
   matching login alone does not prove this session created the review.
2. Resolve the user's requested comment to exactly one comment ID and its
   original path, side, and line or range. If the request is ambiguous, ask.
3. If the creation response, verification, or target identity is unavailable,
   stop without mutation. Ask the user to edit the comment in GitHub's UI.

## Check current state

Use the private scratch setup and identity checks from the creation workflow.
Fetch the PR, review, changed files, and all pages of the review's comments.
Also fetch the pull-request-scoped comments as in creation step 7. Save the
complete review and comment snapshot before editing.

Require all of these conditions:

- The PR is open on the recorded repository and head SHA.
- The review ID is the one from this session's creation response. Its owner
  is the authenticated login, its state is `PENDING`, its PR is the recorded
  PR, and its commit is the recorded head SHA.
- The target ID belongs to that review and the authenticated user. Its anchor
  still matches the recorded path, side, and line or range. Verify the anchor
  against the current PR patch as in creation step 7.
- The target is still `PENDING`. Its GraphQL `viewerCanUpdate` is true.
- The complete comment snapshot is available. If a field, page, or anchor
  cannot be verified, stop without mutation.

Build the requested replacement body with real newlines. Preserve user-supplied
wording. Apply the suggestion contract when the skill drafts a replacement.
Run `validate_comments.py` on a one-item list with the original anchor and the
new body. Do not change the anchor as part of a body edit.

Immediately before mutation, fetch the PR, review, and target again. Require
the same head, owner, `PENDING` states, anchor, and original body. If any
changed, stop and ask the user. GitHub does not offer a conditional body update
in this mutation, so this check cannot eliminate a concurrent edit race.

## Update and verify

Use the target comment's verified GraphQL node ID, not its numeric REST ID, in
GitHub's `updatePullRequestReviewComment` mutation. GitHub documents the
mutation and its `pullRequestReviewCommentId` and `body` fields at
<https://docs.github.com/en/graphql/reference/pulls#updatepullrequestreviewcomment>.
Keep the body in a JSON file, not in shell code. For a validated one-item list:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
query='mutation($id: ID!, $body: String!) { updatePullRequestReviewComment(input: {pullRequestReviewCommentId: $id, body: $body}) { pullRequestReviewComment { id body state pullRequestReview { id state } } } }'
jq -n --arg query "$query" --arg id "$comment_node_id" \
  --slurpfile comments "$tmpdir/comments.validated.json" \
  '{query:$query,variables:{id:$id,body:$comments[0][0].body}}' \
  >"$tmpdir/edit-payload.json"
gh api --hostname "$host" graphql --input "$tmpdir/edit-payload.json" \
  >"$tmpdir/edit-response.json"
```

Save the raw response before inspecting it. Treat GraphQL `errors`, a missing
result, or a non-clean command as an uncertain outcome. Do not retry or delete
the review. Fetch the remote state and report what can be verified.

After a clean response, fetch the review and both comment endpoints again.
Verify the exact new body, target ID, original anchor, owner, PR, head SHA,
and `PENDING` state. Compare all other comments with the pre-edit snapshot by
ID, body, and anchor. If a comparison fails, report the mismatch and stop.
Do not overwrite another change or recreate the review. The remote state is
the result, even if verification fails.

Report the review ID and state, the changed comment's path and anchor, and
whether the new body and other comments were verified. State that nothing was
published, submitted, approved, or marked as changes requested. Link the PR's
**Files changed** view. Clean up only the scratch files created for this edit.
