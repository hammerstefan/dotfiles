# ses_e27c8380affehSoW92XccRaJr4: just dev up reports the workshop Ready with monitor-agent

## What the person asked for

The first turn is the handoff brief, not the person's words. Its Ask is
`/wayfinder #44 #52` (line 12). The person then typed seven messages.

- USER 2 (line 145): "why should a human run the todos rather than you?"
- USER 3 (line 196): "I don't like that the daemon.service is on a global location. is it possible to have the service file live with the project? don't change, just discus"
- USER 4 (line 227): "I like A, but is .control the right place?"
- USER 5 (line 254): ".control makes sense, apply the fixes"
- USER 6 (line 306): "run dev down, I'm done"
- USER 7 (line 328): "open pr"
- USER 8 (line 345): "rebase against origin/main and then consider if the README needs updating base on instructions"

## What was produced, and whether it worked

The branch `wayfinder/fence-from-development-workshop` delivered the control
service that ADR 0010 decides. The package is `monitor_agent/control/`. The
entry point is `monitor-agent-verb-daemon`. The recipes `just dev up`,
`just dev down`, and `just dev apply` run the repository entry point.

Commits moved with rebases. The first commit was `84b757b` (line 80). The
unit file move was `d0db51e` (line 266). The push rebased them to `9529254`
and `89d6d73` (line 338). A second rebase ended at six commits, head
`3e6818f` (line 353).

The pull request is #88. The ticket #52 is closed. The map #44 records the
decision in one line (line 82).

Verified live on the host:

- `just dev up` prints the workshop Ready, the socket device, and the active
  unit (line 87).
- `just dev apply` inside the workshop prints both probe verdicts and exits 0
  (line 102).
- The unit restarts after a crash: `kill -9` changes the pid and sets
  `NRestarts=1` (line 116).
- The unit is not enabled: `is-enabled` prints `static` then `linked` after
  the move (line 100, line 281).
- `just dev down` stops the unit, removes the link and the device, and stops
  the workshop (line 290).
- `just test` passed. The count rose from 164 to 166 (line 124, line 266).

The launch branch and the rebuilt-instance device were not verified in the
first report (line 136). The agent ran both after the person allowed it
(line 160, line 172).

## Corrections the person made

- The agent's report said "The four remaining items are in the sidebar todo
  list: exercising the launch branch and a refresh, pushing the branch and
  opening a pull request, and optionally removing the unit file" (line 141).
  The person answered: "why should a human run the todos rather than you?"
  (line 145). Two of those four were the agent's checks. The agent's reply
  admits it moved its own work off its plate (line 147).

- The agent offered a todo that said: "Decide whether to remove
  `~/.config/systemd/user/monitor-agent-verb-daemon.service` after `just dev
  down`" (line 194). The person answered: "I don't like that the daemon.service
  is on a global location. is it possible to have the service file live with
  the project? don't change, just discus" (line 196).

- The agent's preference was "A with the flat file,
  `.control/monitor-agent-verb-daemon.service`, plus one sentence each in ADR
  0010 and `.kb/control-service.md`" (line 252). The person answered: "I like
  A, but is .control the right place?" (line 227). The agent then justified
  the placement rather than accepting its own first answer.

## Conventions, commands and values stated and written down nowhere

- The person requires the unit file to live with the project, not in
  `~/.config/systemd/user/`, which every worktree shares. Quote: "is it
  possible to have the service file live with the project?" (line 196).

- The person approved `.control/` as the unit file's home. Quote: ".control
  makes sense, apply the fixes" (line 254).

- The person approved option A, the link. Quote: "I like A" (line 227).

- The person's exact permission strings: "open pr" (line 328) and "run dev
  down, I'm done" (line 306).

## Failures, their cause, and the fix

Two edit calls failed during the unit file refactor. Both failed with
"Could not find oldString ... It must match exactly, including whitespace and
indentation" (line 542, line 545).

- Line 541 retried an edit whose oldString had already been applied by the
  edit at line 535. The file already held the new constructor signature.

- Line 544 renamed a body line that still read `unit_path`, but the signature
  rename at line 543 had already replaced `unit_path` with `link_path`. The
  oldString named `_link_path_override` before the file held that name.

The fix was the same each time: read the file (line 546, line 548) and retry
the edit against the current content (line 547, line 549).

No test, recipe, or systemd command failed in the session.

## Candidate lessons

- NEW. Put only work the person can finish on the handoff todo list. A check
  the agent can run is the agent's, and it asks permission to run it instead
  of handing it over. Quote: "why should a human run the todos rather than
  you?" (USER 2, line 145).

- NEW. A systemd user unit that names one worktree's absolute path belongs in
  the project, linked with `systemctl --user link`, not written to
  `~/.config/systemd/user/` where it outlives the worktree. Quote: "is it
  possible to have the service file live with the project?" (USER 3, line
  196). The command exists in systemd 255, and `disable` undoes the link
  (line 207).

- PROJECT-SPECIFIC FACT. `workshop refresh dev` answers `no updates available
  for "dev"` and rebuilds nothing. `workshop restore dev` rebuilds the
  instance (line 160). Belongs in `.kb/development-workshop.md`.

- PROJECT-SPECIFIC FACT. The control socket device uses `bind=instance`,
  `listen=unix:/run/user/1000/…`, `connect=unix:<host socket>`, `mode=0600`,
  and the operator uid and gid in `security.uid` and `security.gid`. The
  service reads the operator uid from the connection (line 129). Belongs in
  `.kb/control-service.md`.

- PROJECT-SPECIFIC FACT. The recipe inside the workshop runs `python3 -m
  monitor_agent.control.cli`, not `uv run`, because the host `.venv` names
  interpreter paths that do not exist in the workshop (line 130). Belongs in
  the `just dev` recipe docs.

- ALREADY WRITTEN. A push that rebases onto `main` changes the hashes, and the
  posted comment is corrected in the same turn (line 341). Recorded in
  `AGENTS.md`.

- ALREADY WRITTEN. Every user-facing change updates the root `README.md` in
  the same commit (line 375). Recorded in `AGENTS.md` and `.kb/project.md` §3.

## What should not become a skill

- The `.control/` against `.workshop/` against `scripts/` placement debate
  (lines 229 to 252). It is a one-time design choice, now recorded in ADR
  0010 and `.kb/control-service.md`.

- "don't change, just discus" (line 196). A scoping instruction for one turn,
  not a repeatable workflow.

- The proxy device configuration values. They are facts about this control
  service, so they belong in a record, not a skill.
