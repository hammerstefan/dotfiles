# ses_e29c07bc8ffehleox1IKel7toN: Research ticket 49: ctlcmd channel

This session is a research subagent spawned by ses_e2a211dc0ffenjeQD6D6v7DvqQ to resolve wayfinder ticket #49. It has one user message, and that message is the parent session's brief, not the person's own words. The session ran in `/home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/spike-development-workshop` on 13 November 2026.

## What the person asked for

The person did not speak in this session. The brief that stands in for their ask, quoted:

- "Resolve wayfinder ticket #49 in hammerstefan/monitor-agent: \"Can a workshopctl subcommand carry the control requests?\""
- "Decide what such a subcommand needs: the command registration, the daemon handler, the identity check, and the release path. Read the upstream `canonical/workshop` code and its contribution guidance. Record whether upstream is likely to accept the command, and what this repository would carry if it does not."
- Constraints: "This is a read-only investigation. Do not modify the host, the daemon, or the repository." "Do not create, switch, or commit on any git branch. Write the findings markdown to `/tmp/opencode/chart/research-ctlcmd.md`."

## What was produced, and whether it worked

- `/tmp/opencode/chart/research-ctlcmd.md`. The parent copied it to `research/development-workshop-ctlcmd.md` on branch `research/development-workshop-ctlcmd`, which merged to `main` through pull request #58.
- The record holds the verdict "No", four groups of findings (command registration, daemon handler, identity check, release path), the live state of this host, the upstream acceptance argument with the maintainer's words, three candidate shapes in a table, a list of what was and was not verified, and a table of every upstream file read.
- **Verified by reading source and the host:** the command interface and its two model commands, the route table and the single `UntrustedOK` command, the instance-identifier chain from `/etc/machine-id` to `ResolveWorkshopInstanceID`, the daemon running as root with no `user:` in `snap/snapcraft.yaml`, and the host's workshop 0.9.9 with `/var/lib/workshop/bin` holding only `workshopctl`.
- **Verified by reading upstream issues:** the maintainer's policy in #761, and #927, #971, #1019 and #1139 as agreeing signals. The record quotes #761: "By design, workshop does not trust anything coming from the definition or an SDK, therefore, one cannot ship something that would be executed on the host."
- **Not verified, stated in the record:** whether a maintainer would accept a lifecycle verb on the caller's own workshop. Whether the instance-ID path resolves from a live workshop, because no call was made. Whether a development workshop can learn the agent workshop's UUID. The upstream commit, because `/tmp/opencode/ws-src` holds no Git metadata.
- The repository worktree was left clean and no branch was created.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

- The brief's own guard: "a call can start the socket-activated daemon". The record keeps it in its not-verified list, and no other file states it.
- "The client sends the `workshop-instance-id` header from `/etc/machine-id`." The record states the same, and adds that the value equals the LXD instance UUID without dashes.

## Failures, their cause, and the fix

- `!! FAILED edit` with `No changes to apply: oldString and newString are identical.` The agent had already added a bullet in one edit, then tried to correct a typo in the same bullet with a second edit whose matched text did not include the typo. Fix: it read the file, then re-issued the edit with the whole bullet as the old text. Nothing else failed.
- **A wrong attribution, corrected before the file left the session.** A draft sentence said the maintainers "state the opposite of what a fence verb needs". It was replaced with "The maintainers also refuse the host execution that a fence verb would need", after the issue threads were read. The first sentence attributed a policy no maintainer had stated.

## Candidate lessons

- ALREADY WRITTEN. The verdict, that no subcommand would serve as the control channel, and that the instance identity authorizes acting as one workshop and not on another. `research/development-workshop-ctlcmd.md` and `workshop-host-authority`, under "What a definition and an SDK cannot do".
- ALREADY WRITTEN. That a verb reaches the host only through a `canonical/workshop` release, with no plugin path and no second untrusted endpoint. `research/development-workshop-ctlcmd.md`, under "The release path".
- ALREADY WRITTEN. That the identifier is a bearer credential, that `/etc/machine-id` is writable by root in the workshop, and that the user filter limits a forged identifier to the same user's workshops. `research/development-workshop-ctlcmd.md`, under "The identity check".
- ALREADY WRITTEN. The four error responses, the header name, and the identity chain with its file and line references. `research/development-workshop-ctlcmd.md`.
- ALREADY WRITTEN. That a call to the endpoint can start the socket-activated daemon, which is why the check was not made end to end. `research/development-workshop-ctlcmd.md`, under "Not verified".
- ALREADY WRITTEN. Quote a maintainer before stating their policy. The `research` skill says to follow every claim back to the source that owns it, and the record's own "Upstream acceptance" section does this.
- NEW. A read through `lxc exec` into a product instance is still a touch, and a spawning brief should say whether it is allowed. The daemon-channel brief said "Do not touch the running `agent-4863fffc` or `plane-2a96f0cb` instances", while this brief said only "Do not modify the host, the daemon, or the repository", and the agent then ran `lxc exec --project "workshop.1077165261" agent-007bc764 -- cat /etc/machine-id` (tool log). Both readings are defensible, so the brief has to settle it.

## What should not become a skill

- The `!! FAILED edit` and its message. It is a tool behaviour, not a project rule. The general habit, read the file before a second edit at the same place, is already what the write and edit tools ask for.
- The list of upstream file paths and line numbers. They belong to the record that cites them, and a skill that repeated them would go stale with the next release.
- The three candidate shapes in the record's table. They exist to show why each is refused, and the refusal is what a skill should state.
