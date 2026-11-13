---
name: hwt
description: Hand an ask to a fresh opencode session in its own git worktree and its own Herdr space, with a prompt that describes the work completely and a goal that holds the session to it until an independent reviewer says the objective is met. Use when the person types /hwt <ask>, or says to spawn, branch off, hand over, or run something in a new worktree, space, or agent instead of doing it here.
---

# Spawn an ask in its own worktree and session

The person typed an ask and wants it done **somewhere else**: a new checkout,
a new Herdr space, an opencode session that starts cold. That session sees
nothing of this conversation, so the prompt written here is the whole brief.

Two things go to that session: the brief, which says what to do and the rules
that apply, and the goal, which says what must be true when it is done. An
independent reviewer holds the session to the goal, so the session works past
the point where it would otherwise report success.

One shot: build the brief and the goal, dry-run, spawn. Ask questions only when
the ask is too thin to brief (step 1), never to confirm details the repository
answers.

## 1. Understand the ask

The ask is the text after `/hwt`.

Ask one round of questions, at most three, numbered, no preamble, when the ask
read against this conversation lacks any of: the outcome wanted, why it is
wanted, or how someone would tell it worked. Otherwise ask nothing.

The goal needs the third of those. When the ask says what the work is but not
how someone would tell it worked, that is a question to ask: the reviewer
judges the objective literally, and an objective nobody can check from a
transcript sends the session round in circles.

Read before writing, never ask what this answers:

- `AGENTS.md` and every file it points at (`.kb/`, `docs/`) — the rules the new
  session must obey, and the vocabulary it should use;
- the build and test entry points (`pyproject.toml`, `Makefile`,
  `package.json`, `.workshop.yaml`);
- what the ask names, and its neighbours: the module, the test, the spec, the
  last few commits that touched it.

## 2. Choose the branch

The branch is also the space name and the checkout's folder, so it must read
as the work does in the sidebar:

- a spike, probe, trial, or experiment → `spike/<slug>`; a repository with a
  spike convention (`.kb/spikes.md`, `spike/`) has laws the prompt must state;
- a defect → `fix/<slug>`; new behaviour → `feat/<slug>`; an OpenSpec or Spec
  Kit change name → that name;
- slug: the ask's own words, lowercase, `[a-z0-9-]`, two to four words
  ("spike option 2" → `spike/option-2`). Never `work`, `task`, `tmp`, or a
  number alone.

The repository is the folder of the program in front in this terminal, so a
session started from a checkout branches that checkout's repository even when
its pane belongs to another one. Do not cd elsewhere for it. When the ask
names another space or repository, use `hwt --space <name>` or
`hwt --repo <path>` and say so in the report.

## 3. Write the prompt

Write it with the write tool to a scratch file outside the repository, such as
`/tmp/opencode/hwt-prompt-<slug>.md`. Never assemble it with a shell heredoc or
`echo`: quotes and newlines will not survive, and the file is passed to `hwt`
as it stands.

Fill every placeholder. The prompt carries the whole brief:

```markdown
You are starting work in a fresh git worktree.

Checkout: <path>
Repository: <main root>  Branch: <branch>  Base: <base>

# Ask

<the person's ask, verbatim, in one block>

# Why

<two to five sentences: what they want and what it is for, taken from this
conversation and from what you read>

# Where things stand

- <file: what it does, and why it matters to this work>
- <the command that builds, tests, or runs the thing>
- <what you already found: versions, a failing test, a prior attempt, the
  decision this depends on>

# What to do

1. <first concrete step, naming the file or command>
2. ...

# Rules

- Read <AGENTS.md and the files it points at> before editing.
- <the rules that apply to this work: spike laws, the requirements process,
  commit message form, no production code for a probe>
- Commit on <branch>; do not push, merge, rebase, or touch other branches.
- Ask before <the expensive or destructive step this work could reach>.
- When you need a decision, a credential, or a value only the person has, ask
  for it with the `question` tool and wait for the answer. Do not guess it, and
  do not stop to ask in prose.

# Done when

<the observable end state: the README states the question and verdict, the
test passes, the command prints X>

# Report

Finish with: what you did, what you found, what you did not verify, and what
you need from the person.
```

The prompt must stand alone: no "as discussed", no "the plan above", no
reference to a transcript, no secrets or tokens. Name the branch and the
checkout path, because that is where the session starts.

## 3a. Write the goal

The goal is the objective the new session is held to. OpenCode's own `/goal`
command gives the session that objective and keeps a reviewer on it: after every
turn the reviewer judges the transcript against the objective and continues the
work when it is not met yet. The reviewer trusts only what it can see in the
transcript — command output, test results, file contents — and reads the
assistant's own claim that the work is done as a claim, not as evidence.

So write the objective as the check that decides it is done, in one sentence
that names the command and what it prints:

- good — "`pytest tests/test_health.py` passes and prints `3 passed`"
- good — "`README.md` has a section `## Verdict`, and `grep -c '^## Verdict' README.md` prints `1`"
- bad — "the health check is implemented"
- bad — "the work is complete"

The reviewer reads the objective literally. "Implement the health check" cannot
be judged from a transcript, so the reviewer keeps sending the session back and
the session loops. Name the file, the command, and the expected output. The
reviewer runs the command itself and quotes what it printed, so a goal that
names one can be checked without trusting the session's word for it.

Keep the objective to one goal. A second, unrelated objective makes the
reviewer judge both and rarely accept either. When the work has two parts, spawn
two sessions.

The goal and the brief are different things and both are sent: the brief says
what to do and the rules that apply, the goal says what must be true when it is
done. The "Done when" section of the brief and the goal say the same thing from
two sides; write them together so they do not drift.

Write the objective to a scratch file outside the repository, such as
`/tmp/opencode/hwt-goal-<slug>.md`, one line. Use the write tool, never a shell
heredoc.

## 4. Spawn

Dry run first, then for real, from this session's shell. Pass this session's
own model, so the new one does not fall back to the configured default:

```
model="$(opencode session export "$OPENCODE_SESSION_ID" |
	jq -r '.info.model | "\(.providerID)/\(.id)" +
		(if .variant then "#\(.variant)" else "" end)")"

hwt -n --agent opencode --model "$model" \
	--task-file <prompt file> --goal-file <goal file> <branch>
hwt    --agent opencode --model "$model" \
	--task-file <prompt file> --goal-file <goal file> <branch>
```

When `OPENCODE_SESSION_ID` is unset or the export fails, leave `--model` out
and say which default the new session will use instead. `--goal` and
`--goal-file` still work without `--model`: `hwt` then creates the session on
the configured default and sets the goal on it.

`--model` does not start a private OpenCode server. `hwt` creates the session
on OpenCode's background server and opens it with `--session`. Never replace
that with `OPENCODE_CONFIG_CONTENT` or `--standalone`: pending `question`
forms live in the server's memory, so a private server hides them from every
other surface, the Questions panel included, while the session sits blocked.

The goal is set through OpenCode's own `/goal` command, on the session
`hwt` created. It cannot be written into the prompt file: a prompt that starts
with `/goal` is read as prose by the model, not dispatched as a command, and
the session would carry no goal at all.

If `hwt` is not on PATH, stop and say so. Do not hand-build its two steps:
the checkout location and the space name must stay the ones Herdr's own
"New worktree..." produces.

Read the dry run: it prints the repository, the checkout, the session, the
goal, and the exact `space.new` argv. The repository and checkout lines must
name the repository and branch you meant, and the goal line must read the
objective you wrote. Then run the second line. Use `--agent <kind>` only when
the person asked for another agent.

`hwt` refuses rather than guesses: an existing checkout, an invalid branch, a
space on another machine, no Herdr window. Report that message and stop. Never
quietly pick another branch name or another repository, and never fall back to
`--no-space` to get past a refusal.

## 5. Report

Give, in a few lines:

- the branch, the checkout path, and the space name (`hwt` prints
  `hwt: <branch> -> <path>`);
- the base: `HEAD` of the main checkout for a new branch, or the `--base` you
  passed;
- the model it runs: `provider/model#variant` taken from this session, or the
  default the new session falls back to;
- what the new session was told, one line per section of the prompt;
- the goal, quoted, and the goal file's path, so the person can read or edit
  what was sent;
- the prompt file's path, so the person can read or edit what was sent;
- whether this checkout had uncommitted changes, because the new branch
  starts from the last commit and will not contain them.

Say what the goal means for the person: the session keeps working until the
objective is met, so it will not stop to ask whether it is finished. When the
work needs a decision, a credential, or a manual step, the session asks for it
through the `question` tool and waits for the answer in the Questions panel.
A session that stops without asking pauses the goal instead: the person reads
the state with `/goal` and resumes it with `/goal resume`, in that tab. Say
that a goal does not survive an OpenCode server restart: the server pauses it,
and the person resumes it again.

Then stop. The other session owns the work: do not start it here, do not
create files in the new checkout, and do not wait for it.