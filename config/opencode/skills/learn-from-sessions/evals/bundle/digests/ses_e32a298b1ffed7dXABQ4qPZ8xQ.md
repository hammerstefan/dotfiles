# ses_e32a298b1ffed7dXABQ4qPZ8xQ: Hermes egress via proxy instead of openshell

## What the person asked for

Two human turns. This is the session where the person opened the departure that
ended OpenShell.

- U1 (flat:3): "@wayfinder on this repo and with current map issue #1 as context.
  I want to consider an approach that is a departure of the current plan and
  ADRs. for the sake of this investigation ADR and requirement violation is
  acceptable, but we must reconcile at the end." The same turn states the
  requirement: "the key architecture requirement that I need to fulfill is to
  separate the hermes agent from the internet. filesystem isolation is already
  handled by workshop, but I need to strictly control egress and provide proxy
  api to access resources that require credentials. What if we abandon openshell,
  let hermes have full control over the workshop lxd container, but all traffic
  is routed to a configurable http/https proxy that runs on the plane workshop.
  research configurable proxies that use similar configuration (and if possible
  audit, inspection) to openshell, but only handles the web traffic and not
  everything else that openshell manages."
- U2 (flat:61-65), the `hwt` skill instructions and one ask:
  "follow up #13 with wayfinder on #14"

## What was produced, and whether it worked

- Issue #13, "Research a web-only egress proxy for the plane workshop", label
  `wayfinder:research`, and issue #14, "Decide whether a web-only proxy replaces
  OpenShell", label `wayfinder:grilling` (flat:107-109). Both linked to map #1 as
  sub-issues, and #14 given a blocked-by edge on #13, through the REST API
  (flat:109-110).
- A background research subagent for #13 (flat:111). Its work is the sibling
  session `ses_e329b90a5ffeBo1zteLg82e8Uv` in this batch.
- #13 resolved and closed. The agent verified the pushed branch before recording
  the resolution: "The branch is clean: 584 lines of findings, proper commit
  message, no attribution issues." (flat:32), then the comment (flat:114) and the
  close (flat:114).
- The map body updated with a #13 pointer in "Decisions so far" and one new fog
  item: "The iron-proxy version line. Hermes pins v0.39.0 while upstream docs
  describe v0.7.0 features." (flat:117-119). The map update ran as
  `gh issue edit 1 --body-file` (flat:119).
- The initiative page updated, related to the existing page
  `kp-88d78d6b758e48d8a3822df07700cfe2` (flat:120).
- An `hwt` spawn for the decision: a dry run first (flat:128), then the real run
  with `--agent opencode --model "zai-coding-plan/glm-5.3-flash#high"
  --task-file /tmp/opencode/hwt-prompt-web-proxy-decision.md
  wayfinder/web-proxy-decision` (flat:130). The worktree is
  `/home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/wayfinder-web-proxy-decision`
  and the Herdr space id starts `sp5007abd01db4ee35959109ec7f8f4678`
  (flat:83).
- Records left untouched, as the person required: "ADRs and requirements are
  untouched, as agreed" (flat:59).
- Not verified in this transcript: whether the spawned session claimed #14 and
  what it decided. The transcript ends at the spawn.

## Corrections the person made

(none found as a correction of the agent). The person states the frame the agent
must work inside rather than correcting a claim:

- "ADR and requirement violation is acceptable, but we must reconcile at the
  end." (U1, flat:3). The agent honored it and said so at flat:59.
- "for the sake of this investigation" (U1, flat:3). It bounds the departure to
  the investigation.

One self-correction inside the agent's own answer is worth recording, because it
contradicts a memory it had quoted: the agent had framed the plan as
"Hermes-in-a-sandbox with a host-level gateway and OVN fence" (flat:20), which is
not the shape the ticket #7 conversation reached, and it then treated the
person's new proposal as a different shape.

## Conventions, commands and values stated and written down nowhere

- The reconciliation rule, in the person's words: "ADR and requirement violation
  is acceptable, but we must reconcile at the end." (U1, flat:3)
- The departure becomes two tickets, not one: a research ticket that is claimed
  and a decision ticket that is blocked on it (flat:14, flat:24). The agent
  described the split: "the HITL decision that weighs findings against ADR 0001,
  and if adopted, schedules the reconciliation" (flat:24).
- The findings convention carried into the new ticket: "findings live at
  `research/<name>.md` on a pushed `research/<name>` branch" (flat:8).
- The `hwt` values: branch `wayfinder/web-proxy-decision`, base "HEAD of main
  (`1fd4448`)", model `zai-coding-plan/glm-5.3-flash#high`, dry run with `hwt -n`
  before the real run (flat:83-85, flat:128-130).
- The brief's rules for the spawned session, quoted from the prompt file: "one
  ticket only, no deciding for you, writing style and ASD-STE100, no pushes or
  PRs, ask before closing #14 or editing the map body" (flat:92).
- The model and variant are read from
  `opencode session export <id>` at `.info.model` (flat:125-126).

## Failures, their cause, and the fix

- `gh issue create --parent 1 ...` failed. Cause: "This `gh` build lacks
  `--parent`." (flat:10). Fix: create the issue plain, then link it with
  `gh api --method POST repos/<owner>/<repo>/issues/1/sub_issues -F
  sub_issue_id=<db id>` (flat:109).
- `gh issue view 13` and `gh issue view 1` answered the Projects-classic GraphQL
  deprecation. Fix: `gh api repos/<owner>/<repo>/issues/<n> --jq '{title, body}'`
  (flat:100-101).
- `model="$(opencode session export "$OPENCODE_SESSION_ID" | jq -r ...)"` was
  refused: "Portable shell scanner cannot analyze command: unterminated-quote"
  (flat:123-124). Cause: the harness could not parse the nested quoting in a
  command substitution. Fix: export to a file, then read the file with `jq`
  (flat:125-126).
- The `hwt` brief was written with the placeholder "Checkout: <given by hwt
  output>" and filled from the dry run before the real spawn (flat:127, flat:129).
  Cause: the checkout path is only known once `hwt` reports it.
- No other `!! FAILED` line appears in this session's tool log.

## Candidate lessons

1. NEW. An investigation may set an ADR aside, and the reconciliation is part of
   the decision's outcome, never of the research. Quote: "for the sake of this
   investigation ADR and requirement violation is acceptable, but we must
   reconcile at the end." (U1, flat:3). `.kb/project.md` §2 covers the record
   update once a change is made, and states nothing about investigating a
   departure first.
2. NEW. A departure is charted as a claimed research ticket plus a decision
   ticket blocked on it, so the records stay untouched until the person decides.
   Quote: "Decide whether a web-only proxy replaces OpenShell ... the HITL
   decision that weighs findings against ADR 0001, and if adopted, schedules the
   reconciliation" (flat:24).
3. NEW. The harness refuses a shell command it cannot parse, so a value is written
   to a file and read back. Quote: "Portable shell scanner cannot analyze
   command: unterminated-quote" (flat:124). The fix is at flat:125-126.
4. NEW. Verify a pushed research branch before recording its resolution: read the
   commit, the author line, and the line count. Quote: "The branch is clean: 584
   lines of findings, proper commit message, no attribution issues." (flat:32).
5. ALREADY WRITTEN. On an older `gh`, sub-issues and blocking edges are wired
   through `gh api .../sub_issues` and `.../dependencies/blocked_by` with the
   issue's database id. `.kb/issue-tracker.md`, Conventions.
6. ALREADY WRITTEN. `hwt` takes `--model provider/model#variant`, `--task-file`,
   and `-n` for a dry run. The help text of
   `/home/stefan.hammer@canonical.com/scripts/hwt` states all three.
7. PROJECT-SPECIFIC FACT. The nine proxies, the shortlist of iron-proxy run
   standalone, mitmproxy and Squid, and the reason each rejected family failed.
   `adr/0001` now carries the shortlist, and the full profile is on the branch
   `research/web-egress-proxy`.
8. PROJECT-SPECIFIC FACT. The iron-proxy version discrepancy. `adr/0001` records
   that it is reconciled in issue #16, and issue #16 owns the answer.

## What should not become a skill

- The `wayfinder:*` label set and the map body layout. `.kb/issue-tracker.md`
  already defines the map, the child ticket and the frontier query.
- The hwt worktree path and space id (flat:83). They are state of one spawn.
- "follow up #13 with wayfinder on #14" (U2, flat:65). It is one instruction to
  one session, and the `hwt` skill owns how an ask becomes a brief.
- The claim that no recorded decision existed on a configurable proxy (flat:20).
  It was a memory reading at that moment, and it is now false.
