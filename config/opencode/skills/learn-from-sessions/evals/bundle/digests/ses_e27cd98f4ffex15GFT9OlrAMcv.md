# ses_e27cd98f4ffex15GFT9OlrAMcv: Wayfinder ticket session spawning

## What the person asked for

The person gave one command spec, USER 1 (line 2). It defines a `/wayfinder`
command that wraps the `hwt` skill and spawns one session per ticket.

USER 1 (line 3): "Load the `hwt` skill with the skill tool, id `hwt`, and apply it once per ticket."

USER 1 (line 11): "Load it at the start with the skill tool, id `wayfinder`. It lives at `~/.agents/skills/wayfinder/SKILL.md`, and its frontmatter sets `disable-model-invocation: true`."

USER 1 (line 33): "`frontier` alone — query the map for the tickets the person can pick up now, and confirm the list before spawning (step 3)."

USER 1 (line 39): "`hwt` takes its repository from the opencode session that runs it, not from a `cd`."

USER 1 (line 74): "The frontier is the nodes with `state == OPEN`, no assignees, and no `blockedBy` node still `OPEN`."

USER 1 (line 112): "`research/<slug>` for a `wayfinder:research` ticket, `wayfinder/<slug>` for the other three."

USER 1 (line 136): "Write the goal to `/tmp/opencode/hwt-goal-<slug>.md` with the write tool, one line: the ticket's observable end state, naming the command that proves it and what that command prints."

USER 1 (line 147): "A refusal — non-zero exit, or a printed refusal — is recorded in `hwt`'s own words, and the loop continues with the next ticket."

USER 1 (line 206): "Write them together, in the same words, so they cannot drift."

USER 1 (line 239): "Then stop. The new sessions own the work: do not start it here, do not write into a new checkout, and do not wait for it."

The person answered three questions through the `question` tool. The answers are in the raw export and clipped from the flat file at lines 279 and 282. They picked map "#44 a development workshop that drives the product", then "The frontier", then the frontier tickets "Decide the LXD channel for the conformance VM, Apply the fence from inside the development workshop" (tickets #69 and #52).

## What was produced, and whether it worked

The agent loaded the two skills (tool log line 275 and 276), found two open maps and asked which (line 279), queried the frontier of map #44 (line 281), and asked which frontier tickets to spawn (line 282).

It wrote four files: two briefs and two goals (lines 292, 293, 295, 296).

It ran two dry runs (lines 297, 299), then rewrote each brief's `Checkout:` line from the printed path (lines 298, 300).

It ran two spawns (lines 301, 302). The raw export shows both printed `hwt: checkout`, `hwt: session session.create`, `hwt: task session.prompt`, `hwt: goal`, and `hwt: herdr space.new`, then `EXIT=0`.

The two spawned sessions are:

- #69 `Decide the LXD channel for the conformance VM`, branch `wayfinder/lxd-channel-conformance-vm`, checkout `/home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/wayfinder-lxd-channel-conformance-vm`.
- #52 `Apply the fence from inside the development workshop`, branch `wayfinder/fence-from-development-workshop`, checkout `/home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/wayfinder-fence-from-development-workshop`.

The report (lines 255 to 273) names both, states the base commit `9557905`, lists no skipped tickets, and names four already-running research worktrees.

Verified: the two spawns exited 0 and created two worktrees and two Herdr spaces. Not verified: the work of the two spawned sessions, which this session did not wait for.

The agent reported a mid-run `AGENTS.md` change (line 251 and 273): resolution comments and posted Markdown now need `just style`. It folded that rule into both briefs (lines 273, 294). That rule is now written in `AGENTS.md` lines 135 to 138.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

The repository does not record any of these. Each is from USER 1.

- Branch name. USER 1 (line 112): "`research/<slug>` for a `wayfinder:research` ticket, `wayfinder/<slug>` for the other three."
- Slug. USER 1 (line 114): "The slug is the title's own words: lowercase, `[a-z0-9-]`, two to four words, with the leading verb and the articles dropped."
- Model. USER 1 (line 123): `model="$(opencode session export "$OPENCODE_SESSION_ID" | jq -r '.info.model | "\(.providerID)/\(.id)" + (if .variant then "#\(.variant)" else "" end)')"`.
- Model fallback. USER 1 (line 128): "Empty `$OPENCODE_SESSION_ID`, or an export that fails: run without `--model` and say in the report that the new session takes the configured default."
- Dry run. USER 1 (line 145): "Read the dry run. `hwt: repository` must be `$repo`, `hwt: checkout` and `hwt: herdr space.new` must name this branch, and `hwt: goal` must read the objective you wrote."
- Refusal. USER 1 (line 147): "Nothing is deleted, no space is closed, no second branch is tried, and `--no-space` is not a fallback."
- Space name. USER 1 (line 149): "The space is named after the branch, so the branch is the space name."
- Brief placeholder. USER 1 (line 135): "Put `PENDING: from hwt -n` on its `Checkout:` line."
- Rules line. USER 1 (line 220): "A `research` ticket's Rules line reads: "Push `<branch>` and open no pull request. It is a throwaway record." The other three read: "Do not push.""
- Report format. USER 1 (line 226): "one line per spawned session: `#20 Implement the proxy egress fence — wayfinder/proxy-egress-fence — <checkout> — space wayfinder/proxy-egress-fence — <model, or "configured default"> — <brief path> — goal: <objective>`".
- Goal commands. USER 1 (line 236): "The person reads a session's goal state with `/goal` and resumes it with `/goal resume`, in that session's tab."
- Frontier query. USER 1 (lines 57 to 72): one `gh api graphql` query over `subIssues` returning `number title state`, `assignees`, `labels`, and `blockedBy` for each child of the map.
- Skip reasons. USER 1 (lines 98 to 102): the five skip lines, each shaped `skipped: <reason>`.

## Failures, their cause, and the fix

(none found)

## Candidate lessons

- NEW (line 112): spawn a wayfinder ticket on `wayfinder/<slug>` and a research ticket on `research/<slug>`.
- NEW (line 114): make the slug from two to four title words, lowercase, `[a-z0-9-]`, with the leading verb and articles dropped.
- NEW (line 145): run `hwt -n` first and read its printed checkout before the real spawn.
- NEW (line 147): a `hwt` refusal is recorded in its own words and the loop moves to the next ticket. Nothing is deleted and `--no-space` is not a fallback.
- NEW (line 123): pass the session's own model to the spawned session, resolved from `opencode session export`, and report "configured default" when it is empty.
- NEW (line 206): write the goal and the brief's `Done when` section together, in the same words.
- NEW (line 220): a `research` ticket pushes its throwaway branch and opens no pull request. The other three do not push.
- NEW (line 149): the Herdr space is named after the branch.
- NEW (line 236): the person reads a goal with `/goal` and resumes it with `/goal resume`.
- PROJECT-SPECIFIC FACT (line 54): `gh` 2.45 reads `blockedBy` and only lacks the flags that write blocking edges.
- ALREADY WRITTEN (line 11): the wayfinder skill path and its `disable-model-invocation: true` flag. `AGENTS.md` lines 90 to 93.
- ALREADY WRITTEN (line 74): the frontier definition. `.kb/issue-tracker.md` lines 120 to 123.
- ALREADY WRITTEN (line 185): "Claim the ticket: `gh issue edit <n> --add-assignee @me`." `.kb/issue-tracker.md` line 125.

## What should not become a skill

- The whole `/wayfinder` command spec (USER 1, lines 2 to 239). It is a command definition that belongs with the `hwt` and `wayfinder` skills, not a monitor-agent repository skill. The parts that already restate monitor-agent law, such as the claim, resolve, close, and frontier rules, belong in `.kb/issue-tracker.md`, where they already are.
- The skip-reason lines (lines 98 to 102). They are a fixed output shape of one command, not a reusable rule.
- The report format (lines 226 to 231). It is the command's output contract, not a general skill.
