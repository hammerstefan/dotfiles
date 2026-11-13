# Append inline comments to a pending review

Use this workflow only when step 2 of `SKILL.md` routed the skill into
**append mode**. That mode requires exactly one `PENDING` review owned
by the authenticated user to exist on the resolved pull request and
head SHA. The workflow adds new top-level comments to that review
through GraphQL. It never modifies the review's pre-existing comments,
summary body, or state.

This is a different capability from editing a single comment's body on
a session-created review. See
[`edit-session-review.md`](./edit-session-review.md) for that
workflow. Appending is purely additive. Body edits change one
existing comment.

## Auto-detect decision (mirrors step 2)

Build the candidate set from the PR's reviews:

- `.user.login == $login`
- `.state == "PENDING"`
- canonical `.pull_request_url` ends with `<owner>/<repo>/pull/<number>`
- `.commit_id == $head_sha`

Then:

| candidate count | mode |
| --- | --- |
| 0 | create (skip this doc) |
| 1 | append (continue) |
| 2+ | refuse. List each id. |

Wrong-owner and stale-head-SHA pending reviews do not enter the
candidate set and do not, by themselves, trigger refuse mode. Mention
them in the final response so the user knows why the workflow skipped
them.

## Pre-mutation invariants (mirrors step 5a)

Re-fetch the PR and the target review immediately before any mutation:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
gh api --hostname "$host" "repos/$repo/pulls/$pr" >"$tmpdir/pr-pre-mutation.json"
gh api --hostname "$host" "repos/$repo/pulls/$pr/reviews/$target_review_id" \
  >"$tmpdir/review-pre-mutation.json"
```

Require all of:

- the PR's `.head.sha` equals `$head_sha`
- the review's `.id` equals `$target_review_id`
- the review's `.user.login` equals `$login`
- the review's `.state` equals `"PENDING"`
- the review's `.commit_id` equals `$head_sha`
- the review's `.pull_request_url` ends with the resolved PR path
- the review's `.node_id` is present and well-formed (a string starting
  with `PRR_`)

If any verification fails, stop without mutation and report the
actual state.

## Append each comment (mirrors step 5b)

GitHub's REST surface cannot add a comment to an existing pending review.
The REST endpoint `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews`
creates a new review. There is no sibling endpoint that adds a comment
to an existing one. GitHub deprecated the older GraphQL mutation
`addPullRequestReviewComment` on 2023-10-01. The skill uses the modern
`addPullRequestReviewThread` mutation, sending one mutation per
appended comment.

The mutation input carries the target review's `node_id` (not the
numeric `id`), the comment's `path`, `line`, `side`, `body`, and
`subjectType: "LINE"`. A range comment also carries `startLine` and
`startSide`. The input never carries `inReplyTo`: every appended
comment is a top-level thread on the target review.

Build the GraphQL query string once, in a shell variable, so the loop
body stays small and the variable substitution stays in `jq`:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
query='mutation($input: AddPullRequestReviewThreadInput!) {
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
}'
```

Then loop over the verified comments. Build each payload with `jq`
using `--arg` and `--argjson`, capture the raw response, and only parse
after the process exits cleanly:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
target_review_node_id=$(jq -r .node_id "$tmpdir/review-pre-mutation.json")
count=$(jq 'length' "$tmpdir/comments.validated.json")
for index in $(seq 0 $(( count - 1 ))); do
  jq -n \
    --arg query "$query" \
    --arg node_id "$target_review_node_id" \
    --slurpfile comments "$tmpdir/comments.validated.json" \
    '{
      query: $query,
      variables: {
        input: (
          $comments[0][$index]
          | {
              pullRequestReviewId: $node_id,
              subjectType: "LINE",
              path: .path,
              line: .line,
              side: .side,
              body: .body
            }
          + (if has("start_line") then { startLine: .start_line, startSide: .start_side } else {} end)
        )
      }
    }' \
    --argjson index "$index" \
    >"$tmpdir/append-payload-$index.json"
  gh api --hostname "$host" graphql \
    --input "$tmpdir/append-payload-$index.json" \
    >"$tmpdir/append-response-$index.json"
done
```

A non-clean outcome on any iteration stops the loop without retrying.
Specifically the workflow treats all of these as a failed mutation:

- non-zero exit from `gh api graphql`
- a non-empty `errors` array in the GraphQL response
- a missing `thread` in the response
- the returned comment's id, path, line, side, startLine, startSide,
  or body not matching the request
- the returned comment's body not matching the request byte for byte

When a mutation fails, capture `index`, the requested comment, and the
raw response. Continue to verification with the responses that did land
and the missing response recorded as a failure. Do not retry. Do not
delete.

## Verification (mirrors step 7a)

Re-fetch the PR and the target review's comments from both endpoints:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
gh api --hostname "$host" --paginate \
  "repos/$repo/pulls/$pr/comments?per_page=100" >"$tmpdir/pr-comments.pages.json" \
  && jq -s 'add' "$tmpdir/pr-comments.pages.json" >"$tmpdir/pr-comments.json"
gh api --hostname "$host" --paginate \
  "repos/$repo/pulls/$pr/reviews/$target_review_id/comments?per_page=100" \
  >"$tmpdir/review-comments.pages.json" \
  && jq -s 'add' "$tmpdir/review-comments.pages.json" >"$tmpdir/review-comments.json"
```

Re-verify the PR's `head.sha` and the review's `state`, `commit_id`,
`user.login`, and `pull_request_url` against the values recorded in the
pre-mutation step. Any drift stops the workflow before running the
verifier.

Run the existing `scripts/verify_review.py` once over the appended
comments:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
python3 "<skill-directory>/scripts/verify_review.py" \
  --files "$tmpdir/files.json" \
  --comments "$tmpdir/comments.validated.json" \
  --remote "$tmpdir/pr-comments.json" \
  --remote "$tmpdir/review-comments.json" \
  --review-id "$target_review_id" \
  --head-sha "$head_sha" \
  --output "$tmpdir/verification-appended.json"
```

Then compare every comment in `$tmpdir/pre-existing-comments.json` (the
snapshot from step 2) against the remote comments on the same review.

The remote comments are the union of the pull-request-scoped and
review-scoped endpoints, merged by `verify_review.py`. The unchanged
verification filters the merged remote comments to those whose id
appears in the snapshot and compares the remaining fields:

| field | comparison |
| --- | --- |
| id | exact equality (the join key) |
| path | exact equality |
| line | exact equality, treating null as the absence of a line |
| side | exact equality (`LEFT`, `RIGHT`, or null) |
| start_line | exact equality, treating null as the absence of a range |
| start_side | exact equality (`LEFT`, `RIGHT`, or null) |
| body | byte-for-byte equality |

A pre-existing comment whose id is missing from the remote view is a
deletion. A pre-existing comment whose id is present and any other
field differs is a change. Either is a verification failure.

Write the result of the comparison as a JSON object:

```json
{
  "unchanged": [{"id": 1, "path": "src/example.py", "line": 6, "side": "RIGHT"}],
  "changed": [{"id": 2, "path": "src/other.py", "line": 12, "side": "RIGHT", "differing_fields": ["body"]}],
  "missing": [{"id": 3, "path": "src/another.py", "line": 4, "side": "LEFT"}]
}
```

A failure in either the appended-comment verification or the
pre-existing-comment unchanged comparison stops the workflow. The
skill never deletes the target review, never tries to delete
individual comments, never retries the failed mutation, and never
recreates the review. The remote state is the result.

## Endpoints the append path never calls

- `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events`
  (submit)
- `PUT /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}`
  (update summary body)
- `PUT /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/dismissals`
  (dismiss)
- `DELETE /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}`
  (delete the target review)
- `PATCH /repos/{owner}/{repo}/pulls/comments/{comment_id}` (edit a
  comment. Belongs to the edit workflow.)
- `PATCH /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}`
  (does not exist for this purpose)
- GraphQL `addPullRequestReviewComment` (deprecated on 2023-10-01)
- GraphQL `updatePullRequestReviewComment` (belongs to the edit workflow)
- GraphQL `addPullRequestReviewThreadReply` (the skill never replies to a
  pre-existing comment)
- GraphQL `submitPullRequestReview` (submit)

## Cross-links

- Body edits on a session-created review live in
  [`edit-session-review.md`](./edit-session-review.md). The append path
  does not edit any pre-existing comment, including one this session
  appended earlier.
- The skill reuses the bundled scripts `scripts/validate_comments.py`,
  `scripts/anchor_text.py`, `scripts/diff_positions.py`, and
  `scripts/verify_review.py` unchanged. They have no append-specific
  flags.
