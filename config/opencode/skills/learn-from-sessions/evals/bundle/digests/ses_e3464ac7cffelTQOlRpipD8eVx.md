# ses_e3464ac7cffelTQOlRpipD8eVx: OpenShell two-bridge gateway spike

## What the person asked for

The session holds one prompt, an `hwt` hand-off written from a plan file. No
further human turn appears in this transcript (flat:2-171).

- "spike ~/tmp/plan-openshell-two-bridge-gateway.md"
- "The plan at `~/tmp/plan-openshell-two-bridge-gateway.md` describes a spike
  that measures whether the real OpenShell gateway works when the agent
  workshop and the plane workshop sit on two different LXD bridges with the
  agent bridge ACL in force."
- "Two earlier spikes split that question. `spike/two-workshop` proved the
  real gateway but on one shared bridge. `spike/separate-bridges` proved the
  two-bridge fence but used a stand-in listener on the gateway port. Neither
  shows the combination."
- "Read a branch without checking it out: `git show
  spike/separate-bridges:spike/separate-bridges/bridges.sh`."
- "This host runs other sessions. Use names nobody else uses: workshops
  `gbagent` and `gbplane`, bridges `gbr-agent` and `gbr-plane`, ACLs
  `gbr-agent` and `gbr-plane`, host stand-in ports `19811` and `19812`."
- "Never touch LXD objects, workshops, bridges, ACLs, or git branches you did
  not create."
- "Land the conclusion on `main` as `.kb/spikes.md` §7 requires ... Do it from
  a temporary branch: `git checkout -b tmp/record main`, commit, `git branch -f
  main HEAD`, return to your branch, delete the temporary branch."
- "Before you touch `main`, run `git -C
  /home/stefan.hammer@canonical.com/git/monitor-agent status --short`. If that
  worktree is not clean, stop and report instead of landing the record."
- "An earlier spike committed a private key by accident and had to purge it
  from every commit. Do not repeat that."
- "Report `ok`, `refused`, and `timeout` separately, because a refusal means
  the ACL admitted the path and nothing was listening, while a timeout means
  the packet was dropped."
- "which must report zero hard violations" (of `ste-lint.py`).
- "Finish with: what you did, what you found, what you did not verify, and
  what you need from the person."

## What was produced, and whether it worked

The session built the spike, ran it three times, committed the spike branch,
and committed the record to `main`.

- `spike/two-bridge-gateway/` holds the two workshop definitions, `bridges.sh`,
  `probe.sh`, `run.sh`, both install scripts, `state.env.template`,
  `README.md`, and a local `.gitignore` for `.tls/` (flat:189).
- The spike commit is on `spike/two-bridge-gateway` with subject
  "spike(workshop): measure the real gateway across two bridges" (flat:357).
- The record `research/two-bridge-gateway.md`, one bullet in ADR 0001, and one
  sentence in `research/separate-bridges.md` went to `main` in one commit
  (flat:193, flat:369).
- Quote on the runs: "The second and third runs agree, and the third run is
  the one the committed scripts and the record describe." (flat:191).
- Quote on the lint: "`ste-lint.py` reports zero hard violations on the README,
  the record, ADR 0001, and the edited separate-bridges record." (flat:195).
- The host was checked back to its prior state: no `gbr-agent` or `gbr-plane`
  bridge, no ACL, no workshop, no listener on 19811 or 19812, no `.tls`
  (flat:195, flat:328).
- Key material: the child scanned every commit on `main` and on the spike
  branch for private key blocks (flat:375, flat:376), and confirmed that
  `main` advanced by fast-forward only (flat:371, flat:373).
- Verified by measurement: the gateway reached over mutual TLS, the sandbox
  work under the fence, and the fence after each lifecycle event (flat:201-209).
- Not verified, and stated as such: the mediation path after a lifecycle
  event, the `lxd-vm` runtime, an OVN NIC ACL, the LXD `logged` state, an
  audit-mode policy violation, and whether the escape can be closed without
  passwordless sudo (flat:211-216).
- Open at the end of the transcript: the child asked four questions and no
  answer appears in this file (flat:218-223).

## Corrections the person made

(none found). The person does not reply in this transcript, so the four
questions at flat:218-223 are unanswered here.

## Conventions, commands and values stated and written down nowhere

- The naming rule for shared host objects: "Use names nobody else uses:
  workshops `gbagent` and `gbplane`, bridges `gbr-agent` and `gbr-plane`, ACLs
  `gbr-agent` and `gbr-plane`, host stand-in ports `19811` and `19812`."
  (flat:75-79). No repository file states this rule.
- The landing procedure it was told to use: "`git checkout -b tmp/record main`,
  commit, `git branch -f main HEAD`" (flat:120-122). This failed. See below.
- The lint gate and the script path: "`/home/stefan.hammer@canonical.com/.config/opencode/skills/asd-ste100/scripts/ste-lint.py
  <file>`, which must report zero hard violations" (flat:146-148).
- The three-outcome vocabulary for a TCP probe, quoted above (flat:98-101).
  The repository already states the same distinction in
  `research/separate-bridges.md` and `research/two-bridge-gateway.md`.
- The incident the credential rule came from: "An earlier spike committed a
  private key by accident and had to purge it from every commit." (flat:138-139).

## Failures, their cause, and the fix

The transcript holds no `!! FAILED` tool entry. Every failure below appears in
the run logs or in the report.

1. Run 1, remote gateway registration. Quote: "The first run failed on the
   remote gateway registration: the active gateway is named in
   `/root/.config/openshell/active_gateway`, one level above the `gateways`
   directory, and the file inside the gateway directory is never read."
   (flat:191). The fix was to confirm the path in upstream source
   (`crates/openshell-bootstrap/src/paths.rs`) and move the write (flat:299,
   flat:300).
2. Run 1, the ACL phase on a second run. Quote: "also made the ACL phase
   detach the ACL from the bridge before replacing it, so the phase can run
   twice" (flat:191, edit at flat:308).
3. Run 2, the workshop address. The `eth0_address` function read the address
   from `lxc list`, and the column is quoted across two lines once Docker adds
   a second address. The fix reads the address from the instance (flat:322).
   The record states the cause in `research/two-bridge-gateway.md`, Gotchas.
4. The landing procedure. Quote: "`git branch -f main HEAD` failed because
   `main` was checked out in the main worktree at that moment. I
   fast-forwarded `main` in that worktree with `git merge --ff-only
   tmp/record`, then deleted `tmp/record`." (flat:220). The child then checked
   containment before deleting the branch (flat:373).
5. Lint findings. The child read the linter to learn which findings gate, then
   rewrote several sentences (flat:336, flat:339-340, flat:341-352). The
   report counts only hard violations.

## Candidate lessons

1. NEW. A landing procedure that moves a branch fails while that branch is
   checked out in another worktree. Quote: "`git branch -f main HEAD` failed
   because `main` was checked out in the main worktree at that moment."
   (flat:220). The form that works is a fast-forward inside the worktree that
   holds `main`, after the cleanliness check (flat:371). No repository file
   states a landing procedure.
2. NEW. A spike record should name the run that the committed scripts match.
   Quote: "The second and third runs agree, and the third run is the one the
   committed scripts and the record describe." (flat:191). `.kb/spikes.md` §3
   names the sections a README holds and asks for no such statement.
3. NEW. A spike that closes another record's "Not verified" item edits a
   record it did not write, and the brief should settle that before the run.
   Quote: "one added sentence in `research/separate-bridges.md` whose "Not
   verified" list still called the real gateway across two bridges unmeasured"
   (flat:193), and the question asked after the fact: "Say the word if you
   would rather that record stay untouched." (flat:221).
4. NEW. "Zero hard violations" leaves linter findings of another class that
   still cost prose rewrites. The child had to read `ste-lint.py` to separate
   the two classes (flat:339-340) before it could tell whether a finding
   blocked the work. State which class gates before drafting.
5. NEW. A prompt for a spike on a shared host fixes the object names before
   the run, so two sessions cannot collide. Quote: "This host runs other
   sessions. Use names nobody else uses" (flat:75). No repository file states
   this rule.
6. ALREADY WRITTEN. The active gateway path, the client that ignores
   `OPENSHELL_LOCAL_TLS_DIR`, the quoted `lxc list` column, the Docker address
   on `ip -4 -o addr`, the ACL detach before replacement, the credential copy
   left by an early stop, and the `refused` against `timeout` distinction are
   all in `research/two-bridge-gateway.md`, Findings and Gotchas.
7. ALREADY WRITTEN. The rule that a spike concludes onto `main` with its
   record and any ADR in one commit is `.kb/spikes.md` §7.
8. PROJECT-SPECIFIC FACT. The land addresses `10.255.0.10` and `10.254.0.1/24`,
   the stand-in ports, and the OpenShell 0.1.8 version belong in the record
   that already holds them.

## What should not become a skill

- The harness calls used to watch the run (`shell_start` with a `watch` map,
  flat:276, flat:311, flat:324). They are how this session was driven, not a
  method a later session can be held to.
- The specific port numbers and addresses. They are measurements for one run.
- The sentence rewrites the linter forced (flat:341-352). Read as a lesson,
  they restate `.kb/writing-style.md` §2, which already says to write two
  sentences instead of one long one.
- "Ask before anything destructive outside your own objects" (flat:154). The
  same rule is already in the prompt's own words and in `.kb/spikes.md` §5.
