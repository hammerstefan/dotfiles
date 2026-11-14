# ses_e2f16efa5ffemm5Uw17xKTpmBB: Review PR 31 ADR 0001 fix

## What the person asked for

One user turn (flat line 2), the review brief from the parent session `ses_e2f1ce8d1ffew0PyV7RXBPvBUT`. It is the same brief that the failed session `ses_e2f176fceffeeTR4CUSlvrn1yT` received, sent a second time with `zai-coding-plan/glm-5.3-flash`. It asks for four things: concrete defects, style and format violations, scope, and a verdict of "approve, approve with nits, or request changes".

## What was produced, and whether it worked

- Verdict: "approve with nits".
- Section 1, concrete defects: "none found", with the evidence for each corrected sentence. Hunk 1 matches ADR 0005 lines 66 to 68 and `.kb/agent-workshop.md` line 73. The code agrees, because `setup-base` installs hermes with `sudo -u workshop -H bash -c`. Passwordless sudo is stated in ADR 0006 lines 40 to 42. The record already carried the correct claim in its Consequences, so the edit repairs an internal inconsistency.
- Section 2, style: no hard violations. Two optional nits, the compound sentences and the phrase "that user".
- Section 3, scope: no creep, and one completeness nit. Two sentences in the same record still say "root agent": "Both stay true in effect through sudo, so the conclusions are unaffected. Line 67 could simply become 'the agent can remove that CA'. Non-blocking, but worth one line in the same PR since these are the same claim being corrected."
- What worked: the parent applied both nits. The commit was amended to `e62db42`, and the Context and Consequences sentences were split. The parent followed the completeness nit on line 67 and left line 27.
- What the reviewer left open and the parent decided: line 27, "why a root agent defeats HTTPS credential injection". The parent's reason: "because it summarizes the argument of `research/web-egress-proxy.md` and should keep that record's words." (parent session, flat line 93)
- The verdict and the findings agree, the scope statement is concrete, and every claim it makes carries a file and a line.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

- The reviewer's sources for a code claim about hermes: `agent/.workshop/hermes/hooks/setup-base`, `agent/.workshop/agent.yaml`, and `.kb/agent-workshop.md`. The parent named them in the brief.
- The review rule that a category with nothing in it is reported: "say explicitly when you find nothing in a category" (parent brief, flat line 26).
- The parent's resolution rule for a sentence that quotes a research record: keep the record's words even when they read stale beside a new claim.

## Failures, their cause, and the fix

- No `!! FAILED` line appears in this session's tool log.
- The session exists because the first spawn failed on a retired model. The failure and its fix are recorded in the parent's transcript and in the digest of `ses_e2f176fceffeeTR4CUSlvrn1yT`.
- No other failure is visible. The four `execute` calls used `review_inspect` and `read`, which are the tools the runtime provides.

## Candidate lessons

1. NEW. A prose correction to an accepted record sweeps every place the same claim appears in that file. Quote: "Non-blocking, but worth one line in the same PR since these are the same claim being corrected." (assistant, section 3, flat line 65)
2. NEW. A correction that repeats the words of a research record keeps those words, and the pull request body says so. Quote the parent: "Left as-is, and stated in the PR body: Context line 27 ... because it summarizes the argument of `research/web-egress-proxy.md` and should keep that record's words." (parent session, flat line 93)
3. NEW. A review brief asks for an explicit "nothing found" per category, so an empty category reads as checked and not as skipped. Quote: "say explicitly when you find nothing in a category" (parent brief, flat line 26).
4. NEW. A review of a correction checks the record's own earlier statements first. The strongest evidence for the new sentence was the record's own Consequences, which already said the same thing. Quote: "The correction also repairs an internal inconsistency rather than creating one: the record already said 'Everything in a workshop runs as one user' (line 10)". (assistant, section 1, flat line 45)
5. ALREADY WRITTEN. The record format, the index rule, and the style laws the reviewer checked. `adr/README.md` and `.kb/writing-style.md` state them.

## What should not become a skill

- The line numbers in ADR 0001 and ADR 0005. They move with every edit.
- The wording of the two corrected sentences. They are in the merged commit.
- The `sudo -u workshop -H bash -c` invocation. `.kb/agent-workshop.md` states the run command, and the hook holds the line.
