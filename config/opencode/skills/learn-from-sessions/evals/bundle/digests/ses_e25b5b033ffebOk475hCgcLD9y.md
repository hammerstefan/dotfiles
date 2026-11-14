# ses_e25b5b033ffebOk475hCgcLD9y: Verify development research findings

## What the person asked for

Quotes from USER 1 (line 4):

- "Read-only verification of an existing documentation readability review." (line 4)
- "Verify the development-workshop research findings: bullets under 'Research records' that cite research/development-workshop*.md, plus the development-workshop part of Minor editorial 'Mark historical research relationships'." (line 4)
- "Read all five research/development-workshop*.md files in full." (line 4)
- "For each report bullet, independently decide whether each factual claim is supported, whether surrounding context resolves it, and whether the proposed clarification accurately describes it." (line 4)
- "Check exact line citations, run labels/memory values/timings, publication-location claims, ticket references, and headings/spellings." (line 4)
- "Return a compact item-by-item table with status VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, or INCONCLUSIVE; exact source line evidence; and any needed correction." (line 4)
- "End by naming anything you could not check." (line 4)
- "Do not edit files, run workshops, mutate git, or use network." (line 4)
- "Historical records must be judged as history, not current runtime instructions." (line 4)

The person also named the worktree and commit (line 4): "Work in /home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/review-writing at HEAD 9003ccd6937060f2bb697ac69a871070e326b665. The report is the untracked file docs/documentation-readability-review.md."

## What was produced, and whether it worked

No commits, branches, records, or pull requests. The task was read-only.

The agent returned an item-by-item verification table of six report bullets.
The agent's own summary (line 8): "I checked 6 items. 2 are VERIFIED and 4 are PARTLY VERIFIED. None are INCORRECT or UNSUPPORTED."

The six verdicts:

1. Nested-LXD record gives incompatible memory limits (report lines 247-251). VERIFIED (line 12).
2. Nested-LXD run numbers and times need fixed labels (252-258). VERIFIED (line 13).
3. Development research sends readers to old publication locations (259-264). PARTLY VERIFIED (line 14).
4. "Open decision" names different questions and tickets (265-271). PARTLY VERIFIED (line 15).
5. A verdict begins with an answer to a different question (272-276). PARTLY VERIFIED (line 16).
6. Minor editorial "Mark historical research relationships", development-workshop part (419-425). PARTLY VERIFIED (line 17).

The agent named what it could not check (lines 19-21):
- "The contents and relationship of issues #44, #45, #47, #48 and #51, and whether the branches named in the records exist on the remote. I had no network access." (line 20)
- "Upstream source citations, such as the `canonical/workshop` and LXD files. These are outside the review and I did not check them." (line 21)

The output channels were empty. The `review-json` block held `[]` (line 24), and the readability block held no suggestions with complete coverage (lines 31-35). The agent wrote "None. This was a verification task, so I wrote no new suggestions about the source files." (line 29).

The verification was not checked against the report by any second pass. The digest does not confirm whether the six verdicts are correct.

## Corrections the person made

(none found)

The person spoke once, in the spawning brief, and never corrected the agent's behavior.

## Conventions, commands and values stated and written down nowhere

These values come from USER 1 (line 4). None appear in AGENTS.md, GLOSSARY.md, the `.kb/` files, the research records, or the skills of the main checkout.

- The five-value verification status scale: "VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, or INCONCLUSIVE". The verify-a-claim skill names only verified and inconclusive. It has no five-value scale.
- "Historical records must be judged as history, not current runtime instructions." No file states this rule.
- The three-question per-bullet method: "independently decide whether each factual claim is supported, whether surrounding context resolves it, and whether the proposed clarification accurately describes it."
- The verification checklist: "Check exact line citations, run labels/memory values/timings, publication-location claims, ticket references, and headings/spellings."

## Failures, their cause, and the fix

(none found)

Every tool call in the log returned `ok`. There are no `!! FAILED` lines.

## Candidate lessons

- NEW. A verification of a readability report uses a five-value status scale: VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, INCONCLUSIVE. Quote: "status VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, or INCONCLUSIVE" (USER 1, line 4). Not in the repository.
- NEW. Historical records are judged as history, not as current runtime instructions. Quote: "Historical records must be judged as history, not current runtime instructions." (USER 1, line 4). Not in the repository.
- NEW. A verification of one report bullet answers three questions for each factual claim: supported, resolved by surrounding context, and accurately described by the proposed clarification. Quote: "independently decide whether each factual claim is supported, whether surrounding context resolves it, and whether the proposed clarification accurately describes it" (USER 1, line 4). Not in the repository.
- NEW. A verification checks exact line citations, run labels, memory values, timings, publication-location claims, ticket references, and headings and spellings. Quote: "Check exact line citations, run labels/memory values/timings, publication-location claims, ticket references, and headings/spellings." (USER 1, line 4). Not in the repository.
- ALREADY WRITTEN. Name what you could not check. Quote: "End by naming anything you could not check." (USER 1, line 4). The review-a-change skill's Output section has "Not verified. State the reach you lacked." The verify-a-claim skill has "State what was not verified as plainly as what was."
- ALREADY WRITTEN. A verification child is read-only. Quote: "Do not edit files, run workshops, mutate git, or use network." (USER 1, line 4). The review-a-change skill's Read-only section forbids changing files, committing, pushing, and running LXD or Workshop state. It does not name the no-network part.
- PROJECT-SPECIFIC FACT. The five research files are `research/development-workshop.md`, `-nested-lxd.md`, `-ctlcmd.md`, `-lxd-scope.md`, and `-channel.md`. Quote: "Read all five research/development-workshop*.md files in full." (USER 1, line 4).

## What should not become a skill

- The six item-by-item verdicts and their corrections (lines 12-17). They are one-off facts tied to specific report lines and research file lines. They are output, not a method.
- The transient worktree path and HEAD commit "9003ccd6937060f2bb697ac69a871070e326b665" (line 4). They change with each run.
- The report path "docs/documentation-readability-review.md" (line 4). It is a project artifact, not a rule.
- The finding that the glossary has no term that tells "channel", "route", and "transport" apart (line 17). It is a specific gap in the report, not a reusable lesson.
