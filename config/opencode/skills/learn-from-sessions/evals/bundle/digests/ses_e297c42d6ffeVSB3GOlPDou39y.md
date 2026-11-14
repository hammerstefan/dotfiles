# ses_e297c42d6ffeVSB3GOlPDou39y: Wayfinder ticket spawning with hwt

## What the person asked for

- USER 1 (line 3): run the `/wayfinder-hwt` command. It opens: "Load the `hwt` skill with the skill tool, id `hwt`, and apply it once per ticket." The agent reports the argument was `frontier` (line 219), which the command defines as: "query the map for the tickets the person can pick up now, and confirm the list before spawning (step 3)." (line 12)
- USER 2 (line 281): "what? wayfinder is installed"
- USER 3 (line 324): "you do the correction"
- USER 4 (line 340): "update the hwt-wayfinder with instruction on loading/finding wayfinder skill"
- USER 5 (line 369): "commit the command change"

## What was produced, and whether it worked

Three hwt sessions were spawned from map #44's frontier (lines 245-249):

- #45 Grill the trust model of the development workshop control service, branch `wayfinder/control-service-trust-model`.
- #48 Can a Workshop VM run a nested LXD and a nested Workshop?, branch `research/development-workshop-nested-lxd`.
- #50 The development workshop runs the test suite, branch `wayfinder/development-workshop-test-suite`.

Each used model `openrouter/deepseek/deepseek-v4.1-flash-1017#high` and base `f587700`, the `HEAD` of `main` (line 272). Six tickets were skipped as blocked (lines 253-258).

Three briefs were corrected to load the wayfinder skill (lines 299-303). A correction was sent into the three live sessions with `opencode run --session <id>` (lines 475-477), and its delivery was confirmed (lines 359-365). The `wayfinder-hwt.md` command in dotfiles gained a "The wayfinder skill" section (lines 344-357). Commit `15ff66a` landed in dotfiles (lines 371-381).

Verified: the dry runs, the three spawns, the delivery of the correction, and the commit. Not verified: the three sessions' own ticket outcomes, which were still running at the end (lines 305-315).

## Corrections the person made

1. The agent reported (line 276): "No `wayfinder` skill is installed on this host or in this repository, only the `/wayfinder-hwt` command." Person (USER 2, line 281): "what? wayfinder is installed".
2. The agent offered to let the person paste the correction and said (line 320): "You paste that yourself in each tab, which keeps your voice in those sessions." Person (USER 3, line 324): "you do the correction".
3. Person (USER 4, line 340): "update the hwt-wayfinder with instruction on loading/finding wayfinder skill".
4. Person (USER 5, line 369): "commit the command change".

## Conventions, commands and values stated and written down nowhere

- The person stated (USER 2, line 281): "what? wayfinder is installed". The `wayfinder` skill is at `~/.agents/skills/wayfinder`. This fact now sits in `AGENTS.md` under "Wayfinding", so it is no longer unwritten.
- The rule that a spawning brief must never write that the skill is absent, and the disk check `sed -n '1,5p' ~/.agents/skills/wayfinder/SKILL.md` that settles it, came from the person's directive (USER 4, line 340). They now sit in the dotfiles `wayfinder-hwt.md` command, not in this repository.

## Failures, their cause, and the fix

The agent reported the `wayfinder` skill absent (line 276). The skill frontmatter sets `disable-model-invocation: true`, which keeps it out of `<available_skills>`. The agent searched the catalog, `~/.config/opencode/skills`, `~/.config/opencode/skill`, the command directories, dotfiles, and `node_modules`, and never looked in `~/.agents/skills` (lines 293, 349). A prior brief already named the path and the flag, and the agent did not read it (line 293). The person's correction ended it (line 281). The agent found the skill, corrected the three briefs (lines 287, 459-464), and changed the command so it never again reports the skill absent.

The transcript records no `!! FAILED` tool lines.

## Candidate lessons

1. The `wayfinder` skill is at `~/.agents/skills/wayfinder` with `disable-model-invocation: true`, so the skill catalog omits it but the `skill` tool loads it by id. From "It is installed, at `~/.agents/skills/wayfinder`. Its frontmatter sets `disable-model-invocation: true`" (assistant, line 287). ALREADY WRITTEN in `AGENTS.md`, "Wayfinding" section.
2. Never conclude a skill is absent from the model's catalog or the usual skill directories. The disk read `sed -n '1,5p' ~/.agents/skills/wayfinder/SKILL.md` settles it. From the dotfiles command edit: "never conclude that from the catalog, `~/.config/opencode/skills`, `~/.config/opencode/skill`, or the command directories" and "the disk check that settles it: `sed -n '1,5p' ~/.agents/skills/wayfinder/SKILL.md`" (assistant, lines 349-350). NEW.
3. A spawned session told a wrong fact in its brief can be corrected with `opencode run --session <id> "<correction>"`, capped by `timeout 120`, and the delivery confirmed with `opencode session export <id>`. From "I send one line into each with `opencode run --session <id> ...`" (assistant, line 319), "Each call is capped at 120 seconds" (assistant, line 338), and the delivery check (assistant, lines 484-485). NEW.
4. A `wayfinder:research` ticket uses the branch its body names, over a title slug. From "#48's brief uses `research/development-workshop-nested-lxd`, the branch the ticket body names" (assistant, line 277). PROJECT-SPECIFIC FACT.

## What should not become a skill

- The frontier-query-then-spawn sequence, the brief skeleton, and the goal file. The `/wayfinder-hwt` command already defines them, and the mechanics belong there. From USER 1 (lines 2-215).
- The model extraction `opencode session export "$OPENCODE_SESSION_ID" | jq ...`. The command already defines it (lines 102-105). Rejected as a skill: command content, not a lesson.
