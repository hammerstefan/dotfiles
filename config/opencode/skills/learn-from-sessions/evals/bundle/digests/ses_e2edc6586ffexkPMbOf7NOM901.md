# ses_e2edc6586ffexkPMbOf7NOM901: Review the fence PR stack

Positions are line numbers in `flat/ses_e2edc6586ffexkPMbOf7NOM901.txt`. The
conversation is the whole file, lines 1 to 72. The tool log starts after
`@@TOOLS@@` at line 73.

No turn of the person appears in this session. The single user block, lines 2
to 64, is the brief of the delegating session
`ses_e2fa0b018ffeiQJxQdJlZNMTnU`, which wrote it for a `review-minimax`
subagent. Every "you" below is that delegating session addressing the
reviewer, not the person.

## What the person asked for

(none found). The person wrote nothing in this session. The brief asks, in its
own words (2 to 64):

- "Review all changes in the open PR stack for ticket #20 (the proxy egress
  fence) in the monitor-agent repository." (4).
- "The stack is four branches, each PR based on the one before it:" (11),
  naming `wayfinder/proxy-egress-fence` as PR #32 to `main`, `-state` as #33,
  `-probe` as #34, and `-wrapper` as #35 at the top (13 to 16).
- "Review the complete stack as one change set. The authoritative command is:"
  then "git diff main...wayfinder/proxy-egress-fence-wrapper" (18 to 20).
- "use three-dot diffs (`...`) against the merge base, and ignore the merge
  commits themselves" (22).
- "Adversarial review, concrete and cited. Prioritize, in this order:" (51),
  then security and fail-open defects, correctness against the requirements,
  test adequacy, and architecture (53 to 56).
- "For every finding: severity (blocking / should-fix / nit), `file:line`, what
  is wrong, why it matters, and the smallest correct fix." (58).
- "You may run the test suite read-only:" then
  ".venv/bin/python -m pytest tests/ -q" (60 to 62).
- "Do not modify files, do not commit, do not push, and do not create or edit
  issues or pull requests. Do not run anything that creates, changes, or
  deletes LXD or Workshop state." (64).

## What was produced, and whether it worked

Nothing was produced. The reviewer made four assistant turns and eight tool
calls, then the provider ended the run.

The tool log records these calls, in order (74 to 81): `hindsight_list_pages`,
`review_inspect` with `status`, `hindsight_search_pages`,
`review_inspect` with `pr_diff` for pull request 32, `review_inspect` with
`pr_files` for pull request 35, `glob` on `monitor_agent/fence/*.py`, `read` of
`monitor_agent/fence/config.py`, and `read` of
`monitor_agent/fence/apply.py`.

The flatten holds no `!! FAILED` line. The raw export
`transcripts/ses_e2edc6586ffexkPMbOf7NOM901.json` records the end: message
index 6 finished with `"type": "provider.quota"`, status 429, the message
"Token Plan usage limit reached: Upgrade your Token Plan or purchase Credits
for more usage. (2056)", and message index 7 is an idle record with
`"outcome": "failed"`.

The session record also holds `"outcome": "failed"`, 349 output tokens, and a
cost of 0.0135. No finding, no severity, and no report reached the delegating
session. The delegating session reported the failure to the person at
position 598 of its own transcript, and offered four ways forward. The person
dismissed that question and had the review done elsewhere.

## Corrections the person made

(none found). The person made no turn in this session.

## Conventions, commands and values stated and written down nowhere

- The review target is named by its diff, not by its files: "The authoritative
  command is:" then `git diff main...wayfinder/proxy-egress-fence-wrapper`
  (18 to 20).
- Three-dot diffs against the merge base, with merge commits ignored (22).
- The severity vocabulary is "blocking / should-fix / nit" (58).
- Each finding names `file:line`, the fault, why it matters, and "the smallest
  correct fix" (58).
- The reviewer states what it checked that turned out fine: "If you verify
  something is actually fine that looks suspicious, say so briefly — I want to
  know what you checked." (58).
- The settled constraints are listed so the reviewer does not reopen them,
  under the heading "Constraints that are settled (do not ask to change
  these)" (41 to 47). Two of them are stated as values: "The agent workshop
  `agent/` and the plane workshop `plane/` are separate Workshop projects."
  (43), and "Requirements are numbered 002 because 001 was withdrawn; numbers
  are never reused." (44).
- The reviewer's test command is `.venv/bin/python -m pytest tests/ -q` (62).
  The repository's `justfile` runs its suite through `uv run pytest tests/`,
  and `.kb/project.md` states "`just test` runs the suite".

## Failures, their cause, and the fix

1. The review ended before it began its reading. The raw export records
   `"type": "provider.quota"`, status 429, "Token Plan usage limit reached:
   Upgrade your Token Plan or purchase Credits for more usage. (2056)". Cause:
   the MiniMax account quota for the `review-minimax` agent, not a fault in the
   change set. Fix: none inside this session. The delegating session offered
   three fallbacks and one stop option, and its tool log records the outcome as
   "The user dismissed this question" (line 1217 of its transcript). The
   person had the review done out of band.
2. The reviewer had read two of the five implementation files when it stopped
   (a `read` of `config.py` at 80 and of `apply.py` at 81). Its first edit or finding never
   existed, so a partial review may not be reported as a review.

## Candidate lessons

1. Write a review brief around the diff command and the merge-base rule, so
   the reviewer reads the change set and not the merge commits. Quote: "use
   three-dot diffs (`...`) against the merge base, and ignore the merge
   commits themselves" (22). NEW.
2. State the settled constraints in the review brief, so the reviewer cannot
   spend the review reopening a decision. Quote: "Constraints that are settled
   (do not ask to change these)" (41). NEW.
3. Give the reviewer an ordered list of what to look for first, with security
   and fail-open defects at the top. Quote: "Adversarial review, concrete and
   cited. Prioritize, in this order:" (51). NEW.
4. Require a severity, a `file:line`, the fault, why it matters, and the
   smallest correct fix for every finding. Quote (58). NEW.
5. Ask the reviewer to report what it checked and found sound. Quote: "If you
   verify something is actually fine that looks suspicious, say so briefly — I
   want to know what you checked." (58). NEW.
6. A read-only review brief names the writes the reviewer must not make and
   the host state it must not touch. Quote: "Do not modify files, do not
   commit, do not push, and do not create or edit issues or pull requests. Do
   not run anything that creates, changes, or deletes LXD or Workshop state."
   (64). NEW.
7. A delegated reviewer can end on a provider quota with no findings, so the
   caller checks that a review exists before it reports one. Quote: "Token
   Plan usage limit reached: Upgrade your Token Plan or purchase Credits for
   more usage. (2056)" (raw export, message index 6). NEW.
8. Name the repository entry point in a review brief, not an interpreter path.
   The brief names ".venv/bin/python -m pytest tests/ -q" (62). ALREADY
   WRITTEN in `.kb/project.md` §Testing ("`just test` runs the suite") and in
   `AGENTS.md` ("An action runs the repository entry point, never a copy of its
   command: `just test`, not `pytest`").
9. A pull request stack is reviewed as one change set, with per-PR slices for
   the layer boundaries. Quote: "Review the complete stack as one change set."
   (18) and the per-PR slice list (22). NEW. `.kb/spec-kit.md` states how a
   stack is built, not how it is reviewed.

## What should not become a skill

- The four branch names and pull request numbers. They describe one ticket's
  stack, and a skill would go stale as soon as the stack merged.
- The MiniMax model name, its agent name `review-minimax`, and its quota
  message. Provider account facts, not repository knowledge.
- The project layout `agent/` and `plane/` as a review constraint. It is a
  settled decision, already recorded in ADR 0006, and the brief only repeated
  it.
- The requirements numbering statement in the brief. ALREADY WRITTEN in
  `.kb/requirements-format.md` §4, and the brief repeated it to keep the
  reviewer from raising it.
- The `review_inspect` tool calls. They are one harness's interface, and a skill
  that named them would break on another harness.
