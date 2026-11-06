---
name: github-pending-pr-review
description: Create, draft, or append to an editable, pending GitHub pull-request review with inline comments using gh api and the modern GraphQL addPullRequestReviewThread mutation. A comment that proposes a concrete change carries a GitHub suggestion block the maintainer commits with one click, and a suggestion is never invented when the right change is not clear. Use whenever the user asks to prepare, create, draft, or add to a PR review whose comments must remain editable in GitHub before submission, especially when they mention pending reviews, inline review comments, suggested changes, Files changed, or not publishing yet. When exactly one PENDING review owned by the authenticated user already exists on the same PR and head SHA, the skill appends the new comments to it; otherwise it creates a fresh pending review. Never submit, approve, request changes, or publish during the creation or append action.
compatibility: Requires authenticated GitHub CLI (gh), jq, Python 3, and network access to the target GitHub host.
---

# GitHub pending PR review

Create exactly one **PENDING** review containing validated inline comments. The
review remains unpublished so the user can inspect and adjust it in GitHub's
**Files changed** UI.

## Safety boundary

- Restrict mutations to creating the pending review explicitly requested by
  the user and, when transactional recovery requires it, deleting only the
  pending review created during the current invocation.
- Never delete, replace, or modify a review that existed before this
  invocation, not even one the authenticated user owns. The append path is
  the only exception, and only in the additive direction: it may add new
  top-level comments to a single pending review the authenticated user owns
  on this pull request and head SHA. The append path never edits a
  pre-existing comment, never replies to one, never updates the review's
  summary body, and never submits the review. When two or more pending
  reviews owned by the authenticated user match, stop, list each id, and
  ask the user to delete the unwanted ones in the GitHub UI before
  re-running.
- In the append path the skill uses the modern GraphQL
  `addPullRequestReviewThread` mutation to add one top-level comment at a
  time, and never the deprecated `addPullRequestReviewComment` mutation. The
  append path never calls
  `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events`,
  `PUT /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}`,
  `PUT /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/dismissals`,
  or `DELETE /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}`.
- Never delete another user's review, and never touch a submitted review.
  GitHub refuses to delete a submitted review, and this skill never asks it
  to.
- Do not modify repository files, the index, branches, commits, remotes, or any
  other git state. Temporary files belong in the private scratch directory of
  step 0, never in the repo.
- Never call `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events`,
  never send an `event` key in any request body, never approve, request
  changes, publish comments, or merge. Even if creation and submission are
  requested together, create only the pending review; submission requires a
  separate, later user action.
- Do not print tokens, credential variables, verbose authorization headers, or
  the output of commands that expose secrets. Use normal `gh` authentication.
- Fail closed on ambiguity, stale data, invalid anchors, unexpected ownership,
  or unverifiable remote state.

## Accepted input

Prefer a PR URL or an unambiguous repository plus PR number, followed by a
structured list:

```yaml
comments:
  - path: src/example.py
    line: 42
    side: RIGHT
    body: |-
      First paragraph.

      Second paragraph.
  - path: src/example.py
    start_line: 40
    start_side: RIGHT
    line: 42
    side: RIGHT
    body: |-
      A comment that covers the lines 40 to 42.
```

Each item has exactly:

- `path`: repository-relative path present in this PR's changed files
- `line`: positive integer blob line visible in the PR diff, the last line of
  the range the comment covers
- `side`: `LEFT` for a deleted line or `RIGHT` for an added/context line
- `body`: non-empty Markdown with the user's paragraph newlines preserved

A comment may also carry the two optional fields of a range comment, and they
come as a pair:

- `start_line`: the first line of the range the comment covers
- `start_side`: the side of that first line, the same value as `side`

A comment without `start_line` covers the single line that `line` names. A
comment with one covers every line from `start_line` to `line`, and that is
the range a suggestion block replaces.

Ask for missing or ambiguous values. Reject unsupported sides instead of
normalizing them. Treat a literal backslash followed by `n` as suspicious and
ask whether literal characters were intended; paragraph breaks must be real
newline characters.

## The suggestion contract

A comment that carries a `suggestion` block gives the maintainer a **Commit
suggestion** button: one click and the change lands on the branch as its own
commit, with the reviewer as a co-author. A comment without one asks for the
work in prose. The button saves a round trip, so the skill leans on it
whenever the replacement is clear.

**Leave a suggestion when the replacement is clear and available.** A comment
that proposes a concrete change to the lines it is anchored to carries a
`suggestion` block holding the complete replacement for those lines. The
replacement comes from the user, or from the file content and the diff, which
the workflow reads before the comments are written.

**Leave no suggestion when it is not.** An invented suggestion is worse than
none, because the maintainer can commit it with one click and it lands broken.
Write no `suggestion` block when:

- the right fix depends on knowledge the reviewer does not have
- several designs are equally reasonable and the choice belongs to the
  maintainer
- the change reaches another file, or lines that are not next to the anchor
- the replacement text would have to be made up to fill the block

In that case write the prose comment: open with the question, name the
problem, and quote the candidate change inline when there is one. A correct
prose comment always beats a one-click suggestion that silently corrupts the
file.

### How GitHub applies a suggestion

The block replaces the lines the comment is anchored to:

- `line` alone replaces that one line.
- `start_line` and `line` together replace the whole range between them.

So the block holds the complete replacement. Every line of the range that
stays has to appear in the block, and a line of the range that is missing from
the block is deleted when the maintainer commits the suggestion. Keep the
indentation of the anchored line, because the block replaces that line rather
than adding to it. Put the block last in the body and write the explanation
above it, the way GitHub's own comment box writes it, so that every
suggestion reads the same way in the **Files changed** UI. GitHub applies at
most one suggestion block per comment, and a suggestion cannot hang on a
deleted line, which has no new content to replace.

### The check before posting

Read every suggestion block as a replacement of the anchored range and ask
one question: does applying it produce exactly the code the comment
describes? Three failures are common.

- **A line disappears.** The range covers more lines than the block repeats.
  Repeat the lines that stay, or narrow the range to the line that changes.
- **The code is not the code described.** The block was written from the
  comment instead of from the file.
- **The block was made up.** The replacement text was guessed rather than
  taken from the file or the user. Remove the block and write prose.

The validator checks the mechanical parts of this. The rest is on the agent.

### Ask, then show

Open with the problem as a question the author can answer, and follow it with
the edit you would make:

````markdown
Could we name the provider here? A reader cannot tell which of the two
credentials this line refers to.

We could change this to:

```suggestion
The `jenkins.env` file in the `medic` Workshop holds these credentials.
```
````

"Could we" and "Should we" keep the comment a conversation. A bare "this is
wrong" makes the reader defend the code instead of reading the suggestion.

Keep the wording the user supplied. When the user hands over a body, use it
as it is, and do not rewrite it into a question or append a suggestion to it.
Only the comments the skill drafts itself carry the ask-then-show shape and
the suggestion contract.

A suggestion block is a claim about the file's content, so hold it to that
standard. It must keep the meaning of the line it replaces, it must not
silently drop a check, a guard, or an error path, and it must keep the
anchored line's indentation, because the block replaces that line rather
than adding to it.

## Workflow

### 0. Set up a private scratch directory

Every command below writes into `$tmpdir` and reads `$host`, `$repo`, `$pr`
and `$login`. Each command may run in its own shell, so keep those values in
a file that the later steps source.

Create the directory and the file:

```bash
umask 077
state="$HOME/.local/state/gh-pending-pr-review"
mkdir -p "$state" && chmod 700 "$state"
tmpdir="$(mktemp -d "$state/run.XXXXXX")"
printf 'tmpdir=%q\nstate=%q\n' "$tmpdir" "$state" >"$state/env.sh"
```

Every later command block starts by sourcing that file:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
```

Remove the state directory when the work is done:

```bash
rm -rf "$HOME/.local/state/gh-pending-pr-review"
```

Also turn on `set -o pipefail` in the shell that runs the fetches. It
matters because `gh api --paginate` writes each page as it arrives. Without
it, a page that fails to load looks like a complete but truncated answer.

### 1. Resolve identity, repository, and PR without guessing

Require `gh auth status --hostname "$host"` to succeed for the relevant host.
Resolve the login with `gh api --hostname "$host" user --jq .login`. Include
`--hostname "$host"` on every `gh api` call. Do not read or display token environment
variables.

If the user supplied a PR URL, resolve it with `gh pr view <url> --json
number,url`; derive `HOST/OWNER/REPO` only from the canonical returned URL. If
the user supplied `OWNER/REPO` and a number, use those exact values. Otherwise:

1. Resolve the current repository with `gh repo view --json nameWithOwner,url`.
2. Resolve the current branch's PR with `gh pr view --json number,url`.
3. If either fails or multiple interpretations remain, ask the user.

Fetch the canonical PR object using:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
gh api --hostname "$host" "repos/$repo/pulls/$pr"
```

Validate that its canonical repository/URL matches the resolved target, its
`number` matches, and `state == "open"`. Capture `.head.sha`, `.html_url`, and
`.changed_files`. Use the API head SHA, never a local checkout SHA. Immediately
before the POST, fetch the PR again and require the head SHA to remain equal;
otherwise stop and revalidate all anchors.

Keep the resolved identity in the scratch file, so that the later steps find
it in whichever shell they run in:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
printf 'host=%q\nrepo=%q\npr=%q\nlogin=%q\n' \
  "$host" "$repo" "$pr" "$login" >>"$state/env.sh"
```

### 2. Snapshot existing reviews and decide create vs append

Fetch all review pages and combine the JSON streams safely. Write the raw
pages to a file first, so that a failed page stops the workflow instead of
leaving a truncated array that looks complete:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
gh api --hostname "$host" --paginate \
  "repos/$repo/pulls/$pr/reviews?per_page=100" >"$tmpdir/reviews.pages.json" \
  && jq -s 'add' "$tmpdir/reviews.pages.json" >"$tmpdir/reviews.json"
```

Require this to be a JSON array. Record every existing review ID. Filter for
the **candidate set**: reviews where `.user.login == $login`,
`.state == "PENDING"`, the canonical `.pull_request_url` ends with the
resolved pull request's `<owner>/<repo>/pull/<number>` path, and
`.commit_id == $head_sha`. Do not infer ownership from display names or
URLs; compare the authenticated login value exactly and the canonical URL
byte for byte.

From the candidate set the workflow enters exactly one of three modes:

- **Zero matches** -> **create mode**. Continue to step 5 and create a new
  pending review through `POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews`.
- **Exactly one match** -> **append mode**. Continue to step 5a. Record the
  target review's numeric id and fetch its `node_id` with
  `GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}` (it is
  the `.node_id` field of the response, distinct from the numeric `.id`).
  Snapshot every pre-existing comment on that review into
  `$tmpdir/pre-existing-comments.json` as a JSON array of
  `{id, path, line, side, start_line, start_side, body}` objects, taken from
  the review-scoped endpoint
  (`repos/$repo/pulls/$pr/reviews/$review_id/comments`). The snapshot is the
  basis for the unchanged check in step 7a.
- **Two or more matches** -> **refuse**. Stop without mutation, list each
  matching review's numeric id and `commit_id`, and ask the user to delete
  the unwanted ones in the GitHub UI before re-running. The skill never
  picks one of the candidates on the user's behalf.

A pending review on the same PR whose `.user.login` differs from
`$login` is **not** in the candidate set. The skill never appends to it,
and its presence does not, by itself, trigger refuse mode. The skill
behaves as if the review did not exist; if the candidate set is empty the
skill creates a new review on top.

A pending review the authenticated user owns but whose `.commit_id` does
not match `$head_sha` is **not** in the candidate set. The skill never
appends to a stale review, and its presence does not, by itself, trigger
refuse mode. Report it so the user knows why it was ignored.

### 3. Fetch and validate the diff anchors

Fetch every changed-file page into a temporary JSON file, again checking the
exit status of the fetch before merging the pages:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
gh api --hostname "$host" --paginate \
  "repos/$repo/pulls/$pr/files?per_page=100" >"$tmpdir/files.pages.json" \
  && jq -s 'add' "$tmpdir/files.pages.json" >"$tmpdir/files.json"
```

Require the array length to equal the PR's `changed_files`. GitHub caps this
endpoint at 3000 files and may omit/truncate `patch`; if all files or an anchor
cannot be verified, stop rather than guessing.

### 4. Build the comment list with real newlines and validate it

Read the anchored lines before writing the bodies, so that every suggestion
block is built from the lines that are really there:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
python3 "<skill-directory>/scripts/anchor_text.py" \
  --files "$tmpdir/files.json" \
  --path 'src/example.py' \
  --line 42 \
  --side RIGHT
```

The output holds the exact lines a suggestion block replaces, and the range
that a range comment covers. A suggestion written from memory of the file is
a suggestion that lands wrong.

Never interpolate comment text into JSON or shell code. Prefer `jq -n` with
`--arg`, `--argjson`, and variables containing real newlines. For example:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
body=$'First paragraph.\n\nSecond paragraph.'
jq -n \
  --arg path 'src/example.py' \
  --argjson line 42 \
  --arg side 'RIGHT' \
  --arg body "$body" \
  '[{path:$path,line:$line,side:$side,body:$body}]' \
  >"$tmpdir/comments.json"
```

A comment that covers a range names its first line as well:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
jq -n \
  --arg path 'src/example.py' \
  --argjson start_line 40 \
  --argjson line 42 \
  --arg side 'RIGHT' \
  --arg body "$body" \
  '[{path:$path,start_line:$start_line,line:$line,side:$side,start_side:$side,body:$body}]' \
  >"$tmpdir/comments.json"
```

`jq` will serialize actual newlines as JSON escapes, which is correct. Do not
set `body='First paragraph.\n\nSecond paragraph.'`; that sends literal `\n`
characters. For user-provided multiline text, capture it without `eval`, then
pass it only as a quoted `--arg` value. Never deserialize executable formats or
pass comment data to a system command as code.

Now run the bundled validator over the list you just built:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
python3 "<skill-directory>/scripts/validate_comments.py" \
  --files "$tmpdir/files.json" \
  --comments "$tmpdir/comments.json" \
  --output "$tmpdir/comments.validated.json"
```

The validator checks schema, path membership, side, line, duplicate anchors,
body limits, suspicious literal `\n`, and whether each line/side pair is
commentable in the patch. A range has to cover lines that the diff really
holds, because GitHub anchors a comment on a contiguous run of them.

It also checks a suggested change against the lines it replaces: at most one
suggestion block per comment, no unclosed code fence, no suggestion on a
deleted line, which has no new content to replace, a fence that starts in the
first column, a block that is the last thing in the comment, a block that
changes something rather than repeating the anchored lines, and a block that
keeps the anchored line's indentation. Do not bypass a failure. If the user
explicitly wants literal backslash-n text, rerun with
`--allow-literal-backslash-n`. If the change is a deliberate re-indentation,
rerun with `--allow-indent-change`.

The validator reports how many comments carry a one-click suggestion, and it
notes a suggestion that is shorter than the range it replaces, because every
line of that range the block does not repeat is deleted when the maintainer
commits it. Read those notes before creating the review.

### 5. Construct the review payload safely

Construct the request from the validated comments. Keep the review summary body
empty unless the user specifically requested one; GitHub may not pre-populate a
pending review body in the final submission dialog.

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
comments=$(jq -c . "$tmpdir/comments.validated.json")
requested_review_body=""
payload=$(jq -n \
  --arg commit_id "$head_sha" \
  --arg body "$requested_review_body" \
  --argjson comments "$comments" \
  '{commit_id:$commit_id,body:$body,comments:$comments}')
```

Set `requested_review_body` to the user's text when they asked for a summary
body, and leave it empty otherwise. A range comment keeps its `start_line` and
`start_side` in the payload; they are the fields GitHub uses to anchor the
comment on the range that a suggestion replaces.

Inspect the payload structurally before POSTing: it must have the current
`commit_id`, the expected comment count, no `event` key, and comments identical
to the validated input.

When the workflow is in **append mode**, skip step 6 (it creates a new
review, which append mode never does) and continue with step 5a. When it
is in **create mode**, continue with step 6 and skip step 5a and step 5b.

### 5a. Pre-mutation invariants (append mode)

The target review's state may have changed between the step-2 snapshot and
the first GraphQL mutation. Re-fetch the PR and the target review
immediately before any mutation, and require all of these to be true:

- the PR's `.head.sha` equals `$head_sha`,
- the target review's `.id` equals the recorded id,
- the target review's `.user.login` equals `$login`,
- the target review's `.state` equals `"PENDING"`,
- the target review's `.commit_id` equals `$head_sha`,
- the target review's `.pull_request_url` ends with the resolved pull
  request's `<owner>/<repo>/pull/<number>` path,
- the target review's `.node_id` is present and well-formed (a string of
  the form `PRR_` followed by letters and digits, distinct from the
  numeric `.id`).

If any check fails, stop without mutation and report the actual state. Do
not proceed to step 5b with a stale snapshot.

Fetch the re-checked state into the scratch directory so a later step can
reconcile against it:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
gh api --hostname "$host" "repos/$repo/pulls/$pr" >"$tmpdir/pr-pre-mutation.json"
gh api --hostname "$host" "repos/$repo/pulls/$pr/reviews/$target_review_id" \
  >"$tmpdir/review-pre-mutation.json"
```

Read `.head.sha`, `.id`, `.user.login`, `.state`, `.commit_id`,
`.pull_request_url`, and `.node_id` from `$tmpdir/review-pre-mutation.json`
and verify them against the recorded values before sending any mutation.

### 5b. Append each comment with GraphQL (append mode)

GitHub's REST surface cannot add a comment to an existing pending review:
`POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}` does
not exist, and the older GraphQL mutation `addPullRequestReviewComment`
was deprecated on 2023-10-01. The skill uses the modern
`addPullRequestReviewThread` mutation, sending one mutation per appended
comment so verification stays atomic per comment and a partial append is
easy to report.

The mutation input carries the target review's `node_id` (not the numeric
`id`), the comment's `path`, `line`, `side`, `body`, and `subjectType:
"LINE"`. A range comment also carries `startLine` and `startSide`. The
input never carries `inReplyTo`: every appended comment is a top-level
thread on the target review.

Resolve the target review's `node_id` from the pre-mutation snapshot so
the GraphQL payload can reference it:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
target_review_node_id=$(jq -r .node_id "$tmpdir/review-pre-mutation.json")
```

Loop over the validated comments in order. For each comment, build the
GraphQL payload with `jq` and real newlines (exactly as step 5 does), save
the raw response, and parse it before sending the next one. A failed
mutation stops the loop without retrying; the skill does not delete the
target review or any individual comment and does not attempt to revert
the appended comments that did land. The `addPullRequestReviewThread`
GraphQL mutation takes the form:

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

A worked example for one appended comment, built from the validated
comment list, with `subjectType: "LINE"` and the target review's
`node_id`:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
query='mutation($input: AddPullRequestReviewThreadInput!) { addPullRequestReviewThread(input: $input) { thread { id isResolved comments(first: 1) { nodes { id databaseId path line side startLine startSide body } } } } }'
jq -n \
  --arg query "$query" \
  --arg node_id "$target_review_node_id" \
  --slurpfile comments "$tmpdir/comments.validated.json" \
  '{query:$query,variables:{input:{pullRequestReviewId:$node_id,subjectType:"LINE",path:$comments[0][0].path,line:$comments[0][0].line,side:$comments[0][0].side,body:$comments[0][0].body}}}'
```

A range comment extends the `input` with `startLine` and `startSide`:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
jq -n \
  --arg query "$query" \
  --arg node_id "$target_review_node_id" \
  --slurpfile comments "$tmpdir/comments.validated.json" \
  '{query:$query,variables:{input:{pullRequestReviewId:$node_id,subjectType:"LINE",path:$comments[0][0].path,line:$comments[0][0].line,side:$comments[0][0].side,startLine:$comments[0][0].start_line,startSide:$comments[0][0].start_side,body:$comments[0][0].body}}}'
```

Send each mutation, capture the raw response, and parse only after the
process exits cleanly. A non-clean outcome (non-zero exit, GraphQL
`errors`, missing `thread`, or the returned comment not matching the
request) stops the loop and reports which comments landed and which did
not. The full per-comment loop and response parsing are described in
`references/append-to-pending-review.md`; the workflow never reads a
GraphQL `errors` field as a success.

### 6. Create one pending review (create mode only)

Save the raw response before projecting fields:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
printf '%s' "$payload" | gh api --hostname "$host" --method POST \
  "repos/$repo/pulls/$pr/reviews" --input - \
  >"$tmpdir/create-response.json"
```

Do not pipe this POST directly into a jq projection. A successful creation
response can omit `.comments`; `.comments | ...` may then fail even though the
mutation succeeded. A formatting/projection failure is not a mutation failure.
After any non-clean command outcome, inspect remote state before retrying. Never
repeat the POST merely because output parsing failed.

Parse `.id`, `.state`, `.user.login`, and `.commit_id` if available. Keep the
response's `.id` as `posted_review_id`. It is the strongest link between the
review and this invocation, so hold on to it.

### 7. Verify remote state

Refetch all reviews into a new file. Keep the snapshot from step 2 intact,
because the checks below and the recovery in step 8 both compare against it:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
gh api --hostname "$host" --paginate \
  "repos/$repo/pulls/$pr/reviews?per_page=100" >"$tmpdir/reviews-after.pages.json" \
  && jq -s 'add' "$tmpdir/reviews-after.pages.json" >"$tmpdir/reviews-after.json"
```

Identify reviews satisfying all of these:

- ID was absent from the pre-mutation snapshot
- `.user.login == $login`
- `.state == "PENDING"`
- target PR is the resolved PR
- `.commit_id == $head_sha`

Require exactly one candidate and call it `created_review_id`. If there are zero
or multiple candidates, stop and report the actual state; do not retry or
delete anything automatically.

When the POST returned cleanly, `created_review_id` must equal
`posted_review_id`. A review that appeared in the meantime, for instance one
the user started in the Files changed UI, matches every other condition but
was not created here, so it is never adopted and never deleted. When the POST
outcome was not clean, do not adopt a candidate at all: reconcile the remote
state and ask the user.

Then fetch the review's comments from both endpoints:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
gh api --hostname "$host" --paginate \
  "repos/$repo/pulls/$pr/comments?per_page=100" >"$tmpdir/pr-comments.pages.json" \
  && jq -s 'add' "$tmpdir/pr-comments.pages.json" >"$tmpdir/pr-comments.json"
gh api --hostname "$host" --paginate \
  "repos/$repo/pulls/$pr/reviews/$created_review_id/comments?per_page=100" \
  >"$tmpdir/review-comments.pages.json" \
  && jq -s 'add' "$tmpdir/review-comments.pages.json" >"$tmpdir/review-comments.json"
```

The two endpoints return different shapes, and which one carries the anchor
depends on the review's state. In observed responses the pull-request-scoped
endpoint returns the full comment shape, with `line` and `side`. The
review-scoped endpoint returns the legacy shape, which holds the diff
`position` and omits `line` and `side`. A pending review's comments may appear
in either. Read both and let the verifier merge them.

Run the bundled verifier:

```bash
. "$HOME/.local/state/gh-pending-pr-review/env.sh"
python3 "<skill-directory>/scripts/verify_review.py" \
  --files "$tmpdir/files.json" \
  --comments "$tmpdir/comments.validated.json" \
  --remote "$tmpdir/pr-comments.json" \
  --remote "$tmpdir/review-comments.json" \
  --review-id "$created_review_id" \
  --head-sha "$head_sha" \
  --output "$tmpdir/verification.json"
```

The verifier establishes each comment's anchor from the API fields when the
API states them, and otherwise from the diff position mapped against the
file's patch. GitHub documents the position as the number of lines down from
the file's first hunk header, and `scripts/diff_positions.py` implements that
rule, including the detail that a later hunk header consumes a position. The
verifier requires the API fields and the mapped position to agree when both
are available, requires the body to match exactly, and reports the anchor of
every comment it could not verify. A comment that names a range is checked
against the start line the remote comment reports, because the range is what
a suggested change replaces.

Treat a non-zero exit as a failed verification. Do not report a comment as
verified when the verifier did not verify it, and do not describe a field the
API did not return as if it had. Say which evidence established each anchor:
the API fields, the diff position, or both.

Also GET the review itself and reconfirm owner, PENDING state, PR, and head
commit.

In **append mode** the verification has an additional check that step 7
does not perform: every pre-existing comment on the target review must be
unchanged from the snapshot taken in step 2. Continue with step 7a.

### 7a. Verify pre-existing comments are unchanged (append mode)

Append mode can only be reported as successful when the appended comments
landed on the requested anchors AND every pre-existing comment on the
target review is byte-for-byte identical to the snapshot. A changed
pre-existing comment means the append touched something the skill does not
own, and the workflow reports it as a failure.

Re-fetch the PR and the target review's comments from both endpoints,
using the same fetches as step 7 but with the target review's id
(`$target_review_id` recorded in step 2, not `$created_review_id`):

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

Re-confirm the PR's `head.sha` and the review's `state`, `commit_id`,
`user.login`, and `pull_request_url` against the values recorded in step
5a. Any drift stops the workflow before running the verifier.

Run `verify_review.py` once over the appended comments to confirm their
anchors and bodies landed:

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
snapshot from step 2) against the remote comments on the same review. A
pre-existing comment is unchanged when its id, path, line, side,
start_line, start_side, and body all match the snapshot. Write the
result of that comparison to `$tmpdir/verification-unchanged.json`. The
exact comparison logic is in `references/append-to-pending-review.md`.

The final report distinguishes the two outcomes:

- **appended-comment failures**: which requested comments did not land,
  with the discrepancy named (anchor, body, missing from remote).
- **pre-existing-comment changes**: which pre-existing comments changed,
  with the field that changed (id, path, line, side, start_line,
  start_side, or body) named.

A failure in either category stops the workflow. The skill never deletes
the target review, never tries to delete individual comments, never
retries the failed mutation, and never recreates the review. The remote
state is the result, and the report tells the user exactly what to clean
up in the GitHub UI.

### 8. Recover transactionally when newly-created content is wrong (create mode only)

Step 8 applies to **create mode only**. In **append mode** there is no
recovery: the target review was not created by this invocation and must
not be deleted, and GitHub offers no API to delete individual review
comments. A failed append is reported by step 7a, never retried, and
never recovered.

GitHub documents `PATCH /repos/{owner}/{repo}/pulls/comments/{comment_id}`, but
PATCHing a comment that belongs to a pending review can return 404. Do not rely
on PATCH as the recovery path.

If verification shows wrong formatting or content during this invocation:

1. Re-fetch the review and its comments.
2. Require the review ID to be `posted_review_id`, owned by `$login`, still
   `PENDING`, on the exact PR and expected head SHA.
3. Delete that review only with
   `DELETE /repos/$repo/pulls/$pr/reviews/$posted_review_id`.
4. Verify that ID is gone and that no pre-existing review ID disappeared.
5. Rebuild bodies with real newlines, revalidate, recheck the PR head SHA and
   pending-review list, then create exactly once and perform full verification.

The rerun writes to the same output paths as the first pass. The scripts
overwrite their output file, so a rerun is not blocked by the first run's
file. Do not carry a stale validation or verification report into the second
pass: run both scripts again and read the new reports. If a rerun fails it
writes no new report at all, so stop and fix the failure before creating
again.

If any identity or state check fails, do not delete. Ask the user how to
proceed.

A pending review found before this invocation is never automatic cleanup in
create mode, and never a replacement target, including one apparently owned
by the same login. In append mode the auto-detect decision in step 2 may
target a single such review; the workflow never deletes it, never edits
its pre-existing comments, never updates its summary body, and never
submits it.

## Final response

Report, in **create mode**:

- repository and PR number
- pending review ID and `PENDING` state, taken from the review GET
- verified comment count
- each verified path, side and line, with the API-returned position when the
  API returned one, and confirmation that the body matched (do not
  unnecessarily repeat sensitive comment text)
- which evidence verified each anchor, and any anchor that stayed unverified
- how many comments carry a one-click suggestion, so the maintainer knows
  which ones can be committed with the **Commit suggestion** button
- for every comment without a suggestion, one line on why: the change was not
  clear enough to suggest, the anchor is a deleted line, or the wording came
  from the user and was left untouched
- `<PR html_url>/files`
- “Nothing was published, submitted, approved, or marked as changes requested.”

Report, in **append mode**:

- repository and PR number
- target review id (numeric and `node_id`) and `PENDING` state, taken from
  the pre-mutation review GET
- count of appended comments that verified, and for each one the verified
  path, side, and line with the API-returned position when available and
  the body match confirmation (do not unnecessarily repeat comment text)
- count of pre-existing comments that verified unchanged, and the explicit
  list of any pre-existing comments that changed, with the field that
  changed (id, path, line, side, start_line, start_side, or body) named
- count of appended comments that did not land, with the discrepancy named
  (anchor, body, or absent from remote)
- how many appended comments carry a one-click suggestion, so the maintainer
  knows which ones can be committed with the **Commit suggestion** button
- for every appended comment without a suggestion, one line on why: the
  change was not clear enough to suggest, the anchor is a deleted line, or
  the wording came from the user and was left untouched
- `<PR html_url>/files#pullrequestreview-<target_review_id>` so the user
  jumps straight to the pending review in the Files changed UI
- “Nothing was submitted, approved, or marked as changes requested. No
  pre-existing comment was edited, replied to, or deleted. The review's
  summary body was not updated.”

If verification reported any failure, also report: a partial append cannot
be undone by the skill (GitHub has no API to delete individual review
comments and the skill will not delete the target review). Name the
appended comments that landed and the ones that did not, so the user can
clean up in the GitHub UI.

Tell the user that pending inline comments can be reviewed and adjusted in the
GitHub **Files changed** UI before submission. A suggestion block can be
edited there before it is committed. Also warn that the pending review
summary body may not be pre-populated in GitHub's final submission dialog.

If a recovery failed after the created review was deleted, say so plainly.
Report what the remote state is, not what the workflow intended.

## Bundled scripts

- `scripts/validate_comments.py` checks the comment list against the PR's
  patches and writes the validated list. Used unchanged by create mode and
  append mode.
- `scripts/anchor_text.py` prints the lines a comment covers, so that a
  suggestion block is built from the file and not from memory. Used
  unchanged by create mode and append mode.
- `scripts/diff_positions.py` maps a diff position to a blob line and side.
  It also runs on its own with `--files`, `--path`, and `--position`.
- `scripts/verify_review.py` compares the remote comments with the request and
  reports what it could verify. In append mode it is run once over the
  appended comments; the unchanged check for pre-existing comments lives
  in `references/append-to-pending-review.md`.

Each script writes its output file, overwriting what was there, so a rerun
after a recovery is not blocked by the first run's file. Each script exits
non-zero when it cannot do its job, and prints the reason on standard error.

Run the tests for all four from the skill directory:

```bash
cd "<skill-directory>" && python3 -m unittest discover -s tests
```

## Security notes

- Authentication and authorization are delegated to GitHub and `gh`; GitHub
  enforces repository permissions on every API call.
- Inputs are allowlist-validated before mutation, JSON is built with `jq`, and
  comment text is never evaluated as shell code.
- Review creation is rate-limited by GitHub; create once and never retry without
  reconciling remote state.
- Temporary files can contain review text. Use a private `mktemp -d`, set
  `umask 077`, install a cleanup trap, and do not log payloads in shared logs.
- The developer must configure least-privilege GitHub credentials, local log
  retention, and organization audit/IAM policy. This skill never handles or
  displays the credential itself.
