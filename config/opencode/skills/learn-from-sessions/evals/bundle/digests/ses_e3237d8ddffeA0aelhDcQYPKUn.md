# ses_e3237d8ddffeA0aelhDcQYPKUn: Next wayfinder issues to pick up

Transcript: `flat/ses_e3237d8ddffeA0aelhDcQYPKUn.txt`, 105 messages, read in
full. Flat line numbers below point into that file. The session ran in the
main checkout.

## What the person asked for

- "@wayfinder what are the next issues to pick up?" (user turn 1, flat line 3)
- "@hwt for EACH ticket you identified" (user turn 2, flat line 38)
- "most of the open decisions can be made by the child sessions, not every
  question needs to be answered up front" (user turn 3, flat line 52)

## What was produced, and whether it worked

- The frontier was read from map issue #1 with a sub-issue query and a
  `blocked_by` query per ticket (tool log, flat lines 81 to 85). The agent
  reported three takeable tickets: #17, #19, and #22 (assistant, flat lines
  11 to 23).
- All three were claimed in the parent session with
  `gh issue edit 17 --add-assignee @me`, then the same for #19 and #22
  (tool log, flat lines 137 and 139). The claim is also the child's first
  write under the wayfinder law (`.kb/issue-tracker.md`, "Claim").
- Three briefs were written under `/tmp/opencode/hwt-prompt-*.md` and
  dry-run with `hwt -n` (tool log, flat lines 186 to 189).
- Three sessions were spawned, on branches `wayfinder/plane-proxy-config`,
  `wayfinder/proxy-binary-integrity`, and
  `wayfinder/agent-workshop-provisioning` (tool log, flat lines 190 to 192).
- The third spawn passed the model name
  `minimax-coding-plan/MiniMax-M3.1-Fash#default` (tool log, flat line 192).
- No tracker resolution was recorded. The session ends while the agent is
  still establishing which model the third session started with
  (assistant, flat line 74).
- Not verified: whether any of the three child sessions did its work. The
  transcript holds no report from any of them.

## Corrections the person made

- After five assistant turns of upstream verification ("Let me verify the
  upstream facts each session will need.", flat line 42, and "Let me
  verify the upstream schema details each session will need.", flat line
  44), the person wrote "most of the open decisions can be made by the
  child sessions, not every question needs to be answered up front" (user
  turn 3, flat line 52). The agent read it as a correction: "I've been
  front-loading decisions that the child sessions can make." (assistant,
  flat line 54).

## Conventions, commands and values stated and written down nowhere

- One `hwt` session per frontier ticket, for every ticket the parent
  identified: "@hwt for EACH ticket you identified" (user turn 2, flat
  line 38).
- The child decides the open questions: "most of the open decisions can be
  made by the child sessions" (user turn 3, flat line 52).
- `hwt` invocation used here:
  `hwt --repo <repo> --agent opencode --model <model> --task-file <file> <branch>`,
  with `-n` as the dry run (tool log, flat line 189).
- Model string passed to the children:
  `minimax-coding-plan/MiniMax-M3.1-Flash#default` (tool log, flat line
  190).
- The parent read its own model with
  `opencode session export "$OPENCODE_SESSION_ID"` (tool log, flat line
  106).
- Base commit of the children: `5c7528a` (tool log, flat line 189).

## Failures, their cause, and the fix

- Wrong model name in the third spawn. What ran:
  `hwt --repo ... --model "minimax-coding-plan/MiniMax-M3.1-Fash#default" --task-file /tmp/opencode/hwt-prompt-agent-workshop-provisioning.md wayfinder/agent-workshop-provisioning`
  (tool log, flat line 192). The tool call reported `ok`. The error
  appeared in the agent's own reading afterwards: "I made a typo in the
  third spawn's model name (`Fash` instead of `Flash`)." (assistant, flat
  line 62) and "The typo in the third spawn's model name caused opencode
  to fall back to a different model." (assistant, flat line 64). Cause:
  an unresolvable model id makes opencode fall back to another model, and
  nothing in the spawn stops it. Fix: none inside this session. The agent
  was testing whether a resume with the right model works when the
  transcript ends (assistant, flat line 74).
- No `!! FAILED` line records that spawn. A spawn on the wrong model is
  not a failed tool call in the tool log.

## Candidate lessons

- NEW: a child session is spawned for each frontier ticket the parent
  names. "…@hwt for EACH ticket you identified" (user turn 2, flat line
  38). This belongs to the `hwt` skill, not to `monitor-agent`.
- NEW: the brief holds context and leaves the open decisions to the
  child. "most of the open decisions can be made by the child sessions,
  not every question needs to be answered up front" (user turn 3, flat
  line 52).
- NEW: a model id that does not resolve makes opencode fall back to a
  different model, and the spawn reports `ok`. Quote: "The typo in the
  third spawn's model name caused opencode to fall back to a different
  model." (assistant, flat line 64). Evidence in the tool log, flat line
  192. Belongs to the `hwt` skill.
- NEW: the parent must not claim a frontier ticket. The frontier query
  drops a ticket with an assignee (`.kb/issue-tracker.md`,
  "Frontier query"), and the claim is the child's first write
  (`.kb/issue-tracker.md`, "Claim"). Ran here: `gh issue edit 17
  --add-assignee @me` in the parent (tool log, flat line 137). The
  consequence is not written down: the assignment hides the ticket from
  every later frontier query.
- ALREADY WRITTEN: the frontier query and its first-in-map-order tie
  break, `.kb/issue-tracker.md`, "Wayfinding operations".
- ALREADY WRITTEN: the claim command and the resolve sequence,
  `.kb/issue-tracker.md`, "Claim" and "Resolve".
- ALREADY WRITTEN: sub-issue and blocking commands for an older `gh`,
  `.kb/issue-tracker.md`, "Conventions".
- PROJECT-SPECIFIC FACT: the frontier on that day was #17, #19, and #22
  (assistant, flat lines 17 to 21). A snapshot, not a rule.

## What should not become a skill

- The three ticket numbers and their blocking edges. They are the state of
  the map on one evening.
- The three prompt files. They were written for those three tickets.
- Reading the map with `gh api`. `.kb/issue-tracker.md` already states it.
