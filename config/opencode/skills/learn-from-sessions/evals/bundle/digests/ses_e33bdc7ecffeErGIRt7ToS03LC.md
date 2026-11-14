# ses_e33bdc7ecffeErGIRt7ToS03LC: Research hermes execution model (ticket #2)

## What the person asked for

The session holds one prompt. It was written by the spawning session
(`ses_e33d0c7c5ffejcYl5L4FlzKPPv`), not by the human, and no human turn appears
in this transcript (flat:3-25).

- "TICKET: issue #2 "Research the hermes execution and configuration model",
  label wayfinder:research, child of map issue #1" (flat:6).
- "UNKNOWN: the upstream project location, install method, execution
  architecture, and configuration model. This ticket must find them." (flat:12)
- "Candidate identities must be verified against the known upstream terms
  (`skill`, `toolset`, `plugin`) and the autonomous-command-running behavior
  before you commit to one. If you cannot identify it unambiguously, state that
  plainly in the findings and list every candidate you checked with why it fits
  or does not. Do not guess silently." (flat:16)
- "Distinguish upstream documentation claims from what you could not confirm."
  (flat:18)
- "Commit: ... No AI or tool attribution anywhere." (flat:19)
- "git push -u origin research/hermes-execution-model. Never open a PR. Never
  merge." (flat:20)
- "Do NOT edit issue #1 (the map owner appends the decision pointer)." (flat:21)
- "Never run any script from spike/ branches. Never launch, refresh, or remove
  anything. Never print or commit secret or credential contents." (flat:23)
- "FINAL REPLY to me: the ticket number, the branch name, the verdict in at most
  five sentences, and any fact you found that contradicts the repo's records in
  adr/ or research/." (flat:25)

## What was produced, and whether it worked

- Branch `research/hermes-execution-model`, commit `66b94e9`, holding
  `research/hermes-execution-model.md` (flat:71, flat:124). The file is not on
  `main` today, so the record lives on the branch only.
- Resolution comment posted on #2 and the issue closed (flat:125). The tool log
  shows the comment command and the close in sequence.
- Two trail entries (flat:126-127).
- The verdict, as the agent reported it: upstream is
  `NousResearch/hermes-agent`. One `terminal` tool selects a backend through
  `terminal.backend` in `~/.hermes/config.yaml`. A sandbox integrates as a
  terminal environment provider plugin implementing `create_environment()` and
  returning `execute(command, timeout)` and `cleanup()`. Configuration is
  `config.yaml`, credentials come from `.env` or pluggable secret sources, an
  OpenAI-compatible endpoint is set through `model.provider: custom` with
  `model.base_url`, and about 28 toolsets are toggled with `hermes tools`
  (flat:73).
- Contradictions with the repository records: the agent reported none. It named
  one adjacent fact, that "upstream ships its own egress control, `hermes
  egress` (iron-proxy), a TLS-intercepting credential-injection proxy that runs
  as a subprocess on the same host as the agent and covers the Docker backend
  only" (flat:75).
- Not verified: nothing beyond the documentation read. No hermes process was
  installed or run in this session.

## Corrections the person made

(none found). The one prompt-level constraint that the session bent is the
report length. The prompt asked for "the verdict in at most five sentences"
(flat:25) and the reply spends five long sentences on the verdict plus a
contradiction section (flat:73-75).

## Conventions, commands and values stated and written down nowhere

- The review pass the agent ran on its own file: grep for the banned patterns
  before the commit, with the pattern list
  (`;|—|–|\bjust\b|\bsimply\b|...|first-class|surface area|load-bearing|...|
  \bmint\b|\bminted\b|\brid(e|es|ing)\b|\blands\b|\bcarries\b|\blives in\b|
  \bsits\b|\bjoins\b`) (flat:115). The repository states the practice in
  `AGENTS.md`. The working pattern list is one session's own.
- Heading fixes the agent applied for the noun-phrase rule: "### Where commands
  run" to "### Execution backends", "### Toolsets and disabling them" to
  "### Toolsets", "### Upstream egress features, read against ADR 0001" to
  "### Upstream egress features and ADR 0001" (flat:111-113).
- The upstream install command the findings record:
  "`curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`"
  (flat:73).
- The docs index route that made the whole documentation set readable:
  `https://hermes-agent.nousresearch.com/docs/llms.txt` (flat:93).

## Failures, their cause, and the fix

- `webfetch` of `https://hermes-agent.nousresearch.com/docs/reference/toolsets-reference`
  answered `StatusCode: non 2xx status code (503 ...)` twice (flat:102-106).
  Cause: the docs site answered 503, not a wrong path. Fix: the agent took the
  same page from the repository source,
  `https://raw.githubusercontent.com/NousResearch/hermes-agent/main/website/docs/reference/toolsets-reference.md`
  (flat:108).
- An `edit` call failed with "Could not find oldString in
  research/hermes-execution-model.md. It must match exactly, including
  whitespace and indentation." (flat:119-120). Cause: the agent guessed the
  line wrapping of the sentence it wanted to change. Fix: it re-ran the edit
  with the preceding word ("that flag.") as anchor (flat:123).
- `gh issue view 2` returned a Projects-classic GraphQL deprecation error.
  Cause: the default template of `gh issue view` queries a deprecated field on
  this host's `gh`. Fix: read the issue with `--json` or with
  `gh api repos/<owner>/<repo>/issues/<n>` (flat:29, flat:81-82).

## Candidate lessons

1. NEW. `gh issue view <n>` without `--json` fails on this host with a
   Projects-classic GraphQL deprecation, so an issue is read with `--json` or
   with `gh api`. Quote: "`gh issue view` hit the Projects-classic GraphQL
   deprecation. I'll query with `--json` instead" (flat:29). The practice is
   already in `.kb/issue-tracker.md`, Conventions, but the failure and its cause
   are written nowhere.
2. NEW. A documentation page that answers 503 is recovered from the project's
   docs directory on `raw.githubusercontent.com`, which serves the same source
   file. Quote: "The toolsets page keeps failing on the docs site. I'll take it
   from the repository source directly (raw GitHub), same content." (flat:51).
3. NEW. An upstream identity is confirmed by matching the repository's own known
   terms before the findings are written. Quote: "Candidate identities must be
   verified against the known upstream terms (`skill`, `toolset`, `plugin`) and
   the autonomous-command-running behavior before you commit to one." (flat:16).
   The session did that in one turn and recorded the match (flat:35).
4. ALREADY WRITTEN. Grep the drafted file for the banned words and punctuation
   before the commit. `AGENTS.md`, last bullet of "Workshop definition rules".
5. ALREADY WRITTEN. No AI or tool attribution in a commit. `.kb/writing-style.md`
   §7.
6. PROJECT-SPECIFIC FACT. The hermes execution model: one `terminal` tool, the
   backend key `terminal.backend`, the plugin contract, and the file tools that
   run through the backend unless it declares `uses_host_filesystem`. This
   belongs in `research/hermes-execution-model.md` on its branch, and in
   whatever record the current design needs. It decided nothing that stands
   today, because `adr/0001` runs hermes with full control of its container.
7. PROJECT-SPECIFIC FACT. `model.provider: custom` with `model.base_url` takes
   any OpenAI-compatible endpoint. `.kb/agent-workshop.md` now depends on this
   fact and goes further: it names a custom provider because "hermes derives the
   transport of a bare `provider: custom` entry from the endpoint host".
8. PROJECT-SPECIFIC FACT. Upstream `hermes egress` (iron-proxy) is a
   TLS-intercepting proxy in the agent's own host. `adr/0001` rejected that
   shape, then adopted iron-proxy run standalone in the plane. The adjacency is
   recorded in `adr/0001` and worth one sentence wherever the two are compared.

## What should not become a skill

- The `edit` retry with a wider anchor (flat:119-123). It is how one text tool
  failed on one wrapped line, and the lesson does not generalize beyond "read
  the file before editing it".
- The three heading rewrites (flat:111-113). They implement a rule that
  `.kb/writing-style.md` §5 already states.
- The toolset count ("about 28") and the toolset names. They are values of one
  upstream version, and hermes updates against the tip of main.
- The docs URL list. Each URL belongs in the findings record's Sources section.
