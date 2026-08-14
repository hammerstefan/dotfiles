## Why

Reviewing a GitHub PR locally today means either mutating the current checkout with `gh pr checkout` (which leaves a stray local branch behind forever) or hand-rolling a worktree plus remote wiring each time. The existing `get_mp` script solves exactly this shape for Launchpad merge proposals — an ephemeral, disposable review environment scoped to a subshell lifetime — but it only speaks Launchpad, and it is dead code (it hardcodes `PYTHON=/home/shammer/.pyenv/...`, a path that no longer exists).

`gh pr checkout --worktree` would cover part of this, but it is unreleased (merged to `cli/cli` trunk as `b130a9be` on 2026-07-21, absent from v2.97.0) and the locally installed `gh` is v2.45.0. Even when released it provides only the directory, not the subshell lifecycle or the teardown safety checks.

## What Changes

- Add a new `get_pr` script that, given a PR number or URL, creates a git worktree for the PR, drops the user into a subshell inside it, and tears the worktree down on exit.
- Delegate all fetch/remote/push plumbing to `gh pr checkout` run from inside the linked worktree, rather than reimplementing fork resolution and `maintainerCanModify` handling.
- Check out the PR onto a local branch renamed to `pr-<N>` to avoid collisions with existing local branches and to make teardown unambiguous.
- Restore working `git push` inside the review subshell via environment-scoped git config (`GIT_CONFIG_*`), without mutating repository config.
- Refuse teardown when the reviewer has committed work that is not part of the PR head, detected by comparing `HEAD` against the `headRefOid` recorded at setup.
- Implement in pure bash with no Python, no `launchpadlib`, and no virtualenv — unlike `get_mp`.

Not in scope: PR review commands (`diff`, `checks`, `comment`), environment provisioning inside the worktree (venv creation, dependency sync), and any change to the existing `get_mp` script.

## Capabilities

### New Capabilities
- `github-pr-worktree`: Creating, entering, and tearing down an ephemeral git worktree for a GitHub pull request, including push configuration and teardown safety guards.

### Modified Capabilities

(none — `openspec/specs/` currently contains only `oci-image-lookup`, which is unaffected)

## Impact

- **New files**: a `get_pr` script in `scripts/`.
- **External dependencies**: `gh` (v2.45.0 or later) and `git` (v2.43.0 or later), both already present. `gh` must be authenticated; the script does not attempt to authenticate.
- **Repository state touched**: adds `/pr-*/` to `.git/info/exclude` of the repository being reviewed (not committed, invisible to collaborators). Creates and deletes a `pr-<N>` worktree and local branch. Does not add or remove git remotes — `gh` writes the fork URL directly into `branch.pr-<N>.remote`, and `git branch -D` removes those keys.
- **Pre-existing environment issue surfaced, not fixed here**: `~/.gitconfig` sets `remote.pushdefault = hammerstefan`, a remote name that does not exist in third-party repositories. This breaks `git push` today, independent of this change. `get_pr` will neutralise it within its own subshell, but the global setting should be fixed separately.
