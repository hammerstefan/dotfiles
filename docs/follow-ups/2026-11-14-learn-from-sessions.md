# Follow-ups: `learn-from-sessions` evaluation and enforcement

Status: **open**. Written 2026-11-14 at the end of the session that graded the
model evaluation and turned its findings into scripted checks. These are things
to do, not a record of what was done: tick each one as it lands, and delete the
section when the whole list is closed.

The work already landed is on `master` (`8e55ce9`): the seven evaluation gates,
four skill rules, the extraction checker, and the optional critic. Nothing is
pushed.

## Do these, in this order

- [ ] 1. Try to make the four unreached corrections mechanical
- [ ] 2. Measure how unstable the judge is
- [ ] 3. Test whether a same-model second pass replaces the independent critic
- [ ] 4. Pin the five runs as a golden corpus for the citation check
- [ ] 5. Give the evaluation artefacts a durable home
- [ ] 6. Put the critic in the brief template, or record why not
- [ ] 7. Close the `GH_REPO` edge in the citation check

## Where things are

Repository: this one. Mainline is `master`; there is **no** `main` branch.
`origin/master` is 12 commits behind and unpushed by decision.

Skill tree: `config/opencode/skills/learn-from-sessions/`
- `SKILL.md` — steps 1 to 8, the report contract.
- `scripts/checks.py` — the checks; `scripts/check-extraction` runs rows 3 to 9.
- `scripts/sessions` — list and export.
- `evals/gates.py` — the seven evaluation gates, frozen; it reads `checks.py`.
- `evals/grade.py` (43 expectations), `evals/test_check_extraction.py` (16),
  `evals/test_sessions.py` (8), `evals/bundle/` (answer key and nine digests).

Evaluation artefacts, **all under `/tmp/opencode/` and therefore volatile**:
- `/tmp/opencode/learn-from-sessions-eval/report.md` — the grading record and
  all three critic experiments.
- `.../runs/<slug>/` — five collected runs (three models, two repeats).
- `.../judging/` — `judge.py`, `judge-run.sh`, `mapping.json` (the blind map;
  never show it to a judge), `prompts/`, `verdicts/run-2` to `run-8`.
- `.../critic/` — the runners, mergers and appliers; `measure3.py` reads the
  verdicts.
- `/tmp/opencode/cx/` — experiment 1: completeness critics, judged `run-6`.
- `/tmp/opencode/cx2/{a,b}/` — A: report against citations (`run-7`), B:
  sessions against the repository (`run-8`).

## Decisions not to re-litigate

- `.kb/` is in the write scope by the person's ruling; `docs/` and `tests/` are
  not. The evaluation's gates stay frozen as the record of grading; new checks
  are runtime-only rows 8 and 9.
- `mimo-v2.6-flash` stays dropped: it timed out with nothing written, and it
  gets no repeat.
- Gates disqualify, scores rank. `deepseek-v4.1-flash` was the only gate-passing
  model; `minimax` scored highest and was disqualified by gate 3.
- No critic is a step in the skill's loop. The completeness critic is offered by
  `hwt-wrapup`, because a skill cannot require a second model.
- Experiment A's two findings were mechanised, not delegated. Experiment B was
  not worth its tokens and is implemented nowhere.

## 1. The four corrections no model reaches

Five verification statuses, two-axes verification, the `gh` 2.104.0 correction,
and `gh pr edit --body-file`. Four attempts, three models, three framings, none
reached them.

The class is *record contradiction*: the repository states something and a
session disproves it. Every attempt asked "what is missing", which is the wrong
question.

Try diffing literals instead. For each digest, take the literal a command output
establishes — a version, a status word, a flag, a branch rule — and grep the
record (`.kb/`, `AGENTS.md`) for the same key. Flag where the record states a
different value. `gh` 2.45 against 2.104.0 is the easy case; the five statuses
is a vocabulary diff against the record's two.

Done when a script flags all four on the base run with no false positives. The
four are the fixture; the answer key names the exact files and quotes. If it
cannot be made mechanical, write that down and stop spending model tokens.

## 2. How unstable is the judge?

Noisier than `report.md` admits: `run-7` changed two report claims and its
"found" count rose from 17 to 24, and it was credited with the ticket-body rule
that no file gained. Three of five verdict flips in `run-6` were on artefacts
that did not change.

Judge the same run three times in fresh sessions with the same prompt and
measure agreement per expectation and per recall item. `judge-run.sh` makes this
cheap.

Done when there is a variance number. If disagreement exceeds two expectations
or two recall items, the evaluation needs two judges and an adjudicator, and the
report's counts must be labelled single-pass.

## 3. Does a same-model second pass replace the critic?

The completeness critic recovered six lessons at 2.6 times the tokens, but on a
different model. A same-model re-read of its own report with the completeness
question would cost 30 to 50 thousand tokens, not 305 thousand.

One call, same model, digests plus its own report, then apply and grade as
before. Done when the recall delta and cost are known against the six lessons
and 305 thousand tokens. If it recovers half, drop the independent critic.

## 4. A golden corpus for the citation check

`check_claims` went from 18 findings to 2 by tuning exemptions against the five
runs. Test inputs, absence statements, throwaway remotes, skill shorthand and
global-skill attribution are heuristics; an edit could swallow a real defect
silently.

Turn the five runs into fixtures with expected findings (two for `deepseek`,
none for the rest) and assert them in `test_check_extraction.py`. The runs are
in `/tmp`; copy the reports or the fixtures vanish.

Done when the corpus test fails if an exemption starts hiding a known finding.

## 5. A durable home for the artefacts

Everything except the commits lives in `/tmp/opencode/`. The report, the five
verdicts, the blind map and the experiments are the evidence behind the commits
and will not survive a reboot. Hindsight holds summaries, not the files.

Decide: a short ADR plus `report.md` under `docs/adr/` follows this repository's
own pattern; the raw runs and verdicts may belong in a tarball elsewhere. Do not
commit the 80 MB of checkouts.

Done when the report can be found from the repository, not from a temp path.

## 6. The critic is in the skill but not in the brief

`hwt-wrapup/SKILL.md` describes the optional critic; `brief.md.tmpl` does not,
and the brief is what drives the reflection session. The extraction checker is
wired into both, the critic into one.

Add a step to the template or record why it stays out. Done when the two files
agree and `hwt-wrapup/evals/grade.py --render` still passes.

## 7. `GH_REPO` and the no-remote rule

The citation check assumes `gh` cannot work without a remote, but `GH_REPO`
makes it possible. Rare, and it only causes a false positive on a report that
does not say how it ran. Add a comment or an exemption if it ever bites.

## If an agent picks this up

- `review-agent-instructions` before changing `SKILL.md` or its tests; the
  skill's own step 5 names it as the gate.
- Hindsight search before re-deriving any decision here; the experiments and the
  linter tightening are recorded in the bank.
- `git-commit-msg` for the commit style: conventional, imperative, no em dashes,
  no co-author line.
- OpenSpec skills only if a follow-up becomes a tracked change; this repository
  does not run OpenSpec.

## Gotchas

- The mainline is `master`. "Merge to main" means merge to `master`.
- Do not push without an explicit yes; the person has twice chosen to stay local.
- `evals/gates.py` is frozen. New checks go into `scripts/checks.py` as runtime
  rows, never into the gates, or the graded verdicts rewrite themselves.
- Row 9 fails every graded report by design: they predate the rule.
- `judging/mapping.json` is the blind key. A future judge must not see it.
- Graded reports cite the harness path, which lets a critic wander into the
  evaluation tree. Check every critic session for answer-key reads before
  trusting a result; one listed the live skill directory, none opened the key.
