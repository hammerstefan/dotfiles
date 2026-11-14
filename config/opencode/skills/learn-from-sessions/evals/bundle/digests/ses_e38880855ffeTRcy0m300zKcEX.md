# ses_e38880855ffeTRcy0m300zKcEX: Hermes in a podman container

## What the person asked for

- "explore the possibility of running hermes inside an openshell podman container directly for this project, and forgo workspaces" (USER msg 1, flat line 3)
- "you can pull and update openshell repo if it helps" (USER msg 2, line 5)
- "record all investigation findings in hindsight" (USER msg 3, line 58)

## What was produced, and whether it worked

- One Hindsight document, "Feasibility: Hermes in an OpenShell Podman sandbox on the host, forgoing Workshop (monitor-agent)" (tool log line 129). The agent's summary of it is at lines 60 to 69.
- No repository file was written and no branch was created. The ingested document states "no decision taken, no host changes made (no sudo, no installs)" (tool log line 129).
- Verified live on the host, in the agent's own table (lines 35 to 42): `openshell status` connected at version `0.0.45`, the `openshell-gateway` user service active, rootless `podman` with `podman.socket` active and `ubuntu:24.04` run, the supporting packages installed, a subuid range of 500000 to 565535, and host podman `4.9.3`.
- Verified by reading: the OpenShell Podman driver source, its gateway configuration documentation, and the OpenShell `workspaces.mdx` page (tool log lines 104, 105, 120 to 124).
- Not verified: any part of the target architecture. No sandbox was created, no image was built, and no plucky package was installed. The agent names the reason for each gap but runs none of them.

## Corrections the person made

- (none found)

## Conventions, commands and values stated and written down nowhere

- The person's permission for third-party checkouts: "you can pull and update openshell repo if it helps" (line 5). The agent then ran `git -C ~/git/OpenShell pull --ff-only` (tool log line 98).
- The person's scope words "forgo workspaces" (line 3). The agent read two meanings and stated both: "two readings, both fine. The Workshop layer is dropped entirely, and OpenShell's own \"workspace\" feature (RBAC for shared gateways) is simply unused" (line 31). No repository file defines the term.
- The agent's claim of a hard host requirement, recorded nowhere in the repository: "**Podman 5.x is a hard requirement.** Upstream ships no Linux server binaries (confirmed with the maintainer's note)" (line 46), against "Host podman version, **4.9.3** (noble archive + ESM)" (line 42).
- The agent's stated parent uid value: "this host's LDAP uid is large (`1077165261`)" (line 29). The repository holds that number only as an LXD project name, `workshop.1077165261`, in the `research/development-workshop*.md` records.

## Failures, their cause, and the fix

- No `!! FAILED` line exists in the tool log. The session read and inspected; it did not attempt an upgrade or an install.
- Three gaps are stated with their cause and no fix was applied:
  - Podman version. Cause: "the realistic routes on noble are: apt-pin the container stack (`podman, crun, conmon, netavark, passt, ...`) from Ubuntu 25.04 *plucky* at priority 991 while pinning everything else back to noble" (line 46). The agent notes the cost: "Needs sudo; this is the biggest piece of host surgery."
  - Gateway version. Cause: "The installed gateway predates the Podman driver and the `version = 2` config format (`preflight` rejects the old file)." Fix named: "`install.sh` crosses a flagged breaking boundary (`0.0.37`), so it wants `OPENSHELL_ACK_BREAKING_UPGRADE` and a gateway.toml rewrite." (line 47)
  - The workload image. Cause: the image must hold `/etc/passwd`, "the spike gotcha: the default sandbox image lacks it and fails `IdentityResolutionFailed`" (line 48). Fix named: build an image on Ubuntu 24.04 with Hermes and `terminal: backend: local`.

## Candidate lessons

- "**Podman 5.x is a hard requirement.** Upstream ships no Linux server binaries" (line 46), against a host at `4.9.3` (line 42). PROJECT-SPECIFIC FACT. No repository file records the Podman driver requirement.
- "`install.sh` crosses a flagged breaking boundary (`0.0.37`), so it wants `OPENSHELL_ACK_BREAKING_UPGRADE` and a gateway.toml rewrite" (line 47). PROJECT-SPECIFIC FACT. No repository file records the OpenShell upgrade boundary.
- "With `userns = \"keep-id:uid=1000,gid=1000\"`, files the sandbox writes into the repo land owned by *your* host user ... `auto`/`no-map` userns makes bind-mounted host files unreadable per the driver source." (line 29). PROJECT-SPECIFIC FACT. No repository file records the userns mapping.
- "The Podman driver supports `bind` mounts (opt-in: `enable_bind_mounts = true` + resource admission off)." (line 29). PROJECT-SPECIFIC FACT. The value exists in no repository file.
- The `/etc/passwd` requirement appears again here, from the earlier spike: "`/etc/passwd` present (the spike gotcha: the default sandbox image lacks it and fails `IdentityResolutionFailed`)" (line 48). This confirms the fact from ses_e39f22ad and keeps it out of the repository. PROJECT-SPECIFIC FACT, as in that digest.
- "linger-based persistence of the gateway across logout (currently `Linger=no`)" (line 54). PROJECT-SPECIFIC FACT. It is the counterpart of the finding in ses_e39f22ad that a gateway started through `workshop exec` needs `loginctl enable-linger`.
- A feasibility answer that changes the runtime should name what it costs the existing decision. Quote: "If this direction looks right, the natural next step is a `spike/hermes-in-openshell-podman` branch mirroring the previous spike's shape ... before anyone writes an ADR or touches `.kb/project.md`." (line 56). ALREADY WRITTEN (`.kb/spikes.md`§7, the findings record and the ADR land together).

## What should not become a skill

- The plucky apt-pin recipe with priority 991. It pins one Ubuntu release pair at one moment, and ADR 0001 removed the need for Podman.
- The OpenShell driver configuration keys (`compute_driver`, `userns`, `enable_bind_mounts`). Upstream documents its own gateway file, and the project abandoned OpenShell.
- The two readings of "forgo workspaces". The ambiguity was resolved by the session and the whole runtime was later dropped, so no rule survives it.
- The target architecture diagram. It describes an arrangement no spike ran and no record accepted.
- "Ask before a step that needs `sudo`." The agent disclosed the cost, "Needs sudo; this is the biggest piece of host surgery." (line 46), and asked before it did anything, so there is no failure to encode.
