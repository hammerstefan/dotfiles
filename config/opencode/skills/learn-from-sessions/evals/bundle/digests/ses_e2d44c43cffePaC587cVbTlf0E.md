# ses_e2d44c43cffePaC587cVbTlf0E: Code review prompt for branch diff

## What the person asked for

- The dictated review prompt, sent in message 1 (1794536868520) with one input
  line: "Input: this branch". The prompt is quoted in full under "Conventions,
  commands and values stated and written down nowhere". It is the same 100
  lines the person sent in `ses_e2ed9abfeffeVfzkMZKrqss0P1`.
- "handle the two minors" (message 2, 1794537447018).

## What was produced, and whether it worked

- A review of branch `wayfinder/plane-workshop` against `main`, printed in the
  session as "# Review: `wayfinder/plane-workshop` vs `main`". Scope as
  reported: "one commit (`973f8c7 build: build the plane workshop`), 6 files,
  +173/−4".
- Verdict as reported: "**Verdict: no bugs found.**" plus two minor notes.
- What the agent checked against the upstream Workshop documentation, in its
  words: `setup-base` "runs as root before the project mount, once per install
  and again on revision change", `setup-project` "runs as the `workshop` user
  in `/project/`", and `check-health` "runs as root after `setup-project`, has
  five seconds, reports via `workshopctl set-health`".
- Two probes it ran on the host rather than reason about:
  - the cleanup trap with an empty operand: "I tested this: GNU `rm` exits 0
    silently on the empty operand, so the trap is safe on the Ubuntu 24.04
    base".
  - the version extraction against the committed pin: "I ran the
    version-extraction `sed` against the pinned name: `0.56.0` → tag
    `v0.56.0`".
- The two minors it reported: the `sed` version extraction passes garbage
  through when the pin line does not match, and the token file exists at the
  ambient umask for a moment before `chmod 0600`.
- After "handle the two minors" the agent edited
  `plane/.workshop/iron-proxy/hooks/setup-base` twice and re-checked each one:
  "The guard, against three pin shapes: a wrong archive name
  (`not-an-archive.zip`) and an empty pin both log `the pin does not name a
  release archive: ...` and exit 1" and "The install idiom: `install
  --mode=0600 /dev/null` creates the file at 0600, the redirect preserves the
  mode, and a re-run over a pre-existing 0644 file tightens it back to 0600."
- Not committed. The agent's words: "The changes are in the working tree for
  you to commit."
- Verified against the current repository: both fixes are in the hook.
  `plane/.workshop/iron-proxy/hooks/setup-base:43-45` logs "the pin does not
  name a release archive: ${archive}" and exits 1, and `:64-65` writes the
  token with `install --mode=0600 --owner=root --group=root /dev/null
  "${token_file}"` followed by the redirect.
- No GitHub activity in this session, and no test run. Nothing in the
  transcript shows the hook executed inside a workshop.

## Corrections the person made

(none found). "handle the two minors" extends the scope of the agent's own
report. The agent had asked no question before it.

## Conventions, commands and values stated and written down nowhere

The dictated prompt, quoted verbatim with its own punctuation:

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

Values the session fixed, which no file states:

- The pin line shape the hook relies on: digest, two spaces, then the file
  name. The agent's words: "the pin line is digest + two spaces + filename,
  valid `sha256sum -c` input".
- The token variable name `IRON_MANAGEMENT_API_KEY` and the reload target
  `127.0.0.1:9092/v1/reload`. Both are in the policy and the plan of the
  agent's report, and `IRON_MANAGEMENT_API_KEY` is in the hook and the unit.
- The agent's claim about action bodies, which it verified in the upstream
  documentation: "upstream runs action bodies as bash with `errexit` and
  `pipefail` already set, so the explicit `set -euo pipefail` is redundant but
  harmless".
- The agent's claim about the status tokens: "the documented status tokens are
  exactly `okay` and `error`".

## Failures, their cause, and the fix

1. `!! FAILED webfetch` on
   `https://raw.githubusercontent.com/canonical/workshop/main/docs/explanation/sdks/sdks.rst`:
   "StatusCode: non 2xx status code (404 GET .../docs/explanation/sdks/sdks.rst)".
   Cause: the file name was guessed from the page subject. Fix: the agent listed
   the directory with `https://api.github.com/repos/canonical/workshop/contents/docs/explanation/sdks`
   and fetched the real files, `concepts.rst` and `runtime-hooks.rst`.
2. A first attempt to run the extracted `sed` against a bare string gave a
   result the agent did not accept, and it re-ran it as a `bash -c` block with
   the pin's `awk` step included. The transcript shows both runs and no error
   text for the first.
3. The `install --owner=root` check could not run as the agent's own user. Its
   words: "(`--owner=root` was dropped for the local test only; the hook runs as
   root in the container, where it applies.)"

## Candidate lessons

- NEW: the dictated review prompt, as quoted above. No file in the repository
  states a review method.
- NEW: list an upstream documentation directory through the GitHub contents API
  before fetching a page by guessed path. Quote: "StatusCode: non 2xx status
  code (404 GET https://raw.githubusercontent.com/canonical/workshop/main/docs/explanation/sdks/sdks.rst)"
  (tool log, message 1). The working route in the same log is
  `webfetch https://api.github.com/repos/canonical/workshop/contents/docs/explanation/sdks`.
- NEW: a shell guard is verified with the input that must fail it, on the host.
  Quote: "The guard, against three pin shapes: a wrong archive name
  (`not-an-archive.zip`) and an empty pin both log ... and exit 1" (message 2
  reply).
- NEW: a secret file is created at 0600 by `install --mode=0600` before the
  redirect, because a redirect creates the file at the ambient umask. Quote:
  "`printf ... > "${token_file}"` creates the file at the ambient umask (0644)
  a moment before `chmod 0600`" (message 1 reply). `.kb/project.md` §1 states
  that a credential is never committed, and it says nothing about file modes.
- ALREADY WRITTEN: an unmatched `sed -E` line passes through, so a value taken
  from `sed` needs a pass-through check. The hook now states it at
  `plane/.workshop/iron-proxy/hooks/setup-base:40-45` ("An unmatched sed line
  passes through, so this holds only when the pin names no release archive.").
- PROJECT-SPECIFIC FACT: `check-health` runs as root, so a `test -r` there
  checks existence. The agent's words: "`test -r` runs as root there, so it
  effectively checks existence, not readability." The fact belongs in
  `.kb/agent-workshop.md` or a record.
- PROJECT-SPECIFIC FACT: the `check-health` window is five seconds and its
  tokens are `okay` and `error`. Agent claim from upstream documentation.
- PROJECT-SPECIFIC FACT: an SDK file change moves the SDK revision, so the next
  `refresh` reruns `setup-base` and issues a new token. The agent's words: "the
  change touches an SDK file, so it changes the SDK revision, and the next
  `refresh` reruns `setup-base`". This is already in ADR 0006 and
  `.kb/agent-workshop.md`.
- NEW: a value that three files must agree on is checked in all three before
  anything is flagged. Quote: "`IRON_MANAGEMENT_API_KEY` matches in
  `setup-base:59`, the unit's `EnvironmentFile` var, and the policy's
  `management.api_key_env`" (message 1 reply). No file states the check.

## What should not become a skill

- The two hook fixes. They are in the file, with the reason in a comment.
- The list of fields ADR 0006 fixes for `plane.yaml`. The record holds them.
- "No ADR change is needed". That is one decision about one edit.
- The `rm -rf ""` result as a general rule. It holds for GNU `rm` on this base
  image, and the agent measured it once.
