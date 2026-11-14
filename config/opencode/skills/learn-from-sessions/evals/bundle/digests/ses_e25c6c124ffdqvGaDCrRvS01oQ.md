# ses_e25c6c124ffdqvGaDCrRvS01oQ: Review workshop operations guidance

## What the person asked for

The session opened with one instruction, a subagent spawn from a review
coordinator. USER 1 (line 2) asked for a "Read-only readability review of
group WORKSHOP GUIDANCE AND DIAGRAM" (line 3). The rest of the brief:

- "Review EVERY listed file" (line 3). It named `.kb/agent-workshop.md`,
  `.kb/development-workshop-authority.md`, `.kb/development-workshop.md`,
  `.kb/fence.md`, `.kb/privileged-conformance-suite.md`, the topology source
  `.kb/topologies/development-workshop-authority/development-workshop-authority.mmd`,
  and "its generated rendered counterparts .html and .svg" (line 3).
- "For rendered diagram, concentrate on human-facing labels/alt
  text/accessibility and report duplicate content once at the Mermaid source
  if same issue is in copies" (line 4).
- "Apply .kb/writing-style.md" (line 4).
- "Return full file list examined, up to 12 actionable findings with exact
  path:line, quote, reader impact and proposed fix; separate minor editorial
  suggestions and cross-file issues" (line 4).
- "Avoid changing normative technical meaning or inferring unverified
  behavior. Do not edit files." (line 4).

The person gave no further turns.

## What was produced, and whether it worked

The agent read the six `.kb` files, the `.mmd` source, and grepped the
rendered HTML and SVG for accessibility attributes. It made no edits. It
returned a findings list of 12 items and a separate suggestions list of 19
items, then two structured blocks, `review-json` (line 133) and
`review-readability-json` (line 143).

It read these files (line 13): `.kb/writing-style.md` (style reference),
`.kb/agent-workshop.md`, `.kb/development-workshop-authority.md`,
`.kb/development-workshop.md`, `.kb/fence.md`,
`.kb/privileged-conformance-suite.md`, the `.mmd` source, the `.html`, and
the `.svg`.

The 12 findings, each as severity, file:line, and the fix:

- RDB-1 (medium) `.kb/development-workshop-authority.md:29` (line 27). The
  "six verbs" are never named. The diagram shows only four. Fix: list the six
  host verbs and say `exec` is not one of them.
- RDB-2 (medium) `.kb/development-workshop-authority.md:34` (line 33).
  "reach" has no definition, and it can mean host changes or workshop access.
  Fix: add one sentence on what the reach includes.
- RDB-3 (medium) `.kb/agent-workshop.md:52` (line 39). "a `remove` and a
  `launch` leaves the workshop unconnected" can mean each command or a
  sequence. Fix: write "A `remove` followed by a `launch`".
- RDB-4 (medium) `.kb/fence.md:139` (line 45). The lock-file step does not say
  which id to write to each of the two lock files. Fix: name the source of
  each id.
- RDB-5 (medium) `.kb/fence.md:64` (line 51). `start` and `stop` conflict with
  the wrapper verbs `launch`, `refresh`, `restore`, `remove`. Fix: say how the
  operator runs `start` and `stop`.
- RDB-6 (medium) `.kb/privileged-conformance-suite.md:201` (line 57). The
  list of check states omits `not run`, used at line 211. Fix: add `not run`.
- RDB-7 (medium) `.mmd:518` (line 63). The diagram has no accessible title or
  description. Fix: add `accTitle:` and `accDescr:` after `flowchart LR`.
- RDB-8 (low) `.kb/privileged-conformance-suite.md:52` (line 68). The
  document describes tests not yet in the tree. Fix: add a status note naming
  ticket #70.
- RDB-9 (low) `.kb/development-workshop.md:49` (line 74). "launched again"
  conflicts with the `launch` rule that refuses an existing workshop. Fix:
  name the commands that lose the files.
- RDB-10 (low) `.kb/agent-workshop.md:73` (line 80). "secret interface" has
  no definition. Fix: name the part.
- RDB-11 (low) `.kb/agent-workshop.md:81` (line 86). "served set" has no
  definition. Fix: say what the gateway publishes and the ready sign.
- RDB-12 (low) `.mmd:537` (line 92). The diagram verb "revokes" differs from
  the text verb "stops". Fix: use "starts and stops".

The 19 suggestions span cross-file issues and per-file edits. Three are
cross-file (line 101): RDS-1 "live in" is a banned figurative verb, RDS-2
"hermes" versus "Hermes", RDS-3 capitalized "Workshop" in diagram labels. The
rest are one-line edits per file, each with `id`, `file`, `line`, `original`,
`problem`, `suggested_edit`.

Nothing was verified by command. The review changed no files, so there is no
commit or branch. The output is read-only review feedback only.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

The brief stated one review-scoping rule that no file in the repository or the
review council writes down:

- "report duplicate content once at the Mermaid source if same issue is in
  copies" (USER 1, line 4). The agent restated it: "The HTML and SVG files
  repeat the Mermaid labels. I report each diagram problem once, at the
  `.mmd` source." (line 23).

The finding shape is the agent's output following the review council contract,
not something the person stated. The agent loaded `review-council.md`,
`readability-criteria.md`, and the `asd-ste100` skill (lines 141-143) before
writing the findings.

## Failures, their cause, and the fix

(none found)

## Candidate lessons

- NEW. A rendered Mermaid diagram needs screen-reader labels. RDB-7: "Add
  `accTitle:` and `accDescr:` lines after `flowchart LR`, then render the
  diagram again." (line 66). RDS-19: "Add `aria-label=\"Zoom out\"` and
  `aria-label=\"Zoom in\"`." (line 131). `.kb/topologies.md` §4 names the
  source, SVG, and HTML files and the brand contract, but the contract covers
  "color, font, text size, corner shape, and geometry", not accessibility.
  This lesson belongs in `.kb/topologies.md` or the global `diagram` skill.
- NEW. When a rendered diagram's copies repeat a label issue, report it once
  at the `.mmd` source. USER 1 (line 4), restated by the agent (line 23).
  Not in `review-council.md` or `readability-criteria.md`.
- ALREADY WRITTEN. The readability finding shape: `id`, `file`, `line`,
  `category`, `severity`, `confidence`, `title`, `rationale`,
  `suggested_fix`, `out_of_scope` (line 135). This is the review council
  contract in `review-council.md` and `readability-criteria.md`.
- ALREADY WRITTEN. When the source cannot support a precise edit, request an
  author decision instead of inventing one. The fixes say "The author must
  supply this" (line 31) and "The author must confirm" (line 84).
  `readability-criteria.md` states "Request a definition, reference, or author
  decision when the source cannot support a precise edit."
- ALREADY WRITTEN. "live in" is a banned figurative verb. RDS-1 (line 101).
  `.kb/writing-style.md` line 70 lists "lives in" in its banned-words table.
- PROJECT-SPECIFIC FACT. The 12 findings name exact defects in six `.kb`
  files and the topology source with line numbers. They belong in a follow-up
  edit, not a skill.
- PROJECT-SPECIFIC FACT. The product name is "Hermes", the command is
  `hermes`. RDS-2 (line 102).

## What should not become a skill

- The 19 editorial suggestions are one-off wording edits to specific files.
  They do not generalize.
- The 12 findings are defects to fix in the reviewed files, not review method.
- The finding and suggestion JSON schemas are already the review council's
  output contract. A skill that restated them would duplicate
  `review-council.md` and `readability-criteria.md`.
