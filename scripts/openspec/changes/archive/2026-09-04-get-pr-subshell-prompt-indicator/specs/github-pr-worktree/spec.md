## MODIFIED Requirements

### Requirement: Review subshell

The tool SHALL start an interactive bash subshell whose working directory is
the pull request worktree, and SHALL block until that subshell exits.

The subshell SHALL source the user's normal shell initialisation before
changing directory, so the reviewer's usual environment is preserved.

The subshell SHALL export an environment variable `GET_PR_SUBSHELL` whose
value is the review branch name (`pr-<N>`), identifying the shell as a
`get_pr` review subshell.

After sourcing the user's shell initialisation, the subshell SHALL prepend a
plain-text marker of the form `(pr-<N>)` to the prompt string (`PS1`), so
that every prompt identifies the shell as a review subshell for pull request
`<N>` while preserving the remainder of the user's own prompt.

The marker SHALL NOT contain ANSI escape sequences or other non-printing
control characters, so that it renders safely on dumb terminals.

The subshell SHALL export environment-scoped git configuration setting
`push.default` to `upstream` and `remote.pushdefault` to the value of
`branch.pr-<N>.remote`, using git's `GIT_CONFIG_COUNT` / `GIT_CONFIG_KEY_<i>` /
`GIT_CONFIG_VALUE_<i>` mechanism.

The tool SHALL NOT write `push.default` or `remote.pushdefault` into any git
configuration file, at any scope.

The tool SHALL NOT define review helper commands, aliases, or functions
beyond the configuration and prompt marker described above.

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

#### Scenario: Prompt identifies the review subshell

- **WHEN** the review subshell starts and the user's shell initialisation has
  been sourced
- **THEN** the first prompt displayed begins with the plain-text marker
  `(pr-<N>)` corresponding to the pull request under review
- **AND** the rest of the prompt matches the user's normal prompt (including
  any working-directory and git-branch segments)

#### Scenario: Review subshell is programmatically detectable

- **WHEN** the review subshell is running
- **THEN** the environment variable `GET_PR_SUBSHELL` is exported with the
  value `pr-<N>`
- **AND** sibling non-`get_pr` shells do not have `GET_PR_SUBSHELL` set
