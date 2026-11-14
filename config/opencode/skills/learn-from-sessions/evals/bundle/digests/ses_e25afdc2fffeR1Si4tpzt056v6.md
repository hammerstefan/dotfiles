# ses_e25afdc2fffeR1Si4tpzt056v6: Fix workshop docs and diagram

## What the person asked for

This session is a fix child of the documentation review. The parent session wrote
the assignment as the USER turn. Its words, quoted in order:

- "Read AGENTS.md, .kb/agents.md and .kb/writing-style.md first." USER 1 (line 4)
- "Fix the findings assigned to you below by editing the named documents." USER 1 (line 4)
- "Edit ONLY the files in your assignment. Other agents edit the other files in
  parallel (one is editing GLOSSARY.md). Do not commit, do not push, do not run
  git add." USER 1 (line 5)
- "Verify facts against the repository (code, justfile, scripts, ADRs, git
  history, upstream Workshop docs) before you write. Never invent a fact." USER 1 (line 6)
- "If a finding needs an owner decision or the facts cannot be established, do
  not guess: leave the text, and report the item as open with the reason." USER 1 (line 6)
- "Run `just style <file>` on every Markdown file you changed and fix its
  findings." USER 1 (line 7)
- "Final answer: per finding, either "fixed: file — what changed" or "open:
  reason". Keep it short." USER 1 (line 8)
- "aligning .kb/agent-workshop.md:3 and the diagram labels with the glossary's
  terms (Workshop/workshop, Hermes Agent/hermes)." USER 1 (line 10)
- "Re-render the HTML and SVG through the process .kb/topologies.md describes
  (the `diagram` skill may help). If the rendering tooling is unavailable, report
  that item open rather than hand-editing rendered output inconsistently." USER 1 (line 10)

## What was produced, and whether it worked

The agent edited six files in the worktree `review-writing`, and it made no
commit, no push, and no stage. "I did not stage, commit or push anything."
(line 14)

The files are `.kb/agent-workshop.md`, `.kb/development-workshop-authority.md`,
`.kb/development-workshop.md`, `.kb/fence.md`,
`.kb/privileged-conformance-suite.md`, and
`.kb/topologies/development-workshop-authority/*` (the `.mmd`, `.svg`, and
`.html`).

The fixes:

- The six host verbs became seven. "now lists the seven verbs as ADR 0010 gives
  them: `apply`, `launch`, `refresh`, `restore` and `remove` run the fence
  command, `policy-reload` runs the plane reload recipe, and `exec` is the
  seventh." (line 17)
- The fence wrapper verbs are listed, and the agent stated it has no `start` or
  `stop` verb. The operator action after `workshop start` or `stop` is open,
  because no ADR or doc decides it. (line 18)
- The lock-file ids are named apart. "Each id is the suffix of the running
  instance name (`agent-{id}` or `plane-{id}`) that `lxc list --all-projects`
  prints." (line 19)
- The reconnect condition names both `connect` commands after a `restore`, and
  after a `launch` that follows a `remove`. (line 20)
- The conformance states add `not run` to the list, and the planned-suite note
  moved into the Preface. (line 21)
- The file-loss event says files outside `/project` are lost after
  `workshop remove dev` and a new `workshop launch dev`. Whether `refresh` or
  `restore` also discards those files is open. (line 22)
- The secret interface names the Workshop secret interface and says the helper
  reads each value with `workshopctl get-secret`. (line 23)
- The "served set" readiness sign is open, because no file states what shows the
  gateway is ready. (line 24)
- The diagram got `accTitle` and `accDescr` in the `.mmd`, was re-rendered with
  the `diagram` skill, and the SVG now has `<title>` and `<desc>`. "After the
  render I changed the `script` element to the CDN address, as `.kb/topologies.md`
  says. I looked at the PNG render, and no labels overlap." (line 25)
- The edge now reads "starts and stops", matching ADR 0010
  (`systemctl --user stop`). (line 26)
- The minor suggestions: "live in" is now "are stored in", "names a named custom
  provider" now reads "declares a custom provider under its own name" (line 29),
  "placement" is defined at first use, "the bound" is now "the six-attempt
  limit" (line 30).
- The authority doc now links to the HTML page, and its last-check date is
  November 14, 2026. (line 31)
- ".kb/agent-workshop.md:3" now reads "hermes, the Hermes Agent" (line 34), and
  the group labels now read "Development workshop: dev" and "Product workshops"
  (line 35).

Verified: "`just style` reports 0 findings on all five Markdown files I
changed." (line 14). The agent ran `just style .kb/development-workshop-authority.md`
and it returned a clean tail (line 61). The agent looked at the PNG render and
reported no overlapping labels (line 25).

Not verified: the open items above (lines 18, 22, 24, 25).

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

These come from the parent session's assignment, not from a repository file.

- The report shape "per finding, either "fixed: file — what changed" or "open:
  reason"" (line 8).
- The rule "report the item as open with the reason" when a finding needs an
  owner decision or the facts cannot be established (line 6).
- The rule "report that item open rather than hand-editing rendered output
  inconsistently" when the rendering tooling is unavailable (line 10).

## Failures, their cause, and the fix

(none found)

## Candidate lessons

- "Run `just style <file>` on every Markdown file you changed and fix its
  findings." USER 1 (line 7). ALREADY WRITTEN in AGENTS.md working rules.
- "Verify facts against the repository ... before you write. Never invent a
  fact." USER 1 (line 6). ALREADY WRITTEN in `.kb/writing-style.md` §6.
- "do not guess: leave the text, and report the item as open with the reason."
  USER 1 (line 6). NEW. A docs-fix finding that needs an owner decision or a
  fact the repository does not state is reported open with a reason, never
  guessed.
- "Final answer: per finding, either "fixed: file — what changed" or "open:
  reason"." USER 1 (line 8). NEW. This is the report shape a parallel
  documentation-fix assignment returns, one line per finding.
- "report that item open rather than hand-editing rendered output
  inconsistently." USER 1 (line 10). NEW. A missing renderer is reported open,
  never worked around by editing the SVG or HTML by hand.
- "I added `accTitle` and `accDescr` to the `.mmd` ... The SVG now has `<title>`
  and `<desc>`." ASSISTANT (line 25). NEW. A Mermaid source carries accessibility
  text through `accTitle` and `accDescr`, which the render turns into the SVG
  `<title>` and `<desc>`. The agent states this. No repository file records it.
- "The skill's HTML template fixes those buttons, so the change belongs in the
  skill, not in the generated file." ASSISTANT (line 25). NEW. The accessible
  names for the zoom buttons belong in the global `diagram` skill HTML template,
  not in the generated page. The agent states this.
- "After the render I changed the `script` element to the CDN address, as
  `.kb/topologies.md` says." ASSISTANT (line 25). ALREADY WRITTEN in
  `.kb/topologies.md` §4 and "Making one".
- "the seven verbs as ADR 0010 gives them: `apply`, `launch`, `refresh`,
  `restore` and `remove` run the fence command, `policy-reload` runs the plane
  reload recipe, and `exec` is the seventh." ASSISTANT (line 17).
  PROJECT-SPECIFIC FACT. Stated in ADR 0010 and GLOSSARY.md.
- "Each id is the suffix of the running instance name (`agent-{id}` or
  `plane-{id}`) that `lxc list --all-projects` prints." ASSISTANT (line 19).
  PROJECT-SPECIFIC FACT.

## What should not become a skill

- The glossary capitalization rule (Workshop/workshop, Hermes Agent/hermes) is
  already fixed in GLOSSARY.md. The fix here only applied it to two documents.
- The specific wording changes to each `.kb` file are facts about those
  documents, not reusable rules.
- The security note that the HTML page loads Mermaid 12.3.0 with no integrity
  check (line 38) is a known fact, unchanged by this session.
