# ses_e34a81f46ffelegPGJEG3QLtLg: herdr hc worktree control

Session directory: `/home/stefan.hammer@canonical.com/git/monitor-agent`.
Every file this session wrote is in `~/git/dotfiles`. No file in the
monitor-agent checkout changed. Positions are `msg N` for a session message
and `flat:N` for the flattened transcript.

## What the person asked for

- "can you control herdr hc as an agent. e.g. create a new worktree?" (msg 1)
- "https://github.com/herdrdev/herdr-app/blob/master/defaults/AGENTS.md
  indicates there is worktree support as a mod, can that be handled from an
  agent?" (msg 13)
- "create the tiny helper" (msg 25)
- "can this open a worktree on an existing workspace?" (msg 74)
- "I don't want it opened as a new tab, I want it opened as a new worktree, the
  same way it does when I right click a space and select "new worktree""
  (msg 95)
- "--here does not seem to work. I run it in this current workspace
  (monitor-agent) and it creates a worktree under "herdr-plugins"" (msg 120)
- "can we instead go by the active terminal?" (msg 140)
- "why not always the terminal running hwt?" (msg 153)
- "make it default" (msg 161)
- "commit the changes you made" (msg 175)
- "create an openspec skill that uses hwt to create a new worktree with a
  opencode and a prompt generated from the user ask. example, "/hwt spike
  option 2" would cause the current session to create a new worktree in herdr
  (using hwt) w/ opencode and a prompt the describes fully what is needed to
  run that spike" (msg 188)
- "yes, commit" (msg 220)
- "fix  /tmp/opencode/handoff-hwt-wrong-repo.md" (msg 229)
- "next, have "/hwt" default to spawning opencode with the same model the
  session is currently running" (msg 235)

Two answers to one `question` call, visible only in the raw export (msg 195):
"Global `hwt` skill + `/hwt` command (Recommended)" and "Immediate, but ask only
when the ask is thin".

## What was produced, and whether it worked

Three commits in `~/git/dotfiles`, on `master`, none pushed. The agent reports
`master` 25 commits ahead of `origin/master` at the end (flat:372).

- `38cb469 feat(scripts): add hwt to open a worktree as a Herdr space`, one new
  file `scripts/hwt`, 315 lines, mode 100755 (flat:265-271).
- `1bc82b8 feat(scripts): read the agent task from a file in hwt`, which adds
  `--task-file` (flat:365-367).
- `01a77f7 feat(opencode): add the /hwt command and its skill`, which adds
  `config/opencode/skills/hwt/SKILL.md` and `config/opencode/commands/hwt.md`
  (flat:360-363).

Left uncommitted at the end: the `--model` change and the foreground-folder fix
in `scripts/hwt`, with the matching skill edit (flat:434-439).

The agent says it verified these in throwaway repositories: a new branch, an
existing branch, a bad base, a bad branch name, a nested run from a linked
worktree, the conflicting flag pairs (flat:100, flat:150), live spaces
including an `opencode --prompt` session that answered (flat:349), the repo
resolution against terminals `t1x`, `t2h`, `t30`, `t13` and with
`HC_TERMINAL_ID` unset (flat:418-428), and the model pin read back as
`{"id":"~deepseek/deepseek-flash-latest","providerID":"openrouter","variant":"high"}`
(flat:392-397). Each round ends with the spaces closed, the worktrees removed,
and focus back on `monitor-agent` (flat:100, flat:186, flat:257).

Not verified:

- whether a worktree space fired on the person's real use, which the agent says
  it asked twice (flat:310).
- the two empty directories `~/.herdr/worktrees/herdr-plugins/` and
  `~/.herdr/worktrees/monitor-agent/` from the broken run, which the person
  never answered about (flat:188, flat:217).
- the ask said "an openspec skill" (msg 188) and the delivery is a plain skill.
  The agent asked about the name and placement (msg 195) and later offered an
  OpenSpec change "like `get_pr` did" (flat:353), with no answer either time.

Read against the current files, read only: `~/git/dotfiles/scripts/hwt` now also
holds `--goal-file`, and `~/.config/opencode/skills/hwt/SKILL.md` now describes
a goal and a reviewer, which this session did not build.

## Corrections the person made

1. The agent had added `--space` and `--here` as tabs: "Herdr's "workspace" is
   a **space**, and the way to put a second checkout into one is a new *tab*
   (`tab.new --space <id> --folder <path>`), not a new space." (flat:108). The
   person answered: "I don't want it opened as a new tab, I want it opened as a
   new worktree, the same way it does when I right click a space and select
   "new worktree"" (msg 95). The agent accepted it: "I had the semantics
   backwards last round." (flat:133).
2. The agent reported a four-step rule from "the folder of **the terminal
   running `hwt`**" to "the folder the space was made in" (flat:163-169). The
   person reported "--here does not seem to work. I run it in this current
   workspace (monitor-agent) and it creates a worktree under "herdr-plugins""
   (msg 120).
3. The agent wrote "The rule now, first one that is actually inside a git
   repository wins:" (flat:163). The person quoted it and asked: "can we
   instead go by the active terminal?" (msg 140). The agent dropped the
   candidate chain (flat:193).
4. The agent then ordered "1. **Space on screen** → the pane with the keyboard
   ... 2. **Space not on screen** → the terminal running `hwt`"
   (flat:195-196). The person pasted those lines and asked: "why not always the
   terminal running hwt?" (msg 153). The agent swapped them (flat:223).
5. The agent offered to make the pane folder the default "then `--here`
   disappears entirely" (flat:240). The person answered "make it default"
   (msg 161), and `--here` was removed (flat:244).

## Conventions, commands and values stated and written down nowhere

The person's words:

- The UI action to reproduce, and the invocation shape, are quoted above
  (msg 95, msg 188).
- Permission to change the helper: "you are allowed to propose additions to the
  hwt script to support this, if needed" (msg 188).
- Where a tool that works in every repository keeps its skill: "Global `hwt`
  skill + `/hwt` command" (msg 195). How it treats a thin ask: "Immediate, but
  ask only when the ask is thin" (msg 195).
- Model inheritance: "have "/hwt" default to spawning opencode with the same
  model the session is currently running" (msg 235).
- A defect handed to another session as a file path: "fix
  /tmp/opencode/handoff-hwt-wrong-repo.md" (msg 229). That file states its own
  scope: "The work is one defect in `~/scripts/hwt`, not in this repository."
  (`/tmp/opencode/handoff-hwt-wrong-repo.md`:3-4).

Values the agent chose, none of them the person's, each in the file it names:

- Checkout at `~/.herdr/worktrees/<repo>/<slug(branch)>`, slashes turned into
  dashes, and the space left unnamed so the sidebar nests it under its repo and
  names it after the branch (flat:47, flat:141).
- Branch prefixes `spike/`, `fix/`, `feat/` (flat:340).
- `-n, --dry-run` prints the repository, the checkout, and the `space.new` argv
  (flat:172-179).
- Commit body lines at 70 columns or fewer, which the agent amended for
  (flat:370).

## Failures, their cause, and the fix

The flat tool log holds 273 `ok` lines and no `!! FAILED` line. The raw export
holds one failed tool call, because it ran inside `execute` and the flatten kept
only the wrapper:

1. `context7.query-docs` with library id `/sst/opencode` returned an error (raw
   export, msg 212). The same query with `/anomalyco/opencode` completed
   (msg 213). Cause: the wrong library id. Fix: the retry.

Failures in the agent's prose, with no failed tool call to show them:

2. "`herdr worktree create` (from the older `herdr` 0.9.5 multiplexer) is a
   *different* feature, and from here it fails with `not_git_worktree` because
   this terminal has no herdr pane/workspace context" (flat:63). Cause: no
   `HERDR_PANE_ID` or `HERDR_WORKSPACE_ID` in the session (flat:35). Fix: use
   `herdr-app`.
3. "`space.new --task` passes the text as an argument to the agent's own
   command line, so `--argv '["opencode"]' --task "…"` hands opencode the task
   as its *project folder* — it dies with `ENOENT: chdir …`" (flat:80). Cause:
   Herdr's semantics for `--task`. Fix: the helper builds the argv,
   `opencode --prompt <text>`.
4. The first version added tabs, not worktrees (flat:108). Cause: the agent read
   "workspace" as Herdr's space and reached for `tab.new`. Fix: correction 1,
   which the person made.
5. `--here` branched herdr-plugins. Cause the agent gives: the helper took the
   space's first terminal in `herdr-app ls` order, `t1x` in
   `~/git/herdr-plugins`, and that space's recorded folder is
   `~/git/herdr-plugins` too (flat:161). Fix: a candidate chain, then the
   active terminal, then the caller terminal, then `--repo`.
6. "the space lookup returned the JSON string `""`/`"NONE"` with quotes (`jq -c`
   on a string)" (flat:153). Fix: `jq -cr` (flat:555).
7. "an earlier edit pass mangled the script — it's been rewritten whole"
   (flat:153), and before that "The file got mangled by a bad edit"
   (flat:131). Cause: successive string replacements on a 315-line file. Fix:
   write the whole file (flat:542, flat:590).
8. "with `set -euo pipefail`, `git … | awk` inside a command substitution
   aborted the script **silently** when the folder wasn't a repo" (flat:259).
   Fix: each such assignment falls through to its own message (flat:594).
9. "`opencode`'s interactive command **rejects** `--model` (`Unrecognized flag:
   --model in command opencode` — only `run` and `mini` take it)" (flat:384).
   Without `--standalone`, the TUI "attaches to the long-running background
   server, which keeps the config it started with" (flat:392), so the new
   session showed the config default. Fix at the time:
   `OPENCODE_CONFIG_CONTENT` plus `--standalone`, now forbidden, see the last
   section.
10. `hc get`'s folder field was the wrong one. The handoff file found it:
    "`.cwd` is the pane's shell folder ... `.foreground.cwd` is where the
    foreground process runs" (`/tmp/opencode/handoff-hwt-wrong-repo.md`:45-48).

## Candidate lessons

Scope is named on each line, so a lesson from one project is not applied to the
other. One candidate belongs to monitor-agent, and it is lesson 18.

1. NEW (herdr-plugins). A herdr-app dialog cannot be filled from a shell: "The
   only shell-facing mod command is `mod.open --name <mod>` — its sole argument
   is `name`, no props" (flat:61). Check `herdr-app commands` first, that text
   is from 2026-11-11.
2. NEW (herdr-plugins). `space.new --task` puts the text on the agent's command
   line, so carry the message as argv: "`space.new --task` passes the text as an
   argument to the agent's own command line" (flat:80).
3. NEW (herdr-plugins). A worktree space takes two calls, and the space stays
   unnamed so the sidebar names it after the branch: "path is
   `~/.herdr/worktrees/<repo>/<slug(branch)>`" and "deliberately leaving the
   space unnamed so it's named after the folder and nested under its repo"
   (flat:47).
4. NEW (herdr-plugins). `herdr worktree` needs a pane context an agent's shell
   does not have: "from here it fails with `not_git_worktree` because this
   terminal has no herdr pane/workspace context" (flat:63). Agent's claim, its
   output is not in the log.
5. NEW (herdr-plugins). The window's focus is one client's view, never the
   caller's: "Previously it used the window's focus, which is another client's
   business and can differ from where you are." (flat:170).
6. NEW (herdr-plugins). `herdr-app ls` reports no per-terminal activity, so ask
   `herdr-app status` for `.focused_pane`: "`herdr-app ls` has no per-terminal
   "active" flag; only space/tab `active`" (flat:322).
7. NEW (herdr-plugins). `hc get` answers with two folders and the second is the
   live one: "`hc get`'s `.cwd` is the folder the terminal was **created** in,
   not the shell's live one — the live one is `.foreground.cwd`" (flat:430).
8. ALREADY WRITTEN. The repository comes from the terminal running the command,
   with no fallback chain: "the terminal running `hwt` always wins when it is in
   the space" (flat:223). `~/git/dotfiles/scripts/hwt` line 51, hwt skill §2.
9. ALREADY WRITTEN. A multi-paragraph prompt goes in a file: "A multi-paragraph
   prompt full of quotes is not something to hand to a shell line." (flat:347).
   `scripts/hwt --task-file`, hwt skill §3.
10. ALREADY WRITTEN. Print the dry run, read it, then run for real:
    "`-n, --dry-run`" (flat:172). `scripts/hwt` `dry_run`, hwt skill §4.
11. ALREADY WRITTEN. A live test closes what it opened: "Both spaces closed,
    worktrees removed, focus restored to `monitor-agent`" (flat:100).
    `.kb/spikes.md` §5 says the same for spikes, and `.agents/skills/herdr/SKILL.md`
    states the mirror rule about not closing what you did not create.
12. ALREADY WRITTEN. Commit the files the work touched and leave a worktree
    that was already dirty: "commit the changes you made" (msg 175). The agent
    kept `scripts/functions` out of every commit (flat:372).
    `.agents/skills/cpc-commit-messages/SKILL.md` holds the one-change rule and
    the line-length rule.
13. NEW (dotfiles scripts, and any bash). `set -euo pipefail` turns a failed
    pipeline inside a command substitution into a silent exit: "`git … | awk`
    inside a command substitution aborted the script **silently**"
    (flat:259). Each such assignment needs its own guard.
14. NEW (agent workflow, both projects). Rewrite a long script whole after a
    bad replacement pass: "an earlier edit pass mangled the script — it's been
    rewritten whole" (flat:153). It happened twice in one session (flat:131).
15. NEW (opencode tooling). The context7 library id for opencode docs is
    `/anomalyco/opencode`. The `/sst/opencode` query is the one failed tool call
    in the raw export (msg 212), and the retry completed (msg 213).
16. NEW (opencode tooling). The interactive TUI takes no `--model`:
    "`opencode`'s interactive command **rejects** `--model`" (flat:384). The
    workaround this session built is forbidden now, see the last section.
17. ALREADY WRITTEN. A spike branches as `spike/<slug>`: "a spike, probe,
    trial, or experiment → `spike/<slug>`" (flat:340). For monitor-agent that is
    `.kb/spikes.md` §2, which also puts the spike's directory at `spike/<name>`.
18. NEW (monitor-agent, the boundary with the global config). A tool that works
    in every repository keeps its skill in the global config, so this project's
    `.opencode/skills/` holds only its own skills. The person chose "Global
    `hwt` skill + `/hwt` command (Recommended)" over "Only in monitor-agent"
    (msg 195), and the three files landed in `~/git/dotfiles` (flat:327-333).
    This project's rules for its own work stay in `.kb/` and in its one skill,
    `.opencode/skills/workshop-host-authority/SKILL.md`.
19. ALREADY WRITTEN. `/hwt` runs in one shot and asks only when the ask cannot
    be briefed: "Immediate, but ask only when the ask is thin" (msg 195).
    `~/.config/opencode/skills/hwt/SKILL.md`, opening paragraph and §1.

## What should not become a skill

- The model delivery this session built, `OPENCODE_CONFIG_CONTENT` in the argv
  plus `--standalone`. It was reversed later, and the tool's own skill forbids
  it: "Never replace that with `OPENCODE_CONFIG_CONTENT` or `--standalone`"
  (`~/.config/opencode/skills/hwt/SKILL.md` §4, which gives the reason: pending
  `question` forms live in the server's memory).
- `opencode --prompt` as the way to start a session with a first message
  (flat:80). The current `hwt` opens a session with `--session` instead (same
  skill, §4). Lesson 16 holds, this fix does not.
- `jq -c` against `jq -cr` for a string (flat:555). One flag, and no reader of a
  skill needs it.
- The `-m, --machine` flag, added and then dropped (flat:513). A local step in
  one evening's design.
- The leftover empty directories under `~/.herdr/worktrees/` (flat:188). The
  person never answered, and no rule follows from that.
- Session state as a fact: 315 lines, `master` 25 commits ahead, the branch
  `spike/option-2` and its checkout (flat:349, flat:372).
- This machine's space layout on 2026-11-11, the monitor-agent space holding
  `t1x` in `~/git/herdr-plugins` beside two monitor-agent terminals (flat:161).
  Layouts change, and lesson 8 is the rule that survives them.
