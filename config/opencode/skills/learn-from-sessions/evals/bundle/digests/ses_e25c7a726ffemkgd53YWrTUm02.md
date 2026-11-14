# ses_e25c7a726ffemkgd53YWrTUm02: Review all documentation in this repo and break the documentation work into parts

## What the person asked for

One goal message, in full:

- "review all documentation in this repo" — USER 1 (line 8)
- "Break the documentation up into logical groupings, then use the @review-readability agent on each grouping to review that group. Deduplicate and capture the output as a review markdown file in this repo." — USER 1 (line 9)

The person added nothing else after the goal. There were no follow-up turns.

## What was produced, and whether it worked

The agent inventoried the documentation and counted 63 tracked files. From its
reply:

- "The tracked documentation includes 60 Markdown files and a topology diagram with source and rendered copies." — ASSISTANT (line 20)
- "I'm splitting the review by document purpose: project guidance, workshop guidance, decisions and requirements, research, local agent skills, and generated Spec Kit material." — ASSISTANT (line 20)

It split the work into seven groups and spawned one `review-readability` child
per group. This session is the parent. The seven children and what each was
told:

- `ses_e25c6c126ffeouNkivBC3BEYRs` — "Review project guidance prose" (line 59).
  Group PROJECT GUIDANCE. Files AGENTS.md, GLOSSARY.md, and `.kb/agents.md`,
  `.kb/domain-docs.md`, `.kb/issue-tracker.md`, `.kb/project.md`,
  `.kb/requirements-format.md`, `.kb/spec-kit.md`, `.kb/spikes.md`,
  `.kb/topologies.md`, `.kb/writing-style.md`. Told to focus on "wording, reader
  navigation, ambiguous referents, order, duplication, and clarity" (from the
  full prompt in the tool log).
- `ses_e25c6c124ffdqvGaDCrRvS01oQ` — "Review workshop operations guidance"
  (line 60). Group WORKSHOP GUIDANCE AND DIAGRAM. Files `.kb/agent-workshop.md`,
  `.kb/development-workshop-authority.md`, `.kb/development-workshop.md`,
  `.kb/fence.md`, `.kb/privileged-conformance-suite.md`, the Mermaid source
  `development-workshop-authority.mmd`, and its rendered `.html` and `.svg`.
  Told to concentrate on "human-facing labels/alt text/accessibility" for the
  rendered diagram and to report duplicate content once at the Mermaid source.
- `ses_e25c6c117ffe7mnda6RHciu71b` — "Review ADR and requirements" (line 61).
  Group DECISIONS AND REQUIREMENTS. Files `adr/*.md` (README and nine records:
  0001, 0002, 0004, 0005, 0006, 0007, 0008, 0009, 0010) and
  `requirements/002-proxy-egress-fence/requirements.md`. Told that ADRs and
  requirements target ASD-STE100, so flag unclear phrasing without altering
  accepted decisions.
- `ses_e25c6c102ffeX0MkYMMBlmCkWF` — "Review network research reports" (line
  62). Group NETWORK/PROXY RESEARCH. Files `research/acl-fence.md`,
  `research/iron-proxy-plane.md`, `research/separate-bridges.md`,
  `research/two-bridge-gateway.md`, `research/two-workshop.md`. Told to
  preserve historical observations and avoid guessing current status.
- `ses_e25c6c102ffdtWizZvtaE1ktrz` — "Review development research reports"
  (line 63). Group DEVELOPMENT WORKSHOP RESEARCH. Files
  `research/development-workshop.md`, `research/development-workshop-channel.md`,
  `research/development-workshop-ctlcmd.md`,
  `research/development-workshop-lxd-scope.md`,
  `research/development-workshop-nested-lxd.md`. Told not to change facts or
  edit files.
- `ses_e25c6c0edffe3EZ3NX7jojPmzT` — "Review local agent skills" (line 64).
  Group LOCAL AGENT INSTRUCTIONS. Files `.opencode/skills/*/SKILL.md`, eight
  tracked skills: fence-verification, merge-a-pull-request-stack,
  resolve-a-decision-ticket, retire-a-name, review-a-change,
  run-a-workshop-in-a-vm, verify-a-claim, workshop-host-authority. Told to
  assess readability to a nonhuman agent: clear conditions and actions, order,
  concrete outputs, no ambiguous references.
- `ses_e25c6c0edffd1gV6iyWXJjCOm4` — "Review generated Spec Kit prose" (line
  65). Group GENERATED SPEC KIT DOCUMENTATION. Fifteen files:
  `.opencode/commands/speckit.{analyze,checklist,clarify,constitution,converge,implement,plan,specify,tasks}.md`,
  `.specify/memory/constitution.md`, and
  `.specify/templates/{checklist-template,constitution-template,plan-template,spec-template,tasks-template}.md`.
  Told these are generated, so distinguish upstream generator wording from
  locally actionable guidance and do not propose hand edits.

Every child was told the same return contract: report every file examined, up
to twelve actionable findings with exact `path:line`, quoted phrase, reader
cost, and concrete revision, then separate minor editorial suggestions, then
cross-file duplication. Every child was told to read only and not edit files.
This contract is clipped from the flattened file but visible in the tool log.

One child reported incomplete coverage. The parent sent it back:

- "One agent flagged that it had searched, rather than fully read, several generated Spec Kit files. I've asked that same agent to finish those files before I claim complete coverage." — ASSISTANT (line 22)

The follow-up went to the Spec Kit child `ses_e25c6c0edffd1gV6iyWXJjCOm4`
(line 71). Its prompt: "Read in FULL every file previously only searched or
partially read: .opencode/commands/speckit.analyze.md, speckit.checklist.md,
speckit.clarify.md, speckit.tasks.md, speckit.constitution.md;
.specify/templates/checklist-template.md, constitution-template.md,
spec-template.md, tasks-template.md." (line 71)

The parent then wrote the combined review file and reported:

- "Created docs/documentation-readability-review.md with deduplicated findings and editorial suggestions from seven review-readability group reviews." — ASSISTANT (line 24)
- "covered: 63 tracked files (60 Markdown, 3 diagram files)" — ASSISTANT (line 29)
- "missing: []  duplicates: []" — ASSISTANT (line 30)
- "negative control: removing one research file reported one missing file" — ASSISTANT (line 31)
- "just style docs/documentation-readability-review.md" then "0 finding(s) in 1 file(s)" — ASSISTANT (lines 32-33)

Verified in the tool log: `just style docs/documentation-readability-review.md`
ran twice and returned no findings. The coverage check compared the group
inventory against `git ls-files`. Not verified: the individual findings inside
the review file, which came from the children's reports rather than this
session's own reading of every document. No commits were made. The one file
added and edited was `docs/documentation-readability-review.md`.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

(none found)

## Failures, their cause, and the fix

- `patch` failed on `docs/documentation-readability-review.md` (line 88):
  "patch verification failed: Failed to find expected lines". The error named
  text that was not in the file. The cause was a stale hunk: the patch was
  prepared against an earlier state of the file, which the preceding successful
  patches (line 87 and earlier) had already changed. The fix: the agent re-read
  the file (line 90), then re-applied the patch with corrected context
  (line 91), which succeeded.

## Candidate lessons

- NEW — A whole-documentation review is split into logical groups by purpose
  and one `review-readability` agent runs per group, in parallel. From "Break
  the documentation up into logical groupings, then use the @review-readability
  agent on each grouping to review that group." — USER 1 (line 9). The seven
  groups: "project guidance, workshop guidance, decisions and requirements,
  research, local agent skills, and generated Spec Kit material" — ASSISTANT
  (line 20).
- NEW — A readability reviewer that reports it searched rather than read some
  files must be sent back, to the same child by its session id, to read them in
  full before coverage is claimed. From "One agent flagged that it had
  searched, rather than fully read, several generated Spec Kit files. I've
  asked that same agent to finish those files before I claim complete
  coverage." — ASSISTANT (line 22).
- NEW — A fan-out review proves coverage by diffing the group inventory against
  `git ls-files` and reports the count, missing, and duplicate files. From
  "covered: 63 tracked files (60 Markdown, 3 diagram files)" and
  "missing: []  duplicates: []" — ASSISTANT (lines 29-30).
- ALREADY WRITTEN — A coverage check needs a negative control that drops one
  file and expects one missing. `verify-a-claim` skill, "A negative result
  needs a positive control taken the same way." Shown here as "removing one
  research file reported one missing file" — ASSISTANT (line 31).
- ALREADY WRITTEN — Prove the style check can fail with a known-bad input
  before trusting its pass. `verify-a-claim` skill, "Feed it a known-bad
  input." Shown here when the agent planted an em dash and ran `just style`
  against it (lines 97-98).
- ALREADY WRITTEN — Run `just style <file>` on a changed Markdown file.
  `AGENTS.md` Working rules, "Run `just style <file>` on every changed Markdown
  file before a commit." Shown here on the review file (lines 32, 80, 92).

## What should not become a skill

- The seven group names and their file lists. They are this repository's
  documentation inventory on this date and change as files are added or moved.
- The individual findings and editorial suggestions. They belong in
  `docs/documentation-readability-review.md`, the review output, not in a skill.
- A coverage-check script as its own skill. Diffing a file list against
  `git ls-files` is one instance of the rule already in `verify-a-claim` that
  compares a value against the source that names it.
