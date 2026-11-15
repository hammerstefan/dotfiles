---
name: learn-from-sessions
description: Turn what sessions taught into repository-level skills, agents guidance and glossary terms. Use when someone says to turn this into a skill or to extract the lessons. Use when sessions must teach a repository before their worktree closes. Also use for "learn from these sessions".
---

# Learn from sessions

A session holds what the work taught. The person's corrections, the conventions
they stated, the commands that worked and the traps they hit twice stay in it.
This skill turns that evidence into what a later session reads. It writes
skills, `AGENTS.md` lines, `GLOSSARY.md` lines, a staged change and a record of
what you checked. It commits nothing. Its caller commits.

## Inputs

- **Evidence**: export paths, session IDs, or one directory that holds sessions.
  When the evidence is your own session, export it first.
- **The checkout**: the repository the knowledge belongs to.
- **The state directory**: exports, digests and the extraction report. It lives
  outside the repository. The caller names it. The default is
  `/tmp/opencode/learn-from-sessions-<slug>`.
- **The branch**: the caller's. You never create one, switch to one, or commit.

## The rules

- Change skills, `AGENTS.md`, `GLOSSARY.md`, the knowledge base under `.kb/`
  and check scripts under `scripts/`. `.kb/` is documentation, so a lesson
  that belongs there is in scope. Change no application source code, no
  configuration, no dependency.
- Put no credentials, tokens or private paths in anything you write.
- A quote from a session is evidence, not a fact. Check it before you write it.
- A lesson the repository already states is nothing. Correct the existing rule
  instead of repeating it.
- Commit nothing. Stage the change and record which paths belong to which
  concern.
- Some choices need judgement: two skills to merge, a name collision, a removal.
  Ask with the `question` tool and wait. Decide only when the choice is trivial
  and additive. Then record the alternative you chose against.

## The steps

1. **Find the evidence.** `scripts/sessions list --directory <dir>` prints JSON.
   The JSON holds every session at or under the directory, child sessions
   included. It also holds the message count, the size, the newest top-level
   session and a fallback flag. The fallback flag says the store could not be
   read and the list came from the CLI. `fallback: true` means child sessions
   are missing, so say so. Export each session you will read. A session you
   cannot export, or choose not to read, needs a reason in the extraction
   report.

   ```sh
   scripts/sessions list --directory <dir> --exclude-tree <id>
   scripts/sessions export <id> --out <state>/transcripts/<id>.json
   ```

2. **One digest per session**, each in a background subagent, run in parallel.
   Give each subagent exactly one export path, the path to write its digest
   (`<state>/digests/<id>.md`), and the shape in
   [references/digest.md](references/digest.md). A digest quotes a transcript.
   It never paraphrases the transcript into a fact.

3. **Synthesise.** Read the repository's `AGENTS.md`, `GLOSSARY.md` and existing
   skills first. Cluster the digests into lessons. When a digest is ambiguous,
   read that part of its export yourself. For each lesson, decide: a new skill,
   an update to an existing skill, an `AGENTS.md` or `GLOSSARY.md` line, or
   nothing.

4. **Check every claim** before you write it. Run every example before you write
   it and show its output. Name the version and the subcommand behind every
   claim. Record the command and its result in the extraction report.
   [references/claims.md](references/claims.md) holds the method, the scope
   rules and the traps.

5. **Write for the review.** The gate is the `review-agent-instructions` skill:
   context efficiency, reliability, description and trigger, scriptability,
   style. Write so that each one passes. Use the `skill-creator` skill for a new
   or revised skill. Use the `writing-for-agents` skill for the wording of a
   skill, `AGENTS.md` or `GLOSSARY.md`. Run its evals when you can exercise the
   skill without new infrastructure. An eval that needs the skill loaded in this
   session cannot run. OpenCode discovers a skill at session start. Say in the
   extraction report which evals you ran and which you did not.

6. **Write the files.** `.opencode/skills/<id>/SKILL.md` for a new skill, in
   place for an existing one, in the repository the evidence belongs to. Never
   the global config. A lesson from one project is not a rule for every project.
   Put a check script under the repository's `scripts/` directory. Update
   `AGENTS.md` or `GLOSSARY.md` only where the lesson is guidance rather than
   procedure.

   A rename touches the skill ID, the frontmatter name, the heading, `AGENTS.md`
   and the trigger phrases. Update every one.

   Before you stage, run `git check-ignore -q .opencode/skills/<id>/SKILL.md`. It
   must exit 1. Run `git check-ignore -q scripts/<name>` for each new script.
   That must also exit 1. When the repository ignores `.opencode/`, do not fight
   the ignore rule. Put the skills where the repository already keeps tracked
   skills, and say so in the extraction report.

7. **Run the checks.** Run every script you wrote. Run the repository's test
   command when the change can reach the code it tests. When the change cannot
   reach that code, do not run it: name the checks that cover the changed paths
   instead. Say in the extraction report why the test command ran or did not
   run. Run the linter on
   every changed file, before and after your change. Put both counts in the
   extraction report, and add no new finding. Run the banned-word grep over
   every changed file.

   Prove each check fails on a planted defect before you trust its pass. A check
   that cannot fail proves nothing. A step with one right answer and no
   judgement is a script. It has an exit code and a line that names what failed.
   A banned-word grep, a header-spacing check, a branch-name collision test and
   a file-list check are scripts. Run it with the other checks.

8. **Review your own change, then stage it.** Use the `review-agent-instructions`
   skill for the pass. Read every changed file whole. For each criterion, state
   pass or fail with evidence. Correct every defect you can. Name each finding
   you leave and say why. The verdict must agree with the findings. "Ready" with
   an open major finding is not a verdict.

   Then `git add` every file you changed and write the extraction report.

   **Run the completeness pass.** Read the digests again against the report and
   name every required lesson it does not cover. Add each one, or record why you
   rejected it. An author misses what a second reader finds: on the measured
   bundle an independent critic recovered six lessons the extraction had left
   out. When the caller can spawn one on another model, hand it the digests and
   the report, apply what survives your own check, and run the check below again
   after you apply.

   Run `scripts/check-extraction --repo <the checkout> --report
   <state>/extraction.md --digests <state>/digests`. It checks the rules that
   have one right answer: the write scope, the report's sections, the secret
   scan, the ignore rule, the session accounting, every repository citation the
   report makes, and that the completeness pass is recorded. A non-zero exit
   means the extraction is not ready. Correct every failing check and run it
   again. The check reads the report, so run it after the report is written.

## The extraction report

Write `<state>/extraction.md`. It is the one thing the steps after this skill
read. It holds:

- each lesson, the files it became, and the concern it belongs to.
- the concern map: one concern per commit, its paths, and its commit message.
- the Checked section: one line per claim with the command, the version and the
  result.
- the claims you did not check.
- the linter counts before and after.
- each hard finding that remains, named with its justification.
- the evals you ran and the ones you did not, with the reason.
- what the completeness pass found, and each lesson it left out with the reason.
- the self-review verdict and its evidence.
- the IDs of the sessions you read and the ones you did not, with the reason.
- any copy of a corrected claim outside the repository, and where you corrected
  it.
- the alternative you chose against, where you decided alone.

## The files

- `SKILL.md` — this.
- `references/digest.md` — the export shape, how to read one in slices, and the
  digest shape.
- `references/claims.md` — how to check a claim, scope it, and reach every copy.
- `scripts/sessions` — `list` and `export` for the sessions of a directory.
- `scripts/check-extraction` — the mechanical checks the extraction must pass
  before it is ready. `scripts/checks.py` holds the rules, shared with the
  evaluation gates.
- `evals/` — the assertions this skill and its references must satisfy.
