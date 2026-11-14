# ses_e2a79290dffeekXpV7absQgR8u: Development workshop feasibility spike

One handoff message opens the session. It is the only USER turn. The session
is a spike that the repository later concluded. Its findings record on `main`
is `research/development-workshop.md`.

## What the person asked for

- "You are starting work in a fresh git worktree." USER 1 (line 5)
- "@onboard-workshop explore creating a workshop for the development of this project" USER 1 (line 12)
- "whether the development loop of this repository can run inside a Workshop" USER 1 (line 18)
- "This is an exploration, not a delivered definition." USER 1 (line 22)
- "Deliver the feasibility verdict (FULL / PARTIAL / INFEASIBLE) before writing any file." USER 1 (line 69)
- "Never drop a detected need to make the proposal look complete." USER 1 (line 76)
- "Stop after the proposal. Do not generate a `.workshop/*.yaml` or an in-project SDK unless the person approves generation." USER 1 (line 80)
- "Every question you ask the person carries a recommendation, with the evidence behind it. Batch the questions into one message." USER 1 (line 97)
- "Commit on `spike/development-workshop`. Do not push, merge, rebase, or touch `main` or any other branch." USER 1 (line 100)
- "Finish with: what you did, what you found, what you did not verify, and what you need from the person." USER 1 (line 116)

## What was produced, and whether it worked

- One commit, `164eae2`, subject "docs: propose the development workshop", on branch `spike/development-workshop`.
- One file changed, `spike/development-workshop/README.md`, 220 lines.
- The verdict is PARTIAL. The build and test loop maps to the `uv` and `just` Store SDKs. The fence command and the plane policy reload do not map.

Verified, from the agent's tool log:

- `git status --porcelain` is empty after the commit.
- `git branch --show-current` answers `spike/development-workshop`.
- `git diff --name-only 7451cc7..HEAD` answers only `spike/development-workshop/README.md`.
- The README holds the `Question`, `Verdict`, and `How to run` headings.
- The `Verdict` section holds one `PARTIAL` token.

Not verified:

- No action ran in a Workshop. "No action ran in a Workshop. Every "Covered" row is an envelope mapping, not a launch." (line 167)
- "`uv` 0.13.7 reads the revision 3 `uv.lock` written by host `uv` 0.9.26. Untested inside a Workshop." (line 168)
- "`just` 1.51.0 runs this `justfile`. Untested under that version." (line 169)
- "`uv sync` reaches PyPI from inside the development Workshop." (line 170)
- "The `mount` plug and the `workshop remount` were not exercised." (line 171)

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

(none found)

The handoff restates the repository laws and the `onboard-workshop` skill's
principles. The verdict-before-files rule, the honesty gate, the question
batching rule, and the `sdk find` / `sdk info` lookup rule all come from
`~/.agents/skills/onboard-workshop/SKILL.md`. The spike rules come from
`.kb/spikes.md`. The fence rule comes from `.kb/fence.md`.

## Failures, their cause, and the fix

Three shell commands aborted with the same error.

- `lsb_release -ds 2>/dev/null; apt-cache policy just 2>&1 | head -8` (line 221)
- `git log --oneline -5; echo '---'; git status --short; echo '---'; ls spike 2>&1` (line 223)
- `grep -rn 'pytest|hypothesis' pyproject.toml uv.lock | head; echo '---'; grep -c '' tests/*.py | tail -12` (line 225)

The error was `{"type":"aborted","message":"Interaction cancelled because the location shut down"}`.

The cause was the worktree location shutting down mid-run. It was a harness
interruption, not a command error.

The fix was to re-run the command. The first two commands were re-run and
succeeded (lines 227 and 228). The third was not re-run. Its information was
already present from the earlier read of `pyproject.toml` (line 188).

## Candidate lessons

- "Deliver the feasibility verdict (FULL / PARTIAL / INFEASIBLE) before writing any file." USER 1 (line 69). ALREADY WRITTEN. `AGENTS.md`, "Workshop definitions" section, and `~/.agents/skills/onboard-workshop/SKILL.md`, principle 1.
- "Never drop a detected need to make the proposal look complete." USER 1 (line 76). ALREADY WRITTEN. `~/.agents/skills/onboard-workshop/SKILL.md`, principle 1, honesty gate.
- "Every question you ask the person carries a recommendation, with the evidence behind it. Batch the questions into one message." USER 1 (line 97). ALREADY WRITTEN. `~/.agents/skills/onboard-workshop/SKILL.md`, principle 3.
- "The tests need no LXD and no Workshop, because the fakes replace the host commands." (line 160). ALREADY WRITTEN. `.kb/project.md`, Testing section.
- "The fence command needs the host `lxc` and the host LXD state. A container has no LXD socket." (line 161). ALREADY WRITTEN. `AGENTS.md`, "Never pass the host LXD socket into a workshop", and `.kb/fence.md` §1.
- "`just policy-reload` needs the host `workshop` command and the plane instance." (line 162). ALREADY WRITTEN. `.kb/fence.md`, the justfile concept.
- "A definition in the spike directory gets `/project` = the spike directory, not the repository root." (line 163). ALREADY WRITTEN. `AGENTS.md`, Workshop definition rules, and `research/development-workshop.md`.
- "The `uv` Store SDK is live and Canonical-published for `ubuntu@24.04`." (line 158) and "The `just` Store SDK is live at 1.51.0 for base `all`, published by Luca Bello." (line 159). PROJECT-SPECIFIC FACT. Store catalog state that changes. The third-party publisher and the 1.51.0 version are already in `research/development-workshop.md`.
- Confirm a Store SDK with `sdk find <keyword>` then `sdk info <name>` before writing its name into a definition. Tool log (lines 212 to 215). ALREADY WRITTEN. `~/.agents/skills/onboard-workshop/SKILL.md`, principle 2, and `workflows/propose-plan.md`.

## What should not become a skill

- The Store SDK version numbers and publisher names (`uv` 0.13.7, host `uv` 0.9.26, `just` 1.51.0, "Luca Bello", base `all`). They are catalog state that changes. A research record holds them, not a skill.
- The "location shut down" abort and its retry. It is a harness interruption, not repository knowledge.
- The fence gap and the plane policy reload gap. They are already laws in `.kb/fence.md` §1 and `AGENTS.md`. A skill would repeat them.
