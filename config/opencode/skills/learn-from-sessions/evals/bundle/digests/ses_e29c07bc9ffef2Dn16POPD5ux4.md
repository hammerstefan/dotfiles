# ses_e29c07bc9ffef2Dn16POPD5ux4: Research ticket 47: LXD project scope

This session is a research subagent spawned by ses_e2a211dc0ffenjeQD6D6v7DvqQ to resolve wayfinder ticket #47. It has one user message, and that message is the parent session's brief, not the person's own words. The session ran in `/home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/spike-development-workshop` on 13 November 2026.

## What the person asked for

The person did not speak in this session. The brief that stands in for their ask, quoted:

- "Resolve wayfinder ticket #47 in hammerstefan/monitor-agent: \"Can a restricted LXD certificate run the fence against a disposable copy?\""
- "A disposable target would let the everyday loop run the fence without touching the product. Four checks decide whether a project-scoped certificate is enough."
- The four checks: a project with `features.networks: true` and a restricted certificate that creates a bridge, an ACL and a container and runs `lxc exec`. A second project with a network of the same name. A second project with a bridge on the same subnet. A `macvlan` network on `enp1s0f0` and `all-projects=true`, "Both should fail. Record the exact error."
- Constraints: "Use project names beginning `monitor-agent-probe`. Do not touch the default project's `mon-*-br` networks or ACLs, the `workshop.1077165261` project, or any running workshop instance." "Clean up every project, network, container, and certificate you create. Revoke the certificate." "Do not create, switch, or commit on any git branch in the repository. Write the findings markdown to `/tmp/opencode/chart/research-lxd-scope.md`."

## What was produced, and whether it worked

- `/tmp/opencode/chart/research-lxd-scope.md`. The parent copied it to `research/development-workshop-lxd-scope.md` on branch `research/development-workshop-lxd-scope`, which merged to `main` through pull request #58.
- The record holds the verdict "No", the method, four check sections with the commands and the exact errors, a "Findings that decide the question" section, what it means for a disposable target, cleanup, and sources.
- **Verified by measurement:** a bridge in a non-default project is refused with `Network type does not support non-default projects`, and the same command as administrator in the same project gives the same error, so the certificate is not the cause. An ACL, a container and `lxc exec` succeed in that project. A certificate restricted to a project with `features.networks: false`, and one restricted to `default`, can create and delete networks in the default project. A certificate restricted to `default,workshop.1077165261` lists both live instances. A restricted certificate can configure a NIC with `nictype=macvlan` or `nictype=physical` on `enp1s0f0`.
- **Not verified, stated in the record:** whether an OVN network would work, because no OVN uplink exists on this host. Whether the `macvlan` and `physical` NIC devices attach, because both instances were deleted before they were started. Checks 2 and 3 as written, because a project bridge cannot exist to collide.
- **Cleanup was verified after the fact:** every probe project, network, ACL, profile, instance and certificate removed, and `ip -br link show | grep -i maprobe`, `lxc project list` and `lxc config trust list` checked afterwards.
- **A defect in the record on `main`.** `research/development-workshop-lxd-scope.md` holds 25 em dashes and 9 semicolons, and `.kb/writing-style.md` §2 forbids both. I checked the four `research/development-workshop*.md` files on `main` today. The other three hold none. The style pass that `AGENTS.md` requires before a commit was not run on this one.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

- The probe project prefix: "Use project names beginning `monitor-agent-probe`". The names used were `monitor-agent-probe-a`, `-b` and `-c`.
- The near-name networks used in the default project: `maprobe-sub-a`, `maprobe-sub-b`, `maprobe-e-br`, and the addresses `10.199.77.1/24`, `10.199.78.1/24`, `10.199.88.1/24`, `10.199.91.1/24`. These are the probe's own values and the record keeps them.

## Failures, their cause, and the fix

- No `!! FAILED` line appears in this session's tool log.
- The two client-side facts the record keeps are the wrong turns that cost time. `LXD_CONF` is ignored by `/snap/bin/lxc` because the snap launcher removes the variable, so every request went out as the operator's own certificate. The fix was to call `/snap/lxd/current/bin/lxc` with `LXD_CONF` set. The temporary configuration directory needs `servercerts/<remote-name>.crt`, named after the remote and not the host, or the answer is `x509: certificate signed by unknown authority`. The agent first wrote `servercerts/127.0.0.1.crt` and then also copied it to `servercerts/probe.crt`.
- A `lxc init -d eth0,...` device flag failed twice with `Error: Cannot override config for device "eth0": Device not found in profile devices`, once with a profile and once with `--no-profiles`. The cause is that `-d` overrides a device the profile already defines. The fix, which the record's working commands show, is to create the instance and then add the NIC with `lxc config device add`.
- A check that failed for the wrong reason, recorded as such: the `macvlan` network refused with `Network type does not support non-default projects`, so "The failure is the project rule, not the host-interface rule the ticket expected."

## Candidate lessons

- ALREADY WRITTEN. The verdict and the structural reason, that a bridge cannot exist in a non-default project and a disposable target needs its own LXD daemon. `research/development-workshop-lxd-scope.md`, and `workshop-host-authority` under "A restricted certificate and the fence".
- ALREADY WRITTEN. That a certificate scoped to a project with `features.networks: false` reaches the default project's networks and ACLs, and that this is the product's own fence under another login. `research/development-workshop-lxd-scope.md` and `workshop-host-authority`.
- ALREADY WRITTEN. That a restricted certificate can configure a `macvlan` or `physical` NIC on `enp1s0f0`, and that the `restricted.*` project options are what should stop it. `research/development-workshop-lxd-scope.md`, check 4.
- ALREADY WRITTEN. The `LXD_CONF` trap and the `servercerts/<remote-name>.crt` name. `research/development-workshop-lxd-scope.md` and `workshop-host-authority`.
- ALREADY WRITTEN. A second bridge on an address already in use is rolled back rather than half started. `research/development-workshop-lxd-scope.md`, check 3.
- ALREADY WRITTEN. Grep a drafted record for em dashes and semicolons before the commit. `AGENTS.md`, "A skill's mandated output format still follows `.kb/writing-style.md`". The lxd-scope record shows the check was skipped, so this is a rule to keep, not a new one.
- NEW. When a check's premise turns out not to exist, say so and measure the nearest form, labelled as an approximation. "**Not testable as specified, because the network never exists.** No interface is created, so there is nothing to collide." Then "Approximated in the default project, which is the only place a bridge can be created, using a certificate restricted to `default`". The record keeps both statements apart, which is what lets a reader trust check 3 without believing check 2 was run.
- NEW. A check that returns the expected verdict for an unexpected rule answers a different question, and the record must name the rule that refused. "The request never reaches the point where `parent` would be judged. The failure is the project rule, not the host-interface rule the ticket expected." The ticket asked whether a `macvlan` network should fail, and it did fail, for the project rule.
- NEW. `lxc init -d <device>` cannot introduce a device that no profile defines, and answers `Cannot override config for device "eth0": Device not found in profile devices` even with `--no-profiles` (tool log, twice). Create the instance, then add the NIC with `lxc config device add <instance> eth0 nic ...`. The record shows only the working form, so a later probe would meet the same refusal.

## What should not become a skill

- The probe names, prefixes and subnets. They were one run's disposable values.
- The `x509` message as a trust symptom. The record keeps it once, next to the real cause. A skill that repeated it would teach the wrong diagnosis.
