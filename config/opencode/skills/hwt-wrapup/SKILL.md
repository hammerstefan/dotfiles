---
name: hwt-wrapup
description: Close a finished worktree by turning what its sessions showed into repo-level skills, guidance and memory. Use when the person types /hwt-wrapup, or says to wrap up a worktree, extract the lessons from this worktree's sessions, turn what happened here into a skill, or finish and close the worktree now that the work is done.
---

# Wrap up a finished worktree

A worktree's sessions hold what was learned in it: corrections the person made,
conventions they stated, commands that worked, traps that were hit twice. When
the work is done those sessions are the only record, and the worktree is one
more checkout in the sidebar. A wrapup turns them into a pull request against
the repository and then closes the worktree.

Two actors, and this skill is the first:

- **This session**, in the source worktree, runs `hwt-wrapup` once and reports
  what it decided. It owns no step of its own.
- **The reflection session**, in a worktree of its own, exports and reads the
  transcripts, writes the skills, guidance and memory, opens the pull request,
  and closes the source worktree. Its whole world is the brief the script
  writes for it.

## Why a script, not a conversation

A wrapup is triggered at the end of the longest session in the worktree, and the
harness re-sends that session's whole transcript on every turn. Measured on
monitor-agent's spike wrapup: eleven turns of orchestration at a 320k-token
context cost 3.6M input tokens — about $0.10, more than twice the whole
reflection session that did the actual work ($0.045 including its digest
subagent). Nine of those eleven turns had one right answer: the refusal checks,
the session list, the paths, the goal, the dry run, the spawn.

So those are a script, and one call replaces them. The judgement — what the work
taught, which lesson becomes a skill — stays in the reflection session, where
the context is fresh and the price is its own.

## Run it

```sh
hwt-wrapup --spawn              # wrap up and close the source worktree
hwt-wrapup --spawn --keep       # leave the source worktree open
hwt-wrapup --dry-run            # plan only: write the briefs, spawn nothing
hwt-wrapup                      # write the brief, print the plan
```

`--notes <file>` is the one place this session still contributes: a short
section, forty lines at most, for what the extraction cannot see — work that
landed on another branch or repository, a decision taken verbally, a trap that
is written down nowhere. Pass nothing when the plan already reads right; the
brief names the trigger session's whole export for the rest.

`--session <id>` names the trigger session; it defaults to this one.

## Refuse rather than guess

The script prints `wrapup: refused: <check>` and exits 3 when a check fails: not
in a linked worktree, a tool missing from `PATH`, `gh` unauthenticated, a wrapup
branch that already exists, an offline `git fetch`, a brief template it cannot
find, or a worktree where neither the trigger session's export nor any other
session can be read.

A worktree made by `hwt` usually holds one session — the trigger — and that is
not a refusal any more: its export is the brief's evidence, quoted and linked,
and the brief names it as the reflection session's one input.

## What the script decides, and what you report

The script lists the sessions — subagents included, the trigger session's own
tree excluded as orchestration — extracts the person's words and the files,
links and commits the trigger session produced, renders `brief.md` from
`brief.md.tmpl`, writes the goal, dry-runs `hwt`, spawns it, and prints the
plan: the wrapup branch and its checkout, the base, the sessions and their
sizes, the trace, the model, the space, and what happens next.

Report that in a few lines, then stop. Do not wait for the reflection session,
and write nothing into its checkout.

## The files

- `SKILL.md` — this.
- `brief.md.tmpl` — the reflection session's brief, with `{{PLACEHOLDER}}`
  sections the script fills. Change the wording here, never in a generated
  brief: the next wrapup overwrites that file.
