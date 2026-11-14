# ses_e32619bb6ffeuxwpfhrsrk8Vkp: Proxy topology recapture for iron-proxy

Transcript: `flat/ses_e32619bb6ffeuxwpfhrsrk8Vkp.txt`, 63 messages, read in
full. Flat line numbers below point into that file. The session ran in
worktree `wayfinder-recapture-proxy-topology`, which no longer exists, so
this transcript is the only record. Its one commit, `5c7528a`, is on `main`.

## What the person asked for

- The opening message is an `hwt` brief, not the person's own words. Its
  ask is "wayfinder Recapture the runtime topology for the proxy
  departure" (user turn 1, flat line 10).
- "I added some proxy tickets and updated the map, don't lose those" (user
  turn 2, flat line 144)
- "merge branch to main" (user turn 3, flat line 251)
- Eight answers through the `question` tool, clipped in the tool log (flat
  lines 290 to 295). The agent's summary of the settled set is a table at
  assistant, flat lines 110 to 119.

## What was produced, and whether it worked

- #15 was claimed (tool log, flat line 266).
- The grilling ran in three rounds on the fence mechanism, the record
  shape, the requirements, the ticket dispositions, and the glossary
  (assistant, flat lines 93 to 108).
- Files changed and committed as `5c7528a` "docs: record the proxy runtime
  topology" (tool log, flat line 340):
  - `adr/0001-...` renamed to
    `0001-hermes-runs-in-a-fenced-agent-workshop-and-a-plane-workshop-proxy-mediates-its-web-egress.md`
    and rewritten (tool log, flat lines 302 and 303).
  - ADR 0002 amended in place, with the OpenShell and mTLS sentences
    rewritten (tool log, flat lines 305 to 311).
  - The `adr/README.md` index row title updated (tool log, flat line 313).
  - `GLOSSARY.md` terms updated (tool log, flat line 314).
  - `requirements/001-workshop-egress-fence/requirements.md` deleted (tool
    log, flat line 315).
  - Four research records repointed at the renamed record (tool log, flat
    line 312).
- `ste-lint.py` was run on both records and reported "0 hard violations"
  (tool log, flat line 338, and assistant, flat line 217).
- #20 to #25 were created as sub-issues of #1 with blocking edges wired
  (tool log, flat lines 326 and 327). #5 to #12 were closed with comments
  that link their replacements (tool log, flat line 328). The stale
  blocking edge from #18 to the closed #10 was removed (tool log, flat
  line 343).
- The resolution was posted on #15 and #15 was closed (tool log, flat line
  330). The map body was rebuilt from a fresh read by a script that splits
  on `## ` headings (tool log, flat lines 331 to 334).
- The branch was merged into `main` at the person's request:
  `git -C /home/stefan.hammer@canonical.com/git/monitor-agent merge
  --ff-only wayfinder/recapture-proxy-topology` (tool log, flat line 350).
  The agent reported a fast-forward at `5c7528a` (assistant, flat line
  257). Nothing was pushed: "Nothing was pushed. Say the word if you want
  `git push origin main`." (assistant, flat line 261).
- The person's #17, #18, and #19 were kept: "#17, #18, and #19 were
  preserved. #17 is now unblocked." (assistant, flat line 224).
- Not verified: the fence wrapper is not built, no proxy binary was run,
  and the OVN fence is unmeasured (assistant, flat lines 234 to 242). The
  links to the renamed record resolve only after the merge (assistant,
  flat line 242).
- One divergence from the brief: the brief expected ADR 0001 to be
  deprecated. The person chose the in-place edit, and the agent flagged
  the difference (assistant, flat line 207).

## Corrections the person made

- The agent had closed its plan with "Planned new tickets", six tickets
  including "Decide the plane workshop provisioning and proxy lifecycle"
  (assistant, flat line 140). The person wrote "I added some proxy tickets
  and updated the map, don't lose those" (user turn 2, flat line 144). The
  agent answered "I'll re-read the map and the tracker first, then
  reconcile my plan with what you added rather than creating duplicates."
  (assistant, flat line 146) and created no duplicate of #17, #18, or #19.
- After the report, the person wrote "merge branch to main" (user turn 3,
  flat line 251). The agent had left the merge to the person (assistant,
  flat line 249). It merged from the main worktree because `main` is
  checked out there (assistant, flat line 253).

## Conventions, commands and values stated and written down nowhere

- The person edits the tracker while a session runs, and expects the
  session to keep their work: "don't lose those" (user turn 2, flat line
  144).
- A record may be rewritten in place under a new file name, and it keeps
  the `Accepted` status: "You chose the in-place edit, so 0001 stays
  Accepted under the new title" (assistant, flat line 207). `adr/README.md`
  describes deprecation as the way to retire a record and does not mention
  this form.
- Closing an issue releases its assignee: "#7's assignee was released by
  the close, as you chose." (assistant, flat line 223).
- The merge is local only. The person asked for the merge and not for a
  push (user turn 3, flat line 251, and assistant, flat line 261).
- Command used: `git -C <main checkout> merge --ff-only <branch>`, because
  `main` is checked out in the main worktree (assistant, flat line 253).
- The record's new file name, and the four research records that carried
  the old link (tool log, flat lines 300 and 302).

## Failures, their cause, and the fix

(none found)

The tool log holds no `!! FAILED` line. One hazard was handled before it
caused an error: renaming the record file broke every link to it, so the
agent found the links first with
`grep -rn "0001-hermes-runs" --include=*.md .` (tool log, flat line 300),
renamed with `git mv` (flat line 302), and rewrote the links in the four
research records and ADR 0002 (flat lines 306 and 312).

## Candidate lessons

- NEW: re-read the map and the tracker before creating tickets, because
  the person edits them while the session runs. "I added some proxy
  tickets and updated the map, don't lose those" (user turn 2, flat line
  144).
- NEW: a record may be rewritten in place under a new name, and the index
  row changes with it. "You chose the in-place edit, so 0001 stays
  Accepted under the new title" (assistant, flat line 207).
  `adr/README.md` names only the deprecation form, so the in-place form is
  a gap in that document.
- NEW: edit the map body from a fresh read, one section at a time, so a
  concurrent edit survives. Evidence: the fresh read at
  `gh issue view 1 --json body` (tool log, flat line 331) and the script
  that splits the body on `## ` headings and writes every other section
  back unchanged (tool log, flat line 332).
- PROJECT-SPECIFIC FACT: closing an issue releases its assignee.
  "#7's assignee was released by the close, as you chose." (assistant,
  flat line 223). It belongs in `.kb/issue-tracker.md`.
- ALREADY WRITTEN: a requirement whose behavior was removed may be deleted
  and git history is the archive, `.kb/requirements-format.md` §4.
- ALREADY WRITTEN: the deprecation section, the index row status, and the
  ASD-STE100 requirement for records, `adr/README.md`, "Conventions".
- ALREADY WRITTEN: the ASD-STE100 lint pass, `adr/README.md`, and
  `.kb/requirements-format.md` §6.

## What should not become a skill

- The eight answers and the ticket dispositions. They are in the #15
  resolution, ADR 0001, ADR 0002, and `GLOSSARY.md`.
- The link repair with `grep` and `sed`. It is an ordinary editing step.
- The `build-map.py` script. The lesson is "edit from a fresh read
  by section", not one script.
- The trail entries.
