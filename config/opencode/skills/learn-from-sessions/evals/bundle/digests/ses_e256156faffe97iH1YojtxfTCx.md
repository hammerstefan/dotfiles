# ses_e256156faffe97iH1YojtxfTCx: README section count in the feat/user-facing-readme worktree

## What the person asked for

USER 1 (line 8):

- "create a user facing README for this project. this readme must be kept up to date on every change that is user facing" (line 16)
- "Write a root `README.md` that a user reads first" (line 35)
- "Record the standing rule where agents read standing rules: add one working rule to the root `AGENTS.md` stating that every user-facing change updates the root `README.md` in the same commit." (line 37)
- "Commit on `feat/user-facing-readme` with a conventional commit subject in the form `type(scope): subject` under about 60 characters after the prefix" (line 39)
- "Do not push." (line 39)
- "Run `just style <file>` on every changed Markdown file before committing, and run `just test`." (line 45)
- "When you need a decision or a value only the person has, ask with the `question` tool and wait for the answer" (line 49)
- "The repository root has a `README.md` with at least three `## ` sections" (line 53)

USER 2 (line 101):

- "create pr" (line 102)

## What was produced, and whether it worked

- A root `README.md` with four `## ` sections: Operator commands, The workshops, Where to read more, Keeping this file current (line 93).
- A working rule in `AGENTS.md` at line 153 (line 89).
- A law in `.kb/project.md` as §3 The root README (line 94).
- Commit `048eced` with the subject "docs(readme): add the root README and its update rule" (line 90).
- Pull request #90 at https://github.com/hammerstefan/monitor-agent/pull/90 (line 116).
- A trail record for the pull request (line 119, tool log line 160).

Verified: `grep -c '^## ' README.md` printed 4, at least the 3 the person required (line 88). `grep -n 'README.md' AGENTS.md` printed line 153 with the standing rule (line 89). `just style` exited 0 with no findings (line 95). `just test` exited 0 (line 95, tool log line 148). The head commit of PR #90 is `048eced` (line 117).

Not verified: the session reported nothing left unverified (line 98). The merge of PR #90 was left to the person (line 123).

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

- `grep -c '^## ' README.md` must print at least 3 (line 53). This is the person's acceptance check for a README, not a repository rule.
- `grep -n 'README.md' AGENTS.md` must print at least one line (line 54). This is the person's acceptance check for the standing rule, not a repository rule.

The commit-subject form, the `just style` rule, and the `question`-tool rule are already written in the repository. They are not repeated here.

## Failures, their cause, and the fix

(none found)

## Candidate lessons

- Every user-facing change updates the root `README.md` in the same commit. ALREADY WRITTEN in `AGENTS.md` (line 155) and `.kb/project.md` §3. From USER 1: "this readme must be kept up to date on every change that is user facing" (line 16).
- Style-check a pull request body before posting it. ALREADY WRITTEN in `AGENTS.md` working rules (lines 135-138). From the agent: "The PR body was written to a file and passed `just style` (0 findings) before posting" (line 118).
- A commit subject uses `type(scope): subject` under about 60 characters after the prefix. ALREADY WRITTEN in `.kb/writing-style.md` §3. From USER 1 (line 39).
- A handoff that forbids a push leaves the work committed and reported as local. ALREADY WRITTEN in `AGENTS.md` working rules (lines 121-128). From the agent: "Not pushed, per the rules; working tree is clean" (line 96).
- User-facing prose uses the glossary terms. ALREADY WRITTEN in `GLOSSARY.md` and `.kb/domain-docs.md`. From the agent: "It uses the glossary terms (agent workshop, plane workshop, development workshop, fence command, proxy policy)" (line 93).

NEW lessons: 0.

## What should not become a skill

- The README section-count check `grep -c '^## ' README.md` (line 53). It is a one-off acceptance criterion for this task, not a general rule.
- The pull request creation flow `gh pr create --base main --head ... --body-file ...` (line 158). It is standard `gh` use, and the style-check part is already a working rule.
- The head-commit check `gh pr view 90 --json commits -q '.commits[0].oid'` (line 161). It is a one-off check that the push landed, not a general rule.
