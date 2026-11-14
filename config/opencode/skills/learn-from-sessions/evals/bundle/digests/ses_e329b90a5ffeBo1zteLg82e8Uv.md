# ses_e329b90a5ffeBo1zteLg82e8Uv: Research web-only egress proxies

## What the person asked for

The session holds one prompt. It was written by the spawning session
(`ses_e32a298b1ffed7dXABQ4qPZ8xQ`) from the person's words at its flat:3, and no
human turn appears in this transcript (flat:4-31).

- The departure under study, as the prompt restates it: "OpenShell is abandoned
  entirely (no gateway, no supervisor, no sandboxes). Hermes (NousResearch/hermes-agent)
  runs directly in the agent Workshop LXD container with full control of it
  (root, CAP_NET_ADMIN). A configurable HTTP/HTTPS forward proxy in the plane
  Workshop mediates all web traffic. The fence that forces traffic onto the proxy
  must live outside the container (host-level: LXD bridge ACL / OVN / host
  firewall), because the agent controls the container's inside." (flat:14)
- "Do not post comments to GitHub, do not close issues, do not open pull requests"
  and "the parent session records the resolution." (flat:8)
- "Current date: November 2026", "verify against current upstream docs and
  release notes", and "retrieval first, pretrained memory second." (flat:15)
- "Do not state a capability you did not see in a doc, release note, or source
  file" and "mark uncertain items as "not verified" instead." (flat:15)
- "Read `.kb/writing-style.md` in that worktree FIRST and follow it strictly"
  (flat:23).
- "verify: whether Hermes' own `hermes egress` (iron-proxy) can run out of
  process on a separate host, and what it actually enforces." (flat:25)
- "Commit with a plain commit message (no AI attribution, no Co-Authored-By),
  push with `git push -u origin research/web-egress-proxy`, and open NO pull
  request." (flat:26)

## What was produced, and whether it worked

- Branch `research/web-egress-proxy`, commit `cfe9e7f`, holding a 584-line
  `research/web-egress-proxy.md`, pushed with no pull request (flat:77). The file
  is not on `main` today, and the current `adr/0001` links it on the branch.
- The branch was made in a separate worktree,
  `/tmp/opencode/web-egress-proxy`, from `origin/main` (flat:102). The worktree
  was left in place, as the prompt said (flat:27, flat:73).
- The shortlist, as the agent reported it: iron-proxy run standalone from the
  upstream release, mitmproxy 12, and Squid 7.8 (flat:80-83).
- The structural finding: "Credential injection into HTTPS is advisory against
  your threat model, no matter which proxy you pick" (flat:48). Injection needs a
  proxy CA in the agent container, and the agent holds root there. CONNECT-level
  allow, deny and audit survive a CA removal.
- The inverted default it flagged: OpenShell "audits by default and enforces when
  told", while "iron-proxy blocks by default and audits only with `warn` set"
  (flat:52).
- The style pass ran over the file before the commit, in four sweeps
  (flat:151-180), and the commit and push came last (flat:181-182).
- Verified: documentation, release notes and source files only, fetched
  2026-11-11. Not verified, and named in the file: Envoy dynamic forward proxy on
  CONNECT, the mitmproxy addon hook for refusing a CONNECT by hostname, tinyproxy
  and 3proxy destination ACL details, Squid v8 `http_access`, gost `rewriter`, the
  Caddy CONNECT log, the `docs.iron.sh/audit` schema, the iron-proxy version line,
  and Envoy hot restart (flat:95).

## Corrections the person made

(none found). No human turn appears in this transcript.

## Conventions, commands and values stated and written down nowhere

- The comparison shape: profile each candidate against a named baseline table,
  then end with a shortlist. The prompt asks for "a comparison table against the
  OpenShell baseline (policy TOML, audit-by-default with explicit enforce,
  credential placeholders `openshell:resolve:env:` resolved by the proxy, CONNECT
  chaining via `https_proxy`, supervisor middleware) and a shortlist verdict"
  (flat:24).
- The nine candidates: mitmproxy, Envoy, Squid, Caddy forward proxy, tinyproxy,
  3proxy, Pomerium, gost, and `hermes egress` (flat:26 of the parent, flat:80-85
  here).
- The iron-proxy settings that later appear in `adr/0001`: `tls.mode: sni-only`
  for CONNECT enforcement without a CA, the per-rule `warn` flag for audit-only
  mode, and the `secrets` transform with `proxy_value` and `require: true`
  (flat:42, flat:85).
- The style sweeps, run as four `grep` passes over the drafted file before the
  commit (flat:151, flat:167, flat:173, flat:180).
- The working path to a mitmproxy page after a 404:
  `https://docs.mitmproxy.org/stable/concepts/modes/` (flat:116).

## Failures, their cause, and the fix

- `webfetch` of `https://docs.mitmproxy.org/stable/overview-modes/` answered 404
  (flat:107-108). Cause: the path is retired. Fix: the live path is
  `/stable/concepts/modes/` (flat:116).
- `webfetch` of `https://gost.run/en/tutorials/mitm/` answered 404 (flat:125-126).
  Cause: the tutorial path differs. Fix: the sniffing tutorial at
  `/en/tutorials/sniffing/` answered (flat:143).
- One `websearch` and three `webfetch` calls came back "aborted",
  "Interaction cancelled because the location shut down" (flat:132-139). Cause:
  the tool session ended mid-call. Fix: the agent re-ran the same four requests
  unchanged and all four answered (flat:140-142).
- No `!! FAILED` line names a wrong configuration or a wrong fact. Every failure
  is a fetch that did not answer.

## Candidate lessons

1. ALREADY WRITTEN. Credential injection into HTTPS is advisory against a root
   agent, and CONNECT-level allow, deny and audit survive a CA removal.
   `adr/0001-hermes-runs-in-a-fenced-agent-workshop-and-a-plane-workshop-proxy-mediates-its-web-egress.md`,
   Decision, last bullet.
2. ALREADY WRITTEN. iron-proxy blocks by default, and a new allowlist rule runs
   with `warn` first so the traffic pattern can be checked. `adr/0001`, Decision
   and Consequences.
3. ALREADY WRITTEN. The version line of iron-proxy is unresolved, and `adr/0001`
   names no release because of it. `adr/0001`, Decision.
4. NEW. Candidates are compared against a named baseline in one table, and the
   report ends with a shortlist. Quote: "a comparison table against the OpenShell
   baseline ... and a shortlist verdict: which one to three candidates best fit
   the departure, and why" (flat:24). Neither `AGENTS.md` nor
   `.kb/writing-style.md` states a comparison shape for a survey.
5. NEW. A capability that no fetched page shows is reported as absent, with the
   date the pages were read, rather than as "not supported". Quote: "The Pomerium
   absence verdict covers the pages fetched on 2026-11-11. No claim is made about
   unreleased or undocumented modes." (flat:172).
6. NEW. A retired documentation path is replaced from the site's own index. Quote:
   "Now let me get the mitmproxy docs (the first URL 404'd)" (flat:41). The working
   path is at flat:116.
7. PROJECT-SPECIFIC FACT. The nine candidates and the four rejected families, with
   the reason each fails: Envoy for weight and unverified CONNECT behaviour, the
   Caddy plugin for being experimental, tinyproxy and 3proxy for coarse
   destination policy, Pomerium for having no outbound forward proxy. The full
   profile is on the branch and `adr/0001` names the shortlist.
8. PROJECT-SPECIFIC FACT. `hermes egress` runs the proxy as a local subprocess
   bound to the Docker bridge or loopback, so the plane must run the upstream
   binary directly (flat:91). `adr/0001` states the same in one line: the proxy
   is "iron-proxy, run standalone from its upstream release".

## What should not become a skill

- The per-candidate configuration excerpts and the table cells. They are values
  of nine upstream products at one date.
- The four `grep` sweeps (flat:151-180). They implement the rule `AGENTS.md`
  already states.
- "Do not post comments to GitHub, do not close issues, do not open pull
  requests" (flat:8). It is the division of labor of one dispatch, and the parent
  session's rule is that it records the resolution.
- The final poke to the style of one sentence (flat:172). It is an edit.
