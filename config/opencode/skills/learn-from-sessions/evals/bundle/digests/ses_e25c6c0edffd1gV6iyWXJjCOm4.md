# ses_e25c6c0edffd1gV6iyWXJjCOm4: Review generated Spec Kit prose

## What the person asked for

USER 1 (line 4): "Read-only readability review of group GENERATED SPEC KIT DOCUMENTATION".

USER 1 (line 4): "Review ALL 15 files: .opencode/commands/speckit.{analyze,checklist,clarify,constitution,converge,implement,plan,specify,tasks}.md; .specify/memory/constitution.md; .specify/templates/{checklist-template,constitution-template,plan-template,spec-template,tasks-template}.md".

USER 1 (line 4): ".kb/spec-kit.md says these are generated, so distinguish upstream generator wording from locally actionable integration guidance; do not propose hand edits to generated files".

USER 1 (line 4): "Return list of every file examined, up to 12 specific findings path:line, quote, reader impact and where a change belongs (upstream or local guidance), plus small editorials separately. Do not edit files."

USER 2 (line 57): "Your report explicitly says coverage incomplete. Continue the SAME generated Spec Kit group. Read in FULL every file previously only searched or partially read".

USER 2 (line 57): "In particular inspect skipped lines 1-54 and all templates. Report new actionable findings with exact path:line and suggestion, corrections to previous findings, and explicit coverage status complete/incomplete."

## What was produced, and whether it worked

The review is read-only. No file changed. The tool log shows read, grep and skill calls only (lines 87-112). The skill call loaded `asd-ste100` (line 89).

The first reply returned 8 substantive findings (RDB-1 through RDB-8) and 5 readability suggestions (RDS-1 through RDS-5). It declared coverage incomplete in its own words (line 6): "Coverage is **incomplete** because I did not read 6 of the files line by line (listed below)."

The second reply returned 6 more findings (RDB-9 through RDB-14), 4 more suggestions (RDS-6 through RDS-9), and 3 corrections. It declared coverage complete (line 59): "Coverage for the Spec Kit group is now **complete**: all 15 files are read in full."

The substantive findings, with the location each one says its fix belongs:

- RDB-1 `speckit.analyze.md:56`, medium, local guidance. The constitution is called non-negotiable while `.kb/spec-kit.md` says it is the unfilled template.
- RDB-2 `speckit.specify.md:115`, medium, local guidance. The "IF EXISTS" constitution load is always true here.
- RDB-3 `speckit.specify.md:89`, medium, local guidance. Numbering from `specs/` conflicts with `.kb/spec-kit.md` §4.
- RDB-4 `speckit.implement.md:145`, medium, local guidance. Implement runs every task, and the local per-group guidance names no invocation method.
- RDB-5 `speckit.converge.md:61`, medium, local guidance. The converge precondition is unclear for a stacked feature.
- RDB-6 `speckit.implement.md:154`, medium, upstream plus local. The test instructions conflict.
- RDB-7 `speckit.implement.md:113`, low, upstream plus local. The ignore-file step has undefined scope.
- RDB-8 `.specify/templates/plan-template.md:5`, low, upstream. The `specs` path is written with a leading slash.
- RDB-9 `speckit.clarify.md:213`, medium, upstream. A step reference says "step 7" where the spec is saved in steps 6 and 8.
- RDB-10 `.specify/templates/tasks-template.md:249`, medium, upstream plus local. The test-first note lacks an "if tests are included" condition.
- RDB-11 `.specify/templates/tasks-template.md:250`, medium, local guidance. The commit advice ignores stacked pull requests.
- RDB-12 `speckit.checklist.md:318`, low, upstream. Two numbering formats for checklist items.
- RDB-13 `speckit.constitution.md:6`, low, upstream. A handoff prompt asks the wrong command to implement.
- RDB-14 `.specify/templates/spec-template.md:15`, low, upstream plus local note. "Deployed independently" conflicts with the local layer model.

The readability suggestions, all marked upstream:

- RDS-1 `speckit.specify.md:30` `HookExecutor` is not defined.
- RDS-2 `speckit.specify.md:312` the data retention default does not say what to do.
- RDS-3 `speckit.constitution.md:104` two instructions joined into one clause.
- RDS-4 `speckit.constitution.md:90` "less or more principles".
- RDS-5 `speckit.implement.md:165` a phrasal verb in a required step.
- RDS-6 `speckit.analyze.md:54` one sentence mixes several conditions.
- RDS-7 `speckit.clarify.md:56` "spike" has its own meaning in this repository.
- RDS-8 `speckit.checklist.md:268` the cleanup note does not say who removes the checklist.
- RDS-9 `.specify/templates/tasks-template.md:1` a blank line in the front matter.

Verified: the agent read all 15 files in full by the second reply, which the read calls in the tool log back (lines 103-111).

Not verified: each finding's line reference against the actual generated files. This digest does not re-run the review.

## Corrections the person made

One correction. The agent ended its first reply with an admission of incomplete coverage (line 6): "Coverage is **incomplete** because I did not read 6 of the files line by line (listed below)." The person answered (USER 2, line 57): "Your report explicitly says coverage incomplete. Continue the SAME generated Spec Kit group. Read in FULL every file previously only searched or partially read".

The agent then corrected three of its own findings (lines 72-74). RDB-2 gained that `speckit.analyze.md:100` loads the constitution with no "IF EXISTS" condition. RDB-6 gained `tasks-template.md:85` and `tasks-template.md:182` as further conflict sites. The coverage limitations were withdrawn.

## Conventions, commands and values stated and written down nowhere

The review emits two JSON blocks, and their field shapes are stated only in the global command `~/.config/opencode/command/review-council.md`, which the agent read first (line 88). They are not in this repository.

A substantive finding object (line 39) has these fields: `id`, `file`, `line`, `category`, `severity`, `confidence`, `title`, `rationale`, `suggested_fix`, `out_of_scope`. In this review `category` is "readability", `severity` is "medium" or "low", `confidence` is "high" or "medium", and `out_of_scope` is false. The `id` prefix is RDB-.

A readability suggestion object (line 54) has these fields: `id`, `line`, `original`, `problem`, `suggested_edit`, grouped under a `file` key. The `id` prefix is RDS-.

The `suggested_fix` and `suggested_edit` fields carry the split the brief asked for. They open with "Upstream:" or "Local:" or "Local guidance, same edit as RDB-1".

The repository's own `.opencode/skills/review-a-change/SKILL.md` describes a different, simpler finding shape (severity, `file:line`, the fault, why it matters, the triggering scenario, the smallest correct fix). The readability review's JSON shape is richer and does not match it.

## Failures, their cause, and the fix

(none found)

The tool log holds no `!! FAILED` entry. Every read, grep and skill call returned `ok` (lines 87-112).

## Candidate lessons

- The generated Spec Kit prose contradicts the repository's local Spec Kit rules in several named places, and the remedy for each is already recorded. From RDB-3 (line 20): "prefix is `NNN` (next available 3-digit number after scanning existing directories in `specs/`)". ALREADY WRITTEN in `.kb/spec-kit.md` §4, §5, and "Local rules for a stacked run", which also holds the test rule and the `.gitignore` scope rule.
- A review of generated files reports where each fix belongs, upstream in the generator or local guidance in this repository, and proposes no hand edit to a generated file. From USER 1 (line 4): "distinguish upstream generator wording from locally actionable integration guidance; do not propose hand edits to generated files". NEW. `.kb/spec-kit.md` §1 covers the no-hand-edit half only.
- A readability review emits the two JSON blocks named above, with fixed fields that differ from the finding shape in `.opencode/skills/review-a-change/SKILL.md`. From ASSISTANT 1 (line 39): `{"id":"RDB-1","file":"...","line":56,...,"out_of_scope":false}`. PROJECT-SPECIFIC FACT. The contract lives in the global review-council command, outside this repository.

## What should not become a skill

The upstream wording defects (RDB-6, RDB-7, RDB-8, RDB-9, RDB-10, RDB-12, RDB-13, RDB-14, and RDS-1 through RDS-9) are not lessons for this repository. The files under `.specify/` and `.opencode/commands/` are generated, and `.kb/spec-kit.md` §1 says to change them by re-running Spec Kit, not by hand. This repository cannot act on the upstream prose, so those findings belong to Spec Kit upstream.

The specific local-guidance recommendations (RDB-1 through RDB-5, and RDB-11) are not new lessons either. They restate what `.kb/spec-kit.md` already records, as the candidate lessons note.
