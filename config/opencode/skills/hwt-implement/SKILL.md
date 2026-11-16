---
name: hwt-implement
description: Implement tracker issues in their own hwt worktree sessions. One conflict plan covers the files, host resources and merge order the sessions share, and optional autonomous mode logs decisions for the person. Use for "/hwt-implement 111 115", "spawn sessions for these tickets", "implement these in parallel, autonomous". Use implement for work in this session.
---

# Hand issues to worktree sessions

One run turns a list of issues into N sessions. Each session gets a worktree, a
brief, a checkable goal, and a place in one conflict plan. Your work here is the
plan and the briefs. The sessions do the implementing.

The `hwt` skill owns the spawn mechanics: where the checkout goes, what the dry
run prints, and when `hwt` refuses. Read it once per run. This skill adds what N
sessions share: who owns which file, who holds which host resource, and who
merges first. It also sets what an away person reads on return.
## 1. Read the ask

Tickets are numbers. Two optional words switch on extra work:

- `autonomous` — the person is away. Add `references/autonomy.md` to every
  brief.
- `plan` — stop after the dry run. Spawn nothing.

Give one line back for anything else, such as a map number or a sentence: "Give
issue numbers, optionally with `autonomous` or `plan`." Spawn nothing. Each
spawn claims a branch and opens a space, so a guessed set costs real work to
undo.

## 2. Preflight every issue

```sh
python3 <skill>/scripts/hwt_implement.py plan 111 115 116 \
    --json <run>/plan.json
```

Put `<run>` outside the repository, for example
`/tmp/opencode/hwt-implement-<timestamp>`. The briefs, the manifest, and every
decision log then stay out of the tree and out of the pull request.

For each issue this prints the state, the assignees, the child count, the open
blockers, and the branch it derives from the title. It also prints whether that
branch or checkout already exists, the repository files the issue names, and the
host commands the issue names. The output ends with **contested files** (two
issues naming one file) and **shared host commands**.

Skip an issue that the tracker closed, one that another login claimed, or one
that still holds a `wayfinder:*` label. Skip it too when its branch or checkout already exists.
Report each skip in one line and carry on with the rest.

An **open blocker** is not a refusal when the person named the issue. Put it in
the brief, because the ticket's criteria may compare against work the blocker
has not done. Put it in the report too. Refuse the blocker, not the issue.

## 3. Pick the flow

- **No children** — one session per issue, running the `implement` skill.
- **Implementation children** — one session on the parent, running
  `implement-spec`. That skill owns the integration branch and its subagents.
  The conflict plan below applies to those subagents too.
- **A `wayfinder:*` child still open** — the map still has wayfinding work open.
  Skip the issue and name the open child.

## 4. Build the conflict plan

Five moves, in this order. Each one removes a collision the other sessions
cannot see coming.

1. **Claim the files.** The plan lists what each issue names. A name is a
   candidate, not proof. Give every contested file to exactly one session, the
   one whose acceptance criteria need it. Every other session gets a line in its
   brief. That file belongs to the other ticket, so state the needed diff in the
   pull request body instead of editing it.
2. **Name every host instance.** Give each VM, image alias, temp directory, and
   port the ticket number (`conf-vm-111`, `conf-image-117`). A generator that
   refuses a duplicate name turns a collision into a lost run. A shared name
   corrupts two runs, and both exit zero.
3. **Serialize what cannot be named.** Take one lock per shared resource with
   `mkdir`, and release it on every exit path. `references/host-locks.md` holds
   the protocol, including how to take over a stale lock with evidence. Put the
   lock path and the release line in each brief.
4. **Order the merges.** Owners merge before dependents. A dependent rebases
   afterwards. Put the order in the manifest and in every brief's sibling table,
   so each session knows whose pull request lands first.
5. **Fold or sequence irreducible overlap.** Two tickets may need the same
   region of one file. Then either one session covers both tickets on one
   branch, or the second session waits for the first merge. That choice changes
   scope, so the person makes it. Ask.

`plan` also chooses the base. It picks `origin/<default>` when the checkout sits
on another branch, so every pull request stays free of that branch's commits.
Report the base it chose, and why.

## 5. Write one notes file per issue

The notes file is the only per-issue prose. `render` injects the rest from one
template: header, rules, sibling table, host protocol, and autonomy. So the N
briefs cannot drift apart.

```markdown
## Why
Two to five sentences: what this issue delivers, for whom, and why.

## Files owned
`path/a.py`, `path/b.py` — the files this session edits, and no other ticket's.

## Host resources
What this session holds on the host: the lock path, and its instance name.

## What to do
1. Ordered steps, with the first one naming what to read.

## Extra rules
- Rules only this issue has.

## Done when
The observable end state, in prose, including the host left as found.

## Goal
One line: the command that decides the work is done, and what it prints.
```

Required sections: `Why`, `What to do`, `Done when`, `Goal`. Write `Done when`
and `Goal` together. They are one claim in prose and in a command. The reviewer
judges the command literally. "The work is complete" cannot be checked, so the
session loops. A goal naming `gh pr list --head <branch> --json isDraft` that
prints `false` can be checked.

For a repository that closes work with pull requests, the goal is the draft
check plus the evidence the body must carry. For a tracker without pull
requests, it is the open-child count. When the ticket's value is a number, such
as a measured duration, name that number in the goal sentence.

## 6. Render, dry-run, spawn

```sh
python3 <skill>/scripts/hwt_implement.py render \
    --plan <run>/plan.json --notes <run>/notes --out <run> \
    --autonomous --merge-order 115,111,116
python3 <skill>/scripts/hwt_implement.py spawn --out <run> --repo "$PWD" \
    --model "provider/model#variant"
```

`render` writes one `hwt-prompt-<slug>.md`, one `hwt-goal-<slug>.md`, and
`plan-rendered.json`. It fails when a notes section is missing, so a half-written
brief cannot go out.

`spawn` without `--go` runs each `hwt` dry run. It checks five lines before it
makes anything. The repository is this one, the checkout names this branch, the
goal shows exactly what you wrote, the Herdr space is named `#<issue> <words>`,
and focus stays where it is. That space name is the issue's number, then the
slug's first three words, hyphenated (`#115 monitor-eval-egress`): it groups the
session under its ticket in the sidebar, while the branch and checkout keep the
slug alone. Then it writes the printed checkout path into the brief. Read the
printed plan lines.

`spawn --go` makes the sessions. It also unsets the upstream that `hwt` pointed
at the base, so `git push` creates `origin/<branch>`. Without that, git refuses
the push and hints at the default branch. A refusal goes into the manifest, and
the loop moves to the next ticket. The loop retries nothing, and tries no
fallback branch.

Pass this session's own model, from
`opencode session export "$OPENCODE_SESSION_ID"`. Leave `--model` out when that
export is empty, and say the new sessions take the configured default.

## 7. Report

The manifest at `<run>/manifest.md` holds the plan, the branches, the checkouts,
the spaces, the conflicted files, and the refusals. Report from it:

- one line per session: ticket, branch, checkout, space name, model, brief, goal.
- one line per skipped issue with the reason, and any open blocker.
- the contested files and the session that owns each.
- the merge order.
- the decision-log directory, when autonomous.
- the retry command for each ticket `hwt` refused.

End with the todo list of work only the person can finish. A reviewer holds each
spawned session to its goal, so it works until that reviewer agrees the objective
is met. A decision it needs appears in the Questions panel.

## Plan mode

When the ask says `plan`, do steps 1 to 6 without `--go`. Report the plan and the
brief paths, and spawn nothing. Plan mode is also how to test a change to this
skill without making worktrees.

## Example

Ask: `111 115 autonomous plan`.

`plan` finds `monitor_agent/conformance/runner.py` named by both issues, plus one
conformance run each. The plan gives #115 ownership of `runner.py`'s `_exec_text`
and gives each session its own VM name and one shared lock. It orders #115 first
and drops both issues' blocked-by ticket into their briefs. The two notes files
carry the per-issue reason and steps. `render` fills the shared blocks, so the
sibling table reads the same in both briefs. `spawn` dry-runs both, prints the
two briefs and the plan, and stops.

## Files

- `references/autonomy.md` — the away-person protocol. The decision log, when to
  ask, bounded exploration, visible waiting, and the report section to read first.
- `references/host-locks.md` — naming and locking shared host resources.
- `references/brief-template.md` — the brief skeleton `render` fills.
- `scripts/hwt_implement.py` — `plan`, `render`, `spawn`.
