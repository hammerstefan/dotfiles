# ses_e29c07bcaffeKVAYPXCzxM00zA: Research ticket 46: daemon channel

This session is a research subagent spawned by ses_e2a211dc0ffenjeQD6D6v7DvqQ to resolve wayfinder ticket #46. It has one user message, and that message is the parent session's brief, not the person's own words. The session ran in `/home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/spike-development-workshop` on 13 November 2026.

## What the person asked for

The person did not speak in this session. The brief that stands in for their ask, quoted:

- "Resolve wayfinder ticket #46 in hammerstefan/monitor-agent: \"Can a workshop process drive the host Workshop daemon?\""
- "The Workshop daemon source says a bind-mounted trusted socket fails, because `workshopd` looks up the peer uid with SO_PEERCRED and a container process has a host subuid with no account. A proxy device makes the peer root, and the daemon then resolves the caller to root and looks in the `workshop.root` LXD project instead of the operator's project." "Confirm both paths against this running system."
- Checks: "Bind-mount `/var/snap/workshop/common/workshop/workshop.socket` into a scratch workshop and run `workshop list` from inside it. Record the daemon response." "Add a proxy device for the same socket and repeat. Record the response and the LXD project the daemon resolves." "Record the uid the daemon sees for each path, and whether the user lookup succeeds."
- Constraints: "Use a scratch Workshop project under `/tmp/opencode/chart/r1`. Do not touch the running `agent-4863fffc` or `plane-2a96f0cb` instances, the `mon-*-br` bridges or ACLs, or the real fence." "Create and then remove every object you create, including the scratch project, instances, and devices." "Do not create, switch, or commit on any git branch in the repository. Write the findings markdown to `/tmp/opencode/chart/research-daemon.md`."

## What was produced, and whether it worked

- `/tmp/opencode/chart/research-daemon.md`. The parent copied it to `research/development-workshop-channel.md` on branch `research/development-workshop-channel`, which merged to `main` through pull request #58.
- The findings file on `main` is the same text. It holds the verdict, six findings, the mechanism with source line numbers, the commands with their output, the gotchas, the cleanup and the not-verified list.
- One scratch workshop `scratchd-a4740e59` was launched and removed. The LXD projects `workshop.root` and `workshop-snapshots.root` were created by the daemon as a side effect and deleted. The scratch project path was removed from `user.workshop.projects` on the operator's own project `workshop.1077165261`, and the subagent checked that the other 17 entries were unchanged.
- **Verified by measurement:** both paths, as root and as the workshop user, with the daemon journal lines for each, and an `exec` through the socket.
- **Not verified, stated in the record:** the raw peer uid, which the daemon does not log. A third `security.uid`. The VM runtime. A workshop whose idmap maps no container uid to a host account. The untrusted socket end to end.
- **Branch handling.** The subagent made no branch and no commit, as its brief required. It also left the repository worktree clean.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

The brief held two values that the record does not repeat:

- The instance names it was told not to touch: "Do not touch the running `agent-4863fffc` or `plane-2a96f0cb` instances". The record names `agent-007bc764` and `plane-4d1696e1` instead, because the workshops were recreated during the parent session. That is the only trace of the earlier names.
- The scratch location `/tmp/opencode/chart/r1` and the findings path. Both are the parent's choice, not a repository convention.

## Failures, their cause, and the fix

- No `!! FAILED` line appears in this session's tool log.
- The record states two wrong turns that cost time and that a reader would otherwise repeat. The first: `workshop -p /project list` from inside the workshop answers `cannot create or load project at "/project": lstat /project: no such file or directory`, because the daemon resolves the path on the host. The fix was to name the host path. The second: a bind device and a proxy device cannot both own `/var/lib/workshop/run/workshop.socket`, so the second check used `workshop.socket.bind`.

## Candidate lessons

- ALREADY WRITTEN. The whole verdict, that the uid the connection presents is the cause and the mount or the proxy is not. `research/development-workshop-channel.md`, and `workshop-host-authority` in its "traps that make a probe lie" section.
- ALREADY WRITTEN. `raw.idmap: uid 1077165261 1000` and the `unknown userid 1000000` answer. `research/development-workshop-channel.md` and `workshop-host-authority`.
- ALREADY WRITTEN. The `security.uid` rule and the empty `workshop.root` project. `research/development-workshop-channel.md` and `workshop-host-authority`.
- ALREADY WRITTEN. The host path rule for `workshop -p`. `workshop-host-authority`, probe order step 2.
- ALREADY WRITTEN. The journal lines to read, `POST /v1/projects 500` and `POST /v1/projects/<id>/workshops/<name>/exec 202`. `workshop-host-authority`, probe order step 3.
- ALREADY WRITTEN. That a launch registers the project path in `user.workshop.projects` on the operator's project, that `workshop remove` leaves the entry behind, and that cleanup therefore edits the operator's own project configuration. `research/development-workshop-channel.md`, under "Cleanup".
- ALREADY WRITTEN. That the untrusted socket admits one route, `/v1/workshopctl`. `research/development-workshop-channel.md` and `research/development-workshop-ctlcmd.md`.
- ALREADY WRITTEN. The method of pinning the running daemon to a tag with `go version -m /snap/workshop/current/bin/workshopd` before reading source. `research/development-workshop-channel.md`, under "Mechanism".

## What should not become a skill

- The scratch paths and instance names from the parent's brief. They were true for one afternoon and the instances had already been recreated by the end of the parent session.
- The power to write `user.workshop.projects` on the operator's project. A skill that teaches a probe to edit that key would teach a probe to write to the product's configuration. The record states the fact. A skill should say to ask before the cleanup, not how to do it.
