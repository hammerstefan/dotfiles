# ses_e2fa0b018ffeiQJxQdJlZNMTnU: Implement wayfinder proxy egress fence

Positions are line numbers in `flat/ses_e2fa0b018ffeiQJxQdJlZNMTnU.txt`. The
conversation is lines 1 to 788, and the tool log starts after `@@TOOLS@@` at
line 789. The tool log records each command with no command output, so every
reading of a host result below is the agent's own sentence at the cited line.
The worktree and the branch are gone.

## What the person asked for

The opening turn (2 to 53) is a handoff prompt written by the delegating
session:

- "`/wayfinder wayfinder #20`" (10).
- "Ticket #20 is a `wayfinder:task` ticket, so it delivers a feature, not a
  decision." (14).
- "Claim issue #20: `gh issue edit 20 --add-assignee @me`. This is the first
  write." (33).
- "Ticket #20 is a delivery ticket. Produce the feature, not a plan." (42).
- "Commit on `wayfinder/proxy-egress-fence`. Do not push, merge, rebase, or
  touch other branches." (44).
- "Ask before any step that destroys host state, including `lxc` deletions and
  Workshop removal." (45).
- "Finish with: what you did, what you found, what you did not verify, and what
  you need from the person." (53).

Then, in order: "pause" (107), "summarize next steps to prepare for
compaction" (109), "continue the work" (166), "continue" (388), "@review-minimax
all changes in the pr stack" (592), "the reviewer found and made fixed on this
branch. apply these fixes to the prs as it makes sense" (608), "adress #32
comments" (706), "review all done, merge the full pr stack (including new 36)"
(743).

## What was produced, and whether it worked

Verified against `main` for this digest:

- Four stacked branches and their pull requests: #32 base to `main`, #33 to
  base, #34 to state, #35 to probe. All merged, as `d7fc9b1`, `c930c57`,
  `abf6863` and `fa3eb81`. A fifth, #36, merged as `f4d8f59` on the
  instruction at 743.
- `requirements/002-proxy-egress-fence/requirements.md`, at 26 requirements
  and 6 success criteria at the end, grown from the 23 and 5 of the first draft
  (118). The file on `main` holds `FR-027`, so later sessions changed it again.
- `.kb/fence.md`, a `justfile` with `fence`, `fence-launch`, `fence-refresh`,
  `fence-restore`, `fence-remove`, `policy-reload` and `test`, an `AGENTS.md`
  index entry, amendments to ADR 0001 and ADR 0005, and the `.kb/project.md`
  repository-state line.
- `monitor_agent/fence/{config,lxd,apply,probe,cli}.py`, `tests/`,
  `pyproject.toml`, `uv.lock`, `fence/fence.yaml`.

Claimed by the agent, not verified here: the live run against two scratch
Workshop projects (302, 488 to 506), which reports the fence rules, a
zero-change second apply, an ACL detach that let the denied destination
answer, a re-apply of one change, a denied answer that stopped the agent and
exited 1, a `refresh` and a `remove` then `launch` cycle, and a shared-bridge
placement recovered by one apply. Also claimed: "84 tests pass" (567). No test
count is repeated here as a fact.

Reported as not verified (579 to 584): the plane workshop and the
`policy-reload` recipe, because `plane/.workshop/plane.yaml` and its `reload`
action did not exist. The real iron-proxy, the real LLM endpoint, and hermes
under the fence.

## Corrections the person made

1. The person stopped the agent at the end of a long reconnaissance phase. The
   agent's sentence before the stop: "I have a complete design. Let me write
   the requirements document (base pull request)." (103). The next turn is
   "pause" (107). The transcript gives no reason, and a model switch to
   `glm-5.3-flash` is recorded immediately before (104).
2. The person did not take up the review fallback. The agent said "I don't want
   to silently substitute a different model and present it as the MiniMax
   review, so:" (604), after reporting "The MiniMax reviewer could not run —
   the provider returned an account quota error, not a code problem:" (598),
   and then asked which of four options to take. The tool log records "The
   user dismissed this question" (1217). The person's next turn is "the reviewer
   found and made fixed on this branch. apply these fixes to the prs as it
   makes sense" (608). The person had the review done out of band and left the
   fixes in the working tree.
3. The person reversed the handoff rule at 44. "Do not push, merge, rebase, or
   touch other branches" became "review all done, merge the full pr stack
   (including new 36)" (743), which also named a pull request the agent had not
   created.

The turns at 109, 166, 388, 592 and 706 are instructions, not corrections.

## Conventions, commands and values stated and written down nowhere

Host facts this session measured and no repository file states:

- "`acl create` rejects `description=`" (304). The ACL is created with its name
  only.
- "The default actions are bridge-level keys, not ACL-level (matches the
  research gotcha)." (218). `research/separate-bridges.md` records the
  `security.acls.default.egress.action` setting, not that the key belongs to
  the bridge.
- "`rule add` rejects exact duplicates — so converge must diff before adding."
  (220). The agent recorded the LXD message as "Duplicate of egress rule N".
- "`workshop refresh` cannot infer a name when the project holds several
  workshops. The wrapper knows the two fence workshops, so with no arguments it
  should forward them itself." (332).
- "The actions schema maps name → command string." (338). A definition writes
  `actions: hello: echo hello`.
- The host set for the live run: `lxc 6.10.1`, `workshop 0.9.9`, `just` and
  `uv` installed, PyYAML present. The handoff names only "Host tooling:
  `workshop`, `lxc` 6.10.1, `gh`" (29).

The stacked-branch naming rule, from the agent's own notes: "Stack branches
contain no slashes beyond the base name (git D/F conflict)" (680). The
branches used are `wayfinder/proxy-egress-fence`, then `-state`, `-probe` and
`-wrapper`.

A review comment the agent quotes on pull request #32 at `justfile:13`: "can we
use uv instead of calling a .venv path?" (708). The `justfile` header on `main`
states the resulting rule: "Every recipe runs through `uv run`".

The bridge names, subnets, addresses, DNS domains, denied probe and exit codes
this session chose are now in `fence/fence.yaml` and `.kb/fence.md`, so they are
written down.

## Failures, their cause, and the fix

1. `lxc network acl create <name> description=<text>` was rejected on the real
   host. Cause: LXD takes no `description=` argument. Fix: the ACL is created
   bare, and `create_acl` lost its parameter (304, 1048). A failing host
   command also raised a traceback, because the CLI did not turn a command
   failure into a fault. Fix: clean faults with exit 2 (304).
2. The `workdir` parameter of the `shell` tool did not take effect: "The
   workdir parameter didn't apply — rerunning with an explicit cd:" (308). The
   tool log shows the call carried `"workdir":"/tmp/opencode/fence-verify"`
   (1059). Fix: every later command begins with `cd <dir> &&`.
3. The plane workshop address came out `None` on the live apply: "The plane
   address is `None` because I never wired the endpoint address into the plane
   side." (310). Fix: the endpoint reaches the plane side, with a test for a
   plane address outside its subnet (312).
4. `argparse` rejected a pass-through flag such as `launch --foo` even with
   `nargs=REMAINDER` (290). Fix: a manual parser replaced argparse (1032).
5. A resolver rule was written with a masked destination: "the gateway is the
   address part of the CIDR, not the network address" (260).
6. A first test run failed 6 of 49 tests (254). The four causes the agent
   names: "operator address, ACL rule state, the missing-LLM note, and the test
   assertion" (256).
7. `workshop refresh` found nothing to apply, and the verb has no rebuild flag
   (335). Fix: the agent produced the post-rebuild state by hand, moving the
   agent NIC back to `workshopbr0`, then let the wrapper recover it (340).
8. A scratch definition nested `command:` under an action (338).
9. The rebuild of the layer branches started from the wrong tree: "The tag was
   created before the fix commit — I rebuilt from the pre-fix trees." (356).
   The command at 149 chains `git add -A` and `git tag tmp-final-stack` before
   `git commit`, so the tag names the previous commit. A second attempt left
   only build state, "That commit went wrong — only egg-info landed." (358).
10. A long `&&` chain of git commands left junk on the base branch: "The branch
   flip silently failed and left a junk commit on base." (360). Fix: `git reset
   --hard` to the base, then one step at a time with a check after each.
11. `gh pr edit <n> --body` failed. The agent's cause: "`gh pr edit` hits a
   deprecated-API bug in gh 2.45" (532). Fix: `gh api -X PATCH` with the body
   in a file.
12. The delegated reviewer produced nothing: "Token Plan usage limit reached:
   Upgrade your Token Plan or purchase Credits for more usage. (2056)" with
   status 429 (598). Cause: the provider account quota. Fix: none inside the
   session, and the person had the review done elsewhere (608).
13. A pipe into a heredoc read the script as the input: "The heredoc ate the
   pipe. Writing the check to a file instead:" (638).
14. The live sibling workshop `agent-90d16497` was gone at 380. The agent's
   account: its project directory was torn down and its registration read
   `missing-project`, and no write of this session touched it (577).

## Candidate lessons

1. A `git tag` written in the same `&&` chain before `git commit` names the
   previous commit, so a later rebuild restores the pre-fix tree. Quote: "The
   tag was created before the fix commit — I rebuilt from the pre-fix trees."
   (356). NEW.
2. Rebuild a stack branch by branch with a check after each step. Quote: "The
   branch flip silently failed and left a junk commit on base. Recovering step
   by step with verification at each stage" (360). NEW.
3. A stacked branch cannot sit under the name of its base branch, because git
   holds a ref and a directory at one path. Quote: "Stack branches contain no
   slashes beyond the base name (git D/F conflict)" (680). NEW.
4. Merge a stack by retargeting each pull request to `main` after the one below
   it merges, and read the file list before each merge. Quote: "I retargeted
   each PR to `main` after the one below it merged. That is what kept each PR's
   diff to its own layer instead of re-showing the whole stack — I checked the
   file list on every PR before merging" (773). NEW.
5. Verify a merged tree from a clean extraction, not from the worktree. Quote:
   "From a clean extraction of `main` (`git archive origin/main`), 104 tests
   pass" (777). NEW.
6. Before shipping a stricter validator, run it read-only over every real
   object it will meet. Quote: "I queried all real workshop instances read-only
   — all six are instance-owned and `nic_device` accepts every one." (661). NEW.
7. Check a document lint against the same document on the base branch before
   reporting findings. Quote: "ADR 0001 shows findings — let me check whether
   they're pre-existing on main or from my edit" (198). NEW.
8. Apply another actor's uncommitted fixes to a stack one layer at a time.
   Quote: "Now I'll split the fixes by layer so each PR carries only what
   belongs to it" (620). The layer boundary is ALREADY WRITTEN in
   `.kb/spec-kit.md`. NEW for the patch-per-layer method.
9. Reproduce the effect of a rebuild when the lifecycle verb has nothing to
   apply. Quote: "The post-revert recovery path can be measured directly — move
   the agent back to the shared bridge (as a rebuild would), then let the
   wrapper recover it" (340). NEW. `.kb/fence.md` describes the rebuild and the
   release, not a verification recipe.
10. `lxc network acl create` takes a name only, and `lxc network acl rule add`
    refuses an exact duplicate. Quotes: "`acl create` rejects `description=`"
    (304), "`rule add` rejects exact duplicates — so converge must diff before
    adding." (220). NEW. PROJECT-SPECIFIC FACT for `research/` or
    `.kb/fence.md`.
11. Every recipe runs through `uv run`, not a `.venv` path. Quote from the
    review comment on #32: "can we use uv instead of calling a .venv path?"
    (708). ALREADY WRITTEN in the `justfile` header.
12. Never quote a test count. The agent wrote "84 tests pass" (567) and "Tests:
    59 → 75 → 92" (659). ALREADY WRITTEN in `.kb/writing-style.md` §6.
13. A feature number is never reused. Quote: "Number **002** chosen
    deliberately: 001 = withdrawn `workshop-egress-fence`, never reuse a number
    for a different feature" (118). ALREADY WRITTEN in
    `.kb/requirements-format.md` §4.
14. A delivery ticket produces a feature. Quote from the handoff: "Ticket #20
    is a delivery ticket. Produce the feature, not a plan." (42). ALREADY
    WRITTEN in `.kb/issue-tracker.md` and `.kb/spec-kit.md`.
15. A later instruction of the person overrides the handoff prompt. The handoff
    said "Do not push, merge, rebase, or touch other branches" (44), and the
    person later said "review all done, merge the full pr stack (including new
    36)" (743). NEW. The `hwt` skill states the handoff sentence and no rule for
    its reversal.
16. A change merged to `main` while a delegated session runs can reject the
    design that session built. Quote: "Decisive finding: ADR 0006 on main
    **rejected** one project for both workshops — the design my code assumes. I
    must adapt the stack." (406). NEW. No repository file states how a running
    session notices a new decision record.
17. The description of an ACL rule became part of the rule identity, so a
    reworded description rebuilds the rule. Quote: "adding the description to
    the rule identity means a rule whose description is edited is now
    *replaced* rather than updated" (665). PROJECT-SPECIFIC FACT for the
    convergence record.
18. `gh pr edit <n> --body` fails on `gh` 2.45, and `gh api -X PATCH` works.
    Quote: "`gh pr edit` hits a deprecated-API bug in gh 2.45. Using the REST
    API instead" (532). NEW as a version fact. `.kb/issue-tracker.md` already
    teaches `gh api` as the fallback for a missing flag.
19. Write a script to a file instead of piping into a heredoc. Quote: "The
    heredoc ate the pipe. Writing the check to a file instead" (638). NEW.
20. Pass the working directory inside the command. Quote: "The workdir parameter
    didn't apply — rerunning with an explicit cd" (308). NEW. A fact about the
    agent harness, not about this repository.

## What should not become a skill

- The bridge names, the `wp-agent` and `wp-plane` DNS domains, and the two
  subnets. They are configuration in `fence/fence.yaml`, and a skill that
  repeated them would drift from the file.
- The operator config at `~/.config/monitor-agent/fence.env` with
  `MONITOR_LLM_ADDRESS` and `MONITOR_LLM_PORT`. This session made the LLM allow
  rule part of the fence. Later requirements withdrew that rule, and ADR 0008
  now records the file as the proxy's upstream setting.
- The scratch workshop project ids (`325ae762`, `f0244857`, `3e3bd21d`) and the
  leftover `probe-acl` object. One host's history.
- "Ask before any step that destroys host state" as a standing rule. It is one
  handoff prompt's rule, and a general form would need a decision about which
  kinds of state count.
- The note that the person's own checkout of `main` was behind: "your primary
  checkout's `main` is still behind `f4d8f59` (I only fetched into this
  worktree, since `main` is checked out elsewhere)" (788). One moment on one
  host. Naming the commit and the branch state is the durable form, and the
  agent did that.
- The MiniMax quota error as a lesson about reviewing. The reusable part is the
  shape of the review brief, which belongs to the review session's digest.
- The claim that a stand-in listener does not survive a rebuild, so the probe
  answers `refused`. ALREADY WRITTEN in `research/separate-bridges.md`.
- The agent's account that its own writes did not cause the sibling workshop to
  disappear. One session's account of one host event, unverifiable from the
  repository.
