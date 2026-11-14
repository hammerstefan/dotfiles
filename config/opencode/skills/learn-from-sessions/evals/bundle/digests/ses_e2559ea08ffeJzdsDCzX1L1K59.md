# ses_e2559ea08ffeJzdsDCzX1L1K59: to-spec #1

## What the person asked for

USER 1 (line 3):

> @to-spec #1

USER 2 (line 47):

> we need to apply a correction to current processes agents fall into. using
> the "wayfinder" skill and processing wayfinder mapped issue (labeled
> "wayfinder:<type>") should never write production or final code.
> experimention, spikes, exploration, grilling, and building knowledge is all
> approved. The goal is to get enough data to run "to-spec" before any realy
> implementation starts. This is particularly relevant to "wayfinder:task"
> tickets that were created that instructed to implement / build portions of
> the design, before we ever created a spec. suggest how to best guide and
> safeguard that

USER 3 (line 145):

> I approve

USER 4 (line 164):

> pull, commit your changes, push

## What was produced, and whether it worked

Two pieces of work. Both succeeded except for the final commit and push.

Piece one: a spec issue. The agent wrote a spec body to
`/tmp/opencode/spec-issue-1-egress-controlled-hermes-runtime.md`, ran two lint
gates on it, and published it as issue #91. The publish command (line 205)
created the `ready-for-agent` label and the issue in one chain:

- `gh label create ready-for-agent --repo hammerstefan/monitor-agent --description "Spec ready for an agent to implement" --color 0E8A16`
- `gh issue create --repo hammerstefan/monitor-agent --parent 1 --label ready-for-agent --title "Spec: the egress-controlled Hermes runtime" --body-file /tmp/opencode/spec-issue-1-egress-controlled-hermes-runtime.md`

The issue was read back with `gh issue view 91` (line 206), so its number,
title, label, and parent are verified. The spec body holds 34 user stories.
It passed `ste-lint.py` with 0 hard violations and `check-writing-style.py`
with 0 findings (line 43). Ten advisory passive-voice findings remained.

Piece two: the wayfinder process correction. The agent proposed a layered
safeguard, asked three `question` calls (lines 177, 213), and applied it after
the person approved. Applied changes:

- `.kb/issue-tracker.md` gained §4 (line 217) and a "Spec handoff" bullet in
  the Wayfinding operations section (line 218).
- `AGENTS.md` Issue tracker entry gained one sentence pointing at §4 (line 219).
- Map #1 and map #44 bodies were rewritten through read, patch, read back
  (lines 220, 221, 227).
- Ticket #70 got a comment gating its tree code behind a spec (line 223):
  https://github.com/hammerstefan/monitor-agent/issues/70#issuecomment-6879955474.
- The global wayfinder skill `~/.agents/skills/wayfinder/SKILL.md` was amended
  after approval (line 234). A pre-approval backup went to
  `/tmp/opencode/SKILL.md.pre-approval-backup`.
- A Hindsight initiative page was captured (line 215) and updated (line 237).

The two repo file edits passed `check-writing-style.py` (line 224). The
rewritten map bodies passed too (line 228).

Not verified: the final commit and push. The person asked for them at USER 4
(line 164). The last tool call was
`git pull --ff-only && git status --short && git branch --show-current`
(line 238). No `git commit` or `git push` call follows, and the transcript ends
there. The `.kb/issue-tracker.md` and `AGENTS.md` edits were not committed or
pushed in this transcript.

## Corrections the person made

(none found)

The person gave no in-session correction of the agent's behavior. USER 2 is a
directive to change the process, and it is quoted in full under "What the
person asked for". The only later feedback was approval (line 145) and the
commit instruction (line 164).

## Conventions, commands and values stated and written down nowhere

The person's approved activity list, in the person's exact words (USER 2,
line 47):

> experimention, spikes, exploration, grilling, and building knowledge is all
> approved

The law the session wrote enumerates "experiments, probes, provisioning, and
measurements" (.kb/issue-tracker.md §4). The word "exploration" from the
person's list is not in that enumeration. The word "grilling" appears only as
the `wayfinder:grilling` label, not as an activity in the law's list.

The person stated no new command, flag, or ticket key. The `gh` commands the
agent ran follow the conventions already in `.kb/issue-tracker.md`.

## Failures, their cause, and the fix

1. `hindsight_capture_initiative` failed on the update call (line 235). The
   error was `title: Invalid input: expected string, received undefined`. The
   call sent only `relates_to_page_id` and `summary`, and omitted `title`. The
   fix was to re-send the call with `title` set to the initiative's existing
   name (line 237). The retry succeeded.

2. The agent's own new text failed the writing style check. The new `.kb` text
   used the banned verbs `sits` and `carries`, and the map #44 text used
   "lands on the tree" (line 84). The fix rewrote them to `holds` and "enters
   the tree" (lines 225, 226, 227). These are caught violations, not tool
   errors. The banned words are already listed in `.kb/writing-style.md`.

3. The spec body's first lint run reported 22 hard violations (line 25). The
   agent fixed them in two passes, down to 0 hard findings (line 43). Ten
   advisory passive-voice findings remained, each stating a settled fact.

## Candidate lessons

- A wayfinder ticket never writes production or final code. From USER 2,
  "should never write production or final code" (line 47). ALREADY WRITTEN:
  `.kb/issue-tracker.md` §4 (this session wrote it).
- The spec issue is the map's exit child, labeled `ready-for-agent`, and is
  claimed after the map is done. From USER 2, "get enough data to run 'to-spec'
  before any realy implementation starts" (line 47). ALREADY WRITTEN:
  `.kb/issue-tracker.md` §4 and the Wayfinding operations "Spec handoff"
  bullet (this session wrote them).
- Run both gates before publishing a spec: `check-writing-style.py` and
  `ste-lint.py`. From the agent's "Both gates pass" (line 31). ALREADY WRITTEN:
  `.kb/requirements-format.md` names the `asd-ste100` skill and `ste-lint.py`
  (line 50), and `AGENTS.md` working rules require `just style` (line 135).
- "carries", "sits", and "lands" are banned figurative verbs. From the agent's
  "the repo's own checker flags `carries`" (line 29). ALREADY WRITTEN:
  `.kb/writing-style.md` Banned words (line 69).
- `ready-for-agent` is the label that signals a spec is ready to implement.
  Its description is "Spec ready for an agent to implement" and its color is
  `0E8A16` (line 205). PROJECT-SPECIFIC FACT. The label name is in
  `.kb/issue-tracker.md`, but the color and description live only in GitHub.
- A `hindsight_capture_initiative` call needs a `title` string, even on an
  update that passes `relates_to_page_id`. Reuse the initiative's existing
  title. From the failure at line 235 and the retry at line 237. NEW.

## What should not become a skill

- The wayfinder never-deliver rule. It became a repository law (§4) and a
  global skill amendment in the same session. A third copy as a new skill would
  duplicate them.
- The spec-publishing workflow. The repository already governs it through the
  `to-spec` skill, the `asd-ste100` skill, `.kb/requirements-format.md`, and
  `.kb/issue-tracker.md` §2.
- The `hindsight_capture_initiative` title gotcha. It is a single tool-call
  requirement, too small for a skill. It belongs in a tool note.
