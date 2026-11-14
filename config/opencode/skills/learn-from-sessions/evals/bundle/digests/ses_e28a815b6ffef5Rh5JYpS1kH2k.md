# ses_e28a815b6ffef5Rh5JYpS1kH2k: ADR 0010 control service bounds

## What the person asked for

- "review @adr/0010-the-control-service-bounds-the-request-surface-and-runs-agent-code-as-the-operator.md" (USER 1, line 3)
- "I just rebased. validate the findings still exist, then fix them" (USER 2, line 84)
- "rebase on remote and then push" (USER 3, line 130)

## What was produced, and whether it worked

The first turn produced a review of ADR 0010 at commit `81b5ad5`. The verdict
was "Not ready. One finding is blocking. Four are minor." (line 37). The five
findings were:

1. Major. Line 27 said "The README states the reach." No README in the tree
   states it. The reach statement is in
   `.kb/development-workshop-authority.md`.
2. Minor. Lines 36, 44, 48-49 relied on phases 1, 2, and 3 with no cited
   source.
3. Minor. Line 9 said "a project with networks disabled" and named no setting.
4. Minor. Line 44 stated a host tunnel path the tree does not hold.
5. Minor. Lines 11 and 47 named the control service three ways.

The second turn validated the findings after a rebase and fixed all five in
commit `e8ad6b8` (local, not pushed). The record was untouched between
`81b5ad5` and the new HEAD `077a5ee` (line 110). The rebase added
`.workshop/dev.yaml` at the root, which changed no finding (line 111). The
fixes, one per finding, were:

1. Line 27 now points at the authority topology document (line 116).
2. Line 9 cites the research plan, and line 36 names phase 1 (line 117).
3. Line 9 now says "a project with `features.networks` disabled" (line 118).
4. Line 44 now states what the tree holds and moves the path detail to
   phase 3 (line 119).
5. Line 11 and line 47 drop "the service" (line 120).

The third turn rebased onto the remote and pushed. The fix replayed as
`71fbcde` with no conflicts, touching only the ADR record, 6 insertions and
6 deletions (line 138). The push moved `ee754f9..71fbcde main -> main`
(line 140).

Verified:

- `just style` on the record: 1 finding before, `0 finding(s) in 1 file(s)`
  after (line 124).
- `ste-lint.py` on the record: 0 violations, 790 words (line 125).
- `just test` passed: 113 tests in 2.59s (line 74).

Not verified:

- The host-side path of a definition tunnel. No measurement exists in the
  definitions, the research records, or the spike branches (line 78).
- The daemon does not exist in the tree yet, so no claim about its behavior
  was checked against code (line 82).

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

- "I just rebased. validate the findings still exist, then fix them" (USER 2,
  line 84). The person re-checks a review's findings against the current tree
  before they are fixed.
- "rebase on remote and then push" (USER 3, line 130). The person rebases
  local work onto `origin/main` and re-runs the gate before a push.

## Failures, their cause, and the fix

- The first `skill` load for `asd-ste100` failed (line 152). The harness
  answered `{"type":"aborted","message":"Interaction cancelled because the
  location shut down"}` (line 153). The cause was a transient environment
  shutdown. The fix was to load the skill again, which succeeded (line 154).

## Candidate lessons

- NEW. After a rebase, re-check each review finding against the current tree
  before fixing it, because the rebase can add documents that change the
  verdict. Source: "I just rebased. validate the findings still exist, then
  fix them" (USER 2, line 84). The agent gave the reason: "since the rebase
  added documents that could change the verdict" (line 88).
- NEW. After a rebase that changes the style checker, re-run `just style` on
  the record before pushing, because the earlier clean result no longer
  holds. Source: "Because the rebase brought the updated style checker
  (`262d684`), I re-ran the gate on the record before pushing" (line 139).
- NEW. The house commit body is short prose paragraphs. Source: "The house
  body style is short prose paragraphs." (line 104). This is the agent's
  reading of the last two commits, not a rule the person stated. The synthesis
  should verify it against the repository before it becomes a rule.
- ALREADY WRITTEN. Run `just style <file>` on every changed Markdown file
  before a commit, and fix a banned word on any line the change touches. The
  checker flagged `carries` on line 9, a line the fixes touched (line 96).
  This rule is in `AGENTS.md` under "Working rules", and the banned word list
  is in `.kb/writing-style.md`.
- ALREADY WRITTEN. Cite another record or research record as a short link,
  such as `[ADR 0001](0001-the-slug.md)`. The fixes added a link to
  `.kb/development-workshop-authority.md` and a research link (lines 116-117).
  This rule is in `.kb/writing-style.md` under "Decision records".
- ALREADY WRITTEN. A decision record is written to be understood on one
  reading, and a claim that names a document the tree does not hold is a
  blocking finding. Source: "A reader who takes the sentence at its word looks
  for a document that does not exist" (line 45). This rule is in
  `.kb/writing-style.md` and `adr/README.md`.
- ALREADY WRITTEN. The review method: read the records the change cites,
  verify each factual claim against the tree, run `just test` as the entry
  point, and separate "What I checked and found sound" from "Not verified".
  This session followed `.opencode/skills/review-a-change/SKILL.md`.

## What should not become a skill

- The five ADR 0010 findings and their fixes. They are record-specific
  corrections that now live in the record itself.
- The verb count of the control service. Five fence verbs plus `policy-reload`
  plus `exec` make seven (line 69). This is in `GLOSSARY.md` and
  `.kb/development-workshop-authority.md`.
- The phase definitions. The three phases are defined in
  `research/development-workshop.md` under "The phases" (line 51).
