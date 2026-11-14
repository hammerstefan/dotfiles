# ses_e28a460d4ffeV8uZgr8yHYjesF: Digest nested-LXD research trace

## What the person asked for

The person was the session that spawned this digester. It sent one brief and never wrote again.

USER 1 (line 3): "You are a subagent spawned by another session."

USER 1 (line 4): "You are writing one evidence digest from a recorded agent session trace. Work read-only; do not modify any repository."

USER 1 (line 6): "Input (the only one): /tmp/opencode/hwt-wrapup-docs-development-workshop-nested-lxd/trace.json"

USER 1 (line 9): "Output: write exactly one markdown file to /tmp/opencode/hwt-wrapup-docs-development-workshop-nested-lxd/digests/trace.md"

USER 1 (line 12): "Use this shape, with quotes (verbatim, message index cited):"

USER 1 (line 22): "Context you need: the repository is monitor-agent (github hammerstefan/monitor-agent)."

USER 1 (line 24): "Be exhaustive about exact host facts the person or the agent measured and later relied on: LXD version, workshop snap version, `lxc`/`workshop` subcommand flags and which were refused, kernel/module behaviour, AppArmor, network setup, timings, and any claim the person corrected."

USER 1 (line 26): "Reply with a short summary (10 lines max) of the digest's candidate lessons, so I can plan without reading the file."

## What was produced, and whether it worked

The digester wrote one file with the `write` tool (line 96): `/tmp/opencode/hwt-wrapup-docs-development-workshop-nested-lxd/digests/trace.md`.

The file exists and holds 28816 bytes. It opens with `# Trace digest: worktree `research-development-workshop-nested-lxd``.

The digester's own claim (line 32): "Digest written to `/tmp/opencode/hwt-wrapup-docs-development-workshop-nested-lxd/digests/trace.md` (all seven sections, quotes cited by message index, host facts table, 14 failures with verbatim error text)."

The digester then posted a summary of ten candidate lessons and one note (lines 34 to 47).

The digester read the 2.2 MB, 262-message trace in slices with `jq`, `grep`, and `sed` (lines 49 to 95). It never read the whole file at once, as the brief ordered.

The digester made no commits, branches, pull requests, or tickets. The work was read-only.

Verified: the digest file exists at its path and opens with the correct heading.

Not verified: each quote and message-index citation inside `trace.md` against the underlying `trace.json`. The file content is clipped in this transcript, so I read only its opening.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

The brief restates conventions that the repository already records. It states nothing new.

- monitor-agent is `hammerstefan/monitor-agent`. Written in `.kb/issue-tracker.md` §1 and `AGENTS.md`.
- The wayfinder skill is at `~/.agents/skills/wayfinder` and is not model-invoked. Written in `AGENTS.md` under Wayfinding.
- A ticket assigned to a session leaves the frontier. Written in `AGENTS.md`.
- A spike ticket keeps the branch `.kb/spikes.md` gives it. Written in `AGENTS.md`.
- Research findings are raised as a pull request to main. Written in `.kb/spikes.md` §7 and `.kb/issue-tracker.md`.
- Wayfinder tickets #44 and #48. Written in `research/development-workshop-nested-lxd.md`.

One value the brief states that the repository does not name is `PR #73 (merged)`. The research record names the branch but not the pull request number.

## Failures, their cause, and the fix

(none found)

## Candidate lessons

The summary (lines 34 to 45) lists ten candidate lessons. Each one is ALREADY WRITTEN. None is NEW.

- ALREADY WRITTEN in `AGENTS.md` and `.kb/spikes.md` §7. "A brief written by another agent is a draft — the person corrected two of its lines (msg 27 wrong about the wayfinder skill, msg 244 wrong about no PR)." (line 36)
- ALREADY WRITTEN in `.opencode/skills/run-a-workshop-in-a-vm/SKILL.md`. "An experimental root-only gate is a question for the person, not a reason to substitute a private build and declare done (msg 106 → 109)." (line 37)
- ALREADY WRITTEN in `AGENTS.md`. "Never raise a desktop `pkexec` prompt from an agent session (msg 38, "Request dismissed", exit 126)." (line 38)
- ALREADY WRITTEN in `AGENTS.md` and `.opencode/skills/run-a-workshop-in-a-vm/SKILL.md`. "`print()` inside a redirect corrupted the host's shared `user.workshop.projects` registry (msg 81 → 82); validate JSON, prefer `workshop remove`, verify by id." (line 39)
- ALREADY WRITTEN in `.opencode/skills/run-a-workshop-in-a-vm/SKILL.md`. "`lxc` verbs need help first: `config device show <inst>` (not `… root`), `device set` (not `override`), `delete <name> --project` (not `remote:name`)." (line 40)
- ALREADY WRITTEN in `.opencode/skills/run-a-workshop-in-a-vm/SKILL.md`. "A "warm" launch needs the artefact that made it warm; none could be found (msg 114) yet the record claimed warm (msg 129)." (line 41)
- ALREADY WRITTEN in `.opencode/skills/run-a-workshop-in-a-vm/SKILL.md`. "Only `lxc monitor --type=lifecycle` dates an image download; `journalctl` and syslog gave nothing (msg 143/150)." (line 42)
- ALREADY WRITTEN in `research/development-workshop-nested-lxd.md`. "A second `workshopd` needs an unprivileged vsock port (870 privileged and taken; 1870 is the development value)." (line 43)
- ALREADY WRITTEN in `.kb/writing-style.md` §6. "GiB/GB conversions are a defect surface — one slip self-corrected (msg 94/95), one survived into PR #73 (5.62 "GiB")." (line 44)
- ALREADY WRITTEN in `.kb/writing-style.md` §6. "The rule "never quote a test count" was broken in the committed record (msg 186/193), and a later run invalidated the map line written early (msg 222)." (line 45)

## What should not become a skill

The digester's own method stays out of this repository. Its `jq` flattening, its slice reading, and its message-index citation belong to the `learn-from-sessions` skill in the global config, not to monitor-agent.

The exact host figures (LXD 6.10.1, Workshop 0.9.9, the 870 and 1870 vsock ports, the 4 GiB memory limit, the 20 GiB disk) are PROJECT-SPECIFIC FACT. They belong in the research record, which holds them.

The digester's note (line 47) flags a conflict with the underlying digest's own "what should not become a skill" section: "a skill `run-a-workshop-in-a-vm` appeared just now, whose description lands squarely on the two things section 7 says should stay out of a skill (the exact memory/disk figures and the root-only opt-in recipe). Worth reading it against section 7 before it is kept." The repository kept the skill. `.opencode/skills/run-a-workshop-in-a-vm/SKILL.md` now holds both the figures and the root-only opt-in. This conflict was resolved in favor of the skill.
