# ses_e28a683a5ffe16KwNIwHs02TNE: A pull request is open from branch wrapup/docs-development-workshop-nested-lxd

## What the person asked for

This session is a wrapup reflection session. Its one USER turn is the
`hwt-wrapup` brief, not live typed words. The brief's ask:

- "You are wrapping up a finished git worktree. Its sessions hold what the
  work taught. Your job is to turn that into repo-level skills, guidance and
  memory. Then open one pull request and close the worktree." (line 5)
- Checkout, repository, branch and base: "Checkout:
  /home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/wrapup-docs-development-workshop-nested-lxd"
  and "Repository: /home/stefan.hammer@canonical.com/git/monitor-agent
  Branch: wrapup/docs-development-workshop-nested-lxd Base: origin/main".
  (line 9)

The person's own words, quoted inside the brief under "The person's words",
in order:

- `/wayfinder #44 #48` (line 28)
- "Correction to your brief, sent at the person's request: the `wayfinder`
  skill is installed at `~/.agents/skills/wayfinder`. Its frontmatter sets
  `disable-model-invocation: true`, so it does not appear in the model's skill
  catalog, and the brief's line saying it is not installed is wrong. Load it
  now with the skill tool, id `wayfinder`, and follow it: claim by assigning
  yourself, resolve on the ticket, close it, and append the map's line." (line 41)
- "reopen #48, workshop workshop.experimental-vms=1 is set. run your tests" (line 45)
- "skip todo 5, work on the other 4" (line 49)
- "what open should be handled under this ticket vs future ticket work?" (line 53)
- "make sure the future work is capture in extant or new tickets" (line 57)
- "does this correctly update the wayfinder map and set the dependency edges?" (line 61)
- "all changes up in PR?" (line 65)
- "where are the research findings recorded?" (line 69)
- "why does this not need merging to main?" (line 73)
- "research findings must be raised as PR to main. capture those instructions
  and perform" (line 77)
- "hwt-wrapup --spawn" (line 83)

## What was produced, and whether it worked

- Pull request #74 "monitor-agent: lessons from
  docs/development-workshop-nested-lxd", created then merged by the person at
  2026-11-14T02:55:37Z, merge `7e6ff4c`. (line 380)
- Pull request #89 "monitor-agent: correct the nested VM memory figure", open,
  not a draft, one file, a follow-up after #74 merged. (line 381)
- New skill `.opencode/skills/run-a-workshop-in-a-vm/SKILL.md`. (line 385)
- New section in `.opencode/skills/workshop-host-authority/SKILL.md`. (line 386)
- Script `scripts/check-writing-style.sh` and test
  `tests/test_style_script.py`. The report says another session later rewrote
  them as `scripts/check-writing-style.py` and `just style`. (line 387)
- AGENTS.md rules, `.kb/issue-tracker.md`, `.kb/writing-style.md` §6,
  `GLOSSARY.md`, and four Hindsight documents. (line 388)
- The source worktree `research-development-workshop-nested-lxd` closed. (line 410)

Verified:

- The objective check
  `gh pr list --repo hammerstefan/monitor-agent --head wrapup/docs-development-workshop-nested-lxd --state open --json number --jq 'length'`
  prints 1, and `gh pr view 89 --json number,state,isDraft` answers
  `#89 OPEN draft=false`. (line 369)
- `just style` on every changed file and both pull request bodies: 0 findings. (line 402)
- `just test` passes, with eight planted style defects and four clean drafts. (line 403)
- `ruff check .`: 6 findings before and 6 after, all outside the changed files. (line 404)

Not verified (line 398):

- The experimental-gate error text.
- The `workshop info` runtime line, which needs a VM.
- `lxc config device override`.
- `growpart`.
- The `pkexec` dismissal.
- The record's timings and memory figures.

The memory figure was later corrected: the record had labelled 5,617,856,512
bytes as 5.62 GiB, and the follow-up pull request states the bytes and 5.23 GiB
beside them. (line 558)

## Corrections the person made

These corrections were made to the trigger session and are quoted inside this
session's brief. This wrapup session had no live corrections. The two
`question` calls were cancelled by server restarts. (line 414)

- "Correction to your brief, sent at the person's request: the `wayfinder`
  skill is installed at `~/.agents/skills/wayfinder`." (line 41)
- "research findings must be raised as PR to main. capture those instructions
  and perform" (line 77)

## Conventions, commands and values stated and written down nowhere

- "make sure the future work is capture in extant or new tickets" (line 57).
  No file in the repository states that a research ticket's close-out must
  capture out-of-scope open items as new or existing tickets. A `grep` for
  "future" over `AGENTS.md`, `GLOSSARY.md` and `.kb/` finds nothing.
- The `hwt-wrapup` command and its flags: `--spawn`, `--dry-run`, `--keep`,
  `--notes <file>`, and exit 3 with `wrapup: refused: <check>`. (line 83)
  These live in the global dotfiles config, not in this repository.

## Failures, their cause, and the fix

- `!! FAILED webfetch` for
  `https://raw.githubusercontent.com/canonical/workshop/v0.9.9/internal/workshop/lxd/device.go`
  with "StatusCode: non 2xx status code (404 ...)". (line 490) Cause: the file
  is at `internal/workshop/device.go`, not under `lxd/`. Fix: the GitHub trees
  API (`git/trees/v0.9.9?recursive=1`) listed the `lxd` Go files, and the
  agent located `device.go` and `lxd_backend.go`. (line 492)
- `!! FAILED question` twice, both "Interaction cancelled because the location
  shut down". (line 546) Cause: server restarts cancelled the calls. Fix: the
  agent left the wrapup checkout in place and recorded one pending todo for the
  removal decision. (line 570)

## Candidate lessons

- A research ticket's close-out separates what the ticket handles now from
  future work, and future work goes into extant or new tickets. Quote "make
  sure the future work is capture in extant or new tickets" (line 57). NEW, not
  in the repository.
- Research findings reach `main` by a pull request from a `docs/<name>`
  branch, never by merging the research branch. Quote "research findings must
  be raised as PR to main. capture those instructions and perform" (line 77).
  ALREADY WRITTEN, `.kb/issue-tracker.md` "Research findings" and
  `.kb/spikes.md` §7.
- The `wayfinder` skill lives at `~/.agents/skills/wayfinder` with
  `disable-model-invocation: true`, so the catalog omits it but the `skill`
  tool loads it by id. Quote "the `wayfinder` skill is installed at
  `~/.agents/skills/wayfinder`" (line 41). ALREADY WRITTEN, `AGENTS.md`
  "Wayfinding".
- The lxd-vm opt-in is the snap option `workshop.experimental-vms=1`, set by
  root, followed by a daemon restart. Quote "reopen #48, workshop
  workshop.experimental-vms=1 is set. run your tests" (line 45). ALREADY
  WRITTEN, `.opencode/skills/run-a-workshop-in-a-vm/SKILL.md` and
  `.kb/privileged-conformance-suite.md`.
- A commit pushed to a branch after its pull request merged needs a new pull
  request. Quote "AGENTS.md says a commit pushed after its pull request merged
  needs a new pull request, so this is the follow-up." (line 381). ALREADY
  WRITTEN, `AGENTS.md`.
- State a size in the unit the command printed, or give the bytes beside the
  converted figure. Quote "The outer VM used 5,617,856,512 bytes against its
  6 GiB limit" (line 558). ALREADY WRITTEN, `.kb/writing-style.md` §6. The
  value 5,617,856,512 bytes equals 5.23 GiB, not 5.62 GiB, and that fact is a
  PROJECT-SPECIFIC FACT.
- A cancelled `question` call is a run limit, not an absent person. Quote
  "both `question` calls were cancelled by the server restarts" (line 414).
  ALREADY WRITTEN, `AGENTS.md` "Working rules".

## What should not become a skill

- The `hwt-wrapup` command and its flags (`--spawn`, `--dry-run`, `--keep`,
  `--notes <file>`, exit 3). (line 83) It is the global `hwt-wrapup` tool in
  the dotfiles config, not a monitor-agent concern.
- The measurement values and versions (lxc 6.10.1, workshop 0.9.9, kernel
  `7.0.0-42-generic`, 5,617,856,512 bytes). (line 396) These belong in the
  research record, not in a skill.
- The ticket numbers (#44, #48) and pull request numbers (#73, #74, #89).
  These are project records, not procedures.
