# ses_e32ea95acffeyejYnGLXXe5Ge8: Research OpenShell custom compute drivers

## What the person asked for

The session holds one prompt. It was written by the spawning session
(`ses_e33d0c7c5ffejcYl5L4FlzKPPv`) on the person's question at flat:407 of that
transcript, and no human turn appears in this transcript (flat:4-16).

- "You are doing read-only documentation research for a design session. Do not
  edit any files, do not create branches, do not touch GitHub issues. Research
  and report back" (flat:4). The prompt closes that sentence with "your reply is
  the deliverable."
- "Does OpenShell support custom or extension COMPUTE drivers (out-of-tree or
  plugin drivers) ... Or is `compute_driver` limited to the built-in set
  (kubernetes, podman, docker)? Quote the doc or source that answers this."
  (flat:10)
- "Is there any existing LXD, incus, or libvirt compute driver for OpenShell,
  upstream or community?" (flat:12)
- "Topology consequences, reasoned from the contract: if sandboxes were LXD
  containers, where could they live", naming "nested LXD inside the plane
  workshop container, or host-level LXD with the gateway reaching the host LXD
  socket?" (flat:14)
- "Distinguish documentation claims from source-code reading. Keep the report
  under about 60 lines. Cite URLs for every doc claim." (flat:16)

## What was produced, and whether it worked

One prose report in the reply (flat:32-65). No file, no branch, no issue, which
matches the prompt.

- Q1 verdict: "SUPPORTED (documented, first-class extension point)" (flat:34).
  Any driver name outside the built-ins selects an extension driver, configured
  with `compute_driver = "<name>"` and `[openshell.drivers.<name>] socket_path`
  under a local Unix socket (flat:36-38).
- Q2: the driver contract from `proto/compute_driver.proto`, thirteen baseline
  RPCs, and the ownership split in which the driver owns placement and fencing
  while the isolation backend inside the workload owns enforcement (flat:42-48).
- Q3: `canonical/openshell-driver-lxd` exists, Rust, AGPL-3.0, maintained, and
  passes upstream conformance (flat:50-52).
- Q4 and Q5: sandboxes become pairs of LXD instances, the fence is two OVN
  per-NIC ACLs, and the driver requires OVN. Nested LXD costs nesting plus OVN
  inside the plane. Host-level LXD makes the plane hold a host control-plane
  credential, which LXD projects and a restricted certificate only narrow
  (flat:54-65).
- The reply is the whole deliverable, and the session wrote no branch, so nothing
  from it reached `main`. The parent session used it in the Q13 and Q14 questions
  of `ses_e33d0c7c5ffejcYl5L4FlzKPPv` (its flat:481-510), and the person's answer
  at its flat:515 opened the sandbox-topology path.
- The current `adr/0001` keeps one trace of that path: "A host OVN fence. The
  November 12 pivot named it, but nothing in this repository measures it."
- Verified: every claim is a documentation or source reading with a URL. Not
  verified: nothing was run, and no driver was installed.

## Corrections the person made

(none found). No human turn appears in this transcript.

## Conventions, commands and values stated and written down nowhere

- The extension driver socket default: `/var/run/openshell-driver.sock` (flat:56).
- The capability name the gateway and driver exchange during negotiation:
  `openshell.compute.contract`, protocol 1.0, checked with `openshell gateway
  info` (flat:40).
- The contract's hard rule about the token split: `launch_authentication` bytes
  "the driver **must split** between supervisor and workload runtime (supervisor
  bearer tokens must never reach the workload)" (flat:48).
- The privilege drop the LXD driver uses, shared with the Podman driver:
  `openshell-sandbox launch-capability-free` (flat:59).
- The driver's admitted fence gap: "the OVN network's own DHCP/DNS stays
  reachable" (flat:58).
- The shape the report names as a middle option: "the driver is an unsupervised
  standalone service ... so it can run in its own minimal container sharing only
  the socket with the gateway" (flat:65).

## Failures, their cause, and the fix

No `!! FAILED` line appears in this session's tool log, and no retry is visible
in the prose. Every fetch and search it ran answered.

## Candidate lessons

1. NEW. A dispatched research task with no ticket and no file leaves no record.
   This report is the deliverable, so its findings live only in this transcript
   and in the parent's question text. Give every dispatch a ticket number or a
   path to write, and say which one. Quote: "Do not edit any files, do not create
   branches, do not touch GitHub issues." (flat:4), and the rest of that sentence
   says the reply is the deliverable.
2. NEW. A claim about what an extension point allows is answered from the
   contract source, and the report labels each claim as documentation or as code
   reading. Quote: "Distinguish documentation claims from source-code reading."
   (flat:16). The report does it for every answer (flat:36-48).
3. NEW. When a candidate solution carries a prerequisite the host lacks, the
   prerequisite belongs in the verdict, ahead of the benefits. Quote: "the
   driver **requires OVN**", with the reason that it "refuses unfenceable
   sandboxes" (flat:63). The parent session made it a gate in its Q13 (flat:500
   of `ses_e33d0c7c5ffejcYl5L4FlzKPPv`).
4. PROJECT-SPECIFIC FACT. OpenShell extension compute drivers are documented, the
   contract is `compute_driver.proto`, and `canonical/openshell-driver-lxd`
   exists and needs OVN. This is a record about a dropped dependency, and
   `adr/0001` keeps only the OVN rejection.
5. PROJECT-SPECIFIC FACT. The three placements and their costs: nested LXD in the
   plane, host-level LXD with a scoped certificate, and a standalone driver
   container that shares only its socket. The last one is the shape that keeps a
   host credential out of the plane, and no record states it.
6. PROJECT-SPECIFIC FACT. A workload process launched capability-free and
   non-root changes what "the enforcer shares the agent's trust domain" means.
   That reasoning reversed the parent's Q12 answer (its flat:489 and flat:517).

## What should not become a skill

- The thirteen RPC names and the `DriverSandboxSpec` field list (flat:44-48).
  They are the contract of one upstream version.
- The driver's boot sequence (flat:59). It is an implementation reading of one
  Rust repository.
- "Keep the report under about 60 lines" (flat:16). It is the shape one parent
  session wanted, and `.kb/writing-style.md` already asks for a list over a
  paragraph and for state-what-was-not-verified.
- The URL list. It belongs to a findings record.
