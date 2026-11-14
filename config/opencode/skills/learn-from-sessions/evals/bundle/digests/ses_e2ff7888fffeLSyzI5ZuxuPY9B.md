# ses_e2ff7888fffeLSyzI5ZuxuPY9B: Review ADR 0005 branch changes

## What the person asked for

One user turn (flat line 2), the brief from the parent session `ses_e321e9151ffeTbwYCErDGc6Jm7`. It names the branch `wayfinder/agent-workshop-provisioning`, the commit `d3a1166`, the two files, and five review priorities in order. It closes with "Do not edit any files. Report findings as a list, each with file and line, severity (blocker / should-fix / nit), and the evidence for it. If a finding depends on an upstream fact you could not check, say so instead of guessing."

## What was produced, and whether it worked

- Eleven findings and the verdict "The record is **not ready to stand as written**".
- Finding 1, a blocker: ADR 0001's agent bridge allow rules name the LLM endpoint, while ADR 0005 makes the endpoint an operator secret behind `workshopctl get-secret`, which runs inside a workshop and not on the host. Quoted conclusion: "The fence either cannot be built as described, or the endpoint must be duplicated in committed host state (violating §1 of `.kb/project.md`)."
- Findings 2 and 3, should-fix: `agent.disabled_toolsets` and `approvals.deny` asserted without upstream confirmation. Evidence given: "The hermes-execution-model research ... does not name `agent.disabled_toolsets`. No other document in this repository confirms the key."
- Findings 4 to 8, should-fix: the `config.yaml` template omits the `secrets:` section, the helper's split of one keyring item into two names is unstated, the coupling between the committed proxy address and the fence's plane bridge address is unstated, four ADR 0001 references are bare text rather than short links, and "must be unlocked" is passive.
- Findings 9 and 11, nits: the headless approval keys, and the partial secret failure.
- Finding 10, a nit, on why `web` stays when `browser` goes.
- What worked: the parent accepted and fixed findings 1, 4, 5, 6, 7, 8, 9 and 11 in commit `c6b0b8d`. The blocker was a real gap in the record. Finding 7 and finding 8 match rules that `.kb/writing-style.md` and `adr/README.md` state.
- What did not hold: findings 2 and 3. The parent checked both keys against live pages and rejected them: "the reviewer's two 'unverified key' findings are factually wrong on correctness, but right that the record cites no source of verification for them." Its reason: "The reviewer only had the research record, which predates the key's documentation."
- Judgement: eight of eleven findings were acted on, one was skipped with a reason, and two were wrong. The verdict "not ready to stand as written" rested on the blocker and on the two wrong findings.

## Corrections the person made

(none found)

The session has one user turn, the parent's brief. No follow-up corrected it, and the parent's triage is recorded in the parent session `ses_e321e9151ffeTbwYCErDGc6Jm7`.

## Conventions, commands and values stated and written down nowhere

The parent agent, not the person, stated these:

- The severity words for a review in this repository: "severity (blocker / should-fix / nit)". No repository file fixes a severity scale.
- The linter path and the expectation that it is not enough: "The mechanical linter is at /home/stefan.hammer@canonical.com/.config/opencode/skills/asd-ste100/scripts/ste-lint.py". The brief adds "it already reports 0 violations, so look for what it cannot catch".
- The numbering state to check: "0003/0004 are reserved by parallel open branches" and "0005 must be the row added".
- The reader to review for: "Anything a later reader implementing 'Build the agent workshop' (issue #24) would misread."

## Failures, their cause, and the fix

- Five calls at flat lines 122 to 126 wrapped `execSync` from `child_process` inside `execute` to run the linter, `git show`, and `gh issue view`. The Code Mode runtime has no such module, so the calls could not have done the work, and each is logged as `ok execute`. The agent noticed and changed approach: "Let me use the available Code Mode tools instead. I'll use `review_inspect` for git operations and `semble` for the research files." (flat line 29)
- A later read of the four issue comment threads used `fetch` against `api.github.com` with no token, at flat line 131. The repository is private, so that request cannot succeed unauthenticated. The transcript does not show the answer, and no finding rests on it.
- No `!! FAILED` line appears in this session's tool log.
- The linter could not run through the attempted path, so the claim "it already reports 0 violations" comes from the parent, not from this session's own run.

## Candidate lessons

1. NEW. A reviewer that calls an upstream key unverified names each source it checked and the date of each. A research record older than the upstream page makes a correct claim look unsupported. Quote: "The hermes-execution-model research ... does not name `agent.disabled_toolsets`. No other document in this repository confirms the key." (assistant, finding 2, flat line 52)
2. NEW. A blocker is credible when it quotes the two paragraphs that cannot both be true and says what an implementer cannot resolve. Quote: "The fence either cannot be built as described, or the endpoint must be duplicated in committed host state (violating §1 of `.kb/project.md`)." (assistant, finding 1, flat line 46)
3. NEW. A review can state a false choice between two bad options, and the author answers it by naming the third option the record already implies. The parent: "The reviewer's dilemma ('fence cannot be built, or the endpoint must be committed') was false: the endpoint URL is not a credential, and the fence's reading mechanism is ticket #20's deliverable." (parent session, flat line 249)
4. NEW. A finding that a document cites no source is a real finding even when the fact is correct. The parent accepted that part: "right that the record cites no source of verification for them." (parent session, flat line 229)
5. ALREADY WRITTEN. Bare ADR references, passive voice, and one fact to a sentence. `.kb/writing-style.md` §Decision records states the short-link rule, and "Name who acts" states the passive rule.
6. ALREADY WRITTEN. The record structure, the status line, and the index row. `adr/README.md` §Conventions.
7. PROJECT-SPECIFIC FACT. That two config keys exist under the names `agent.disabled_toolsets` and `approvals.deny`. ADR 0005 now names both, and the upstream pages confirm them.

## What should not become a skill

- Finding 10, the asymmetry between keeping `web` and dropping `browser`. The parent skipped it with a reason the table already gives: "the table row already gives the reason."
- The severity words themselves. A three-step scale needs no skill.
- The specific line numbers in ADR 0005. The record changes, so a line number is evidence for one review only.
