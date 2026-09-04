## Context

`get_pr` drops the reviewer into `bash --init-file <(...)` whose init file
sources `~/.bashrc`, exports environment-scoped git config, and `cd`s into
the worktree. The user's `~/.bashrc` unconditionally sets `PS1` (a colored
variant under `xterm-color|*-256color`, a plain one otherwise;
`~/.bash-git-prompt` is not installed). Because the subshell inherits the
user's exact prompt, nothing on screen distinguishes it from a normal shell,
yet exiting it is the only trigger for worktree teardown.

## Goals / Non-Goals

**Goals:**

- Make every prompt inside the review subshell visibly identify it as a
  `get_pr` review environment for `pr-<N>` (e.g. `(pr-42)`).
- Preserve the user's own prompt configuration (colors, `__git_ps1`,
  `PROMPT_COMMAND`) — the marker is added *on top of*, not instead of, the
  normal prompt.
- Keep the marker programmatically available (env var) so scripts or future
  customisation can detect or restyle it.

**Non-Goals:**

- No changes to setup, guards, teardown, or git configuration handling.
- No prompt changes outside the review subshell (normal shells untouched).
- No theming framework, no per-prompt dynamic evaluation, no custom
  colors for the marker.
- No modification of `~/.bashrc` or any user dotfile.

## Decisions

- **D1: Modify `PS1` in the init file, after sourcing `~/.bashrc`.**
  The bashrc sets `PS1` unconditionally, so any marker set before the
  source would be clobbered. Appending `PS1="(pr-<N>) $PS1"` after the
  source (and after `cd`) reliably prefixes the final prompt in both the
  colored and plain variants. Alternative rejected: re-using the
  `debian_chroot` mechanism — the active `PS1` lines in this user's
  bashrc do not interpolate `${debian_chroot}`, so it would be invisible.

- **D2: Static, plain-text marker.** The PR number is known at setup time,
  so the prefix is baked in once at init; there is no per-prompt cost and
  no interaction with `__git_ps1`'s expansion. No ANSI colors: the bashrc
  deliberately degrades to a plain prompt on dumb terminals, and a colored
  marker would emit escape garbage there.

- **D3: Export `GET_PR_SUBSHELL="pr-<N>"`.** The env var carries the same
  identifier as the branch/worktree name, letting the user (or tooling)
  detect the subshell and restyle `PS1` in their own bashrc if they ever
  want to. Survives a manual `source ~/.bashrc` inside the subshell, which
  would strip the prefix from `PS1` (accepted trade-off; re-sourcing is
  rare and the visible prompt then simply loses the marker, not any
  functionality).

- **D4: Heredoc escaping.** `build_init_file` uses an unquoted heredoc, so
  the `PS1` assignment must escape the *inner* expansion (`\$PS1`) — the
  same pattern already used for `\$HOME` — while `pr-${pr_number}` is
  expanded by the outer script at generation time.

## Risks / Trade-offs

- [User re-sources `~/.bashrc` inside the subshell → marker disappears
  from `PS1`] → Mitigation: `GET_PR_SUBSHELL` env var remains exported;
  entry/exit messages from the script still frame the session.
- [Prompt frameworks (if ever installed) that rewrite `PS1` on every
  prompt via `PROMPT_COMMAND` could overwrite the marker] → Mitigation:
  out of scope today (`bash-git-prompt` is not installed); the env var
  remains as a detection hook for such setups.
- [Marker text adds width to every prompt line] → Mitigation: kept
  minimal (`(pr-<N>) `).
