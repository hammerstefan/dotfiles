# ses_e25b68d12ffe3XfAGBBJ5TE0P9: Documentation readability review verification

## What the person asked for

USER 1 (line 3): "verify @docs/documentation-readability-review.md"

## What was produced, and whether it worked

The agent produced a written verdict, not a commit. It made no edits. The
final `git status --short --untracked-files=all` lists only the original
untracked report (line 75).

The verdict opened with "not ready as a fully verified review" (line 5). It
found two Major errors in the report and many non-blocking citation
corrections (lines 11-64). It reproduced the report's mechanical checks and
passed the test suite (lines 68-75).

The checks the agent reproduced, each with a failure control (lines 68-75):

- Inventory: `git ls-files` grouped 63 files, 60 Markdown and three diagram
  files. Removing one file produced the missing-file result. Duplicating one
  produced the duplicate-file result.
- References: all 120 backticked path-and-line references resolved to existing
  files and in-range lines. A planted out-of-range `GLOSSARY.md` reference
  failed the check.
- Style: `just style docs/documentation-readability-review.md` returned zero
  findings. A temporary file with a planted em dash returned one finding and
  exit status 1.
- Accessibility source: the Mermaid source has no `accTitle` or `accDescr`,
  and the SVG has no `<title>` or `<desc>`. Positive controls detected the
  tokens.
- Regression: `just test` passed.

The agent listed three items it did not verify (lines 79-82):

- The coverage claim at `docs/documentation-readability-review.md:447-450`
  about what the original reviewers read has no review transcripts in the
  checkout.
- No browser accessibility tree was inspected.
- No Workshop, LXD, proxy, or lifecycle measurement was rerun.

The agent spawned seven `review-readability` subagents in parallel, one per
domain of the report (lines 96-102). It later sent two follow-up prompts to
close gaps in their reads (lines 112-113).

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

(none found)

## Failures, their cause, and the fix

No `!! FAILED` tool line appears in the log. One subagent under-read its
sources. The follow-up prompt stated the cause and the fix (line 112):

> Your previous run did not satisfy the full-read requirement: your own
> limits say several generated commands were only searched and
> constitution-template.md was not opened.

The follow-up demanded a full read of every generated command and closed the
gap (line 112).

## Candidate lessons

- NEW. "Both say **"tunnel listener."** The differing term is **"CONNECT
  listener port"** in ADR 0005:134." (assistant, line 23). A finding that
  claims two sources differ must read both cited lines and show the
  difference.
- NEW. "the bridge gateway address appears at `research/separate-bridges.md:89`,
  not the cited lines 19-20." (assistant, line 47). A reference check that
  proves a line is in range does not prove the cited content is at that line.
  Verify the content, not the range.
- NEW. "the `workshop --project <directory>` sentence is already immediately
  after the lock-file instruction at `.kb/fence.md:141`. Remove the relocation
  request." (assistant, line 34). Before a review asks to move text, check
  that the text is not already placed where the finding wants it.
- NEW. "required approval would be a new rule, not clarification of an
  existing one. Identify it as a proposed owner decision." (assistant, line
  56). A finding that adds a required approval is a proposed new rule. Label
  it a proposal, not a clarification.
- NEW. "the glossary does not define terms that distinguish "channel,"
  "route," and "transport.""Use the glossary's terms" is not actionable until
  the report selects or defines a term." (assistant, line 53). A review that
  says to use the glossary's terms must confirm the glossary defines them
  first.
- ALREADY WRITTEN. "A unique temporary file containing a planted em dash
  returned one finding and exit status 1." (assistant, line 71). This restates
  `.opencode/skills/verify-a-claim/SKILL.md`, "Feed it a known-bad input."
- ALREADY WRITTEN. "> Neither urgency nor a bug-fix framing makes it
  maintenance." (assistant, line 15, quoting the source). The report reversed
  a source rule. This restates `.opencode/skills/verify-a-claim/SKILL.md`,
  "Compare a value against the source that names it."
- ALREADY WRITTEN. "The statements at
  `docs/documentation-readability-review.md:447-450` about what the original
  reviewers read have no accompanying review transcripts in this checkout."
  (assistant, line 79). This restates the "Not verified" rules in
  `.opencode/skills/verify-a-claim/SKILL.md` and
  `.opencode/skills/review-a-change/SKILL.md`.
- ALREADY WRITTEN. "Your previous run did not satisfy the full-read
  requirement: your own limits say several generated commands were only
  searched." (assistant, line 112). This restates
  `.opencode/skills/verify-a-claim/SKILL.md`, "A parent repeats a child's
  verdict only after the child's own tool log shows the command."
- PROJECT-SPECIFIC FACT. "Local Git history contains no addition, deletion, or
  rename of `adr/0003*`." (assistant, line 82). This is a fact about this
  repository's history, not a skill.

## What should not become a skill

- The individual citation corrections (lines 33-64). Each names the exact
  right and wrong line in one report. They are one-off fixes to that report.
- The ADR 0001 history evidence, commits `46404ece` and `5c7528a` (line 43).
  This is repository history, which belongs in the records.
- The finding that the report's coverage claim at lines 447-450 has no
  transcripts (line 79). This is a statement about one report's reach, not a
  rule.
