# ses_e2ea37a5bffeGYvmm3MCmT27yK: Hypothesis property testing in Wayfinder PRs

## What the person asked for

- "@wayfinder on the current stack of prs for this branch, I want to consider
  adding python hypothesis property tests. evaluate. should this be done as
  this current issue or added to the wayfinder map?" (message 1,
  1794513884508)
- "do any project or agent instructions need to be updated to include property
  tests?" (message 2, 1794514693648)

## What was produced, and whether it worked

The worktree is
`.../.herdr/worktrees/monitor-agent/wayfinder-proxy-egress-fence`, on the stack
#32 to #35 for issue #20.

- The answer to message 1: no map ticket, and a tests-only layer. The agent's
  words: "**Map: no.** The map resolves decisions and carries feature tickets
  through the requirements process." and "**Stack: yes, as its own tests-only
  PR (#36) on top of #35** — not stuffed into #35, which is in review."
- Branch `wayfinder/proxy-egress-fence-property`, three commits as reported:
  `build: add hypothesis to the test dependency group`, `fix: fault on a
  scalar fence section and unreadable config`, `test: property-test the fence
  with hypothesis`. PR #36 "Property-test the fence invariants with
  hypothesis", based on #35. The map body gained #36 in its stack index, and
  the agent added a trail entry.
- Three faults the agent probed before it wrote a test, as reported: a scalar
  `agent`, `plane`, `probes` or `probes.denied` section gives `AttributeError`,
  an operator config with non-UTF-8 bytes gives `UnicodeDecodeError`, and a
  `.workshop.lock` with non-UTF-8 bytes gives `UnicodeDecodeError`.
- One commit for message 2: `1bd03ac docs: state the test conventions in the
  project rules`, pushed to #36, and the PR body was patched afterwards. The
  agent's report: "Committed and pushed to PR #36 (commit `1bd03ac`), with the
  PR body noting the doc addition."
- Verified against the current repository: `pyproject.toml:14` reads
  `dev = ["pytest>=8", "hypothesis>=6"]`, `.gitignore` lists `.hypothesis/`,
  and `tests/` holds `test_apply_properties.py`, `test_cli_properties.py`,
  `test_config_properties.py`, `test_lxd_properties.py` and
  `test_release_properties.py`.
- Verified against the current repository: `.kb/project.md` holds a
  `## Testing` concept section. Its three bullets say that `just test` runs the
  suite in memory, that "The example tests hold one behavior each. The property
  tests with hypothesis hold the invariants over generated input", and that "A
  fake models the semantics of the surface it stands in for: a query returns a
  snapshot".
- Not verified: "104 tests", "Stable across four full-suite runs.", the state
  of PR #36, and the map edit. The transcript keeps no tool output.

## Corrections the person made

(none found). Both messages are questions. The person did not object to the
map-or-stack decision, to carrying three fixes in a tests-only layer, or to
writing the testing section as a repository-wide convention. The agent offered
an escape on each: "flag it in review if you'd rather they live in a separate
layer" and "If you'd rather keep it scoped to the fence work, say so and I'll
narrow the wording before #36 merges."

## Conventions, commands and values stated and written down nowhere

The person stated no option, path, flag or number in this session. Every value
below is the agent's, accepted by the person's silence:

- The branch name `wayfinder/proxy-egress-fence-property` and the PR title
  "Property-test the fence invariants with hypothesis".
- The dependency line `dev = ["pytest>=8", "hypothesis>=6"]`, and `uv lock`
  beside it. The agent's reason: "The property tests generate host states and
  input files, so the dev group needs hypothesis beside pytest."
- The three properties it chose to hold: convergence, reader robustness, and
  the exit-code mapping. Its words: "1. **`apply.py` convergence
  (FR-013/014/015)** — the best target. 2. **`config.py` parse robustness** ...
  3. **`cli.py` exit-code mapping (0/1/2)**".
- The placement rule for this kind of work. Its words: "This is test deepening
  of code that is unmerged *right now* — there is no open decision (the
  invariants to check are already committed in
  `requirements/002-proxy-egress-fence/requirements.md`), no fog, and it's not
  an architecture decision in the ADR sense."
- The rule that a tests-only layer holds the fixes it forces. Its words:
  "So the PR is not strictly tests-only: it carries these three small fixes,
  because a test suite that documents a crash as expected behavior isn't
  shippable."
- The rule that generated input needs a repeated run before a commit. Its
  words: "Stable across four full-suite runs." and "The CLI property also
  caught a bug in my own expected-code mapping (a nonzero verb code can't
  affect `apply`), which is why I ran the suite four times before committing."
- Which instruction files it left alone, and why, as its own claim:
  "**`.kb/agents.md`** — locked; must not be edited unless you explicitly
  request it." and "**Root `AGENTS.md`** — it's an index of `.kb` files."

## Failures, their cause, and the fix

1. `!! FAILED edit` on `tests/test_apply_properties.py`: "Could not find
   oldString in tests/test_apply_properties.py. It must match exactly,
   including whitespace and indentation." Cause: the anchor came from the text
   the agent had drafted, not from the file. Fix: `read` at the offset, then
   retry. It happened twice in the file.
2. The first fault-path property asserted the wrong thing. The agent's words:
   "One flaw in the fault tests I just wrote: the profile mutations pre-create
   the bridge, so "networks is empty" is the wrong assertion — the contract is
   "the run changes nothing", which needs a before/after state snapshot."
3. The convergence property failed on a snapshot taken in the wrong place. The
   agent's words: "Found it — my own test bug: I snapshot the state *before*
   the converging apply, then compare it after the second apply, so the
   legitimate first-pass changes look like a violation. The snapshot belongs
   between the two applies:"
4. The convergence property then found a defect in the fake. The agent's
   words: "This one's a genuine find — and it's in the fake, not the applier.
   The applier iterates the ACL's rule list while `FakeLxd.remove_acl_rule`
   mutates that same list, so each removal skips the next rule. Real LXD
   returns a snapshot on query; the fake hands out its live list." Fix:
   `FakeLxd.acl()` returns a deep copy.
5. A CLI property failed on the agent's expected code. The agent's words: "The
   property caught my own mapping error: a nonzero verb code only matters for
   lifecycle verbs — `apply` never runs a workshop command." Fix: pass the verb
   into `expected_code` and test `verb != "apply"`.
6. The denied-probe expectation was too narrow. The agent's words: "Two fixes
   in that file: the denied probe can also fault with "not running" (probe
   checks stderr generically), and there's a leftover empty try/finally."
7. The PR body edit failed. The agent's words: "The push landed; the PR-body
   edit hit a `gh` GraphQL quirk. Retrying via the API:". The retry in the log
   reads the body with `gh api repos/.../pulls/36 --jq .body` into a file,
   rewrites the one sentence with a Python `assert body.count(old) == 1`, and
   patches it back.

## Candidate lessons

- NEW: a choice between a map ticket and a stack layer for work on code that is
  under review. Quote: "This is test deepening of code that is unmerged *right
  now*" (message 1 reply). `.kb/spec-kit.md` states that a tests-only layer
  exists, and it does not state when to add one.
- NEW: a tests-only layer fixes the crash that its own tests prove. Quote: "a
  test suite that documents a crash as expected behavior isn't shippable"
  (message 1 reply).
- NEW: probe a fault path with a throwaway script before the property is
  written, so the test targets a real defect. Quote: "Before writing any test I
  probed the fault paths, and confirmed three inputs that crash with a
  traceback instead of the fault line and exit 2" (message 1 reply).
- NEW: run a property suite more than once before the commit, because each run
  draws different examples. Quote: "Stable across four full-suite runs."
  (message 1 reply).
- ALREADY WRITTEN: a fake returns a query snapshot.
  `.kb/project.md` §Testing, last bullet.
- ALREADY WRITTEN: the example tests hold one behavior each and the property
  tests hold the invariants. `.kb/project.md` §Testing, second bullet.
- ALREADY WRITTEN: the suite runs in memory through fakes and `just test`.
  `.kb/project.md` §Testing, first bullet, and the `test` recipe in `justfile`.
- ALREADY WRITTEN: `.kb/agents.md` is not edited unless the person asks.
  `.kb/agents.md` §3.
- NEW: a hostile `gh pr edit` body fails here, so the body is patched through
  `gh api -X PATCH repos/<owner>/<repo>/pulls/<n>`. Quote: "the PR-body edit
  hit a `gh` GraphQL quirk. Retrying via the API:" (message 1 reply). The full
  idiom is in the tool log of `ses_e2f2b2b00ffeXWdtibMXa55t80`: `jq -Rs
  '{body: .}' /tmp/body.md > /tmp/body.json && gh api -X PATCH
  repos/.../pulls/30 --input /tmp/body.json`.
- NEW: a scalar where a mapping belongs is an input class that example tests
  miss, and a reader that takes YAML must reject it. Quote: "a fence definition
  whose `agent`/`plane`/`probes`/`probes.denied` section is a scalar →
  `AttributeError`" (message 1 reply). The code now holds `_section` in
  `monitor_agent/fence/config.py`, and no file states the rule.
- PROJECT-SPECIFIC FACT: which three properties the fence needed, and the count
  104. The code holds the tests.

## What should not become a skill

- The four property test files and what each asserts. They are in `tests/`.
- `@settings(deadline=None)` and `max_examples=30`. They are in the test files,
  and the transcript states no reason for either.
- The map edit and the trail entry. They are bookkeeping for one ticket.
- "104 tests passed". `.kb/writing-style.md` §6 forbids quoting a test count.
