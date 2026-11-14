# Extraction is a skill of its own, and its caller commits

One brief held everything a wrapup does. It held the export, the digests, the
synthesis and the claim checks. It held the review gate, the files, the checks,
the pull request, the memory documents and the close. Only the last part has any
business involving a worktree.

So the rest is `learn-from-sessions`, a skill that takes session exports and
produces repository-level knowledge. It writes one digest per session, a
synthesis against the existing conventions, a check of every claim, a staged
change and an extraction report. The later steps write from that report. It
commits nothing, because the branch is the caller's and the message is a claim
about intent. The wrapup keeps one-concern-per-commit and the pull request.

## Considered Options

- **Keep the whole procedure in the brief.** Rejected: a second caller would
  copy it, and a second copy of the claim checks is exactly what goes stale.
- **Inline the skill's text into the brief at render time.** Rejected: the brief
  stops being readable on its own and the runner grows a build step. Loading a
  skill at session start is the mechanism the reflection session already uses
  for `skill-creator` and `review-agent-instructions`.
- **Have the extraction commit.** Rejected: an ad-hoc extraction may sit on a
  feature branch that carries work of its own. The staged change belongs to the
  extraction and the commit is the caller's.
- **Give the extraction the Hindsight retention.** Rejected: retention writes
  outside the repository and no commit undoes it. The wrapup keeps it and feeds
  it from the extraction report.

## Consequences

- The reflection session must load `learn-from-sessions` before it writes
  anything. The brief stops rather than improvises when the skill is absent. The
  global config is a link into the main dotfiles checkout, so the skill must
  land there before a wrapup can use it.
- The brief keeps only the wrapup's own steps. Its numbered list is shorter and
  the structural check counts what the brief declares.
- The review lessons split across two eval suites: the extraction's, ported with
  their provenance, and a small one for what the brief still does.
- The session discovery moves out of `scripts/hwt-wrapup` into a script the
  skill owns. The runner and the skill then find sessions the same way.
