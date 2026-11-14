# Answer key: learn-from-sessions eval bundle

Nine digests, frozen 2026-11-14. Each entry states what a model must produce or
correct, the file it should become, and the quote the requirement rests on. The
quote anchors are lines in `flat/<id>.txt`; the digest carries the same words.

A requirement is met when the extraction names the rule, the file, and enough
evidence to check it. A requirement is missed when the rule is absent, or when
the model mints a new skill for a rule the repository already states under
another name. A model is not penalised for a cluster listed at the end as
outside the bundle.

## ses_e25c7a726ffemkgd53YWrTUm02: documentation review parent

Concern: documentation review. Clusters: C25, with C14 and C18 as context.

Required:

1. A whole-documentation review is split by logical group, and one reviewer runs
   per group in parallel. File: the global review workflow (`review-council` or
   `review-readability`), not a new monitor-agent skill. A model that mints a
   repository skill for this fails the C23 discrimination check.
   Quote: line 9, "Break the documentation up into logical groupings, then use
   the @review-readability agent on each grouping".

2. Coverage is proved by diffing the group inventory against `git ls-files` and
   reporting the count, the missing files and the duplicate files. File: the
   global review workflow.
   Quote: line 29, "covered: 63 tracked files (60 Markdown, 3 diagram files)".

3. The coverage check is proved able to fail by dropping one file and expecting
   one missing file. This is an application of the rule already in
   `verify-a-claim`; the model should cite that rule, not mint a second one.
   Quote: line 31, "removing one research file reported one missing file".

4. A child that reports it searched instead of reading is sent back to the same
   session, and a stated limit does not satisfy a full-read brief. File: the
   global review workflow.
   Quote: line 22, "I’ve asked that same agent to finish those files before I
   claim complete coverage".

## ses_e25b68d12ffe3XfAGBBJ5TE0P9: documentation verification

Concern: documentation verification. Clusters: C24, C25, C27.

Required:

1. A review finding is verified on two axes: whether the factual claim is
   supported, and whether the proposed problem is real. File:
   `.opencode/skills/verify-a-claim/SKILL.md`, a section on verifying a review
   finding.
   Quote: line 4, "independently decide whether each factual claim is supported
   and whether the proposed readability problem is real".

2. A verified finding gets one of five statuses: `VERIFIED`, `PARTLY VERIFIED`,
   `UNSUPPORTED`, `INCORRECT`, `INCONCLUSIVE`. File: the same section. The
   repository today offers only "verified" and "inconclusive", so this is a
   correction to an existing rule, not a new skill.
   Quote: line 4, "status VERIFIED, PARTLY VERIFIED, UNSUPPORTED, INCORRECT, or
   INCONCLUSIVE".

3. A citation is checked by the content at the cited line, not by the line
   falling inside the cited range. File: the same section, and
   `.opencode/skills/review-a-change/SKILL.md`, "Verify before you report".
   Quote: line 47, "the bridge gateway address appears at
   `research/separate-bridges.md:89`, not the cited lines 19-20".

4. A finding that adds a required approval proposes a new rule. Label it a
   proposed owner decision, not a clarification. File: `review-a-change`,
   "Before you flag something".
   Quote: line 56, "required approval would be a new rule, not clarification of
   an existing one".

5. A "use the glossary's terms" finding is not actionable until the glossary
   defines the terms named. File: `review-a-change`, "Before you flag
   something".
   Quote: line 53, "the glossary does not define terms that distinguish
   “channel,” “route,” and “transport.”" and "is not actionable until the report
   selects or defines a term".

## ses_e25afbe31ffe7j4d6XUKNu1fnQ: research-record fix

Concern: documentation fix. Clusters: C26, C30, C33.

Required:

1. A research record is history. A fix keeps its measurements and dates and
   changes only labels, relations and locations. File:
   `.opencode/skills/review-a-change/SKILL.md`, and `.kb/spikes.md` §5.
   Quote: line 6, "These are historical records: keep measurements and dates;
   clarify labels, relations, and locations only."

2. A finding that needs an owner decision, or a fact no record states, is left
   unchanged and reported open with the reason. File: `review-a-change`, the
   output section.
   Quote: line 6, "do not guess: leave or qualify the text, and report the item
   as open with the reason".

3. A fix pass reports one line per finding: `fixed: file — what changed` or
   `open: reason`. File: the global review workflow, which owns this output
   contract.
   Quote: line 8, "Final answer: per finding, either "fixed: file — what
   changed" or "open: reason"."

4. A parallel fix edits only its assigned files and commits nothing. File: the
   same section.
   Quote: line 5, "Edit ONLY files under research/. Other agents edit the other
   files in parallel."

5. A research-record fact is verified against its spike branch with
   `git branch -a`, `git log` and `git show origin/spike/<name>:<path>`. File:
   `.opencode/skills/verify-a-claim/SKILL.md`, "How to check a check".
   Quote: line 6, "spike branches (`git branch -a`, `git log`)".

## ses_e28783289ffeXXihkFz6Kc9g0d: PR #74 review and rebase

Concern: pull request review and rebase. Clusters: C8, C19, C28, C36.

Required:

1. Correct the `gh` version claim. The host runs 2.104.0 on 2026-11-12, so the
   2.45 flag workarounds are retired. The `gh pr edit` failure is not version
   bound, though: it still aborts on 2.104.0. File: `.kb/issue-tracker.md`,
   Conventions. A model that repeats "gh 2.45" as current fails this.
   Quote: line 13, "Host probes confirm: `gh` is 2.104.0 (so the PR's "gh 2.45"
   bullet is false here)".

2. `gh pr edit --body-file` can abort on a Projects-classic deprecation after it
   prints success, so the body stays unchanged. Read the body back with
   `gh pr view --json body`, and use the REST `PATCH` when the edit refuses
   again. File: `.kb/issue-tracker.md`, Conventions.
   Quote: line 262 of `ses_e28c8242dffeTG5Hp2vUQ5NBzU`, "The body did not
   update. The deprecation error aborted the edit."

3. Push a rebased branch with `--force-with-lease=<branch>:<remote-head>`, never
   with a bare force. File: `.opencode/skills/merge-a-pull-request-stack/SKILL.md`,
   a section on rebasing and pushing.
   Quote: line 138, the command
   "git push --force-with-lease=refs/heads/kb/host-tooling-and-stack-landing:04d3a246".

4. An unattended rebase runs with `GIT_EDITOR=true`, and a commit is dropped or
   reordered with `GIT_SEQUENCE_EDITOR`. `git merge-tree --write-tree` previews
   the conflicts. File: the same section.
   Quote: line 124, "retry with a non-interactive editor".

5. A skill that quotes a command's output must hold that output in the record it
   cites. File: `verify-a-claim`, "How to check a check".
   Quote: line 75, "Four quoted outputs in the new skill are not in the record it
   cites."

6. When a change adds a second checker for one job, the stronger checker
   survives and the weaker one's unique rule moves into it. File: `AGENTS.md`,
   Working rules.
   Quote: line 63, "port the test-count rule into the Python checker".

## ses_e28a815b6ffef5Rh5JYpS1kH2k: ADR 0010 after a rebase

Concern: decision record. Clusters: C29.

Required:

1. After a rebase, re-check each review finding against the current tree before
   fixing it, because the rebase can add documents that change the verdict.
   File: `.opencode/skills/merge-a-pull-request-stack/SKILL.md`, "When `main`
   moves under the stack".
   Quote: line 84, "I just rebased. validate the findings still exist, then fix
   them".

2. Re-run a gate the rebase changed. The rebase brought a new style checker, so
   the earlier clean result no longer held. File: the same section.
   Quote: line 139, "Because the rebase brought the updated style checker
   (`262d684`), I re-ran the gate on the record before pushing".

3. The rules already in the repository are cited, not minted: run `just style`
   on changed Markdown, read the record on `main` before amending a copy, and
   update a posted comment when a rebase rewrites its hashes. File: `AGENTS.md`
   and the merge skill.

## ses_e28050c89ffe6Av0kFiLl7jMeO: wayfinder frontier spawn

Concern: wayfinding. Clusters: C12, C21.

Required:

1. The ticket type picks the branch prefix: `research/<slug>` for a
   `wayfinder:research` ticket and `wayfinder/<slug>` for the other three. The
   ticket body's own branch name outranks a slug from the title. File:
   `.kb/spikes.md` §2 and `.kb/issue-tracker.md`.
   Quote: line 138, "`research/<slug>` for a `wayfinder:research` ticket,
   `wayfinder/<slug>` for the other three."

2. A model switch in the spawning session applies to every remaining spawn, and
   not to a session already running. File: the global `hwt` skill. This is not
   this repository's lesson (C23). A model that writes it into monitor-agent
   fails the discrimination check.
   Quote: line 301, "take note of model switch, that needs to apply to hwt".

3. A `frontier` request queries the map and confirms the list before spawning.
   File: the global `/wayfinder-hwt` command.
   Quote: line 59, "query the map for the tickets the person can pick up now,
   and confirm the list before spawning".

4. A grilling ticket's goal is the decision recorded on the ticket, with the
   person's answer in it, and no checkable end state. File: the global
   `wayfinder` or `/wayfinder-hwt` command.
   Quote: line 236, "give it the goal that the decision is recorded on the
   ticket".

5. The frontier rule itself (open children, no assignee, no open blocker, first
   in map order) is already written in `.kb/issue-tracker.md`. The model should
   cite it, not mint it.

## ses_e2566d3e8ffeXoezjNVxLv37Je: property tests

Concern: fence and tests. Clusters: C31.

Required:

1. A property test's oracle is written from the module's stated contract, not
   from its behavior. File: `.kb/project.md`, Testing, and
   `.opencode/skills/verify-a-claim/SKILL.md` for the failure proof.
   Quote: line 9, "only if they are written from what the module *claims*
   rather than from what it *does*".

2. A new property test is proved able to fail by running it against the pre-fix
   code at HEAD in a throwaway worktree. File: `verify-a-claim`, "How to check a
   check".
   Quote: line 74, "Now I prove the checks can fail: run the new property file
   against the pre-fix code (HEAD) in a throwaway worktree."

3. A fix and its property file are separate commits, each passing on its own.
   File: `.opencode/skills/merge-a-pull-request-stack/SKILL.md`, or `AGENTS.md`.
   Quote: line 78, "I'll commit the two fixes and the property file separately,
   each passing on its own."

4. A systemd unit file holds one directive per line, so a value with a line
   break is refused and not escaped. `WorkingDirectory=` is written unquoted,
   and `systemd-analyze verify` settles the spelling. File: `AGENTS.md`,
   Workshop definition rules, or `.kb/fence.md`.
   Quote: line 24, "quote() ... is correct for `ExecStart=` and wrong here,
   because systemd does not strip quotes on `WorkingDirectory=`."

5. Property tests are worth it only where an invariant generates cases the
   example tests do not name. The session refused four candidates for that
   reason. File: `.kb/project.md`, Testing.
   Quote: line 46, "input space too small or the invariant too weak to generate
   anything interesting".

## ses_e2571af5bffeMWFmj71Q1iKsdE: service rename

Concern: service rename. Clusters: C32.

Required:

1. A rename of a running control service strands host state: the old unit stays
   linked and the old daemon keeps running as the operator on the old socket.
   The migration is ordered, `just dev down` on the old commit before `up` on the
   new one, and the change states the order. File:
   `.opencode/skills/retire-a-name/SKILL.md`, a section on a running service.
   Quote: line 36, "Both are fixable, but only if you do it in order: `just dev
   down` on the old commit first, then `up` on the new one".

2. The `-dev` name inverted the risk, because the service runs with the
   operator's reach. This is a project fact for the change, not a rule.
   Quote: line 21, "wrong in the dangerous direction: this service runs as the
   operator with the operator's full reach".

3. The rules already in the repository are cited, not minted: name a service for
   what it does, and a decided name copied into an ADR is a decided literal.

## ses_e28a683a5ffe16KwNIwHs02TNE: ticket close-out

Concern: ticket close-out. Clusters: C34.

Required:

1. A research ticket's close-out separates what the ticket handles now from the
   future work, and the future work goes into extant or new tickets. File:
   `.opencode/skills/resolve-a-decision-ticket/SKILL.md`, and
   `.kb/issue-tracker.md`, "Resolve".
   Quote: line 57, "make sure the future work is capture in extant or new
   tickets".

2. The rules already written are cited, not minted: research findings reach
   `main` by a `docs/<name>` pull request and the research branch never merges
   (`.kb/spikes.md` §7); a commit pushed after its pull request merged needs a
   new pull request (`AGENTS.md`); a cancelled `question` call is a run limit,
   not an absent person (`AGENTS.md`).

## Clusters outside the bundle

The judge must not penalise a run for missing these. They are valid clusters,
and their evidence is not in the nine frozen digests.

- C1. A check script must be able to fail.
- C2. A shared checkout belongs to whatever session is busy in it.
- C3. Following a sibling repository's conventions means checking upstream.
- C4. A skill's seed template yields to the repository's own conventions.
- C5. An identifier in a request is verified before it is used.
- C6. A kept spike branch reaches the remote.
- C7. A probe against live host state breaks in four known ways.
- C9. An operator value is never printed, and the obvious redaction fails.
- C10. A delivered change is a branch and a pull request the person merges.
- C11. A branch's lifetime depends on what links it.
- C13. Two more checks that could not fail.
- C14. A negative result needs a control that was shown to hit.
- C15. A research child is only as good as the premise it was given.
- C16. Landing a pull request stack.
- C17. The shape of a review brief.
- C18. A parent adopts a child's verdict only if the child's commands ran.
- C20. Claiming a ticket hides it from every later frontier query.
- C22. Workshop and hermes start traps.
- C23. A skill that works in every repository does not live here.
- C35. A worktree is dead weight when it is clean, pushed and merged.
- C37. A frontier answer is checked against the native ticket graph first.
- C38. A repository setting goes in the project's gitconfig, not the global one.

C14, C16 and C18 are partly in the bundle through another digest. A model that
reaches them gets credit, and a model that does not is not penalised.
