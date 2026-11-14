# ses_e2a211dc0ffenjeQD6D6v7DvqQ: Host LXD access options for fence command

Session ran in `/home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/spike-development-workshop` on 13 November 2026. The person's messages are numbered U1 to U15 below, in order, with `@to-tickets` as U9b. Three research subagents were spawned, and their transcripts are digested separately.

## What the person asked for

- U1: "from parallel session, topics:" then "let's dive deeper and help me understand options and solutions". The two topics named were the fence command's need for host `lxc` and host LXD state, and `just policy-reload` needing the host `workshop` command and the plane instance.
- U2: "context: the alternative is running my development agent on the host. with that, giving workshop temporary and restricted lxd access is an improvement"
- U3: "if the proposal works, what can not be validated from inside the dev workshop? what testing requires humans in the loop? keep in mind, we want to avoid humans for tedious testing, because then the testing just won't get run"
- U4: "if we are willing to losen security bounds, what is a simpler way?"
- U5: "would it be possible to take a two phase approach 1) only filesystem/process isolation. map in workshop and lxd control (fast win, does not need humans in test loop) 2) then build a lxd cert and validation proxy approach (longer term correct approach, still does not need humans in validation loop)"
- U6: "is there no way to map in workshopctl to the workshop?"
- U7: "let's make it a priority for the dev workshop to be able to control the plane/agent workshops, otherwise agentic development will not be possible. give a phased approach toward that"
- U8: "phase 1: the service should be run when the dev workshop is launched, and stopped when the workshop is stopped. maybe through a just recipe?"
- U9: "do we have enough of a plan to start defining work tickets?"
- U9b: "@to-tickets"
- U10: "are there other reasearch / grilling / exploration tickets needed for topics in this session?"
- U11: "@wayfinder"
- U12: "are there any prs that need to be raised? I want to collapse this all back into main, and handle the rest of the map from there"
- U13: "we should pr the readme change to main"
- U14: the `hwt-wrapup` skill invocation.
- U15: "what is this session id?"

## What was produced, and whether it worked

- **Answer to U1 to U8.** Seven options were compared in prose, first as fence access alone, then as the phased plan: a control service that runs a fixed set of verbs on the host. Nothing was built in this session. The `plan` and `--report` fence verbs recommended in the reply to U1 were never written.
- **Map #44**, "Map: a development workshop that drives the product", with twelve child tickets #45 to #56 and a standalone doc defect #57. Created with `gh issue create` from files under `/tmp/opencode/chart/`.
- **Three research subagents** for #46 (daemon channel), #47 (LXD project scope) and #49 (`ctlcmd` channel). Each wrote its findings to `/tmp/opencode/chart/research-*.md`. The parent created one branch per ticket and pushed it with no pull request: `research/development-workshop-channel`, `research/development-workshop-lxd-scope`, `research/development-workshop-ctlcmd`. The three tickets were closed with their answers.
- **Pull requests.** #58 `docs: record the development workshop research` (three records) and #59 `docs: record the development workshop` (`research/development-workshop.md`). Both are merged on `main` (`a6b86fc` holds both).
- **`spike/development-workshop`** was pushed and deliberately not merged, because `.kb/spikes.md` §2 forbids it.
- **The main agent's own host reads.** `lxc network acl show` on both fence ACLs, `lxc project list`, `lxc list --all-projects`, and reads of `monitor_agent/fence/apply.py`, `lxd.py`, `cli.py` and the `justfile`. These were reads.
- **Not verified in this session.** No fence verb was built or run. No control service exists. The claim that a restricted certificate reaches no fence object was measured by the #47 subagent, not here.

## Corrections the person made

- The agent had weighed a workshop with a narrow grant against a workshop with none. U2 replaced the baseline: "context: the alternative is running my development agent on the host. with that, giving workshop temporary and restricted lxd access is an improvement". The reply opened "You are right. The comparison is not a workshop with fence access against a workshop without it. It is this."
- The reply to U1 kept both fence verbs on the host and allowed a broker only as a read-only option: "Leave the broker out until someone needs to operate from the workshop. If it is built, limit it to the read-only verbs." U7 overrode that ranking: "let's make it a priority for the dev workshop to be able to control the plane/agent workshops, otherwise agentic development will not be possible. give a phased approach toward that".
- The agent's reply to U7 left the host service to be started by a person. U8 tied it to the workshop: "phase 1: the service should be run when the dev workshop is launched, and stopped when the workshop is stopped. maybe through a just recipe?".
- U13 corrected the agent's reading of the request: "we should pr the readme change to main". The agent had offered the research record instead and had said that putting the README on `main` "is a deliberate exception to §2".

## Conventions, commands and values stated and written down nowhere

All of the following are the agent's proposals in this session, not the person's words, and none is in the repository today:

- The recipe set: "`just dev up` | Check lingering, run `workshop --project . launch dev`, wait for ready, then `systemctl --user start monitor-agent-dev-control`", with `just dev down`, `just dev rm` and `just dev refresh`.
- The unit settings: "`Restart=on-failure`", "Not enabled at boot", and the statement that "`just dev down` is the revocation."
- The request directory inside the worktree: "Use a git-ignored directory inside the worktree, such as `.dev-control/`."
- The backstop for phase 2: "A timer every 30 seconds checks `workshop info dev`."
- The verb set: `fence-apply`, `fence-launch`, `fence-refresh`, `fence-restore`, `fence-remove`, `policy-reload`.
- The research workflow: "The research subagents write their findings to `/tmp/opencode/chart/` instead of switching branches in this worktree, because four parallel branch switches would collide."
- The agent's own statement of the charting limit: "`gh` 2.45 has no native sub-issues and no native dependency edges."
- The person's working rules, quoted: "we want to avoid humans for tedious testing, because then the testing just won't get run" (U3), and "I want to collapse this all back into main, and handle the rest of the map from there" (U12).

## Failures, their cause, and the fix

- `!! FAILED webfetch` for `https://raw.githubusercontent.com/canonical/workshop/main/docs/explanation/interfaces/tunnel.rst`, answer `404`. Cause: the agent guessed a documentation path. Fix: it listed the repository tree through the GitHub API, then fetched `docs/explanation/interfaces/tunnel-interface.rst`.
- **A wrong claim, corrected by the agent.** "I wrote that network ACLs are global. They are not." The cause it gave: "My `--project` query returned the default ACLs because that project has networks disabled." The result read as a server-wide rule when the option did not apply to that project.
- **A wrong claim, corrected by the research.** "I wrote that the trusted Workshop socket does not work from a container" was withdrawn in the reply to U7: "That is a correction to what I said earlier about mapping the trusted socket." The mount was never the cause, the uid was.
- **A stale name, corrected by the agent.** "One correction to the record: the live instances are `agent-007bc764` and `plane-4d1696e1`, not the names I used earlier. The workshops were recreated during the session."

## Candidate lessons

- NEW. "keep in mind, we want to avoid humans for tedious testing, because then the testing just won't get run". U3. `research/development-workshop.md` and the `workshop-host-authority` skill state that an acceptance run needs no human. Neither states why, nor that a test that needs a person is a test that does not run.
- NEW. "My `--project` query returned the default ACLs because that project has networks disabled." Reply to U1, in the paragraph headed "A correction to what I said". A query whose option does not apply returned another project's objects, and the result read as a global rule. Check `features.networks` before concluding that an LXD object is server-wide.
- NEW. "The research subagents write their findings to `/tmp/opencode/chart/` instead of switching branches in this worktree, because four parallel branch switches would collide." Reply to U11. Three parallel research sessions finished under this rule, and the parent created each branch after.
- NEW. "One correction to the record: the live instances are `agent-007bc764` and `plane-4d1696e1`, not the names I used earlier. The workshops were recreated during the session." Reply to U11. A workshop instance name changes on recreation, so it is read from `lxc list`, never reused from an earlier turn.
- NEW. "`gh` 2.45 has no native sub-issues and no native dependency edges." Reply to U11. The stronger form, that GitHub supports both through GraphQL while `gh` lacks the flags, is measured in ses_e29a6e8fcffej9WEFqqvOxC3d5 and counted there.
- NEW. `!! FAILED webfetch` with `404` on a guessed `canonical/workshop` doc path. Tool log. List the upstream tree through `https://api.github.com/repos/<owner>/<repo>/git/trees/main?recursive=1` before fetching a documentation path.
- ALREADY WRITTEN. The baseline correction at U2. `workshop-host-authority` line 72: "The baseline is a development agent that runs on the host. A workshop with a narrower and revocable reach is an improvement on that baseline."
- ALREADY WRITTEN. A spike branch does not merge, so its README travels as a findings record. `.kb/spikes.md` §2 and §7, and the agent cited both.
- ALREADY WRITTEN. Naming the shape before a probe. `workshop-host-authority`: "Name the shape before the probe. A probe of the wrong shape answers a different question, and it answers it convincingly."
- ALREADY WRITTEN. The restricted-certificate verdict, the bridge-in-a-project refusal, `LXD_CONF` and the `servercerts/<remote>` name. `research/development-workshop-lxd-scope.md` and `workshop-host-authority`.
- ALREADY WRITTEN. That no `ctlcmd` verb would serve as the control channel. `research/development-workshop-ctlcmd.md` and `workshop-host-authority`.
- PROJECT-SPECIFIC FACT. The control-service lifecycle: "Start after the workshop is ready, so the mount exists before a request can arrive. Stop the service before the workshop, so no request runs against a workshop that is already going away." Reply to U8. This belongs in the decision record for #51, which does not exist yet.
- PROJECT-SPECIFIC FACT. The source-address defect the agent raised in the reply to U1 is still open as #57. I checked `main` today: `.kb/fence.md` line 50 says "No allow rule names a source address", and `monitor_agent/fence/apply.py` line 120 sets `source=config.agent.bridge_address`. `.kb/project.md` already states the rule that the code is authoritative.

## What should not become a skill

- The `plan` and `--report` fence verbs, `just fence-snapshot`, and the host broker with a socket under `$XDG_RUNTIME_DIR`. They were options weighed in one reply and then dropped. The control service replaced them.
- The trusted certificate as a phase 1 shape. It was proposed in the reply to U5 and closed by #47, which found that a project cannot hold the bridge.
- The two-phase plan. `research/development-workshop.md` records the three phases that replaced it, so a skill that repeats the earlier shape would teach a superseded design.
- The person's request at U15 for the session identifier. It is a fact about the harness.
