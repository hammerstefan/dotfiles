# ses_e2a7aa3f1ffex7dayPUPZuI1kz: HWT workshop exploration

Session ran in the main checkout `/home/stefan.hammer@canonical.com/git/monitor-agent` on 13 November 2026. Messages are numbered U1 to U3 below.

## What the person asked for

- U1: the `hwt` skill invocation with the ask "@onboard-workshop explore creating a workshop for the development  of this project".
- U2: "why did that not set a goal?"
- U3: the same `hwt` skill invocation again, with the same ask.

## What was produced, and whether it worked

- `wayfinder` work was not involved. The session spawned one child session, `ses_e2a79290dffeekXpV7absQgR8u`, on branch `spike/development-workshop` at `/home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/spike-development-workshop`, base `7451cc7`.
- The prompt file `/tmp/opencode/hwt-prompt-development-workshop.md` held the ask, the why, the repository state, five rules (no `adr/` on the branch, no edits outside `spike/development-workshop/`, no touch of `agent/`, `plane/`, `justfile`, `monitor_agent/`, `tests/` or `fence/`, ask before any `lxc` or `workshop` command that creates host state) and a "Done when" line.
- The goal was written to `/tmp/opencode/hwt-goal-development-workshop.md` after the spawn, and set on the child session out of band.
- The child session committed `164eae2` `docs: propose the development workshop` with `spike/development-workshop/README.md` and verdict PARTIAL. The reviewer judged the goal met.
- **Verified:** the goal landed, the objective names three headings and one verdict word, the checkout was clean, and the commit changed only that README.
- **Not verified:** the goal store was read indirectly. The agent found the objective by querying the session's messages with `metadata.source=="goal"` and by searching `opencode.db`, and the two calls it used are not documented anywhere.

## Corrections the person made

- U2 rejected a spawn that set no goal: "why did that not set a goal?". The agent's answer opened "The goal was missing because of how I spawned it, not because anything failed. My `hwt` call passed only `--task-file`."

## Conventions, commands and values stated and written down nowhere

- The recovery call, in the agent's words: "`hwt` refuses a second spawn while the checkout exists, so I set the goal on the session it already created (`ses_e2a79290dffeekXpV7absQgR8u`) with the same call hwt makes (`opencode api session.command` with `name: goal`)."
- "The goal store holds one goal, id `6e08a177`, with that objective". Then "the second call replaced the first rather than adding a second objective."
- The objective text: "`spike/development-workshop/README.md` exists in the checkout with the headings `Question`, `Verdict`, and `How to run`, its Verdict section contains exactly one of `FULL`, `PARTIAL`, or `INFEASIBLE`, the work is committed on `spike/development-workshop`, and `git status --porcelain` in the checkout prints nothing."
- The agent's claim about skill freshness: "The skill I loaded at spawn time had no goal step", while the text the person reloaded at U3 has one.

## Failures, their cause, and the fix

- `!! FAILED shell` with `Portable shell scanner cannot analyze command: unterminated-quote`. The command was one line that put `opencode session export "$OPENCODE_SESSION_ID" | jq -r '...'` inside a `$(...)` and then passed the result to `hwt`. Fix: it ran the export and `jq` as their own command, read the value, and pasted it into the `hwt` call.
- `!! FAILED shell` on `grep -ril "goal" /home/stefan.hammer@canonical.com/git/dotfiles/`. The person interrupted it. No fix was needed. The goal search continued in `~/.config/opencode` and `~/.local/share/opencode` instead.
- `!! FAILED read` with `Tool execution interrupted`. The path is not in the flattened log, and the transcript states no cause.
- The spawn set no goal. Cause, per the agent: the goal cannot be written into the prompt file, and the `hwt` version it loaded had no goal step. The fix was the out-of-band call above, and the person's U3 reloaded the skill before the second report.

## Candidate lessons

- NEW. "`hwt` refuses a second spawn while the checkout exists, so I set the goal on the session it already created (`ses_e2a79290dffeekXpV7absQgR8u`) with the same call hwt makes (`opencode api session.command` with `name: goal`)." Reply to U2. The `hwt` skill says the goal is set through `/goal` on the session hwt creates, and that hwt refuses a second spawn. It gives no recovery for a session that already exists without a goal.
- NEW. "the second call replaced the first rather than adding a second objective." Reply to U2. Sending the goal twice is safe, so a call whose output was empty can be repeated. The agent sent it twice for that reason.
- NEW. `!! FAILED shell` with `Portable shell scanner cannot analyze command: unterminated-quote`. Tool log, before the first `hwt` dry run. A command that nests a quoted `jq` expression inside `$(...)` is refused before it runs. Run the export alone and paste the value.
- NEW. "The skill I loaded at spawn time had no goal step" and "the version you just reloaded does". Reply to U2. The agent's claim, not verified against the loader. If it holds, a spawn made with a stale skill text produces a session with the old behaviour and nothing reports it.
- ALREADY WRITTEN. A prompt that starts with `/goal` is read as prose and sets nothing. The `hwt` skill: "It cannot be written into the prompt file: a prompt that starts with `/goal` is read as prose by the model, not dispatched as a command."
- ALREADY WRITTEN. That a goal pauses when a session stops without asking, does not survive an OpenCode server restart, and is read and resumed with `/goal` and `/goal resume`. The `hwt` skill, near its report section.
- ALREADY WRITTEN. The checkout path is read from the dry run and not built from the branch name. The `hwt` skill: "Read the dry run: it prints the repository, the checkout, the session, the goal, and the exact `space.new` argv." The agent met this in the tool log, where it first wrote `spike/development-workshop` as the checkout and then edited the prompt to `spike-development-workshop`.

## What should not become a skill

- The instance identifiers of the goal store and its table names. They are internals that the next OpenCode release may change, and the `/goal` command is the documented surface.
- The interrupted `grep` over the dotfiles repository. The person stopped it, and it taught nothing about the task.
- The claim that a skill's loaded text goes stale. It is the agent's inference from one reload, so it needs a measurement before it becomes guidance.
