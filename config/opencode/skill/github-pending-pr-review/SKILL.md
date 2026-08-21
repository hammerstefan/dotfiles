---
name: github-pending-pr-review
description: Create or draft an editable, pending GitHub pull-request review with inline comments using gh api. Use whenever the user asks to prepare, create, or draft a PR review whose comments must remain editable in GitHub before submission, especially when they mention pending reviews, inline review comments, Files changed, or not publishing yet. Never submit, approve, request changes, or publish during the creation action.
compatibility: Requires authenticated GitHub CLI (gh), jq, Python 3, and network access to the target GitHub host.
---

# GitHub pending PR review

Create exactly one **PENDING** review containing validated inline comments. The
review remains unpublished so the user can inspect and adjust it in GitHub's
**Files changed** UI.

## Safety boundary

- Restrict mutations to creating the pending review explicitly requested by the
  user and, when transactional recovery requires it, deleting only the pending
  review created during the current invocation.
- Do not modify repository files, the index, branches, commits, remotes, or any
  other git state. Temporary files belong under `mktemp -d`, never in the repo.
- Never call the review submission endpoint, set `event`, approve, request
  changes, publish comments, or merge. Even if creation and submission are
  requested together, create only the pending review; submission requires a
  separate, later user action.
- Never delete or replace a review that existed before this invocation without
  the user's explicit approval. Never delete another user's review.
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
```

Each item has exactly:

- `path`: repository-relative path present in this PR's changed files
- `line`: positive integer blob line visible in the PR diff
- `side`: `LEFT` for a deleted line or `RIGHT` for an added/context line
- `body`: non-empty Markdown with the user's paragraph newlines preserved

Ask for missing or ambiguous values. Reject unsupported sides instead of
normalizing them. Treat a literal backslash followed by `n` as suspicious and
ask whether literal characters were intended; paragraph breaks must be real
newline characters.

## Workflow

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
gh api --hostname "$host" "repos/$repo/pulls/$pr"
```

Validate that its canonical repository/URL matches the resolved target, its
`number` matches, and `state == "open"`. Capture `.head.sha`, `.html_url`, and
`.changed_files`. Use the API head SHA, never a local checkout SHA. Immediately
before the POST, fetch the PR again and require the head SHA to remain equal;
otherwise stop and revalidate all anchors.

### 2. Snapshot existing reviews before any mutation

Fetch all review pages and combine the JSON streams safely:

```bash
reviews_before=$(gh api --hostname "$host" --paginate \
  "repos/$repo/pulls/$pr/reviews?per_page=100" | jq -s 'add')
```

Require this to be a JSON array. Record every existing review ID. Filter for
reviews where `.user.login == $login` and `.state == "PENDING"`.

- If one or more exist, do not create another. Report their IDs and ask whether
  the user wants to keep using the existing review or explicitly authorizes its
  replacement.
- Do not infer ownership from display names or URLs; compare authenticated
  login values exactly.

### 3. Fetch and validate the diff anchors

Fetch every changed-file page into a temporary JSON file:

```bash
gh api --hostname "$host" --paginate \
  "repos/$repo/pulls/$pr/files?per_page=100" | \
  jq -s 'add' >"$tmpdir/files.json"
```

Require the array length to equal the PR's `changed_files`. GitHub caps this
endpoint at 3000 files and may omit/truncate `patch`; if all files or an anchor
cannot be verified, stop rather than guessing.

Build the requested comments as JSON with actual newlines, then run the bundled
validator:

```bash
python3 "<skill-directory>/scripts/validate_comments.py" \
  --files "$tmpdir/files.json" \
  --comments "$tmpdir/comments.json" \
  --output "$tmpdir/comments.validated.json"
```

The validator checks schema, path membership, side, line, duplicate anchors,
body limits, suspicious literal `\n`, and whether each line/side pair is
commentable in the patch. Do not bypass a failure. If the user explicitly wants
literal backslash-n text, rerun with `--allow-literal-backslash-n`.

### 4. Preserve real paragraph newlines and construct JSON safely

Never interpolate comment text into JSON or shell code. Prefer `jq -n` with
`--arg`, `--argjson`, and variables containing real newlines. For example:

```bash
body=$'First paragraph.\n\nSecond paragraph.'
jq -n \
  --arg path 'src/example.py' \
  --argjson line 42 \
  --arg side 'RIGHT' \
  --arg body "$body" \
  '[{path:$path,line:$line,side:$side,body:$body}]' \
  >"$tmpdir/comments.json"
```

`jq` will serialize actual newlines as JSON escapes, which is correct. Do not
set `body='First paragraph.\\n\\nSecond paragraph.'`; that sends literal `\n`
characters. For user-provided multiline text, capture it without `eval`, then
pass it only as a quoted `--arg` value. Never deserialize executable formats or
pass comment data to a system command as code.

Construct the request from the validated comments. Keep the review summary body
empty unless the user specifically requested one; GitHub may not pre-populate a
pending review body in the final submission dialog.

```bash
comments=$(jq -c . "$tmpdir/comments.validated.json")
payload=$(jq -n \
  --arg commit_id "$head_sha" \
  --arg body "$requested_review_body" \
  --argjson comments "$comments" \
  '{commit_id:$commit_id,body:$body,comments:$comments}')
```

Inspect the payload structurally before POSTing: it must have the current
`commit_id`, the expected comment count, no `event` key, and comments identical
to the validated input.

### 5. Create one pending review

Save the raw response before projecting fields:

```bash
printf '%s' "$payload" | gh api --hostname "$host" --method POST \
  "repos/$repo/pulls/$pr/reviews" --input - \
  >"$tmpdir/create-response.json"
```

Do not pipe this POST directly into a jq projection. A successful creation
response can omit `.comments`; `.comments | ...` may then fail even though the
mutation succeeded. A formatting/projection failure is not a mutation failure.
After any non-clean command outcome, inspect remote state before retrying. Never
repeat the POST merely because output parsing failed.

Parse `.id`, `.state`, `.user.login`, and `.commit_id` if available, but use the
remote verification in the next step as the source of truth.

### 6. Verify remote state

Refetch all reviews and identify reviews satisfying all of these:

- ID was absent from the pre-mutation snapshot
- `.user.login == $login`
- `.state == "PENDING"`
- target PR is the resolved PR
- `.commit_id == $head_sha`

Require exactly one candidate and call it `created_review_id`. If there are zero
or multiple candidates, stop and report the actual state; do not retry or
delete anything automatically.

Fetch its inline comments from:

```text
GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/comments
```

Compare count and each comment's `path`, `line`, `side`, and `body` against the
validated request; require each API-returned `position` to be a positive integer
and retain it for the final report. Compare bodies exactly, including actual
newline characters. Also GET the review itself and reconfirm owner, PENDING
state, PR, and head commit.

### 7. Recover transactionally when newly-created content is wrong

GitHub documents `PATCH /repos/{owner}/{repo}/pulls/comments/{comment_id}`, but
PATCHing a comment that belongs to a pending review can return 404. Do not rely
on PATCH as the recovery path.

If verification shows wrong formatting/content during this invocation:

1. Re-fetch the review and its comments.
2. Require the review ID to be the unique new ID absent from the baseline,
   owned by `$login`, still `PENDING`, on the exact PR and expected head SHA.
3. Delete that review only with
   `DELETE /repos/$repo/pulls/$pr/reviews/$created_review_id`.
4. Verify that ID is gone and that no pre-existing review ID disappeared.
5. Rebuild bodies with real newlines, revalidate, recheck the PR head SHA and
   pending-review list, then create exactly once and perform full verification.

If any identity/state check fails, do not delete. Ask the user how to proceed.
A pending review found before this invocation is never automatic cleanup,
including one apparently owned by the same login.

## Final response

Report:

- repository and PR number
- pending review ID and `PENDING` state
- verified comment count
- each verified path, side, line and API-returned position, with confirmation
  that the body matched (do not unnecessarily repeat sensitive comment text)
- `<PR html_url>/files`
- “Nothing was published, submitted, approved, or marked as changes requested.”

Tell the user that pending inline comments can be reviewed and adjusted in the
GitHub **Files changed** UI before submission. Also warn that the pending review
summary body may not be pre-populated in GitHub's final submission dialog.

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
