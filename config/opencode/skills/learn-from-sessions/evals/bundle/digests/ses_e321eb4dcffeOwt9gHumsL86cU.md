# ses_e321eb4dcffeOwt9gHumsL86cU: Write v0.56.0 plane proxy configuration

## What the person asked for

- Message 1 (flat line 2), the hwt brief for ticket #17. Its Ask line: "@hwt for EACH ticket you identified". The brief names the ticket as "Write the plane proxy configuration for v0.56.0", GitHub issue #17.
- Message 2 (flat line 120): "continue"
- Message 3 (flat line 172): "create PR"
- Message 4 (flat line 187): "@review-deepseek changes in this branch"
- Message 5 (flat line 240): "rebase on main"

## What was produced, and whether it worked

- `plane/proxy-policy.yaml` with `tls.mode: sni-only`, `dns.enabled: false`, `tunnel_listen: 10.255.0.10:1080`, `http_listen` and `https_listen` pinned to loopback, `metrics.listen: 127.0.0.1:9090`, `management.listen: 127.0.0.1:9092`, `api_key_env: IRON_MANAGEMENT_API_KEY`, one allowlist entry `example.com` with `warn: true`, and `upstream_deny_cidrs` omitted.
- One sentence added to the "Repository state" section of `.kb/project.md`.
- Commit `140e62e` on `wayfinder/plane-proxy-config`, pushed. A follow-up `24f158f` from the review. Both rebased onto `main` as `db3701a` and `5dec57e`, force-pushed with `--force-with-lease`.
- Issue #17 resolved with comment 6814138833 and closed. The comment was edited after the rebase to cite the new SHAs.
- One line appended to `## Decisions so far` in map issue #1, with a read before the write and a read after it.
- PR #27, titled "Add the plane proxy policy for v0.56.0". It is merged today as `30fdc22`.
- Verified: the policy parses and validates under the release's own loader. The agent wrote a scratch Go test into a clone at tag `v0.56.0` (commit `3d96ce8`), ran `go test ./internal/config/`, and ran three control cases that confirmed the loader rejects an unknown field, rejects DNS enabled without `proxy_ip`, and rejects an unset bearer-token variable. The scratch file was deleted before the commit.
- Verified: port `17670` is in use on the host, by `ss`.
- Verified by the agent: the released tree gives the tunnel listener the plain HTTP role as well as CONNECT, so the ticket body's split of the two roles is wrong for this release. The review child confirmed the same reading with line citations.
- Not verified: that the process starts or binds any listener. The ticket assigns that claim to #18, and the agent stated the limit in the report.
- Not verified by anyone in this session: the archive download and its digest. Ticket #19 owns that.
- The file on `main` today differs from what this session committed. `warn: true` is gone, `api.githubcopilot.com` is in the list, and the header comment about the fence was changed again.

## Corrections the person made

- The agent closed the ticket work with "No pull request opened." in the commit report and "No pull request is opened, and the person decides what merges." in the resolution comment. The person then wrote "create PR" (message 3, flat line 172).
- The agent reported "PR #27 now holds two commits and is ready for your merge decision." The ticket said "do not rebase". The person then wrote "rebase on main" (message 5, flat line 240). The agent read the instruction as an override: "The user's explicit instruction overrides the ticket's no-rebase rule (same as the PR override)."
- No correction of the agent's technical work by the person appears in this transcript. Every correction of the file came from the review child, not from the person.

## Conventions, commands and values stated and written down nowhere

- Reserved record number, from the brief: "Two other sessions work in parallel on this map, so `0003` is yours alone." The agent decided no record was needed and left `0003` unused.
- Shared map body procedure, from the brief: "The map body is shared with two other sessions working in parallel, so re-read the body immediately before you write it, write only your own line into it, and re-read afterwards to confirm your line survived. If a concurrent write dropped your line, put it back."
- A host port is not free merely because upstream documents it: "Port `17670` is already taken on this host by the machine's own OpenShell gateway, so it is not free."
- The claim limit for a configuration ticket: "Do not start the proxy, and do not claim that it starts."
- The branch and PR sequence the person wants, which no repository file states: the ticket brief says "Open no pull request", and the person asks for "create PR" and then "rebase on main" on the finished branch. The same two requests appear in `ses_e321ea872ffeuUyyOvuQCYo8WS` (messages 3 and 5).
- The chosen values, from the agent: tunnel listener at `10.255.0.10:1080`, taken from the plane bridge address in the two-bridge spike. The agent then wrote "`10.255.0.10` follows the spike's convention."

## Failures, their cause, and the fix

- A program under `/tmp/opencode/policy-check` imported `github.com/ironsh/iron-proxy/internal/config`. The Go internal-package rule blocks that import from another module. The agent's own words: "The `internal/` package boundary blocks imports from outside. I'll run the check inside the throwaway clone as a scratch test file (untracked, never committed)." The fix was a test file inside `internal/config` of the clone, run with `go test ./internal/config/ -run 'TestPlanePolicy'`, then deleted.
- The tool log holds no `!! FAILED` line for this session. The two failures above and below are recorded in the agent's prose only.
- The session was interrupted by a model switch: `===== MODEL-SWITCHED: {"id":"glm-5.3-flash","providerID":"zai-coding-plan"} =====` at flat line 118, then the person typed "continue". The cause is not stated in the transcript.
- The review child returned "approve with nits" while its first finding was marked "Major". The agent treated it as work to do rather than a nit: "The reviewer's quote of ADR 0001 matches (my grep just split on a line wrap). The 'only' is genuinely ambiguous, so I'll fix it as a follow-up commit rather than rewriting the pushed commit."

## Candidate lessons

1. NEW. Check a configuration file written for a release against that release's own loader, by running a scratch test inside the tagged tree. Quote: "The `internal/` package boundary blocks imports from outside. I'll run the check inside the throwaway clone as a scratch test file (untracked, never committed)." (assistant, flat line 127)
2. NEW. A commit cannot fix a claim that reads two ways, so the follow-up commit is the correct repair when the pushed commit must not be rewritten. Quote: "The 'only' was meant to scope to the proxy's listeners, but a security comment that reads two ways is wrong." (assistant, flat line 202)
3. NEW. A rebase rewrites the commit SHAs that a posted issue comment cites, so update the comment in the same pass and check for other stale statements in it. Quote: "One consequence to handle: the #17 resolution comment cites commit `140e62e`, and a rebase rewrites both SHAs." (assistant, flat line 243)
4. NEW. A line written into a shared issue body needs a read before the write and a read after it, compared against the count of lines the writer meant to add. Quote: "The map body is shared with two other sessions working in parallel, so re-read the body immediately before you write it, write only your own line into it, and re-read afterwards to confirm your line survived." (person, brief, flat line 82)
5. NEW. The person wants a pull request and a rebase on each ticket branch after the session reports, although the ticket brief forbids both. A ticket session that stops at "pushed, no PR" costs the person a second message on every branch. Quote: "create PR" (person, message 3) and "rebase on main" (person, message 5).
6. ALREADY WRITTEN. The listener roles of `v0.56.0` and the plane address and port. `research/iron-proxy-plane.md` states "The tunnel listener answers plain HTTP and CONNECT on one port" and names `10.255.0.10:1080`.
7. ALREADY WRITTEN. That the documentation pages omit fields the release has. `research/iron-proxy-plane.md` records the `log.audit_path` refusal with the loader message, and the committed `plane/proxy-policy.yaml` header states the rule.
8. PROJECT-SPECIFIC FACT. The five `upstream_deny_cidrs` defaults, including `fd20:ce::254/128`, and the `IRON_MANAGEMENT_API_KEY` default name. These are release facts of `v0.56.0` and belong in the policy file's comments, which is where the agent put them.

## What should not become a skill

- The addresses `10.255.0.10` and `1080`. They are this project's choice, and the fence ticket allocates the real bridges.
- `example.com` as the allowlist host for the acceptance task. Nothing in the repository named a host, and the person has not confirmed the choice.
- "The documentation pages name no release." It is a fact about one upstream project on one date, and the agent recorded the fetch date.
- The claim that the loader rejects an unknown field. It is a release fact that the file's header comment and `research/iron-proxy-plane.md` already state.
