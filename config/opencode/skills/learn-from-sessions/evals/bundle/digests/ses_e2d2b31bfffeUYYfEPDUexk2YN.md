# ses_e2d2b31bfffeUYYfEPDUexk2YN: Enforce the Hermes proxy allowlist

Worktree `wayfinder-acceptance-task-proxy-allowlist`, since removed. 676
messages, two compactions, one model switch. A number is a message position.

## What the person asked for

- msg 2, the task: "`/wayfinder #1 #25`", with "hermes has not fetched a public
  web page through the plane proxy under a policy that admits one host and
  refuses the rest", and "no test run may print them" about operator values.
- msg 168: "continue"
- msg 211: "re "The LLM address in the operator config". I want to use github
  copilot as the primary provider. Can we specify their api domain?"
- msg 251: "continue"
- msg 421: "create opencode todo for "what needs you""
- msg 484: "continue"
- msg 508: "push this br and open pr"
- msg 526: "merge the pr"
- msg 535: "details on todo 2"
- msg 565: "1. disable passive check, upgrades need to be handled through
  workshop refresh / 2. agree"
- msg 602: "todo 3 - describe. that issue is done"
- msg 613: "nevermind. 38 should be it's own dedicated work branch. / todo 4 -
  descrive"
- msg 625: "todo 4 done / action todo 5"
- msg 655: "any remaining work or can this worktree be removed?"
- msg 661: "merged, remove the workshops, I'll handle rest"
- msg 671: "remove the bridges"

Answers the transcript records in the `question` tool result: msg 46 "write
from keyring. we also need to consider how to keep keyring and fence.env in
sync" plus three approvals, msg 307 "Route it through the proxy (Recommended)",
msg 401 "Delete it (Recommended)", msg 591 "Commit on the merged branch".

## What was produced, and whether it worked

Four commits on `wayfinder/acceptance-task-proxy-allowlist`, all merged:

- `f014c40` "fix: set the proxy variables in both letter cases": adds
  `http_proxy` and `https_proxy` to `hermes.env` and to
  `terminal.env_passthrough`, and writes ADR 0007.
- `76ed3bb` "fix: let the proxy allowlist enforce": removes `warn: true` from
  `plane/proxy-policy.yaml`.
- `fa382de` "fix: route the model call through the plane proxy": the policy
  names `api.githubcopilot.com`, the helper writes `NO_PROXY` with the loopback
  addresses only, and the fence drops its LLM rule. Removes the operator config
  from `monitor_agent/fence/`, `fence/fence.yaml` and the tests. Adds ADR 0008,
  amends ADR 0001 and ADR 0005, withdraws FR-008, FR-017 and FR-018 and adds
  FR-027.
- `a4771b7` "fix(agent): disable the passive hermes update check": adds
  `updates.check: false` and the "Upgrades" section of `.kb/agent-workshop.md`.

PR #40 merged as `956dacf` at 16:23 UTC. PR #43 merged as `f9f305b` at 17:44
UTC, opened from the already merged branch on the answer at msg 591. Both
workshops were removed, and the bridges and their ACLs were deleted (msgs 664
to 673).

Tickets: #25 claimed and closed with a resolution comment. #39 closed with a
resolution comment (msg 406). #38 filed and left open (msg 157). #42 filed,
linked as a sub-issue of #1, and closed (msgs 582 to 586). The map `#1` gained
a "Decisions so far" line for #25 and one for #39.

Verified on the host: `just fence` applied and probed, the allowed probe
connected and the denied probe timed out (msg 41). The acceptance run answered
`HTTP status: 200` and `Page title: Example Domain` in warn mode (msg 159),
after enforcement, with the fence holding no LLM rule (msg 293), and on the
restored baseline (msg 299). `http://example.org/` through the proxy answered
403, and `http://example.com/` without the proxy variables timed out after 25 s
(msg 173). The final agent bridge ACL holds two egress rules, `10.255.0.10`
port `1080` and `10.254.0.1` port `53`, and no ingress rule. The final policy
holds `example.com` and `api.githubcopilot.com` (msg 417). Direct connections
from the agent workshop to three GitHub hosts timed out (msg 398). `just test`
passed after each change.

Not verified: a tool other than curl that reads the proxy from its own
configuration, a denied host on a port other than 80 and 443, the model call
after the final refresh, and the origin of four journal requests that name the
plane workshop source address (msg 176).

## Corrections the person made

- The agent asked to write the operator config from the keyring, and the person
  widened the step: "write from keyring. we also need to consider how to keep
  keyring and fence.env in sync" (msg 46). The agent answered the drift by
  removing the file and its reader, and Option A at msg 307 closed #39 with no
  address to decide.
- The agent recommended stopping the update check and wrote "The workshop is
  rebuilt from its definition, so an in-place update is not the normal path"
  (msg 542). The person turned it into a rule of the system: "1. disable
  passive check, upgrades need to be handled through workshop refresh" (msg
  565). That sentence became the "Upgrades" section of `.kb/agent-workshop.md`.
- The person withdrew a claim of their own after the agent checked it. The
  person wrote "todo 3 - describe. that issue is done" (msg 602), the agent
  answered "You said "that issue is done". The tracker disagrees." with the
  three refresh failures, and the person answered "nevermind. 38 should be it's
  own dedicated work branch." (msg 613).

## Conventions, commands and values stated and written down nowhere

- The branch freeze: "Commit on `wayfinder/acceptance-task-proxy-allowlist`.
  Do not push, merge, rebase, or touch other branches" (msg 2). The person
  lifted the push and merge parts at msg 508 and msg 526.
- The ask list, from msg 2: "Ask before the step that removes `warn` from
  `plane/proxy-policy.yaml`, before the step that stores or connects an
  operator value on the host, and before the step that stops or removes a
  workshop." Deleting an operator file on the host was added by the agent and
  accepted at msg 401.
- The map line rule: "Use the ticket title, not a bare number, in the map line"
  (msg 2).
- The allowlist values: `example.com` alone in warn mode, then `example.com`
  and `api.githubcopilot.com` with `warn` removed.
- The fence values: agent `agent-4863fffc` at `10.254.0.20` on `mon-agent-br`,
  plane `plane-2a96f0cb` at `10.255.0.10` on `mon-plane-br`, ACLs
  `mon-agent-br-acl` and `mon-plane-br-acl`, LXD project
  `workshop.1077165261`, snapshot project `workshop-snapshots.1077165261`.
- The operator values: keyring `service=monitor-agent account=llm-endpoint`
  holds `MONITOR_LLM_BASE_URL=https://api.githubcopilot.com` and
  `MONITOR_LLM_MODEL=gpt-6.1-terra`, and `account=llm-api-key` holds the key.
  The operator config that no longer exists held
  `MONITOR_LLM_ADDRESS=140.82.112.0/20` and `MONITOR_LLM_PORT=443` in
  `~/.config/monitor-agent/fence.env`, mode 600.
- `NO_PROXY=localhost,127.0.0.1,::1`.
- The acceptance command, run from the worktree: `workshop -p agent exec
  --timeout 20m agent -- hermes -z "Use the terminal tool to fetch the public
  web page http://example.com/ with curl. Report the HTTP status code and the
  page title."` It answered in 34 s (msg 159).
- The sub-issue call that works here with `gh` 2.45.0: `gh api --method POST
  repos/hammerstefan/monitor-agent/issues/1/sub_issues -F
  sub_issue_id="$(gh api repos/hammerstefan/monitor-agent/issues/42 --jq .id)"`
  (msg 583).
- The install of a changed SDK file inside the workshop: `install --mode=755
  --owner=workshop --group=workshop
  /project/.workshop/hermes/files/monitor-secrets
  /home/workshop/.local/bin/monitor-secrets` (msg 394).
- The lock files a fresh worktree needs, written before the fence can resolve
  the running instances: `printf '4863fffc' > agent/.workshop.lock` and
  `printf '2a96f0cb' > plane/.workshop.lock` (msg 38).
- The workflow rule for a follow-up commit on a merged branch, from the answer
  at msg 591: "Commit on the merged branch".

## Failures, their cause, and the fix

1. `just fence-launch` exited 2 (msg 49). `launch` answered `error: cannot
   launch "plane": workshop exists`, and the fence reported `fault: the
   instance agent-c72ff403 in project workshop.1077165261 sits on a fence
   bridge: the fence carries two workshops only`. Cause: an agent instance from
   an earlier session held `mon-agent-br` at `10.254.0.20`. The fix removed it
   and the second leftover `agent-a21f5c6d` with `workshop remove`, run from a
   prepared project directory (msgs 54 and 55).
2. The model call failed with a timeout after 120 seconds. Cause: the fence
   allowed one address, `140.82.112.21`, and the endpoint also answered from
   `140.82.112.22` and `140.82.113.22`. The fix was the range
   `140.82.112.0/20`, and later the proxy path.
3. The acceptance run reached the fence instead of the proxy, and the proxy
   journal held no record for the request (msg 92). Cause: curl 8.5.0 reads
   `http_proxy` for a plain HTTP request and ignores `HTTP_PROXY`, and the
   template set the uppercase names only. The fix is `f014c40` with ADR 0007.
4. `just fence-refresh` exited 2 after 12m19s (msg 124), with `error: cannot
   refresh "agent"; aborted` and `fault: the instance stash-agent-4863fffc is
   not running, so the fence cannot probe`. `workshop -p agent tasks 741`
   named `Run hook "setup-base" for "hermes" SDK`. Three causes: the fixed
   address collided with the stashed instance, `setup-base` had no path to
   `github.com` on the agent bridge, and the stopped stash matched the workshop
   keys. `just fence` then exited 2 on the same stash. The fix deleted the
   stash with `lxc --project workshop-snapshots.1077165261 delete` and ran
   `workshop -p agent refresh agent --verbose` from the shared bridge, which
   succeeded in 2m43s (msgs 126 to 147).
5. `workshop -p agent refresh agent --abort` answered `error: cannot abort: no
   refresh in progress` (msg 133). Cause: the earlier refresh had ended.
6. The LLM API key was printed in a tool result (msg 16). Cause:
   `secret-tool search --all service monitor-agent account llm-api-key` prints
   the value, and the pipe that followed redacted a second call only. The agent
   noted it at msg 17 and wrote it to no file.
7. The key was printed a second time (msg 92). Cause: the redaction
   `s/(MONITOR_LLM_API_KEY="?)[^"]*/\1<set>/g` stopped at the quote and left the
   value. The agent used `s/=.{12,}/=<redacted>/` afterwards.
8. `lxc push` copied nothing, twice (msgs 245 and 391), and `lxc` printed its
   command list. Cause: `lxc` has no `push` verb, and the verb is `lxc file
   push`. The fix installed from the mount at
   `/project/.workshop/hermes/files/`, the way the hook does.
9. `lxc -p`, `lxc list --all` and `lxc list -a` failed with `unknown shorthand
   flag: 'p'` and `unknown flag: --all` (msgs 18, 129 and 130). The working
   forms are `lxc --project` and `lxc list --all-projects`.
10. The httpx measurement was invalid (msg 258). Both cases returned
    `ProxyError 403 Forbidden` where the first should have gone direct. Cause:
    the test script overwrote `NO_PROXY` in both cases, which the agent called
    "my own test bug" (msg 265). The corrected run answered 404 and 403.
11. `gh issue create --parent 1` printed the `gh` help (msg 156). Cause: `gh`
    2.45.0 has no `--parent`. The fix was `Part of #1` in the body, and for #42
    the REST sub-issue call.
12. An edit to `.kb/fence.md` failed with `Could not find oldString` (msg 368).
    Cause: the agent quoted text that an earlier edit had changed. The agent
    re-read the file and split the edit.
13. An earlier edit removed the docstring of `read_project_id` instead of the
    loader function, and the agent restored it (msgs 307 and 309).
14. The map gained a near-duplicate line under "Not yet specified" (msg 409).
    Cause: the agent appended a line that an existing line already covered. The
    fix merged them and kept `raw.githubusercontent.com` in the existing line.
15. `hindsight_search_pages` answered `Unknown tool` at msg 232 and `trail_add`
    did at msg 412. Both were called again later and succeeded, apart from the
    trail, which was recorded through the testimony command at msg 522.
16. The assistant emitted a malformed tool call as prose at msg 165, starting
    `]<]minimax[>[<invoke name="shell">]`. The shell command never ran, and a
    compaction followed.

## Candidate lessons

- NEW. A fresh worktree has no `.workshop.lock`, so the fence resolves no
  instance. Write the running project's id into `agent/.workshop.lock` and
  `plane/.workshop.lock` first. Evidence: msg 38, and `.gitignore` holds that
  file so it never arrives with the checkout.
- NEW. `gh` 2.45.0 links a sub-issue through `gh api --method POST
  repos/<o>/<repo>/issues/<parent>/sub_issues -F sub_issue_id=<db id>`, so
  `.kb/issue-tracker.md` needs no `Part of #` fallback here. Evidence: msgs 583
  and 584.
- NEW. The running workshop mounts the worktree's project directory, so the
  committed SDK files are readable at `/project/.workshop/hermes/files/`.
  Install a changed file the way `setup-base` does. Evidence: msgs 392 and 394.
- NEW. `lxc` takes `--project` and `lxc list` takes `--all-projects`. It has no
  `-p`, no `--all`, no `-a` and no `push` verb. Evidence: msgs 18, 129, 130,
  245 and 391.
- NEW. `secret-tool search --all` prints the stored secret, so a step that must
  not print an operator value reads it with `secret-tool lookup`. Evidence:
  msg 16 and the note at msg 17.
- NEW. A redaction of `NAME=value` misses `NAME="value"`. Use a pattern that
  consumes the quoted form. Evidence: msg 92.
- NEW. The acceptance command, its `--timeout 20m`, and the 34 s answer. It is
  the cheapest proof that the whole path works. Evidence: msg 159.
- NEW. The iron-proxy `domains` list matches a glob, so one entry can admit a
  host family. Source: `hostmatch.MatchGlob` in `internal/hostmatch`, measured
  at msg 231. ADR 0008 records the list without the glob.
- NEW. Before appending a line to the map's "Not yet specified", read the lines
  already there. Evidence: msg 409.
- NEW. A follow-up commit on a merged branch goes onto that branch and gets its
  own pull request. Evidence: the answer at msg 591, which produced PR #43.
- ALREADY WRITTEN. The two letter cases of the proxy variables, in
  `adr/0007-the-agent-workshop-sets-the-proxy-variables-in-both-letter-cases.md`.
- ALREADY WRITTEN. The model call through the proxy, `NO_PROXY` with the
  loopback addresses only, and the two fence rules, in
  `adr/0008-the-model-call-reaches-the-llm-endpoint-through-the-plane-proxy.md`.
  That record also states that LXD rejects a host name in an ACL rule, that the
  selectors need OVN, that one address drops about half of the model calls, and
  that `140.82.112.0/20` holds 4096 addresses.
- ALREADY WRITTEN. The refresh failures on the stash, the address and the
  download path, in `.kb/fence.md` "The release" and ADR 0009. The rule that a
  stash is never probed is in `.kb/fence.md` "The instance of a workshop".
- ALREADY WRITTEN. The upgrade path and the disabled check, in
  `.kb/agent-workshop.md` "Upgrades". The proxy journal fields and the two
  records per CONNECT are in `research/iron-proxy-plane.md`.
- PROJECT-SPECIFIC FACT. The allowlist values, the fence rules, and the keyring
  item names. ADR 0008, `.kb/fence.md` and `.kb/agent-workshop.md`.
- PROJECT-SPECIFIC FACT. `check_for_updates` returns `{"reason": "disabled"}`
  at `hermes_cli/source_check.py:570`. A record, not a skill.

## What should not become a skill

- The `todowrite` search. The agent read the OpenCode server API and a 5.8 GB
  SQLite database over about 60 messages before the tool appeared at msg 485.
  That is a harness fault of the moment, not a rule about the repository.
- The `trail_add` and `hindsight_search_pages` answers. Tool catalogs change
  within a session, and no repository rule follows.
- The near-duplicate map line and the withdrawn docstring. Both are the agent's
  own slips, fixed in the same turn.
- The measured DNS pool of the endpoint. The addresses change, and ADR 0008
  keeps the reason instead of the values.
