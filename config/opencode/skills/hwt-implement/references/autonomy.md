# Autonomous mode

The person is away. The session must reach the ticket's end state without them,
and must leave them a record they can audit in one sitting. Judge a decision by
one test: can the person re-derive it from the evidence in under a minute?

## Write the decision log as you go

Keep `<run dir>/decisions/<slug>.md`, and append a block when you decide, not
at the end. A session that pauses, faults, or hits its context limit still
leaves everything decided before that point.

```markdown
## D3 Shorten the refresh check, not the hermes hook

- Choice: force the rebuild with a new SDK slot instead of editing the hook.
- Options: (a) change the hook's cache (b) change what the check changes.
- Evidence: `conformance/test_fence.py:156` reads the definition's SDK list;
  the hook is `agent/.workshop/hermes/hooks/setup-base:14`.
- Why this one: it keeps the change inside the file this ticket owns, so
  #116's hook work merges cleanly.
- Reversible: yes, one file.
- For the person: nothing to confirm.
```

Batch the log into the final report under `## For review`. Never write a
decision only in the transcript.

## Ask only what is the person's

The `question` tool is for three things: a value only they hold, a credential,
or a scope call that changes what the ticket is. Everything else is yours to
settle with evidence: read the code, run the probe, quote the output.

When a decision is reversible and inside the ticket's acceptance criteria,
decide it. Record it, and say in the PR body that the person may overturn it.
Some decisions are not yours: a destructive step, money, a claim on another
ticket, or a wider scope. Ask for those. If no answer comes, stop and report
rather than guess.

## Explore options without thrashing

Two plausible mechanisms is normal. Four is scope creep. Bound the look:

- one probe or one measurement per candidate, inside the ticket's own cost
  bound (a conformance run, a single build).
- stop at the number that separates them, not at a fully polished two-way
  implementation.
- implement one. The other goes in a `Candidates considered` table with the
  evidence that rejected it, so the next person does not re-run the same probe.

## Never invent a number a criterion compares against

When a criterion says "below the baseline that #114 sets" and #114 has not run,
measure it yourself and label it `self-measured`. Name the missing baseline in
the PR body and the decision log. A borrowed or guessed baseline is a false
claim in a record that later work trusts.

## Waiting is visible

A held lock, a busy host, a queue. Poll with a fixed schedule: 30 s, then 60 s,
then 120 s. Print one line per poll naming the holder and the elapsed time, and
record the wait in the decision log. Stop at the bound the brief gives and
report the block. A sleep loop with no output looks like a hung session, and the
person cannot tell a wait from a fault.

## Order the work around the contended thing

Do every step that needs no shared resource first: the code, the unit tests,
the docs, the review. A host run is then the only thing left, so a wait costs
nothing and an abandoned wait leaves a nearly complete branch.

## A fault is data

Record the evidence, and retry once when the cause is outside your change
(another session's run, a timeout, a stop signal). Retry the same way, not
harder. A second failure goes in the report with its output. Do not spend the
session on a third.

## Stop at the goal

The goal's command passing is the stop condition. Then write the decision log
summary, the todo list of person-only work, and the four-part report. Work you
notice along the way becomes a follow-up line in the report, not a detour.

## What the person reads first

End the report with `## For review`, holding:

- every decision from the log, one line each, with its evidence.
- the options you rejected and why.
- what you could not verify, and the command that would verify it.
- the host state you left (VMs, images, locks, branches, PRs).
- the one question, if any, still theirs.
