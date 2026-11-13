---
name: hwt-wrapup
description: Close a finished worktree by turning what its sessions showed into repo-level skills, guidance and memory. Use when the person types /hwt-wrapup. Also use when they say to wrap up a worktree or turn what happened here into a skill. Use it when they want the worktree closed now that the work is done.
---

# Wrap up a finished worktree

A worktree's sessions hold what was learned in it. They hold the corrections the
person made, the conventions they stated, the commands that worked, and the traps
they hit twice. When the work is done, those sessions are the only record. The
worktree is one more checkout in the sidebar. A wrapup turns the sessions into a
pull request against the repository and then closes the worktree.

Two actors, and this skill is the first:

- **This session**, in the source worktree, runs `hwt-wrapup` once and reports
  what it decided. It owns no step of its own.
- **The reflection session**, in a worktree of its own, exports and reads the
  transcripts. It writes the skills, guidance and memory. It opens the pull
  request and closes the source worktree. Its whole world is the brief the
  script writes for it.

## Why a script, not a conversation

The person starts a wrapup at the end of the longest session in the worktree.
The harness re-sends that session's whole transcript on every turn. We measured
monitor-agent's spike wrapup. Eleven turns of orchestration at a 320k-token
context cost 3.6M input tokens. That is about $0.10, more than twice the whole
reflection session that did the actual work ($0.045 including its digest
subagent). Nine of those eleven turns had one right answer. They were the
refusal checks, the session list, the paths, the goal, the dry run and the
spawn.

So those are a script, and one call replaces them. The judgement stays in the
reflection session: what the work taught, and which lesson becomes a skill. Its
context is fresh and the price is its own.

## Run it

```sh
hwt-wrapup --spawn              # wrap up and close the source worktree
hwt-wrapup --spawn --keep       # leave the source worktree open
hwt-wrapup --dry-run            # plan only: write the briefs, spawn nothing
hwt-wrapup                      # write the brief, print the plan
```

`--notes <file>` is the one place this session still contributes. It holds a
short section, forty lines at most, for what the extraction cannot see. That
includes work that went to another branch or repository, a decision taken
verbally, and a trap that is written down nowhere. Pass nothing when the plan
already reads right. The brief names the trigger session's whole export for the
rest.

`--session <id>` names the trigger session. It defaults to this one.

## Refuse rather than guess

The script prints `wrapup: refused: <check>` and exits 3 when a check fails.
The checks are:

- not in a linked worktree.
- a tool missing from `PATH`.
- `gh` unauthenticated.
- a wrapup branch that already exists.
- an offline `git fetch`.
- a missing brief template.
- a worktree where neither the trigger session's export nor any other session
  can be read.

A worktree made by `hwt` usually holds one session, the trigger. That is no
longer a refusal. Its export is the brief's evidence. The brief quotes and links
it, and it names the export as the reflection session's one input.

## What the script decides, and what you report

The script lists the sessions, subagents included. It excludes the trigger
session's own tree as orchestration. It extracts the person's words and the
files, links and commits the trigger session produced. It renders `brief.md`
from `brief.md.tmpl`, writes the goal, and dry-runs `hwt`. Then it spawns `hwt`
and prints the plan. The plan holds the wrapup branch and its checkout, the
base, and the sessions and their sizes. It also holds the trace, the model, the
space, and what happens next.

Report that in a few lines, then stop. Do not wait for the reflection session,
and write nothing into its checkout.

## What the reflection session must satisfy

The brief is a gate, not a wish list. Before the reflection session opens the
pull request, it must:

- run every example, and name the version and the subcommand behind every claim.
- read the existing conventions, and correct one there rather than repeating it.
- write a script for every mechanical check, and prove it fails on a planted
  defect.
- run the repository's test command and its linter, before and after the change,
  and justify each hard finding that remains.
- review its own change against five criteria: context efficiency, reliability,
  description and trigger, script, style.
- make the verdict agree with its findings.

The gate comes from a review of skills and guidance from an earlier wrapup. That
review found a false git example, host facts that no longer held, and a blanket
claim about a tool. `evals/` holds those lessons as assertions.

## The files

- `SKILL.md` — this.
- `brief.md.tmpl` — the reflection session's brief, with `{{PLACEHOLDER}}`
  sections the script fills. Change the wording here, never in a generated
  brief. The next wrapup overwrites that file.
- `evals/evals.json` — the assertions the brief must satisfy, one eval per
  lesson from that review.
- `evals/grade.py` — grades `brief.md.tmpl` and this file against them. Run it
  after a change to either. `--render` also renders a fresh brief and checks it
  for unfilled placeholders and missing steps:

  ```sh
  python3 <skill dir>/evals/grade.py
  python3 <skill dir>/evals/grade.py --render --worktree <a worktree>
  ```
