# ses_e35651f4cffe6xJc5a1FCZtryq: LXD ACLs for hermes egress

## What the person asked for

- "in https://github.com/canonical/workshop/issues/927 they discuss an option to use LXD network acls to control workshop egress. evaluate and consider this path for our project to separate hermes from the general network and route hermes to one or more proxies (possibly the openshell proxy as a default)" (USER msg 1, flat line 3)
- "record all investigation findings in hindsight" (USER msg 2, line 102)
- "perform Record the decision now as ADR-0001 ("Hermes egress is mediated by a sandbox proxy and fenced by a network ACL"). Per .kb/project.md§2 a structural choice like this needs a record, and there are none yet." (USER msg 3, line 115, and again at msg 4, line 120)
- "@general create a @handoff for Run a second spike alongside the openshell one: apply a NIC-level ACL (default drop, allow only gateway/DNS/apt) to a workshop running the OpenShell gateway, and verify from inside that (a) denied destinations fail closed, (b) proxied allowlisted endpoints still work, (c) the fence survives workshop refresh and is lost on remove+launch" (USER msg 5, line 126)
- "the ADR had decisions that I did not want. what I want / hermes runs inside workshop / openshell proxy runs outside of hermes workshop (in a different workshop maybe) / LXD ACL enforce that the hermes workshop must route through the openshell proxy and does not have open egress / evaluate, critique" (USER msg 6, lines 143 to 148)
- "I confirm B. @asd-ste100 scrap ADR-0001 and write a new one. create a @handoff for a new spike. update hindsight" (USER msg 7, line 204)
- "commit the adr, make sure it's in main too" (USER msg 8, line 224)

## What was produced, and whether it worked

- An evaluation of issue 927, with a two-layer recommendation (proxy first, ACL fence second) and a security notes section (lines 25 to 100). Not verified by any run. The agent states the open questions at line 98.
- One Hindsight investigation document and one initiative page, `kp-88d78d6b758e48d8a3822df07700cfe2` (tool log lines 292 and 293).
- A first ADR 0001, `adr/0001-hermes-egress-is-mediated-by-a-sandbox-proxy-and-fenced-by-a-network-acl.md`, plus its index row in `adr/README.md` (tool log lines 295 and 296). Uncommitted. The person rejected its content (msg 6).
- A handoff at `/tmp/opencode/handoff-monitor-agent-acl-fence-spike.md` (tool log line 297). Deleted at tool log line 300.
- The rewrite after the correction: the old record deleted, a new `adr/0001-hermes-runs-in-a-fenced-workshop-and-a-second-workshop-mediates-its-workload-egress.md` written, the index row updated, a second handoff written, the initiative page recaptured, and a correction document ingested (tool log lines 299 to 304).
- Commit `db175ca`, subject "docs: add the two-workshop decision record" (line 238, tool log line 310). The record was restored from `main` first, and the agent verified it: "both branches now carry the identical blob (`4ca8210`)" (line 240, tool log line 311). The working tree was left clean.
- The commit carries a file whose content the agent did not write. It states that plainly: "I copy the record from main, where the spike sessions corrected it with the measured results." (tool log line 310)

## Corrections the person made

- The agent reported the first record as finished: "Both `adr/0001-hermes-egress-is-mediated-by-a-sandbox-proxy-and-fenced-by-a-network-acl.md` and the index row are uncommitted and ready for a commit when you want one." (line 132). The person replied "the ADR had decisions that I did not want. what I want" and then gave the three-line architecture (lines 143 to 146).
- The person repeated the whole "perform Record the decision now as ADR-0001" instruction twice, at line 115 and again at line 120. The agent answered only after the second, with "The plan is approved, so I'll record the initiative in Hindsight first" (line 122).
- No other correction. The later message "I confirm B" confirms the agent's reading rather than correcting it.

## Conventions, commands and values stated and written down nowhere

- The person's target architecture, in their own three lines: "hermes runs inside workshop", "openshell proxy runs outside of hermes workshop (in a different workshop maybe)", "LXD ACL enforce that the hermes workshop must route through the openshell proxy and does not have open egress" (lines 144 to 146). The word `maybe` is the person's, and the agent treated it as open question 7 (line 192).
- The number disposal instruction: "scrap ADR-0001 and write a new one" (line 204). The agent read this as rewriting in place at the same number: "never committed, so the clean path is to rewrite it in place with the same number rather than deprecate-and-replace" (line 198).
- The record must reach `main`: "commit the adr, make sure it's in main too" (line 224). No repository file states that a change made on a spike branch has to be checked against `main`.
- The skill named for the record: "@asd-ste100" (line 204), and the agent's reading of it: "active voice, one fact per sentence, no semicolons or em dashes, noun clusters at three words or fewer" (line 216). ALREADY WRITTEN in `adr/README.md` Conventions.
- The delegation request and its override: the person wrote "@general create a @handoff", and the agent wrote it itself, "the subagent would not have this conversation's context, and the handoff has to come from the session that holds it" (line 128).
- The host facts the agent packed into the handoff: "workshop 0.9.9 via snap, the per-user LXD project gotcha (`lxc project list` first), strict definition validation, the 503 workaround (raw.githubusercontent + context7 `/canonical/lxd`)" (line 137). Only the strict validation reached a repository file, as `adr/0001` Context.

## Failures, their cause, and the fix

- Nine documentation fetches failed (tool log lines 258 to 284).
  - Five returned `503` from the canonical redirect host: three LXD ACL page variants, `/lxd/docs/latest/network-acls/`, `/lxd/docs/latest/howto/network-acls/` and `/lxd/docs/latest/howto/network_acls/`, and two `ubuntu.com/workshop/docs/` release-note pages. The error text is "StatusCode: non 2xx status code (503 GET https://canonical.com/lxd/docs/latest/network-acls/)". Cause: the documentation sites redirect and refuse the fetch.
  - Four returned `404` for guessed paths under `raw.githubusercontent.com` and `api.github.com` for both `canonical/workshop` and `canonical/lxd`. Cause: the guessed file names were wrong.
  - What ended it: the GitHub contents API listed the real directory (`docs/release-notes`, `docs/reference`, tool log lines 277 to 279), and context7 answered from `/canonical/lxd` (tool log lines 288 to 291). The agent wrote the recovery into the handoff at line 137.
- The local record was empty and the branch index pointed at a file it did not hold. Cause, in the agent's words: "on this branch (`spike/acl-fence`) the index row referenced the record, but the file was missing, and the working copy had been emptied to zero bytes at some point" (line 236). What ended it: `git restore --source=main -- adr/0001-...` then a commit and a blob comparison (tool log lines 309 to 311).
- The commit target moved under the session. Cause: "other sessions ran both spikes, and `main` already carries a committed ADR-0001 row plus spike-result commits" (line 226). The agent also names the content change: "the other sessions corrected my pre-spike text with real findings (one bridge per workshop ... no rule names a source address ... measured residuals like the unfenced DNS and the lifecycle window)" (line 228).

## Candidate lessons

- "The supervisor is co-located with the sandbox by design ... So OpenShell's proxy is not a network service that a neighboring workshop can dial into. Mediation follows the sandbox" (line 157), and "There is no documented mode where the supervisor accepts connections from arbitrary external clients and applies OPA policy to them." (line 163). PROJECT-SPECIFIC FACT. No repository file records it. `research/two-workshop.md` records only that a remote gateway client works.
- "The supervisor dials out to the gateway, so B needs outbound but accepts inbound only on the gateway endpoint." (line 170). ALREADY WRITTEN in part (`adr/0001` names the gateway path with mutual TLS), and the dial direction is stated in no file.
- "Traffic between instances on the same bridge is never filtered by ACLs." (line 187). ALREADY WRITTEN (`research/acl-fence.md` Findings, `research/two-workshop.md` Not verified, which records that the upstream statement did not hold on this host).
- "the direct fetches 503'd, so I'll go via context7 for LXD docs and check Workshop release notes directly" (line 17) and "the 503 workaround (raw.githubusercontent + context7 `/canonical/lxd`)" (line 137). NEW. No repository or `AGENTS.md` file tells an agent how to reach the LXD or Workshop documentation when the canonical host refuses.
- "Main's committed ADR-0001 is the spike-measured version" (line 228) and the empty local copy at line 236. NEW. Sessions share one checkout and several worktrees, and no file tells an agent to compare its record against `main` before it commits. The repository now holds records that were corrected by a different session than the one that drafted them.
- "never committed, so the clean path is to rewrite it in place with the same number rather than deprecate-and-replace" (line 198). NEW. `adr/README.md` states numbering, statuses and deprecation, and it does not say what an uncommitted draft that is rejected becomes.
- "I copy the record from main, where the spike sessions corrected it with the measured results." (tool log line 310). NEW, and it is the same lesson as the `main` line above: a branch that carries a record has to check the record on `main` first.
- "A new record is written as Accepted, and merging its pull request is the acceptance." Quote from `adr/README.md` Conventions. ALREADY WRITTEN. The first record followed it, and the person's rejection still arrived before the merge.
- "per `.kb/project.md`§2 a structural choice like this needs a record" (line 91, the person's own words at line 115). ALREADY WRITTEN (`.kb/project.md`§2).
- "The writing style rules are stricter than my draft will assume, so I wrote the record to them" (line 124). ALREADY WRITTEN (`.kb/writing-style.md`, `adr/README.md` Conventions).
- "The ADR task left one convention step undone (the index row in `adr/README.md`)" (line 128). ALREADY WRITTEN (`adr/README.md` Conventions).

## What should not become a skill

- The two-layer architecture the agent proposed. The person rejected it, and ADR 0001 later abandoned OpenShell. Encoding it now would contradict the record on `main`.
- The Reading A and Reading B split of the person's three-line model. It is a critique of one proposal, it rests on an OpenShell the project dropped, and the topology that survived is in ADR 0001.
- The handoff-in-`/tmp/opencode` practice. The next session in this batch read the handoff from that path, so it worked once, and it sits outside the repository. Whether a handoff belongs in the tree is a repository decision, not a skill.
- "Reuse the ADR number after a rejection." The agent's own reading covers it, and `adr/README.md` already governs numbering.
