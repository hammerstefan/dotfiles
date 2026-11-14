# ses_e2d2b58c2ffeHuzBKnV2ma2GvZ: Verify the v0.56.0 binary in the plane workshop

The session ran in the worktree
`/home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/spike-iron-proxy-plane`,
on the branch `spike/iron-proxy-plane`, from the base `7451cc7`.
It was spawned by session `ses_e2d30ff01ffePWE31UOV5nrZ3d`.

Position references below name the user turn and the line in the flattened
transcript `flat/ses_e2d2b58c2ffeHuzBKnV2ma2GvZ.txt`.

## What the person asked for

The first user message is the brief that `/wayfinder-hwt` wrote, not the
person's own typing. Its asks:

- "Put the spike in the repository at `spike/iron-proxy-plane/`, on the branch `spike/iron-proxy-plane`, which is the branch this worktree already holds."
- "Answer the questions in the ticket body and record each answer". The five
  questions are the binary start and its listeners, one allowlisted host and
  one refused host, the reload and a bad file, where per-request records go,
  and the archive digest against the published `checksums.txt`.
- "Ask before the step that touches host state the spike did not create, such as removing an existing workshop instance or changing the committed `plane/proxy-policy.yaml`, and ask before the step that commits a record on `main`."

The person's own words, in order:

- USER 2 (line 73): "keep going"
- USER 3 (line 200): "continue"
- USER 4 (line 367): "continue"
- USER 5 (line 407): "push, create pr for main changes"
- USER 6 (line 438): "merge the pr. are we done?"

The person answered two questions the agent put to them. The first was where
the ADR amendments and the record should go. The second was whether to push
the spike branch. "push, create pr for main changes" answered both at once.

## What was produced, and whether it worked

Verified in the main checkout on 2026-11-13:

- The spike commit `38bf2f2 spike(workshop): verify the v0.56.0 binary in the plane workshop` on `spike/iron-proxy-plane`, three files and 675 insertions: `spike/iron-proxy-plane/README.md`, `probe.sh`, `run.sh`. The commit was `a9f88d3` with four files before the agent amended it.
- The findings record `research/iron-proxy-plane.md` on `main`, and the amended records `adr/0004-the-plane-verifies-the-proxy-archive-against-a-pinned-digest.md` and `adr/0006-the-plane-workshop-installs-the-proxy-from-a-pinned-release.md`.
- Pull request #41 "Record the iron-proxy plane verification", merged as `7d8932c` at 2026-11-13T16:24:39Z. The branch `docs/adr-iron-proxy-plane` was deleted after the merge.
- Issue #18 is closed and assigned to `hammerstefan`.
- The map line in issue #1 "Decisions so far" was edited four times. It first pointed at `blob/spike/iron-proxy-plane/research/iron-proxy-plane.md`, then at `blob/main/research/iron-proxy-plane.md` after the record moved.

The values the session recorded, and their standing:

- The installed binary is version `0.56.0` with sha256
  `ffc438b55c104b896a918dca74fb8b016d0b5e84bf12349586d50e07ea5c9b1f`.
- The archive pin in `plane/.workshop/iron-proxy/proxy-digest.txt` is
  `46189e16f3f97319d68bc6a672f0be003bf8d2f2052ccd2be8cac00d8c3346b2` for
  `iron-proxy_0.56.0_linux_amd64.tar.gz`. I fetched the release
  `checksums.txt` for `v0.56.0` and the line for that file name holds the
  same digest, so the pin agrees with the published file.
- The five listeners, the transform pipeline `allowlist`, the HTTP 200 and
  403 answers, the CONNECT response `HTTP/1.1 403 Forbidden` with curl exit
  code 56, the management API answers 401 and 200 and 422, and the journal as
  the place of the per-request records: all stated in
  `research/iron-proxy-plane.md`.

What the session stated as not verified, and what I could not verify:

- The archive against a signature. The release publishes none from `v0.43.0`
  onward, as ADR 0004 already records.
- The `checksums.txt` as it stood when the pin was written.
- A rebuilt container, and the service after a fence restart.
- The metrics listener was not read, the `check-health` hook was not run, and
  the `dnsguard` list was not tested.
- The agent's claim "the pin matches the published `checksums.txt`" is true of
  the values. The check as executed did not compare the downloaded file, as
  the failures section shows.

## Corrections the person made

(none found)

The person gave decisions and permissions, not corrections. The agent
corrected its own placement of the record once: "`.kb/spikes.md` §7
says the findings record goes to `main` in the same commit as the ADR"
(line 429). The brief that told it to do otherwise was written by the parent
session.

## Conventions, commands and values stated and written down nowhere

The person stated these, and no repository file holds them:

- The delivery of a change that touches `main` is a pushed branch and a pull
  request for the person to merge. USER 5: "push, create pr for main changes".
  The brief had offered "commit them on `main`, put them on a docs branch, or
  leave them", and the person chose none of the three as written.
- The person merges. USER 6: "merge the pr. are we done?". The agent ran
  `gh pr merge 41 --merge --delete-branch` only after that line.

The agent stated these, and they hold as project facts:

- The plane instance is `plane-2a96f0cb` in the LXD project
  `workshop.1077165261`, at `10.255.0.10` on the bridge `mon-plane-br`.
- The source clone for the release is `https://github.com/ironsh/iron-proxy.git`,
  while the release assets come from
  `https://github.com/paradigmxyz/iron-proxy/releases/download/v0.56.0/`. The
  second URL is the one in `plane/.workshop/iron-proxy/hooks/setup-base`, so
  only the source clone exposes the different organization.
- The host linter is
  `python3 /home/stefan.hammer@canonical.com/.copilot/skills/asd-ste100/scripts/ste-lint.py <file>`.
  `adr/README.md` names `ste-lint.py` but not its path.
- The agent read the Workshop LXD project from `id -u` as
  `workshop.$(id -u)`. The transcript does not show the output of that
  command.

## Failures, their cause, and the fix

1. A `shell` call failed with "Working directory does not exist:
   /home/stefan.hamer@canonical.com/...". Cause: the work directory was
   misspelled, with `hamer` for `hammer`. Fix: the next call used the correct
   path.
2. Two `edit` calls failed with "Could not find oldString ... The closest
   lines in the file: 195: ...". Cause: the README text had changed since the
   agent read it, because earlier edits in the same turn rewrote those lines.
   Fix: the agent read the lines around the target, then edited the text that
   was there.
3. Three tool calls aborted with "Interaction cancelled because the location
   shut down" or "Tool execution interrupted", one `edit`, one `write` with an
   empty input, and one `question`. Cause: the harness stopped the call, not
   the file. Fix: the agent re-read the file and ran the call again.
4. `run.sh` picked the plane instance with a status filter that matched no
   running instance: "The status filter is wrong. Let me fix it and the
   override ordering." (line 211). Fix: the script selects by
   `user.workshop.name == "plane"` and the running status.
5. A curl through the tunnel to a denied host printed `000`. Cause: the
   response on the wire is HTTP 403, and "curl reports exit 56" (line 215).
   Fix: the probe reads the raw response with `nc` and reports exit code 56 as
   the client's answer.
6. The record search in the probe returned unrelated man pages, and `tail -2`
   selected the wrong records. Cause: "The audit records interleave, so `tail
   -2` is not a stable selection" (line 225). Fix: a `record()` helper selects
   by host and by mode.
7. The run exited 1 before cleanup: "The probe's last command (the intentional
   config rejection) propagates a nonzero status" (line 237). The scratch
   directory held the bearer token header and was left behind. Cause: the
   cleanup trap ran only on the paths the script reached. Fix: `run.sh`
   removes the scratch directory on every exit, and the agent removed the
   leftover directory by hand.
8. The live policy digest changed between two runs, `2746689c` then
   `bb898e2f`. Cause: the concurrent session `#25` was editing the mounted
   `/project/proxy-policy.yaml`. Fix: the probe reports the digest of the file
   the service read next to the digest of the committed policy, and the record
   states that the two differed.
9. The agent created a stray `plane/.workshop.lock` in the main checkout with
   an exploratory `workshop --project plane ...` run, then removed it with
   `rm -f ~/git/monitor-agent/plane/.workshop.lock` and restored the earlier
   value with `printf '29f37005' > plane/.workshop.lock`. Cause: a `workshop`
   run in a project directory writes that file, and `.kb/fence.md` states that
   the fence reads it to find the instance.
10. The archive digest check ran as
    `curl ... -o iron-proxy-0.56.0.tar.gz <archive> && sha256sum iron-proxy-0.56.0.tar.gz`
    and then `curl ... -o checksums.txt <checksums> && sha256sum -c checksums.txt`
    in `/tmp/opencode`. The checksum file names
    `iron-proxy_0.56.0_linux_amd64.tar.gz`, with underscores. `sha256sum -c`
    reads each input by the name in the file, so the downloaded file under the
    dash name is not the file that check reads. The transcript shows no output
    for that call, and the agent's report states the two agree. The two digest
    values do agree, as I confirmed against the published file.

## Candidate lessons

Positions name the user turn and the line number in the flattened transcript.

- NEW: A checksum comparison selects its input by the file name in the
  checksum file, so download the archive under the name the release names.
  Quote: the shell call `curl -sSL --max-time 120 -o iron-proxy-0.56.0.tar.gz https://github.com/paradigmxyz/iron-proxy/releases/download/v0.56.0/iron-proxy_0.56.0_linux_amd64.tar.gz && sha256sum iron-proxy-0.56.0.tar.gz && tar -xzf ...` and later `sha256sum -c checksums.txt` (tool log lines 583 and 585). The agent then wrote "the pin matches the published `checksums.txt`" (line 386).
- NEW: A `workshop --project <dir>` run writes `.workshop.lock` in that
  directory, so an exploratory run in a checkout changes the file the fence
  reads, and a copied project directory addresses the same instance.
  Quote: "removed the stray lock file I created in the main checkout" and
  "restored the lock file that was there before my exploration" (tool log
  lines 601 and 604). `.kb/fence.md` states that the fence reads the lock and
  `.kb/spikes.md` §4 keeps it untracked. Neither states that the CLI writes
  it.
- NEW: A probe whose last command is an expected failure exits nonzero and
  skips its cleanup. Quote: "The run exited 1 before cleanup. The probe's last
  command (the intentional config rejection) propagates a nonzero status."
  (line 237). `.kb/spikes.md` §5 states that a spike cleans up what it
  creates, and not how a failing command defeats that.
- NEW: When another session shares the host, a measurement states the digest
  of the file it read, not the digest of the committed file. Quote: "The live
  `/project` policy digest changed between runs (2746689c → bb898e2f)."
  (line 221). The record states this case in `research/iron-proxy-plane.md`
  Findings, and no rule states the practice.
- NEW: A brief that places a spike's findings record on the spike branch
  contradicts `.kb/spikes.md` §7, so the brief is checked against that law
  before the session starts. Quote: "I had first put the record on the spike
  branch, so I amended that commit to drop it before pushing, and moved the
  record into the docs PR instead." (line 429). The law is ALREADY WRITTEN in
  `.kb/spikes.md` §7. The brief's mismatch is the new fact.
- NEW: `gh issue edit --body-file` stores a trailing newline, so a byte
  comparison of a map body strips it. Quote: "GitHub added a trailing newline.
  Let me confirm the body content is otherwise identical." (line 287), and the
  verification with `diff <(printf '%s' "$(cat file)") ...` (tool log line
  783).
- NEW: The repository's own records produce the same Simplified Technical
  English findings, so the target is no worse than the precedent. Quote: "The
  house records show the same lint findings. Let me still improve the passive
  constructions" (line 259).
- ALREADY WRITTEN (`research/iron-proxy-plane.md` Verdict and Gotchas, and
  the comment in `plane/proxy-policy.yaml`): the refused host answers HTTP 403
  only when the policy holds no `warn` line. Quote the record: "The refusal
  with HTTP 403 needs the policy without that line." The `example.com` and
  `example.net` choice is in `plane/proxy-policy.yaml`, so it is a
  PROJECT-SPECIFIC FACT and not a lesson.
- ALREADY WRITTEN (`research/iron-proxy-plane.md`): the five listeners, the
  journal as the place of the per-request records, the missing `log.audit_path`
  field, the reload that leaves a listener in place, the record shapes for
  plain HTTP and CONNECT, and curl exit code 56 on a refused CONNECT.
- ALREADY WRITTEN (`adr/README.md`): the record number is one higher than the
  last record in the index or in any open pull request, and `ste-lint.py` is
  the mechanical first pass. The agent's "ADR 0007 is claimed by the
  acceptance branch, so the next number is 0008" (line 291) restates that rule.
- PROJECT-SPECIFIC FACT: `plane-2a96f0cb`, the LXD project
  `workshop.1077165261`, the address `10.255.0.10`, the bridge `mon-plane-br`,
  and the two digests. These belong in the findings record, and
  `research/iron-proxy-plane.md` holds them.

## What should not become a skill

- The decision to measure the live plane instance instead of launching a
  separate one. The fence owns the one plane address, and the concurrent
  session held the instance. `.kb/fence.md` already fixes the address, so the
  decision needs no rule.
- The scratch proxy inside the container with the listener ports moved aside.
  It is script detail of this spike, and `spike/iron-proxy-plane/run.sh` holds
  it.
- What the ticket did not ask, such as the metrics listener, `dnsguard`, and
  the `check-health` hook. That is ticket scope, and the record states each as
  not verified.
- The agent's repeated reading of ADR 0004 and 0006 while drafting the
  amendments. It reflects an unclear place to start, not a practice to teach.
- The trail entries for the pull request and the ticket. They are harness
  bookkeeping with no repository rule behind them.
