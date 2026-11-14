---
description: Turn a finished worktree's sessions into repo-level skills in a pull request, then close the worktree
---

Run, from this worktree:

```sh
hwt-wrapup --spawn $ARGUMENTS
```

It does the whole deterministic chain in one call — the refusal checks, the
session list, the brief and the goal, the dry run, and the spawn of the
reflection session that reads the transcripts, opens the pull request and closes
this worktree. Report what it printed, in a few lines, and stop.

The reflection session gets a space of its own that opens behind this one: the
window does not move, so the person reads the report where they asked for it
and finds the new space waiting in the sidebar.

`--dry-run` plans without spawning; `--keep` leaves this worktree open.

If it exits 3 it printed `wrapup: refused: <check>`. Repeat that reason and stop:
never choose another branch, base or session set to get past it.

If this worktree learned something the script cannot see — work that landed on
another branch or repository, a decision taken verbally — write it to a short
file, forty lines at most, and pass `--notes <file>`.

The `hwt-wrapup` skill documents what the reflection session does with the brief;
load it only when someone asks how a wrapup works.
