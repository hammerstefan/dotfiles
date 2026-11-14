# ses_e2566d3e8ffeXoezjNVxLv37Je: Value of property tests for new code

## What the person asked for

- USER 1 (line 3): "evaluate value in adding property tests to the code added"
- USER 2 (line 58): "go"

## What was produced, and whether it worked

The agent measured whether property tests pay for the new control package.
It wrote throwaway probes under `/tmp/opencode/control-probe*.py` and changed
nothing in the tree until the person approved (line 5). Baseline: "183 passed
in 4.34 s" (line 5).

The verdict was five properties worth writing, each written from the module's
stated contract. Three of the five fail on the code as it stood, and each
failure is a real defect (line 9). Two hold behavior that was already correct
(line 86).

The agent landed three commits on branch
`wayfinder/fence-from-development-workshop`, pushed, and commented on PR #88
(line 82):

- `fix(control): refuse a result outside the record` (line 218)
- `fix(control): write a unit file systemd can read` (line 220)
- `test(control): hold the control invariants over generated input` (line 222)

Files changed: `monitor_agent/control/records.py`,
`monitor_agent/control/dev.py`, `tests/test_control.py`,
`tests/test_control_properties.py` (new), `.kb/control-service.md`,
`.kb/project.md`.

Verified, with the command that ran:

- The suite passes: `uv run pytest tests/ -q` (line 191, line 209, line 230).
- The style check passes: `check-writing-style.py .kb/control-service.md
  .kb/project.md` (line 209).
- The property file fails on the pre-fix code: the new test file copied into a
  throwaway worktree at HEAD reported fifteen failures, each naming a measured
  defect (line 98).
- The unit-file fix holds: `systemd-analyze verify` on the generated file
  reported the two faults before the fix and only the sandbox's missing
  `/usr/bin/uv` after it (line 105).

Not verified: the agent's summary says "`just test` passes" (line 111), but
the tool log shows `uv run pytest tests/ -q`, not the literal `just test`
recipe. The `justfile` `test` recipe runs `uv run pytest tests/`, so the two
name the same command.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

(none found)

## Failures, their cause, and the fix

Four `edit` calls failed with "Could not find oldString" in the file. Each
time the proposed text did not match the file text, and the fix was to read
the file region and re-apply with the exact text.

- The `checked` helper edit in `monitor_agent/control/dev.py` failed because
  the target text did not exist yet. The error named the closest lines, the
  `quote` helper at lines 71 through 76 (line 151). The agent read `dev.py`
  at offset 71 (line 152) and re-applied (line 153).
- The `_instances` test edit in `tests/test_control.py` failed because the
  new text was already in the file: "newString is already in the file, so this
  edit may already be applied" (line 159). The agent read `tests/test_control.py`
  at offset 560 (line 160) and continued.
- The `CONTROL_CHARACTERS` edit in `tests/test_control_properties.py` failed
  because the comment wording differed from the file's lines 85 through 88
  (line 174). The agent read the file at offset 83 (line 175) and re-applied
  (line 176).
- The `VALUES` edit in `tests/test_control_properties.py` failed because the
  file used a single-quoted alphabet string where the edit proposed a
  double-quoted one, at file lines 113 through 117 (line 199). The agent read
  the file at offset 112 (line 200) and re-applied (line 201).

## Candidate lessons

1. NEW. Write a property test's oracle from the module's stated contract, not
   from its behavior, so it fails on a defect instead of restating the code.
   Quote: "only if they are written from what the module *claims* rather than
   from what it *does*" (line 9). Message position: ASSISTANT, first reply.
2. NEW. Prove a new property test can fail by running it against the pre-fix
   code at HEAD in a throwaway worktree. Quote: "Now I prove the checks can
   fail: run the new property file against the pre-fix code (HEAD) in a
   throwaway worktree." (line 74). Message position: ASSISTANT.
3. NEW. Measure systemd unit-file spellings with `systemd-analyze verify`
   before writing the fix. `WorkingDirectory=` is written unquoted because
   systemd reads it as written and does not strip quotes. `Environment=` takes
   the whole assignment as one value. Quote: "`quote()` ... is correct for
   `ExecStart=` and wrong here, because systemd does not strip quotes on
   `WorkingDirectory=`." (line 24). Message position: ASSISTANT.
4. NEW. A unit file holds one directive per line, so a value holding a line
   break, a NUL, or an edge of whitespace is refused, not escaped. Quote:
   "`quote()` also never escapes a line break, so a root holding `\n` injects
   a directive into the file" (line 28). Message position: ASSISTANT.
5. PROJECT-SPECIFIC FACT. Every fence module with an invariant has a companion
   property file, and the new control package lacked one. Quote: "every fence
   module with an invariant has a companion" (line 11). Message position:
   ASSISTANT.
6. PROJECT-SPECIFIC FACT. Both records refuse an unknown field, an unknown
   verb, and a field of the wrong type. Quote: "Both records refuse an unknown
   field, an unknown verb, and a field of the wrong type" (line 30). Message
   position: ASSISTANT.
7. NEW. Commit each fix and the property file as separate commits, each
   passing on its own. Quote: "I'll commit the two fixes and the property file
   separately, each passing on its own." (line 78). Message position:
   ASSISTANT.

## What should not become a skill

- The four fixed defects: the result reader accepting an unknown field, the
  exit-code type coercion, the `lxc query` answer shape, and the unit-file
  quoting (lines 88 through 93). They are fixed in this session's commits, so
  a skill that names them teaches history, not practice.
- Property tests over `up`/`down` ordering, `parse_argv`, `audit_line`, and
  `write_json` atomicity. The ordering tests already assert the sequence with
  index comparisons, and the other three have an input space too small to
  generate anything the example tests do not name. Quote: "`audit_line`,
  `_status` parsing, `write_json` atomicity: input space too small or the
  invariant too weak to generate anything interesting." (line 46).
