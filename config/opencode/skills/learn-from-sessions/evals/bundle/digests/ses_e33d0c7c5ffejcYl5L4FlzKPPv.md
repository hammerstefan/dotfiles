# ses_e33d0c7c5ffejcYl5L4FlzKPPv: Hermes agent egress via OpenShell proxy

## What the person asked for

Fourteen human turns. This session charted the map and then grilled ticket #7.

- U1 (flat:3): "@wayfinder build a hermes agent that is egress controlled through
  an openshell proxy running in workshops. the hermes agent must run in a
  different workshop from the openshell proxy workshop. network must be tightly
  controlled so that hermes can no egress without going through the openshell
  proxy." The same turn reserves the future proxies: "In the future we will also
  add other proxies into the proxy workshop (what reserach calls the "plane") to
  handle credential based access (git, jenkins, mattermost, launchpad, etc)
  proxies. Those future proxies do not need to be designed in this pass, just
  need to leave design space open to integrate them in the future."
- U2 (flat:59): "agreed to recommended"
- U3 (flat:137): "Is there any required research on the map?"
- U4 (flat:156): "/new @wayfinder 7"
- U5 (flat:204): "explore q4 more. I agree with the others. is it possible for
  custom proxies to be in the plane workshop but adjacent to the openshell
  docker container. hermes could route to dedicated custom apis that act as
  proxies for actions it wants to take. possible? flaws?"
- U6 (flat:254): "@general @diagram your explanation"
- U7 (flat:287): "use ~/tmp as dir"
- U8 (flat:306): "two questions 1) shouldn't llm traffic go through the openshell
  gateway too? 2) what would it take to have action-api proxies not go through
  the sandbox workload?"
- U9 (flat:352): "q7 yes" and "q8 if hermes was to run a "tool", where would it
  run. inside the agent workshop or inside the plane workshop?"
- U10 (flat:379): "is it possible to route no 2, the "other toolsets" to the
  plane, e.g. to filter with the openshell proxy?"
- U11 (flat:407): "@explore openshell supports extension drivers. would it be
  possible to add an extension driver to turn a workshop lxd container into a
  sandbox that connects to an openshell gateway?"
- U12 (flat:445): "q10 - we want to consider the feasibility. I would want to be
  able to drop the docker container in the design right now and treat the entire
  agent workshop as the sandbox itself."
- U13 (flat:514). "q4b - yes; q4c yes" then "hermes running directly in the
  sandbox is not a violation. enforcement would still be handled by the gateway,
  which would run outside the agent workshop - either in a workshop of it's own
  or a container or host service"
- U14 (flat:558): "I want to explore q13 D more deeply. let's define that as a
  research ticket @to-tickets"

## What was produced, and whether it worked

- Five `wayfinder:*` labels created, then map issue #1 and child tickets #2 to
  #12 (flat:616, flat:630-634). Child links and blocking edges were wired with
  the REST API because this host's `gh` predates the sub-issue flags.
- `GLOSSARY.md` written and pushed to `main` as `docs: add the glossary`
  (flat:635-636). The file is on `main` today and still carries the `plane
  workshop` term with `proxy workshop` under `_Avoid_`.
- Three research subagents dispatched for tickets #2, #3 and #4 (flat:637-639).
  Each reported back, and the map's "Decisions so far" gained one pointer per
  ticket (flat:641-643). All three showed the ticket state read before the close,
  so the closure is verified in the transcript.
- One report refinement recorded from ticket #3: "One record refinement, stated
  explicitly rather than silently overriding: [research/two-workshop.md] ... says
  the Docker driver's supervisor endpoint defaults to a fixed
  `https://127.0.0.1:17670`, while upstream documents automatic selection"
  (flat:111).
- Ticket #7 claimed (flat:648) and grilled in rounds. Accepted in the
  conversation: Q1 to Q3, Q4b, Q4c, Q5 to Q7, Q11, Q13 (implicitly, through U14).
- One diagram rendered three ways: `plane-proxy-architecture.svg`, `.html` and
  `.mmd`, first under `/tmp/opencode/wayfinder/diagrams/` and then copied into
  `~/tmp` with `~/tmp/vendor/mermaid.min.js` (flat:656-663).
- Not verified: nothing was published from the `to-tickets` breakdown in U14.
  The last tool call in this transcript is the custom-driver research dispatch
  (flat:665), so the four proposed slices were never created here.

## Corrections the person made

- On the custom-driver question the agent recommended a gate: "the
  recommendation: treat this as a feasibility answer first, and adopt nothing
  unless a concrete gain emerges" (flat:421). The person set the want instead:
  "we want to consider the feasibility. I would want to be able to drop the
  docker container in the design right now and treat the entire agent workshop
  as the sandbox itself." (U12, flat:445)
- On the two-workshop boundary the agent had put a question that recommended
  keeping it: "The two-workshop boundary of ADR 0001 stands in this design"
  (flat:471). The person rejected the reason: "hermes running directly in the
  sandbox is not a violation. enforcement would still be handled by the gateway,
  which would run outside the agent workshop" (U13, flat:515). The agent
  conceded: "your pushback on Q12 is ... correct", and that "my earlier framing
  over-applied it." (flat:517)
- On where the diagram files go, after the agent listed
  "`/tmp/opencode/wayfinder/diagrams/plane-proxy-architecture.svg`" (flat:268),
  the person said "use ~/tmp as dir" (U7, flat:287).
- On the LLM destination list the agent had closed Q4 with an allowlist of "the
  gateway endpoint, the LLM endpoint, and the resolver" (flat:41). The person
  asked "shouldn't llm traffic go through the openshell gateway too?" (U8,
  flat:307), and the agent answered that the gateway "is not a forward proxy for
  external clients" and proposed a plane-hosted LLM proxy instead (flat:314-323).
- On the tool-location question the agent had put Q8 before establishing where a
  hermes tool runs (flat:344). The person asked "q8 if hermes was to run a
  "tool", where would it run" (U9, flat:353), and the agent went back to the
  ticket #2 findings before answering ("The findings settle it precisely",
  flat:357).

## Conventions, commands and values stated and written down nowhere

- "use ~/tmp as dir" (U7, flat:287). The agent then copied the page's Mermaid
  vendor file to `~/tmp/vendor/` so the page opens from there (flat:289,
  flat:663). Neither the repository nor the diagram skill names `~/tmp`.
- The answering style. A six-question round came back as one line, "agreed to
  recommended" (U2, flat:59), and later rounds as "q7 yes" (U9) and "q4b - yes;
  q4c yes" (U13). Objections are appended to the same short message.
- "let's define that as a research ticket @to-tickets" (U14, flat:558). The
  person names the skill for the follow-up and expects the ticket, not the
  discussion.
- "`gh` 2.45 uses `-a` on create. Re-running:" (flat:71). The two `mk()` shell
  calls are at flat:632 and flat:633. `.kb/issue-tracker.md` records
  `--add-assignee` only for `gh issue edit`.
- The person's own statement of the decision rule: the verdict on a boundary
  turns on where enforcement runs and who can touch it. "enforcement would still
  be handled by the gateway, which would run outside the agent workshop" (U13,
  flat:515). That is the shape the repository adopted, with the fence outside the
  container.

## Failures, their cause, and the fix

- No `!! FAILED` line appears in this session's tool log. The failures are
  visible only in the agent's prose.
- `gh issue create ... --add-assignee @me` did not work on this host's `gh`
  2.45. Cause: the create subcommand of that version takes `-a`. Fix: re-ran
  with `-a @me` (flat:71, flat:632-633).
- Mermaid 12 rejected the first diagram source. Cause: "Mermaid 12 rejects `:::`
  on subgraph declarations" (flat:260). Fix: apply the roles with `class`
  statements (flat:657-658).
- The copied HTML page did not load. Cause: it "loads Mermaid from a relative
  `vendor/` path" (flat:289). Fix: copy `mermaid.min.js` beside it (flat:663).

## Candidate lessons

1. NEW. A want behind a feasibility question is the requirement, and the answer
   owes its cost. The agent offered a gate ("adopt nothing unless a concrete
   gain emerges", flat:421) and the person answered with the want (U12,
   flat:445). Answer the second with what the want costs, as the agent did at
   flat:495-502.
2. ALREADY WRITTEN. Enforcement outside the container the agent controls is the
   deciding property, and a container the agent owns can still sit inside it.
   `adr/0001-hermes-runs-in-a-fenced-agent-workshop-and-a-plane-workshop-proxy-mediates-its-web-egress.md`,
   Context: "The agent can remove a fence inside the container. The fence
   therefore stays outside the container." Quote: "hermes running directly in
   the sandbox is not a violation. enforcement would still be handled by the
   gateway, which would run outside the agent workshop" (U13, flat:515).
3. NEW. Diagram artifacts for the person go under `~/tmp`, with the vendor
   JavaScript beside the HTML page. Quote: "use ~/tmp as dir" (U7, flat:287).
   Nothing in the repository or in the diagram skill states it.
4. NEW. When upstream documentation contradicts a committed research record,
   mark the disagreement in the findings and keep the measurement. Quote: "One
   record refinement, stated explicitly rather than silently overriding"
   (flat:111). Ticket #3 repeated the practice at flat:67.
5. NEW. `gh issue create` on `gh` 2.45 takes `-a @me`, and `--add-assignee` is
   the flag of `gh issue edit`. Quote: "`gh` 2.45 uses `-a` on create. Re-running:"
   (flat:71). Version-bound, so it belongs beside the tracker fallbacks if it is
   kept at all.
6. NEW. One line per question in the answer, so a round of six can be settled
   in one sentence. Quotes: "agreed to recommended" (U2, flat:59), "q7 yes"
   (U9, flat:352), "q4b - yes; q4c yes" (U13, flat:514).
7. ALREADY WRITTEN. Put the recommended answer with each question and word it so
   a yes accepts it. The global skill
   `/home/stefan.hammer@canonical.com/.config/opencode/skill/grilling/SKILL.md`
   states both.
8. ALREADY WRITTEN. Finding the facts is the agent's work before the question
   goes to the person. Same skill: "Finding _facts_ is your job, never the
   user's". The failure to do it produced the question at U9 (flat:353).
9. PROJECT-SPECIFIC FACT. The model call travels through a plane-hosted proxy,
   and the agent bridge then names gateway, LLM proxy and resolver. Now recorded
   by `adr/0008-the-model-call-reaches-the-llm-endpoint-through-the-plane-proxy.md`.
10. PROJECT-SPECIFIC FACT. The OpenShell gateway listener multiplexes the mTLS
    gRPC API and exposed sandbox services and is not a forward proxy for
    external clients (flat:314). The current ADR 0001 no longer states it,
    because OpenShell was abandoned.
11. PROJECT-SPECIFIC FACT. Where a hermes tool runs: the dispatch happens in
    the agent workshop, and the effect follows `terminal.backend`, so the file
    tools run in the sandbox unless the backend declares
    `uses_host_filesystem = True` (flat:363). This decided the ticket #6 design
    that was later abandoned.
12. PROJECT-SPECIFIC FACT. The accepted ticket #7 values that outlived the
    pivot: addressing plan `10.250.0.1/24` and `10.253.0.1/24` with the
    gateways at `.10`, OpenShell pinned at `v0.1.8`, and the gateway global
    policy as the single policy file (flat:174-200). The two subnets did not
    survive. `adr/0006` now gives the plane bridge `10.255.0.1/24` with the
    plane workshop at `10.255.0.10`.

## What should not become a skill

- The fifteen grilling questions of ticket #7. OpenShell was abandoned, and
  `adr/0001` records the replacement decision, so the question set now teaches a
  retired topology.
- The Mermaid `:::` and `vendor/` fixes (flat:260, flat:289). They are details
  of one render and one copied page, and the diagram skill owns that workflow.
- The ticket numbering and the label colors of this map. They are state of one
  tracker, not a rule.
- "the trivial representative task is the acceptance bar" (flat:35). It reads as
  a rule about acceptance, but the acceptance task of this map died with the
  topology. The general practice is already the requirement process.
