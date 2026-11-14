# ses_e25a6f1b1ffe57UBQ9Zmr6GGfx: Open documentation decisions and missing facts

## What the person asked for

One turn (USER 1, line 2). The person pasted the open items from the readability review and asked to resolve them together.

- "from @docs/documentation-readability-review.md the following items remain open" (USER 1, line 3).
- "Open: these need your decision" (USER 1, line 4).
- "What counts as a sign that you are gone, in the decision-ticket skill." (USER 1, line 5).
- "The severity scale in the review skill, and which severities block a merge." (USER 1, line 6).
- "What "map order" means in .kb/issue-tracker.md." (USER 1, line 7).
- "What the operator does after workshop start or stop. The fence command has no verb for either." (USER 1, line 8).
- "Whether ADR 0002's DNS reasoning should be rewritten now that ADR 0008 sends the model call through the proxy." (USER 1, line 9).
- "when converge runs in a stack", "where the tasks-template commit goes", "the test rule", "when a workflow may edit .gitignore" (USER 1, lines 11-14).
- "Open: the facts are not in the repo" (USER 1, line 15).
- "Why ADR number 0003 is missing. No commit, branch, pull request or issue ever held it." (USER 1, line 16).
- "Which event ADR 0001 means by "the November 12 pivot"." (USER 1, line 17).
- "Nested-LXD record: the memory limit of run 3, and where the 8-second figure came from." (USER 1, line 18).
- "Whether refresh or restore also deletes files outside /project in the development workspace." (USER 1, line 19).
- "What shows that the gateway is ready ("served set")." (USER 1, line 20).
- "How long to wait between the VM disk resize and the stop." (USER 1, line 21).
- "collaborate with me to resolve these" (USER 1, line 23).

## What was produced, and whether it worked

Two commits on the review-writing branch, then PR #87 updated.

- Commits: `396daaf` feat(fence): start/stop verbs, and `3020910` docs: resolve the open items (line 69). Working tree clean.
- Code: the fence wrapper gained `start` and `stop` verbs in `monitor_agent/fence/cli.py`, plus `fence-start` and `fence-stop` recipes in the justfile, and 3 new tests (line 52).
- Docs: `.kb/fence.md`, `.kb/issue-tracker.md`, `.kb/spec-kit.md`, `.kb/development-workshop.md`, `.kb/agent-workshop.md`, the three skills, two ADRs, the ADR index, and the nested-lxd research record were edited (lines 142-154).

Verified:

- `just test`: 138 passed (line 70).
- `just style`: 0 findings on all 13 changed Markdown files (line 70).
- PR #87 body updated, open items replaced by "Resolved open items" (lines 71, 165).

Not verified:

- The fence start/stop acceptance run on the host (`just fence-acceptance`) was not run (line 73).

## Corrections the person made

The person answered each decision as a multi-choice question. Two answers differ from the option the agent marked Recommended.

- Severity scale. The agent offered "blocking/major/minor/nit; only blocking (Recommended)". The person answered "critical/high/medium/low; critical+high block" (question answer, raw export; the question was asked at line 122). This aligns the review scale with the scale in `speckit.converge`.
- Fence start/stop. The agent offered "apply after start; nothing after stop (Recommended)". The person answered "Wrapper gains start/stop verbs" (question answer, raw export; the question was asked at line 121).

The remaining six answers matched the Recommended option.

## Conventions, commands and values stated and written down nowhere

The person's answers came through the question tool, so the flattening clipped them. Each decision and fact now lives in a named file.

Decisions (the person's question answers):

- Gone signal: "Your words only". Own words in the chat or the session end. A cancelled `question` call and silence never count (asked at line 122).
- Severity scale: "critical/high/medium/low; critical+high block" (asked at line 122).
- Map order: "Sub-issue list order". The fallback is the task-list order in the map body (asked at line 121).
- ADR 0002: "Amend in place, cite ADR 0008" (asked at line 121).
- Fence: "Wrapper gains start/stop verbs" (asked at line 121).
- Converge: "Per layer, after its implement" (asked at line 123).
- Tasks-template commit: "Own commit in the base PR" (asked at line 123).
- Test rule: "Tests required per behavior" (asked at line 123).
- .gitignore: "specs/ paths only" (asked at line 123).

Facts (from git history, the tracker, and memory, stated in the summary):

- ADR 0003: "no commit, branch, PR, or issue ever held it", checked all 213 commits (line 58).
- November 12 pivot: the sandbox pivot in issue #15, reconciled with #14 (line 59).
- Nested-LXD run 3 memory limit not established. 6 GiB is reported but no command set it. The 8-second figure came from an earlier draft with no measurement. 3.56 s stands (line 60).
- refresh and restore both discard files outside `/project` (line 61).
- Gateway ready: `hermes gateway status` reports ready, which is the served set published. `hermes gateway ensure --json` exit 0 is the same state (line 62).
- VM disk resize: LXD resizes a VM root disk only while stopped. The order is stop, set memory and disk, start, then growpart/resize2fs. No wait between resize and stop because the stop comes first (line 63).

## Failures, their cause, and the fix

- websearch failed twice with HTTP 402 (lines 109, 111). The web search integration returned HTTP 402. The agent switched to `MiniMax.web_search` through `execute` (lines 116-117) and `webfetch` of the hermes gateway docs (line 118). The facts then came from git history and the tracker instead of web search.

## Candidate lessons

- The review severity scale is critical, high, medium, low, and critical and high block a merge. ALREADY WRITTEN in `.opencode/skills/review-a-change/SKILL.md` (line 107).
- A cancelled `question` call is a run limit, not an absent person. Only the person's own words or the session end is the sign that the person is gone. ALREADY WRITTEN in `AGENTS.md` (line 116) and `.opencode/skills/resolve-a-decision-ticket/SKILL.md` (lines 71-73).
- Map order is the sub-issue list order, with the task-list order in the map body as the fallback. ALREADY WRITTEN in `.kb/issue-tracker.md` (lines 121-123).
- Tests are required per behavior. Every behavior ships with an example test in the in-memory suite and `just test` passes before the layer merges. ALREADY WRITTEN in `.kb/spec-kit.md` (lines 105-108) and `.kb/project.md` §Testing.
- The fence wrapper has `start` and `stop` verbs that keep the placement because start and stop do not rebuild. PROJECT-SPECIFIC FACT in `monitor_agent/fence/cli.py` and `.kb/fence.md`.
- The gateway is ready when `hermes gateway status` reports it ready, which is the served set published. PROJECT-SPECIFIC FACT in `.kb/agent-workshop.md` (lines 86-88).
- LXD resizes a VM root disk only while the instance is stopped. PROJECT-SPECIFIC FACT in `.opencode/skills/run-a-workshop-in-a-vm/SKILL.md` (line 54).
- `workshop refresh` and `workshop restore` discard files written outside `/project`. PROJECT-SPECIFIC FACT in `.kb/development-workshop.md` (lines 49-52).
- ADR 0003 was never assigned. The pivot is issue #15. The run 3 memory limit is not established. PROJECT-SPECIFIC FACT in `adr/README.md`, `adr/0001-…`, and `research/development-workshop-nested-lxd.md`.

## What should not become a skill

- The web search HTTP 402 fallback is a tooling and environment issue, not a repository lesson.
- "The person's non-recommended choice wins" is too generic to be a skill.
- The resolution workflow (ask each decision as a multi-choice question, then search git history and memory for missing facts) describes what happened and needs no new skill. The repository's review and verify skills already cover evidence gathering.
