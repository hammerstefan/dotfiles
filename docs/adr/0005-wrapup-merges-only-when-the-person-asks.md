# A wrapup merges the pull request only when the person asks for it in the last
# question

The wrapup opens one ready-for-review pull request and never merges it. The
person reviewed the work as it ran, and in five sessions the person answered
"close it and merge" in their own words. A session merged the pull request,
and rebased it first when the base moved. A session that merged on its own
made a decision that was not its own.

So the last question offers three options. Close both. Rebase the pull request
onto the base branch and merge it, then close both. Or leave both open. The
merge answer is the person's review decision, and other answers keep the
pull request unmerged.

## Considered Options

- **Keep the ban.** Rejected: the person merged from the question in five
  sessions, and typed it as free text because no option offered it. The person
  reviews the work as it runs, and the merge answer is their review decision.
- **Let a session merge on its own.** Rejected: the pull request is the review
  handoff, and a merge lands it on the base branch. Only the person makes that
  decision, and they make it from the question.
- **Squash the merge.** Rejected: the brief commits one concern per commit so
  the pull request reads as separate concerns. A squash collapses them into one
  on the base branch.

## Consequences

- The pull request is the only one a session may merge, and only on that
  answer. A merge the repository refuses leaves the pull request open. The
  session reports what the repository said and closes nothing.
- The rebase rewrites the branch. The push carries a lease on the head the
  remote held, so a push that lost a race fails instead of discarding a commit.
  A conflicting replay aborts for the same reason: never resolve, never guess.
- The goal accepts a merged pull request, not only an open one. A session that
  merged on request then stops, and the reviewer reads the goal as met.
- The merge method follows the target repository's own mainline: a merge
  commit there, a rebase in a repository that keeps a linear mainline.
- The pull request body may name the base or a commit id. The replay makes
  both stale, so the session re-checks them and corrects the body before the
  push.
