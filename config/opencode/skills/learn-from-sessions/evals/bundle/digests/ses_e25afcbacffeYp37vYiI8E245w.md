# ses_e25afcbacffeYp37vYiI8E245w: Fix ADRs and requirements

## What the person asked for

One USER message, a spawning brief from the parent session. In order:

- "Read AGENTS.md, .kb/agents.md, .kb/writing-style.md and .kb/domain-docs.md first." (USER 1, line 4)
- "Fix the findings assigned to you below by editing the named documents." (USER 1, line 4)
- "Edit ONLY the files in your assignment. Other agents edit the other files in parallel. Do not commit, do not push, do not run git add." (USER 1, line 5)
- "Verify facts against the repository (code, justfile, scripts, git log/history, upstream Workshop docs) before you write. Never invent a fact. Do not change an accepted ADR's decision; clarify wording and history only." (USER 1, line 6)
- "If a finding needs an owner decision or the facts cannot be established (e.g. whether restore runs hooks, whether another agent-side DNS lookup exists), do not guess: leave the text, and report the item as open with the reason and what you found." (USER 1, line 6)
- "Run `just style <file>` on every Markdown file you changed and fix its findings." (USER 1, line 7)
- "Final answer: per finding, either "fixed: file — what changed" or "open: reason". Keep it short." (USER 1, line 8)
- "Your assignment: All findings under '### Decisions and requirements', plus the Minor suggestions for adr/* and requirements/002-proxy-egress-fence/requirements.md. Your files: adr/*.md and requirements/002-proxy-egress-fence/requirements.md." (USER 1, line 10)
- "Use git log to find ADR 0001's earlier version and what happened to number 0003." (USER 1, line 10)

## What was produced, and whether it worked

The agent's own summary: "I fixed eight of the eleven findings. One is partly fixed and two are open. `just style` reports 0 findings on every file I changed, and the extra wording changes came from that check. I did not commit or stage anything." (ASSISTANT, line 26)

Files changed, from the edits in the tool log: `adr/0001`, `adr/0002`, `adr/0004`, `adr/0005`, `adr/0006`, `adr/0007`, `adr/0008`, `adr/0009`, `adr/0010`, `adr/README.md`, and `requirements/002-proxy-egress-fence/requirements.md`.

Findings fixed, as the agent reports them:

- Old LLM rule shown as current: fixed in `adr/0001` and `adr/0005` (ASSISTANT, line 29). The current `NO_PROXY` value is stated as `localhost,127.0.0.1,::1` (ASSISTANT, line 31).
- Hooks at `restore`: fixed in `adr/0004` and `adr/0006` (ASSISTANT, line 33). The Workshop SDK reference says `setup-base` runs only at `launch` and `refresh`, and `setup-project` and `check-health` also run at `restore` (ASSISTANT, line 33).
- Passthrough count in ADR 0007: fixed (ASSISTANT, line 34). The five variables are `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`, `http_proxy` and `https_proxy` (ASSISTANT, line 34).
- "Names both values and holds no port": fixed in `adr/0005` (ASSISTANT, line 35).
- FR-028 and stashes: fixed in `requirements/002-proxy-egress-fence/requirements.md` (ASSISTANT, line 36). FR-029 is now limited to finding the instance to place or probe (ASSISTANT, line 38). "Workshop keys" is defined as `user.workshop.name` and `user.workshop.project-id` (ASSISTANT, line 39).
- Phases in ADR 0010: fixed (ASSISTANT, line 40).
- Earlier version of ADR 0001: fixed. It names the earlier title and file and commit `5c7528a` (ASSISTANT, line 41).
- Measurement count in ADR 0008: fixed. "Two" became "Four" (ASSISTANT, line 45).
- Proxy listener and policy file names: fixed. "tunnel listener" now matches `tunnel_listen` in `plane/proxy-policy.yaml` (ASSISTANT, line 49).

Findings left open, as the agent reports them:

- DNS rationale in ADR 0002: open. "I could not confirm whether any other lookup in the agent workshop still needs the resolver, so I left the rationale as it is." (ASSISTANT, line 32)
- Missing ADR 0003: open. "No commit, branch, pull request or issue I could find has ever held an `adr/0003` file. The index went from 0002 to 0004 when commit `a4029b3` added 0004." (ASSISTANT, line 44)
- "The November 12 pivot" in ADR 0001: open. "I could not confirm which event it means from the repository history, so I left it." (ASSISTANT, line 56)

Partly fixed:

- ADR index template link: fixed in `adr/README.md` (ASSISTANT, line 43).
- ADR citations and format: partly fixed. The date is removed from ADR 0002, the `.kb/project.md` references became links, and the rejected alternatives in ADR 0009 became bullets (ASSISTANT, lines 53-55).

What was verified and what was not:

- The tool log shows the `just style` loop ran over every changed file (line 109).
- The tool log shows git log, git show, and fetch commands that found commit `5c7528a` (line 61) and commit `a4029b3` (line 70), and the upstream SDK reference fetched over HTTP (lines 78-80).
- The ADR index check did not run. The command at line 112 found no `scripts/check-adr-index.py` on the branch.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

The spawning brief states workflow rules that no repository file records:

- "Edit ONLY the files in your assignment. Other agents edit the other files in parallel." (USER 1, line 5)
- "Do not commit, do not push, do not run git add." (USER 1, line 5)
- "Do not change an accepted ADR's decision; clarify wording and history only." (USER 1, line 6)
- "do not guess: leave the text, and report the item as open with the reason and what you found." (USER 1, line 6)
- "Final answer: per finding, either "fixed: file — what changed" or "open: reason". Keep it short." (USER 1, line 8)
- "Use git log to find ADR 0001's earlier version and what happened to number 0003." (USER 1, line 10)

## Failures, their cause, and the fix

No tool call failed with a `!! FAILED` marker.

One check could not run. The command `uv run python scripts/check-adr-index.py` (line 112) found no script on the review-writing branch. The agent reported: "I also did not run the ADR index check, because this branch has no `scripts/check-adr-index.py`." (ASSISTANT, line 26). The cause is the script missing from the branch, not a command error.

## Candidate lessons

- NEW — A parallel documentation fix child edits only its assigned files and never commits, pushes, or runs `git add`: "Edit ONLY the files in your assignment. Other agents edit the other files in parallel. Do not commit, do not push, do not run git add." (USER 1, line 5)
- NEW — Report a finding that needs an owner decision or unprovable facts as open instead of guessing: "do not guess: leave the text, and report the item as open with the reason and what you found." (USER 1, line 6)
- NEW — A readability review of a decision record does not change the accepted decision, only its wording and history: "Do not change an accepted ADR's decision; clarify wording and history only." (USER 1, line 6). Adjacent but not the same as `.kb/domain-docs.md` §4, which forbids silently overriding a record.
- ALREADY WRITTEN — Verify against the repository and upstream docs before writing: "Verify facts against the repository (code, justfile, scripts, git log/history, upstream Workshop docs) before you write. Never invent a fact." (USER 1, line 6). In `review-a-change/SKILL.md` "Verify before you report" and `verify-a-claim/SKILL.md`.
- ALREADY WRITTEN — Run `just style` on every changed Markdown file: "Run `just style <file>` on every Markdown file you changed and fix its findings." (USER 1, line 7). In `AGENTS.md`.
- PROJECT-SPECIFIC FACT — Workshop SDK hook timing: `setup-base` runs only at `launch` and `refresh`, and `setup-project` and `check-health` also run at `restore` (ASSISTANT, line 33). Now written into ADR 0004 and ADR 0006.
- PROJECT-SPECIFIC FACT — The five passthrough names and the NO_PROXY value: `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`, `http_proxy`, `https_proxy`, and `localhost,127.0.0.1,::1` (ASSISTANT, lines 34 and 31). Now written into ADR 0007 and ADR 0005.
- PROJECT-SPECIFIC FACT — The workshop keys are `user.workshop.name` and `user.workshop.project-id` (ASSISTANT, line 39). Now in ADR 0009 and the requirements.

## What should not become a skill

- The wording edits to each ADR and the requirements file. They are one-off corrections that now live in the records themselves.
- The git archaeology that found ADR 0001's earlier file and the missing 0003. `verify-a-claim/SKILL.md` already records "Before you create a named artifact, check the base commit for it" with `git cat-file -e` and `git log --diff-filter=A`.
- The upstream SDK reference URL. It is a source to cite, not a workflow.
