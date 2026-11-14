# ses_e25aff063ffem9EKGrJ14ISypE: Fix project guidance docs

## What the person asked for

USER 1 (line 3): "You are a subagent spawned by another session."

USER 1 (line 4): "You work in the git checkout /home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/review-writing (repo monitor-agent). Read AGENTS.md, .kb/agents.md and .kb/writing-style.md first."

USER 1 (line 4): "The file docs/documentation-readability-review.md lists readability findings. Fix the findings assigned to you below by editing the named documents."

USER 1 (line 11): "Your assignment: All findings under '### Project guidance', plus the Minor editorial suggestions that touch AGENTS.md, GLOSSARY.md, .kb/spec-kit.md, .kb/requirements-format.md, .kb/writing-style.md, .kb/project.md, .kb/issue-tracker.md, .kb/spikes.md, .kb/topologies.md, .kb/domain-docs.md."

USER 1 (line 11): "Also the '### Generated Spec Kit prose and local integration' findings, implemented ONLY as local guidance in .kb/spec-kit.md (when a constitution is active, numbering rule at the invocation point, how to limit implement to one layer and when converge runs, test rule, when a workflow may edit .gitignore, a user story is not automatically a PR layer) — only where the repository's facts support the rule; otherwise report open."

USER 1 (line 11): "Your files: AGENTS.md, GLOSSARY.md, and those .kb files. Another agent aligns .kb/agent-workshop.md and diagram labels to the glossary terms; state the defined capitalization terms in your final answer."

## What was produced, and whether it worked

No commits, branches, pull requests, or records. The session edited files in place in the `review-writing` worktree and reported the result as its final answer.

The agent's summary (line 13): "I fixed most of my assigned findings. Six items stay open because the repository does not hold the facts or decisions they need. `just style` reports 0 findings on every Markdown file I changed. Nothing is staged or committed."

Fixes the agent reported (lines 15-49):

- fixed: `AGENTS.md`. The frontier rule now excludes children with an assignee and children with an open blocker, and it points to `.kb/issue-tracker.md` (line 16).
- fixed: `.kb/project.md` §2. The default record rule and the stack record rule are two sentences. A bug-fix or urgent label still needs a record for an architecture decision (line 17).
- fixed: `.kb/spikes.md` §7. The text says "the findings record" (line 18).
- fixed: `.kb/topologies.md` §4. It gives `https://cdn.jsdelivr.net/npm/mermaid@<version>/dist/mermaid.min.js` and says the pages use version `12.3.0`, taken from the existing HTML page (line 19).
- fixed: `GLOSSARY.md`. Capitalization is defined, the fence command entry lists `launch`, `refresh`, `restore`, `remove`, and the "agent workshop" entry says Hermes Agent (line 20).
- fixed: `GLOSSARY.md`. "Verb" is defined under the control service entry with a link to ADR 0010. The bound entry separates the request limit from the reach of caller-written code (line 21).
- fixed: `.kb/topologies.md`. "Entry" is now "`.kb/*.md` file" (line 22).
- fixed: `.kb/spec-kit.md` and `.kb/requirements-format.md`. The "why requirements" rationale and the move procedure appear only in `requirements-format.md`, and `spec-kit.md` links to it (line 26).
- fixed: `AGENTS.md`. The warning about `blob` links now refers to `.kb/issue-tracker.md` (line 27).
- fixed: `.kb/writing-style.md`. "As one" now reads "as a plan or an intention" (line 28).
- fixed: `.kb/requirements-format.md` and `.kb/spec-kit.md`. "Deposit" is replaced. The `spec-kit.md` §3 heading is now "Spec Kit output stays untracked" (line 29).
- fixed: `AGENTS.md`. "Reads the ref" now names `--ref` (for example `origin/main`) and says the script reads the working tree when `--ref` is absent (line 30).
- fixed: `.kb/project.md`. The duplicate "Planned runtime" section is merged into one with a bulleted list (line 31).
- fixed: `.kb/issue-tracker.md`. The `gh` 2.104.0 version is stated once, in its last convention item (line 32).
- fixed: `.kb/spikes.md` and `.kb/spec-kit.md`. Removed "lives on", "lands", "carries", "itself" and "exactly". The `AGENTS.md` handoff rule is now a direct instruction (line 33).
- fixed: `.kb/spec-kit.md` §5. No constitution is active until it is filled in through `speckit.constitution`. Until then a command skips its constitution checks (line 36).
- fixed: `.kb/spec-kit.md` §4. Give the number each time you invoke `speckit.specify`. The generated command does not know this rule (line 37).
- fixed: `.kb/spec-kit.md`. A user story is not automatically a pull request layer (line 38).
- partly fixed: limiting work to one layer. Each task group now runs on the branch of its layer (line 39).

Items the agent left open (lines 23, 40-43):

- open: "map order" in `.kb/issue-tracker.md`. Neither the wayfinder skill nor the repository says whether it means sub-issue order, task-list order or issue number. The owner must decide (line 23).
- open: when `converge` runs in a stack, and where the tasks-template commit belongs. The repository has no record of either (line 40).
- open: test rule. The repository has no decision on test-first work or optional tests. `.kb/project.md` describes the suite only (line 41).
- open: when a workflow may edit `.gitignore`. No repository fact supports a rule. "I drafted one and then removed it." (line 42).
- open: the requests to upstream. They are outside this checkout (line 43).

Verified: the agent states `just style` reports 0 findings on every changed file and nothing is staged or committed (line 13). These are the agent's claims. The transcript shows no `git diff` output that a reader could use to confirm the file contents.

Not verified: the transcript does not show the edited files. It shows only `git diff --stat` at the last command (line 61), with no output in the flattened file.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

USER 1 (line 5): "Edit ONLY the files in your assignment. Other agents edit the other files in parallel."

USER 1 (line 5): "Do not commit, do not push, do not run git add."

USER 1 (line 6): "If a finding needs an owner decision or the facts cannot be established, do not guess: leave the text, and report the item as open with the reason."

USER 1 (line 9): "Final answer: per finding, either "fixed: file — what changed" or "open: reason". Keep it short."

Stated but already written down, so not new:

- USER 1 (line 6): "Verify facts against the repository (code, justfile, scripts, ADRs, git log/history, upstream docs via web) before you write. Never invent a fact." This matches `.opencode/skills/verify-a-claim/SKILL.md`, named in `AGENTS.md` line 73.
- USER 1 (line 7): "Do not edit generated Spec Kit files (.opencode/commands/speckit.*, .specify/**)." This is `.kb/spec-kit.md` §1.
- USER 1 (line 8): "Run `just style <file>` on every Markdown file you changed and fix its findings." This is `AGENTS.md` line 135.

## Failures, their cause, and the fix

(none found)

## Candidate lessons

- NEW: "If a finding needs an owner decision or the facts cannot be established, do not guess: leave the text, and report the item as open with the reason." — USER 1 (line 6). The agent applied it by leaving six items open (line 13) and removing a drafted `.gitignore` rule it could not support (line 42).
- ALREADY WRITTEN: "Do not edit generated Spec Kit files (.opencode/commands/speckit.*, .specify/**)." — USER 1 (line 7). Written in `.kb/spec-kit.md` §1.
- ALREADY WRITTEN: "Run `just style <file>` on every Markdown file you changed and fix its findings." — USER 1 (line 8). Written in `AGENTS.md` line 135.
- PROJECT-SPECIFIC FACT: "**Workshop**" is the product, "**workshop**" is one environment, "**Hermes Agent**" is the product and `hermes` is its command — ASSISTANT (lines 45-49). Now recorded in `GLOSSARY.md` lines 8-12.

## What should not become a skill

- USER 1 (line 5): "Edit ONLY the files in your assignment. Other agents edit the other files in parallel. Do not commit, do not push, do not run git add." This is the orchestration of one parallel documentation review across worktree agents, not a reusable workflow rule.
- USER 1 (line 9): "Final answer: per finding, either "fixed: file — what changed" or "open: reason"." This is the report format for this one review task, not a general skill.
