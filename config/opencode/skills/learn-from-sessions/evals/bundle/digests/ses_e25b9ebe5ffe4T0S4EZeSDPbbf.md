# ses_e25b9ebe5ffe4T0S4EZeSDPbbf: Review active research worktrees for cleanup

## What the person asked for

USER 1 (line 3): "The following worktree are reported as already running"

The list (USER 1, lines 5-9):

- line 6: "research/web-egress-proxy — /tmp/opencode/web-egress-proxy"
- line 7: "research/development-workshop-channel — /tmp/opencode/wt-channel"
- line 8: "research/development-workshop-ctlcmd — /tmp/opencode/wt-ctlcmd"
- line 9: "research/development-workshop-lxd-scope — /tmp/opencode/wt-lxd"

USER 1 (line 11): "however, I don't think I'm using any of those. Check that state of them, identify if there is anything that needs conciling, then confirm with me before removing"

The person then answered the agent's two questions. These answers are in the raw export, in the question tool result, not in the flattened file:

- "option one, plus wt-docs, wt-record, pr74-review. KEEP review-writing that is in progress"
- "Open a docs/ PR to copy it to main"

## What was produced, and whether it worked

- Seven worktrees removed with `git worktree remove`, no branch deleted. The four `/tmp/opencode` research worktrees plus `/tmp/opencode/wt-docs`, `wt-record`, and `pr74-review` (line 54). The agent reported the removals and stated every branch still exists locally and on `origin` (line 61).
- Pull request #86, "docs: record the web egress proxy research", opened at https://github.com/hammerstefan/monitor-agent/pull/86 (line 65). It copies the 584-line record to `main` from `research/web-egress-proxy` (line 67).
- The record copy needed three fixes. Two stale ADR links in the record now name the current ADR 0001 file. ADR 0001's link to the record now uses a relative path. A banned word `carries` at ADR 0001 line 75 was rewritten (lines 69-71).
- `just style` reports 0 findings on both files and on the PR body (line 73).
- `review-writing` and `wayfinder/fence-from-development-workshop` were left alone (line 59). The agent stated the `wayfinder` branch has 1,757 unmerged lines across 15 files and is live work (line 42).
- Verified: the worktree states, branch push status, and merge status were checked with git before removal. Not verified: nothing in the transcript shows PR #86 merged.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

- The person's rule to confirm before removing (USER 1, line 11): "confirm with me before removing". No repository document states this rule for worktree cleanup.
- The scope decision from the question answers: "KEEP review-writing that is in progress". This names `review-writing` as in-progress work that cleanup must not touch.
- Commands used that the repository does not record: `git worktree remove` (line 106), `git rev-list --left-right --count <branch>...origin/<branch>` to read push status (line 84), and `git cherry main <branch>` to read merge status (line 100).

## Failures, their cause, and the fix

- FAILED edit (line 117): the edit of the record's ADR link. Error (line 118): "Found 2 matches for oldString, but expected exactly one. Add more surrounding context to make oldString unique, or set replaceAll to true." The record held two identical stale ADR 0001 links, so the plain edit matched twice. The fix set `replaceAll: true` (line 120).

## Candidate lessons

- ADR records cite a research record with a relative `../research/<name>.md` path, never a `blob/` URL to a research branch. Quote (ASSISTANT, line 70): "It now uses the relative `../research/web-egress-proxy.md` path that ADR 0004 and 0010 use." NEW.
- A `blob/` URL to a research branch is a dead link for a record that §7 copies to `main`. Quote (ASSISTANT, line 77): "`adr/0004-…:34` has the same defect: it links `research/workshop-definition-and-lifecycle` by a `blob/` URL to that branch, and the record is not on `main`." NEW.
- A research record reaches `main` through a `docs/<name>` pull request, and the research branch never merges. Quote (ASSISTANT, line 67): "It copies the 584-line record to `main` from `research/web-egress-proxy`, per `.kb/spikes.md` §7, and the branch stays unmerged." ALREADY WRITTEN in `.kb/spikes.md` §7 and `.kb/issue-tracker.md`.
- `just style` flags the banned word `carries`. Quote (ASSISTANT, line 71): "`just style` flagged `carries` at ADR 0001 line 75". ALREADY WRITTEN in `.kb/writing-style.md` Banned words and in `AGENTS.md` line 137.
- A worktree is dead weight when it is clean, has 0 unpushed commits, and its commits are merged. Check with `git status --branch`, `git rev-list --left-right --count <branch>...origin/<branch>`, and `git cherry main <branch>`. Quote (ASSISTANT, line 15): "All four `/tmp/opencode` worktrees are clean (no uncommitted changes)." NEW.

## What should not become a skill

- The edit tool failure "Found 2 matches for oldString" and its `replaceAll: true` fix (line 118, line 120). This is generic tool behavior, not a repository lesson.
- The specific values: branch names `research/web-egress-proxy`, worktree paths `/tmp/opencode/wt-channel`, ticket keys #13 and #65, and PR number #86. These are PROJECT-SPECIFIC FACT that belongs in a record, not a skill.
- The ADR 0001 filename change from `0001-hermes-runs-in-a-fenced-workshop-and-a-second-workshop-mediates-its-workload-egress.md` to the current name (line 69). This is history, not a reusable rule.
- The agent's use of the banned word "load-bearing" in its reply (line 36). The word is banned in `.kb/writing-style.md`, so the reply was itself a style finding, not a lesson.
