# ses_e25b5b02dffdWJSam3NwYKuor6: Verify generated SpecKit findings

## What the person asked for

- USER 1 (line 4): "Read-only verification of an existing documentation
  readability review."
- USER 1 (line 4): "Verify ALL 'Generated Spec Kit prose and local
  integration' findings and the Minor editorial item 'Tighten upstream
  command prose at regeneration time'."
- USER 1 (line 4): "Read all nine .opencode/commands/speckit.*.md files,
  .specify/memory/constitution.md, and all five .specify/templates/*.md files
  in full."
- USER 1 (line 4): "Return a compact item-by-item table with status VERIFIED,
  PARTLY VERIFIED, UNSUPPORTED, INCORRECT, or INCONCLUSIVE; exact source line
  evidence; and any needed correction."
- USER 1 (line 4): "Do not edit generated files, mutate git, run workshops, or
  use network."
- USER 2 (line 54): "Now read in full every one of the nine
  .opencode/commands/speckit.*.md files, .specify/memory/constitution.md, and
  all five .specify/templates/*.md files, plus .kb/agents.md,
  .kb/writing-style.md, and .kb/requirements-format.md."
- USER 2 (line 54): "Return only changed verdicts/corrections, an explicit
  full-coverage statement, and remaining limits."

## What was produced, and whether it worked

Two prose replies. No commits, branches, records, or pull requests. The
session was read-only and produced no repository files.

The first reply (ASSISTANT 1, line 6) gives a nine row table with one row per
report item plus the minor item, each row holding a status, source evidence,
and a correction. Its "What I could not check" list (line 26) admits it read
parts of only four commands and searched the rest.

The person rejected that reply for partial reads.

The second reply (ASSISTANT 2, line 56) reports that no verdict changed and
gives a changed corrections table (line 60) for five items. It ends with a
coverage list (line 77) and a remaining limits list (line 87).

Statuses assigned: VERIFIED for items 1, 2, 4, 6b, and 6c. PARTLY VERIFIED
for items 3, 5, 7a, 7b, and M. Item 6a is "PARTLY VERIFIED / INCORRECT in
detail" (line 17).

One correction changed content after the full read. The minor item about
"clean up obsolete checklists" became a contradiction with "Never delete or
replace existing checklist content" (line 66), not only an unclear actor.

The agent states upstream and local disposition is sound for every item
(line 24 and line 75).

Verified: the nine speckit commands, the constitution, the five templates,
and the four .kb files were read in full in the second run (line 79).

Not verified: the helper scripts the commands call, named as
`resolve-template.sh` and `check-prerequisites.sh`, and the files
`.specify/init-options.json`, `.specify/extensions.yml`, and `.gitignore`
(line 89).

## Corrections the person made

- USER 2 (line 54): "Your previous run did not satisfy the full-read
  requirement: your own limits say several generated commands were only
  searched and constitution-template.md was not opened."

## Conventions, commands and values stated and written down nowhere

- The verification status scale: "VERIFIED, PARTLY VERIFIED, UNSUPPORTED,
  INCORRECT, or INCONCLUSIVE" (USER 1, line 4). No repository file holds this
  scale. The verify-a-claim skill uses "verified" and "inconclusive". The
  review-a-change skill uses critical, high, medium, low.
- The re-check protocol: "Return only changed verdicts/corrections, an
  explicit full-coverage statement, and remaining limits" (USER 2, line 54).
  No repository file states that a follow-up verification reports only what
  changed.
- The Spec Kit file inventory: nine speckit commands, the constitution at
  `.specify/memory/constitution.md`, and five templates under
  `.specify/templates/`. The nine commands are named in `.kb/spec-kit.md`
  under Command set. The five template names are not listed as a set there.

## Failures, their cause, and the fix

No tool failure. The tool log has no `!! FAILED` line.

Process failure: the first run did not read the named files in full. Its own
limits (line 26) show it read only parts of speckit.implement, speckit.clarify,
speckit.constitution, and speckit.checklist, searched the rest, never opened
constitution-template.md, and never read .kb/agents.md, .kb/writing-style.md,
or .kb/requirements-format.md. The cause was the agent reading selected line
ranges and grepping instead of reading whole files. The fix was the person's
correction at line 54, and the second run then read every named file whole
(line 79).

## Candidate lessons

- NEW. A "read in full" instruction is a coverage contract, not a search
  hint. Quote: "Now read in full every one of the nine
  .opencode/commands/speckit.*.md files" (USER 2, line 54).
- NEW. A listed limit does not satisfy a full-read brief. The first run
  reported what it did not read and was still rejected. Quote: "your own
  limits say several generated commands were only searched and
  constitution-template.md was not opened" (USER 2, line 54).
- NEW. Verification reports use the five value status scale. Quote: "status
  VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, or INCONCLUSIVE"
  (USER 1, line 4).
- NEW. A re-check reports only changed verdicts and corrections. Quote:
  "Return only changed verdicts/corrections, an explicit full-coverage
  statement, and remaining limits" (USER 2, line 54).
- ALREADY WRITTEN. State what you could not verify. The agent did this in
  both runs. Already in `.kb/writing-style.md` §6 and in
  `.opencode/skills/verify-a-claim/SKILL.md` under How to report.
- ALREADY WRITTEN. A verification is read-only. Quote: "Do not edit generated
  files, mutate git, run workshops, or use network." (USER 1, line 4).
  Already in `.opencode/skills/review-a-change/SKILL.md` under Read-only.
- PROJECT-SPECIFIC FACT. The Spec Kit tooling is nine commands, one
  constitution, and five templates. The command set is already in
  `.kb/spec-kit.md` under Command set.

## What should not become a skill

- The specific generated file findings, such as "Follow TDD approach" against
  "Tests are OPTIONAL" (line 15), or "clean up obsolete checklists" against
  "Never delete or replace existing checklist content" (line 66). These are
  facts about the upstream generated commands. `.kb/spec-kit.md` §1 forbids
  hand edits and requires regeneration, so a skill stating these specifics
  would go stale on the next regeneration.
- The fact that `HookExecutor` appears 18 times, twice in each of the nine
  command files (line 66). This is a state of the generated tree, not a
  workflow rule.
- The fact that `.specify/memory/constitution.md` and `constitution-template.md`
  have identical content (line 85). This is a point of evidence for the report,
  not a rule.
