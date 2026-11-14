# ses_e33bdc7ebffetbgHtAVOxK8vFq: Research OpenShell gateway mechanics (ticket #3)

## What the person asked for

The session holds one prompt. It was written by the spawning session
(`ses_e33d0c7c5ffejcYl5L4FlzKPPv`), not by the human, and no human turn appears
in this transcript (flat:3-23).

- "TICKET: issue #3 "Research OpenShell gateway, policy, and credential
  mechanics", label wayfinder:research, child of map issue #1" (flat:6).
- "LOCAL EVIDENCE (read-only): the branches spike/openshell-in-workshop,
  spike/two-workshop, and spike/two-bridge-gateway hold the scripts that
  installed and drove the gateway. Read them with `git show <branch>:<path>` ...
  Do NOT check out over your working tree carelessly and do NOT run any script."
  (flat:12)
- "Cross-check upstream claims against the local spike evidence and mark
  disagreements explicitly." (flat:14)
- "mark what the local spikes measured versus what upstream docs state" (flat:16)
- "Then: gh issue close 3 ... Do NOT edit issue #1 (the map owner appends the
  decision pointer)." (flat:19)
- "RULES: Read-only research. Never run any script from a spike branch. Never
  launch, refresh, or remove anything. Never print or commit secret or
  credential contents. Never touch any issue other than #3. Never edit the map."
  (flat:21)
- "FINAL REPLY to me: the ticket number, the branch name, the verdict in at most
  five sentences, and any fact you found that contradicts the repo's records in
  adr/ or research/." (flat:23)

## What was produced, and whether it worked

- Branch `research/openshell-gateway-mechanics`, pushed, holding
  `research/openshell-gateway-mechanics.md`, committed as `docs: research
  openshell gateway mechanics` (flat:113, flat:63). The file is not on `main`
  today.
- The branch was made in a throwaway worktree,
  `/tmp/opencode/monitor-agent-openshell-mechanics`, created from `origin/main`
  (flat:111). The worktree was removed after the push (flat:114).
- Resolution comment on #3 and the close (flat:115-116). Two trail entries
  (flat:117-118).
- The verdict, as the agent reported it: a schema version 2 TOML file, one TLS
  listener defaulting to `127.0.0.1:17670`, `openshell-gateway generate-certs`,
  YAML `network_policies` rules on endpoints and real binary paths, `audit` as
  the default enforcement that applies only to request rules so
  `enforcement: enforce` must be explicit, provider credentials held at the
  gateway and handed to sandboxes as `openshell:resolve:env:` placeholders under
  three fail-closed checks, and two documented interfaces for a second plane
  proxy: `https_proxy` CONNECT chaining under the Docker driver, and
  `[[openshell.supervisor.middleware]]` gRPC (flat:65).
- The one refinement it raised is stated against a committed record, not against
  the spikes: `research/two-workshop.md` "states the Docker driver's supervisor
  endpoint defaults to a fixed `https://127.0.0.1:17670`, while upstream
  documents it as automatic selection" (flat:67). The record still carries that
  sentence today.
- Not verified: no gateway was started in this session. Every OpenShell claim is
  a documentation reading.

## Corrections the person made

(none found). The prompt's own rules shaped the run, and the agent obeyed them:
it read the spike scripts with `git show` and ran none of them (flat:87-93), and
it touched no issue other than #3.

## Conventions, commands and values stated and written down nowhere

- The worktree shape for a research branch:
  `git worktree add -b research/<name> /tmp/opencode/<something> origin/main`
  (flat:111), then `git worktree remove <path>` after the push (flat:114).
- The reason for it: "The working tree is on another session's branch. I'll
  branch mine off `origin/main` in a separate worktree." (flat:55)
- The API form the agent used to read issues on this host:
  `gh api repos/hammerstefan/monitor-agent/issues/3 --jq '{title: .title, body:
  .body, labels: [.labels[].name], state: .state}'` (flat:71).
- The evidence marker the findings file uses to separate measurement from
  documentation. The prompt asked for it, and the reply names both kinds
  side by side (flat:65-67).

## Failures, their cause, and the fix

- `gh issue view 3` and `gh issue view 1` returned the Projects-classic GraphQL
  deprecation error. Cause: the default template of `gh issue view` on this
  host. Fix: `gh api repos/<owner>/<repo>/issues/<n> --jq ...` (flat:25,
  flat:71-72).
- The first branch attempt would have failed on a shared clone. Cause: "The
  working tree is on another session's branch." (flat:55). Fix: a separate
  worktree from `origin/main`, which also keeps the other session's working tree
  untouched.
- No `!! FAILED` line appears in this session's tool log.

## Candidate lessons

1. NEW. A research branch is created in a throwaway worktree from `origin/main`
   when the shared clone sits on another session's branch, and the worktree is
   removed after the push. Quote: "The working tree is on another session's
   branch. I'll branch mine off `origin/main` in a separate worktree."
   (flat:55). The sibling session `ses_e33bdc7daffebNv7yFSoh2BFA8` learned the
   same lesson by inheriting a commit (its flat:88).
2. NEW. A finding that disagrees with a committed record is written as a
   refinement of the record's wording, with the measurement kept. Quote:
   "The spike's observed behavior matches the host-mode loopback case, so the
   record's wording is what changes, not the measurement." (flat:67).
3. NEW. `gh issue view <n>` without `--json` fails on this host with a
   Projects-classic GraphQL deprecation, so the issue is read with `gh api`.
   Quote: "`gh issue view` hits a GraphQL deprecation error, so I'll read the
   issues through the REST API instead." (flat:25).
4. ALREADY WRITTEN. A spike branch's scripts are read and never run, and research
   about a spike stays read-only. `.kb/spikes.md` §5.
5. PROJECT-SPECIFIC FACT. The OpenShell mechanics this session established. They
   are a record of a retired dependency, and `adr/0001` now states that "Its
   sandbox, supervisor, gateway, policy file, and mutual TLS bundle are gone."
   Two of the facts still teach something about proxies in general: policy that
   names the calling binary needs the binary hash pinned, and an audit mode that
   is not the default must be asked for explicitly.
6. PROJECT-SPECIFIC FACT. `enforcement: enforce` had to be explicit because
   `audit` was the default and applied only to request rules (flat:65). Read
   against iron-proxy, which blocks by default and audits under `warn`, this is
   the inversion `adr/0001` now records.

## What should not become a skill

- The gateway configuration keys, the certificate command, the placeholder
  prefix and the port numbers. They are values of one upstream release of a
  dependency the project dropped.
- "Let me read the rest of the saved output" (flat:41). Reading a long fetched
  page from the tool-output file is a habit of one harness, not a rule.
- The `--jq` field list of the issue read (flat:71). It is one command.
- "Never touch any issue other than #3. Never edit the map" (flat:21). It is the
  rule of one dispatch, and `.kb/issue-tracker.md` already gives the map owner
  the job of appending the pointer.
