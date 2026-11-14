# ses_e29a6e8fcffej9WEFqqvOxC3d5: Wayfinder ticket spawning with hwt

Session ran in the main checkout `/home/stefan.hammer@canonical.com/git/monitor-agent` on 13 November 2026. Messages are numbered U1 to U4 below.

## What the person asked for

Each user message is the body of a slash command rather than the person's own prose. The person supplied the argument and four short replies. The command body is quoted only where it states a fact about this repository's tooling.

- U1: argument `44 frontier`.
- U2: argument `frontier`.
- U3: "yes, fix the edges"
- U4: "fix the sub-issues"
- The person also answered through the `question` tool, and those answers are not in the flattened transcript. The agent's replies show two of them: "Not spawning anything" because the person "asked me to check the dependency graph first", and "Your reading is right: the map's dependency graph is broken, and `56` incorrectly looked takeable."

## What was produced, and whether it worked

- U1 was refused under the command's own rule: `44 frontier` mixes a number with the word, so the agent answered "Give ticket numbers, or `frontier` alone." and spawned nothing.
- **Ten native blocked-by edges on map #44**, written with the GraphQL `addBlockedBy` mutation. The agent verified them against the same eligibility rule and reported the frontier as #45, #48, #50.
- **Twelve native sub-issues under #44** (#45 to #56), written with the GraphQL `addSubIssue` mutation, so the command's step-3 `subIssues` query returns them. The agent verified the query returns `children: 12`.
- **The map body's `## Tickets` checklist was removed**, because it listed the children a second time and showed #47 and #49 unticked after they closed.
- **No session, branch or checkout was created.** The agent said so twice, and the tool log confirms it: the only writes were `gh api graphql` mutations, one `gh issue edit --body-file`, and two trail records.
- **Verified:** the edges, the sub-issue count, and the frontier computed from the sub-issue query. **Not verified:** that the `/wayfinder-hwt` command then spawns correctly from the corrected map, because no spawn happened in this session.

## Corrections the person made

- The person rejected the agent's first frontier answer and asked for the graph to be checked, in the agent's words: "Not spawning anything", then "you asked me to check the dependency graph first". The agent then found "Every ticket's native `blockedBy` is **empty** on GitHub" and that its earlier count of nine takeable tickets was wrong.
- U3 and U4 each rejected a partial fix. After U3 the agent had fixed the edges and still reported "Map #44 has no native sub-issues", so U4 asked for that second defect to be fixed as well.

## Conventions, commands and values stated and written down nowhere

- The person's own command body states: "`gh` 2.45 reads `blockedBy`" and "it only lacks the flags that write blocking edges."
- The agent's measurement of the same limit for sub-issues: "`gh` 2.45 has no `sub-issue` command, so I'll attach through the GraphQL `addSubIssue` mutation with both node IDs."
- The edge set: "45→51, 50→52, 51→52, 52→53, 52→55, 53→54, 52→56, 54→56", plus #38 on #54, ten in all.
- The sub-issue rule the agent applied at U4: "The three closed research tickets (#46, #47, #49) are included, so the map owns its full history."

## Failures, their cause, and the fix

- **The frontier query over-reported.** It said nine tickets were takeable and three were. Cause: "Every ticket's native `blockedBy` is **empty** on GitHub. The real dependencies exist only as prose lines (`Blocked by: #51, #50`) in the ticket bodies." Fix: the ten GraphQL edges, then a re-query.
- **The frontier query would have returned nothing.** Cause: "Map #44 has **zero native sub-issues**", and "its children are marked only by a `Part of #44` line and a checkbox list in the body. The command's step 3 queries `subIssues`, so it returns nothing regardless of the edges." Fix: twelve `addSubIssue` calls and the checklist removed.
- `!! FAILED question` with `Interaction cancelled because the location shut down`. The agent recovered with a prose message: "The question form was cancelled by the environment shutting down, not by you", then "so here is the state, and you can just say which way to go." Nothing was changed while the answer was missing.
- **A wrong caution, withdrawn by the agent:** "Note `research/development-workshop-lxd-scope` already exists", then "check whether #48 duplicates it before spawning." Later: "**#48 does not duplicate existing work.** `research/development-workshop-lxd-scope` is ticket #47's record ... My earlier caution was wrong."

## Candidate lessons

- NEW. "`gh` 2.45 reads `blockedBy`" and "it only lacks the flags that write blocking edges." The person's command body, step 3. A `gh` version that cannot write an edge does not mean GitHub cannot hold one. `.kb/issue-tracker.md` gives a REST path for dependencies and a `Part of #<parent>` body fallback for sub-issues, and it says nothing about the GraphQL mutations this session used.
- NEW. "`gh` 2.45 has no `sub-issue` command, so I'll attach through the GraphQL `addSubIssue` mutation with both node IDs." Reply to U2. The same shape as the blocked-by edge: the node ids come from a query, and the mutation takes `issueId` and `subIssueId`.
- NEW. A prose `Blocked by:` line does not make a native edge, and a frontier query that trusts only the graph over-reports. "Every ticket's native `blockedBy` is **empty** on GitHub. The real dependencies exist only as prose lines (`Blocked by: #51, #50`) in the ticket bodies." The query then "reported 9 takeable tickets. Only 3 are." Reply to U2. Read the bodies against the graph before spawning anything.
- NEW. A checklist in the map body is a second copy of the children and it goes stale. "the checklist was showing #47 and #49 unticked after they had closed." Reply to U4. The sub-issue query is the copy that cannot drift.
- NEW. A closed ticket belongs under the map as a sub-issue, so the map owns its history. "The three closed research tickets (#46, #47, #49) are included, so the map owns its full history." Reply to U4. `.kb/issue-tracker.md` does not say whether a closed child stays attached.
- PROJECT-SPECIFIC FACT. "**52–55 are not safe in parallel.** They are one chain, not four independent tickets". Reply to U2. The reason is that #52, #53, #54 and #55 edit the same `justfile`, verb map and audit writer. That is a judgement about this map's tickets, and it belongs in the map body, where the map #44 already records its Decisions.
- PROJECT-SPECIFIC FACT. "**#51's premise is not on `main`.** It says \"rewrite `spike/development-workshop/README.md` from PARTIAL to the phased plan\", but no `spike/` directory exists on `main`." Reply to U2. Since then `research/development-workshop.md` merged as #59, so the defect is stale, and it shows a ticket can name a file that only a branch holds.
- ALREADY WRITTEN. That a map is one issue with child issues and that blocking uses the native relationship. `.kb/issue-tracker.md`, "Wayfinding operations", and the global `wayfinder` skill.
- ALREADY WRITTEN. A claimed ticket stays claimed and is not re-spawned. `.kb/issue-tracker.md`: "Claim: `gh issue edit <n> --add-assignee @me`. This is the session's first write."

## What should not become a skill

- The ten specific edges and the six-row table. They are one map's shape.
- The refusal of `44 frontier` as an argument. It is the command's own rule, stated in the command body, and the command is the place for it.
- The question form's cancellation by a location shutdown. It is a harness event with a recovery the agent already made in prose, and a rule for it would not change the next outcome.
- The agent's caution about #48 duplicating #47. The lesson is to read the branch before raising a doubt, which the agent then did in the same session.
