## 1. Scaffold

- [x] 1.1 Create `scripts/get_pr` as an executable bash script with `set -euo pipefail` and a usage/help path
- [x] 1.2 Implement argument handling: exactly one positional argument, reject zero or more than one with a usage message and non-zero exit
- [x] 1.3 Add a preflight check that `git` and `gh` are on `PATH`, failing non-zero with a clear message if either is missing
- [x] 1.4 Add a preflight check for `gh auth status`, failing non-zero without prompting or initiating authentication

## 2. Context guards

- [x] 2.1 Refuse to run when not inside a git repository
- [x] 2.2 Determine the main worktree root (e.g. first entry of `git worktree list --porcelain`) and refuse to run when the current directory is inside a linked worktree
- [x] 2.3 Detect whether the argument is a URL, and when it is, compare its `owner/repo` against `gh repo view --json nameWithOwner`, failing non-zero and naming both repositories on mismatch
- [x] 2.4 Confirm the fork case passes the guard: invoking from a clone of a fork with an upstream pull request must proceed
- [x] 2.5 Verify all guards run before any worktree, branch, or config is created

## 3. Pull request resolution

- [x] 3.1 Resolve the argument via `gh pr view <arg> --json number,headRefOid,state`, using its output rather than parsing the argument
- [x] 3.2 Extract `number`, `headRefOid`, and `state`; store `headRefOid` as the teardown fallback value
- [x] 3.3 Emit a warning when `state` is `CLOSED` or `MERGED`, without refusing

## 4. Worktree creation

- [x] 4.1 Append `/pr-*/` to `.git/info/exclude` if that exact pattern is not already present; verify repeated invocations do not duplicate the line
- [x] 4.2 Create the worktree with `git worktree add --detach <root>/pr-<N> HEAD`, resolving the path against the main worktree root rather than `pwd`
- [x] 4.3 Run `gh pr checkout <N> -b pr-<N>` with the worktree as the current directory
- [x] 4.4 Assert after checkout that `git -C pr-<N> rev-parse HEAD` equals `headRefOid`, and abort with cleanup if it does not
- [x] 4.5 Handle failure of any step in this group by removing the partially created worktree and branch before exiting, so a failed setup leaves no residue

## 5. Review subshell

- [x] 5.1 Read `branch.pr-<N>.remote` after checkout to determine the push destination
- [x] 5.2 Build the subshell init-file: source `~/.bashrc`, export `GIT_CONFIG_COUNT=2` with `push.default=upstream` and `remote.pushdefault=<branch.pr-N.remote>`, then `cd` into the worktree
- [x] 5.3 Launch `bash --init-file <(...)` and block until it exits
- [x] 5.4 Confirm no `push.default` or `remote.pushdefault` is written to any git config file at any scope
- [x] 5.5 Confirm no helper commands, aliases, or functions are defined in the subshell

## 6. Teardown

- [x] 6.1 On subshell exit, re-query the pull request head via `gh pr view <N> --json headRefOid`, falling back to the setup-time value and printing a staleness note when the re-query fails
- [x] 6.2 Compare the worktree `HEAD` against that OID; on divergence, print `git log <oid>..HEAD --oneline` and refuse teardown, leaving worktree and branch intact
- [x] 6.3 On match, run `git worktree remove <root>/pr-<N>` without `--force`, surfacing git's refusal message verbatim if the worktree is dirty
- [x] 6.4 On successful worktree removal, run `git branch -D pr-<N>`
- [x] 6.5 Confirm teardown deletes no git remote
- [x] 6.6 Set a non-zero exit status when teardown is refused, so the refusal is scriptable

## 7. Verification

- [x] 7.1 End-to-end test against a real same-repository pull request: create, inspect, exit, confirm clean teardown
- [x] 7.2 End-to-end test against a real fork pull request, confirming no named remote is created and that `branch.pr-<N>.pushRemote` holds the fork URL
- [x] 7.3 Verify `git status` in the main worktree does not list `pr-<N>`, and that `rg --files` does not descend into it
- [x] 7.4 Verify branch-name collision handling by testing a pull request whose head branch matches an existing local branch
- [x] 7.5 Verify push behaviour with a dry run inside the subshell, confirming the resolved destination is `HEAD:<contributor-branch>` on the head repository and that the global `remote.pushdefault` does not hijack it
- [x] 7.6 Verify the uncommitted-changes guard: edit a file, exit, confirm refusal and preservation
- [x] 7.7 Verify the committed-but-unpushed guard: commit, exit, confirm refusal and that the commit is listed
- [x] 7.8 Verify invocation from a subdirectory places the worktree at the main worktree root
- [x] 7.9 Verify nesting refusal by invoking the tool from inside an existing `pr-<N>` worktree

## 8. Follow-ups (not part of this change)

- [x] 8.1 Record a note to migrate to `gh pr checkout --worktree` once it ships in a released `gh`, replacing the cd-into-worktree workaround
- [x] 8.2 Record separately that `~/.gitconfig` sets `remote.pushdefault = hammerstefan`, which breaks pushes in repositories lacking that remote and should be fixed independently of this change
