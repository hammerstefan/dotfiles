# ses_e321ea872ffeuUyyOvuQCYo8WS: Issue #19 proxy binary integrity

## What the person asked for

- Message 1 (flat line 2), the hwt brief for ticket #19, "Decide the release integrity check for the proxy binary". Its Ask line: "@hwt for EACH ticket you identified".
- Message 2 (flat line 121): "continue"
- Message 3 (flat line 156): "create PR"
- Message 4 (flat line 172): "@review-deepseek changes in this branch"
- Message 5 (flat line 286): "rebase on main"

## What was produced, and whether it worked

- `adr/0004-the-plane-verifies-the-proxy-archive-against-a-pinned-digest.md`, the pin file `plane/proxy-digest.txt` holding one `sha256sum -c` line, and one row in `adr/README.md`.
- Commits `91065b7` and, after the review, `8496901` on `wayfinder/proxy-binary-integrity`, pushed. Rebased onto `main` as `a4029b3` and `20c4e42`, force-pushed with `--force-with-lease`. GitHub reported `MERGEABLE` and `CLEAN` after the rebase.
- Issue #19 resolved with comment 6814170196 and closed. One line appended to the map's `## Decisions so far`.
- PR #26, titled "Pin the proxy release digest for the plane". It is merged today as `482b80d`.
- The pin file is now at `plane/.workshop/iron-proxy/proxy-digest.txt`. ADR 0006 moved it after this session. ADR 0004 and the file on `main` carry the same digest, `46189e16f3f97319d68bc6a672f0be003bf8d2f2052ccd2be8cac00d8c3346b2`.
- Verified by the agent, first hand: the asset list at `v0.56.0` and at `v0.42.0`, the published `checksums.txt` fetched with `curl`, `.github/workflows/release.yml`, `sign-release.sh`, `install.sh`, `.goreleaser.yml`, `public-key.asc`, and the attestations API answer. The build probe ran in `/tmp/opencode/iron-proxy-build`: a shallow clone at the tag, a build with the snap Go 1.27.4, about 38 seconds, a binary of about 53 MB, and two builds with identical bytes. The `sha256sum -c` line format was tested against a dummy file, and a mismatch exits nonzero.
- Not verified: any archive download or binary run. The agent states it plainly: "The archive digest was read from the published records, not computed from the artifact."
- Not verified: any comparison of a build against the release archive. ADR 0004 records that as the accepted residual risk.

## Corrections the person made

- The agent closed the ticket with "No pull request opened." in its report. The person then wrote "create PR" (message 3, flat line 156).
- The agent reported "PR #26 ... is ready for your merge decision." The ticket said "do not rebase". The person then wrote "rebase on main" (message 5, flat line 286), and the agent rebased.
- No correction of the technical work by the person appears in this transcript. The two changes to the record came from the review child.

## Conventions, commands and values stated and written down nowhere

- Record number reservation, from the brief: "Two other sessions work in parallel on this map, so if you write a record, take number `0004`. It is yours alone."
- The branch and PR sequence: the brief says "Open no pull request. The person decides what merges." The person then asks for "create PR" and "rebase on main" on the finished branch. The same pattern appears in `ses_e321eb4dcffeOwt9gHumsL86cU`.
- The shared temp path is a real conflict, from the agent's own context summary: "**Parallel sessions share `/tmp/opencode/`**: my `/tmp/opencode/pr-body.md` was overwritten by the #17 session's PR draft. Never trust generic temp filenames; use unique ones." (flat line 284)
- The host `gh` version, from the agent's context summary: "`gh issue view`/`gh pr view`/`gh pr edit` with default fields fail with `GraphQL: Projects (classic) is being deprecated... (repository.issue.projectCards)`. Always pass explicit `--json` fields." (flat line 285)
- The workaround that worked for the pull request body: a GraphQL `updatePullRequest` mutation, because "`gh pr edit` in this gh version trips on the same deprecated field internally." (assistant, flat line 211)
- The claim limit the brief sets: "Name no release as verified unless the step that applies the check exists."

## Failures, their cause, and the fix

- `!! FAILED subagent` at flat line 390: `Invalid arguments for tool "subagent": - agent: Missing key`. The agent passed `description` and `prompt` and no `agent`. The fix was the same call with `"agent": "review-deepseek"`, which is logged as `ok subagent` at flat line 392.
- `!! FAILED edit` at flat line 394: `Could not find oldString in /tmp/opencode/pr-body.md. It must match exactly, including whitespace and indentation.` The cause was not the string. The file had been replaced by the parallel #17 session's draft. The agent's account: "The temp file was overwritten by the parallel #17 session writing its own PR body to the same shared path. I'll leave their file untouched and edit my PR body from the live copy instead, under a unique name." The fix was to read the live body with `gh pr view 26 --json body` into `/tmp/opencode/pr-26-body-integrity.md` and edit that.
- The review child's shells crashed on the same `projectCards` field. The parent's own first attempts at the body edit also failed: "The edit did not land. Re-running it alone to see the error." and then "`gh pr edit` in this gh version trips on the same deprecated field internally."
- The agent continued the crashed child instead of restarting it: "so I'll continue that session with the error and a workaround rather than redo its work."

## Candidate lessons

1. NEW. A parent repeats a child's "verified" only after the child's own tool log shows the command that produced the evidence. This session reported "Five-way agreement between the ADR, the pin file, the #19 resolution comment, the PR body, and the map line" (assistant, flat line 223) on the child's word. The child's tool log shows the shells for that read crashing, and shows later execute calls whose code was sent as a quoted string. (parent message 4 onward, child session `ses_e2ff70385ffezGBIMA57wXXcC7`)
2. NEW. A reviewer states a command as the source of a quote only when the command ran. The child wrote "Read with `gh issue view 19 --json comments --jq '.comments[-1].body'`" and quoted line numbers beside it, while its own shell for that call crashed. (child session, flat line 235)
3. NEW. Continue a crashed subagent session with the error and the workaround. Starting a new session pays for the work again. Quote: "so I'll continue that session with the error and a workaround rather than redo its work." (assistant, flat line 187)
4. NEW. Two sessions on one map must not share a generic temp file name. Quote: "Never trust generic temp filenames; use unique ones." (assistant, context summary, flat line 284)
5. NEW. On this host, `gh` with its default field set fails, and `gh pr edit` fails with it. Use explicit `--json` fields, and update a pull request body through the GraphQL `updatePullRequest` mutation. Quote: "`gh pr edit` in this gh version trips on the same deprecated field internally." (assistant, flat line 211)
6. NEW. A decision that changes how a sibling ticket verifies its work is reported, and the sibling's body is left to the person. Quote: "Ticket #18's body lists its digest comparison as 'against the published `checksums.txt`'. Under this resolution that comparison reads from `plane/proxy-digest.txt`. I did not edit #18's body, since the ticket rules forbid touching other tickets." (assistant, flat line 148)
7. NEW. A failed background review whose final answer omits which checks ran is answered with one question per check, each demanding "verified or not". Quote: "The subagent's final answer does not say whether the issue #19 and map-body consistency checks ever ran." (assistant, flat line 187)
8. ALREADY WRITTEN. The ADR numbering rule, which the agent applied during the rebase conflict. `adr/README.md` states "Records are numbered when they are written, not when they merge, so the index can skip a number that an open pull request has claimed."
9. ALREADY WRITTEN. The residual risk of a digest pin, the two GitHub records, and the rejected build-from-tag option. ADR 0004 states all three.
10. PROJECT-SPECIFIC FACT. The digest `46189e16...3346b2` for `iron-proxy_0.56.0_linux_amd64.tar.gz`. It is in the pin file and in ADR 0004.

## What should not become a skill

- The digest value and the pin file path. After ADR 0006 the path changed to `plane/.workshop/iron-proxy/proxy-digest.txt`, so the path in this session is history.
- The build measurements: 38 seconds, 53 MB, two identical builds from the snap Go 1.27.4. They are one run on one host, recorded in ADR 0004.
- The `gh` version on this host as a rule. `gh pr edit` failing on `projectCards` is a defect of one version, and it ends when the CLI is updated. It belongs in a note about the host, not in a skill.
