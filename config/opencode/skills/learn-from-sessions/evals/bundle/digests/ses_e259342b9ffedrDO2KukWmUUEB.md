# ses_e259342b9ffedrDO2KukWmUUEB: Branch rebase and push

## What the person asked for

- USER 1 (line 3): "rebase this branch push"

## What was produced, and whether it worked

- The `review-writing` branch was rebased onto `origin/main` (line 13). It held 3 commits that `main` did not have, and `main` had moved ahead.
- Two files conflicted. Both conflicts were the branch's readability commit `443c6ae` against newer wording on `main` (line 14).
- In `AGENTS.md`, the agent kept `main`'s expanded handoff-push rule (line 15).
- In `adr/0001-hermes-runs-in-a-fenced-agent-workshop-and-a-plane-workshop-proxy-mediates-its-web-egress.md`, the agent kept `main`'s "No other instance uses the bridge" (line 16).
- `just style` ran on the two resolved files and reported 0 findings (line 17, line 33).
- The push used `git push --force-with-lease origin review-writing` and needed a force update because the rebase rewrote the pushed commits (line 18, line 34).
- The branch then held `83c236f`, `e53fdd8`, and `f668623` on top of `main` (line 20).
- Verified: the `just style` run passed with 0 findings, and the push succeeded. Both are `ok shell` entries (line 33, line 34). Nothing else was stated as verified.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

(none found)

## Failures, their cause, and the fix

(none found)

## Candidate lessons

- Keep `main`'s wording when a branch rewrite conflicts with newer wording on `main`. From "Per the repo rule — read the record on `main` before amending a copy of it on your branch — `main`'s wording wins in both files." (line 9, assistant). ALREADY WRITTEN in `AGENTS.md` lines 101-103.
- A rebase rewrites the pushed commit hashes, so a posted comment that names a `blob` hash is a dead link. From "If any posted comment named a blob hash on the old commit, it's now a dead link" (line 20, assistant). ALREADY WRITTEN in `AGENTS.md` lines 121-128 and in `.opencode/skills/merge-a-pull-request-stack/SKILL.md` line 82.
- Run `just style` on changed Markdown files before a commit. From "Style check: `just style` on the two resolved files — 0 findings" (line 17, assistant). ALREADY WRITTEN in `AGENTS.md` line 135.
- Use `git push --force-with-lease` to push after a rebase that rewrote pushed commits. From "`git push --force-with-lease` → `443c6ae...f668623` (force update was needed since the rebase rewrote the pushed commits)" (line 18, assistant). NEW. No repository file names the force flag.

## What should not become a skill

- The `--force-with-lease` flag is general git practice, not a monitor-agent rule. It fits as one line in the existing merge or rebase guidance, not as a skill of its own.
