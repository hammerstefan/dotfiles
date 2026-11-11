---
name: hwt
description: Hand an ask to a fresh opencode session in its own git worktree and its own Herdr space, with a prompt that describes the work completely. Use when the person types /hwt <ask>, or says to spawn, branch off, hand over, or run something in a new worktree, space, or agent instead of doing it here.
---

# Spawn an ask in its own worktree and session

The person typed an ask and wants it done **somewhere else**: a new checkout,
a new Herdr space, an opencode session that starts cold. That session sees
nothing of this conversation, so the prompt written here is the whole brief.

One shot: build the prompt, dry-run, spawn. Ask questions only when the ask is
too thin to brief (step 1), never to confirm details the repository answers.

## 1. Understand the ask

The ask is the text after `/hwt`.

Ask one round of questions, at most three, numbered, no preamble, when the ask
read against this conversation lacks any of: the outcome wanted, why it is
wanted, or how someone would tell it worked. Otherwise ask nothing.

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

The repository is the folder of the terminal running this, so a session
started from a checkout branches that checkout's repository. Do not cd
elsewhere for it. When the ask names another space or repository, use
`hwt --space <name>` or `hwt --repo <path>` and say so in the report.

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

## 4. Spawn

Dry run first, then for real, from this session's shell:

```
hwt -n --agent opencode --task-file <prompt file> <branch>
hwt    --agent opencode --task-file <prompt file> <branch>
```

If `hwt` is not on PATH, stop and say so. Do not hand-build its two steps:
the checkout location and the space name must stay the ones Herdr's own
"New worktree..." produces.

Read the dry run: it prints the repository, the checkout, and the exact
`space.new` argv. Both lines must name the repository and branch you meant.
Then run the second line. Use `--agent <kind>` only when the person asked for
another agent.

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
- what the new session was told, one line per section of the prompt;
- the prompt file's path, so the person can read or edit what was sent;
- whether this checkout had uncommitted changes, because the new branch
  starts from the last commit and will not contain them.

Then stop. The other session owns the work: do not start it here, do not
create files in the new checkout, and do not wait for it.
