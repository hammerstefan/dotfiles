# ses_e28783289ffeXXihkFz6Kc9g0d: PR #74 review instructions

## What the person asked for

- USER 1 (line 3): `@review-agent-instructions pr #74`

## What was produced, and whether it worked

One review of PR #74 "monitor-agent: lessons from
docs/development-workshop-nested-lxd", then a fix run that closed every
finding, all without a second user turn.

The review read the PR at head `9ee0fa3` and returned "Not ready" with two
major findings, five minor findings, and two advisory findings. The two major
findings were a false `gh` version bullet in `AGENTS.md` and a duplicate
writing-style checker.

The fix run then did this work:

- Rebased the branch onto `origin/main`, dropping the duplicate bash checker
  commit `10ccbde` (line 116).
- Resolved `AGENTS.md` and `GLOSSARY.md` conflicts (lines 118, 138).
- Deduplicated the `user.workshop.projects`, `pkexec`, and VM bound rules
  across `AGENTS.md` and two skills (lines 142, 194).
- Reworded four quoted outputs that the cited record does not hold (line 196).
- Ported the test-count rule into `scripts/check-writing-style.py` with three
  tests (line 152, 192).

Five commits landed on `main` (lines 181-185): `95509e4`, `8f22783`,
`b95026d`, `fcf7360`, `668c90e`. The push was `9ee0fa3...668c90e` with
force-with-lease (line 166). The PR body was rewritten to match the new diff
(line 170).

Verified: `uv run pytest tests/` reports 132 passed (line 200). The style
checker reports 0 findings in 6 files (line 201). GitHub reports
`mergeable: MERGEABLE, mergeState: CLEAN` (line 205).

Not verified in this session: the four quotes the record does not hold were
reworded rather than measured, and the `pkexec` and registry-corruption
anecdotes are past events taken on record (line 82).

## Corrections the person made

(none found)

The person sent one message and made no correction. Every change in this
session is the agent's own claim.

## Conventions, commands and values stated and written down nowhere

(none found)

The one string the person used is the invocation itself, recorded above. All
commands and values in this session appear in ASSISTANT blocks and are the
agent's claims, not conventions the person stated.

## Failures, their cause, and the fix

No `!! FAILED` line exists in the tool log. The agent reported these failures
in its own prose.

1. Wrong linter count. Line 23: "Every file reports exactly 6 — that looks
   like I counted JSON structure, not findings." Cause: `ste-lint.py --json`
   wraps findings in a `violations` key, and the count read the top-level
   array. Fix: recount the `violations` array and split hard from advisory
   (line 25).

2. Shell quoting bug. Line 27: "Quoting bug in my one-liner — fixing it."
   Fix: rewrite the one-liner.

3. Rebase editor hang. Line 124: "The continue likely opened an editor. Let me
   check the rebase state and retry with a non-interactive editor." Cause:
   `git rebase --continue` opened an editor and hung. The hung continue then
   finished in the background and destroyed the rebase state. Line 128: "The
   rebase state got destroyed by the editor hang (HEAD is detached at
   `origin/main`, my resolution lost)." Fix: redo the rebase with
   `GIT_EDITOR=true` from the start.

4. Checkout aborted. Line 130: "The branch is checked out in a Herdr worktree
   owned by another session — that's why my checkout failed." Fix: leave that
   branch ref alone, build a new local branch, and push to the same remote
   branch.

5. Parallel run raced on a shared temp file. Line 19: "my parallel run raced
   on the temp file, so let me redo that check." The bash and Python checkers
   ran on the same temp file at once. Fix: rerun the check.

## Candidate lessons

- NEW — Run an interactive rebase or cherry-pick with `GIT_EDITOR=true` so it
  never opens an editor and hangs. Quote: "retry with a non-interactive
  editor" (line 124) and "Redoing it cleanly with a non-interactive editor
  from the start" (line 128).
- NEW — Drop one commit from a rebase by deleting its line with
  `GIT_SEQUENCE_EDITOR="sed -i '/10ccbde/d'" git rebase -i origin/main`
  (line 244).
- NEW — Preview a merge's content conflicts before rebasing with
  `git merge-tree --write-tree origin/main <head>` (line 229).
- NEW — Push a rebased PR branch with
  `git push --force-with-lease origin HEAD:refs/heads/<branch>` (line 288).
- ALREADY WRITTEN — A branch checked out in another session's worktree belongs
  to that session. Leave the ref alone and push from your own branch.
  `AGENTS.md` working rules, lines 97-100. Quote: "I'll leave that branch ref
  alone and work on my own local branch" (line 130).
- ALREADY WRITTEN — Read the record on `main` before you amend a branch copy
  of it. `AGENTS.md` working rules, lines 101-103. Quote: "`main`'s
  `AGENTS.md:102-105` already records the correction" (line 53).
- NEW — When two checkers do the same job, keep the stronger one and port the
  survivor's unique rule into it, instead of keeping both. Quote: "port the
  test-count rule into the Python checker" (line 63).
- NEW — A quoted command output in a skill must exist in the record it cites.
  Otherwise reword it as a plain statement. Quote: "Four quoted outputs in the
  new skill are not in the record it cites" (line 75).
- ALREADY WRITTEN — A temporary file that another session could write needs a
  unique name. `AGENTS.md` working rules, lines 114-115. Quote: "my parallel
  run raced on the temp file" (line 19).
- ALREADY WRITTEN — An upstream command name keeps its spelling even when it
  trips a synonym rule. `.kb/writing-style.md`, "Upstream terms". Quote: "an
  upstream command name, a justified departure (the alternative would misname
  the command)" (line 150).
- PROJECT-SPECIFIC FACT — The host runs `gh` 2.104.0 (with `--parent`) and
  `lxc` 6.10.1. `lxc config set -p` means `--property`, and `lxc exec` has no
  `-p`. These now sit in `AGENTS.md` after the fix. Quote: "Host probes
  confirm: `gh` is 2.104.0" (line 13).
- PROJECT-SPECIFIC FACT — `ste-lint.py --json` wraps findings in a
  `violations` key. Count the `violations` array, not the top-level JSON.
  Quote: "The JSON wraps findings in a `violations` key — my count was wrong"
  (line 25).

## What should not become a skill

- The host version values (`gh` 2.104.0, `lxc` 6.10.1, the `-p` flag
  meanings) are facts for `AGENTS.md` or a record, not a reusable procedure.
- The upstream `workshop` v0.9.9 `defaultDevices` behavior and the record's
  numbers (1 GiB default, 4 GiB set, 20 GiB disk, 8.7 GB usable) already live
  in `research/development-workshop-nested-lxd.md`.
- The specific findings and fixes of PR #74 are one-off work product.
- The dedupe decisions (`pkexec`, `user.workshop.projects`) restate rules
  already in `AGENTS.md`. Nothing new to teach.
