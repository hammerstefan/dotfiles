# ses_e2f1bf293ffepPEMmljJy05Zwy: Review PR 30

## What the person asked for

This session's `USER` block is the prompt that the session
`ses_e2f2b2b00ffeXWdtibMXa55t80` sent to a review subagent. The orchestrating
agent wrote it, so the lines below are not the person's own words. They are
quoted because they define how a review subagent is briefed here.

- "Review PR #30 in hammerstefan/monitor-agent:
  https://github.com/hammerstefan/monitor-agent/pull/30"
- "Review the diff on its own merits:" followed by five numbered tasks, which
  are: read `adr/README.md` for the conventions, "Verify every factual claim in
  the changed sentences against ADR 0005 and the rest of the repo", check that
  the removed link leaves no dangling reference, "Check STE/writing-style
  compliance of the new prose", and "Flag any scope problem".
- "Report concrete findings with file:line references, severity (blocking /
  should-fix / nit), and a clear verdict. Do not modify files. Do not post
  anything to GitHub."

The person's own instruction behind it is one line, in the other session:
"@review-deepseek pr30".

## What was produced, and whether it worked

- A review report with eight findings: one blocking, one should-fix, one nit
  and five passes, closed with a verdict.
- The blocking finding: "The same staleness error the PR fixes in Consequences
  (ADR 0005 no longer states `.workshop/`) remains uncorrected in the Context
  paragraph at lines 60–63." It names its fix: "The Context paragraph should
  either (a) say ADR 0005 *originally* placed the SDK under `.workshop/`
  ... or (b) drop the claim about ADR 0005's path".
- The should-fix finding: "ADR 0001 still claims: `adr/0001-…`, line 121:
  "Every command runs as root in the persistent agent workshop container"".
- The nit: "The new prose is a single sentence of 24 words" against "ASD-STE100
  rule 1.8 limits descriptive sentences to 25 words".
- Five passes: the capitalization of "Hermes", the rejected-alternative
  justification, the removed link, the STE and writing-style check, and the PR
  body's scope description.
- It modified no file and posted nothing to GitHub. The tool log holds reads, a
  `glob`, one `review_inspect` call with `pr_diff`, and nothing that writes.
- Verified: the blocking finding was acted on in the orchestrating session. The
  worktree `docs-adr-0006-review-notes` stands at
  `39ac14e docs: correct the agent SDK path claim in the plane record`, and the
  agent there wrote "It's now "placed", which is true".
- Verified: the should-fix finding was carried out later. ADR 0001 lines
  130-131 now read "Every command runs as the workshop user in the persistent
  agent workshop container." Commit `e62db42 docs: correct the root claim in
  the agent record` carried the change.
- Not verified: the claim that ASD-STE100 rule 1.8 sets a 25-word limit. No file
  in the repository states the limit, and the review points to no source.
- Not verified: "`ste-lint` already reports 0 violations". The review repeated
  the claim from its prompt.

## Corrections the person made

(none found). The session received no message after the prompt.

## Conventions, commands and values stated and written down nowhere

- The severity vocabulary "blocking / should-fix / nit".
- The evidence a finding holds: "concrete findings with file:line
  references". The report gives `adr/0006-…`, lines 60–63 and `adr/0001-…`,
  line 121.
- The two prohibitions for a review subagent: "Do not modify files. Do not post
  anything to GitHub."
- The instruction to read the record convention before the diff:
  "Read `adr/README.md` for the conventions an accepted record must follow
  (in-place amendment, STE style, no dates, section shape)."
- The agent's route to the diff: `review_inspect` with `operation: "pr_diff"`
  and `number: 30`. It also read the PR diff on the host earlier in the
  orchestrating session with `gh pr diff`.
- The agent's judgement that a scope gap is a finding about the record set, in
  its words: "not a regression introduced by this PR ... but by aligning ADR
  0006 with ADR 0005, the PR makes ADR 0001 line 121 stand out as the isolated
  stale claim".

## Failures, their cause, and the fix

1. `!! FAILED read` on
   `.../adr/0005-the-agent-workshop-is-sandboxed-through-the-plane-workshop-proxy.md`:
   "File not found". Cause: the slug was invented. Fix: `glob` with
   `adr/0005-*`, which named
   `adr/0005-the-agent-workshop-installs-hermes-through-a-project-sdk.md`.
2. `!! FAILED read` on `.../adr/0001-agent-workshop-container.md`: "File not
   found". Cause: the slug was guessed from the record's subject. Fix: `glob`
   with `adr/0001-*`, which named the real file.
3. The `adr/README.md` example name invites both failures. Its Conventions
   section says "named `NNNN-slug.md` (for example
   `0001-the-agent-runs-in-a-workshop.md`)", and that example file does not
   exist.

## Candidate lessons

- NEW: a record is found with a glob on its number, and its slug is never
  guessed. Quote: "File not found:
  .../adr/0001-agent-workshop-container.md" (tool log). `adr/README.md` names
  the pattern and gives an example file name that is not in the repository.
- NEW: a review finding states file and line, and a severity from one
  vocabulary. Quote: "Report concrete findings with file:line references,
  severity (blocking / should-fix / nit), and a clear verdict." (USER block).
- NEW: a review subagent changes no file and posts nothing. Quote: "Do not
  modify files. Do not post anything to GitHub." (USER block).
- NEW: a review of an amendment checks every paragraph for the claim the
  amendment moves, not only the paragraph the note names. Quote: "The record is
  not internally consistent with its own linked evidence." (review report).
- NEW: a claim about a record's content is checked against the record as it
  stands after the patch. Quote: "A reader who follows the link to ADR 0005
  will find `agent/.workshop/`, not `.workshop/`." (review report).
- ALREADY WRITTEN: a record is written in ASD-STE100 and checked with
  `ste-lint.py`. `adr/README.md` §Conventions.
- ALREADY WRITTEN: a record is understood on one reading by someone who took no
  part in the decision. `.kb/writing-style.md` §4, and the review quotes it.
- PROJECT-SPECIFIC FACT: the STE sentence-length number "25 words" for rule
  1.8. It comes from the `asd-ste100` skill, and it belongs there or in
  `adr/README.md`.
- PROJECT-SPECIFIC FACT: ADR 0001's stale root claim, and the two records that
  disagree with it. The records hold the corrected text now.

## What should not become a skill

- The eight findings on PR #30. They are one patch.
- The verdict sentence for this pull request.
- The claim about the STE sentence-length limit read as a repository rule. It is
  a reading of another skill's standard, and the review names no source.
