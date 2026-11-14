# ses_e25b5b042ffeRmoOY0J4rVuPqK: Verify workshop guidance findings

## What the person asked for

One USER turn, the assignment brief. Its words, in order.

USER 1 (line 3): "You are a subagent spawned by another session."

USER 1 (line 4): "Read-only verification of an existing documentation readability review."

USER 1 (line 4): "Work in /home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/review-writing at HEAD 9003ccd6937060f2bb697ac69a871070e326b665."

USER 1 (line 4): "The report is the untracked file docs/documentation-readability-review.md."

USER 1 (line 4): "Read .kb/agents.md and .kb/writing-style.md first."

USER 1 (line 4): "Verify ONLY the 'Workshop guidance and diagram' findings and, under Minor editorial suggestions, the 'Make workshop labels and first uses explicit' item."

USER 1 (line 4): "Read every cited source file in full, including the .mmd source and relevant whole HTML/SVG where needed. Also read ADR 0010 and GLOSSARY entries when the finding cites them."

USER 1 (line 4): "For each report bullet, independently decide whether each factual claim is supported and whether the proposed readability problem is real."

USER 1 (line 4): "Check exact line citations, rendered SVG title/desc claims, button accessible-name claims, and verb consistency. Do not run renderers."

USER 1 (line 4): "Return a compact item-by-item table with status VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, or INCONCLUSIVE; exact source line evidence; and any needed correction."

USER 1 (line 4): "End by naming anything you could not check."

USER 1 (line 4): "Do not edit files, run workshops, mutate git, or use network."

USER 1 (line 4): "This is verification of the cited claims, not a fresh usability review."

## What was produced, and whether it worked

The agent returned one table of nine rows plus a list of what it could not check (lines 6 to 24). It did not change any file.

The agent reported its tally at line 6: "I checked 9 report bullets against the source files. 5 are fully verified, 4 are partly verified, and none is unsupported or incorrect."

The nine rows hold one report item each. Five carry the status VERIFIED. Four carry the status PARTLY VERIFIED. No row carries UNSUPPORTED, INCORRECT, or INCONCLUSIVE.

The rows name a source line and a needed correction for each item. For example, row 1 (line 10) cites `.kb/development-workshop-authority.md:29` for "Six verbs run on the host" and `adr/0010…:19` as the place that lists the verbs.

The agent also emitted two empty harness blocks. The `review-json` block (lines 26 to 28) holds `[]`. The `review-readability-json` block (lines 30 to 35) holds empty `readability_suggestions` and a complete coverage status. These report that the verification produced no inline review comments.

Nothing here was verified against a rendered page. The agent said so at line 22.

## Corrections the person made

(none found)

There is one USER turn, the assignment. No later USER turn corrects the agent.

## Conventions, commands and values stated and written down nowhere

- A five-value status set for verification of a documentation review. USER 1 (line 4): "status VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, or INCONCLUSIVE". `.opencode/skills/verify-a-claim/SKILL.md` writes "verified" and "inconclusive" but not this five-value set. `.opencode/skills/review-a-change/SKILL.md` uses a severity scale, not these words.
- A documentation review verification must not run a renderer. USER 1 (line 4): "Do not run renderers." This is not in the two review skills.
- Naming the HEAD pins the tree under review. USER 1 (line 4): "at HEAD 9003ccd6937060f2bb697ac69a871070e326b665". The rule to name the exact commit already appears in `.opencode/skills/review-a-change/SKILL.md`.

## Failures, their cause, and the fix

(none found)

The tool log holds only `ok` entries and no `!! FAILED` lines.

## Candidate lessons

- NEW. Verification of a documentation review reads every cited source in full and checks five kinds of claim: factual support, exact line citations, rendered SVG title and desc claims, button accessible-name claims, and verb consistency. From USER 1 (line 4): "Read every cited source file in full, including the .mmd source and relevant whole HTML/SVG where needed" and "Check exact line citations, rendered SVG title/desc claims, button accessible-name claims, and verb consistency."
- NEW. Verification of a documentation review reports a per-item status from a fixed five-value set and names what it could not check. From USER 1 (line 4): "status VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, or INCONCLUSIVE" and "End by naming anything you could not check."
- PROJECT-SPECIFIC FACT. ADR 0010 lists the seven verbs as `apply`, `launch`, `refresh`, `restore`, `remove`, `policy-reload`, and `exec` as the seventh. `.kb/development-workshop-authority.md` names the count but not the verbs. From ASSISTANT (line 10): "adr/0010…:19 lists apply, launch, refresh, restore, remove, and policy-reload, and it adds exec as the seventh verb."
- PROJECT-SPECIFIC FACT. The four lifecycle verbs sit on line 545 of the authority `.mmd` file. Line 544 holds only the count label. From ASSISTANT (line 10): "Line 545 has launch / refresh / restore / remove."
- PROJECT-SPECIFIC FACT. The diagram edge reads "starts and revokes", but ADR 0010 defines revoking the reach as stopping the daemon, so the edge should read "starts and stops". From ASSISTANT (line 18): "adr/0010…:33 says The operator revokes the reach by stopping the daemon" and "The fix is starts and stops without the condition."
- PROJECT-SPECIFIC FACT. "bound" at `.kb/fence.md:115` means the six-attempt retry limit. The GLOSSARY **Bound** definition would give the wrong meaning, so the report should replace the word, not link it. From ASSISTANT (line 19): "At .kb/fence.md:115, bound means the six-attempt retry limit. GLOSSARY.md:73-74 defines Bound as what stops a reach. A link to that definition would give the wrong meaning."
- NEW. A button can carry an accessible name from its content and its `title`, so a claim that a button "lacks a name" must be read against the accessibility tree, not inferred from attributes. From ASSISTANT (line 18): "These buttons do have accessible names. The names come from their content, a minus sign and +, and each title gives a name or description." The agent stated its own limit at line 22: "I took the button names from the accessible-name rules, not from a browser accessibility tree."

## What should not become a skill

- The per-row citation corrections are edits to one report. Examples: `.kb/agent-workshop.md:39` should read `:39-40`, and the button citation should read `:56,58` because line 57 is a `<span>`. These are one-off fixes, not a reusable method.
- The row-1 request to remove the move of the `workshop --project` sentence. From ASSISTANT (line 12): "The sentence about workshop --project <directory> is at line 141, directly after the instruction. Remove the request to move it." This is an edit to one report.
- The row-4 citation change from `:52` to `:52-53`. From ASSISTANT (line 13): "Change the citation to :52-53, because the sentence continues onto line 53." This is a one-off fact.
