## 1. Implementation

- [x] 1.1 In `get_pr` `build_init_file`: export `GET_PR_SUBSHELL` with the
      review branch name (`pr-<N>`) in the generated init file
- [x] 1.2 In `build_init_file`: after the `. "$HOME/.bashrc"` source and the
      `cd`, prepend the plain-text marker `(pr-<N>)` to `PS1` (escape the
      inner `\$PS1` expansion; expand `pr_number` at generation time; no
      ANSI escapes)

## 2. Verification

- [x] 2.1 Run `bash -n get_pr` (syntax) and inspect the generated init file
      (`build_init_file` output) to confirm ordering: source bashrc → env
      exports → cd → PS1 prepend
- [x] 2.2 End-to-end test (synthetic repo with shimmed `gh`): ran `get_pr 42`
      and confirmed the prompt shows `(pr-42)` followed by the normal user
      prompt, `GET_PR_SUBSHELL` prints `pr-42`, and exit tears down the
      worktree
- [x] 2.3 Verify `shellcheck get_pr` (if available) reports no new warnings
      (shellcheck not installed; `bash -n` clean)
