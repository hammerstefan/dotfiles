# ses_e2faa3d00ffedxuQSEcstDwF93: Next @wayfinder issues to pick up

Transcript: `flat/ses_e2faa3d00ffedxuQSEcstDwF93.txt`, 78 messages, read in
full. Flat line numbers below point into that file. The session ran in the
main checkout.

## What the person asked for

- "what are the next @wayfinder issues to pick up?" (user turn 1, flat line
  3)
- "one at a time, for each of the three next issues, run "/hwt wayfinder
  <ticket>" with minimal context. let the downstream agent problem solve
  and investigate. keep it breaf, don't think too much" (user turn 2, flat
  line 40)
- "@handoff to create a command that does ... take the user specified
  tickets and use htw to wayfinder each" (user turn 3, flat line 74)

## What was produced, and whether it worked

- The frontier was read from map #1 and reported as #20, #21, and #24
  (assistant, flat line 11 to 17), from a sub-issue query and per-ticket
  `blocked_by` and `blocking` queries (tool log, flat lines 97 and 101).
- The agent recommended #21 first, "not the first ticket in map order"
  (assistant, flat line 27), because that decision fixes the plane bridge
  address and ingress rule that two other tickets use (assistant, flat
  lines 29 to 34). The person did not respond to that recommendation.
- A stale memory page was corrected with an ingested document titled
  "Correction: issue #15 reconciliation is closed, not pending" (tool log,
  flat line 118).
- Three briefs were written, dry-run with `hwt -n`, their checkout paths
  corrected, and the three sessions spawned one after another (tool log,
  flat lines 121 to 135). The agent reported one branch, one worktree
  path, one space id, and one tab id per child (assistant, flat lines 48
  to 63).
- The model for each child was read from the running session (tool log,
  flat line 124, and assistant, flat line 85). Base `30fdc22` (assistant,
  flat line 65).
- A handoff document was written at
  `/tmp/opencode/handoff-wayfinder-hwt-command.md` for a global
  `/wayfinder-hwt` command in the `dotfiles` repository (assistant, flat
  line 78), and two trail entries were attempted (tool log, flat lines
  187 and 188).
- Not verified: whether any child finished. The transcript ends at the
  handoff report. No command file was written in this session.

## Corrections the person made

- The agent closed its turn with "Say the word and I will claim
  **[Decide the plane workshop provisioning and proxy lifecycle](...)** and start
  the grilling." (assistant, flat line 38). The person replaced that plan
  with "one at a time, for each of the three next issues, run "/hwt
  wayfinder <ticket>" with minimal context. let the downstream agent
  problem solve and investigate. keep it breaf, don't think too much"
  (user turn 2, flat line 40). The three tickets went to worktree
  sessions instead of one live session.
- The same turn limits what the parent prepares: "with minimal context"
  and "keep it breaf, don't think too much" (user turn 2, flat line 40).
- After the handoff, the person asked for the command to take tickets from
  them: "take the user specified tickets and use htw to wayfinder each"
  (user turn 3, flat line 74). The agent answered with a second handoff
  document, which is what the person asked for.

## Conventions, commands and values stated and written down nowhere

- Spawn children one at a time, for each of the next three issues (user
  turn 2, flat line 40).
- The ask passed to `hwt` is "/hwt wayfinder <ticket>" (user turn 2, flat
  line 40).
- The child investigates: "let the downstream agent problem solve and
  investigate" (user turn 2, flat line 40).
- The command takes tickets from the person: "take the user specified
  tickets and use htw to wayfinder each" (user turn 3, flat line 74). The
  person writes "htw" for `hwt`.
- The child's checkout path, as the agent stated it: "The checkout path is
  `~/.herdr/worktrees/<repo>/<branch-with-dashes>`, not the repository
  path." (assistant, flat line 84).
- The model comes from the running session: "The model comes from the
  running session via `opencode session export
  "$OPENCODE_SESSION_ID"`" (assistant, flat line 85).
- `gh` on this host: "`gh` here is 2.45.0, older than the 2.94 the tracker
  document assumes, so `--add-sub-issue` and `--add-blocked-by` do not
  exist." (assistant, flat line 86).
- Base commit `30fdc22` (assistant, flat line 65).
- A grilling child waits for the person: "the grilling session needs you
  to answer its questions live in that space, so it will sit idle until
  you go there" (assistant, flat line 72).
- The `research` skill that the wayfinder skill names is not installed on
  this machine (assistant, flat line 89).

## Failures, their cause, and the fix

- `!! FAILED edit` on
  `/tmp/opencode/hwt-prompt-wayfinder-plane-workshop-provisioning.md`:
  "Could not find oldString in
  /tmp/opencode/hwt-prompt-wayfinder-plane-workshop-provisioning.md."
  (tool log, flat lines 126 and 127). Cause: the old string held
  `.../monitor-agent-worktrees/wayfinder/plane-workshop-provisioning`,
  with a slash, and the file held the dashed form. Fix: the retry used
  `.../monitor-agent-worktrees/wayfinder-plane-workshop-provisioning` and
  succeeded (tool log, flat line 130).
- The same failure on
  `/tmp/opencode/hwt-prompt-wayfinder-agent-workshop-build.md` (tool log,
  flat lines 128 and 129), same cause, fixed at flat line 131.
- Cause of both: the briefs were written with a guessed checkout path
  before the dry run. The agent saw it in the dry-run output: "The dry run
  shows a different checkout path than I wrote. Let me correct the prompt
  files." (assistant, flat line 44).

## Candidate lessons

- NEW: spawn one child at a time, give it minimal context, and let it
  investigate. "one at a time, for each of the three next issues, run
  "/hwt wayfinder <ticket>" with minimal context. let the downstream agent
  problem solve and investigate. keep it breaf, don't think too much"
  (user turn 2, flat line 40).
- NEW: pass the running session's model to `hwt`, read with
  `opencode session export "$OPENCODE_SESSION_ID"`, so the child does not
  fall back to the configured default. Quote: "The model comes from the
  running session via `opencode session export
  "$OPENCODE_SESSION_ID"`" (assistant, flat line 85). Belongs to the `hwt`
  skill.
- NEW: write the brief with a placeholder checkout path, run `hwt -n`,
  then rewrite that one line. Quote: "The checkout path is
  `~/.herdr/worktrees/<repo>/<branch-with-dashes>`, not the repository
  path." (assistant, flat line 84). Evidence: the two failed edits. Belongs
  to the `hwt` skill.
- NEW: a grilling ticket cannot be handed to a quiet batch session. It
  waits for the person. Quote: "the grilling session needs you to answer
  its questions live in that space, so it will sit idle until you go
  there" (assistant, flat line 72). Belongs to the `hwt` skill or to the
  wayfinder skill.
- NEW: a session may recommend a different first ticket when the blocking
  edges understate the dependency. Quote: "first, not the first ticket in
  map order" (assistant, flat line 27). The agent's claim, and the person
  did not rule on it. It departs from the written rule "First in map order
  wins" in `.kb/issue-tracker.md`.
- ALREADY WRITTEN: the frontier query and the claim sequence,
  `.kb/issue-tracker.md`, "Wayfinding operations".
- ALREADY WRITTEN: the `gh` 2.94 threshold and the `gh api` fallback for
  sub-issues and blocking, `.kb/issue-tracker.md`, "Conventions".
- PROJECT-SPECIFIC FACT: the frontier on that day was #20, #21, and #24,
  and the three children branched from `30fdc22`. A snapshot.

## What should not become a skill

- The two failed edits. The agent mistyped its own old string.
- The ingested correction document. The global Hindsight protocol already
  prescribes a correction with a "Correction:" title.
- The handoff document's contents. It describes a command for the
  `dotfiles` repository, not for `monitor-agent`.
