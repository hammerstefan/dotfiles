---
description: Spawn one hwt worktree session per wayfinder ticket, each running /wayfinder on its ticket
---

Load the `hwt` skill with the skill tool, id `hwt`, and apply it once per ticket. It owns the branch naming, the dry-run-then-spawn sequence, and the refusal rules. This command adds the wayfinder part: which tickets, what each session is told, and what you report back.

Tickets:

$ARGUMENTS

## The wayfinder skill

Load it at the start with the skill tool, id `wayfinder`. It lives at
`~/.agents/skills/wayfinder/SKILL.md`, and its frontmatter sets
`disable-model-invocation: true`.

That flag keeps the skill out of the model's skill catalog. It does not appear
in `<available_skills>`, so a model that checks only its catalog, or only
`~/.config/opencode/skills`, or only `~/.config/opencode/skill`, or only the
command directories, will report it missing. Never conclude it is absent from
those places, and never write into a brief that it is not installed. Check it
on disk instead:

```sh
sed -n '1,5p' ~/.agents/skills/wayfinder/SKILL.md
```

The skill owns the claim, resolve, close, and Decisions-so-far conventions for
every session this command spawns. Each brief names its path and that flag, so
the spawned session does not repeat the search.

## 1. Read the arguments

- Numbers, with or without `#` (`20 21 24`) — those tickets, in that order.
- `frontier` alone — query the map for the tickets the person can pick up now, and confirm the list before spawning (step 3).
- `frontier` mixed with numbers, or any other word — say "Give ticket numbers, or `frontier` alone." Report what was given and spawn nothing.
- Empty — ask which tickets to spawn, or whether to use the frontier. Continue once they answer.

## 2. Find the repository and the map

`hwt` takes its repository from the opencode session that runs it, not from a `cd`. Every `hwt` call below passes `-r "$repo"`.

```sh
repo="$(git rev-parse --show-toplevel)"
owner="$(gh repo view --json owner -q .owner.login)"
name="$(gh repo view --json name -q .name)"
gh issue list --label wayfinder:map --state open --json number,title
```

Stop when `gh` fails: say what it printed. One open map in the list: set `map` to its number. Several: ask which, by name, and set `map` from the answer. None: say there is no open `wayfinder:map` issue in this repository, and stop.

Read the map body once: its Destination, Notes, Decisions so far, and Not yet specified.

## 3. Frontier only: query, then confirm

One GraphQL query returns every child of the map with the fields eligibility needs. `gh` 2.45 reads `blockedBy`; it only lacks the flags that write blocking edges.

```sh
gh api graphql -f query="
query {
  repository(owner: \"$owner\", name: \"$name\") {
    issue(number: $map) {
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

The frontier is the nodes with `state == OPEN`, no assignees, and no `blockedBy` node still `OPEN`.

Ask with the `question` tool, `multiple: true`: first option `All of them`, then one option per frontier ticket named by its title. Say how many are takeable in the question. `All of them` alone means the whole list, named tickets mean those, and an answer with nothing selected cancels the run.

No frontier tickets: say "The frontier is empty — every open ticket is claimed or blocked", and stop.

## 4. Preflight every selected ticket

Read each selected ticket, in the order given:

```sh
gh issue view <n> --json number,title,state,assignees,labels,body
gh api graphql -f query="
query {
  repository(owner: \"$owner\", name: \"$name\") {
    issue(number: <n>) { blockedBy(first: 20) { nodes { number title state } } }
  }
}"
git -C "$repo" worktree list --porcelain
git -C "$repo" branch --list '<branch>'
```

Skip a ticket, one line each, in this order:

- assigned — `#21 Decide the plane workshop provisioning and proxy lifecycle — skipped: claimed by hammerstefan`
- closed — `#23 Build the plane workshop — skipped: closed`
- a blocker still open — `#18 Verify the v0.56.0 binary in the plane workshop — skipped: blocked by #23 Build the plane workshop (open)`
- its branch or checkout already exists — `#20 Implement the proxy egress fence — skipped: wayfinder/proxy-egress-fence is checked out at <path>`
- no `wayfinder:<type>` label — `#25 Run the acceptance task and enforce the proxy allowlist — skipped: no wayfinder type label`

The four types — `research`, `prototype`, `grilling`, `task` — are all spawnable. A claimed ticket stays claimed: leave the assignee alone, leave an existing branch alone, and pick no substitute.

List every `wayfinder/*` and `research/*` worktree of this repository with its branch and path. These are the sessions already running, and the report names them.

Every selected ticket skipped: say so and stop.

## 5. Choose the branch

`research/<slug>` for a `wayfinder:research` ticket, `wayfinder/<slug>` for the other three.

The slug is the title's own words: lowercase, `[a-z0-9-]`, two to four words, with the leading verb and the articles dropped (`Implement`, `Decide`, `Build`, `Verify`, `Write`, `Run`, `Research`). "Implement the proxy egress fence" becomes `wayfinder/proxy-egress-fence`; "Decide the plane workshop provisioning and proxy lifecycle" becomes `wayfinder/plane-workshop-provisioning`.

When two selected tickets produce the same slug, ask which word to add.

## 6. The model

Once, before the loop:

```sh
model="$(opencode session export "$OPENCODE_SESSION_ID" |
	jq -r '.info.model | "\(.providerID)/\(.id)" +
		(if .variant then "#\(.variant)" else "" end)')"
```

Empty `$OPENCODE_SESSION_ID`, or an export that fails: run without `--model` and say in the report that the new session takes the configured default.

## 7. One ticket at a time

For each passable ticket, in order:

1. Read the ticket body, the map's Notes and Decisions so far, and the repository's `AGENTS.md` and every file it points at. Take the wayfinder skill from the section above, and never write that it is not installed.
2. Write the brief to `/tmp/opencode/hwt-prompt-<slug>.md` with the write tool: the skeleton in step 8, every placeholder filled. Put `PENDING: from hwt -n` on its `Checkout:` line.
3. Write the goal to `/tmp/opencode/hwt-goal-<slug>.md` with the write tool, one line: the ticket's observable end state, naming the command that proves it and what that command prints. The `Done when` section of the brief is the same thing in prose; write the two together so they cannot drift.
4. Dry run from this session's shell:

   ```sh
   hwt -n -r "$repo" --agent opencode --no-focus ${model:+--model "$model"} \
       --space-name '#<map>:<n> <words>' \
       --task-file "/tmp/opencode/hwt-prompt-<slug>.md" \
       --goal-file "/tmp/opencode/hwt-goal-<slug>.md" "<branch>"
   ```

5. Read the dry run. `hwt: repository` must be `$repo`, `hwt: checkout` must name this branch, `hwt: herdr space.new` must carry `--name '#<map>:<n> <words>'` and a `--folder` naming this branch, `hwt: focus` must say it stays on the space it is on now, and `hwt: goal` must read the objective you wrote. Rewrite the `Checkout:` line with the printed path.
6. Spawn, with the same command and no `-n`; `--no-focus` stays.
7. A refusal — non-zero exit, or a printed refusal — is recorded in `hwt`'s own words, and the loop continues with the next ticket. Nothing is deleted, no space is closed, no second branch is tried, and `--no-space` is not a fallback.

The space is named `#<map>:<n> <words>` — the map and ticket numbers, then the
slug's first three words, hyphenated: ticket 102 of map 44, "Implement the
proxy egress fence", opens space `#44:102 proxy-egress-fence`. `<words>` in the
command above is that hyphenated tail. The branch and the checkout keep the
slug alone. Each space opens behind this one, so the window stays here and the
person reads this report: the new sessions wait in the sidebar, each running
its ticket. The goal holds the session to the ticket's end state: a reviewer
judges the transcript against the objective on every idle turn, and continues
the work when it is not met yet. A ticket that needs a decision has the session
ask for it with the `question` tool and wait for the answer.

## 8. The brief

```markdown
You are starting work in a fresh git worktree.

Checkout: <path the dry run printed>
Repository: <repo>  Branch: <branch>  Base: <base>

# Ask

`/wayfinder #<map> #<n>`

# Why

<two to five sentences: the map's destination, what this ticket decides or delivers, and its wayfinder type>

# Where things stand

- `AGENTS.md` and the files it points at: the repository rules.
- <the files that hold the decisions this ticket depends on, by name>
- The map is <map title> (`#<map>`, <url>); the ticket is <ticket title> (`#<n>`, <url>). Read both with `gh issue view`.
- <host tooling the ticket needs>
- The `wayfinder` skill is installed at `~/.agents/skills/wayfinder` with
  `disable-model-invocation: true`, so it is absent from the skill catalog.
  Load it with the skill tool, id `wayfinder`.

# What to do

1. Load the `wayfinder` skill with the skill tool, id `wayfinder`, then read this ticket's `wayfinder:<type>` label.
2. Claim the ticket: `gh issue edit <n> --add-assignee @me`. This is the first write.
3. <the type's method, one line per step>
4. Record the resolution on the ticket, close it, and append the context pointer to the map's Decisions so far.

# Rules

- Read `AGENTS.md` and every file it points at before editing.
- <the repository rules this work must obey>
- Commit on `<branch>`. Do not push, merge, rebase, or touch other branches.
- Ask before <the step in this repository that destroys state or spends money>.

# Done when

<the observable end state, including the closed ticket and the map line that names it>

# Report

Before the report, call `todowrite` once with every item still remaining — work only the person can finish, a step you could not run, a check you did not verify, a decision still open — one todo each, each one `pending`, and nothing that is already done. That list is how the person sees what is left after this session stops; it replaces any earlier list, so write all of it, and write an empty list when nothing remains rather than an invented todo.

Finish with: what you did, what you found, what you did not verify, and what you need from the person.
```

The "Done when" section and the goal say the same thing from two sides: the
section tells the session what to aim for, the goal tells the reviewer what to
check. Write them together, in the same words, so they cannot drift. A
`grilling` ticket has no checkable end state, because its work is a decision
the person makes: give it the goal that the decision is recorded on the ticket,
with the person's answer in it, and nothing more.

Step 3 of the brief, by the ticket's `wayfinder:<type>` label:

- `grilling` — work the decision with the person: load the `grilling` and `domain-modeling` skills, ask through the `question` tool, and never answer your own questions.
- `prototype` — load the `prototype` skill, build the cheap artifact, and link it from the ticket.
- `research` — load the `research` skill, investigate against primary sources, and write the findings file where the repository keeps such notes, citing each claim.
- `task` — deliver what the ticket names and verify it on this host; hand the person a precise checklist for what only they can do.

A `research` ticket's Rules line reads: "Push `<branch>` and open no pull request. It is a throwaway record." The other three read: "Do not push."

## 9. Report

Give, in a few lines:

- one line per spawned session: `#20 Implement the proxy egress fence — wayfinder/proxy-egress-fence — <checkout> — space #<map>:<n> proxy-egress-fence — <model, or "configured default"> — <brief path> — goal: <objective>`
- one line per skipped ticket, with its reason
- `hwt`'s refusal lines verbatim, and which tickets were not attempted
- the `wayfinder/*` and `research/*` worktrees that were already running, by branch and path
- the base: `HEAD` of the main checkout, or the `--base` that was passed
- when anything failed, the exact `/wayfinder-hwt ...` line that retries the remaining tickets

Say that each spawned session is held to its goal: it works until an
independent reviewer says the objective is met. A ticket that needs a decision
has the session ask for it in the Questions panel and wait. The person reads a
session's goal state with `/goal` and resumes it with `/goal resume`, in that
session's tab.

Then stop. The new sessions own the work: do not start it here, do not write into a new checkout, and do not wait for it.
