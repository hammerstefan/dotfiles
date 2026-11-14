# ses_e2d30ff01ffePWE31UOV5nrZ3d: Frontier ticket spawning with hwt

The session ran in the main checkout
`/home/stefan.hammer@canonical.com/git/monitor-agent`. It spawned the two
sessions in batch S12 and S11 from there.

Position references below name the user turn and the line in the flattened
transcript `flat/ses_e2d30ff01ffePWE31UOV5nrZ3d.txt`.

## What the person asked for

The first user message is the `/wayfinder-hwt` command text, pasted with
`Tickets:` set to `frontier`. It is the person's instruction for how tickets
are chosen and spawned, and the words are theirs:

- "Load the `hwt` skill with the skill tool, id `hwt`, and apply it once per ticket. It owns the branch naming, the dry-run-then-spawn sequence, and the refusal rules. This command adds the wayfinder part: which tickets, what each session is told, and what you report back."
- "Tickets:" then "frontier"
- "Numbers, with or without `#` (`20 21 24`), those tickets, in that order."
- "`frontier` alone, query the map for the tickets the person can pick up now, and confirm the list before spawning (step 3)."
- "`frontier` mixed with numbers, or any other word, say \"Give ticket numbers, or `frontier` alone.\" Report what was given and spawn nothing."
- "The frontier is the nodes with `state == OPEN`, no assignees, and no `blockedBy` node still `OPEN`."
- "Ask with the `question` tool, `multiple: true`: first option `All of them`, then one option per frontier ticket named by its title."
- "The four types, `research`, `prototype`, `grilling`, `task`, are all spawnable. A claimed ticket stays claimed: leave the assignee alone, leave an existing branch alone, and pick no substitute."
- "A refusal, non-zero exit, or a printed refusal, is recorded in `hwt`'s own words, and the loop continues with the next ticket. Nothing is deleted, no space is closed, no second branch is tried, and `--no-space` is not a fallback."
- "Then stop. The new sessions own the work: do not start it here, do not write into a new checkout, and do not wait for it."

The second user message is a follow-up question about three worktrees the
first report listed. USER 2 (line 254): "you idenditifed" the three paths,
then "do this need reconciling into main?"

## What was produced, and whether it worked

- The repository and the map were read from the checkout: one open map, `#1`
  "Map: the egress-controlled Hermes runtime".
- The frontier query returned two takeable tickets, `#18 Verify the v0.56.0
  binary in the plane workshop` and `#25 Run the acceptance task and enforce
  the proxy allowlist`. Both carry `wayfinder:task`.
- The agent asked with `question`, `multiple: true`, offering "All of them"
  first. The answer was "All of them".
- Preflight passed for both: open, unassigned, no open blocker, no branch and
  no checkout.
- Two briefs were written to `/tmp/opencode/hwt-prompt-iron-proxy-plane.md`
  and `/tmp/opencode/hwt-prompt-acceptance-task-proxy-allowlist.md`. Each was
  dry run with `hwt -n`, its `Checkout:` line was rewritten from the printed
  path, and then it was spawned with the same command and no `-n`.
- Both `hwt` calls passed `-r "$repo"`, `--agent opencode`, `--model
  minimax-coding-plan/MiniMax-M3.1-Flash#default` and `--task-file`. The model
  came from `opencode session export "$OPENCODE_SESSION_ID"`.
- The branches were `spike/iron-proxy-plane` and
  `wayfinder/acceptance-task-proxy-allowlist`. Their worktrees were under
  `~/.herdr/worktrees/monitor-agent/`, and each space took the branch name.
- The base for both was the `HEAD` of the main checkout, `7451cc7`. Verified:
  that commit is "Merge pull request #37 from hammerstefan/wayfinder/plane-workshop".
- The agent recorded both sessions with `trail_add`, each naming the map
  `hammerstefan/monitor-agent#1`.

What the transcript does not show: the exit status of either `hwt` call. The
commands appended `echo "EXIT=$?"`, and the tool log holds the input only. The
agent's report states that both sessions were running and that `hwt` printed
no refusal. Both branches exist in the checkout today, so both were created.
Neither worktree exists today, so both were removed in a later session.

The answer to the follow-up question, checked against the checkout today:

- `docs/adr-0006-review-notes`: 0 commits not in `main`, as the agent stated.
- `docs/adr-0001-workshop-user`: 0 commits not in `main`, as the agent stated.
- `research/web-egress-proxy`: 1 commit not in `main`, and its record is 584
  lines, as the agent stated.
- `adr/0001` links that record by blob URL on the branch, and `adr/0004` does
  the same for `research/workshop-definition-and-lifecycle`. Both links are in
  the files on `main`.
- Both `docs/` worktrees still exist. The agent offered to remove them and did
  not, because removal is a deletion.

## Corrections the person made

(none found)

The second message asks a question the first report did not answer. The report
named the three live worktrees without saying whether any of them was stale
against `main`. The person had to ask. That is a gap in the report, and not a
correction of a statement.

## Conventions, commands and values stated and written down nowhere

The ticket selection and spawning rules are the person's, and they are written
in the `/wayfinder-hwt` command file at
`/home/stefan.hammer@canonical.com/git/dotfiles/config/opencode/commands/wayfinder-hwt.md`:

- The four argument forms, the refusal line "Give ticket numbers, or
  `frontier` alone.", the frontier definition, the confirmation with the
  `question` tool, the preflight skip order and its wording, the branch forms
  `research/<slug>` and `wayfinder/<slug>`, the slug rules, the model string,
  the dry run, the refusal handling, the brief skeleton, and the report shape.
- That file has changed since this session. It now also holds a goal file per
  session, a `todowrite` step before the report, and a section on the
  `wayfinder` skill's `disable-model-invocation: true` flag.

These came up in this session. The file that holds each one is named where a
file holds it.

- A spike ticket takes the branch that `.kb/spikes.md` §2 fixes, over the
  command's slug rule. Exact words: "`#18` is a spike, and both its own body
  and `.kb/spikes.md` §2 name the branch: \"It lives on branch `spike/iron-proxy-plane` with its directory at `spike/iron-proxy-plane`\"."
  §2 holds the branch form. No file states that it wins over a spawning rule.
- A version number in a ticket title cannot form a slug: "The slug rule would
  also have produced an illegal slug, since `v0.56.0` carries dots that
  `[a-z0-9-]` rejects." No file states this case.
- A spike ticket still has the `wayfinder:task` label. No file states which
  label a spike ticket takes.
- A live worktree outside the `wayfinder/*` and `research/*` families is
  reported too: "The last one is a `docs/` branch, so it is outside the
  `wayfinder/*` and `research/*` set the report names, but it is a live worktree of this repository."
  The command's report list names the two families only.
- A merged `docs/*` branch is cleanup, while a `research/*` branch is kept
  because a record on `main` links its file by blob URL: "Research branches
  are throwaway records. They are pushed and never merged, which is why four
  other `research/*` branches sit in the same state." The agent's operand for
  keeping one: "Deleting the branch breaks that link." No file states a branch
  lifetime rule for `research/*`.
- The installed `gh` is 2.45.0, which the command text states: "`gh` 2.45
  reads `blockedBy`". `.kb/issue-tracker.md` documents `gh issue edit
  --add-blocked-by` and `gh issue create --blocked-by` for `gh` 2.94 and later.
  The knowledge base names no version for the host.

Values the agent stated:

- The report line for `#18` names `spike/iron-proxy-plane`. The report line
  for `#25` names `wayfinder/acceptance-task-proxy-allowlist`.
- The base is `7451cc7`.
- The worktrees already running were `docs/adr-0006-review-notes` at
  `/home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/docs-adr-0006-review-notes`,
  `research/web-egress-proxy` at `/tmp/opencode/web-egress-proxy`, and
  `docs/adr-0001-workshop-user` at
  `/home/stefan.hammer@canonical.com/.local/share/opencode/worktree/8f03a8/adr-0001-workshop-user`.

## Failures, their cause, and the fix

(none found)

No tool call in this session is recorded as failed. The exit status of the two
`hwt` calls is not in the transcript, so the spawn's success rests on the
agent's report and on the two branches that exist today.

## Candidate lessons

Positions name the user turn and the line number in the flattened transcript.

- NEW: A spike ticket takes its branch from `.kb/spikes.md` §2, and the slug
  rule of the spawn command does not apply. Quote: "The generic rule gives
  `wayfinder/<slug>` for a task ticket. `#18` is a spike, and both its own body
  and `.kb/spikes.md` §2 name the branch" (line 235). `.kb/spikes.md` §2 fixes
  the branch form and states no precedence over a spawning rule. The command
  file holds no spike case.
- NEW: A version number in a ticket title cannot form a slug, so the branch is
  read from the ticket before the slug is derived. Quote: "since `v0.56.0`
  carries dots that `[a-z0-9-]` rejects" (line 235).
- NEW: A `research/*` branch stays after its record is committed on `main`
  because a decision record links the file by blob URL on that branch, while a
  merged `docs/*` branch is cleanup. Quote: "Deleting the branch breaks that
  link." (line 296). I checked that `adr/0001` and
  `adr/0004` hold such links. No file states the branch lifetime as a rule.
  `.kb/spikes.md` §7 states it for spike branches only.
- NEW: A report of spawned sessions says which live worktrees are already
  merged into `main`, because the person asked that next. Quote, USER
  2: "do this need reconciling into main?" (line 260).
- NEW: The installed `gh` is 2.45.0, so the blocking flags that
  `.kb/issue-tracker.md` documents for `gh` 2.94 and later are absent, and a
  read of blockers needs a GraphQL `blockedBy` query. Quote: the person's
  "`gh` 2.45 reads `blockedBy`" (line 33). The dotfiles command states it for
  this host. The knowledge base does not.
- ALREADY WRITTEN (`/home/stefan.hammer@canonical.com/git/dotfiles/config/opencode/commands/wayfinder-hwt.md`):
  the four argument forms, the frontier definition, the confirmation with the
  person, the skip order, the slug forms, the model string, the dry run then
  spawn, the refusal handling, the brief, and the report.
- ALREADY WRITTEN (`.kb/issue-tracker.md`, "Wayfinding operations"): the
  frontier query "list the map's open children, drop any with an open blocker
  or an assignee", the claim with `gh issue edit <n> --add-assignee @me`, and
  the resolution order of comment, close, and map line.
- ALREADY WRITTEN (`/home/stefan.hammer@canonical.com/.agents/skills/wayfinder/SKILL.md`):
  "refer to it by that name, never by a bare id, number, or slug", which the
  brief's "Use the ticket title, not a bare number, in the map line" restates.
- ALREADY WRITTEN (the brief skeleton in the command file): "Ask before <the
  step in this repository that destroys state or spends money>", which is why
  the agent left the two worktrees alone.
- PROJECT-SPECIFIC FACT: the map `#1` "Map: the egress-controlled Hermes
  runtime", the two tickets, their labels, the base `7451cc7`, and the three
  live worktree paths. These belong in the ticket or the map, not in a skill.

## What should not become a skill

- The order of the `question` options and the wording of the skip lines. The
  command file holds both, and a copy in a skill would drift.
- The `trail_add` entries for the two sessions. They are harness bookkeeping
  with no repository rule behind them.
- The model string `minimax-coding-plan/MiniMax-M3.1-Flash#default`. It is the
  parent session's model on that day, read from the session export, and a
  skill that names a model would age badly.
- The judgement that both tickets were worth spawning together. The person
  chose "All of them" from the offered list, and the list came from the
  frontier rule.
- The answer to the reconciliation question, as a rule for every report. It is
  a useful one-off audit for three named branches, and the follow-up question
  is the better general lesson.
- The agent's word "load-bearing" in its reply to the person (line 298). It is
  a word `.kb/writing-style.md` bans, so the correction is to apply the law.
  A lesson that records the word teaches nothing.
