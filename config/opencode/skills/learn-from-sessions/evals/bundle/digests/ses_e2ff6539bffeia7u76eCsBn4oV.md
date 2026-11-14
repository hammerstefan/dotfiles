# ses_e2ff6539bffeia7u76eCsBn4oV: Review plane proxy policy branch

## What the person asked for

The session has one user turn (flat line 2), the brief from the parent session `ses_e321eb4dcffeOwt9gHumsL86cU`. It opens: "You are a subagent spawned by another session. Review the changes on branch `wayfinder/plane-proxy-config`". It sets the scope to "Exactly one commit: `git show 140e62e`", lists eight review criteria, and asks for a verdict, findings with severity, a "Verified correct" list, and a "Not verified" heading.

## What was produced, and whether it worked

- Verdict: "Verdict: approve with nits".
- Finding 1, marked "Major": the file's header comment said the fence admits the agent subnet to the tunnel listener "only", and ADR 0001's agent bridge allow rules also name the LLM endpoint and the bridge resolver. The reviewer quoted both texts and offered two rewrites.
- Finding 2, marked "Minor": the commit body of `140e62e` used "joins" and "itself", both on the banned-word list in `.kb/writing-style.md`. The reviewer quoted the rule.
- Finding 3, marked "Minor": the `.kb/project.md` sentence "holds no code yet". The reviewer closed it with "No change needed unless the author wants to qualify it."
- A "Verified correct" list with a source line for each claim: the `Config` struct keys at `config.go:54-67`, `KnownFields(true)` at `config.go:234`, the DNS pointer at `config.go:88` and `config.go:287`, the always-bound listeners at `proxy.go:159,170`, the tunnel protocols at `tunnel.go:63-91`, `TLSModeSNIOnly` at `config.go:153`, the allowlist keys at `allowlist.go:27-31`, the metrics listener at `main.go:309`, the management defaults at `config.go:275` and `config.go:324-326`, the log block at `config.go:188`, the five deny ranges at `dnsguard/dnsguard.go:16-34`, and the warn behavior at `allowlist.go:81-89`.
- What worked: the parent applied finding 1 in commit `24f158f` and left findings 2 and 3. Finding 1 was real. The reviewer's reading of ADR 0001 matches the record.
- What did not hold: the reviewer listed "the documentation pages name no release" under "Not verified", on the ground that "The upstream docs site `https://docs.iron.sh` was not fetched". The parent had fetched that page during the ticket work and said so in its report: "I did verify during the ticket work: I fetched docs.iron.sh's configuration reference on 2026-11-12 and it carries no version string anywhere." The claim was true, and the review reported it as unchecked.
- The reviewer never saw the follow-up commit. Its brief named one commit, and the parent created the second commit after the review returned.

## Corrections the person made

(none found)

The only user turn is the parent session's brief. No follow-up turn corrected this reviewer.

## Conventions, commands and values stated and written down nowhere

The parent agent, not the person, stated these in the review brief:

- The evidence rule: "Keep it evidence-based: no speculation without a quoted source line. If you cannot verify something because a file is missing, say so explicitly under a 'Not verified' heading."
- The reference tree for a release check: "A reference clone of the upstream repository is checked out at tag v0.56.0 (commit 3d96ce8dd2ca093051b75ccb0c9e5e1db52d1c04) at /tmp/opencode/iron-proxy. If it is missing, recreate it read-only with: git clone --depth 1 --branch v0.56.0 https://github.com/ironsh/iron-proxy.git /tmp/opencode/iron-proxy"
- The security check on a policy file: "the deny-CIDR default is not accidentally disabled (an explicit empty list would disable it — confirm the file does not do that)".

## Failures, their cause, and the fix

- The reviewer tried to run git inside the Code Mode runtime. One execute call ran an async block whose body ended in `return "need to use shell"`, so the call reported success and produced no git output. A later call used `await import('fs')` and `readFileSync` on the clone's README, and the runtime has no filesystem module. The fix was `tools.review_inspect` with `range_diff` against `origin/main` for the overlap check and plain `read` for the README.
- No `!! FAILED` line appears in the tool log. Every one of these calls is logged as `ok execute`.

## Candidate lessons

1. NEW. A review brief names the exact commit and the reference tree, and requires a quoted source line for each claim. A review built that way produced a finding that named the two conflicting texts and a verification list that cites a file and a line number each. Quote: "Keep it evidence-based: no speculation without a quoted source line." (parent brief at flat line 38)
2. NEW. A review that returns "approve with nits" while its first finding is marked "Major" gives the author no single instruction to follow. The verdict and the finding severity disagree. Quote: "**Verdict: approve with nits**" and "### 1. Major" (assistant, flat lines 52 and 56).
3. NEW. A review's "Not verified" heading reports the reviewer's reach. The author reads it as a request for the check it could not make, and answers it in the reply. Quote the parent: "One gap the reviewer flagged as unverified, 'the documentation pages name no release', I did verify during the ticket work: I fetched docs.iron.sh's configuration reference on 2026-11-12 and it carries no version string anywhere." (parent session `ses_e321eb4dcffeOwt9gHumsL86cU`, flat line 206)
4. NEW. A review of a file whose comments state security properties must read each comment as a claim separate from the YAML keys. Finding 1 rests on one word in a comment, and the schema was correct throughout. Quote the finding: "The word 'only' makes this claim false." (assistant, flat line 64)
5. ALREADY WRITTEN. The banned words "joins" and "itself" and the rule that a word stays only when dropping it changes the fact. `.kb/writing-style.md` §Concepts, "Banned words".
6. ALREADY WRITTEN. Every schema field and default the reviewer confirmed. The committed `plane/proxy-policy.yaml` states them in its comments, and `research/iron-proxy-plane.md` records the loader behavior.

## What should not become a skill

- The YAML field names and defaults of `v0.56.0`. They are upstream release facts and belong in the policy file's comments.
- The `10.255.0.10:1080` binding. It is this project's choice.
- The "holds no code yet" wording question. The reviewer itself closed it with "No change needed".
