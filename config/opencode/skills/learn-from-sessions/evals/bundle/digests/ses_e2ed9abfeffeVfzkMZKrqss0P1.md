# ses_e2ed9abfeffeVfzkMZKrqss0P1: Code review instructions

## What the person asked for

- The dictated review prompt, sent in message 1 (1794510332598) with one input
  line: "Input: this branch". The prompt is quoted in full under "Conventions,
  commands and values stated and written down nowhere".
- "apply the fixes includ minor" (message 2, 1794511217107). The spelling
  "includ" is the person's.

## What was produced, and whether it worked

The session ran in the worktree
`.../.herdr/worktrees/monitor-agent/wayfinder-proxy-egress-fence`, branch
`wayfinder/proxy-egress-fence-wrapper`.

- A review of that branch against `main`. The commands use the merge base
  `aab4d5065647a6bcf4aa57fbbefd1d0d599fc2d0`. The review is printed in the
  session only. No GitHub review comment was posted and no file records it.
- The agent found the working tree clean and resolved the base. Its words:
  "The working tree is clean, so this is a branch review."
- Findings as reported: two bugs and five minor items.
  - Bug 1: `yaml.safe_load` had no `YAMLError` guard at three parse sites, so a
    malformed definition gave a traceback. The agent ran
    `.venv/bin/monitor-agent-fence apply` in `/tmp/opencode/yamltest` with a
    syntax error in `fence/fence.yaml`, and the review states the result: "a
    `fence/fence.yaml` with a syntax error produces a full
    `yaml.parser.ParserError` traceback and **exit code 1**".
  - Bug 2: the `nic_device` docstring said that `lxc config device set` edits
    the merged device view. The agent checked the LXD rule by web search and
    wrote "LXD maintainers confirm: `config device set` only works on
    instance-owned devices". It then kept the finding at "Verify" because the
    repository does not show who creates the NIC. Its words: "I can't verify
    instance-vs-profile ownership from this repo, which I'll note as a
    question rather than a bug."
  - Minor: `AclRule.identity()` left `description` out, a `nictype: bridged`
    NIC with `parent:` passed `_check_foreign`, `remove` exits 2 after a
    successful removal, a section marker sat on a code line, and a definition
    without `agent.address` sent the string `"None"` to LXD.
- After "apply the fixes includ minor" the agent applied all seven items and
  reported "All 92 tests pass (84 original + 8 new)" and "The exit-code
  contract is restored: clean `fault:` message, exit 2." The transcript keeps
  no test output, so the count is the agent's claim.
- Verified against the current repository: the guards are in the tree.
  `monitor_agent/fence/config.py:117` and `:179` catch `(OSError,
  UnicodeDecodeError)`, `:121` and `:183` catch `yaml.YAMLError`, `cli.py:86`
  catches `(OSError, UnicodeDecodeError)` and `cli.py:92` catches
  `yaml.YAMLError`. `apply.py:177-203` states that the fence sets the address
  on the instance's own device and faults when the device comes only through a
  profile.
- Not committed in this session. The agent closed with "Changes are
  uncommitted — say the word and I'll write the commit messages."

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

The person dictated the review method as a prompt. It is 100 lines, it was
sent again word for word in `ses_e2d44c43cffePaC587cVbTlf0E`, and no file in
the repository states it. Quoted verbatim, with its own punctuation:

    You are a code reviewer. Your job is to review code changes and provide actionable feedback.

    ---

    Input: this branch

    ---

    ## Determining What to Review

    Based on the input provided, determine which type of review to perform:

    1. **No arguments (default)**: Review all uncommitted changes
       - Run: `git diff` for unstaged changes
       - Run: `git diff --cached` for staged changes
       - Run: `git status --short` to identify untracked (net new) files

    2. **Commit hash** (40-char SHA or short hash): Review that specific commit
       - Run: `git show this branch`

    3. **Branch name**: Compare current branch to the specified branch
       - Run: `git diff this branch...HEAD`

    4. **PR URL or number** (contains "github.com" or "pull" or looks like a PR number): Review the pull request
       - Run: `gh pr view this branch` to get PR context
       - Run: `gh pr diff this branch` to get the diff

    Use best judgement when processing input.

    ---

    ## Gathering Context

    **Diffs alone are not enough.** After getting the diff, read the entire file(s) being modified to understand the full context. Code that looks wrong in isolation may be correct given surrounding logic—and vice versa.

    - Use the diff to identify which files changed
    - Use `git status --short` to identify untracked files, then read their full contents
    - Read the full file to understand existing patterns, control flow, and error handling
    - Check for existing style guide or conventions files (CONVENTIONS.md, AGENTS.md, .editorconfig, etc.)

    ---

    ## What to Look For

    **Bugs** - Your primary focus.
    - Logic errors, off-by-one mistakes, incorrect conditionals
    - If-else guards: missing guards, incorrect branching, unreachable code paths
    - Edge cases: null/empty/undefined inputs, error conditions, race conditions
    - Security issues: injection, auth bypass, data exposure
    - Broken error handling that swallows failures, throws unexpectedly or returns error types that are not caught.

    **Structure** - Does the code fit the codebase?
    - Does it follow existing patterns and conventions?
    - Are there established abstractions it should use but doesn't?
    - Excessive nesting that could be flattened with early returns or extraction

    **Performance** - Only flag if obviously problematic.
    - O(n²) on unbounded data, N+1 queries, blocking I/O on hot paths

    **Behavior Changes** - If a behavioral change is introduced, raise it (especially if it's possibly unintentional).

    ---

    ## Before You Flag Something

    **Be certain.** If you're going to call something a bug, you need to be confident it actually is one.

    - Only review the changes - do not review pre-existing code that wasn't modified
    - Don't flag something as a bug if you're unsure - investigate first
    - Don't invent hypothetical problems - if an edge case matters, explain the realistic scenario where it breaks
    - If you need more context to be sure, use the tools below to get it

    **Don't be a zealot about style.** When checking code against conventions:

    - Verify the code is *actually* in violation. Don't complain about else statements if early returns are already being used correctly.
    - Some "violations" are acceptable when they're the simplest option. A `let` statement is fine if the alternative is convoluted.
    - Excessive nesting is a legitimate concern regardless of other style choices.

    ---

    ## Tools

    Use these to inform your review:

    - **Explore agent** - Find how existing code handles similar problems. Check patterns, conventions, and prior art before claiming something doesn't fit.
    - **Available documentation and code-search tools** - Verify correct usage of libraries/APIs before flagging something as wrong.
    - **Web Search** - Research best practices if you're unsure about a pattern.

    If you're uncertain about something and can't verify it with these tools, say "I'm not sure about X" rather than flagging it as a definite issue.

    ---

    ## Output

    1. If there is a bug, be direct and clear about why it is a bug.
    2. Clearly communicate severity of issues. Do not overstate severity.
    3. Critiques should clearly and explicitly communicate the scenarios, environments, or inputs that are necessary for the bug to arise. The comment should immediately indicate that the issue's severity depends on these factors.
    4. Your tone should be matter-of-fact and not accusatory or overly positive. It should read as a helpful AI assistant suggestion without sounding too much like a human reviewer.
    5. Write so the reader can quickly understand the issue without reading too closely.
    6. AVOID flattery, do not give any comments that are not helpful to the reader.

Two properties of the prompt explain the agent's first moves:

- The input line is substituted into command templates, so four commands read
  "`git show this branch`", "`git diff this branch...HEAD`", "`gh pr view this
  branch`" and "`gh pr diff this branch`". None of them runs as written. The
  prompt's own escape hatch is "Use best judgement when processing input."
- The prompt fixes no severity vocabulary. The agent invented "Moderate",
  "Low" and "Behavior note".

## Failures, their cause, and the fix

1. `read` returned mangled long lines, repeatedly. The agent's words: "The
   source files are all fine — the read tool was mangling long lines." and
   "The tool output is getting interleaved when concatenating files." Each
   suspect file was checked with `python3 -c` and an `ast.parse` call, then
   `sed -n` on the byte range. The harness defect stayed.
2. `!! FAILED edit` on `monitor_agent/fence/apply.py`: "Could not find
   oldString in monitor_agent/fence/apply.py. It must match exactly, including
   whitespace and indentation." Cause: the `oldString` was rebuilt from
   mangled read output. Fix: the error prints the closest current lines, and
   the agent retried with that text. Its words: "My oldString was mangled; the
   error shows the exact current text."
3. A second `edit` failed because the anchor text was remembered without the
   loop's indentation. Its words: "The indentation was off — the block sits
   deeper in the nested loop. Retrying with correct indentation:".
4. An `edit` call reached the file with a broken parameter, and the agent
   inspected the result before it continued. Its words: "Thatedit call was
   malformed — let me inspect the damage and fix it cleanly:".
5. The new identity tuples in `tests/test_apply.py` were wrong at first. The
   agent's words: "My expected tuples have an extra `None` — identity is 7
   fields (I duplicated the source slot)." Fix: drop the extra slot in the
   agent and plane expectations.

## Candidate lessons

- NEW: a documented exit-code contract needs every raise path mapped to it,
  because an uncaught Python exception exits 1, and 1 means something else
  here. Quote: "Confirmed: malformed YAML escapes the fault contract — raw
  traceback, exit 1 (which the docs define as "fence lost, agent stopped"),
  not the documented `fault:` + exit 2." (message 1 reply). The exit codes are
  in `.kb/fence.md` §Exit codes. The rule about exceptions is in no file.
- NEW: a docstring's claim about an upstream program is a claim to check
  against that program. Quote: "`nic_device` docstring misstates LXD
  semantics; a profile-provided NIC would fail to converge" (message 1 reply).
  The measured fact is in `research/acl-fence.md:42`.
- ALREADY WRITTEN: an identity that omits a field stops convergence for that
  field. The reason is in the `identity` docstring in
  `monitor_agent/fence/lxd.py`: "The description is part of the identity, so a
  rule whose description someone edited does not match the desired rule and
  gets rebuilt with the committed description."
- ALREADY WRITTEN: `remove` exits 2 after a successful removal by design.
  `.kb/fence.md` §The verbs states it.
- NEW: the review prompt's rule that a bug report names the input that
  triggers it. Quote: "Critiques should clearly and explicitly communicate the
  scenarios, environments, or inputs that are necessary for the bug to arise."
  (message 1).
- NEW: the review prompt's rule for uncertainty. Quote: "If you're uncertain
  about something and can't verify it with these tools, say "I'm not sure
  about X" rather than flagging it as a definite issue." (message 1).
- NEW: the review prompt's scope rule. Quote: "Only review the changes - do
  not review pre-existing code that wasn't modified" (message 1).
- NEW: the review prompt's context rule. Quote: "**Diffs alone are not
  enough.** After getting the diff, read the entire file(s) being modified to
  understand the full context." (message 1).
- NEW: the review prompt's tone rule, which `.kb/writing-style.md` does not
  cover. Quote: "AVOID flattery, do not give any comments that are not helpful
  to the reader." (message 1).
- NEW: the review prompt's pull-request route. Quote: "**PR URL or number**
  (contains "github.com" or "pull" or looks like a PR number): Review the pull
  request" with "Run: `gh pr view this branch`" and "Run: `gh pr diff this
  branch`" (message 1).
- PROJECT-SPECIFIC FACT: the three parse sites and the seven findings of this
  review. The code and `.kb/fence.md` hold them now.

## What should not become a skill

- The individual fence bugs. Six are fixed in the tree, and the seventh is
  documented in `.kb/fence.md`.
- The severity words "Moderate", "Low" and "Behavior note". The person never
  chose them.
- "The read tool mangles long lines". That is a defect of one harness in one
  session, and no rule prevents it.
- The `git merge-base HEAD origin/main` step on its own. It repairs a prompt
  line, and the repair belongs in the prompt.
