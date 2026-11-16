---
description: Spawn one hwt worktree session that implements a whole spec with the implement-spec skill
---

Load the `hwt` skill with the skill tool, id `hwt`, and apply it once. It owns the branch naming, the dry-run-then-spawn sequence, and the refusal rules. This command adds the spec part: which issue, what the session is told, what the goal is, and the one place its rules depart from hwt's default brief.

Spec issue:

$ARGUMENTS

## The implement-spec skill

Load it at the start with the skill tool, id `implement-spec`. It lives at
`~/.agents/skills/implement-spec/SKILL.md`, and its frontmatter sets
`disable-model-invocation: true`.

Loading it here is for one reason: the brief this command writes substitutes
three of its steps, and the substitutions must name what they replace. Do not
run any of it in this session.

Never hand this work to `/hwt @implement-spec #<n>`. A skill mention is resolved
in the session that types it, and `hwt` sends the new session only the brief
text, so the child would receive the literal string `@implement-spec` and, since
the flag above keeps it out of the catalog, report it missing.

## 1. Read the argument

- One number, with or without `#` (`91`, `#91`) — that issue is the spec.
- Empty — ask which spec issue, and spawn nothing until the person answers.
- Anything else — say "Give one spec issue number.", report what was given, and spawn nothing.

## 2. Resolve the spec

```sh
repo="$(git rev-parse --show-toplevel)"
owner="$(gh repo view --json owner -q .owner.login)"
name="$(gh repo view --json name -q .name)"
login="$(gh api user -q .login)"
gh issue view <n> --json number,title,state,labels,body
gh api graphql -f query="
query {
  repository(owner: \"$owner\", name: \"$name\") {
    issue(number: <n>) {
      subIssues(first: 100) {
        nodes {
          number title state
          assignees(first: 5) { nodes { login } }
          labels(first: 10) { nodes { name } }
          blockedBy(first: 20) { nodes { number title state } }
        }
      }
    }
  }
}"
```

Stop when `gh` fails: say what it printed.

Refuse, one line each, and spawn nothing:

- the issue is closed — `#<n> <title> — the spec is closed`;
- the issue carries `wayfinder:map` — `#<n> <title> — that is a map, not a spec; use /wayfinder-hwt`;
- an open child carries a `wayfinder:*` label — `#<n> <title> — skipped: wayfinding is unfinished, #<m> <title> is still open`;
- the spec has no children — `#<n> <title> — the spec has no tickets; run /to-tickets first, or /hwt for a single unit of work`;
- an open child is assigned to another login — `#<n> <title> — skipped: #<m> is claimed by <login>`. Assignment is this repository's claim, and this session does not respect claims, so another person's claim blocks the run. Children assigned to you do not.

The map this spec came from cannot be checked: nothing links the two issues. The `wayfinder:*` children are the reliable test that wayfinding is unfinished.

Report the shape before spawning: how many children are closed, open, unblocked, and blocked. An empty frontier with open children is a refusal: `#<n> <title> — every open ticket is blocked` and stop.

## 3. Choose the branch

The branch and the checkout's folder keep the spec's name, so they read as the
work does in the sidebar. The Herdr space is named for the run instead:
`#<n> spec <words>` — the spec issue's number, the word `spec`, then the slug's
first three words, hyphenated (`#91 spec proxy-egress-fence`). The branch is
not the space name here.

The spec is a named change, so the branch is its name: the title's own words, lowercase, `[a-z0-9-]`, two to four words, with the leading verb and the articles dropped (`Implement`, `Add`, `Build`, `Fix`, `The`, `A`). "Implement the proxy egress fence" becomes `proxy-egress-fence`.

This is also the integration branch, so the name must be one the person would recognise as the whole spec, not one ticket.

When a branch or checkout of that name already exists, ask which word to add. Never pick another name yourself.

## 4. Write the brief

Write it with the write tool to `/tmp/opencode/hwt-prompt-<slug>.md`. Never assemble it with a shell heredoc or `echo`.

Fill every placeholder:

```markdown
You are starting work in a fresh git worktree.

Checkout: <path>
Repository: <main root>  Branch: <branch>  Base: <base>

# Ask

Implement spec #<n> — <title> — with the `implement-spec` skill.

# Why

<two to five sentences: what the spec delivers and for whom, taken from the spec
body and from this conversation>

# Where things stand

- The `implement-spec` skill is installed at `~/.agents/skills/implement-spec`
  with `disable-model-invocation: true`, so it is absent from the skill catalog.
  Load it with the skill tool, id `implement-spec`. Check it on disk with
  `sed -n '1,5p' ~/.agents/skills/implement-spec/SKILL.md`.
- The spec is #<n> (<url>). Its child issues are the tickets. Read both with
  `gh issue view`.
- <the repository's tracker doc, glossary, and the files that hold decisions
  this work depends on, by name>
- Branch `<branch>` in this worktree is the integration branch. It already
  exists.

# What to do

1. Load the `implement-spec` skill with the skill tool, id `implement-spec`.
2. Read spec #<n> and its child issues in full, plus the repository's
   `AGENTS.md` and every file it points at.
3. Follow the skill, with these three substitutions:
   - its integration-branch step is already done: the integration branch is
     `<branch>`, this worktree's branch. Do not create another, and do not open
     a pull request from a different branch;
   - implementer subagents may create their own worktrees from `<branch>`.
     Remove every one before you finish, leaving no extra branch or checkout
     behind;
   - do not add or remove assignees on the tickets. An assignee is a claim made
     by a person or another session.
4. <where this repository closes work: one pull request for `<branch>`, draft
   after the first merge, ready when every ticket is resolved — or, for a
   tracker without pull requests, resolve each ticket the way the tracker
   closes work>

# Rules

- Read `AGENTS.md` and every file it points at before editing.
- Commit on `<branch>`. Merging your ticket branches into `<branch>` and opening
  one pull request for it are this brief's only exceptions to "do not push,
  merge, or rebase". Never force-push, never push another branch, and never
  touch another worktree's branch.
- Build test-first where the spec agreed a seam. Where it agreed none, pick the
  highest existing seam and state it before the first failing test.
- Ask before <the step in this repository that destroys state or spends money>.
- When you need a decision, a credential, or a value only the person has, ask
  for it with the `question` tool and wait for the answer. Do not guess it, and
  do not stop to ask in prose.

# Done when

<the observable end state, in prose: every ticket resolved, the pull request
open and not a draft, and the code review clean>

# Report

Before the report, call `todowrite` once with every item still remaining — work
only the person can finish, a step you could not run, a check you did not
verify, a decision still open — one todo each, each one `pending`, and nothing
that is already done. That list is how the person sees what is left after this
session stops; it replaces any earlier list, so write all of it, and write an
empty list when nothing remains rather than an invented todo.

Finish with: what you did, what you found, what you did not verify, and what
you need from the person.
```

The "Rules" line replacing hwt's default is the point of this command. hwt's
brief template always forbids push and merge; `implement-spec` must merge into
the integration branch and open a pull request. Write the substitution, never
both lines.

## 5. Write the goal

One line, the check that decides the work is done. Which check depends on how
the repository closes work, read from `docs/agents/issue-tracker.md`:

- **A real tracker with pull requests** — the pull request is marked ready only
  after every ticket is resolved, so its draft state is the last thing to turn:

  `gh pr list --head <branch> --state open --json isDraft --jq '.[0].isDraft'` prints `false`

- **A tracker without pull requests (local markdown)** — the open children are
  the check:

  `gh api graphql -f query='query { repository(owner:"<owner>", name:"<name>") { issue(number:<n>) { subIssues(first:100){nodes{state}} } } }' --jq '[.data.repository.issue.subIssues.nodes[] | select(.state=="OPEN")] | length'` prints `0`

No pull request yet prints `null`, not `false`, so the check stays unmet until
one exists. Write the command out in full: the reviewer runs it and quotes what
it printed.

Keep the objective to one goal. Write the file with the write tool to
`/tmp/opencode/hwt-goal-<slug>.md`, one line.

## 6. Spawn

Dry run first, then for real, from this session's shell. Pass this session's own model:

```sh
model="$(opencode session export "$OPENCODE_SESSION_ID" |
	jq -r '.info.model | "\(.providerID)/\(.id)" +
		(if .variant then "#\(.variant)" else "" end)")"
```

Empty `$OPENCODE_SESSION_ID`, or an export that fails: run without `--model` and
say in the report that the new session takes the configured default.

```sh
hwt -n -r "$repo" --agent opencode --no-focus ${model:+--model "$model"} \
	--space-name '#<n> spec <words>' \
	--task-file "/tmp/opencode/hwt-prompt-<slug>.md" \
	--goal-file "/tmp/opencode/hwt-goal-<slug>.md" "<branch>"
```

Read the dry run. `hwt: repository` must be `$repo`, `hwt: checkout` must name
this branch, `hwt: space.new` must carry `--name '#<n> spec <words>'` and a
`--folder` naming this branch, `hwt: focus` must say it stays on the space it is
on now, and `hwt: goal` must read the objective you wrote. Rewrite the brief's
`Checkout:` line with the printed path.

Then spawn, with the same command and no `-n`; `--no-focus` stays.

A refusal — non-zero exit, or a printed refusal — is reported in `hwt`'s own
words, and nothing is retried: no second branch, no `--no-space`.

## 7. Report

Give, in a few lines:

- the spec: `#<n> <title>`, and its shape — open, blocked, closed, and claimed children;
- the branch, the checkout path, and the space name `#<n> spec <words>` (`hwt`
  prints `hwt: <branch> -> <path>`);
- the base: `HEAD` of the main checkout, or the `--base` that was passed;
- the model it runs: `provider/model#variant` taken from this session, or the default the new session falls back to;
- the goal, quoted, and the goal file's path;
- the brief file's path, so the person can read or edit what was sent;
- the one rule that differs from a plain `/hwt`: this session may merge into
  `<branch>` and open one pull request for it;
- whether this checkout had uncommitted changes, because the new branch starts
  from the last commit and will not contain them.

Say what the goal means for the person: the session keeps working until the
objective is met, so it will not stop to ask whether it is finished. When it
needs a decision, a credential, or a manual step, it asks through the `question`
tool and waits in the Questions panel.

Then say two things about what comes after:

- implementer subagents run in the background and create their own worktrees;
  they are visible in the subagents view, not as spaces, and the session must
  remove them before it finishes;
- when the worktree is wrapped up, a pull request for `<branch>` may already be
  open. Tell `/hwt-wrapup` so it does not open a second one.

Then stop. The other session owns the work: do not start it here, do not create
files in the new checkout, and do not wait for it.
