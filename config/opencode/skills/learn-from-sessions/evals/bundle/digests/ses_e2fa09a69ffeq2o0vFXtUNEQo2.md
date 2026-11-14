# ses_e2fa09a69ffeq2o0vFXtUNEQo2: Wayfinder plane Workshop provisioning

## What the person asked for

- The ask block in message 1 (1794497296835), opened with
  "`/wayfinder wayfinder #21`" and closed with a report requirement. The
  reusable part of the block is quoted in full under "Conventions, commands and
  values stated and written down nowhere". The block's own framing of the
  ticket: "Ticket #21 decides how the plane Workshop is provisioned and kept
  provisioned. It is a `wayfinder:grilling` ticket, so it is worked with the
  person, and it needs the `grilling` and `domain-modeling` skills."
- `@handoff for  "The agent build moves"` and, on the next line, `then push to
  remote and open pr` (message 2, 1794501837420). The two spaces after
  "`@handoff for`" are the person's.

## What was produced, and whether it worked

The session ran in
`.../.herdr/worktrees/monitor-agent/wayfinder-plane-workshop-provisioning`, on
branch `wayfinder/plane-workshop-provisioning`.

- The grilling: the agent's report says "13 questions in 4 rounds, all answered
  by you". The answers arrive as `question` tool calls, and the flatten clips
  the tool input at 400 characters, so the decisions survive only through the
  agent's report table.
- New record `adr/0006-the-plane-workshop-installs-the-proxy-from-a-pinned-release.md`
  plus its index row in `adr/README.md`. ADR 0004 amended (the pin's path and
  two stale ticket references). ADR 0005 amended (the agent SDK's path). The
  pin moved with `git mv` from `plane/proxy-digest.txt` to
  `plane/.workshop/iron-proxy/proxy-digest.txt`. `plane/.workshop/iron-proxy/sdk.yaml`
  added. `.kb/project.md` updated. One commit, reported as `171aaed`.
- Tracker work: `gh issue edit 21 --add-assignee @me` as the first write,
  `gh issue comment 21` with the resolution, `gh issue close 21`, the map #1
  body edited in a file and pushed with `gh issue edit 1 --body-file`, and
  dependency notes on #20, #23 and #24.
- Records the agent corrected in memory: a document titled "Correction: the
  project directory is mounted read-write", and an update to the initiative
  page for "Restrict the Hermes agent's network access inside a Workshop".
- The handoff document at `/tmp/handoff-agent-build-move.md`, and a trail
  entry for it.
- Verified against the current repository: `adr/README.md` lists 0006 as
  Accepted, ADR 0006:40-51 holds the passwordless sudo sentence, the SDK
  revision sentence and the read-write mount sentence,
  `plane/.workshop/iron-proxy/proxy-digest.txt` holds one `sha256sum -c` line
  that names `iron-proxy_0.56.0_linux_amd64.tar.gz`, and
  `plane/.workshop/iron-proxy/sdk.yaml` holds `name: iron-proxy`. The
  `policy-reload` recipe is in `justfile`.
- Not verified: no workshop was launched, no hook ran, and no proxy process
  started. The agent states this: "No workshop was launched, no hook ran, and
  no proxy process started."
- Not done: the push and the pull requests from message 2. The agent wrote the
  handoff document and ended. Its closing line covers the handoff only.

## Corrections the person made

- The agent opened with "Round 1 of the grilling:", and then wrote "Good catch.
  Let me correct the premise first, then give the trade-off." followed by
  "With your Q1 answer (two projects, `agent/` and `plane/`), hermes's project
  directory is `agent/`, which does not contain `plane/proxy-policy.yaml` or
  `plane/proxy-digest.txt`." The person's correction is not in the
  transcript, because it arrived as a `question` answer that the flatten clips.
- Two later rounds begin from a fact rather than a correction: "Two facts from
  the upstream source change the picture, and they answer your Q7 question".
- No correction was made after the report.

## Conventions, commands and values stated and written down nowhere

The ask block's instructions, from `# What to do` through `# Report`, quoted
verbatim:

    # What to do

    1. Load the `wayfinder` skill, then the `grilling` and `domain-modeling` skills. The ticket body lists the six things the decision states.
    2. Claim issue #21: `gh issue edit 21 --add-assignee @me`. This is the first write.
    3. Work the decision with the person. Grilling is a live exchange. Do not answer your own questions.
    4. Write the decision as an architecture decision record under `adr/`, following `adr/README.md` and `.kb/project.md` section 2.
    5. Record the resolution: comment on #21, close it, append the context pointer to the map's Decisions-so-far.

    # Rules

    - Read `AGENTS.md` and every file it points at before editing.
    - Follow `.kb/project.md`, `.kb/writing-style.md`, and `.kb/agents.md`.
    - The ticket does not write the proxy policy. It decides where the policy lives and how the process reads it.
    - Use the terms in `GLOSSARY.md`.
    - Commit on `wayfinder/plane-workshop-provisioning`. Do not push, merge, rebase, or touch other branches.
    - Ask before any step that destroys host state, including `lxc` deletions and Workshop removal.

    # Done when

    The decision record is committed and linked from `adr/README.md`, issue #21 is closed with its resolution comment, and the map's Decisions-so-far names it.

    # Report

    Finish with: what you did, what you found, what you did not verify, and what you need from the person.

Values and paths the session fixed, which the person's block does not name:

- The layout: "Two Workshop projects: `plane/` and `agent/`."
- The SDK name `iron-proxy`, the workshop name `plane`, and the fixed address
  `10.255.0.10` on `10.255.0.1/24`.
- The pin's home, `plane/.workshop/iron-proxy/proxy-digest.txt`, and the reason
  the agent gave: "The revision of an in-project SDK is a content hash of its
  whole directory, so a pin inside it makes a pin change install the new
  release with no operator bump."
- The record name and its title convention, from `adr/README.md`.
- The agent's report shape, which follows the block's `# Report` line: "## What
  I did", "## What I found", "## What I did not verify", "## What I need from
  you".

## Failures, their cause, and the fix

1. `!! FAILED edit` on `.kb/project.md`: "Could not find oldString in
   /home/.../.kb/project.md. It must match exactly, including whitespace and
   indentation." Cause: the anchor text was typed from an earlier read and the
   line breaks had moved. Fix: `read` at offset 30, then retry with the current
   text, which wraps "It holds" onto the first line.
2. `execute` was used to find a tool by name instead of calling it. Two calls
   ran `search({ query: "trail_add" })` inside `execute`, one with a bare
   `text(...)` and one with `return ...`. Fix: the next `execute` block called
   `tools.trail_add(...)` and `tools.trail_list({})` directly.
3. A memory claim contradicted the source. The agent's words: "A memory claim
   that the project is mounted read-only was wrong; I filed a correction." The
   evidence is in ADR 0006 and the upstream mount code: "Workshop mounts the
   project directory read-write at `/project` in every workshop of the
   project."

## Candidate lessons

- NEW: a grilling ticket is worked as a live exchange, and the agent does not
  answer its own questions. Quote: "Work the decision with the person. Grilling
  is a live exchange. Do not answer your own questions." (message 1). No file in
  the repository states it.
- NEW: a session that destroys host state asks first. Quote: "Ask before any
  step that destroys host state, including `lxc` deletions and Workshop
  removal." (message 1).
- NEW: a ticket session commits on its own branch and does no other git
  operation. Quote: "Commit on `wayfinder/plane-workshop-provisioning`. Do not
  push, merge, rebase, or touch other branches." (message 1). The person
  reversed this for one branch in message 2, which shows the rule is a default
  and the person lifts it: "then push to remote and open pr".
- NEW: the four-part closing report. Quote: "Finish with: what you did, what
  you found, what you did not verify, and what you need from the person."
  (message 1). `.kb/writing-style.md` §6 covers the verified and unverified
  part and not the other two.
- NEW: the ask block fixes a completion test before the work starts. Quote:
  "The decision record is committed and linked from `adr/README.md`, issue #21
  is closed with its resolution comment, and the map's Decisions-so-far names
  it." (message 1).
- ALREADY WRITTEN: the claim step and the resolve step of a wayfinder ticket.
  `.kb/issue-tracker.md` §Wayfinding operations states "Claim: `gh issue edit
  <n> --add-assignee @me`. This is the session's first write." and "Resolve:
  `gh issue comment <n> --body "<answer>"`, then `gh issue close <n>`, then
  append a context pointer to the map's Decisions-so-far."
- ALREADY WRITTEN: the project directory is mounted read-write at `/project`.
  ADR 0006:49.
- ALREADY WRITTEN: the SDK revision is a hash of every file in the SDK
  directory, so a pin inside it drives the revision. ADR 0006:44-46 and
  `.kb/agent-workshop.md:33-35`.
- NEW: a memory claim that a fact is settled is checked against the source
  before it is used, and a disagreement becomes a correction. Quote: "A memory
  claim that the project is mounted read-only was wrong; I filed a
  correction." (message 1 reply).
- PROJECT-SPECIFIC FACT: the six things ADR 0006 decides, the pin path, the
  `sdk.yaml` content and the `reload` route. The record and the tree hold them.
- PROJECT-SPECIFIC FACT: `ironsh/iron-proxy` redirects to
  `paradigmxyz/iron-proxy`. The agent's words: "The upstream moved:
  `ironsh/iron-proxy` redirects to `paradigmxyz/iron-proxy`." It belongs in
  `research/iron-proxy-plane.md`.

## What should not become a skill

- The 13 decisions. ADR 0006 holds them.
- The pin move and the `sdk.yaml` text.
- "Ask before any step that destroys host state" as a general repository law.
  It comes from the worktree ask template, and it bounds one session.
- The observation that a `question` answer is clipped by the transcript
  flatten. That is a loss of this export, and no rule prevents it.
