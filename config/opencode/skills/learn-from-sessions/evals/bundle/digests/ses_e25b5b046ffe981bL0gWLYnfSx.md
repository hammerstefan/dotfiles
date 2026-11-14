# ses_e25b5b046ffe981bL0gWLYnfSx: Verify project guidance findings

## What the person asked for

The session is a verification child of a documentation readability review. The
caller wrote, USER 1 (line 3):

> You are a subagent spawned by another session.

Then USER 1 (line 4):

> Read-only verification of an existing documentation readability review.

> Verify ONLY the 'Project guidance' findings and, under Minor editorial
> suggestions, the items whose cited files belong to project guidance:
> duplicated guidance, unclear shorthand, repetitive prose, plain-word rules.

> Read every cited source file in full, not only cited lines.

> For each report bullet, independently decide whether each factual claim is
> supported and whether the proposed readability problem is real. Check exact
> line citations and cross-references.

> Return a compact item-by-item table with status VERIFIED, PARTLY VERIFIED,
> UNSUPPORTED, INCORRECT, or INCONCLUSIVE; exact source line evidence; and any
> needed correction.

> Do not edit files, run workshops, mutate git, or use network.

> This is verification of the cited claims, not a fresh usability review.

The caller named the worktree and commit, USER 1 (line 4):

> Work in /home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/review-writing at HEAD 9003ccd6937060f2bb697ac69a871070e326b665.

It named the report, USER 1 (line 4):

> The report is the untracked file docs/documentation-readability-review.md.

It named the two files to read first, USER 1 (line 4):

> Read .kb/agents.md and .kb/writing-style.md first.

## What was produced, and whether it worked

The agent produced an item-by-item table of eleven report items. The agent
wrote, (line 8):

> Of the 11 items, 8 are verified and 3 are partly verified. No item is
> unsupported or incorrect, and all line citations are correct.

The three partly verified items are items 2, 5, and 6. The agent gave a
correction for each partly verified item.

The agent changed no files. The tool log holds only reads and one skill load.
No commit, branch, or pull request was made.

The agent read these files in full: `AGENTS.md`, `GLOSSARY.md`, `.kb/agents.md`,
`.kb/writing-style.md`, `.kb/issue-tracker.md`, `.kb/project.md`,
`.kb/spikes.md`, `.kb/topologies.md`, `.kb/spec-kit.md`, and
`.kb/requirements-format.md`.

The agent read only cited parts of three files, and said so, (line 33):

> I read only the cited excerpts of `adr/0010…md` (lines 1-30),
> `.kb/agent-workshop.md` (lines 1-12), and the `.mmd` file (lines 520-539).
> Other content in those files could resolve or change items 5 and 6.

This partial read leaves items 5 and 6 only partly verified, by the agent's own
limit.

The agent could not check three things, and said so. It wrote, (line 34):

> I could not find out whether the Workshop/workshop and Hermes/hermes
> capitalization is deliberate. Only the author can settle that.

It wrote, (line 35):

> I did not check the upstream Workshop lifecycle command names.

It wrote, (line 36):

> I did not run `just style` or any other tool.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

The caller named a five-status verification set, USER 1 (line 4):

> status VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, or INCONCLUSIVE

This set is not written in any repository skill. The `verify-a-claim` skill
names only "verified" and "inconclusive". The `review-a-change` skill uses a
severity scale of critical, high, medium, and low, not a verification status.

The caller named a two-axis test for each finding, USER 1 (line 4):

> independently decide whether each factual claim is supported and whether the
> proposed readability problem is real

The `verify-a-claim` skill checks a claim against the code but does not name
this two-axis test. The two axes are the fact and the problem.

The caller named a citation check, USER 1 (line 4):

> Check exact line citations and cross-references.

No skill states this check.

The caller named the worktree HEAD, USER 1 (line 4):

> at HEAD 9003ccd6937060f2bb697ac69a871070e326b665

The caller named four minor-editorial categories that belong to project
guidance, USER 1 (line 4):

> duplicated guidance, unclear shorthand, repetitive prose, plain-word rules

## Failures, their cause, and the fix

(none found)

No `!! FAILED` line appears in the tool log. Every tool call returned `ok`.

## Candidate lessons

- NEW. The five-status verification set "VERIFIED, PARTLY VERIFIED, UNSUPPORTED,
  INCORRECT, or INCONCLUSIVE" belongs in the `verify-a-claim` skill, which now
  names only "verified" and "inconclusive". USER 1 (line 4).
- NEW. Verify each review finding on two axes, the factual claim and the
  proposed problem, as stated "independently decide whether each factual claim
  is supported and whether the proposed readability problem is real". USER 1
  (line 4).
- NEW. Verify a review finding by its exact line citations and
  cross-references, not only by reading the cited lines. USER 1 (line 4).
- PROJECT-SPECIFIC FACT. Report item 2 misstates its source. The agent wrote
  that the source says the opposite of what the report claims, (line 15): "The
  source says the opposite: a bug-fix framing does **not** make the change
  maintenance." This correction belongs in the parent review.
- PROJECT-SPECIFIC FACT. Report item 6 proposed rewriting a bound entry "as two
  sentences". The agent wrote that the entry already has three sentences, (line
  19): "lines 74-76 already have three sentences." This correction belongs in
  the parent review.
- PROJECT-SPECIFIC FACT. The report treats the Workshop/workshop and
  Hermes/hermes capitalization split as a defect. The agent wrote that the
  split may be deliberate, (line 18): "The capital/lowercase split may be
  deliberate." This is a question for the author, not a defect.

## What should not become a skill

The eleven readability findings and their line corrections are defects in the
monitor-agent documentation. They belong in the parent review report
`docs/documentation-readability-review.md`, not in a skill. Each finding names a
specific file and line. No finding is a reusable rule.
