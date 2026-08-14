## Context

`get_mp` (Launchpad, Oct 2023, single commit) established the pattern this change ports to GitHub: fetch a proposed branch into a throwaway git worktree, drop the user into a subshell rooted there, and destroy the worktree when the subshell exits. Its value is not "fetch a branch" — it is that the review environment has a *lifetime* bounded by the shell.

Constraints discovered during exploration:

- Installed `gh` is **v2.45.0**; `gh pr checkout --worktree` is unreleased (trunk only, `b130a9be`, 2026-07-21).
- Installed `git` is **v2.43.0**.
- Push capability is a hard requirement, which rules out a detached `refs/pull/N/head` checkout.
- `~/.gitconfig` contains `remote.pushdefault = hammerstefan`, which breaks pushes in any repo lacking a remote by that name.

A spike validated the core approach against the real `cli/cli` repository, testing both a same-repo PR (#14136) and a fork PR (#14130). Results are cited inline below.

## Goals / Non-Goals

**Goals:**

- Given a PR number or URL, produce a ready-to-read worktree and a subshell inside it.
- Support `git push` back to the contributor's branch, for both same-repo and fork PRs.
- Tear down completely on exit, leaving no branches, worktrees, remotes, or config keys behind.
- Refuse to destroy reviewer work — both uncommitted and committed-but-unpushed.
- Zero runtime dependencies beyond `git` and `gh`. Pure bash.

**Non-Goals:**

- PR review commands (`pr diff`, `pr checks`, `pr comment`). Reading and pushing only.
- Provisioning the worktree for execution (venv creation, `uv sync`, copying `.test-env`). `osp-worktree.sh` does that for OpenSpec worktrees; `get_pr` deliberately does not.
- Working across repositories. The script requires the current directory to already be the correct repository.
- Fixing or replacing `get_mp`.
- Fixing the global `remote.pushdefault` misconfiguration (neutralised locally, not repaired).

## Decisions

### D1. Delegate plumbing to `gh pr checkout` run from inside the linked worktree

```
git worktree add --detach pr-<N> HEAD
( cd pr-<N> && gh pr checkout <N> -b pr-<N> )
```

`gh` resolves the base repo from the shared remotes in the common git dir, fetches the head, and writes `branch.pr-<N>.{remote,pushRemote,merge}`. This buys fork resolution and `maintainerCanModify` handling for free.

*Alternative rejected*: reimplementing the fetch and config by hand. Correct fork handling is non-trivial and `gh` already encodes it.

*Alternative rejected*: `gh pr checkout --worktree`. Unreleased and unavailable locally. Should be revisited once it ships — it would collapse D1 into a single command while leaving the rest of this design intact.

*Verified*: exit 0 for both same-repo and fork PRs; the worktree receives the PR head (`wt_head == headRefOid`) while the main worktree is unchanged. The per-worktree `FETCH_HEAD` hazard — which forced upstream's implementation to use `git -C <path>` — did not materialise, because `gh` runs both the fetch and the checkout with the worktree as cwd.

### D2. Rename the local branch to `pr-<N>`

Worktrees share `refs/heads` via the common git dir. Checking out under the contributor's `headRefName` risks colliding with an existing local branch (`main`, `develop`), and makes teardown ambiguous — deleting a branch you did not create.

*Trade-off*: breaks plain `git push` under `push.default=simple`, which matches on branch *name*. Addressed by D3.

### D3. Restore `git push` via environment-scoped config, not repo config

The subshell exports:

```
GIT_CONFIG_COUNT=2
GIT_CONFIG_KEY_0=push.default        GIT_CONFIG_VALUE_0=upstream
GIT_CONFIG_KEY_1=remote.pushdefault  GIT_CONFIG_VALUE_1=<branch.pr-N.remote>
```

`push.default=upstream` pushes `HEAD` to `branch.pr-<N>.merge` on `branch.pr-<N>.remote` — the contributor's branch — regardless of the local name. The second key is load-bearing, not decoration: `remote.pushDefault` overrides `branch.<name>.remote` for pushes, so the global `hammerstefan` value would otherwise hijack every push.

*Verified*: `git push` with these env keys pushed `pr-42 -> contributor-branch` correctly, and `git config --local --get push.default` afterwards returned nothing. No repository state was written.

*Alternative rejected*: a named remote (e.g. `pr-<N>` → fork URL, mirroring `get_mp`). Tested: it does **not** help, because the refusal is name-based, not remote-based. `git push pr42` produced the identical `upstream branch ... does not match` error, and its suggested remedy would silently create a branch literally named `pr-42` on the contributor's fork. It also reintroduces a teardown step (see D5).

*Alternative rejected*: `git config --worktree push.default upstream`. Requires permanently enabling `extensions.worktreeConfig` on the user's repository — mutating durable shared state to solve a per-PR concern.

*Alternative rejected*: injecting a `pr-push` shell function. Teaches a bespoke command instead of making the real one work, and edges toward the review-cockpit scope this change excludes.

### D4. Worktree lives inside the repository at `<main-worktree-root>/pr-<N>`

Follows `get_mp` (which used `repo.working_dir`). Git does not auto-ignore nested worktrees — verified, they appear as `?? pr-42/`. Mitigated by appending an idempotent `/pr-*/` line to `.git/info/exclude`, which silences both `git status` and `ripgrep` (both verified), lives in the common dir, and is never committed.

*Accepted limitation*: `.git/info/exclude` does not stop `pytest` collection or other non-gitignore-aware tooling from walking into the worktree. Acceptable because the scope is reading, not running.

*Accepted limitation*: the exclude line outlives teardown. A single stable `/pr-*/` pattern added once is preferred over add/remove churn per PR.

The path resolves against the **main** worktree root, not `pwd`, so invoking from a subdirectory behaves correctly.

### D5. Teardown is `git worktree remove` + `git branch -D`

*Verified*: `gh` adds **no named remote**. For fork PRs it writes the fork URL directly into `branch.pr-<N>.remote` and `.pushRemote`. Deleting the branch removes those keys. After teardown, `git remote -v` contained only `origin` and all `branch.pr-<N>.*` keys were gone.

This means `get_mp`'s `delete_remote()` step has no analogue here. It is also the second reason to reject the named-remote alternative in D3.

### D6. Two independent teardown guards

| Reviewer state | Detection | Behaviour |
|---|---|---|
| Uncommitted changes | `git worktree remove` refuses on its own | abort, surface git's message |
| Committed, not pushed | `HEAD != pull request head` | abort, print `git log <oid>..HEAD --oneline` |

*Verified*: `git worktree remove` on a dirty worktree exits 128 with `fatal: 'pr-N' contains modified or untracked files, use --force to delete it`. The OID comparison correctly detected a dummy commit and produced a sensible listing.

The OID tripwire deliberately avoids `@{upstream}`, which may not resolve for cross-repo PRs where only a single ref was fetched.

The head OID is re-queried from `gh pr view --json headRefOid` **at teardown**, not reused from setup. Comparing against the setup-time value would refuse teardown for work the reviewer had already pushed — a false positive on the one workflow that push support exists to enable. The setup-time value is retained only as a fallback for when the re-query fails (offline, rate limited), and the tool says so when it falls back.

### D7. Argument is a PR number or a URL; resolution is delegated

`gh pr view <arg> --json number,headRefOid,state` accepts either form and yields a number, so everything downstream is uniform — no URL parsing.

When a URL is supplied, its `owner/repo` is compared against `gh repo view --json nameWithOwner` and mismatches fail loudly rather than silently building a worktree of the wrong project. Sitting in a fork is handled correctly for free: `gh` resolves the base repo to upstream, which is the match we want.

## Risks / Trade-offs

- **`gh` behaviour inside linked worktrees is undocumented and untested upstream on v2.45** → validated by spike for both PR topologies; a future `gh` upgrade could regress it. Once `--worktree` ships, migrate to it and delete the cd-into-worktree workaround.
- **The `-b pr-<N>` rename hides the contributor's branch name** from the prompt and `git status` during review → accepted by the user; the real name remains visible in `branch.pr-<N>.merge` and in `gh pr view`.
- **`GIT_CONFIG_*` env vars leak to every git command in the subshell**, not just pushes → `push.default` and `remote.pushdefault` affect only push behaviour, and the subshell exists solely for this PR.
- **A user who unsets or overrides `GIT_CONFIG_COUNT` inside the subshell loses working push** → acceptable; failure is loud, not silent.
- **Nesting**: invoking `get_pr` from inside a `pr-<N>` worktree. Path resolution against the main worktree root (D4) already prevents nested directories; the script additionally refuses when invoked from a linked worktree, so the two mechanisms are belt-and-braces.
- **Closed or merged PRs** are still checked out; `state` is available and could gate this, but refusing would block a legitimate use (reading a merged PR). Warn rather than refuse.
