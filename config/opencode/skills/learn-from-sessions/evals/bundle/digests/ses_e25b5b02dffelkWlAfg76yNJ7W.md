# ses_e25b5b02dffelkWlAfg76yNJ7W: Verify local skill findings

## What the person asked for

USER 1 (line 4):

- "Read-only verification of an existing documentation readability review."
- "Read .kb/agents.md and .kb/writing-style.md first."
- "Verify ALL 'Local agent skills' findings and the Minor editorial items 'Remove undefined agent shorthand' and 'Reduce repeated skill warnings where the local context permits'."
- "Read all eight .opencode/skills/*/SKILL.md files in full."
- "Return a compact item-by-item table with status VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, or INCONCLUSIVE; exact source line evidence; and any needed correction."
- "End by naming anything you could not check."
- "Do not edit files, mutate git, or use network."

## What was produced, and whether it worked

One verification table of twelve rows. The rows cover the seven report bullets under "Local agent skills" and the two Minor editorial items. Bullet 5 has two rows (5a, 5b) and bullet 6 has three rows (6a, 6b, 6c).

Statuses:

- Eight rows VERIFIED: rows 2, 4, 5a, 5b, 6a, 6b, 6c, and 7.
- Four rows PARTLY VERIFIED: rows 1, 3, M1, and M2.
- No row UNSUPPORTED, INCORRECT, or INCONCLUSIVE.

Seven rows carry a correction in their "Needed correction" cell: rows 1, 3, 5b, 6b, 6c, M1, and M2.

The opening summary does not match the table. The summary says "Five bullets are fully verified. Five are partly verified." and "four need a correction" (line 6). The table shows eight VERIFIED rows and four PARTLY VERIFIED rows, and seven rows carry a correction.

The verification also produced:

- A cross-skill agreement list of three points (lines 26-28).
- A "What I could not check" list of four points (lines 33-36).
- Empty `review-json` and `review-readability-json` blocks (lines 41-49).

How the verification ran:

- It read the report section with `read` at offset 270, limit 180 (line 56).
- It read `.kb/writing-style.md` (line 57).
- It read all eight `.opencode/skills/*/SKILL.md` files (lines 59-66): `fence-verification`, `resolve-a-decision-ticket`, `merge-a-pull-request-stack`, `review-a-change`, `run-a-workshop-in-a-vm`, `retire-a-name`, `workshop-host-authority`, and `verify-a-claim`.
- No tool call failed.

What it did not verify:

- It did not run `git archive`. It stated that `git archive` writes to standard output from general git knowledge, not from a run (line 33).
- It did not read the global `wayfinder` skill, so it could not say whether that skill defines "HITL" or "map" (line 34).
- It did not measure whether VM disk resizing needs a stopped instance (line 35).
- It did not check the other sections of the report (line 36).
- The tool log shows no read of `.kb/agents.md`, although the person asked to read it and `.kb/writing-style.md` first (line 4).

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

USER 1 (line 4) stated these exact strings:

- The status vocabulary: "VERIFIED", "PARTLY VERIFIED", "UNSUPPORTED", "INCORRECT", "INCONCLUSIVE".
- The report path: "docs/documentation-readability-review.md".
- The worktree HEAD: "9003ccd6937060f2bb697ac69a871070e326b665".
- The two Minor editorial items by name: "Remove undefined agent shorthand" and "Reduce repeated skill warnings where the local context permits".

USER 1 (line 4) also stated two constraints for a verification child: "Do not execute destructive commands or workshops" and "Do not edit files, mutate git, or use network".

## Failures, their cause, and the fix

(none found)

## Candidate lessons

- NEW. Decide whether a proposed fix is a clarification the source supports or a new rule the owner must decide, and label it accordingly. From "Adding a 'required approval' step is a new rule the owner must decide, not a clarification." ASSISTANT, table row 1 (line 12).
- NEW. When the source already answers a claim, recast a two-reading finding as a wording suggestion. From "Recast this as a wording suggestion, not a defect with two readings." ASSISTANT, table row 3 (line 14).
- NEW. When a citation misses lines that also carry the term, name the missing lines in the correction. From "Add lines 23, 26, and 112 to the citation." ASSISTANT, table row 6b (line 19).
- NEW. When the source text cannot settle a fact, mark the fact for the owner to confirm instead of guessing the answer. From "The owner must confirm the correct order." ASSISTANT, table row 5a (line 16).
- ALREADY WRITTEN. State what was not verified as plainly as what was. From "I did not run git archive. Its standard-output behavior comes from general git knowledge, not from a run." ASSISTANT (line 33). This restates `.kb/writing-style.md` §6 (line 51).

## What should not become a skill

- The summary-count mismatch (line 6 against the table) is a one-off wording error in this session, not a rule. A rule that says "make the summary match the table" adds nothing beyond the review discipline already in the repository.
- The specific report findings are project-specific facts. The VM disk order, the registry IDs, "HITL", "map line", and "the need" belong in the report and its corrections, not in a skill.
