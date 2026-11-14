# ses_e28c08c21ffeTHqESwIB2yYvXl: Wayfinder map issue #44 direction (fork #1)

## What the person asked for

- USER 1 (line 2): "review and summarize the decisions/research/direction of wayfinder map issue #44. I want to review the current direction of that effort. Suggest some diagrams to help me understand"
- USER 2 (line 105): "use @diagram to create those diagrams"
- USER 3 (line 151): "can the html pages provide mermaid view options? zoom and scrcoll?"
- USER 4 (line 290): "only kb entry for topology, not the others. if the skill has been updated you are done"

The person answered the zoom-and-scroll scope question with "Both". This answer is the question-tool answer in the raw export. The flattened file omits it, so it has no flattened line anchor.

## What was produced, and whether it worked

- A review summary of issue #44, written in the reply, not a file. It names the phases, the tickets, and the three diagram suggestions.
- Three diagrams, each with an SVG, an HTML page, and a Mermaid source. The three are the authority topology, the phase roadmap, and the phase 3 bound options. The first render wrote them into a new `diagrams/` directory.
- The shared `diagram` skill gained a zoom-and-pan toolbar and two bug fixes. The skill is at `~/.config/opencode/skill/diagram/scripts/diagram.py`, a symlink into the dotfiles repository.
- The authority diagram became the committed topology `.kb/topologies/development-workshop-authority/`. Another conversation placed it there and wrote `.kb/topologies.md` and `.kb/development-workshop-authority.md`. This session found those changes mid-way (line 241).

Verified:

- The skill's test suite passes after the changes.
- A headless Chrome run loaded the authority page with no console errors, opened it fitted at 45 percent, zoomed to 54 percent, returned to 45 percent on Fit, and panned.

Not verified:

- The phase roadmap and the bound options were deleted at the person's direction. Nothing remains to check.
- The authority page loads Mermaid from a CDN address, so it needs network access to render. The reply states this at line 336.

## Corrections the person made

The agent had placed the phase roadmap and the bound options into `.kb/topologies/` and was about to write their knowledge-base entries. The agent's sentence before the correction (line 289): "Now let me write the knowledge-base entries for the two new topologies, following the pattern of the existing one."

- USER 4 (line 290): "only kb entry for topology, not the others. if the skill has been updated you are done"

The agent then removed the two extra topologies, their knowledge-base entries, and the `diagrams/` directory.

## Conventions, commands and values stated and written down nowhere

- One knowledge-base entry exists for a topology, not one per diagram. A review-artifact diagram gets no entry. USER 4 (line 290): "only kb entry for topology, not the others."
- The work ends once the skill holds the change. USER 4 (line 290): "if the skill has been updated you are done."

## Failures, their cause, and the fix

1. The `edit` calls to add the `:::leaf` role failed. The error was `File not found: .../diagrams/development-workshop-authority.mmd` (lines 386-387). The cause: the diagram script deletes its input source when a render fails, so the file the agent was editing no longer existed. The fix: recreate the three sources with `write`, with the leaf roles already in the source.
2. The generated HTML page could not load the Mermaid script. The browser reported the script failed to load. The cause: `SKILL_ROOT` used `Path(__file__).resolve()`, which followed the symlink into the dotfiles repository. The relative path then climbed past the filesystem root. The fix: keep the path as the caller reached it, and fall back to a `file://` URI when the relative path escapes.
3. The page opened at 427 percent or 460 percent instead of fitted. The cause: the fit function ran before Mermaid set the SVG viewBox, so it measured a placeholder size. The fix: wait until the SVG viewBox agrees with its width and height attributes.
4. The script prepended a second frontmatter. The cause: the input `.mmd` was the branded output from an earlier render, which already held the frontmatter. The fix: keep clean input sources in a separate `diagrams/src/` directory.
5. One render failed with a transient browser error. The agent attributed it to three concurrent browser renders and re-ran sequentially (line 184).

## Candidate lessons

- NEW — Keep clean diagram input sources separate from the branded output, because the diagram script deletes its input on a failed render. Assistant (line 214): "keep clean input sources in a separate directory so the branded output never overwrites the input. This is a better workflow anyway."
- ALREADY WRITTEN — A topology lives in `.kb/topologies/<name>/`, not a top-level `diagrams/` directory. `.kb/topologies.md` §1 states it. Assistant (line 243): "they live in `.kb/topologies/<name>/`, not in a top-level `diagrams/` directory."
- ALREADY WRITTEN — The HTML page loads Mermaid from a CDN address, not from the skill directory. `.kb/topologies.md` §4 states it. Assistant (line 336): "that page loads Mermaid from `https://cdn.jsdelivr.net/npm/mermaid@12.3.0/dist/mermaid.min.js`."
- NEW — A review-artifact diagram is not a topology and gets no knowledge-base entry. Stop when the person says the skill holds the change. USER 4 (line 290): "only kb entry for topology, not the others. if the skill has been updated you are done."

## What should not become a skill

- The zoom-and-pan toolbar and the two bug fixes (the script path and the fit timing) are changes to the shared `diagram` skill in the dotfiles repository. They belong in that skill's own tests and documentation, not in a monitor-agent skill.
- The review of issue #44 is a one-off report for the person. The decisions and research it summarizes already live in the tickets and in ADR 0010.
- The transient browser render failure is a flake, not a reusable procedure.
