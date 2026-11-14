# ses_e2f04cf0fffeipDNiO5o7dBdsX: Plane workshop iron-proxy build #23

## What the person asked for

- "`/wayfinder #1 #23`" (USER 1794507510030, flat line 12). The ask states the
  boundary and the rules: "Build the plane workshop per ADR 0006" and "Ask
  before removing an existing workshop container, touching a host network
  bridge, or running anything that prints the management token."
- "pause" (USER 1794507849571, flat line 159).
- "continue" (USER 1794508106964, flat line 172).
- "any remaining work?" (USER 1794514873361, flat line 222).
- "open pr" (USER 1794536726126, flat line 236).
- "the review found some things. commit, push, and then merge the pr"
  (USER 1794537685179, flat line 312).
- "just commit the diff" (USER 1794537983926, flat line 314).
- Answered three questions: "Apply the network manually (Recommended)"
  (msg 125), "Apply the network by hand (Recommended)" (msg 138), and
  "Temporary deny probe (Recommended)" (msg 194).

## What was produced, and whether it worked

- One branch, `wayfinder/plane-workshop`, with two commits:
  `973f8c7 build: build the plane workshop` (msg 213) and
  `fc43fc3 fix: guard the pin and create the token file 0600` (msg 262).
- Pull request #37 created (msg 234), then merged with `gh pr merge 37 --merge`
  (msg 263). The agent's final message reports the merge commit as `7451cc7` on
  `main`. The transcript does not confirm the merge after msg 263.
- The plane workshop launched after one failed attempt and reported `Ready`
  (msg 98). Verified inside the container on that run: `/usr/local/bin/iron-proxy`
  reports `0.56.0`, the binary is present and executable, the unit is `enabled`,
  the policy is readable, and `/etc/iron-proxy/management.env` is `600 root:root`
  (msg 98).
- Before the fence, `systemctl is-active iron-proxy` answered `inactive` and the
  container listened on 22 and 53 only (msg 107). After the manual bridge
  placement and a restart it answered `active` and listened on
  `10.255.0.10:1080`, `127.0.0.1:80`, `127.0.0.1:443`, `127.0.0.1:9090`, and
  `127.0.0.1:9092` (msg 177).
- Measured from the agent workshop: the proxy port accepts a TCP connection
  (`CONNECTED`, msg 178), `example.com` through the proxy answers `HTTP 200`
  (msg 191), a direct connection to `1.1.1.1:443` and to `example.com:80` times
  out with `exit=124` (msg 192), and with `warn` removed the unlisted hosts
  answer `HTTP 403` (msg 199).
- The committed policy was restored byte for byte after the deny probe. The
  sha256 of `plane/proxy-policy.yaml` on the host and of `/project/proxy-policy.yaml`
  in the container agree (msg 193, msg 201).
- Not verified, by the agent's own statement: every check that needs the fence
  wrapper from #20, which was unmerged. Ticket #23 was closed with a resolution
  comment (msg 204).
- The transcript shows a fault in the agent's last reply to the ticket turn: the
  same three sentences repeat ("The map's "Done when" is the map's Decisions
  section", flat lines 214 to 220). The person then asked "any remaining work?".

## Corrections the person made

- The agent wrote "Let me check that rig's state and whether the fence session
  is still active." (flat line 157). The person answered "pause" (flat line
  159), and the agent's next reply opens "Paused. Nothing has been written or
  changed yet". The transcript does not state the reason.
- The person first asked for the full sequence: "the review found some things.
  commit, push, and then merge the pr". The next message narrowed it: "just
  commit the diff" (flat line 314). The agent answered "The diff is already
  committed and merged — nothing left to commit." Both person messages precede
  that reply, so the narrowing arrived after the merge had happened.

## Conventions, commands and values stated and written down nowhere

- The ask's rule about the token, verbatim: "No token value, no digest of it,
  and no secret material enters the tree or a command's printed output." It is
  the rule that the launch log broke (see lesson 3).
- The ask's rule on host state: "Ask before removing an existing workshop
  container, touching a host network bridge, or running anything that prints
  the management token."
- The person's choice of the temporary deny probe fixes a habit: a ticket that
  asks for two incompatible facts is answered with a measurement of the running
  process and no committed change (msg 194).
- The manual fence the person approved, in the agent's commands (msg 171 to
  msg 174): `lxc network create mon-plane-br ipv4.address=10.255.0.1/24
  ipv4.nat=true ipv6.address=none dns.mode=managed dns.domain=wp-plane`,
  `lxc network create mon-agent-br ipv4.address=10.254.0.1/24 ...`,
  `lxc network acl create`, `lxc network acl rule add mon-agent-br-acl egress
  action=allow protocol=tcp destination=10.255.0.10 destination_port=1080`,
  `lxc network set mon-agent-br security.acls=mon-agent-br-acl
  security.acls.default.egress.action=drop`, and
  `lxc --project workshop.1077165261 config device set plane-2a96f0cb
  workshop.network network=mon-plane-br ipv4.address=10.255.0.10` followed by
  `lxc --project workshop.1077165261 restart plane-2a96f0cb`.
- The agent bridge allow rule for the LLM endpoint names one address,
  `destination=140.82.113.21`, not a host name (msg 172). The measured ACL is
  in msg 191.

## Failures, their cause, and the fix

1. The first `workshop -p plane launch --verbose` aborted. The hook log ended
   with
   `/var/lib/workshop/sdk/iron-proxy/sdk/hooks/setup-base: line 1: work: unbound variable`
   then `error: cannot perform the following tasks:` and
   `- Run hook "setup-base" for "iron-proxy" SDK (command exit code 1)` and
   `"plane" launch aborted` (msg 91). Cause: the hook set
   `trap 'rm -rf "${work}"' EXIT` inside a function that declared `work` as
   `local`, so the trap ran after `work` had left scope and `set -u` read an
   unset name. Fix, in msg 93: declare `work=` and set the trap at the top level
   of the script, and drop `work` from the `local` list. `bash -n` passed before
   and after, so a syntax check does not catch this (msg 86, msg 94). The second
   launch succeeded (msg 95).
2. `workshop run -p plane reload` failed with `error: unclear if "reload" names
   a workshop or action: try "workshop run -- reload"` (msg 197). The fix is
   `workshop run -p plane -- reload`, which printed `200` and recorded
   `pipeline reloaded via management API` in the journal (msg 198).
3. The launch log held the generated management token. Under
   `workshop -p plane launch --verbose`, the log carried a bash trace, and the
   trace printed the token value in the `printf` line that writes
   `IRON_MANAGEMENT_API_KEY` (msg 91). The token was therefore in the launch
   output, against the ticket's rule. The transcript does not establish what
   turned the trace on. No later run removed the trace.
4. `workshop info` with no workshop name, in the fence session's rig, failed
   with `error: cannot infer workshop name: multiple workshops found: "agent",
   "plane"` (msg 49). `workshop info` also failed with `error: workshop not
   launched` in the worktree's own `plane` project after the aborted launch
   (msg 94).
5. `workshop fence status` failed with `error: unknown command "fence"`
   (msg 46). The fence is its own command, `monitor-agent-fence`, on an
   unmerged branch. `.kb/fence.md` already names the command, so this failure
   only repeats what the repository says.
6. The plane reported `Ready` while the proxy service was `inactive` and the
   container had no fixed address, so a client could reach nothing (msg 107).
   The service bound no proxy port. ADR 0006 already states this.
7. The host held two agent workshops at once. `agent-a21f5c6d` (the workshop
   from #24) and `agent-c72ff403` (this session's launch) both reported `READY`,
   the first on the shared bridge at `10.229.46.228` and the second at
   `10.229.46.9` before the placement (msg 107). After the placement the first
   stayed on the shared bridge while the second took `10.254.0.20` (msg 191).
   The fixed address `10.255.0.10` was already held by the fence session's rig
   in `/tmp/opencode/fence-verify` when this session started (msg 23 to msg 25).
8. Two `webfetch` calls returned 404 for `docs/reference/workshopctl-cli.rst` and
   `docs/reference/sdk-hooks.rst` (msg 77). The pages live under
   `docs/reference/cli/workshopctl.rst` and
   `docs/reference/definition-files/sdk-definition.rst`, which is what the agent
   fetched next (msg 80, msg 81).
9. `workshop -p agent start` failed with `error: cannot start "agent": workshop
   not launched`, while `workshop -p agent list` showed `agent  Off`. A workshop
   that was never launched cannot be started (msg 103).

## Candidate lessons

1. NEW. A hook that sets an EXIT trap for a temporary directory declared
   `local` fails the whole launch with `<path>: line 1: work: unbound variable`
   and `"plane" launch aborted`. The trap must read a variable declared at the
   top level of the script, and `bash -n` will not find the fault. Quote:
   `line 1: work: unbound variable` (msg 91) and the fix (msg 93).
2. NEW. The container path of a project SDK hook is
   `/var/lib/workshop/sdk/<sdk-name>/sdk/hooks/<hook>`, so a hook failure names
   the staged copy and not the file in the tree. Quote:
   `/var/lib/workshop/sdk/iron-proxy/sdk/hooks/setup-base` (msg 91). The same
   staging shows on the files side as `/var/lib/workshop/sdk/hermes/files/...`.
3. NEW. `workshop launch --verbose` prints a bash trace of the hook, and a hook
   that creates a credential writes it into the launch output. A hook that
   handles a secret must not run under a trace, and the operator must read the
   launch log as a place where a secret can appear. Quote: the trace line
   `+ printf 'IRON_MANAGEMENT_API_KEY=%s\n' <the token>` (msg 91).
4. NEW. `workshop run` cannot tell a workshop name from an action name, and the
   answer is `error: unclear if "reload" names a workshop or action: try
   "workshop run -- reload"`. The `--` form prints the action's own output
   (`200` from the reload). Quote: msg 197 and msg 198.
5. NEW. `workshop info` with no name fails in a project that holds more than one
   workshop: `error: cannot infer workshop name: multiple workshops found:
   "agent", "plane"`. Quote: msg 49.
6. NEW. Every session on this host shares the operator's Workshop project and
   its LXD project `workshop.1077165261`, so workshop names, container names,
   and fixed addresses are host-wide. Two sessions that build the same
   definition produce two containers, and a session sees only the workshops of
   its own project directory through `workshop list` (msg 17), while `lxc
   --project workshop.1077165261 list` shows every instance. Quote:
   `agent-a21f5c6d` and `agent-c72ff403` both `READY` (msg 107), and the fence rig
   already holding `10.255.0.10` (msg 24).
7. NEW. `workshopctl` is not installed on the host PATH. `workshopctl set-health
   --help` answered `/usr/bin/bash: line 1: workshopctl: command not found`
   (msg 76), and `which workshop workshopctl ...` returned exit 1 (msg 14).
   `workshopctl` exists inside a workshop.
8. ALREADY WRITTEN. The root `.gitignore` ignores `.workshop.lock`, with the
   comment "The lock a workshop definition application writes". `git status
   --ignored` reported `!! plane/.workshop.lock` (msg 91).
9. NEW. Closing the ticket before the files are committed makes the map bullet
   false. The agent updated the map and closed the ticket while the plane files
   were still staged, then noticed: "the bullet's claim ... is not true yet: the
   plane files are staged in the index, not committed". Quote: the agent's
   sentence at flat line 210, and the commit that followed (msg 213). The resolve
   order is already in `.kb/issue-tracker.md`.
10. ALREADY WRITTEN. `warn: true` forwards an unlisted host and records it, and
    the 403 needs the line removed. See `research/iron-proxy-plane.md`.
11. ALREADY WRITTEN. A plane workshop without the fixed address cannot bind, so
    it serves nothing after a launch. See `adr/0006`.
12. ALREADY WRITTEN. A fixed address takes effect at the next boot of the
    container. See `adr/0006`.
13. ALREADY WRITTEN. A bridge and its ACLs are created in LXD's default project,
    because a network cannot exist in another project on LXD 6.10.1. See
    `research/development-workshop-lxd-scope.md`.
14. ALREADY WRITTEN. The operator's LXD project is `workshop.1077165261`. See
    `research/development-workshop-channel.md`.
15. ALREADY WRITTEN. The fence verbs, the probe results, the exit codes, and the
    placement release are in `.kb/fence.md`.
16. ALREADY WRITTEN. The proxy variables reach hermes through `~/.hermes/.env`,
    and `workshop exec` shows them empty. See `adr/0005`. The measurement is
    msg 187: `HTTP_PROXY=`, `HTTPS_PROXY=`, `NO_PROXY=`.
17. PROJECT-SPECIFIC FACT. The manual fence commands and the single allowed
    address `140.82.113.21` belong in the fence definition and the records. The
    fence command owns that state now.

## What should not become a skill

- The manual `lxc network create` sequence. `.kb/fence.md` gives the fence
  command that owns this state, and copies of the commands drift from it.
- The warn-mode behavior and the pre-fence "Ready" state are already decided.
  Repeating them teaches nothing new.
- "Read the ticket boundary before asking" is too general to be a skill. The
  useful content is lesson 6, which names the shared project and how to see the
  other instances.
- The two 404 doc URLs are a guess about an upstream path, not a rule.
- The repeated sentences in the agent's reply are a model failure to report, not
  a lesson for the repository.
