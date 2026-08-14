# github-pr-worktree Specification

## Purpose

Provide a `get_pr` command-line tool that creates an isolated git worktree
review environment for a GitHub pull request, drops the reviewer into an
interactive subshell configured to push back to the pull request's head
branch, and tears the environment down safely when the reviewer exits.

## Requirements

### Requirement: Command-line interface

The tool SHALL be named `get_pr` and SHALL accept exactly one positional
argument identifying a GitHub pull request, given either as a bare pull
request number or as a full pull request URL.

The tool SHALL reject an invocation supplying no argument, and SHALL reject an
invocation supplying more than one argument.

The tool SHALL resolve the argument by invoking `gh pr view <arg> --json
number,headRefOid,state` rather than parsing the argument itself, so that both
argument forms reduce to a pull request number before any further work.

The tool SHALL NOT attempt to authenticate to GitHub. If `gh` is not
authenticated, the tool SHALL exit non-zero and report that fact.

#### Scenario: Numeric invocation

- **WHEN** the tool is invoked as `get_pr 42` from within the repository that
  hosts pull request 42
- **THEN** it resolves pull request 42
- **AND** proceeds to create the review environment

#### Scenario: URL invocation is equivalent

- **WHEN** the tool is invoked with the full URL of pull request 42 from within
  the repository that hosts it
- **THEN** the resulting review environment is identical to the numeric form

#### Scenario: No argument

- **WHEN** the tool is invoked with no argument
- **THEN** it exits non-zero with a usage message
- **AND** creates no worktree, branch, or configuration

#### Scenario: gh not authenticated

- **WHEN** `gh` is not authenticated
- **THEN** the tool exits non-zero reporting that authentication is required
- **AND** does not prompt for or initiate authentication

### Requirement: Invocation context guards

The tool SHALL verify its execution context before mutating any state, and
SHALL fail loudly rather than proceed on a mismatch.

The tool SHALL refuse to run when the current directory is not inside a git
repository.

The tool SHALL refuse to run when the current directory is inside a linked
worktree rather than the main worktree.

When the argument is a URL, the tool SHALL compare the `owner/repo` named by
the URL against the value of `gh repo view --json nameWithOwner` for the
current repository, and SHALL refuse to proceed when they differ.

The tool SHALL treat the case where the current directory is a fork of the
pull request's repository as a match, because `gh` resolves the base repository
to the upstream.

All guards SHALL be evaluated before the tool creates a worktree, branch, or
configuration entry.

#### Scenario: Not in a git repository

- **WHEN** the tool is invoked from a directory outside any git repository
- **THEN** it exits non-zero reporting that it must be run inside a repository

#### Scenario: Invoked from a linked worktree

- **WHEN** the tool is invoked from within an existing `pr-<N>` worktree
- **THEN** it exits non-zero refusing to nest review environments
- **AND** creates no worktree

#### Scenario: URL names a different repository

- **WHEN** the tool is invoked with a pull request URL whose `owner/repo` does
  not match the current repository
- **THEN** it exits non-zero reporting the mismatch, naming both repositories
- **AND** creates no worktree

#### Scenario: Invoked from a fork of the pull request's repository

- **WHEN** the tool is invoked from a local clone of a fork, with a pull
  request belonging to the upstream repository
- **THEN** the repository guard passes
- **AND** the review environment is created normally

### Requirement: Worktree creation

The tool SHALL create a git worktree for the pull request at the path
`pr-<N>` relative to the **main** worktree root, where `<N>` is the resolved
pull request number.

The tool SHALL resolve the worktree path against the main worktree root rather
than the current working directory, so that invoking from a subdirectory places
the worktree consistently.

The tool SHALL ensure the pattern `/pr-*/` is present in the repository's
`.git/info/exclude`, adding it if absent and leaving it unchanged if already
present.

The tool SHALL check out the pull request head into that worktree by invoking
`gh pr checkout <N> -b pr-<N>` with the worktree as the current directory,
delegating fetch, remote resolution, fork handling, and push configuration
to `gh`.

The tool SHALL record the pull request's `headRefOid`, as reported at setup
time, for later use by the teardown guards.

The tool SHALL NOT create a named git remote for the pull request.

The tool SHALL NOT provision the worktree for execution, and specifically SHALL
NOT create virtual environments, install dependencies, or copy environment
files into it.

#### Scenario: Worktree receives the pull request head

- **WHEN** the review environment is created for pull request `<N>` with head
  commit `<oid>`
- **THEN** `git -C pr-<N> rev-parse HEAD` equals `<oid>`
- **AND** the main worktree's `HEAD` is unchanged

#### Scenario: Fork pull request

- **WHEN** the pull request originates from a fork
- **THEN** the worktree still receives the pull request head
- **AND** `git remote -v` lists no remote that was not present beforehand

#### Scenario: Local branch is renamed

- **WHEN** the pull request's head branch is named `main`, and a local branch
  named `main` already exists
- **THEN** the checked-out local branch is named `pr-<N>`
- **AND** the existing local `main` branch is unmodified

#### Scenario: Nested worktree is excluded from git and search tooling

- **WHEN** the worktree has been created
- **THEN** `git status` in the main worktree does not list `pr-<N>` as
  untracked
- **AND** `.git/info/exclude` contains exactly one `/pr-*/` line, even after
  repeated invocations

#### Scenario: Invoked from a subdirectory

- **WHEN** the tool is invoked from a subdirectory of the main worktree
- **THEN** the worktree is created at `pr-<N>` under the main worktree root,
  not under the subdirectory

#### Scenario: Closed or merged pull request

- **WHEN** the resolved pull request is closed or merged
- **THEN** the tool emits a warning naming the state
- **AND** still creates the review environment

### Requirement: Review subshell

The tool SHALL start an interactive bash subshell whose working directory is
the pull request worktree, and SHALL block until that subshell exits.

The subshell SHALL source the user's normal shell initialisation before
changing directory, so the reviewer's usual environment is preserved.

The subshell SHALL export environment-scoped git configuration setting
`push.default` to `upstream` and `remote.pushdefault` to the value of
`branch.pr-<N>.remote`, using git's `GIT_CONFIG_COUNT` / `GIT_CONFIG_KEY_<i>` /
`GIT_CONFIG_VALUE_<i>` mechanism.

The tool SHALL NOT write `push.default` or `remote.pushdefault` into any git
configuration file, at any scope.

The tool SHALL NOT define review helper commands, aliases, or functions beyond
the configuration described above.

#### Scenario: Plain push reaches the contributor's branch

- **WHEN** the reviewer commits a change inside the subshell and runs
  `git push` with no arguments
- **THEN** the commit is pushed to the pull request's head branch on the head
  repository
- **AND** no branch named `pr-<N>` is created on the remote

#### Scenario: Global push misconfiguration is neutralised

- **WHEN** the user's global configuration sets `remote.pushdefault` to a
  remote name absent from the repository
- **THEN** `git push` inside the subshell still targets the pull request's head
  repository

#### Scenario: No configuration residue

- **WHEN** the subshell has exited
- **THEN** neither `push.default` nor `remote.pushdefault` is set in the
  repository's local configuration

### Requirement: Teardown

The tool SHALL attempt teardown when, and only when, the review subshell
exits.

Teardown SHALL consist of removing the `pr-<N>` worktree and deleting the local
`pr-<N>` branch.

The tool SHALL NOT delete any git remote during teardown.

The tool SHALL refuse teardown, leaving the worktree and branch intact, when
the worktree's `HEAD` differs from the pull request's head commit. In that case
it SHALL report the divergence and list the offending commits using
`git log <head-oid>..HEAD --oneline`.

To avoid refusing teardown for work the reviewer has already pushed, the tool
SHALL re-query the pull request's current `headRefOid` at teardown time, and
SHALL compare the worktree's `HEAD` against that value. The `headRefOid`
recorded at setup SHALL be used as a fallback only when the re-query fails,
in which case the tool SHALL note that it is comparing against a possibly
stale value.

The tool SHALL detect divergence by comparing commit object IDs and SHALL NOT
rely on `@{upstream}`, which may not resolve for cross-repository pull
requests.

The tool SHALL surface, rather than suppress or override, `git worktree
remove`'s own refusal to delete a worktree containing modified or untracked
files, and SHALL NOT pass `--force`.

#### Scenario: Clean teardown

- **WHEN** the reviewer exits the subshell without modifying the worktree
- **THEN** the `pr-<N>` worktree is removed
- **AND** the local `pr-<N>` branch is deleted
- **AND** no `branch.pr-<N>.*` configuration keys remain
- **AND** the set of git remotes is identical to before the tool ran

#### Scenario: Uncommitted changes block teardown

- **WHEN** the reviewer exits the subshell with modified or untracked files in
  the worktree
- **THEN** teardown fails and reports git's refusal message
- **AND** the worktree and its contents are preserved

#### Scenario: Committed but unpushed work blocks teardown

- **WHEN** the reviewer commits a change inside the worktree and exits the
  subshell without pushing
- **THEN** teardown is refused
- **AND** the offending commits are listed
- **AND** the worktree and the `pr-<N>` branch are preserved

#### Scenario: Pushed work does not block teardown

- **WHEN** the reviewer commits a change inside the worktree and pushes it, so
  that the pull request head now equals the worktree `HEAD`
- **THEN** the teardown re-query observes the updated head
- **AND** teardown proceeds normally

#### Scenario: Head re-query fails

- **WHEN** the pull request's current head cannot be retrieved at teardown time
- **THEN** the tool compares against the `headRefOid` recorded at setup
- **AND** reports that the comparison may be stale before refusing or
  proceeding
