---
name: review-agent-instructions
description: Review a skill or an agent instruction against five criteria: context efficiency, reliability, description and triggers, scriptability, and ASD-STE100. Use when the person asks to review a skill, judge AGENTS.md, check agent instructions, or decide whether a rule should be a script.
---

# Review a skill or an agent instruction

A review has one verdict and five criteria. Read the whole artefact first. Test
every claim in it. Report findings before you suggest edits.

## Before you start

- Read every changed file whole. For a pull request, read the diff and each
  changed file.
- Read the rules the artefact must follow: the repository's `AGENTS.md`, its
  writing guide, and the `asd-ste100` skill when the repository has no guide.
- Find the linter, the test command and the skills the artefact references.
- Run the skill's `scripts/measure.py <path>` for the mechanical counts.

## The five criteria

### a) Context efficiency

OpenCode injects the description into every session. The body loads on every
trigger. Both cost the reader each time.

- Keep the whole description under 60 words, and each sentence under 25.
- Keep the body to what the reader needs on every trigger. Move long tables,
  worked examples and reference material into `references/`.
- A rule repeated from `AGENTS.md` or another skill costs context twice. Link
  to it instead.

Finding: quote the text, name the cost, and say what to cut or move.

### b) Reliability

A reader must be able to act on the text and get the stated result.

- Every factual claim names the version and the subcommand it was tested on.
- Every example was run. A false example is a major finding.
- A check script fails on a planted defect. A check that cannot fail proves
  nothing.
- The repository's tests pass.
- A rename updates the ID, the frontmatter name, the heading, every reference
  and the trigger phrases.

### c) Description and trigger conditions

The description is the only text OpenCode shows before it loads the skill.

- It says what the skill does.
- It names the situations and phrases that should reach for it.
- A generic word alone, such as "review", fires everywhere.
- The person's trigger phrases stay verbatim.

### d) Should this be a script?

A step with one right answer and no judgement belongs in a script.

- The script has an exit code and prints what failed.
- It joins the repository's test runner when one exists.
- The same check written as prose is a finding. Name the check and where the
  script should live.

### e) ASD-STE100

- Run the `asd-ste100` linter on every changed file, before and after.
- Report both counts. A new hard finding is a defect.
- Name each remaining hard finding and justify it. "The linter is noisy" is not
  a justification.
- A verbatim quote, a trigger phrase or a proper name may depart from a rule.
  Name the departure.

## Findings

Each finding has a severity, a location, the quoted text, the risk and the fix.

- **Major**: it would mislead a reader or fail the task.
- **Minor**: it costs context, is unclear, or departs from the style.
- **Advisory**: a possible improvement. It never blocks.

Do not invent a finding. A preference is not a defect. When a claim is not
tested, say "not verified" rather than calling it false.

## The verdict

- **Ready**: no major finding, and every minor finding is named.
- **Not ready**: at least one major finding.

The verdict must agree with the findings. "Ready" with an open major finding is
not a verdict.

## Report

1. the verdict.
2. each finding: severity, file and line, quote, risk, fix.
3. what you checked and what you did not.
4. the linter counts before and after, or why they are unavailable.
5. the counts from `scripts/measure.py`.

Do not edit the artefact unless the person asks for the fix. When you do edit,
change only what a finding names.
