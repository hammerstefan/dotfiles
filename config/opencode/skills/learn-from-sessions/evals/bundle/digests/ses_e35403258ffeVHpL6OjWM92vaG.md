# ses_e35403258ffeVHpL6OjWM92vaG: Handoff monitor agent two spike

Positions are `flat L<line>` in
`/tmp/opencode/hwt-wrapup-monitor-agent/flat/ses_e35403258ffeVHpL6OjWM92vaG.txt`.
Thirteen USER turns, 463 messages, no compaction. Repository files were read
from `/home/stefan.hammer@canonical.com/git/monitor-agent` on 2026-11-13.

## What the person asked for

- `flat L3`: "@prototype /tmp/opencode/handoff-monitor-agent-two-workshop-spike.md . watch out for other spikes running in separate sessions (for port conflicts, etc)"
- `flat L325`: "continue but try to wrap up with a conclusion and next steps"
- `flat L384`: "@general create a mermaid diagram illustrating the concern "fence cannot hold against its own container's root". Render in HTML. open."
- `flat L411`: "put the files in ~/tmp"
- `flat L424`: "@explore why can we not apply the acl to be applied at the workshop NIC level?"
- `flat L502`: "@general @prototype spike "Put the instances on separate bridges — per-workshop bridges with one ACL each, giving per-workshop granularity without OVN""
- `flat L551`: "do 1, write a plan to prototype 2, describe the current options/state of 3"
- `flat L610`: "what is the risk of unblocked dns?"
- `flat L656`: "what is the value/tradoff of C"
- `flat L707`: "we should document "The value is smaller than it first appears, because of how the ADR works." and leave a record that we are following the "accept and document" with the future option to adding logging"
- `flat L747`: "clean it up"
- `flat L774` to `L780`: "Load the `hwt` skill with the skill tool, id `hwt`, and follow it." then "Ask:" then "spike  ~/tmp/plan-openshell-two-bridge-gateway.md"
- `flat L812`: "@handoff fix the hwt resolving to the wrong repo"

The person also ran `hwt --here feature/two` in their own pane (message 397,
exit 0), which created
`/home/stefan.hammer@canonical.com/.herdr/worktrees/herdr-plugins/feature-two`.

## What was produced, and whether it worked

- Branch `spike/two-workshop`, 9 tracked files, tip `f4b0f68`. Verified. The
  session claimed "9 tracked files, no credentials, all scripts parse, run
  cleans up after itself" (`flat L371`).
- `main`: `46404ec` "docs: record the two-workshop spike result and correct the
  fence record", then `0b591b0` and `ddeb6e3`, and `9c6f4c3` "docs: fence each
  workshop on its own bridge". Branch `spike/separate-bridges`, 7 tracked
  files, tip `a917a2c`. Verified.
- `main` `f9a6867` added `requirements/001-workshop-egress-fence/requirements.md`,
  75 lines, and `3d2be41` added ADR 0002, its index row, and the cross-link from
  requirement 001. Verified. `5c7528a` deleted requirement 001 later, when the
  proxy topology replaced the OpenShell topology.
- The primary checkout's `spike/acl-fence` was reset from `db175ca` to
  `832b307`. Verified, that is the branch tip now.
- `~/tmp/fence-root-diagram/` and `~/tmp/plan-openshell-two-bridge-gateway.md`.
  The plan exists. Neither file was opened here.
- A worktree and Herdr space through `hwt` (branch `spike/two-bridge-gateway`,
  base `main` at `3d2be41`, prompt file
  `/tmp/opencode/hwt-prompt-two-bridge-gateway.md`), and a handoff at
  `/tmp/opencode/handoff-hwt-wrong-repo.md`. The branch exists with later
  commits, the worktree is gone, and the handoff is outside the repository.
- The claim "No commit in any branch carries a key" (`flat L345`) rests on the
  agent's own `git log --all -- spike/two-workshop/.tls`. Not verifiable now.

Not verified, as the record states: the `lxd-vm` runtime, an OVN NIC ACL, a
fence without passwordless sudo, the audit-mode policy log, and what the LXD
`logged` action produces on a bridge.

### Where the records restate the session

- `research/two-workshop.md` restates every measurement: the remote gateway at
  `https://10.251.0.10:17670` with mutual TLS, the sandbox exec and download,
  the egress drop that times out, the two allowed paths, the refresh and
  remove+launch revert, the `CAP_NET_ADMIN` address claim, and the NXDOMAIN
  answer from the authority. The verdict "Partly" repeats `flat L355`.
- `research/separate-bridges.md` restates the second spike: source-less allow
  rules, the timed-out archive connection after the same claim, the plane
  ingress rule that held when the agent fence was gone, and `refused` against
  `timeout`.
- `research/acl-fence.md` is the concurrent session's record, from
  `spike/acl-fence` commit `c3b9919`. This session read its README (`flat L857`)
  and did not write the record.

### Where the session holds something the records do not

- The failure sequence and its causes, below, with "The "own source" label was
  inverted in my test" (`flat L311`) and the listener that settled it.
- The credential incident (`flat L343` to `L347`). The records keep the rule
  about the bundle copy and not the staging mistake that caused it.
- The practice for a checkout a second agent session owns.
- The gateway configuration facts in `flat L586`. Only the
  `OPENSHELL_LOCAL_TLS_DIR` fact is in `research/two-bridge-gateway.md:88`.

## Corrections the person made

- The agent wrote "**File:** `/tmp/opencode/fence-root-diagram/index.html`
  (with `mermaid.min.js` beside it, so it renders offline)" (`flat L390`), and
  offered to keep the diagram in the repository. The person: "put the files in
  ~/tmp" (`flat L411`).
- The agent wrote "Now let me run the complete spike one final time to validate
  the committed scripts end-to-end." (`flat L321`), after a long run of reruns.
  The person: "continue but try to wrap up with a conclusion and next steps"
  (`flat L325`).
- The agent wrote "Worth telling that session to drop it, or I can clean it up
  if you want me to touch their worktree." (`flat L745`). The person: "clean
  it up" (`flat L747`).
- The agent asked "Want me to run the item-2 spike next, or write the DNS
  requirement first?" (`flat L608`). The person replaced that order with "do 1,
  write a plan to prototype 2, describe the current options/state of 3"
  (`flat L551`).

## Conventions, commands and values stated and written down nowhere

- An ask opens with a mode tag: `@prototype` with a path (`flat L3`),
  `@general` (`flat L384`), `@explore` (`flat L424`), `@handoff` (`flat L812`),
  and `@general` with `@prototype` (`flat L502`).
- Another session's spike may hold the host: "watch out for other spikes
  running in separate sessions (for port conflicts, etc)" (`flat L3`). No law
  in `.kb/spikes.md` states this.
- An artifact outside the repository goes under `~/tmp` (`flat L411`). The
  agent's first choice was `/tmp/opencode` (`flat L390`, `L415`).
- The `hwt` ask names an action and a plan path: "spike
  ~/tmp/plan-openshell-two-bridge-gateway.md" (`flat L778`).
- The values of this run: `twbr0` at `10.251.0.1/24`, plane workshop
  `10.251.0.10`, agent workshop `10.251.0.20`, port `17670`, ACL `tw-fence`,
  stand-in ports `19801` and `19802`, escape listener `19803`. The second
  spike used `abr0`, `pbr0`, `10.252.0.1/24`, `10.253.0.10`. The plan reserved
  `gbagent`, `gbplane`, `gbr-*`, ports `19811` and `19812`, and it is the only
  place that reservation appears.
- The two scratch worktrees: `/tmp/opencode/ma-two-workshop` and
  `/tmp/opencode/ma-separate-bridges`.
- Agent-stated and not confirmed by the person: a dry run with `hwt -n`,
  `--repo` to name the repository, and `--base main` because the checkout stood
  on `spike/acl-fence` at `832b307` (`flat L783` to `L796`).

## Failures, their cause, and the fix

1. Three `webfetch` 404s (`flat L880`, `L883`, `L885`) for guessed upstream doc
   paths. The session read the local skill reference and the previous spike's
   scripts instead (`flat L888`, `L889`).
2. The plane came up at `.210` and not at `10.251.0.10` (`flat L101`, `L137`).
   Cause: a static address on a bridged NIC applies at the next boot. Fix: stop
   and restart after setting it.
3. `Failed to connect to bus` (`flat L117`). Cause: the user bus was not
   running. Fix: `loginctl enable-linger root` and a wait.
4. The service read `active` with no listener (`flat L119` to `L123`, `L141`).
   Cause: a readiness race. Fix: wait from the agent workshop.
5. No OpenShell download (`flat L127` to `L131`). Cause: the fence ran before
   the install. Fix: ordered phases, bridge, installs, ACL.
6. Docker's `172.17.0.1` chosen as the plane address (`flat L159`). Cause:
   `ip -o addr` returns it first once Docker is installed. Fix: name the
   interface.
7. The supervisor could not reach the gateway (`flat L153`). Cause: the driver
   endpoint defaults to loopback. Fix: `grpc_endpoint` and `host_gateway_ip`.
8. `refresh` did nothing (`flat L173`), and an action change did not trigger
   one (`flat L175`). Cause: an unchanged definition needs no rebuild. Fix:
   change the base image.
9. The first spoof test was invalid (`flat L79`), then "I made an error — the
   bridge points at different ACLs now. Let me redo this cleanly" (`flat L81`).
   Cause: probe containers left on old state. Fix: rebuild and repeat.
10. A route flush took the default route during the escape test (`flat L189`).
    Fix: restore the route and run the test again.
11. The escape did not reproduce (`flat L303`) and the first label was wrong
    (`flat L311`). Cause: a reply-dependent probe cannot show that egress left.
    Fix: a host listener on the source of a one-way connection (`flat L313`),
    and the capability reported as repeatable with the escape observed once.
12. The mTLS key in a commit: "**A credential leak in my own commit** —
    `.tls/tls.key` is a private key." (`flat L343`). Cause: `git add -A` staged
    the `.tls` directory the run wrote. Fix: `git reset --soft HEAD~1`, unstage,
    delete, commit again, delete it in the `run.sh` cleanup.
13. Requirement 001 on `spike/acl-fence` ("Committed on the wrong branch — that
    belongs on `main`. Fixing.", `flat L557`). Cause: the checkout stood on
    another session's branch. Fix: cherry-pick on a branch from `main`, move
    `main`, reset the checkout to `832b307`.
14. A rebase took the `acl-fence` commits into the branch (`flat L225`). Fix:
    `git rebase --onto 472cf45 d3c2729 spike/two-workshop`.
15. A tracked ADR of the other session changed ("I touched another session's
    tracked ADR — restoring it rather than leaving their worktree dirty",
    `flat L711`). Fix: `git checkout --` on that path.
16. Long sentences, and a synonym pair the linter reported: "The linter pairs
    "start" with "launch" — but "start" here is the OpenShell verb and "launch"
    is the Workshop command." (`flat L267`). Fix: the upstream term stays.
17. `hwt` chose `herdr-plugins` on the dry run (`flat L782`). Cause: `hc get`
    `.cwd` is the pane folder and `.foreground.cwd` is the agent folder
    (`flat L833`). Fix: `--repo`. The defect became a handoff.

## Candidate lessons

1. NEW. Check the host for another session's spike before a run, and avoid its
   ports and object names. "watch out for other spikes running in separate
   sessions (for port conflicts, etc)" (`flat L3`). `.kb/spikes.md` has five
   laws about running a spike and none about a second session or a port
   collision. The records note the collisions after the fact.
2. NEW. Conclude from a run of the committed script on a clean host, and where
   that run disagrees with an earlier manual measurement, record the repeatable
   result and mark the rest as observed once. "That inconsistency must be
   reported honestly, not smoothed over." (`flat L327`). `.kb/writing-style.md`
   §6 requires the report, and not the second run.
3. NEW. Stage a spike directory by explicit path when a run writes a credential
   into it, because `git add -A` will commit it. "**A credential leak in my own
   commit** — `.tls/tls.key` is a private key." (`flat L343`).
   `.kb/project.md` §1 forbids committing a credential, and `.kb/spikes.md` §4
   lists only `.workshop.lock` and `spike/**/*.env` as untracked output.
   `.gitignore` on `main` names no `.tls`.
4. NEW. A fence probe that needs a reply cannot show that a packet left, so
   measure egress with a listener outside the path that records the source
   address. "the agent workshop sent a packet with the plane's source address,
   and the host received it. The egress path is open" (`flat L313`). The record
   states the result and leaves the method in the branch script.
5. NEW. In a checkout a second agent session owns, do not reset, rebase or
   rewrite its work without the person's word, back up its untracked file, and
   re-read any knowledge-base file it adds before you commit. "I did not want
   to leave another session's worktree dirty or silently rewrite their branch"
   (`flat L743`), and "A new `.kb/spikes.md` appeared from the concurrent
   session. Let me read it to comply." (`flat L209`). No file states this.
6. NEW. When `ste-lint.py` pairs an upstream system's verb with this
   repository's command, keep the upstream verb and change the other word.
   "The linter pairs "start" with "launch" — but "start" here is the OpenShell
   verb and "launch" is the Workshop command." (`flat L267`).
   `.kb/writing-style.md` says an upstream term keeps its spelling, and nothing
   about a lint hit that follows.
7. NEW. When `speckit.*` is a command the person runs and not the agent, write
   the committed `requirements.md` directly and leave no `specs/` deposit.
   "the `speckit.*` commands are user-invoked slash commands, so I produced the
   committed artifact directly in the required format instead of leaving a
   `specs/` deposit" (`flat L565`). `.kb/spec-kit.md` describes the deposit path
   only.
8. NEW. Keep an artifact that is outside the repository under `~/tmp`. "put the
   files in ~/tmp" (`flat L411`). `AGENTS.md` and `.kb/` name no location.
9. ALREADY WRITTEN. A NIC-level ACL on a bridged NIC fails with `Invalid device
   option`, and a network ACL on the bridge is the placement.
   `research/acl-fence.md`, Verdict.
10. ALREADY WRITTEN. One bridge per workshop with one ACL per bridge closes the
    source-address escape, and the plane ingress rule is a second layer.
    `research/separate-bridges.md`, Verdict, and ADR 0001, Decision.
11. ALREADY WRITTEN. A lifecycle event reverts the NIC placement while the ACL
    and the bridge survive. Both records, Findings. ADR 0001, Consequences.
12. ALREADY WRITTEN. Install before the fence phase, because the fence blocks
    the archive. `spike/two-workshop/README.md`, and `.kb/fence.md`.
13. ALREADY WRITTEN. A fixed address on a bridged NIC applies at the next boot,
    and the Docker bridge address appears first in `ip -o addr`.
    `research/two-workshop.md`, Gotchas.
14. ALREADY WRITTEN. The gateway driver needs `grpc_endpoint` and
    `host_gateway_ip` off loopback, and the service reads `active` before its
    listener is ready. `research/two-workshop.md`, Findings and Gotchas.
15. ALREADY WRITTEN. A spike branch holds no `adr/` change and the conclusion is
    committed on `main` with the record. `.kb/spikes.md` §7. A prose document
    follows `.kb/writing-style.md` and not the STE standard,
    `.kb/requirements-format.md` §6.
16. ALREADY WRITTEN. DNS stays unfenced, and option C loses because the workload
    names already resolve in the plane. ADR 0002, Decision.
17. ALREADY WRITTEN. Delete the mTLS bundle copy when the run ends, and note
    that a run stopped early leaves it. `research/two-workshop.md`, Gotchas.
18. PROJECT-SPECIFIC FACT. `hwt` reads the pane folder and not the foreground
    process folder: `.cwd` is `git/herdr-plugins` and `.foreground.cwd` is
    `git/monitor-agent` (`flat L833`). It belongs in the `hwt` tool, and the
    session wrote `/tmp/opencode/handoff-hwt-wrong-repo.md` for it.
19. PROJECT-SPECIFIC FACT. The gateway configuration the spikes paid for:
    `bind_address` as `IP:port` in TOML and IP only as a flag, the IP SAN with
    `host.openshell.internal`, and the client that ignores
    `OPENSHELL_LOCAL_TLS_DIR` (`flat L586`). Only the last is in
    `research/two-bridge-gateway.md:88`.

## What should not become a skill

- The `git rebase --onto` recovery (`flat L226`) and the wrong-branch commit.
  Both are general Git practice.
- The one-sentence progress line before each tool call. That is the model's
  style and not a convention the person stated.
- The option tables the agent wrote for the DNS choices (`flat L596`, `L682`).
  The decision and its reason are in ADR 0002.
- The bridge, address and port names. They are one run's values, and the next
  spike had to choose new ones.
- The readiness wait as a rule for every action. It belongs to the OpenShell
  user unit on this host, and the project replaced OpenShell.
- The `.tls` leak as a story about one commit. The lesson is candidate 3.
