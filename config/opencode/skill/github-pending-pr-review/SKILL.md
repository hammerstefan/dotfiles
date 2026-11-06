---
name: github-pending-pr-review
description: Create or draft an editable, pending GitHub pull-request review with inline comments using gh api. A comment that proposes a concrete change carries a GitHub suggestion block the maintainer commits with one click, and a suggestion is never invented when the right change is not clear. Use whenever the user asks to prepare, create, or draft a PR review whose comments must remain editable in GitHub before submission, especially when they mention pending reviews, inline review comments, suggested changes, Files changed, or not publishing yet. Never submit, approve, request changes, or publish during the creation action.
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
- Never delete or replace a review that existed before this invocation, not
  even one the authenticated user owns. If a pending review already exists,
  stop, report its ID, and ask the user to delete it in the GitHub UI. The
  user performs that deletion, the skill proceeds afterwards.
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

### 2. Snapshot existing reviews before any mutation

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
reviews where `.user.login == $login` and `.state == "PENDING"`.

- If one or more exist, do not create another. Report their IDs and ask the
  user to delete them in the GitHub UI, then continue once they are gone.
- Do not infer ownership from display names or URLs; compare authenticated
  login values exactly.

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

### 6. Create one pending review

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

### 8. Recover transactionally when newly-created content is wrong

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

A pending review found before this invocation is never automatic cleanup, and
never a replacement target, including one apparently owned by the same login.

## Final response

Report:

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

Tell the user that pending inline comments can be reviewed and adjusted in the
GitHub **Files changed** UI before submission. A suggestion block can be
edited there before it is committed. Also warn that the pending review
summary body may not be pre-populated in GitHub's final submission dialog.

If a recovery failed after the created review was deleted, say so plainly.
Report what the remote state is, not what the workflow intended.

## Bundled scripts

- `scripts/validate_comments.py` checks the comment list against the PR's
  patches and writes the validated list.
- `scripts/anchor_text.py` prints the lines a comment covers, so that a
  suggestion block is built from the file and not from memory.
- `scripts/diff_positions.py` maps a diff position to a blob line and side.
  It also runs on its own with `--files`, `--path`, and `--position`.
- `scripts/verify_review.py` compares the remote comments with the request and
  reports what it could verify.

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
