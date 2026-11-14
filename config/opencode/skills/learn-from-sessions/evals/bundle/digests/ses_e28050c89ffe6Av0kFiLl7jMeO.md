# ses_e28050c89ffe6Av0kFiLl7jMeO: Wayfinder frontier ticket priorities

## What the person asked for

- "which of the wayfinder frontier tickets is the best to pick up next. keep in mind that we still have pr 74 unmerged" — USER 1 (line 3)
- "74 is now merged" — USER 2 (line 5)
- "Load the `hwt` skill with the skill tool, id `hwt`, and apply it once per ticket. It owns the branch naming, the dry-run-then-spawn sequence, and the refusal rules. This command adds the wayfinder part: which tickets, what each session is told, and what you report back." — USER 3 (line 29)
- "Tickets:" then "frontier" — USER 3 (line 31)
- "pause" — USER 4 (line 279)
- "continue" — USER 5 (line 299)
- "take note of model switch, that needs to apply to hwt" — USER 6 (line 301)

## What was produced, and whether it worked

The agent recommended ticket #51 as the next pick. It stated the frontier rule
from `.kb/issue-tracker.md` and listed #51, #67, and #68 as the three open,
unassigned, unblocked children of map #44. The agent said to claim #51 with
`gh issue edit 51 --add-assignee @me`.

The person then gave a command spec (USER 3, lines 28 to 265) that combines the
`hwt` skill with wayfinder ticket selection. The agent ran it against the
`frontier` argument. It found two open maps and asked the person which one. The
person chose map #44 and tickets #51 and #67.

The agent produced four files:

- `/tmp/opencode/hwt-prompt-development-workshop-spike.md`
- `/tmp/opencode/hwt-goal-development-workshop-spike.md`
- `/tmp/opencode/hwt-prompt-privileged-conformance-suite.md`
- `/tmp/opencode/hwt-goal-privileged-conformance-suite.md`

The agent dry-ran and spawned two sessions:

- #51 "Conclude the development workshop spike and record the control-service decision" on branch `wayfinder/development-workshop-spike`, checkout `/home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/wayfinder-development-workshop-spike`, model `opencode-go/mimo-v2.6-flash#default`.
- #67 "Define the privileged conformance suite" on branch `wayfinder/privileged-conformance-suite`, checkout `/home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/wayfinder-privileged-conformance-suite`, model `opencode-go/deepseek-v4.1-flash#high`.

Both branches started from base `7e6ff4c85b6f8568d197d70222c2edc773548a42`, the
`main` head after the PR 74 merge. The main checkout had no uncommitted changes.

Verified: PR 74 merged, the frontier query, the preflight for #51 and #67, and
the dry-run readback. Not verified: the work inside the two spawned sessions,
which had not run yet. No commits were made in this session itself.

## Corrections the person made

- "take note of model switch, that needs to apply to hwt" — USER 6 (line 301).
  Before this, the agent had spawned #51 on the old model `opencode-go/mimo-v2.6-flash#default`
  because the session model was read once before the loop. The person's words
  told the agent to apply the switch to the remaining `hwt` spawns.

## Conventions, commands and values stated and written down nowhere

The person dictated a wayfinder spawn command in USER 3. Its rules that the
repository does not already record:

- Branch prefix split by type: "`research/<slug>` for a `wayfinder:research` ticket, `wayfinder/<slug>` for the other three." — USER 3 (line 138)
- Slug rule: "lowercase, `[a-z0-9-]`, two to four words, with the leading verb and the articles dropped" — USER 3 (line 140)
- Frontier argument: "`frontier` alone — query the map for the tickets the person can pick up now, and confirm the list before spawning" — USER 3 (line 59)
- Several open maps: "Several: ask which, by name, and set `map` from the answer." — USER 3 (line 74)
- Model capture: "`model="$(opencode session export "$OPENCODE_SESSION_ID" | jq -r '.info.model | "\(.providerID)/\(.id)" + (if .variant then "#\(.variant)" else "" end)' )"`" — USER 3 (line 149)
- Brief ask line: "`/wayfinder #<map> #<n>`" — USER 3 (line 191)
- Grilling goal: "give it the goal that the decision is recorded on the ticket, with the person's answer in it, and nothing more." — USER 3 (line 236)

Values stated in the session:

- Repository: `hammerstefan/monitor-agent`.
- Base commit: `7e6ff4c85b6f8568d197d70222c2edc773548a42`.
- Models: `opencode-go/mimo-v2.6-flash#default` and `opencode-go/deepseek-v4.1-flash#high`.
- Map #44 is "a development workshop that drives the product". Map #1 is "the egress-controlled Hermes runtime".

## Failures, their cause, and the fix

(none found)

## Candidate lessons

- NEW — A model switch in the spawning session must flow to `hwt`'s `--model` for the remaining spawns. From "take note of model switch, that needs to apply to hwt" — USER 6 (line 301). A session already spawned keeps its model.
- NEW — Wayfinder ticket branch names split by type: `research/<slug>` for `wayfinder:research`, `wayfinder/<slug>` for the other three. From "`research/<slug>` for a `wayfinder:research` ticket, `wayfinder/<slug>` for the other three." — USER 3 (line 138).
- NEW — The `frontier` argument selects the map's currently takeable tickets and needs a confirm step before spawning. From "`frontier` alone — query the map for the tickets the person can pick up now, and confirm the list before spawning" — USER 3 (line 59).
- NEW — A grilling ticket's goal is the decision recorded on the ticket, no checkable end state. From "give it the goal that the decision is recorded on the ticket, with the person's answer in it, and nothing more." — USER 3 (line 236).
- ALREADY WRITTEN — The frontier rule, open children without assignee or open blocker, first in map order. `.kb/issue-tracker.md` §Wayfinding operations.
- ALREADY WRITTEN — The `wayfinder` skill path `~/.agents/skills/wayfinder` and its `disable-model-invocation: true` flag. `AGENTS.md` §Wayfinding.
- ALREADY WRITTEN — The `hwt` dry-run-then-spawn sequence and its refusal rules. The `hwt` skill.
- PROJECT-SPECIFIC FACT — Map #44 holds the active frontier. Map #1 has no open children. #51, #67, and #68 were the takeable tickets this session.

## What should not become a skill

- The frontier state itself, which tickets were takeable on this date. That is tracker state that changes with each claim and close.
- The recommendation to pick #51 over #67 and #68. It is one application of the frontier rule in `.kb/issue-tracker.md`.
- The specific models and the base commit. They are points in time, not rules.
