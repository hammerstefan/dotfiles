# ses_e28c8242dffeTG5Hp2vUQ5NBzU: Wayfinder map issue #44 direction

## What the person asked for

- USER 1 (line 3): "review and summarize the decisions/research/direction of wayfinder map issue #44. I want to review the current direction of that effort. Suggest some diagrams to help me understand"
- USER 2 (line 106): "use @diagram to create those diagrams"
- USER 3 (line 152): "keep the authority topology as persistent documentation for this project. the rest can be discarded"

The person answered three `question` prompts (diagram location, diagram timing, HTML library weight). The answer text is not in the transcript. The `question` tool state records `output: null` for each.

## What was produced, and whether it worked

Turn 1 produced a prose review of wayfinder map #44. It was a text reply with no files. It named the research findings, the three phases, and three challenges to sharpen.

Turn 2 produced three diagrams with the `diagram` skill. The files were `diagrams/development-workshop-authority.{mmd,svg,html}`, `diagrams/development-workshop-phases.{mmd,svg,html}`, and `diagrams/development-workshop-bound-options.{mmd,svg,html}`. The agent's claim: "All three rendered and passed the brand contract check." (line 112). The PNGs were rendered and read back for a visual check (lines 370 to 372).

Turn 3 made the authority topology persistent and discarded the other two. The output:

- Two `.kb` entries: `.kb/topologies.md` (the convention with four laws) and `.kb/development-workshop-authority.md` (the topology entry).
- The diagram assets at `.kb/topologies/development-workshop-authority/` with a `.mmd` source, an `.svg`, and an `.html` page.
- The `AGENTS.md` index updated with both entries.
- A commit on branch `wayfinder/control-service-trust-model`, pushed to pull request 72.
- The phase roadmap and bound-options diagrams removed.

Verified: the three diagrams rendered and passed the brand contract check (the agent's claim). The final authority diagram re-rendered at the new path and was read back (line 443). The CDN address `https://cdn.jsdelivr.net/npm/mermaid@12.3.0/dist/mermaid.min.js` returned HTTP 200 (line 423). The branch pushed, and the agent reported pull request 72 state open and mergeable (line 273).

Not verified: the commit hash `de6be9d` is the agent's prose claim (line 273). The tool log shows the commit command (line 455) but not its hash. The pull request description update has no visible REST call in the tool log.

## Corrections the person made

(none found)

The person gave three requests and answered three `question` prompts. The transcript holds no verbatim correction of the agent's behavior.

## Conventions, commands and values stated and written down nowhere

The person's directive became the topology convention. USER 3 (line 152): "keep the authority topology as persistent documentation for this project. the rest can be discarded". The convention is now written in `.kb/topologies.md`.

The person's three `question` answers are absent from the transcript. The outcomes show the choices. The topology landed in the knowledge base as two `.kb` entries. It landed on pull request 72. The HTML page loads Mermaid from a public CDN. These outcomes are recorded in the repository files.

## Failures, their cause, and the fix

1. The `edit` tool answered "File not found: .../diagrams/development-workshop-authority.mmd" (line 350) and the same for the phases and bound-options files (lines 356 to 363). Cause: the `diagram` skill script removed the `.mmd` source files after it rendered them. The agent's words: "The script removed the sources." (line 17). Fix: recreate the three source files with the leaf roles and render again (lines 365 to 367).

2. The `webfetch` of the CDN address answered "Response too large (exceeds 5242880 byte limit)" (lines 419 to 420). Cause: the Mermaid library is larger than 5 MB. Fix: verify the address with `curl -sS -I` instead, which returned 200, and pin the version to `12.3.0` (lines 421 to 423).

3. The `gh pr edit 72 --body-file -` left the pull request body unchanged. This is a silent failure with no `!! FAILED` entry. The agent's words: "The body did not update. The deprecation error aborted the edit." (line 262). The agent claims it fixed this with the REST API, but no REST call appears in the tool log.

## Candidate lessons

- NEW. The `diagram` skill script removes or consumes the `.mmd` source file after a render. Recreate the source before re-rendering. From "The script removed the sources." (line 17) and "The script consumed the source file on the previous failed run." (line 232). Message position: ASSISTANT turn 2 and turn 3.
- NEW. A `flowchart` render fails without at least one `:::leaf` role. From "The flowchart needs at least one `:::leaf` role." (line 13). Message position: ASSISTANT turn 2.
- NEW. `webfetch` refuses a response over 5 MB. Verify a large asset address with `curl -sS -I` instead. From "The fetch reached the file and rejected it only for size" (line 210) and the error at line 419. Message position: tool log.
- NEW. `gh pr edit --body-file` can leave the body unchanged, and a GraphQL Projects Classic deprecation warning can abort the edit. Verify with `gh pr view --json body`. From "The body did not update. The deprecation error aborted the edit." (line 262). Message position: ASSISTANT turn 3. The claim is the agent's and has no REST call in the tool log.
- ALREADY WRITTEN. The `diagram` skill points the HTML page at the machine-local Mermaid library and overwrites the page on every render, so the CDN address is re-applied after each render. Written in `.kb/topologies.md` §4 and "Making one". From "The script regenerates the HTML with the local library path, so I need to re-apply the CDN change." (line 234).
- ALREADY WRITTEN. A topology belongs to the `.kb` entry that explains it, never holds a decision, names its source, and keeps its editable source. Written in `.kb/topologies.md`. From the four-law summary in the agent's reply (lines 276 to 282).
- PROJECT-SPECIFIC FACT. The authority topology shows the decision in ADR 0010 and adds no decision of its own. Written in `.kb/development-workshop-authority.md`. From "The diagram therefore documents a decision that is not yet merged." (line 166).

## What should not become a skill

- The authority topology and its `.kb` entry are project documentation. They record one project's decision. They are not a reusable skill.
- The four topology laws in `.kb/topologies.md` are a repository convention. They are already a `.kb` entry, not a skill.
- The map #44 review is session analysis of the project state at that time. It is not reusable guidance.
- The three `diagram` skill gotchas (source deletion, the leaf role, the HTML library path) belong in the `diagram` skill itself in the global config. They do not belong in a repository skill.
