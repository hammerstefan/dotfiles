## Why

The review subshell started by `get_pr` looks and behaves exactly like the
user's normal shell, so it is easy to forget that it is an ephemeral review
environment that must be exited (to trigger teardown of the worktree). A
visible prompt marker makes the subshell's special nature — and the way out
— obvious at all times.

## What Changes

- The review subshell's prompt (`PS1`) gains a leading indicator identifying
  it as a `get_pr` review subshell, including the pull request number (e.g.
  `(pr-42)`), applied on top of the user's normal prompt after `~/.bashrc`
  has been sourced.
- The subshell additionally exports an environment variable carrying the
  marker (name and PR number), so the indicator is also programmatically
  detectable and the prompt string can be customised by the user later.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `github-pr-worktree`: the "Review subshell" requirement gains a
  prompt-indicator obligation — the subshell MUST make itself visually
  distinguishable from a normal shell via a `pr-<N>`-tagged `PS1` prefix
  while preserving the user's own prompt configuration.

## Impact

- `get_pr` script: only the `build_init_file` heredoc (subshell init file)
  changes; setup, teardown, and guards are untouched.
- No changes to main worktrees, git configuration files, or other scripts.
- No new dependencies; the indicator reuses the PR number already resolved
  at setup time.
