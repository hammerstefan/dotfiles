# ses_e25b5b042ffc2zT62yDdkbSJEP: Verify network research findings

## What the person asked for

One USER turn, a spawning brief (USER 1, line 4). Its requests, in order:

- "Read-only verification of an existing documentation readability review." (USER 1, line 4)
- "Read .kb/agents.md and .kb/writing-style.md first." (USER 1, line 4)
- "Verify the network/proxy research findings: all bullets under 'Research records' that cite research/iron-proxy-plane.md, research/two-workshop.md, research/separate-bridges.md, research/two-bridge-gateway.md, or research/acl-fence.md, plus the network part of Minor editorial 'Mark historical research relationships'." (USER 1, line 4)
- "For each report bullet, independently decide whether each factual claim is supported, whether the seeming conflict is actually resolved by surrounding context, and whether the proposed clarification accurately describes it." (USER 1, line 4)
- "Check exact line citations." (USER 1, line 4)
- "Return a compact item-by-item table with status VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, or INCONCLUSIVE; exact source line evidence; and any needed correction." (USER 1, line 4)
- "End by naming anything you could not check." (USER 1, line 4)
- "Do not edit files, run workshops, mutate git, or use network." (USER 1, line 4)
- "Historical records must be judged as history, not current runtime instructions." (USER 1, line 4)

## What was produced, and whether it worked

- A nine-row verification table (lines 10-19). The agent states the totals: "I checked nine items: four are verified and five are partly verified. None is unsupported, incorrect or inconclusive." (line 6)
- The agent read the five research files in full and the report bullets at lines 201-246 and 419-425 (line 6).
- A list of three things it could not check (lines 21-24).
- Empty `review-json` and `review-readability-json` blocks (lines 26-28, 34-38). The agent writes "None. This was a check of an existing report, not a new review." (line 32).
- No file was changed. The tool log holds one skill load, one grep, and eight reads (lines 41-51). This matches the read-only instruction.

A deviation. The brief says "Read .kb/agents.md and .kb/writing-style.md first." (USER 1, line 4). The tool log shows no read of either file. The agent instead loaded the `asd-ste100` skill and read the global `~/.config/opencode/command/review-council.md` and `~/.config/opencode/prompt/readability-criteria.md` (lines 41-43).

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

- The five verification statuses: "VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, or INCONCLUSIVE" (USER 1, line 4). `.opencode/skills/verify-a-claim/SKILL.md` names "verified" and "inconclusive", not this five-value set.
- "Historical records must be judged as history, not current runtime instructions." (USER 1, line 4).
- "Check exact line citations." (USER 1, line 4).
- "Do not edit files, run workshops, mutate git, or use network." (USER 1, line 4). `.opencode/skills/review-a-change/SKILL.md` states a similar rule in its Read-only section, but it names "change files", "commit", "push", and Workshop or LXD state, not "mutate git" or "use network".

## Failures, their cause, and the fix

(none found)

## Candidate lessons

1. NEW. A verification of a review must check the citation line numbers, not only the facts. A fact can be true while its citation points at the wrong line. Evidence: "The three meanings are real, but the citations are off." (line 15), and "The lifecycle revert is at lines 29-36 and 77-88, so that citation is wrong." (line 18).
2. NEW. Use the five-value status set VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, INCONCLUSIVE, and treat PARTLY VERIFIED as a real answer for a fact that is true while its citation or placement is wrong. `.opencode/skills/verify-a-claim/SKILL.md` records "verified" and "inconclusive" but not this set. Source: the brief (USER 1, line 4), and the table where five of nine items are PARTLY VERIFIED (lines 10, 15, 17, 18).
3. ALREADY WRITTEN. Judge research records as history, not as current runtime instructions. `.kb/spikes.md` §5 states "a spike's behavior is never described as the system's behavior", and `.opencode/skills/review-a-change/SKILL.md` states "Name the date of every source the review reads." Both cover the rule the brief states at line 4.
4. NEW. Read the required files that a verification brief names, before loading the global review configuration. The brief named `.kb/agents.md` and `.kb/writing-style.md` (USER 1, line 4). The tool log shows the agent read the global `review-council.md` and `readability-criteria.md` instead (lines 42-43). This is an inference from the tool log, not a person statement.
5. PROJECT-SPECIFIC FACT. The two spikes used different agent-bridge subnets. `separate-bridges.md` uses `10.252.0.1/24`, and `two-bridge-gateway.md:71` uses `10.254.0.1/24` (line 15).
6. PROJECT-SPECIFIC FACT. `separate-bridges.md:89` names the bridge's own gateway address. Lines 16-17, 19-20, and 90-92 name OpenShell gateways (line 15).
7. PROJECT-SPECIFIC FACT. A progression note exists in `separate-bridges.md:96-100` and `two-bridge-gateway.md:9-12`. `two-workshop.md` lacks a forward link (line 18).

## What should not become a skill

- The line-number corrections in items 6 and 8 target an uncommitted draft report. The numbers will not stay valid after the report is edited, so they should not become a skill (lines 15, 18).
- The empty `review-json` and `review-readability-json` blocks show this session returned no review findings and no readability suggestions. Producing empty blocks is not a reusable lesson (lines 26-28, 34-38).
- The `asd-ste100` skill load and the reads of the global `review-council.md` and `readability-criteria.md` are harness scaffolding, not a lesson (lines 41-43).
