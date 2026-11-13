---
description: Turn a finished worktree's sessions into repo-level skills in a pull request, then close the worktree
---

Load the `hwt-wrapup` skill with the skill tool, id `hwt-wrapup`, and follow it.

Run it from the session that lives in the worktree to wrap up — the one whose
work is finished. It reads that worktree's sessions.

Arguments:

$ARGUMENTS

`--dry-run` lists the sessions it would read and the plan, and spawns nothing.
`--keep` wraps up without closing the worktree. No arguments means the whole
chain. Anything else is not an argument: say what the two flags are, and do
nothing.
