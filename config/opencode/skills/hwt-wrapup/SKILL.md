---
name: hwt-wrapup
description: Close a finished worktree by turning what its sessions showed into repo-level skills, guidance and memory. Use when the person types /hwt-wrapup, or says to wrap up a worktree, extract the lessons from this worktree's sessions, turn what happened here into a skill, or finish and close the worktree now that the work is done.
---

# Wrap up a worktree

A worktree's sessions hold what was learned in it: corrections the person made,
conventions they stated, commands that worked, traps that were hit twice. When
the work is done those sessions are the only record, and the worktree is one
more checkout in the sidebar. A wrapup turns them into a pull request against
the repository and then closes the worktree.

Two actors, and this skill is the first:

- **This session**, in the source worktree, lists that worktree's sessions,
  writes the brief and the goal, and spawns the reflection session. Then it
  stops; the other session owns the work.
- **The reflection session**, in a worktree of its own, exports and reads the
  transcripts, writes the skills, guidance and memory, opens the pull request,
  and closes the source worktree.

## 0. Refuse rather than guess

Stop, and say which check failed, when:

- this session is not in a linked git worktree, or is in the main checkout — a
  wrapup closes a linked worktree, never the repository itself;
- `hwt`, `opencode`, `gh`, `jq`, `sqlite3` or `herdr-app` is not on `PATH`;
- `gh` is not authenticated for the repository;
- the wrapup branch already exists locally or on the remote (a stale branch
  from another run is someone's work: name it, remove nothing);
- `git fetch origin` fails — an offline base drags the branch's own commits
  into the pull request;
- the worktree holds no session other than this one and its children.

Never choose another branch name, base, repository or session set to get past a
refusal.

## 1. Read the worktree and the repository

```sh
source_worktree="$(git rev-parse --show-toplevel)"
main_root="$(git -C "$source_worktree" worktree list --porcelain |
	awk '/^worktree /{print substr($0, 10); exit}')"
branch="$(git -C "$source_worktree" rev-parse --abbrev-ref HEAD)"
```

If `source_worktree` equals `main_root`, stop: this is the main checkout, and a
wrapup never removes the repository itself.

Then the base and the pull request's target:

```sh
git -C "$main_root" fetch origin --prune
default_branch="$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name)"
repo_name="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"
base="origin/$default_branch"
wrapup_branch="wrapup/$(printf '%s' "$branch" | tr '/' '-')"
git -C "$main_root" check-ref-format --branch "$wrapup_branch"   # must exit 0
```

`wrapup/<branch>` reads as the work it came from in the sidebar, and the base is
the repository's default branch so the pull request can be reviewed as skill
changes alone. Never base it on the worktree's own branch: until that branch
merges, the pull request would show all of its commits too.

Refuse when the branch already exists: `git -C "$main_root" show-ref --verify
refs/heads/<wrapup branch>` exits 0, or `git ls-remote --heads origin <wrapup
branch>` prints anything.

## 2. List the sessions

The session store is the only place that knows a worktree's sessions and their
children. `session_v2` carries `directory` and `parent_id`, and a child session
inherits its parent's directory, so one filter finds a whole tree.

```sh
db="$HOME/.local/share/opencode/opencode.db"
state="/tmp/opencode/hwt-wrapup-<slug>"   # <slug>: the source branch, '/' as '-'
mkdir -p "$state"
```

Read the ids, the tree and the sizes in one query. `instr` rather than `like`,
because a path may contain `_`, which `like` reads as a wildcard:

```sh
sqlite3 -json "$db" "
with recursive mine(id) as (
  select '$OPENCODE_SESSION_ID'
  union all
  select s.id from session_v2 s join mine m on s.parent_id = m.id
)
select s.id, s.parent_id, s.title, s.time_created, s.time_updated,
       (select count(*) from session_message m where m.session_id = s.id) as messages,
       (select ifnull(sum(length(m.data)), 0) from session_message m
         where m.session_id = s.id) as bytes
from session_v2 s
where (s.directory = '$source_worktree'
       or instr(s.directory, '$source_worktree' || '/') = 1)
  and s.id not in (select id from mine)
order by s.time_created" > "$state/sessions.json"
```

Excluding this session and its descendants keeps the wrapup from reading its
own tail: it is orchestration, not work.

`session_v2` is not a public interface. When the query fails, fall back to
`opencode session list --format json -n 1000`, keep the entries whose
`directory` is the worktree or below it, and say in the report and in the brief
that subagent sessions were skipped because the session store could not be
read. Do not guess at children from titles.

`sqlite3 -json` prints nothing at all for an empty result, not `[]`: an empty
file means no sessions, not a failed query. When no session is left after the
exclusion, report that and stop. Nothing is closed — a worktree that taught
nothing would lose the only copy of its work for nothing.

Render the list for the person: one row per session with its title, whether it
is a subagent, its message count and its size, oldest first.

## 3. Write the brief and the goal

Write both files with the write tool, never a shell heredoc, into `$state`.

The brief is below. Fill every placeholder: it is the reflection session's
whole world, and that session sees none of this conversation.

````markdown
You are wrapping up a finished git worktree. Its sessions hold what the work
taught; your job is to turn that into repo-level skills, guidance and memory,
open one pull request, and then close the worktree.

Checkout: <this worktree's path, where you start>
Repository: <main root>  Branch: <wrapup branch>  Base: <origin/default>
Source worktree: <source path>  Branch: <source branch>
Pull request target: <owner/name>, base <default branch>
Close the source worktree: <yes | no, because the person passed --keep>

# What happened here

<two to five sentences: what the branch was for, and what its sessions show it
did — taken from the session titles and this conversation>

# Sessions to read

<one line per session: id — title — top-level or subagent — messages, size>

Every one of them is an OpenCode session at or under <source path>. Export each
to a file and read the files, never the store:

```sh
mkdir -p /tmp/opencode/hwt-wrapup-<slug>/transcripts
opencode session export <id> > /tmp/opencode/hwt-wrapup-<slug>/transcripts/<id>.json
```

An export is `{info, messages}`. In `messages[]`, `type` is `user`, `assistant`
or `synthetic`: a user message's words are `.text`; an assistant's are in
`.content[]`, whose items are `text`, `reasoning` or `tool` (a tool call's input
is `.state.input`, its failure `.state.error`); a `synthetic` message is harness
injection, not the person. Flatten an export with `jq`, or read it in slices.
Never paste a whole transcript into your own context.

# Rules

- Work only in this checkout, on <wrapup branch>. Commit there; never commit to
  <source branch> or any other branch.
- Change skills, AGENTS.md and GLOSSARY.md. Change no source code, no
  configuration, no dependency.
- Never merge the pull request, and never force-push.
- When a lesson needs judgement — two skills that should become one, a name that
  collides with an existing skill, a skill you would delete or rename — ask with
  the `question` tool and wait. When the choice is trivial and additive, decide,
  and record the alternative in the pull request body.
- Put no credentials, tokens or private paths in anything you commit.

# What to do

1. **Export every session** in the list. A session you cannot export, or choose
   not to read, must be named in the report with the reason.

2. **One digest per session**, each in a background subagent, launched in
   parallel. Give each subagent exactly one export path, the path to write its
   digest (`<state>/digests/<id>.md`), and this shape:

   - what the person asked for, in their words;
   - what was produced, and whether it worked;
   - every correction the person made to the agent's behaviour, quoted;
   - conventions, commands and values they stated that are written down nowhere
     in the repository;
   - failures, their cause, and the fix that ended them;
   - candidate lessons, each with the message it came from;
   - what here should *not* become a skill, and why.

   A digest is a claim about a transcript: quote, never paraphrase into a fact.

3. **Synthesise.** Cluster the digests into lessons. When a digest is ambiguous,
   read that part of its transcript yourself — the export is right there. Per
   lesson, decide: a new skill, an update to an existing skill, an AGENTS.md or
   GLOSSARY.md line, or nothing. A lesson that only restates what the repository
   already says is nothing.

   Use the `skill-creator` skill for every skill you write or revise. Take it as
   far as you can without a person: its anatomy, its frontmatter, and its
   description rules — the description is the trigger, so name the phrases and
   situations that should reach for the skill. Skip its eval runs and say in the
   pull request that you skipped them: they need a person to read results, and
   the skills you write are not loadable in this checkout, because OpenCode
   loads them from the global directory until this branch merges.

4. **Write the files.** `.opencode/skills/<id>/SKILL.md` for a new skill, in
   place for an existing one, in the repository the source worktree belongs to.
   Never the global config: a lesson from one project is not a rule for every
   project. Update `AGENTS.md` or `GLOSSARY.md` only where the lesson is
   guidance rather than procedure.

5. **Commit one concern per commit** — skills, then guidance, then glossary —
   with conventional messages (`feat(skill): …`, `docs(agents): …`). Before
   staging, confirm each new skill is not ignored:
   `git check-ignore -q .opencode/skills/<id>/SKILL.md` must exit 1. When the
   repository ignores `.opencode/`, do not fight the ignore rule: put the skills
   where the repository already keeps tracked skills, and say so in the report.

6. **Push and open the pull request**, ready for review, not a draft:

   ```sh
   git push -u origin <wrapup branch>
   gh pr create --base <default branch> --head <wrapup branch> \
     --title "<repository name>: lessons from <source branch>" --body-file <body>
   ```

   The body states what each skill is for, what evidence produced it, which
   sessions were read and which were not, why, and every alternative you chose
   against. Record the pull request with `trail_add` as soon as it exists.

7. **Retain the lessons in memory** with `hindsight_ingest_document`, one
   document per lesson cluster: the decision or convention, why, and the
   evidence. State plainly where a lesson supersedes something memory already
   held.

8. **Close the source worktree**, when the brief says yes — and not before the
   pull request is open.

   ```sh
   git -C <source path> status --porcelain        # must print nothing
   sqlite3 -json "$HOME/.local/share/opencode/opencode.db" "
   select id, title from session_v2
   where (directory = '<source path>' or instr(directory, '<source path>' || '/') = 1)
     and time_busy is not null
     and (time_idle is null or time_busy > time_idle)
     and time_busy > (strftime('%s','now') * 1000 - 86400000)"
   herdr-app ls | jq -r --arg w "<source path>" \
     '.spaces[] | select(.folder == $w or .name == "<source branch slug>") | .id'
   herdr-app do space.close '{"id": "<space id>", "confirmed": true}'
   git -C <main root> worktree remove <source path>
   ```

   Dirty, or a session busy within the last day: close nothing, and say what
   blocked it and where the work sits. Commits on no remote are a warning, not a
   refusal: `git worktree remove` keeps the branch, so name them and carry on.
   The space goes before the checkout, as Herdr's own remove does it. More than
   one space id: say so and close nothing until one is certain. No space id:
   remove the checkout anyway and say the space was already gone. Never delete
   the branch.

9. **Ask about this space** with the `question` tool: close it and remove this
   checkout, or leave both. Find this space by `.folder` equal to this checkout.
   On "close", write a script with the write tool that sleeps five seconds,
   closes this space, then runs `git -C <main root> worktree remove
   <this checkout>`; start it with `setsid nohup bash <script> ><log> 2>&1 &` so
   it outlives the terminal it would otherwise kill, and name the log file in
   the report. Then stop.

10. **Report**: the pull request's URL; each lesson and where it landed; the
   sessions read, and any you did not; what you did not verify; whether the
   source worktree was closed, kept, or refused, and why. Before the report,
   call `todowrite` once with every item still remaining — work only the person
   can finish, a step you could not run, a check you did not verify, a decision
   still open — each `pending`, and an empty list when nothing remains.
````

## 3a. Write the goal

The goal is what holds the reflection session to a real result. Its reviewer
judges the transcript and continues the work until the objective is met, so the
objective must be a command and its output, never a sentence about the work.

One line, to `$state/goal.md`:

```
A pull request is open from branch <wrapup branch> in <owner/name>:
`gh pr list --repo <owner/name> --head <wrapup branch> --state open --json number --jq 'length'` prints 1.
```

Keep it under 4000 characters, as `hwt` requires. Do not add the closing of the
worktree to it: the close comes after the pull request, and a second objective
makes the reviewer judge both.

## 4. Dry run, then spawn

```sh
model="$(opencode session export "$OPENCODE_SESSION_ID" |
	jq -r '.info.model | "\(.providerID)/\(.id)" +
		(if .variant then "#\(.variant)" else "" end)")"

hwt -n -r "$source_worktree" -b "$base" --agent opencode --model "$model" \
	--task-file "$state/brief.md" --goal-file "$state/goal.md" "$wrapup_branch"
hwt -r "$source_worktree" -b "$base" --agent opencode --model "$model" \
	--task-file "$state/brief.md" --goal-file "$state/goal.md" "$wrapup_branch"
```

Read the dry run before the real one: the repository, the checkout and the goal
must read as you meant. `hwt` refuses an existing checkout and an invalid
branch; report that and stop rather than choosing another name. Without
`OPENCODE_SESSION_ID`, leave `--model` out and say which default the new session
uses instead.

## 4a. `--dry-run` and `--keep`

`--dry-run`: do everything up to and including the `hwt -n` line, then stop.
Print the sessions, the wrapup branch, its checkout, the base, the pull request
target, and which space and checkout would be closed.

`--keep`: the brief's close line says no, and the worktree stays. Everything
else is unchanged.

## 5. Report

In a few lines: how many sessions and messages were sent to be read; the wrapup
branch, its checkout and the base; the model the reflection session runs; the
goal, quoted, with the paths of the brief and the goal file; and what happens
next — it reads the transcripts, opens the pull request, and closes the
worktree unless `--keep`, asking only about its own space. Then stop. Do not
wait for it here, and do not write anything into its checkout.
