# ses_e2fa08eb2ffewNk3XysPmOi06p: Build Hermes agent Workshop #24

## What the person asked for

- "`/wayfinder wayfinder #24`" (USER 1794497300243, flat line 10). The ask states
  the deliverable and the two rules that shaped the session: "Ticket #24 is a
  delivery ticket. Produce the built Workshop, not a plan." and "Ask before any
  step that destroys host state, including `lxc` deletions and Workshop
  removal."
- Asked to name the LLM endpoint (question, msg 76). The person answered:
  "copilot gpt-6.1-terra ; instruct me to set up keyring items if they do not
  exist". The agent had recommended MiniMax in the same question.
- "@luna verify that "service=monitor-agent account=llm-api-key holds
  MONITOR_LLM_API_KEY, set to the GitHub OAuth token from your opencode
  github-copilot login" only has access to copilot models, and not other github
  permissions" (USER 1794502097322, flat line 151).
- "another ticket work identified work for this ticket\n/tmp/handoff-agent-build-move.md"
  (USER 1794502368518, flat line 202).
- Asked how to verify the move (question, msg 238). The person answered
  "Launch and remove the stale one (Recommended)".
- "pr 28 landed, rebase from main" (USER 1794504989434, flat line 252).

## What was produced, and whether it worked

- Three commits on `wayfinder/agent-workshop-build`, per the agent's summary:
  `e9e4f1a feat: add the agent workshop definition and SDK`, `4e44972 refactor:
  move the agent workshop into its own project`, `6792f08 docs: note when the
  setup hook runs`. Then a rebase onto the new `main` and a force-push with
  `--force-with-lease` (`6792f08...a3da630`). The log shows
  `git push --force-with-lease origin wayfinder/agent-workshop-build` (msg 276).
- Pull requests #28 (plane workshop decision, branch
  `wayfinder/plane-workshop-provisioning`, msg 236) and #29 (agent workshop,
  msg 237) opened from this worktree. The transcript ends with #29 mergeable and
  unmerged, so its merge was not observed.
- Issue #24 closed with a resolution comment (comment msg 179, close msg 180)
  and map #1 updated (msg 181). The trail entries were added (msg 184).
- Verified, on the agent's report and the command output in the tool log, and
  not re-measured here: `workshop launch agent` (msg 72) and `workshop refresh
  agent` (msg 138) built and started the workshop, the container's
  `config.yaml`, `.env`, and helper were byte-identical to the committed files
  (msg 151), the helper applied 4 secrets, `hermes -z` answered `ready`
  (msg 134), a terminal command printed `monitor-agent-workshop-ok` and saw
  `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY`, and the key was found only in
  `~/.hermes/cache/scratch/hermes-snap-*.sh` (msg 166).
- Not verified, by the agent's own statement: the proxy leg, because the plane
  workshop and the fence were not built on this host. Also not verified:
  `workshop refresh` from `agent/`, and the #29 merge.
- The token audit in the second turn produced measured results (msg 195 and
  msg 197): `x-oauth-scopes: read:user`, `GET /user` 200, `GET /notifications`
  403, `GET /repos/hammerstefan/monitor-agent` 404, and a `git ls-remote` of the
  private repository failing with `remote: Write access to repository not
  granted.` and `The requested URL returned error: 403` (msg 203).

## Corrections the person made

- The agent offered three endpoint options and recommended the first. The
  person rejected the recommendation: "copilot gpt-6.1-terra ; instruct me to
  set up keyring items if they do not exist" (msg 76). The whole build then
  followed the Responses-API path that this choice forced.
- The agent asked whether to launch from the moved project and remove the stale
  workshop. The person took the option that removed host state: "Launch and
  remove the stale one (Recommended)" (msg 238). No other correction of the
  agent's behavior appears in the transcript.

## Conventions, commands and values stated and written down nowhere

- The ask's host-state rule, in the person's harness words: "Ask before any
  step that destroys host state, including `lxc` deletions and Workshop
  removal." (USER 1794497300243).
- The endpoint choice, verbatim: "copilot gpt-6.1-terra" (msg 76). The agent
  translated it to `https://api.githubcopilot.com` and `gpt-6.1-terra`.
- The keyring layout is the agent's proposal, approved by the person through
  "instruct me to set up keyring items if they do not exist": `service=monitor-agent
  account=llm-endpoint` and `service=monitor-agent account=llm-api-key` (msg 76
  and msg 102). The same two items are recorded in `adr/0005`, so the names are
  written down.
- The person asked for a verification of a claim the agent had already made,
  which fixes a habit: a keyring item's permissions are to be measured, not
  assumed from the value's origin (USER 1794502097322).
- `secret-tool store` keeps a multi-line `KEY=VALUE` value intact: the agent
  wrote `X_ONE=1\nX_TWO=2` and read it back with `secret-tool lookup ... | cat -A`
  (msg 177). The helper depends on this.

## Failures, their cause, and the fix

1. `hermes -z "Reply with the single word: ready"` failed after 1m2s. The output
   was `Command helper: applied 4 secrets` then `Error: Gateway starting:
   deadline` (msg 108). `~/.hermes/logs/agent.log` held `WARNING
   hermes_cli.post_update: config migration skipped: This config predates
   version 12 (~2 years old) and can no longer be auto-migrated. Back up
   ~/.hermes/config.yaml and run \`hermes setup\` to regenerate, or manually set
   _config_version: 12 after reviewing the changelog.` (msg 110). The template
   that the hook wrote held no `_config_version` key. The agent then read
   `hermes_cli/config_defaults.py` and found `"_config_version": 53` (msg 122),
   wrote `_config_version: 53` into the container config (msg 123), started the
   gateway, and the retry answered `ready` (msg 134). The committed template now
   holds `_config_version: 53` at line 15
   (`agent/.workshop/hermes/files/hermes-config.yaml`). The transcript does not
   separate this cause from first-start warmup, because the same window also held
   the gateway start.
2. A gateway started inside `workshop exec` dies with the exec.
   `~/.hermes/logs/gateway.log` recorded `Gateway stopped by an unexpected
   signal` and `Exiting with code 1 (signal-initiated shutdown without restart
   request)` (msg 130). Two earlier attempts to keep it alive gave nothing:
   `hermes gateway run --replace --quiet` printed nothing for 7m24s and the
   agent stopped the shell (msg 124 to msg 128), and `setsid nohup ... &` inside
   the same `bash -lc` produced no output (msg 129). The run that worked used
   `setsid nohup ~/.local/bin/hermes gateway run --quiet ... & disown` and then
   a separate exec (msg 131), and hermes logged `Auto-started gateway:
   exits after 600s with no clients, adapters, cron/kanban work or admissions`
   (msg 116).
3. `workshop list` in a directory without workshop files printed `error: not a
   project (no workshop files found)` (msg 15). The agent had run it before
   reading any definition.
4. `workshop info` with no workshop name printed `error: workshop not launched`
   while `workshop list` showed `agent  Off` (msg 70). After the move to
   `agent/`, the same command printed it again for the new project directory
   (msg 227).
5. `git push` failed four times with `fatal: 'hammerstefan' does not appear to
   be a git repository` and `fatal: Could not read from remote repository.`
   (msg 252 to msg 255). Cause: `git config --show-origin --get
   remote.pushdefault` returned `file:/home/stefan.hammer@canonical.com/.gitconfig
   hammerstefan`, so a bare `git push` asks the local filesystem for a remote
   named `hammerstefan`. `git push origin wayfinder/agent-workshop-build`
   worked (msg 256). The agent did not change the global config.
6. `gh pr edit 29 --body-file -` failed with `GraphQL: Projects (classic) is
   being deprecated in favor of the new Projects experience ...
   (repository.pullRequest.projectCards)` (msg 257). The fix was
   `python3` to build `{'body': ...}` as JSON and `gh api -X PATCH
   repos/hammerstefan/monitor-agent/pulls/29 --input /tmp/opencode/pr29.json`
   (msg 259).
7. The GitHub scope probe returned HTTP 400 on every endpoint. Cause: the agent
   sent `X-GitHub-Api-Version: 2026-08-01`, which `api.github.com` rejects
   (msg 195). The 400 hid the real statuses, and the response still carried
   `x-oauth-scopes: read:user`. With `2022-11-28` the calls returned 200, 403,
   and 404 as the scopes dictate (msg 197).
8. A GitHub token exchange answered `403 Forbidden. For more on scraping GitHub
   and how it may affect your rights ...` when the probe sent the stored
   `access` value with an `Editor-Version` header (msg 83). The probe that used
   the stored `refresh` value worked.
9. A Python one-liner over `gh issue list` raised `TypeError: sequence item 0:
   expected str instance, dict found`, because `assignees` holds objects rather
   than logins (msg 9). A `find /` search was killed after 120 seconds
   (`Exit code: 143`) (msg 9).
10. `search` was called as a direct tool and failed with `No tool named "search"
    is currently available.` (msg 5). The agent then reached the tool catalog
    through `execute`.
11. Three `edit` calls failed with `Could not find oldString in <file>. It must
    match exactly, including whitespace and indentation.` The agent had written
    the replacement text from memory of the file instead of from the line it had
    just read. Re-reading the region fixed each one (msg 142, msg 145, msg 168).
12. `workshop refresh agent` spent 7m58s, and inside it the installer's tag
    fetch timed out: `Could not refresh release history (... 'fetch', '--quiet',
    '--filter=blob:none', '--no-tags', 'origin', 'refs/tags/v*:refs/tags/v*'
    timed out after 30 seconds); the version label may be stale or unknown until
    the next update`. The install completed (msg 149).

## Candidate lessons

1. NEW. A hand-written hermes `config.yaml` without `_config_version` makes
   hermes skip its config migration, and `hermes -z` then fails with `Error:
   Gateway starting: deadline`. The stamp that works is the `_config_version`
   value of `hermes_cli/config_defaults.py` (53 at v0.23.1). The committed
   template holds it at `agent/.workshop/hermes/files/hermes-config.yaml` line
   15, and a hermes upgrade needs that line checked against the default again.
   Quote: "Error: Gateway starting: deadline" (msg 108) and "config migration
   skipped: This config predates version 12" (msg 110).
2. NEW. A helper or gateway started inside `workshop exec` dies when the exec
   ends, with `Gateway stopped by an unexpected signal` in its log. A detached
   process needs `setsid nohup ... & disown` and a separate exec to talk to it.
   Quote: "Gateway stopped by an unexpected signal" (msg 130).
3. NEW. `hermes gateway run --replace --quiet` is silent and does not return
   within seven minutes, so a wait on its output never completes. Quote: the
   agent's own reading, "status: running (pid 1127455, up 7m17s) (no output
   yet)" (msg 127).
4. NEW. `workshop list` outside a Workshop project exits nonzero with `error:
   not a project (no workshop files found)`. Quote: msg 15.
5. NEW. `workshop info` without a workshop name answers `error: workshop not
   launched` when the project's workshop has never been launched, even though
   `workshop list` shows it as `Off`. Quote: msg 70.
6. NEW. A Workshop project tracks its SDK by the absolute path of the SDK
   directory, so `git mv .workshop agent/.workshop` leaves the old project
   listing the workshop as `ready` with `tracking: <old path>/.workshop/hermes`.
   The stale workshop has to be removed, because a refresh there cannot work.
   Quote: the agent's finding, "After the move, the root project still listed a
   ready `agent` workshop whose SDK tracking path pointed at a directory that
   no longer exists." (assistant summary, flat line 235), and the `workshop
   info agent` output in msg 227.
7. NEW. In this person's environment a bare `git push` fails with `fatal:
   'hammerstefan' does not appear to be a git repository`, because
   `~/.gitconfig` holds `remote.pushdefault hammerstefan`. Push with the remote
   named: `git push origin <branch>`. Quote: msg 252 and msg 256.
8. NEW. `gh pr edit` fails in this repository with `GraphQL: Projects (classic)
   is being deprecated ...`, and the working substitute is `gh api -X PATCH
   repos/<owner>/<repo>/pulls/<n> --input <json>`. Quote: msg 257 and msg 259.
9. NEW. A wrong `X-GitHub-Api-Version` value answers 400 on `api.github.com`
   and leaves `x-oauth-scopes` in the response, so a scope audit reads as a
   total failure instead of a permission result. Quote: `HTTP/2 400`,
   `x-oauth-scopes: read:user` (msg 195) against `HTTP/2 200` (msg 197).
10. NEW. `secret-tool` stores and returns a multi-line `KEY=VALUE` value
    unchanged, which is what the secret interface relies on for a two-value
    item. Quote: the agent's probe with `cat -A` (msg 177).
11. NEW. The hermes installer inside a `refresh` takes about eight minutes and
    reports a non-fatal warning when its tag fetch times out at 30 seconds.
    Quote: "timed out after 30 seconds" and "process ended: exited cleanly after
    7m58s" (msg 149).
12. ALREADY WRITTEN. A named custom provider is needed for a Responses-only
    endpoint, because hermes derives the transport of a bare `provider: custom`
    entry from the host. See `adr/0005`.
13. ALREADY WRITTEN. The key reaches the environment of every command hermes
    runs and is written to `~/.hermes/cache/scratch/`. See `adr/0005` and
    `.kb/agent-workshop.md`.
14. ALREADY WRITTEN. A `launch` reuses an installed SDK snapshot whose content
    is unchanged, so `setup-base` does not run. See `.kb/agent-workshop.md` and
    `adr/0006`.
15. ALREADY WRITTEN. A `refresh` keeps the secret connection, and a `remove`
    plus `launch` leaves the workshop unconnected. See `adr/0005`.
16. PROJECT-SPECIFIC FACT. The workshop name `agent`, the two keyring accounts,
    and the endpoint values belong in the records and the operator's notes, not
    in a skill.

## What should not become a skill

- The named-provider rule and the credential exposure are already decided in
  `adr/0005`. Repeating them adds nothing.
- "Check the code before claiming a cause" is too general to teach. The useful
  part is lesson 1, which names the warning and the key.
- The MiniMax option, the keyring account names, and the Copilot endpoint are
  one machine's state. They belong in the operator's notes.
- The `find /` timeout and the `TypeError` in a one-off Python snippet are
  agent slips with no Workshop content.
- The 403 from the Copilot token exchange is upstream behavior of one endpoint
  and one login. It is not a rule for this repository.
