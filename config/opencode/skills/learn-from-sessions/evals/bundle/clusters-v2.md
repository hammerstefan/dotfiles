# Lesson clusters, v2

Base: `clusters.md` from the 2026-11-13 run, 23 clusters over 57 digests.
Refresh: 2026-11-14, one new digest for each of the 48 sessions that had none.
Three of those 48 are byte-identical forks of `ses_e2a79290dffeekXpV7absQgR8u`,
so 45 new digests carry content.

An anchor names the session and the line in its flattened transcript,
`flat/<id>.txt`. Every quote below resolves at its line, or within three lines
of it. `verify_quotes.py` reads this file and checks each one.

Labels:

- `kept`: the rule stands as written, and the refresh adds no change.
- `updated`: the rule or its evidence changed. The change is stated.
- `new`: the refresh produced the cluster.
- `retired`: the rule no longer holds. The reason is stated.

A label is about the rule, not about whether a file states it. Most of these
rules already live in the repository. The rest are named under "Becomes".

## C1. A check script must be able to fail - kept

Evidence:
- `ses_e3a65724dffelibnb7cU48K6gm` line 135: "my header-spacing checker only looked at one line before each header, so it can never count 2 blanks"
- `ses_e340ed5deffemDfYui2pY4R3NE` line 225: "the one awk report was a cross-file artifact of my scan script"
- `ses_e3a65724dffelibnb7cU48K6gm` line 137: "line 46 of `.kb/agents.md` is the `# Knowledge Base` example inside upstream's own fenced code block"
- `ses_e2d2b58c2ffeHuzBKnV2ma2GvZ` line 386: "the pin matches the published `checksums.txt`"
- `ses_e2d2b58c2ffeHuzBKnV2ma2GvZ` digest line 69: "The check as executed did not compare the downloaded file"

The first sentence is true and the command behind it read the wrong file. The
digest line records the mismatch: the archive was saved under a dash name while
`checksums.txt` names an underscore name, so `sha256sum -c` never read the
downloaded archive. C13 and C14 are the same failure in other tools.

Becomes: `.opencode/skills/verify-a-claim/SKILL.md`, "Four shapes of a check
that lies" and "How to check a check".

## C2. A shared checkout belongs to whatever session is busy in it - kept

Evidence:
- `ses_e3a65724dffelibnb7cU48K6gm` line 197: "work in temp dirs, there is an active session running in the cwd branch"
- `ses_e3a65724dffelibnb7cU48K6gm` line 171: "My `git add -A` swept those unrelated files into my docs commit"
- `ses_e35651f4cffe6xJc5a1FCZtryq` line 228: "Main's committed ADR-0001 is the spike-measured version"
- `ses_e2825bf41ffeA8YXsuDvQAuCWy` line 9: "I'll rebase in a temporary worktree with a scratch branch, not touch that checkout."

The refresh adds one more case of the rule followed. The break in the second
quote is the failure the rule prevents.

Becomes: `AGENTS.md`, Working rules, first two entries, and
`.opencode/skills/merge-a-pull-request-stack/SKILL.md`.

## C3. Following a sibling repository's conventions means checking upstream - kept

Evidence:
- `ses_e3a65724dffelibnb7cU48K6gm` line 90: "is the repo .kb setup and instructions consistent with https://github.com/canonical/knowledge-base ?"

Becomes: no file yet. `AGENTS.md` does not state it.

## C4. A skill's seed template yields to the repository's own conventions - kept

Evidence:
- `ses_e340ed5deffemDfYui2pY4R3NE` line 124: "The installed skills don't reference `docs/agents/` at all"

Becomes: no file yet. The refresh adds no case to it.

## C5. An identifier in a request is verified before it is used - kept

Evidence:
- `ses_e340ed5deffemDfYui2pY4R3NE` line 3: "create private hammestefan/monitor-agent gh repo as this repo's origin"
- `ses_e340ed5deffemDfYui2pY4R3NE` line 9: "`hammestefan` doesn't exist on GitHub"

Becomes: nothing. It is a general habit.

## C6. A kept spike branch reaches the remote - kept

Evidence:
- `ses_e340ed5deffemDfYui2pY4R3NE` line 22: "push all the branches"

Becomes: `.kb/spikes.md` §7 for the kept branch. No file states that the remote
must hold it.

## C7. A probe against live host state breaks in four known ways - kept

Evidence:
- `ses_e2d2b58c2ffeHuzBKnV2ma2GvZ` line 237: "The run exited 1 before cleanup."
- `ses_e2d2b58c2ffeHuzBKnV2ma2GvZ` line 380: "a bug where a failed run left it behind"
- `ses_e2d2b58c2ffeHuzBKnV2ma2GvZ` line 221: "The live `/project` policy digest changed between runs (2746689c → bb898e2f)."
- `ses_e2d2b31bfffeUYYfEPDUexk2YN` digest line 135: "The lock files a fresh worktree needs, written before the fence can resolve"
- `ses_e2d2b31bfffeUYYfEPDUexk2YN` digest line 146: "the fence carries two workshops only"

Becomes: `.opencode/skills/fence-verification/SKILL.md` and
`.opencode/skills/verify-a-claim/SKILL.md`.

## C8. The host's tool versions are read before a document's claim about them - updated

Evidence:
- `ses_e2d2b31bfffeUYYfEPDUexk2YN` line 151: "gh 2.45.0 has no `--parent`"
- `ses_e28783289ffeXXihkFz6Kc9g0d` line 13: "Host probes confirm: `gh` is 2.104.0"
- `ses_e28783289ffeXXihkFz6Kc9g0d` line 13: "`lxc config set -p` = `--property` is true"

What changed: the old cluster said the host runs `gh` 2.45.0. On 2026-11-14 it
runs 2.104.0, and `.kb/issue-tracker.md` now states that version and its flags.
The `lxc` client is still 6.10.1 and still rejects `-p`, `--all` and `-a` as the
old digests recorded.

The rule changed with it: a version claim is a probe, not a fact inherited from
an earlier session. The old `gh` workarounds are retired. The `--parent`,
`--add-blocked-by` and `--add-sub-issue` forms now work.

Becomes: `.kb/issue-tracker.md`, Conventions, and `.kb/fence.md`, "The LXD
client it runs". The old `gh` 2.45 sentences are retired.

## C9. An operator value is never printed, and the obvious redaction fails - kept

Evidence:
- `ses_e2d2b31bfffeUYYfEPDUexk2YN` line 29: "None of them is in the repository, and no test run may print them."
- `ses_e2d2b31bfffeUYYfEPDUexk2YN` line 817: "secret-tool search --all service monitor-agent account llm-api-key"
- `ses_e2d2b31bfffeUYYfEPDUexk2YN` digest line 174: "The key was printed a second time (msg 92). Cause: the redaction"

Becomes: `AGENTS.md`, Working rules, and `.opencode/skills/verify-a-claim/SKILL.md`,
"Values that must not print".

## C10. A delivered change is a branch and a pull request the person merges - kept

Evidence:
- `ses_e2d2b58c2ffeHuzBKnV2ma2GvZ` line 408: "push, create pr for main changes"
- `ses_e2d2b58c2ffeHuzBKnV2ma2GvZ` line 439: "merge the pr. are we done?"

Becomes: `.opencode/skills/merge-a-pull-request-stack/SKILL.md`, "Merge it from
the bottom".

## C11. A branch's lifetime depends on what links it - updated

Evidence:
- `ses_e2d30ff01ffePWE31UOV5nrZ3d` line 296: "Deleting the branch breaks that link"
- `ses_e25b9ebe5ffe4T0S4EZeSDPbbf` line 70: "It now uses the relative `../research/web-egress-proxy.md` path that ADR 0004 and 0010 use."
- `ses_e25b9ebe5ffe4T0S4EZeSDPbbf` line 77: "`adr/0004-…:34` has the same defect"

What changed: a record that links a research branch by a `blob/` URL is a dead
link once the record is copied to `main`. The fixed form is a relative path to
the record on `main`. The branch's lifetime rule stays for a branch a record
still cites.

Becomes: `AGENTS.md`, the rule on a local branch's comment, and
`.kb/issue-tracker.md`, "Research findings".

## C12. A ticket's own body outranks the spawn command's slug rule - updated

Evidence:
- `ses_e2d30ff01ffePWE31UOV5nrZ3d` line 235: "The generic rule gives `wayfinder/<slug>` for a task ticket."
- `ses_e297c42d6ffeVSB3GOlPDou39y` line 277: "#48's brief uses `research/development-workshop-nested-lxd`, the branch the ticket body names"
- `ses_e28050c89ffe6Av0kFiLl7jMeO` line 138: "`research/<slug>` for a `wayfinder:research` ticket, `wayfinder/<slug>` for the other three."

What changed: the refresh states the whole rule, not one exception. The ticket
type picks the prefix, and the ticket body's own branch name outranks a slug
made from the title.

Becomes: `.kb/spikes.md` §2, `.kb/issue-tracker.md`, and the global
`wayfinder-hwt` command.

## C13. A test arm that shares the setting under test proves nothing - kept

Evidence:
- `ses_e2d2b31bfffeUYYfEPDUexk2YN` line 243: "The case A anomaly was my own test bug — the script clobbered `NO_PROXY` in both cases."

The old cluster filed a second item here, the measured `hostmatch.MatchGlob`
fact. That is a measurement with a working negative arm, not a check that could
not fail. It belongs in ADR 0008, and it is not evidence for this cluster.

Becomes: `.opencode/skills/verify-a-claim/SKILL.md`, "Four shapes of a check
that lies", and `adr/0008` for the glob fact.

## C14. A negative result needs a control that was shown to hit - kept

Evidence:
- `ses_e3536c40affegAmiHGj8lD3Vkm` line 44: "the `6.10/stable` branch path does **not** resolve on the GitHub mirror (404)"
- `ses_e34b265feffe9BZkiM63DEuZVg` line 155: "There is no `lxd-6.11` tag on the mirror"
- `ses_e352d72a9ffeqqXxfLWc7XdkCc` line 127: "is 25 lines in both v0.1.7 and v0.1.8 (it was 716 lines before the removal)"

The refresh adds an application: a documentation-review coverage check drops one
file from its list and expects one missing file.

- `ses_e25c7a726ffemkgd53YWrTUm02` line 31: "removing one research file reported one missing file"

Becomes: `.opencode/skills/verify-a-claim/SKILL.md`.

## C15. A research child is only as good as the premise it was given - kept

Evidence:
- `ses_e3536c40affegAmiHGj8lD3Vkm` line 44: "the `6.10/stable` branch path does **not** resolve on the GitHub mirror (404)"
- `ses_e32ea95acffeyejYnGLXXe5Ge8` line 63: "the driver **requires OVN**"

The first quote is the premise the parent handed the child, which was wrong.
The second is the prerequisite that belongs in the verdict, ahead of the
benefits.

Becomes: no single file. The rule shapes a child brief.

## C16. Landing a pull request stack - updated

Evidence:
- `ses_e2fa0b018ffeiQJxQdJlZNMTnU` line 680: "Stack branches contain no slashes beyond the base name"
- `ses_e2fa0b018ffeiQJxQdJlZNMTnU` line 773: "I retargeted each PR to `main` after the one below it merged."
- `ses_e2fa0b018ffeiQJxQdJlZNMTnU` line 356: "The tag was created before the fix commit"
- `ses_e2fa0b018ffeiQJxQdJlZNMTnU` line 406: "ADR 0006 on main **rejected** one project for both workshops"
- `ses_e259342b9ffedrDO2KukWmUUEB` line 18: "`git push --force-with-lease` → `443c6ae...f668623`"

What changed: the refresh adds the push that follows a rebase. Seven sessions
pushed a rewritten branch. Three named the old head, and four used the bare flag,
which C28 calls the weaker form.

Becomes: `.opencode/skills/merge-a-pull-request-stack/SKILL.md`, "Merge it from
the bottom" and "When `main` moves under the stack".

## C17. The shape of a review brief - kept

Evidence:
- `ses_e2edc6586ffexkPMbOf7NOM901` line 22: "use three-dot diffs (`...`) against the merge base"
- `ses_e2edc6586ffexkPMbOf7NOM901` line 41: "Constraints that are settled (do not ask to change these)"
- `ses_e2edc6586ffexkPMbOf7NOM901` line 58: "If you verify something is actually fine that looks suspicious, say so briefly"

Becomes: `.opencode/skills/review-a-change/SKILL.md`.

## C18. A parent adopts a child's verdict only if the child's commands ran - updated

Evidence:
- `ses_e321ea872ffeuUyyOvuQCYo8WS` line 223: "Five-way agreement between the ADR, the pin file, the #19 resolution comment, the PR body, and the map line."
- `ses_e25c7a726ffemkgd53YWrTUm02` line 22: "One agent flagged that it had searched, rather than fully read"
- `ses_e25b68d12ffe3XfAGBBJ5TE0P9` line 112: "Your previous run did not satisfy the full-read requirement"

What changed: the rule now covers coverage as well as verdicts. A child that
says it read everything is checked against its own tool log, and a shortfall is
sent back to the same child session. C25 states the coverage proof.

Becomes: `.opencode/skills/verify-a-claim/SKILL.md`, "How to report".

## C19. `gh pr edit` fails on a deprecated API, on 2.45 and on 2.104 - updated

Evidence:
- `ses_e2fa0b018ffeiQJxQdJlZNMTnU` line 532: "`gh pr edit` hits a deprecated-API bug in gh 2.45."
- `ses_e28c8242dffeTG5Hp2vUQ5NBzU` line 262: "The body did not update. The deprecation error aborted the edit."

What changed: the version bound is not the cause. The host moved from 2.45 to
2.104.0, and the same `gh pr edit` call still aborts on the Projects-classic
deprecation after it prints a success line, so the body stays unchanged. The old
cluster read this as a 2.45 limit. The rule is to read the body back with
`gh pr view --json body`, and to write it through the REST `PATCH` when the edit
refuses again.

Becomes: `.kb/issue-tracker.md`, Conventions.

## C20. Claiming a ticket hides it from every later frontier query - kept

Evidence:
- `ses_e3237d8ddffeA0aelhDcQYPKUn` line 137: "gh issue edit 17 --add-assignee @me"

Becomes: `AGENTS.md`, Working rules, and `.kb/issue-tracker.md`, "Wayfinding
operations".

## C21. Spawn a child with a brief prompt and let it decide - updated

Evidence:
- `ses_e3237d8ddffeA0aelhDcQYPKUn` line 38: "@hwt for EACH ticket you identified"
- `ses_e28050c89ffe6Av0kFiLl7jMeO` line 301: "take note of model switch, that needs to apply to hwt"
- `ses_e28050c89ffe6Av0kFiLl7jMeO` line 236: "give it the goal that the decision is recorded on the ticket"
- `ses_e297c42d6ffeVSB3GOlPDou39y` line 319: "I send one line into each with `opencode run --session <id>"

What changed: the refresh states the mechanics the old cluster left out. A model
switch applies to every remaining spawn and not to one already running. A
grilling ticket's goal is the decision on the ticket. A spawned session told a
wrong fact is corrected in place, with `opencode run --session`, and the delivery
is confirmed with `opencode session export`.

Becomes: the global `hwt` and `wayfinder` skills, and the `/wayfinder-hwt`
command. Not this repository.

## C22. Workshop and hermes start traps - kept

Evidence:
- `ses_e2f04cf0fffeipDNiO5o7dBdsX` line 309: "The `setup-base` hook had a `work: unbound variable` bug"
- `ses_e2fa08eb2ffewNk3XysPmOi06p` digest line 160: "A hand-written hermes `config.yaml` without `_config_version` makes"
- `ses_e2fa08eb2ffewNk3XysPmOi06p` digest line 171: "Gateway stopped by an unexpected signal"

The four start traps in the old cluster stand: the missing `_config_version`, the
gateway that dies under `workshop exec`, the `-- reload` form, and the
`work: unbound variable` hook. The refresh adds no trap.

Becomes: `.kb/agent-workshop.md` and
`.opencode/skills/run-a-workshop-in-a-vm/SKILL.md`.

## C23. A skill that works in every repository does not live here - updated

Evidence:
- `ses_e34a81f46ffelegPGJEG3QLtLg` line 620: "Global `hwt` skill + `/hwt` command (Recommended)"
- `ses_e28c08c21ffeTHqESwIB2yYvXl` line 291: "only kb entry for topology, not the others. if the skill has been updated you are done"
- `ses_e25c7a726ffemkgd53YWrTUm02` line 9: "Break the documentation up into logical groupings, then use the @review-readability agent on each grouping"

What changed: the refresh found three more bodies of general knowledge, and each
belongs outside this repository.

- The `diagram` skill's source handling, accessibility and template fixes
  (`ses_e28c8242dffeTG5Hp2vUQ5NBzU`, `ses_e28c08c21ffeTHqESwIB2yYvXl`,
  `ses_e25afdc2fffeR1Si4tpzt056v6`).
- The readability review's fan-out, coverage and output contract
  (`ses_e25c7a726ffemkgd53YWrTUm02`, and the global `review-council` command).
- The `hwt` spawn mechanics in C21.

None becomes a monitor-agent skill.

Becomes: `AGENTS.md`, the rule "A tool that works in every repository keeps its
skill in the global config", and the global files named here.

## C24. A review finding is verified on two axes and gets one of five statuses - new

Evidence:
- `ses_e25b5b046ffe981bL0gWLYnfSx` line 4: "independently decide whether each factual claim is supported and whether the proposed readability problem is real"
- `ses_e25b5b046ffe981bL0gWLYnfSx` line 4: "status VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, or INCONCLUSIVE"
- `ses_e25b5b042ffeRmoOY0J4rVuPqK` line 4: "Check exact line citations, rendered SVG title/desc claims, button accessible-name claims, and verb consistency."
- `ses_e25b5b042ffc2zT62yDdkbSJEP` line 15: "The three meanings are real, but the citations are off."
- `ses_e25b5b042ffdXgrRBJmwyKrOiQ` line 4: "End by naming anything you could not check."

Seven verification children received a brief from their parent session, one per
findings group, and each returned the same five-value table. The two axes
matter: a claim can be true while its citation is wrong, and that case is
`PARTLY VERIFIED`, not `VERIFIED`.

What the repository states today: `.opencode/skills/verify-a-claim/SKILL.md`
offers "verified" and "inconclusive" and says a check is inconclusive when it
settles nothing. It does not state this five-value set, and it does not tell a
reviewer to judge the factual claim and the proposed problem separately.

Becomes: `.opencode/skills/verify-a-claim/SKILL.md`, a new section on verifying
a review finding.

## C25. A fan-out review proves coverage, and "read in full" is a contract - new

Evidence:
- `ses_e25c7a726ffemkgd53YWrTUm02` line 29: "covered: 63 tracked files (60 Markdown, 3 diagram files)"
- `ses_e25c7a726ffemkgd53YWrTUm02` line 22: "One agent flagged that it had searched, rather than fully read"
- `ses_e25b5b02dffdWJSam3NwYKuor6` line 54: "your own limits say several generated commands were only searched"
- `ses_e25b68d12ffe3XfAGBBJ5TE0P9` line 112: "Your previous run did not satisfy the full-read requirement"

A group review counts its files against `git ls-files`, reports the count, the
missing list and the duplicate list, and proves the check can fail by dropping
one file. A child that reports a read it did not do is sent back to the same
session, not replaced. A stated limit does not satisfy a full-read brief.

`review-council.md` in the global config requires a coverage statement. It does
not state the group inventory diff, the duplicate check, or the rule that a
limited read fails the contract.

Becomes: the global `review-council` command and the `review-readability`
agent. A whole-corpus fan-out works in any repository, so C23 keeps it out of
this repository's skills. `review-council.md` requires a coverage statement but
does not state the group inventory diff or the full-read contract.

## C26. A finding the owner must decide stays open and is reported with its reason - new

Evidence:
- `ses_e25aff063ffem9EKGrJ14ISypE` line 6: "do not guess: leave the text, and report the item as open with the reason"
- `ses_e25afbe31ffe7j4d6XUKNu1fnQ` line 6: "do not guess: leave or qualify the text, and report the item as open with the reason"
- `ses_e25b5b02dffelkWlAfg76yNJ7W` line 16: "The owner must confirm the correct order."

Five fix children received this rule in their brief from the parent fix session,
and each applied it to a different document group. The rule has two halves: do
not guess, and report the open item with what you found.

Becomes: the global review workflow. The rule applies to any review that is
applied, and C23 keeps that body out of this repository's skills. The
repository's `review-a-change` already states that a verdict must agree with its
findings, and it does not state the open-with-reason report.

## C27. A finding that adds a required approval proposes a rule, not a clarification - new

Evidence:
- `ses_e25b68d12ffe3XfAGBBJ5TE0P9` line 56: "required approval would be a new rule, not clarification of an existing one"
- `ses_e25b5b02dffelkWlAfg76yNJ7W` line 12: "Adding a "required approval" step is a new rule the owner must decide, not a clarification."
- `ses_e25b5b046ffe981bL0gWLYnfSx` line 15: "The source says the opposite: a bug-fix framing does **not** make the change maintenance."

A finding can be true in its premise and still ask for a new rule. The verifier
labels that a proposed owner decision. The same check catches a finding that
reverses the source it cites, which is a correction, not a clarification.

Becomes: `.opencode/skills/review-a-change/SKILL.md`, "Before you flag
something", and `.opencode/skills/verify-a-claim/SKILL.md`.

## C28. A rebased branch is pushed with a lease, and rebase steps run without an editor - new

Evidence:
- `ses_e259342b9ffedrDO2KukWmUUEB` line 18: "`git push --force-with-lease` → `443c6ae...f668623`"
- `ses_e2825bf41ffeA8YXsuDvQAuCWy` line 73: "pushing the rebased branch with `--force-with-lease`"
- `ses_e2820a486ffeWALwGAVJSc6WwW` line 13: "Force-pushed with `--force-with-lease` (old head `b912a9b` → `9ffc3f6`)"
- `ses_e2876fc5effeZvTiCOmV1xueWX` line 138: "git push --force-with-lease=refs/heads/kb/host-tooling-and-stack-landing:04d3a246"
- `ses_e28783289ffeXXihkFz6Kc9g0d` line 124: "retry with a non-interactive editor"
- `ses_e28783289ffeXXihkFz6Kc9g0d` line 70: "`git merge-tree` reports content conflicts in `AGENTS.md` and `GLOSSARY.md`"

Seven sessions pushed a rewritten branch. Three named the head the remote holds,
so a concurrent push fails instead of being overwritten. Four used a bare
`--force-with-lease`, which accepts whatever the remote holds when the command
runs, and is the weaker form.

An interactive rebase in an unattended run needs `GIT_EDITOR=true` and, to drop
or reorder a commit, `GIT_SEQUENCE_EDITOR`. `git merge-tree --write-tree`
previews the conflicts before a rebase starts.

What the repository states today: `merge-a-pull-request-stack` names neither
the push form nor the editor variables. `AGENTS.md` names the SHA that a rebase
rewrites.

Becomes: `.opencode/skills/merge-a-pull-request-stack/SKILL.md`, a section on
rebasing and pushing.

## C29. After a rebase, re-check every finding and every gate, and check that upstream needs no change here - new

Evidence:
- `ses_e28a815b6ffef5Rh5JYpS1kH2k` line 84: "I just rebased. validate the findings still exist, then fix them"
- `ses_e28a815b6ffef5Rh5JYpS1kH2k` line 139: "Because the rebase brought the updated style checker (`262d684`), I re-ran the gate on the record before pushing"
- `ses_e2589af7affeLEqkNRdPpwJixH` line 3: "make sure upstream changes don't require changes in this branch"
- `ses_e2825bf41ffeA8YXsuDvQAuCWy` line 57: "`main` moved mid-rebase (PR #76 merged → `d3289e4`)"

A rebase adds documents and a new checker from `main`, so an earlier finding and
an earlier pass can both stop holding. The person's instruction was explicit:
re-validate, then fix, then push. The other half is positive: state that each
upstream change needs no change here, and why.

`merge-a-pull-request-stack` says to read what merged and adapt. It does not say
to re-run the review findings or the gates, and it does not ask for the positive
no-change statement.

Becomes: `.opencode/skills/merge-a-pull-request-stack/SKILL.md`, "When `main`
moves under the stack", and `.opencode/skills/review-a-change/SKILL.md`.

## C30. A research record is history, and a fix keeps its measurements - new

Evidence:
- `ses_e25afbe31ffe7j4d6XUKNu1fnQ` line 6: "These are historical records: keep measurements and dates; clarify labels, relations, and locations only."
- `ses_e25b5b042ffc2zT62yDdkbSJEP` line 4: "Historical records must be judged as history, not current runtime instructions."
- `ses_e25c6c102ffeX0MkYMMBlmCkWF` line 73: "in each later file, mark the items that were already found in an earlier spike"

A readability fix to a research record changes its labels, its cross-references
and where a fact is stated. It does not update a measurement to today's value,
and it does not delete an observation that a later spike repeats. The record
states what one run saw on one date.

`.kb/spikes.md` §5 says a spike's behavior is never described as the system's
behavior. It does not state the fix rule, and it does not state the cross-file
repetition rule.

Becomes: `.opencode/skills/review-a-change/SKILL.md`, and `.kb/spikes.md` §5.

## C31. A property test is written from the contract and shown to fail on the old code - new

Evidence:
- `ses_e2566d3e8ffeXoezjNVxLv37Je` line 9: "only if they are written from what the module *claims* rather than from what it *does*"
- `ses_e2566d3e8ffeXoezjNVxLv37Je` line 74: "Now I prove the checks can fail: run the new property file against the pre-fix code (HEAD) in a throwaway worktree."
- `ses_e2566d3e8ffeXoezjNVxLv37Je` line 78: "I'll commit the two fixes and the property file separately, each passing on its own."

An oracle written to match the code restates the code and cannot fail. Written
from the stated contract, it caught three defects on the first run. The proof
that it can fail runs the file against the code before the fix, in a worktree of
its own. The property file is its own commit, and it passes on that commit.

`.kb/project.md` states that every behavior ships with an example test. It does
not state when a property test is worth its cost, or how to prove it can fail.

Becomes: `.opencode/skills/verify-a-claim/SKILL.md` for the failure proof, and
`.kb/project.md` Testing for the contract rule.

## C32. A rename of a running service is a host migration, not only a tree sweep - new

Evidence:
- `ses_e2571af5bffeMWFmj71Q1iKsdE` line 36: "Both are fixable, but only if you do it in order: `just dev down` on the old commit first, then `up` on the new one"
- `ses_e27c8380affehSoW92XccRaJr4` line 196: "is it possible to have the service file live with the project?"

A renamed unit leaves the old unit linked in `~/.config/systemd/user` and, when
it was active, leaves the old daemon running as the operator on the old socket.
The migration is ordered: bring the old commit down before the new one comes up.
A unit file that names one worktree's absolute path is linked from the project
with `systemctl --user link`, so it does not outlive that worktree.

`retire-a-name` sweeps the tree, the branches and the tracker. It states neither
the host state nor the order.

Becomes: `.opencode/skills/retire-a-name/SKILL.md`, a section on a running
service.

## C33. A parallel fix edits only its assignment and reports `fixed` or `open` - new

Evidence:
- `ses_e25afcbacffeYp37vYiI8E245w` line 5: "Edit ONLY the files in your assignment. Other agents edit the other files in parallel. Do not commit, do not push, do not run git add."
- `ses_e25afbe31ffe7j4d6XUKNu1fnQ` line 5: "Edit ONLY files under research/. Other agents edit the other files in parallel."
- `ses_e25afdc2fffeR1Si4tpzt056v6` line 8: "Final answer: per finding, either "fixed: file — what changed" or "open: reason"."

Five fix children ran in parallel in one worktree. Each owned one document group,
committed nothing, and returned one line per finding. The parent then had a
complete map of what changed and what waits for the owner.

Becomes: the global review workflow. The fan-out and its output contract work in
any repository, so C23 keeps them out of this repository's skills.

## C34. A ticket close-out puts future work into tickets - new

Evidence:
- `ses_e28a683a5ffe16KwNIwHs02TNE` line 57: "make sure the future work is capture in extant or new tickets"

A research ticket closes with two statements: what it handles now, and what is
left. The second becomes an existing ticket or a new one, so the close leaves no
work only in a transcript.

Becomes: `.opencode/skills/resolve-a-decision-ticket/SKILL.md`, and
`.kb/issue-tracker.md`, "Resolve".

## C35. A worktree is dead weight when it is clean, pushed and merged - new

Evidence:
- `ses_e25b9ebe5ffe4T0S4EZeSDPbbf` line 15: "All four `/tmp/opencode` worktrees are clean (no uncommitted changes)."

Three checks settle it: `git status --branch` is clean, `git rev-list
--left-right --count <branch>...origin/<branch>` shows nothing unpushed, and
`git cherry main <branch>` shows every commit already on `main`. A worktree with
any of the three open is not dead weight.

Becomes: `AGENTS.md`, Working rules, or the global `hwt` skill. The repository
states how to use a temporary worktree, not when to remove one.

## C36. A skill quotes only output that exists, and one checker survives a duplicate - new

Evidence:
- `ses_e28783289ffeXXihkFz6Kc9g0d` line 75: "Four quoted outputs in the new skill are not in the record it cites."
- `ses_e28783289ffeXXihkFz6Kc9g0d` line 63: "port the test-count rule into the Python checker"

A skill that quotes a command's output must hold that output in the record it
cites, or the quote is a claim with no source. When a change adds a second
checker for the same job, the stronger one survives and the weaker one's unique
rule moves into it.

Becomes: `.opencode/skills/verify-a-claim/SKILL.md`, "How to check a check", and
`AGENTS.md`, Working rules.

## C37. A frontier answer is checked against the native ticket graph first - new

Evidence:
- `ses_e29a6e8fcffej9WEFqqvOxC3d5` line 459: "Every ticket's native `blockedBy` is **empty** on GitHub."
- `ses_e29a6e8fcffej9WEFqqvOxC3d5` line 547: "Map #44 has no native sub-issues, so the `frontier` query returns empty even with correct edges."
- `ses_e29edae3effeAER26N7y1PFTbm` line 227: "I see #38, why not that?"

The frontier query trusts native sub-issues and native blocking edges. When a
map holds its dependencies as prose lines in ticket bodies, the query answers
wrong: it reported nine takeable tickets where three were. The correction came
twice, and the second one also had to repair a missing sub-issue link.

This gap was found while re-reading the old digests, and `clusters.md` did not
hold it. `.kb/issue-tracker.md` states each fact separately: a body `Blocked by:`
line is invisible to the frontier query, and where sub-issues are unavailable,
map order is the task list in the map body. It does not state the check that
joins them: before an answer, confirm that the map's sub-issue list and blocking
edges exist, or apply the fallback and say so.

Becomes: `.kb/issue-tracker.md`, "Wayfinding operations", and the global
`wayfinder` command.

## C38. A repository setting goes in the project's gitconfig, not the global one - new

Evidence:
- `ses_e2f2b2b00ffeXWdtibMXa55t80` line 67: "create a project gitconfig that specifies origin remote default"

The user's `~/.gitconfig` named a `pushDefault` remote that this repository does
not have, so a plain `git push` failed. The person put the setting in the
project's own gitconfig and left the global file alone.

This gap was found while re-reading the old digests. No file states where a
repository-specific git setting belongs.

Becomes: `AGENTS.md`, Working rules.

## What the refresh did not mint

Four candidates did not become clusters.

An `edit` whose `oldString` misses the file's wrap is tool usage, not a
repository rule. The case is at `ses_e2820a486ffeWALwGAVJSc6WwW` line 132, and C2
already sends the work to a worktree. A `hindsight_capture_initiative` call that
needs a title is a tool note, too small for a cluster
(`ses_e2559ea08ffeJzdsDCzX1L1K59` line 235).

`review_inspect` has no `log` operation and a per-session budget
(`ses_e25b5b042ffdXgrRBJmwyKrOiQ` line 42). It is a tool limit, not a lesson
about this repository. A worktree subagent cannot read the main checkout's
`.git` (`ses_e25b5b042ffdXgrRBJmwyKrOiQ` line 39). It is a harness permission,
not a rule.

## Duplicate digests

`ses_e27fd0609ffeq53pUk18UIDNHJ`, `ses_e27fc20dfffe5XTtTCHn3686LX` and
`ses_e27f731fbffehHYadnzTEwD5mo` hold the same conversation as
`ses_e2a79290dffeekXpV7absQgR8u`. They carry no separate evidence and no
cluster.
