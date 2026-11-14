# ses_e3a365970ffeT147YMK7Qjx9Wu: Hermes network access with OpenShell

## What the person asked for

- "explore our options for using hermes in workshop while leveraging pieces of nvidia openshell https://github.com/NVIDIA/OpenShell . In particular I'm interested in the network access proxy/policy system to restrict what hermes can do on the network" (USER msg 1, flat line 3)
- "is it possible run to openshell's policy proxy outside of the hermes container and force network through it? E.g. the proxy is running on host (directly or as a container or as a workshop) and hermes must egress through the proxy" (USER msg 2, line 61)
- "container in the workshop is off the table. what are easy options forward?" (USER msg 3, line 146)
- "if workshop allowed to configure a per-workshop network bridge, would that help?" (USER msg 4, line 212)
- "record all investigation findings in hindsight" (USER msg 5, line 261)

## What was produced, and whether it worked

- No file in the repository was written. The agent states it: "I wrote nothing to the repository. The findings are in Hindsight only." (line 291)
- Five Hindsight documents were ingested and one initiative page was captured, "Restrict the Hermes agent's network access inside a Workshop" (tool log lines 371 to 376).
- Verified by reading only: the OpenShell documentation and source, the Hermes egress documentation, the Workshop security and tunnel pages, and the LXD network ACL page. The agent states what it did not run: "I did not run any of it, so the LXD ACL behavior on the `workshopbr0` bridge and the systemd user unit drop-in remain unverified." (line 144)
- The six-option analysis is in no committed file. ADR 0001, the record that later settled this question, cites none of it.
- The LXD ACL page needed seven separate fetches (tool log lines 352 to 361) before the agent extracted the bridge limitation text.
- No command was run against a workshop or the network fence. The agent queried the SDK Store with `sdk find` and `sdk info` (tool log lines 325, 327, 331, 341), and read the host with `which`, `ls` and `git log`.

## Corrections the person made

- The agent's recommendation was the container arrangement: "If Hermes can run in a container inside the workshop, put it on an `internal` bridge with no default route and put the OpenShell proxy in endpoint-only mode on an `egress` bridge. That gives a complete fence, the full L7 rule set, and no Workshop product change." (line 140). The person answered "container in the workshop is off the table. what are easy options forward?" (line 146).
- No other correction. The later turns are questions, not corrections.

## Conventions, commands and values stated and written down nowhere

- The standing constraint, in the person's words: "container in the workshop is off the table" (line 146). It was written into no repository file, and the agent itself later noted the wording can be read two ways: "That raises a question about your \"container in the workshop is off the table\" constraint. ... If it means the agent does not run in a container, the spike still stands and the mediated arrangement is available without the `docker-ce` SDK." (line 285)
- The person stated no command, path, flag or ticket key in this session. Every command in the replies (`hermes egress install`, `workshop connect`, `lxc network acl`) is the agent's proposal.

## Failures, their cause, and the fix

- No `!! FAILED` line exists in the tool log.
- The agent guarded one fetch against an upstream rate limit. The Rego fetch treats a body that starts with `429` or is shorter than 1000 bytes as a failed fetch (tool log line 344).
- The LXD documentation fetch passed through a rewritten page path. The agent changed the URL until `https://raw.githubusercontent.com/canonical/lxd/main/doc/howto/network_acls.md` returned the text (tool log line 362). That file is the one ses_e355228c reached after a `404` on `doc/reference/network_acls.md`.

## Candidate lessons

- "A proxy without a fence is advisory. Any process in the container that ignores `HTTPS_PROXY` or opens a raw socket reaches the internet directly, because the workshop's egress is open." (line 113). ALREADY WRITTEN (`adr/0001-hermes-runs-in-a-fenced-agent-workshop-and-a-plane-workshop-proxy-mediates-its-web-egress.md`, Context: "Workshop does not filter outbound traffic.").
- "the fence is per-workshop, so the agent gets a workshop of its own" (line 210). ALREADY WRITTEN (`adr/0001`, Decision: "Each workshop has one dedicated LXD bridge and one fixed address on that bridge.").
- "An ACL rule matches CIDR blocks, IP ranges, ports and protocols. An allowlist of cloud endpoints becomes a list of addresses, and cloud endpoints rotate addresses." (line 235). ALREADY WRITTEN (`adr/0001`, rejected alternative "A fence without a proxy").
- "Identity resolution needs the proxy and the client in one network namespace, because it finds the socket owner through `/proc`. A proxy on the host cannot do that for a client in a container." (line 100). PROJECT-SPECIFIC FACT. No file under `research/` records the endpoint-only mode of the OpenShell proxy.
- "It cannot block the baseline service rules. LXD adds its own baseline network service rules before the ACL chain, so ACL rules cannot block them." (line 236). ALREADY WRITTEN (`research/acl-fence.md`, Not verified, and `research/two-workshop.md`, Verdict on DNS).
- An investigation that lives only in Hindsight is not reachable from a later record. Quote: "If you want them in the tree, the Spec Kit research deposit is the place the conventions point to, and a `.kb` document would hold the decisions once they are made." (line 291). The repository now holds `research/*.md` records and ADR 0001 cites none of this analysis. NEW, as a workflow rule: a session that produces an option comparison writes it to `research/`, because memory is not the durable record for this repository.
- The person asked about the bridge as the fence placement one turn after being given the fence at LXD level. Quote: "if workshop allowed to configure a per-workshop network bridge, would that help?" (line 212). The answer was already in the record of the previous turn, and the agent gave it again plus new isolation facts. Considered and rejected below.

## What should not become a skill

- The six-option comparison and its ranking. It is a decision input for one question, it was superseded by ADR 0001, and it belongs in a record if anywhere.
- "Ask what constraints rule out an option before ranking." The agent did condition its top recommendation on the container being allowed (line 140), and the person's constraint arrived as new information rather than as a correction of an unstated assumption.
- The OpenShell policy YAML fields and the L7 protocol list. Upstream documents its own format, and the project has since abandoned OpenShell.
- The exact LXD command spellings. Upstream documents them, and the repository records the measured behavior that matters.
