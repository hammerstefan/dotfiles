# ses_e355228c7ffe54Y3dIQirNBebh: ACL fence spike handoff monitor prototype

## What the person asked for

- "@prototype /tmp/opencode/handoff-monitor-agent-acl-fence-spike.md" (USER msg 1, flat line 3)
- "ignore the ADR for the spike" (USER msg 2, line 11)

## What was produced, and whether it worked

- A spike on branch `spike/acl-fence` at `spike/acl-fence/`: `README.md`, `run.sh`, `apply-acl.sh`, `probe.sh`, `.workshop/fence.yaml` (tool log lines 124 to 127, 130 and 138).
- Commit `c3b9919`, subject "spike(workshop): probe an LXD ACL fence on a workshop NIC" (line 67, tool log line 139). The runtime files stayed untracked and the ADR files were untouched (line 65).
- Verdict, in the agent's words: "A per-workshop egress fence through a NIC-level LXD ACL does not exist on this system. LXD 6.10.1 rejects all three ACL device options on a workshop container's bridged NIC" (lines 71 to 72), with the verbatim error at lines 73 to 76.
- Verified by a run: the ACL object is creatable in the workshop project and survives `workshop refresh` and `workshop remove` plus `workshop launch`, `workshop refresh` on an unchanged definition is a no-op, `remove` plus `launch` gives a fresh DHCP address, `1.1.1.1:443` stayed reachable with no fence bound, and `workshop exec` and `workshop shell` ran (lines 80 to 87).
- Verified cleanup: "the trap deleted both ACL copies, the workshop is removed, the listener is gone, and the user's three workshops are untouched" (line 61).
- Not verified: `workshop exec` and `workshop shell` under an enforced default drop, because no fence could be bound (line 86).
- The verdict was ingested to Hindsight and the initiative page recorded the spike as completed with a negative result (tool log lines 140 and 141).
- No `!! FAILED` line exists in the tool log except one: a `404` on a documentation fetch (tool log line 119). Every other failure in this session is described in the conversation, not by a failed tool call.

## Corrections the person made

- The agent said it would read the material it had been handed: "Now let me read the prior spike's full contents and the Hindsight initiative page." (line 9). The person replied "ignore the ADR for the spike" (line 11). The agent then stated what that removed: "No OpenShell, no Docker, no sandbox inside the workshop. The spike probes the workshop container's own egress." (line 15)
- No other correction.

## Conventions, commands and values stated and written down nowhere

- The scope rule in the person's words: "ignore the ADR for the spike" (line 11). `.kb/spikes.md`§7 states that the spike branch carries no `adr/` changes, and no file states that a spike runs without the constraints of a pending record.
- The person named no command, path or key. The path in the request, `/tmp/opencode/handoff-monitor-agent-acl-fence-spike.md`, is outside the repository and was deleted by ses_e35651f4.
- Host values the agent measured and no main-checkout file records at the time of the run: LXD 6.10.1, workshop 0.9.9, the per-user project `workshop.1077165261` with `NETWORKS: NO` (line 21), and the firewall driver `nftables` (line 33). The LXD version, the project's missing networks and the driver are in `research/acl-fence.md`. The release line is in `research/development-workshop-ctlcmd.md`, and the project name is in `research/development-workshop-channel.md`.

## Failures, their cause, and the fix

- One documentation fetch returned `404` for `https://raw.githubusercontent.com/canonical/lxd/main/doc/reference/network_acls.md` (tool log line 119). The fix was the file one directory over, `doc/howto/network_acls.md` (tool log line 121).
- The first run aborted at the safety check. What ran: `spike/acl-fence/run.sh` (tool log line 129). Cause, in the agent's words: "Port 9999 is held by an unrelated `rootlessport` process, so the listener can't bind there. I'll switch the spike to port 19999 and rerun." (line 53). What ended it: `HOST_PROBE_PORT` default changed from 9999 to 19999 (tool log line 133).
- The probe listener was one-shot, which invalidated part of the second run. Cause: "the `nc` listener was one-shot (so only the baseline tested the private target with a live listener, later `refused` results are the closed listener, not a fence)" (line 59). What ended it: `nc -lk` in `run.sh` (tool log line 136), and the README states the caveat (line 89).
- A failed retry left a second ACL copy behind. Cause: the apply script retried in the default project after the workshop project succeeded. What ended it: the cleanup trap, and the README now deletes both objects (line 59).
- A documentation contradiction surfaced before the script was written: "The context7 snippet says \"ACLs are only supported on OVN NICs\" in one section, which contradicts the plan for a bridged NIC" (line 33). The agent resolved it against the upstream page, which documents NIC assignment for OVN NICs only (line 37).
- The record the spike was written to answer changed while the spike ran: "I also notice the ADR filename changed on disk while the spike ran, so you are editing it right now" (line 65).

## Candidate lessons

- "LXD 6.10.1 rejects `security.acls`, `security.acls.default.egress.action`, and `security.acls.default.ingress.action` on the workshop NIC device" (line 78). ALREADY WRITTEN (`research/acl-fence.md` Verdict).
- "The workshop LXD project holds no networks. Its instances use `workshopbr0` from the default project, and workshopd attaches the NIC as an instance-level device named `workshop.network`." ALREADY WRITTEN (`research/acl-fence.md` Findings).
- "The firewall driver on this host is nftables, so IP-range rule subjects are available" (`research/acl-fence.md`). The session measured it at line 33. ALREADY WRITTEN.
- "Port 9999 was taken on this host by an unrelated `rootlessport` listener. The probe listener defaults to 19999 through `HOST_PROBE_PORT`." (line 53). ALREADY WRITTEN (`research/acl-fence.md` Gotchas).
- "A plain `nc` listener accepts one connection and exits. ... `run.sh` now uses `nc -lk`." (line 59). ALREADY WRITTEN (`research/acl-fence.md` Gotchas).
- "The context7 snippet says \"ACLs are only supported on OVN NICs\" in one section, which contradicts the plan for a bridged NIC" (line 33). NEW. A documentation index answers with a fragment from one section, and the repository tells an agent in no file to check a contradiction against the upstream page before building on it.
- "I also notice the ADR filename changed on disk while the spike ran, so you are editing it right now" (line 65). NEW. The person edits the checkout while an agent works in it, and ses_e35651f4 records the other half of this, where `main` moved under a commit. No file states how an agent handles a file that another writer changed during its run.
- "the trap deleted both ACL copies, the workshop is removed, the listener is gone, and the user's three workshops are untouched" (line 61). ALREADY WRITTEN (`.kb/spikes.md`§5: "A spike cleans up what it creates", and `research/acl-fence.md` Findings on the other workshops).
- "A spike measures the ACL fence mechanics on its own, without the ADR's two-layer architecture." (line 13). ALREADY WRITTEN (`.kb/spikes.md`§1, one question with a running system).
- "No OpenShell, no Docker, no sandbox inside the workshop." (line 15). ALREADY WRITTEN (`.kb/spikes.md`§1) as a scope rule, and the person's narrower scope was recorded on the initiative page (tool log line 122).

## What should not become a skill

- The verbatim LXD error text and the three key names. `research/acl-fence.md` holds the measurement, and upstream LXD documents its own options.
- The port 19999 choice and the `HOST_PROBE_PORT` name. They are one host's workaround, recorded in the spike's gotchas.
- The prototype-skill misfit. It was already stated in ses_e39f22ad, and this session states it once more without adding a rule.
- The verdict itself, "no per-workshop NIC-level ACL on LXD 6.10.1", as a skill. It is a measurement of one version on one host, and `research/acl-fence.md` records it with the branch.
