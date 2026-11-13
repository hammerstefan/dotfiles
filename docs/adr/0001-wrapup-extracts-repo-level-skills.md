# A finished worktree is wrapped up into repo-level skills, then closed

`hwt` gives every ask its own worktree, Herdr space and session, so the lessons
in those sessions die with the worktree and the space sits there until someone
removes it by hand. So a wrapup reads every worktree session, subagents
included, and has one reflection session in a worktree of its own turn the
lessons into repo-level `.opencode/skills`, AGENTS.md or GLOSSARY.md edits, and
Hindsight memory; it opens one ready-for-review pull request against the
repository's default branch, one commit per concern, and only then closes the
space and removes the checkout.

Skills go to the repository rather than the global config because a lesson
learned in one project is not a rule for every project. The pull request is
based on the default branch rather than on the worktree's, so it can be
reviewed as skill changes alone instead of carrying unrelated feature commits.
Closing comes last and only when the pull request exists and no session in the
worktree is busy, because it is the one irreversible step: uncommitted work in
that checkout is what a premature close destroys.

## Considered Options

- **Base the branch on the worktree's HEAD.** Rejected: until the feature
  branch merges, the pull request shows its commits too, and reviewers cannot
  review skill changes on their own.
- **Write the lessons to the global skills directory.** Rejected: it makes one
  project's conventions bind every project.
- **Read every transcript in the reflection session itself.** Rejected: a
  finished worktree runs to megabytes, so the session fills with raw tool
  output before it reaches synthesis.
- **Close the worktree by hand afterwards.** Rejected: it never happens, and
  the worktrees accumulate.

## Consequences

- Session enumeration reads the local session store (`session_v2`), which is
  not a public interface; a schema change breaks it, so the skill must fall
  back and say that subagent sessions were skipped.
- A reflection session cannot trigger the skills it just wrote: they are in
  its checkout, while OpenCode loads them from the global directory until the
  pull request merges.
- Repositories that ignore `.opencode/` wholesale cannot receive skills; this
  repository must stop ignoring the directory's contents except for them.
