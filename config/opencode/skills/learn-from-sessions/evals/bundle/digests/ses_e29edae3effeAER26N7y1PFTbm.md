# ses_e29edae3effeAER26N7y1PFTbm: Wayfinder ticket spawning via hwt

Session ran in the main checkout `/home/stefan.hammer@canonical.com/git/monitor-agent` on 13 November 2026. Messages are numbered U1 and U2. This session is the earlier of the two wayfinder spawning sessions in this batch and it ran on a different model from the later one.

## What the person asked for

- U1 is the body of the `/wayfinder-hwt` command with the argument `frontier`. The command body is quoted below only where it states a fact about the tooling.
- U2: "I see #38, why not that?"

## What was produced, and whether it worked

- **First answer.** "The frontier is empty", with the reason "every open ticket is claimed or blocked". The map was #1, "Map: the egress-controlled Hermes runtime", with 25 children, all closed.
- **After U2,** #38 was attached to map #1 with the GraphQL `addSubIssue` mutation, so later frontier queries see it.
- **One session spawned:** ticket #38, branch `wayfinder/fence-lifecycle-command`, checkout `/home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/wayfinder-fence-lifecycle-command`, space of the same name, model `zai-coding-plan/glm-5.3-flash#high`, prompt `/tmp/opencode/hwt-prompt-fence-lifecycle-command.md`, goal `/tmp/opencode/hwt-goal-fence-lifecycle-command.md`.
- **The goal,** in the agent's words: "`just test` passes and `monitor-agent-fence refresh` on the fenced agent workshop exits 0 and reports the fence in force, with the agent instance running at its fixed address afterward."
- **Verified:** the dry run printed the repository, checkout, space and goal the agent meant, the `Checkout:` line was rewritten from `PENDING: from hwt -n`, and the spawn command ran without `-n`. The work landed on `main` later as the merge of pull request #60.
- **Not verified:** whether the spawned session met its goal, because this session stopped after the spawn. The report also says "uncommitted changes: not checked" for the base checkout.

## Corrections the person made

- U2 overruled the empty frontier: "I see #38, why not that?" The agent's reply opened "#38 is OPEN, unassigned, and labeled `wayfinder:task`", then "so it looks takeable." Its explanation for the miss is in the candidate list below.

## Conventions, commands and values stated and written down nowhere

- The agent's measurement: "`gh` 2.45 has no `sub-issue` command, so I'll attach through the GraphQL `addSubIssue` mutation with both node IDs."
- The recovery order the agent used, which the command body does not state: "Attaching #38 to the map first, then preflight."
- The base it used: "`main` @ `f9f305b`".

## Failures, their cause, and the fix

- **The frontier reported empty when a takeable ticket existed.** Cause, in the agent's words: "The frontier reads only the map's sub-issues, and #38 is not one." Then "Its body says `Part of #1` in prose, but that is not map membership", and "the tracked-items link is what the frontier query reads, and nobody attached #38 to the map when it was charted." Fix: one `addSubIssue` call, then the normal preflight and the spawn.
- **No `!! FAILED` line appears in this session's tool log.** The only defect in the run is the report line above: the base's uncommitted changes were declared not checked.
- **A gap the agent named:** "#38 is not attached to the map" was described as "bookkeeping slip, not an intent to keep it off the map", so the agent asked before changing the map rather than attaching it silently.

## Candidate lessons

- NEW. "The frontier reads only the map's sub-issues, and #38 is not one." Then "Its body says `Part of #1` in prose, but that is not map membership". Reply to U2. `.kb/issue-tracker.md` offers the `Part of #<parent>` line as the fallback where sub-issues are unavailable, and this session shows that line hiding a ticket from the frontier query on a repository where sub-issues do work.
- NEW. "Attaching #38 to the map first, then preflight." Reply to U2. A ticket found outside the map is attached, then taken through the same preflight, and only then spawned, so the map and the session agree about what is takeable.
- NEW. "`gh` 2.45 has no `sub-issue` command, so I'll attach through the GraphQL `addSubIssue` mutation with both node IDs." Reply to U2. The same lesson is counted in ses_e29a6e8fcffej9WEFqqvOxC3d5, where it was measured for both sub-issues and blocked-by edges.
- PROJECT-SPECIFIC FACT. "#38 is OPEN, unassigned, and labeled `wayfinder:task`", and the map's Decisions already named #38 while the graph did not. This is the state of one map on one day.
- ALREADY WRITTEN. Report whether the base checkout had uncommitted changes. The `hwt` skill: "whether this checkout had uncommitted changes, because the new branch starts from the last commit and will not contain them." The report said "not checked", so the rule held and was skipped.
- ALREADY WRITTEN. Claim the ticket, then work it. `.kb/issue-tracker.md`, "Claim: `gh issue edit <n> --add-assignee @me`. This is the session's first write." The command body makes the spawned session do this at step 2.
- ALREADY WRITTEN. A grilling ticket gets the goal that the decision is recorded on the ticket with the person's answer in it. The command body, step 8. This session did not spawn a grilling ticket, so the rule was not exercised.

## What should not become a skill

- The map number, the 25 closed children and the #38 state. They are one map's history.
- The model name `zai-coding-plan/glm-5.3-flash#high`. A model string is read from the running session each time, as the command body's step 6 already says.
- The agent's judgement that the missing attachment was "bookkeeping slip". It was right here, and a skill cannot teach that judgement, only the question.
