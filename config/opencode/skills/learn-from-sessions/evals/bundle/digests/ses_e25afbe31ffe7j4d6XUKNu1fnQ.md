# ses_e25afbe31ffe7j4d6XUKNu1fnQ: Fix research records

## What the person asked for

The person wrote one turn, a spawn brief (USER 1, line 2). In order:

- "You are a subagent spawned by another session." (USER 1, line 3)
- "Fix the findings assigned to you below by editing the named documents." (USER 1, line 4)
- "Edit ONLY files under research/. Other agents edit the other files in parallel. Do not commit, do not push, do not run git add." (USER 1, line 5)
- "These are historical records: keep measurements and dates; clarify labels, relations, and locations only." (USER 1, line 6)
- "Verify facts against the records themselves, spike branches (`git branch -a`, `git log`), and GitHub issues via `gh`. Never invent a fact." (USER 1, line 6)
- "If facts cannot be established (e.g. which run had which memory limit, the 8-second statement), do not guess: leave or qualify the text, and report the item as open with the reason." (USER 1, line 6)
- "Run `just style <file>` on every Markdown file you changed and fix its findings." (USER 1, line 7)
- "Final answer: per finding, either "fixed: file — what changed" or "open: reason". Keep it short." (USER 1, line 8)
- "Your assignment: All findings under '### Research records', plus the Minor suggestions for research/*." (USER 1, line 10)

## What was produced, and whether it worked

The agent edited nine files under `research/` and reported "I edited 9 files under `research/`" (ASSISTANT, line 12). The files are `research/iron-proxy-plane.md`, `research/two-workshop.md`, `research/separate-bridges.md`, `research/two-bridge-gateway.md`, `research/acl-fence.md`, `research/development-workshop-nested-lxd.md`, `research/development-workshop-ctlcmd.md`, `research/development-workshop-lxd-scope.md`, and `research/development-workshop.md` (ASSISTANT, lines 15-41).

Every finding under "Research records" is fixed except two facts in the nested-LXD record. The agent wrote "All findings are fixed except two facts in the nested-LXD record that no record can confirm." (ASSISTANT, line 12). The two open items are the run 3 memory limit and the 8-second suite figure (ASSISTANT, lines 25-29). "Nothing is committed or staged." (ASSISTANT, line 12). "`just style` reports 0 findings on every changed file." (ASSISTANT, line 12).

The agent verified facts against spike branches and GitHub issues. It ran `git branch -a`, `git log`, `git show origin/spike/<name>:spike/<name>/<file>`, `git ls-tree`, and `git grep` (tool log, lines 46-52, 58). It ran `gh issue list` and `gh issue view` with `-R hammerstefan/monitor-agent` (tool log, lines 48, 54). It ran `just style` on every changed file, and the run reported no findings (tool log, lines 65-66, 68).

What the agent verified from the spike branches:

- The two startup records are `iron-proxy starting` and `management server starting`, taken from `probe.sh` on the spike branch (ASSISTANT, line 17).
- `10.252.0.1` is the bridge gateway address of the agent bridge `abr0` (ASSISTANT, line 20).
- The two ACL objects live in the workshop project and the `default` project, confirmed in `run.sh` (ASSISTANT, line 22).

What was not verified: the run 3 memory limit and the 8-second figure. The 4 GiB statement "now says it is the only memory change the record shows a command for" and no record holds a command that set the 6 GiB limit (ASSISTANT, line 25). The text "uses the 3.56 seconds pytest printed" and "marks the earlier 8-second figure as having no measurement in any record" (ASSISTANT, line 28).

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

- "Edit ONLY files under research/. Other agents edit the other files in parallel." (USER 1, line 5). The parallel-edit boundary for a multi-session review fix. Not in `AGENTS.md`, which covers a checkout another session owns but not a per-directory split.
- "These are historical records: keep measurements and dates; clarify labels, relations, and locations only." (USER 1, line 6). The rule for editing a research record. Not written anywhere.
- "Verify facts against the records themselves, spike branches (`git branch -a`, `git log`), and GitHub issues via `gh`." (USER 1, line 6). The spike-branch verification commands are not written. `gh issue view` and `gh issue list` are written in `.kb/issue-tracker.md` lines 59-60.
- "Never invent a fact." (USER 1, line 6). Not written verbatim.
- "do not guess: leave or qualify the text, and report the item as open with the reason." (USER 1, line 6). The open-item output contract. Not written.
- "Final answer: per finding, either "fixed: file — what changed" or "open: reason"." (USER 1, line 8). The fix-child report shape. Not written.
- "Run `just style <file>` on every Markdown file you changed" (USER 1, line 7). Written in `AGENTS.md` line 135.

## Failures, their cause, and the fix

(none found)

## Candidate lessons

- NEW — A fix to a research record keeps its measurements and dates and changes only its labels, relations, and locations. From "These are historical records: keep measurements and dates; clarify labels, relations, and locations only." (USER 1, line 6).
- NEW — A fact that no record confirms is left qualified or reported open with a reason, never guessed. From "do not guess: leave or qualify the text, and report the item as open with the reason." (USER 1, line 6).
- NEW — A fix-child session reports each finding as "fixed: file — what changed" or "open: reason". From "Final answer: per finding, either "fixed: file — what changed" or "open: reason"." (USER 1, line 8).
- NEW — Verify a research-record fact against its spike branch with `git branch -a`, `git log`, and `git show origin/spike/<name>:<path>`. From "spike branches (`git branch -a`, `git log`)" (USER 1, line 6).
- ALREADY WRITTEN — Run `just style <file>` on every changed Markdown file and fix its findings. From "Run `just style <file>` on every Markdown file you changed and fix its findings." (USER 1, line 7). Written in `AGENTS.md` line 135.
- ALREADY WRITTEN — Never invent a fact, and quote a command only when it ran. From "Never invent a fact." (USER 1, line 6). Written in `.opencode/skills/verify-a-claim/SKILL.md` ("Quote a command only when that command ran").
- ALREADY WRITTEN — Read and list GitHub issues with `gh`. From "GitHub issues via `gh`" (USER 1, line 6). Written in `.kb/issue-tracker.md` lines 59-60.
- PROJECT-SPECIFIC FACT — The parallel-edit boundary for this review is "Edit ONLY files under research/". From "Edit ONLY files under research/. Other agents edit the other files in parallel." (USER 1, line 5).
- PROJECT-SPECIFIC FACT — `10.252.0.1` is the bridge gateway address of the agent bridge `abr0`. From "`10.252.0.1` is the bridge gateway address of the agent bridge `abr0`, confirmed on the spike branch." (ASSISTANT, line 20).
- PROJECT-SPECIFIC FACT — The measured pytest figure is 3.56 seconds. The 8-second figure has no measurement. From "The text now uses the 3.56 seconds pytest printed. It marks the earlier 8-second figure as having no measurement in any record." (ASSISTANT, line 28).

## What should not become a skill

- The parallel-edit boundary, "Edit ONLY files under research/." (USER 1, line 5). It is a one-off split for this review, not a reusable rule. It belongs in the fix-child brief.
- The values `10.252.0.1`, issue #18, issue #51, map #44, and ADR 0010. They are record facts. They already live in the research records after this fix.
- The 3.56-second and 8-second figures. They are record facts, already resolved in `docs/documentation-readability-review.md` lines 498-501.
- The `-R hammerstefan/monitor-agent` flag on `gh`. `.kb/issue-tracker.md` §1 says `gh` resolves the repository from the git remote, so the flag is redundant here.
