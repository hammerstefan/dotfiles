# ses_e25afaec7ffetPIa6SShOOeldR: Fix local skill docs

A fix child of the documentation readability review. It edits only the local
agent skills and checks each change with `just style`.

## What the person asked for

USER 1 (line 3): "You are a subagent spawned by another session."

USER 1 (line 4): "Read AGENTS.md, .kb/agents.md and .kb/writing-style.md first.
The file docs/documentation-readability-review.md lists readability findings.
Fix the findings assigned to you below by editing the named documents."

USER 1 (line 5): "Edit ONLY .opencode/skills/*/SKILL.md (the 8 local skills).
Other agents edit the other files in parallel. Do not commit, do not push, do
not run git add."

USER 1 (line 6): "Verify facts against the repository (justfile, scripts, .kb,
git, LXD/Workshop docs) before you write. Never invent a fact. Items the review
says the owner must decide (the absence signal in resolve-a-decision-ticket, the
severity scale in review-a-change, merge authority if the repo does not settle
it, VM disk resize order if unconfirmable) stay open unless the repository
already states the answer; report them open with what you found."

USER 1 (line 7): "Run `just style <file>` on every Markdown file you changed and
fix its findings."

USER 1 (line 8): "Final answer: per finding, either "fixed: file — what changed"
or "open: reason". Keep it short."

USER 1 (line 10): "Your assignment: All findings under '### Local agent skills',
plus the Minor suggestions for .opencode/skills/*."

## What was produced, and whether it worked

No commits, no pull requests, nothing staged. The handoff forbade commit, push,
and `git add`.

Seven skill files changed:

- `.opencode/skills/fence-verification/SKILL.md`
- `.opencode/skills/merge-a-pull-request-stack/SKILL.md`
- `.opencode/skills/retire-a-name/SKILL.md`
- `.opencode/skills/resolve-a-decision-ticket/SKILL.md`
- `.opencode/skills/workshop-host-authority/SKILL.md`
- `.opencode/skills/run-a-workshop-in-a-vm/SKILL.md`
- `.opencode/skills/verify-a-claim/SKILL.md`

`review-a-change/SKILL.md` was not changed. Its severity-scale finding stayed
open.

Nine findings fixed, three left open. The agent states this at line 14: "I fixed
nine findings and left three open. `just style` reports 0 findings on all seven
changed skill files. Nothing is staged or committed."

Fixed findings:

- Permission before the command, in `fence-verification`. The rebuild warning
  and the person's approval now come before `just fence-acceptance`. `just
  fence` is named an apply-only check.
- Merge authority, in `merge-a-pull-request-stack`. An agent merges only after
  the person asks for the merge in words.
- Registry read step, in `run-a-workshop-in-a-vm`. A read-only step now records
  the registry entry ids before the launch.
- Implicit targets, in `retire-a-name`, `resolve-a-decision-ticket`, and
  `workshop-host-authority`.
- Clean-tree extraction, in `merge-a-pull-request-stack`. The step extracts
  `origin/main` into a new folder under `/tmp/opencode` and runs `just test`
  there.
- Minor suggestions in `merge-a-pull-request-stack`, `fence-verification`,
  `run-a-workshop-in-a-vm`, and `verify-a-claim`.

Three findings left open:

- Decision-ticket absence signal. The repo says a cancelled `question` call is
  not an absent person, and defines no signal that the person is gone.
- Severity scale. The session reports the repo states no severity scale.
- VM disk resize order. The research records a 20 GiB disk and a partition that
  grew, but not whether the instance must stop first.

The style check ran twice in the tool log, at lines 59 and 62. The clipped
output hides the finding count, so "0 findings" is the agent's claim, not a
number read from the transcript.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

- The verification source list (line 6): "justfile, scripts, .kb, git,
  LXD/Workshop docs". No skill file records this list as a checklist for a
  documentation fix.
- The parallel division (line 5): "Edit ONLY .opencode/skills/*/SKILL.md (the 8
  local skills). Other agents edit the other files in parallel." This scopes one
  agent to the skill files while sibling agents edit other files.
- The handoff constraint (line 5): "Do not commit, do not push, do not run git
  add."
- The fix report shape (line 8): "per finding, either "fixed: file — what
  changed" or "open: reason"."
- `just style <file>` on every changed Markdown file is already written in
  AGENTS.md (line 135). Do not restate it.

## Failures, their cause, and the fix

(none found)

## Candidate lessons

1. NEW. A review finding that the review marks for the owner stays open unless
   the repository already states the answer, and the fixer reports it open with
   what it found. From USER 1 (line 6): "Items the review says the owner must
   decide ... stay open unless the repository already states the answer; report
   them open with what you found."
2. ALREADY WRITTEN. Verify a fact against the repository before writing it.
   USER 1 (line 6) says "Verify facts against the repository ... before you
   write. Never invent a fact." This restates `.kb/writing-style.md` §6, "Check
   a claim about behavior against the code before writing it."
3. ALREADY WRITTEN. Run `just style` on every changed Markdown file. USER 1
   (line 7). This restates AGENTS.md line 135.
4. ALREADY WRITTEN. A cancelled `question` call is not an absent person. The
   agent repeats this at line 18. It is already in AGENTS.md lines 116 to 120.
5. PROJECT-SPECIFIC FACT. No signal for a person who is gone, apart from the
   cancelled-`question` rule. ASSISTANT (line 18): "It defines no signal that
   the person is gone, so the owner must decide one."
6. PROJECT-SPECIFIC FACT. No severity scale stated. ASSISTANT (line 20): "The
   repository states no severity scale, so the owner must confirm one." Note:
   the current `review-a-change/SKILL.md` now states "The severity scale is
   critical, high, medium, low." This session's worktree did not see that line.
7. PROJECT-SPECIFIC FACT. The VM disk resize order was unconfirmed. ASSISTANT
   (line 23): "It does not say whether the disk change needs the instance
   stopped." Note: the current `run-a-workshop-in-a-vm/SKILL.md` now states
   "LXD resizes the root disk of a virtual machine only while the instance is
   stopped."

## What should not become a skill

- The three open items are decisions for the owner to record, not reusable
  skills. Two of them now look resolved in the current skill files. See
  candidate lessons 5, 6, and 7.
- The individual wording fixes, such as defining "branch flip", "same pass",
  "it", and "plane", correct the named documents. They carry no rule beyond the
  sentence they fix.
