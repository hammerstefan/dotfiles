# ses_e39f22ad1ffe7OvgCgGZCPalVX: Running OpenShell inside Workshop container

## What the person asked for

- "@prototype is running openshell container inside a workshop possible?" (USER msg 1, flat line 3)
- "record all investigation findings in hindsight" (USER msg 2, line 65)

## What was produced, and whether it worked

- A throwaway spike on branch `spike/openshell-in-workshop`, commit `30857ac`, "on top of `main`. `main` holds no spike code." (line 54)
- The spike directory holds `README.md`, `run.sh`, `setup-inside.sh`, `verify-inside.sh`, `probe.sh`, `.workshop/spike.yaml` and `.workshop/spike-vm.yaml` (tool log lines 126, 127, 184, 185, 186, 187, 197). The commit ran at tool log line 203, and the agent returned to `main` at tool log line 204.
- Verified with a running system, in the agent's words: "The sandbox reached the `Ready` phase and `openshell sandbox exec` ran a command as `uid=1000(ubuntu)` inside it." (line 17). The commands are listed at lines 25 to 28.
- Not verified, in the agent's words: "The VM runtime, the MicroVM compute driver inside a Workshop, GPU passthrough, rootless Podman inside a Workshop, and the default policy on egress." (line 50)
- Five Hindsight documents were ingested on request (tool log lines 205, 209 to 212).
- A `.workshop.lock` file reached the index and was removed before the commit: `git reset spike/openshell-in-workshop/.workshop.lock && rm -f ...` (tool log line 202).
- No `!! FAILED` line exists in the tool log.

## Corrections the person made

- (none found)

## Conventions, commands and values stated and written down nowhere

- The person named the skill by its mention form, "@prototype" (line 3), and named no option, path or ticket.
- The agent reported one host requirement that no repository file records: "`workshop launch` refuses to start a VM workshop until `sudo snap set workshop workshop.experimental-vms=1` is set, and that needs your password." (line 19). Every `research/*.md` spike record lists "The `lxd-vm` runtime" as not verified.
- The agent stated an assumption about the skill it was given: "The prototype skill's two branches are UI and state-model demos, neither of which fits a feasibility question, so I built a runnable script and stated the assumption here." (line 54)

## Failures, their cause, and the fix

- No tool call failed. The work contains a sequence of measured failures inside the workshop, each stated with its cause:
  - `openshell sandbox create --from base` pulled a 404 image. Cause, in the agent's words: "`--from base` is not a keyword in 0.1.7. The command sends it as an image reference and the pull fails with a 404." (line 43). Fix: name a real image.
  - The default sandbox image failed the driver. Cause: "`ghcr.io/nvidia/openshell/sandbox:latest` has no `/etc/passwd`, and the driver fails with `IdentityResolutionFailed` when it is the workload image." (line 42). Fix: `--from docker.io/library/ubuntu:24.04`.
  - The gateway did not answer under `workshop exec`. Cause: "The gateway is a systemd user service, and `workshop exec` has no user bus. `loginctl enable-linger <user>` is needed first." (line 41).
  - The CLI and the snap looked in different PKI directories. Cause and fix: "The snap keeps the gateway PKI in its own directory while the CLI looks in the user configuration directory. Point both at one place with `OPENSHELL_LOCAL_TLS_DIR`." (line 45). A later record contradicts this (see the candidate list).
  - The Podman driver would not start. Cause: "The Podman driver needs Podman 5.x. The archive ships 4.9.3, so the Docker driver is the one that works without extra sources." (line 44).

## Candidate lessons

- "`--from base` is not a keyword in 0.1.7. The command sends it as an image reference and the pull fails with a 404." (line 43). PROJECT-SPECIFIC FACT. No `research/` record holds the OpenShell install or image facts, because the spike's findings went to Hindsight only.
- "`ghcr.io/nvidia/openshell/sandbox:latest` has no `/etc/passwd`, and the driver fails with `IdentityResolutionFailed` when it is the workload image." (line 42). PROJECT-SPECIFIC FACT. Absent from `research/` and `.kb/`, and the same fact reappears in ses_e3888085 as an image requirement.
- "The gateway is a systemd user service, and `workshop exec` has no user bus. `loginctl enable-linger <user>` is needed first." (line 41). PROJECT-SPECIFIC FACT. `research/two-workshop.md` records only the narrower symptom, "the gateway's user bus is not ready when the script first reaches `systemctl --user`", and no file states the linger requirement.
- "`workshop launch` refuses to start a VM workshop until `sudo snap set workshop workshop.experimental-vms=1` is set" (line 19). PROJECT-SPECIFIC FACT. `.kb/agent-workshop.md` and `AGENTS.md` state no host requirement for the `lxd-vm` runtime.
- "The snap keeps the gateway PKI in its own directory while the CLI looks in the user configuration directory. Point both at one place with `OPENSHELL_LOCAL_TLS_DIR`." (line 45). ALREADY WRITTEN as a contradiction: `research/two-bridge-gateway.md` records "The client ignores `OPENSHELL_LOCAL_TLS_DIR`. The bundle has to be at `/root/.config/openshell/gateways/plane/mtls/`." The session's fix did not hold for a named gateway.
- "A sandbox does not see the Workshop's `/project` mount." (line 46). PROJECT-SPECIFIC FACT. `AGENTS.md` states the mount rule for a project directory and no file states the sandbox exception, which no longer applies because ADR 0001 abandoned the sandbox.
- "The prototype skill's two branches are UI and state-model demos, neither of which fits a feasibility question, so I built a runnable script and stated the assumption here." (line 54). NEW. The same misfit is stated again in ses_e355228c: "The LOGIC/UI HTML branches don't apply here; the artifact shape is fixed by the prior spike". No repository file tells an agent what to do when a skill's only branches do not fit.
- "the scripts install packages from the upstream OpenShell install script and the Ubuntu archive, and they hold no credentials" (line 60). ALREADY WRITTEN (`.kb/project.md`§1 on credentials, `.kb/spikes.md`§5 on cleanup).
- `.workshop.lock` belongs outside the index. ALREADY WRITTEN (`.kb/spikes.md`§4, which names `.workshop.lock` in `.gitignore`). The agent had to remove it by hand, so the ignore entry was missing at the time of this session.

## What should not become a skill

- The OpenShell install procedure and its version numbers. Upstream documents its own installer, the project abandoned OpenShell in ADR 0001, and the numbers have moved since 0.1.7.
- "Use `docker.io` rather than Podman inside a workshop." It is one measurement of one version, and the decision that followed removed the container runtime from the workshop.
- The five Hindsight document titles and their split. They describe a memory layout, and the repository records findings under `research/`.
