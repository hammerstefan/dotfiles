# ses_e25c6c0edffe3EZ3NX7jojPmzT: Review local agent skills

## What the person asked for

USER 1 (line 2):

- "Read-only readability review of group LOCAL AGENT INSTRUCTIONS in repo
  /home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/review-writing." (line 4)
- "Review EVERY .opencode/skills/*/SKILL.md (8 tracked skills:
  fence-verification, merge-a-pull-request-stack, resolve-a-decision-ticket,
  retire-a-name, review-a-change, run-a-workshop-in-a-vm, verify-a-claim,
  workshop-host-authority)." (line 4)
- "Use .kb/writing-style.md as project style." (line 4)
- "Assess readability to a nonhuman agent: clear conditions/actions, order,
  concrete outputs, no ambiguous references, avoid accidental change in
  behavior." (line 4)
- "Return every file examined; up to 12 actionable findings path:line, quote,
  reader effect and concrete improvement, plus minor editorials and cross-file
  duplicates. No edits." (line 4)

## What was produced, and whether it worked

The agent read the 8 skill files, `.kb/writing-style.md`, and `AGENTS.md`.
It made no edits. No commit, branch, pull request, or record was produced.

It returned 12 substantive findings, RDB-1 through RDB-12. Each finding has
this shape: id, a severity and confidence pair, file and line, a quote, an
effect on the reader, and a fix. The severity and confidence pairs are
medium/high (RDB-1, 2, 4), medium/medium (RDB-3, 5), low/high (RDB-6, 11), and
low/medium (RDB-7, 8, 9, 10, 12).

The 12 findings:

- RDB-1, `.opencode/skills/resolve-a-decision-ticket/SKILL.md:68`: the absence
  signal for "the person is not there" is never stated (line 25).
- RDB-2, `.opencode/skills/fence-verification/SKILL.md:26`: the rebuild
  condition sits 8 lines after the command it gates (line 30).
- RDB-3, `.opencode/skills/merge-a-pull-request-stack/SKILL.md:47`: "The
  person merges, or says so" has two readings (line 35).
- RDB-4, `.opencode/skills/review-a-change/SKILL.md:103`: no severity scale and
  no blocking mapping (line 44).
- RDB-5, `.opencode/skills/run-a-workshop-in-a-vm/SKILL.md:65`: the disk resize
  order is unclear (line 49).
- RDB-6, `.opencode/skills/run-a-workshop-in-a-vm/SKILL.md:111`: "before and
  after" has no earlier record step (line 54).
- RDB-7, `.opencode/skills/retire-a-name/SKILL.md:63`: "the pull request" can
  mean three things (line 59).
- RDB-8, `.opencode/skills/resolve-a-decision-ticket/SKILL.md:86`: "map" and
  "map line" are not defined (line 69).
- RDB-9, `.opencode/skills/fence-verification/SKILL.md:29`: no rule chooses
  `just fence` or `just fence-acceptance` (line 74).
- RDB-10, `.opencode/skills/merge-a-pull-request-stack/SKILL.md:56`: the clean
  extraction omits where to extract and where to run `just test` (line 79).
- RDB-11, `.opencode/skills/resolve-a-decision-ticket/SKILL.md:14`: "HITL" is
  not defined (line 84).
- RDB-12, `.opencode/skills/workshop-host-authority/SKILL.md:38`: "the need" is
  used as a term but never defined (line 89).

It also returned 14 readability suggestions, RDS-1 through RDS-14. Each has
this shape: id, file, line, original, problem, and suggested edit. RDS-1
through RDS-13 are fully in the flattened file (lines 95 through 158). RDS-14
starts at line 160 and its body is clipped at line 161. The clipped text, the
note about repeated rules, and two JSON blocks are recovered from the raw
export.

The raw export also holds two machine-readable blocks. One is `review-json`,
with 12 objects that each have id, file, line, category, severity, confidence,
title, rationale, suggested_fix, and out_of_scope. The other is
`review-readability-json`, with a `readability_suggestions` array and a
`readability_coverage` object. The coverage object reports status "complete"
and an empty limitations list.

Nothing was verified by a run. This is a static reading. The line numbers and
file contents in the findings are the agent's claims. They were not checked
against the skill files in this session.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

- The review group name "LOCAL AGENT INSTRUCTIONS" (line 4). It is not in the
  monitor-agent repository. It belongs to the review-council orchestration in
  the global config.
- The review output contract, "up to 12 actionable findings path:line, quote,
  reader effect and concrete improvement, plus minor editorials and cross-file
  duplicates" (line 4). This contract is in the global review-council command
  and readability criteria, not in the repository.
- The eight skill names and `.kb/writing-style.md` are already written in
  `AGENTS.md` and `.kb/`, so they are not listed again here.

## Failures, their cause, and the fix

(none found)

## Candidate lessons

1. NEW. "Write the condition that gates a command before the command." It comes
   from RDB-2, "so run this only on a host whose workshops you can rebuild"
   (line 30), with the fix "Move this sentence above the code block at line 17."
   (line 32). `.kb/writing-style.md` does not state this ordering rule.
2. ALREADY WRITTEN. "Define a term before you use it, and name the object an
   instruction acts on." It comes from RDB-11, "a HITL ticket only resolves
   through the live exchange" (line 84), and RDB-7, "State which one it is in
   the pull request." (line 59). It is already written in `.kb/writing-style.md`
   as "Say what an internal name does before relying on it." and "Name who
   acts".
3. PROJECT-SPECIFIC FACT. "review-a-change has no severity scale and no mapping
   from severity to a merge verdict." It comes from RDB-4, "\"Ready to merge\",
   only when every finding is non-blocking." (line 44). It belongs in the
   review-a-change skill, not in a shared skill.
4. PROJECT-SPECIFIC FACT. "run-a-workshop-in-a-vm orders the disk resize after
   the memory steps and never records registry ids before launch." It comes
   from RDB-5 (line 49) and RDB-6 (line 54). It belongs in the
   run-a-workshop-in-a-vm skill.
5. NEW. "Assess a skill as an agent that loads one skill with no other
   context." The agent states it as "The reader I assumed is an agent that
   loads one skill and has no other context." (line 20). It is an agent method,
   not a repository rule.

## What should not become a skill

- The 12 RDB findings and the 14 RDS suggestions are edits to specific skill
  files. They are not a new skill.
- The three warnings the agent left alone must stay repeated at the point of
  risk. The agent wrote "Some rules are repeated on purpose, and I did not ask
  to remove them." The three are `user.workshop.projects`, the host LXD socket,
  and the denial of the host client. This text is clipped at line 161 and
  recovered from the raw export. Do not make a "deduplicate shared warnings"
  skill from it.
- The cross-file duplicates RDS-10 and RDS-11 are flagged, but the suggested
  fix keeps the warning at the point of risk. Do not single-source them.
- The readability review method is the review-council command in the global
  config. It is not a repository skill.
