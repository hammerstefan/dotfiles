# ses_e2f2b2b00ffeXWdtibMXa55t80: Branch work after PR 28

## What the person asked for

- "pr 28 landed, any other work to do in this branch?" (message 1,
  1794504991703)
- "fix it in a branch" (message 2, 1794505805105)
- "push and pr" (message 3, 1794505880693)
- "@review-deepseek pr30" (message 4, 1794505964788)
- `for 2 "Your ~/.gitconfig", create a project gitconfig that specifies origin
  remote default` (message 5, 1794506192515)

## What was produced, and whether it worked

- The answer to message 1: nothing left on that branch. Two review notes from
  PR 28 were merged unfixed. The agent's words: "**ADR 0006 Context is
  factually wrong:** "hermes runs as root in the agent workshop"." and
  "**ADR 0006's last consequence is stale:** "ADR 0005 states the old path.""
- A new worktree `.../.herdr/worktrees/monitor-agent/docs-adr-0006-review-notes`,
  branch `docs/adr-0006-review-notes` cut from `origin/main` at `9c9596b`.
  Commit `a78ff5d docs: address review findings in the plane record`. The agent
  reported `ste-lint` at "0 violations".
- PR #30 "Fix the review notes in the plane record", body written from a
  heredoc file, opened with `gh pr create`.
- After `@review-deepseek pr30` the agent ran the review subagent, which found
  a blocking defect. The agent's words: "**Blocking finding (fixed):** the
  Context paragraph still said ADR 0005 "places the agent SDK under
  `.workshop/`" — present tense, linking to a record this same work amended to
  `agent/.workshop/`. I'd fixed the note in Consequences and left the identical
  staleness three paragraphs up." A second commit `39ac14e docs: correct the
  agent SDK path claim in the plane record` followed, and the PR body was
  patched through `gh api -X PATCH repos/.../pulls/30 --input`.
- The git setting from message 5: `git config --local remote.pushDefault
  origin` run in the main checkout, then `git push --dry-run` from the PR
  worktree. The agent's words: "Local scope wins over global, and since the
  config lives in the shared `.git/config`, it covers every worktree of this
  repo."
- Verified against the current repository: `git config --local --get
  remote.pushDefault` in
  `/home/stefan.hammer@canonical.com/git/monitor-agent` answers `origin`, and
  the worktree `docs-adr-0006-review-notes` stands at `39ac14e`.
- Verified against the current repository: ADR 0001 no longer holds the root
  claim. Lines 130-131 now read "Every command runs as the workshop user in
  the persistent agent workshop container." Commit `e62db42 docs: correct the
  root claim in the agent record` carried the fix.
- Not verified: the state of PR #30, the `ste-lint` result, and the review
  subagent's report. The transcript of the subagent is
  `ses_e2f1bf293ffepPEMmljJy05Zwy`.
- Every tool call in this session succeeded. The tool log holds no `!!
  FAILED` line.

## Corrections the person made

- The agent asked: "Your `~/.gitconfig` has `remote.pushDefault =
  hammerstefan`, a remote that doesn't exist in this repo, so plain `git push`
  fails here with "Pushing to hammerstefan". I used `git push origin HEAD`. Want
  me to look at that config?" The person answered with a different target:
  `for 2 "Your ~/.gitconfig", create a project gitconfig that specifies origin
  remote default`. The setting belongs to this repository, and the global file
  is left alone.
- No other correction. Messages 2 to 4 grant the next step in one clause each.

## Conventions, commands and values stated and written down nowhere

- The person's phrase for the scope of a git setting is "a project gitconfig".
  The agent met it with the repository-local scope. Its words: "Set at the
  repo-local scope" and "`git config --local remote.pushDefault origin`".
- The value the setting needs: the remote `origin`.
- The review invocation: "`@review-deepseek pr30`" names the review agent and
  the pull-request number with no separator.
- Branch naming for a records fix: `docs/adr-0006-review-notes`, and the commit
  subject shape `docs: <verb> <what>`.
- The agent's claim about worktrees: "the config lives in the shared
  `.git/config`, it covers every worktree of this repo."
- The person's opening question is a blanket "any other work to do in this
  branch?", and the agent read it as one branch plus a list of the follow-ups
  that belong to other branches.
- The agent's rule for where a record is corrected: "Two things did get merged
  unfixed, so they're follow-ups on a *new* branch (records are amended in
  place, per `adr/README.md`)". The amendment rule is in `adr/README.md`, and
  the new-branch choice is not.

## Failures, their cause, and the fix

1. `git push` failed with no branch written. The agent's words: "plain `git
   push` fails here with "Pushing to hammerstefan"." Cause: `~/.gitconfig` sets
   `remote.pushDefault = hammerstefan`, and this repository has no remote by
   that name. Fix: `git push origin HEAD` for that push, then the repository
   local `remote.pushDefault origin` from message 5.
2. The first version of the fix was incomplete in a way the agent did not see.
   Cause: the same sentence pattern sat in three paragraphs, and the agent
   corrected only the one the PR body named. Fix: the review subagent raised it
   as blocking, and the agent rewrote "places" to "placed".
3. `gh` could not edit the PR body in place. The log shows the body written to
   a JSON file with `jq -Rs '{body: .}'` and patched with `gh api -X PATCH
   repos/hammerstefan/monitor-agent/pulls/30 --input`.

## Candidate lessons

- PROJECT-SPECIFIC FACT: this host's `~/.gitconfig` sets `remote.pushDefault =
  hammerstefan`, which this repository does not have. Agent: "Your
  `~/.gitconfig` has `remote.pushDefault = hammerstefan`, a remote that
  doesn't exist in this repo" (message 4 reply).
- NEW: a git setting that belongs to one repository is set at the repository
  local scope, because `.git/config` serves every worktree of that repository.
  Quote: "since the config lives in the shared `.git/config`, it covers every
  worktree of this repo" (message 5 reply). No file states it.
- NEW: a correction of a stale claim in a record covers every occurrence of the
  claim in that record, in one commit. Quote: "I'd fixed the note in
  Consequences and left the identical staleness three paragraphs up" (message 4
  reply).
- NEW: a sentence about a record that a later commit changed takes the past
  tense. Quote: "It's now "placed", which is true: ADR 0005 originally put it
  there, this record moves it, and the amended 0005 states the new path."
  (message 4 reply). `.kb/writing-style.md` states the present tense for what
  the system does and says nothing about a fact that a record moved.
- NEW: a `gh pr edit` body change fails here and is made through `gh api -X
  PATCH repos/<owner>/<repo>/pulls/<n> --input`. Quote from the log:
  `jq -Rs '{body: .}' /tmp/opencode/pr-body-adr0006.md > /tmp/opencode/pr30-body.json && gh api -X PATCH ... --input`.
- NEW: a review of a two-line docs patch is worth running, because the patch
  can repeat its own defect in another paragraph. Quote: "Review done, and it
  found a real one." (message 4 reply).
- NEW: the review invocation `@review-deepseek <pr>`. Quote: "`@review-deepseek
  pr30`" (message 4).
- ALREADY WRITTEN: an accepted record is amended in place.
  `adr/README.md` §Conventions, and the agent cites it: "records are amended in
  place, per `adr/README.md`".
- ALREADY WRITTEN: `ste-lint` is the mechanical first pass for a record.
  `adr/README.md` §Conventions ("its `ste-lint.py` script for a mechanical
  first pass").
- PROJECT-SPECIFIC FACT: the two stale sentences in ADR 0006 and the ADR 0001
  root claim. Both records hold the corrected text now.

## What should not become a skill

- The two sentence rewrites and the ADR 0001 line. The records hold them.
- "PR 28 is merged". That is one repository state on one day.
- The offer to fold the ADR 0001 line into the same PR. The person did not
  answer it, and the fix went in later under commit `e62db42`.
