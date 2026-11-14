# ses_e33bdc7daffebNv7yFSoh2BFA8: Research Workshop definition and lifecycle (ticket #4)

## What the person asked for

The session holds one prompt. It was written by the spawning session
(`ses_e33d0c7c5ffejcYl5L4FlzKPPv`), not by the human, and no human turn appears
in this transcript (flat:3-24).

- "TICKET: issue #4 "Research the Workshop definition, lifecycle, and secret
  capabilities", label wayfinder:research, child of map issue #1" (flat:6).
- "LOCAL FIRST-HAND EVIDENCE: the `workshop` CLI is installed on this host. Run
  only help and read-only commands: `workshop --help`, and `--help` on every
  subcommand you discover ... NEVER run launch, refresh, remove, or any mutating
  command, and never exec into a workshop." (flat:12)
- "what a workshop definition can express (packages, files, services, users,
  env, and everything else the schema allows, with the exact keys)" (flat:14)
- "whether Workshop validates unknown definition fields strictly (requirements
  001 FR-014 forbids declaring the fence in the definition)" (flat:14)
- "mark CLI help text evidence, upstream docs, and local spike evidence
  separately" (flat:16)
- "Then: gh issue close 4 ... Do NOT edit issue #1 (the map owner appends the
  decision pointer)." (flat:20)
- "FINAL REPLY to me: ... any fact you found that contradicts the repo's records
  in adr/ or requirements/." (flat:24)

## What was produced, and whether it worked

- Branch `research/workshop-definition-and-lifecycle`, commit `51da3cc`,
  "docs: research workshop lifecycle capabilities", holding only
  `research/workshop-definition-and-lifecycle.md` on top of `main` (flat:99).
  The file is not on `main` today.
- The branch was first built on the wrong base and then rebased:
  "My branch accidentally inherited the concurrent ticket's commit because it was
  checked out in this shared working tree. I'll rebase my branch onto main so it
  carries only my research file." (flat:88, the commands at flat:200).
- Resolution comment posted and #4 closed as completed (flat:203-204). One trail
  entry (flat:205).
- The verdict, as the agent reported it: a definition expresses `name`, `base`,
  `runtime`, `sdks`, `connections` and `actions` and no more, and the daemon
  rejects an unknown field. The lifecycle commands are `launch`, `refresh`,
  `restore`, `start`, `stop` and `remove`. Five SDK hooks re-apply state at the
  first three, and "no hook fires at `start`, `stop`, or `remove` and no event
  reaches the host" (flat:101). The secret interface declares a keyring lookup,
  the operator connects the plug by hand, and a process reads the value with
  `workshopctl get-secret <SDK>.<PLUG>` (flat:101).
- Verified first hand: `workshop` 0.9.9 from the CLI (flat:38, flat:123). The
  schema's `"additionalProperties": false` was read from the schema file, and the
  agent then read the parser to confirm the rejection (flat:48, flat:68-70,
  flat:182).
- Not verified: no workshop was launched, refreshed or removed. The refresh
  behaviour for an externally re-pointed NIC is marked unverified for 0.9.9
  (flat:103).

## Corrections the person made

(none found). No human turn appears. The agent corrected its own artifact before
publishing: "My branch accidentally inherited the concurrent ticket's commit"
(flat:88).

## Conventions, commands and values stated and written down nowhere

- The base check the agent ran before pushing:
  `git merge-base --is-ancestor main <branch>` and
  `git diff --name-only main HEAD` (flat:198, flat:200). Its own reading of the
  result: "branch is on top of current main" or "branch is behind main".
- The `workshop` CLI surface it enumerated, all with `--help` only: `init`,
  `launch`, `refresh`, `remove`, `restore`, `start`, `stop`, `info`, `actions`,
  `run`, `changes`, `tasks`, `connect`, `connections`, `disconnect`, `remount`,
  `exec`, `shell`, `warnings`, `okay`, `sketches`, `sketch-sdk`, `list`
  (flat:124-146).
- "no `secret` subcommand exists in the CLI" (flat:40). The secret value is read
  by `workshopctl get-secret`.
- The source path that carries the strict parse:
  `internal/yamlutil/yaml.go` (`UnmarshalStrict`), after a search across the
  repository (flat:178-182).
- Two upstream tensions the agent recorded rather than resolved: the
  runtime-behavior page says refresh "preserves LXD container identity and
  networking", which contradicts the measured refresh behaviour, and the
  definition reference page omits `runtime` from its field table while the schema
  and the CLI include it (flat:103).
- The operational note it passed to the next session: "The next session in this
  shared clone should confirm which branch is checked out before committing."
  (flat:105)

## Failures, their cause, and the fix

- `gh issue view 4` and `gh issue view 1` answered the Projects-classic GraphQL
  deprecation. Cause: the default template of `gh issue view` on this host. Fix:
  `gh api repos/<owner>/<repo>/issues/<n> --jq ...` (flat:28, flat:109-110).
- The research branch carried another session's commit. Cause: the shared working
  tree had the sibling ticket's branch checked out when
  `git checkout -b research/workshop-definition-and-lifecycle` ran (flat:191).
  Fix: `git rebase --onto main 66b94e9 research/workshop-definition-and-lifecycle`,
  then a check that the branch holds only its own file, then the push
  (flat:199-201).
- No `!! FAILED` line appears in this session's tool log.

## Candidate lessons

1. NEW. Before pushing a branch made in a shared clone, prove that `main` is an
   ancestor and that the branch holds only its own files. The check is
   `git merge-base --is-ancestor main <branch>` plus
   `git diff --name-only main HEAD`, and the repair is
   `git rebase --onto main <foreign-commit> <branch>`. Quotes: "My branch
   accidentally inherited the concurrent ticket's commit because it was checked
   out in this shared working tree." (flat:88) and "The next session in this
   shared clone should confirm which branch is checked out before committing."
   (flat:105).
2. NEW. A documented schema claim about strict parsing is confirmed in the parser
   before it carries a requirement. Quote: "One verification remains: that the
   implementation really rejects unknown fields, not just the documented schema.
   Let me check the source." (flat:68). The requirement premise it carried is
   FR-014.
3. NEW. Two upstream statements that disagree with each other are both recorded,
   with the measured one named as the one that stands. Quote: "The upstream claim
   "refresh preserves networking" needs reconciling with the local spike
   evidence." (flat:60).
4. NEW. `gh issue view <n>` without `--json` fails on this host with a
   Projects-classic GraphQL deprecation, so the issue is read with `gh api`.
   Quote: "The `gh issue view` template fails on a deprecation error. I'll use
   the API instead." (flat:28).
5. ALREADY WRITTEN. No Workshop hook fires at `start`, `stop` or `remove`, and no
   lifecycle event reaches the host, so the fence needs a host wrapper around the
   lifecycle commands. `adr/0001-hermes-runs-in-a-fenced-agent-workshop-and-a-plane-workshop-proxy-mediates-its-web-egress.md`,
   Decision and Consequences.
6. ALREADY WRITTEN. A definition rejects an unknown field, so no network setting
   can be declared in one. `adr/0001`, Context, and `.kb/agent-workshop.md`.
7. PROJECT-SPECIFIC FACT. The six definition fields and the hook stages. The
   repository holds the shapes it uses under `agent/.workshop/` and
   `plane/.workshop/` and describes them in `.kb/agent-workshop.md`, and it states
   no list of the six fields.
8. PROJECT-SPECIFIC FACT. The secret read is `workshopctl get-secret
   <SDK>.<PLUG>`, the operator connects the plug by hand, and a `restore` drops
   the connection while a `refresh` keeps it. `.kb/agent-workshop.md` now states
   the connect commands and the refresh and restore behaviour.
9. PROJECT-SPECIFIC FACT. The CLI is 0.9.9 and has no `secret` subcommand. A
   version reading belongs in a record, and it dates.

## What should not become a skill

- The twenty-three `--help` calls (flat:124-146). They are how one session
  enumerated one CLI version.
- The `UnmarshalStrict` function name and the file path (flat:182). It is a fact
  about one Go repository.
- The strict-schema and hook findings as new rules. `adr/0001` already carries
  them as the reason the fence lives on the host.
- "run only help and read-only commands" (flat:12). It is the rule of one
  dispatch, and `.kb/spikes.md` §5 already forbids an unrequested mutating run.
