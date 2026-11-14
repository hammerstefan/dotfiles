# ses_e2ff70385ffezGBIMA57wXXcC7: Review proxy digest pin branch

## What the person asked for

- Message 1 (flat line 4), the brief from the parent session `ses_e321ea872ffeuUyyOvuQCYo8WS`. It names the scope as "the single commit `91065b7`", the three files, the rules to check, three cheap upstream checks to run, and the hard rules: "this is a read-only review. Do not commit, push, or edit any file."
- Message 2 (flat line 184), the parent correcting the first answer: "Two of your shells crashed and your final answer did not say whether those verifications were completed." It gives the error, a workaround, five numbered checks, and the rule "state plainly for each whether it is now verified or not verified".

## What was produced, and whether it worked

- First answer: "## Verdict: **Ready to merge.** No blocking findings."
- A verification table with a method and a result per claim: the digest against the published `checksums.txt` (match), no `.asc` asset at `v0.56.0`, `checksums.txt.asc` at `v0.42.0`, no signing step in the workflow, `sign-release.sh` present, a 404 from the attestations API, `install.sh` comparing against `checksums.txt`, no `signs:` block in `.goreleaser.yml`, and the STE linter at 0 violations.
- Two things it did not verify, stated: whether GoReleaser Pro signs by default without a `signs:` block, and the exact control flow of `install.sh` when the `.asc` download fails.
- Three non-blocking findings. Finding 1: the workflow uses `goreleaser-pro`, so the ADR could say "GoReleaser Pro". Finding 2: the `install.sh` skip happens on `gpg` absence. Finding 3: the reviewer's own `curl` used the `paradigmxyz` name while the other calls used `ironsh`.
- A self-correction after reading the source: "That output corrects my earlier note. The install.sh has three branches, and line 80 is explicit: ... The ADR's claim 'It skips the signature verification with a warning when the signature asset is absent' is **precisely accurate**. I withdraw non-blocking finding #2."
- Second answer after the correction: a five-point table for the requested checks, all marked verified, and the one surviving observation about GoReleaser Pro.
- What worked: finding 1 was applied by the parent in commit `8496901`, and the withdrawal of finding 2 was right. The digest comparison the reviewer ran is correct.
- What the record does not support: the second answer writes "Read with `gh issue view 19 --json comments --jq '.comments[-1].body'`" and quotes that comment by line number. The tool log for that turn shows several `execute` calls whose code was sent as a quoted string, so nothing ran, and shell launches whose output is not visible in the log. Six of the calls in the second turn are like that, at flat lines 350 and 354 to 362. The parent then reported the five-way agreement as verified.
- Verdict of first answer against its own findings: "Ready to merge" with zero blocking findings, while the parent's own note said one finding was worth fixing. The parent fixed it.

## Corrections the person made

- The parent: "Two of your shells crashed and your final answer did not say whether those verifications were completed. The failure cause: `gh issue view <n> --comments` ... fails with `GraphQL: Projects (classic) is being deprecated... (repository.issue.projectCards)`. That is a gh CLI quirk, not a repository problem." (message 2, flat line 184)
- The parent, in the same message, on how to report: "Please finish or confirm these parts of the review scope, and state plainly for each whether it is now verified or not verified."

## Conventions, commands and values stated and written down nowhere

The parent agent, not the person, stated these:

- `curl -fsSL https://github.com/paradigmxyz/iron-proxy/releases/download/v0.56.0/checksums.txt` as the source of the published checksums.
- `gh api repos/ironsh/iron-proxy/attestations/sha256:...` as the check that no attestation exists.
- `python3 /home/stefan.hammer@canonical.com/.config/opencode/skills/asd-ste100/scripts/ste-lint.py adr/0004-the-plane-verifies-the-proxy-archive-against-a-pinned-digest.md` as the mechanical style check.
- The escalation path for a crashed shell: "never use the default field set. Use explicit fields, for example: `gh issue view 19 --json comments --jq '.comments[-1].body'`".

## Failures, their cause, and the fix

- Two background shells died on `gh issue view` with its default field set. The cause is the deprecated `projectCards` GraphQL field, which the `gh` version on this host still requests. The fix was `--json comments` and `--json body` with a `--jq` filter.
- The reviewer's first attempt to poll a shell used a `while (true)` loop inside `execute` with no timer available, so the code could not wait. It then used `shell_wait` and `shell_watch`.
- Several `execute` calls in the second turn sent the code as a quoted string. The log shows `ok execute` with a value like `"const worktree = \"/home/...` at flat lines 350, 354, 355, 357, 359 and 361. A quoted string is a valid code expression, so the runtime returned the string and ran nothing. The work that reached a shell is the `shell_start` calls, and their output is not in the log.
- No `!! FAILED` line appears in this session's tool log.

## Candidate lessons

1. NEW. A reviewer states "verified" per item, and never leaves the reader to infer which checks ran. Quote the parent: "state plainly for each whether it is now verified or not verified". (user message 2, flat line 191)
2. NEW. A reviewer that withdraws a finding names the source line that changed its mind, so the author can check the withdrawal. Quote: "The install.sh has three branches, and line 80 is explicit: ... The ADR's claim ... is **precisely accurate**. I withdraw non-blocking finding #2." (assistant, flat line 160)
3. NEW. A review verdict must agree with its findings. This session returned "Ready to merge" while its first finding was text the parent then changed. A finding worth a commit is not a non-blocking observation. Quote: "## Verdict: **Ready to merge.** No blocking findings." (assistant, flat line 75) and the parent's "The review came back clean: ready to merge, zero blocking findings, one optional precision note. I'll apply that one-word fix" (parent, flat line 205).
4. NEW. Inside the Code Mode runtime, send code and not a string. A quoted string returns the string and runs nothing, and the tool log records it as success. Six calls in this session did that (flat lines 350 to 362).
5. NEW. A gh read from a subagent needs one plain call per read. A background shell plus polling plus a second layer of execute produced a run whose output nobody could see.
6. ALREADY WRITTEN. The style and lint checks: `.kb/writing-style.md` and the `ste-lint.py` first pass that `adr/README.md` names.
7. ALREADY WRITTEN. The residual risk of the pin, the GoReleaser reading, and the rejected alternatives. ADR 0004 carries them.

## What should not become a skill

- The `ironsh` against `paradigmxyz` name question. The reviewer closed it with "Not a defect in any committed file".
- The `goreleaser-pro` wording. It is one word in one record, and the parent applied it.
- Whether GoReleaser Pro signs by default. It is an upstream question about one tool, and the release carries no `.asc` file, which settles the practical answer.
