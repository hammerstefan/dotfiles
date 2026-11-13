# A wrapup's orchestration is one script, not a dozen turns

A wrapup starts at the end of the longest session in a worktree, and OpenCode
re-sends that session's whole transcript on every turn. So a wrapup run as a
conversation pays for the entire history again at every step. Measured on
monitor-agent's spike wrapup: eleven turns at a 320k-token context, 3.6M input
tokens and about $0.10 — while the reflection session that read the transcript, wrote
the skills and opened the pull request cost $0.045, its digest subagent
included. The orchestration cost more than the work.

Nine of those eleven turns had one right answer: the refusal checks, the session
list, the brief's paths, the goal, `hwt`'s dry run and the spawn. They are now
`scripts/hwt-wrapup`, one call that prints a dozen lines. The brief is rendered
from `config/opencode/skills/hwt-wrapup/brief.md.tmpl`, so the prompt text is
no longer retyped inside a large context; the parts that differ are extracted
from the trigger session's own export — the person's messages, the files it
wrote, the links and commits it produced — instead of being summarised by a
model that has already read all of it.

The judgement moves to where it is cheap: the reflection session reads the same
evidence in a fresh context. The trigger session contributes only `--notes`,
forty lines at most, for what the extraction cannot see.

## Considered Options

- **Keep the skill as prose and make it shorter.** Rejected: the cost is turns
  times context, not words in the skill. Ten shorter turns save nothing.
- **Have the script write the "what happened here" prose too.** Rejected: that
  is judgement, and it belongs in the reflection session's cheap context, not in
  the source session's expensive one. The script quotes and links instead.
- **Keep the brief inline in the skill text.** Rejected: it would be retyped
  into a file whose wording drifts from the skill's; one template, rendered, is
  one place to change.

## Consequences

- `hwt-wrapup --dry-run` proves the whole chain without spawning, and the plan it
  prints is what the trigger session reports.
- The brief names the trigger session's export, so the reflection session can
  read what the person's words do not say. It reads it flattened, never whole.
- The script needs Python 3 (standard library only) and the tools the skill
  already refused without: `hwt`, `opencode`, `gh`, `jq`, `herdr-app`.
- A generated brief is scratch, not source: change the template, never the file.
