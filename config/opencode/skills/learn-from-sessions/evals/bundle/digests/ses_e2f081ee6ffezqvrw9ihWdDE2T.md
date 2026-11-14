# ses_e2f081ee6ffezqvrw9ihWdDE2T: Wayfinder ticket sessions via hwt

## What the person asked for

One user turn (flat line 3), the `/wayfinder-hwt` command body. It opens: "Load the `hwt` skill with the skill tool, id `hwt`, and apply it once per ticket. It owns the branch naming, the dry-run-then-spawn sequence, and the refusal rules. This command adds the wayfinder part: which tickets, what each session is told, and what you report back."

Its `## Tickets` heading at flat line 5 is followed by two blank lines, so the ticket list arrived empty. The rest of the body is nine numbered steps with the GraphQL frontier query, the preflight skip list, the slug rule, the model export, the brief skeleton, and the report format.

## What was produced, and whether it worked

- One question through the `question` tool, offering "Use the frontier" or "I'll type numbers", because the ticket list was empty.
- The frontier query on map #1, and a second question with the one takeable ticket listed by title. The agent's summary of the filter: "#23 Build the plane workshop, OPEN, unassigned, only blocker #21 (closed) → **takeable**", and the three it dropped with a reason each.
- Preflight on #23: the issue view, the blocked-by query, `git worktree list --porcelain`, and `git branch --list`. All passed.
- Model lookup through `opencode session export` and `jq`: `zai-coding-plan/glm-5.3-flash#default`.
- The brief written to `/tmp/opencode/hwt-prompt-plane-workshop.md` from the step 8 skeleton, with `Checkout: PENDING: from hwt -n` on line 3.
- A dry run with `-n`, read against three expectations, then the `Checkout:` line rewritten from the dry run's printed path, then the real spawn.
- The report, in the format step 9 asks for: one line for the spawned session with its branch, checkout, space, model, and brief path, then the tickets not takeable, refusals, the worktrees already running, and the base.
- Verified: the dry run output was read before the spawn. The agent states "Dry run is correct: repository matches, checkout and `space.new` both name `wayfinder/plane-workshop`." and the report gives the checkout path.
- Verified by later sessions: the spawned session `ses_e2fa08eb2ffewNk3XysPmOi06p` exists, and #23 was built and merged as PR #37.
- The model the spawn passed is the model the child sessions ran on. `ses_e321eb4dcffeOwt9gHumsL86cU` and `ses_e321ea872ffeuUyyOvuQCYo8WS` both record `MODEL-SWITCHED` to `glm-5.3-flash` early in their transcripts.

## Corrections the person made

(none found)

The command body arrived with its `## Tickets` heading empty. That is a defect in the invocation and not a correction by the person. The agent's answer was a question, and the person's selection came through the `question` tool.

## Conventions, commands and values stated and written down nowhere

Every line below is the person's, from the command body:

- The ticket list forms: "Numbers, with or without `#` (`20 21 24`) — those tickets, in that order." and "`frontier` alone — query the map for the tickets the person can pick up now, and confirm the list before spawning (step 3)." A mixed argument is refused: "say 'Give ticket numbers, or `frontier` alone.' Report what was given and spawn nothing."
- The branch naming: "`research/<slug>` for a `wayfinder:research` ticket, `wayfinder/<slug>` for the other three." The slug rule: "The slug is the title's own words: lowercase, `[a-z0-9-]`, two to four words, with the leading verb and the articles dropped (`Implement`, `Decide`, `Build`, `Verify`, `Write`, `Run`, `Research`)."
- The space name: "The space is named after the branch, so the branch is the space name."
- The model export: `opencode session export "$OPENCODE_SESSION_ID"` piped to `jq -r '.info.model'`, with variant appended after `#`. When it is empty, "run without `--model` and say in the report that the new session takes the configured default."
- The dry run and its three checks: "`hwt: repository` must be `$repo`, and `hwt: checkout` and `hwt: herdr space.new` must name this branch. Rewrite the `Checkout:` line with the printed path."
- The refusal rule: "A refusal — non-zero exit, or a printed refusal — is recorded in `hwt`'s own words, and the loop continues with the next ticket. Nothing is deleted, no space is closed, no second branch is tried, and `--no-space` is not a fallback."
- The preflight skip lines and their exact shapes, for example `#20 Implement the proxy egress fence` with the reason `skipped: wayfinder/proxy-egress-fence is checked out at <path>`. A claimed ticket stays claimed: "leave the assignee alone, leave an existing branch alone, and pick no substitute."
- The handoff boundary: "Then stop. The new sessions own the work: do not start it here, do not write into a new checkout, and do not wait for it."

## Failures, their cause, and the fix

- The `## Tickets` section of the command body arrived empty, so the run could not start. The cause is an unfilled variable in the invocation. The fix was the step 1 question, and the run continued on the answer.
- No `!! FAILED` line appears in this session's tool log, and no refusal was recorded.

## Candidate lessons

1. NEW. A run whose input list arrives empty asks before spawning anything, and names the input it is missing. Quote: "The `hwt` skill is loaded. The Tickets section came in empty, so per step 1 I need to ask before spawning anything." (assistant, flat line 196)
2. NEW. A dry run supplies the checkout path for the brief, and the brief is corrected from its output before the real spawn. Quote: "Read the dry run. `hwt: repository` must be `$repo`, and `hwt: checkout` and `hwt: herdr space.new` must name this branch. Rewrite the `Checkout:` line with the printed path." (person, step 7.4, flat line 122)
3. NEW. The child inherits the spawner's model from a session export, and the report names the model so the person can tell what ran. Quote: the step 6 export and the report field `<model, or "configured default">` (person, flat lines 102 and 187).
4. NEW. One refusal ends that ticket and not the run. Nothing is rolled back and no substitute branch is tried. Quote: "Nothing is deleted, no space is closed, no second branch is tried, and `--no-space` is not a fallback." (person, step 7.6, flat line 124)
5. NEW. The spawner stops when the child starts. It does not begin the work and does not wait for the child. Quote: "Then stop. The new sessions own the work: do not start it here, do not write into a new checkout, and do not wait for it." (person, step 9, flat line 194)
6. NEW. The report lists the worktrees and research branches that were already running, so the person sees every session at once. Quote: "List every `wayfinder/*` and `research/*` worktree of this repository with its branch and path. These are the sessions already running, and the report names them." (person, step 4, flat line 85)
7. NEW. A frontier query with the eligibility fields in one call replaces several issue reads, and it drops claimed and blocked tickets without a second round trip. Quote the step 3 note: "One GraphQL query returns every child of the map with the fields eligibility needs." (person, flat line 33)
8. ALREADY WRITTEN. The slug and branch rules, and the `hwt` dry-run sequence. They are in the `hwt` skill at `/home/stefan.hammer@canonical.com/.config/opencode/skills/hwt/SKILL.md`, outside this repository, and the command body repeats them.
9. PROJECT-SPECIFIC FACT. The frontier on 2026-11-12 held one takeable ticket, #23, because #21 was closed, #20 was claimed, and #18 and #25 were blocked.

## What should not become a skill

- The frontier's state that day. A frontier is a snapshot, and the query in step 3 produces the next one.
- The specific model identifier `zai-coding-plan/glm-5.3-flash#default`. The rule is to inherit the spawner's model, not to name one.
- The example slugs `wayfinder/proxy-egress-fence` and `wayfinder/plane-workshop-provisioning`. They are illustrations of the rule, and the `hwt` skill already holds the rule.
