# ses_e2825bf41ffeA8YXsuDvQAuCWy: PR #74 rebase

## What the person asked for

- USER 1 (line 3): "rebase pr #74"

## What was produced, and whether it worked

PR #74 (`wrapup/docs-development-workshop-nested-lxd`) was rebased onto `main`
twice. The first rebase resolved a conflict in `AGENTS.md` and re-added two
host-tooling facts to `.kb/fence.md` and `.kb/issue-tracker.md`. `main` then
moved again while the agent worked, from PR #76. The agent re-rebased onto the
new tip `d3289e4`.

The agent reports (ASSISTANT, line 79): "PR #74 is rebased and conflict-free
again."

- The 5 commits replayed onto `d3289e4` (ASSISTANT, line 86).
- The push used `--force-with-lease` (ASSISTANT, line 73).
- `gh pr view` reported `MERGEABLE` and `CLEAN` (tool, line 184).
- `just test` printed 135 passed, with the PR's 18 new `test_writing_style.py`
  tests (ASSISTANT, line 88).
- `just style` reported only the 3 `carries` findings in `.kb/fence.md`, which
  the agent verified also exist on `main` (ASSISTANT, line 43).
- The temporary worktree `/tmp/opencode/pr74-rebase` and the scratch branch
  `tmp/rebase-pr74` were removed (tool, line 185).

The person issued one message and ran nothing. Every result above is the
agent's tool output, not a check the person ran.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

(none found)

The person stated no option, flag, path, ticket key, naming rule or workflow
rule. The single instruction is USER 1 (line 3).

## Failures, their cause, and the fix

- The `.kb/fence.md` edit failed. `!! FAILED edit` (line 132): "Could not find
  oldString in /tmp/opencode/pr74-rebase/.kb/fence.md. It must match exactly,
  including whitespace and indentation." The agent's `oldString` assumed a line
  wrap the file did not have. The fix was to `grep` the exact lines (line 134)
  and re-edit with the real text (line 138).
- The first push used a corrupted `--force-with-lease` expected head. Tool
  line 161 names the head
  `668c90e95c68aa5008817f7be9f7f7be9f7f7be9f7f7`. The agent then ran
  `git rev-parse origin/wrapup/docs-development-workshop-nested-lxd`
  (line 162) and re-pushed with the head
  `668c90e95c68aa50088bccff7ece379559fdce19` (line 163). The transcript prose
  does not record the first push failing. The tool log shows two push commands
  with different expected heads.

## Candidate lessons

- ALREADY WRITTEN: use a temporary worktree when two sessions need the same
  branch. `AGENTS.md` "Working rules" states it. ASSISTANT (line 9): "I'll
  rebase in a temporary worktree with a scratch branch, not touch that
  checkout."
- NEW: push a rebased branch with
  `git push --force-with-lease=<branch>:<old-head>`, and read the current
  remote head with `git rev-parse origin/<branch>` right before the push.
  ASSISTANT (line 73): "pushing the rebased branch with `--force-with-lease`,
  expecting the current remote head `9bc76be`". Tool (line 161, line 162,
  line 163).
- ALREADY WRITTEN: re-rebase onto the new tip when `main` moves mid-rebase.
  `.opencode/skills/merge-a-pull-request-stack/SKILL.md` "When `main` moves
  under the stack". ASSISTANT (line 57): "`main` moved mid-rebase (PR #76
  merged → `d3289e4`), so the PR is conflicting again."
- ALREADY WRITTEN: read the record on `main` before you amend a copy of it on
  your branch. `AGENTS.md` "Working rules" states it. The agent kept the PR's
  new bullets and re-added the PR's facts to the `.kb/` files where `main`
  moved them, and dropped the stale `AGENTS.md` bullets. ASSISTANT (line 21):
  "re-add the PR's new facts to the `.kb/` files where main moved them."
- NEW: a failed `edit` `oldString` usually mismatches the file's line wrap.
  `grep` the exact lines, then re-edit. Tool (line 132, line 134, line 138).
- ALREADY WRITTEN: run `just style <file>` on every changed Markdown file
  before a commit, and the checker flags the banned word `carries` and
  semicolons. `AGENTS.md` "Working rules" and `.kb/writing-style.md` "Banned
  words". ASSISTANT (line 29): "my edit added a semicolon". ASSISTANT
  (line 37): "The style check flags a semicolon in my edit."
- NEW: fix a style finding in an earlier commit by amending that commit with
  an interactive rebase, not by a later commit. ASSISTANT (line 39): "The
  semicolon is in commit 1 (e85390f). I'll amend it via an interactive rebase."

## What should not become a skill

- The `lxc` and `gh` CLI facts the session re-added. They are already written
  in `.kb/fence.md` "The LXD client it runs" and `.kb/issue-tracker.md`
  "Conventions". A skill that restates them adds nothing.
- The `carries` finding. It is already a rule in `.kb/writing-style.md`, and
  `scripts/check-writing-style.py` enforces it. It needs no new skill.
- The specific conflict resolution for PR #74, which bullets to keep and which
  to drop. That is one-off project state, not a repeatable rule.
- A single-pull-request rebase as its own skill.
  `.opencode/skills/merge-a-pull-request-stack/SKILL.md` already covers the
  rebase mechanics and the `main`-moved case.
