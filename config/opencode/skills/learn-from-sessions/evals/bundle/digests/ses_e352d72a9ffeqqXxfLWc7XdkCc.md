# ses_e352d72a9ffeqqXxfLWc7XdkCc: Research OpenShell sandbox callback

## What the person asked for

The session holds one prompt, written by the spawning session
(`ses_e35403258ffeVHpL6OjWM92vaG`). No human turn appears in this transcript
(flat:4-34).

- "Research the OpenShell Docker compute driver's gateway callback endpoint."
- "The docs say: "Sandbox containers call back to the gateway over the
  OPENSHELL_GRPC_ENDPOINT address. The Docker driver substitutes
  host.openshell.internal as the host and the gateway's own bind port as the
  port". Confirm this in code."
- "CRITICAL: how does `host.openshell.internal` RESOLVE inside the
  supervisor/sandbox container? Does the Docker driver pass `--add-host
  host.openshell.internal:<ip>` when it creates the supervisor container, or
  does it rely on the workload/supervisor container's own /etc/hosts, or does
  the supervisor use `network_mode: host`?"
- "Does the driver use the gateway's actual bind address, or always the
  literal name `host.openshell.internal`?"
- "Which OpenShell release tags exist (v0.1.7, v0.1.8)? Give the exact git tag
  names"
- "The gateway's own TLS server certificate must be valid for the name the CLI
  uses (the bridge IP) AND for the name the supervisor callback uses
  (host.openshell.internal)."
- "If you cannot confirm something from upstream, say "not confirmed" rather
  than guessing. Return a compact report."

## What was produced, and whether it worked

One prose report (flat:80-311). The report rests on the two release tarballs
and on the pre-release history, read locally. Quote: "**Method:** downloaded
the full `v0.1.7` and `v0.1.8` release tarballs from GitHub, plus the
pre-`v0.1.0` history, and read the sources locally." (flat:82). No file was
written in the repository and no commit was made.

- The headline finding contradicts the premise the question was built on.
  Quote: "The doc sentence you quoted is stale for v0.1.7 and v0.1.8"
  (flat:86). The report also states the published docs still hold the old
  text.
- The report names the deletion: commit `17ce738bfb7e`, "remove gateway
  callback listener dependency (#3365)", dated 2026-09-18 (flat:88), and
  quotes the function that was deleted (flat:94-122).
- Q1 is answered: the supervisor reads `OPENSHELL_ENDPOINT`, and
  `host.openshell.internal` is not substituted into the endpoint (flat:136-181).
- Q2 is answered: the driver sets the structured `HostConfig.extra_hosts`
  field, the supervisor runs with `network_mode: "host"` by default, and the
  workload runs with `network_mode: "none"` (flat:190-311).
- Not readable: the transcript clip starts at flat:311. The answers to Q3
  through Q8 cannot be read from this file, including the two certificate
  questions the prompt marked as design constraints.
- Not verified: no container was started and no gateway was called in this
  session. Every claim comes from source text.

## Corrections the person made

(none found). The child corrected the premise instead, in the headline
quoted above (flat:84-86).

## Conventions, commands and values stated and written down nowhere

- The two route shapes it used to read a pinned tree:
  `https://api.github.com/repos/NVIDIA/OpenShell/tarball/refs/tags/v0.1.8`
  (flat:317) and, when no tarball exists for a crate,
  `https://static.crates.io/crates/rustls/rustls-0.23.46.crate` (flat:435).
- The pre-deletion commit it read the old code from: `d91b1999a0f2`
  (flat:92, flat:443).
- The env var the code writes: `pub const ENDPOINT: &str =
  "OPENSHELL_ENDPOINT"` (flat:155).
- The driver's own statement of the rule: "Explicit endpoints retain TLS
  verification and are never rewritten" (flat:171).
- The three doc errors it counted in one paragraph (flat:186). The docs name
  `OPENSHELL_GRPC_ENDPOINT`, and the code names `OPENSHELL_ENDPOINT`.

The repository has no file that states any of these. Three of them, the doc
error, the env var name, and the callback mechanism, decide how the plane and
agent workshops are configured, so they need a record.

## Failures, their cause, and the fix

Two `webfetch` calls answered 404:

- `https://docs.rs/tonic/0.14.6/src/tonic/transport/service/connector.rs.html`
  (flat:400-401).
- `https://raw.githubusercontent.com/hyperium/tonic/v0.14.6/tonic/src/transport/service/tls.rs`
  (flat:405-406).

The cause is a guessed path inside a crate layout the child had not read.
The fix was to list the tree for the tag (flat:408-409), then fetch only the
paths the listing returned, and to fall back to the crate tarball when a
source view answered 404 (flat:427-437). After the two 404s the child polled
each candidate path with `curl -sfL` before reading it (flat:413, flat:416,
flat:447).

The child also had to work around its own first mistake of vocabulary: the
prompt asked whether the driver passes `--add-host`, and the answer is that
no flag string exists. Quote: "it is the structured `extra_hosts` field."
(flat:192).

## Candidate lessons

1. NEW. When a research question is built on a quoted doc sentence, the first
   answer is whether the sentence still holds for the pinned release. Quote:
   "The doc sentence you quoted is stale for v0.1.7 and v0.1.8" (flat:86).
   The child proved it from the pinned trees and from the history, not from
   the docs page.
2. NEW. A negative grep is evidence only when the same grep is shown to hit
   on the version where the symbol exists. Quote for the negative side:
   "no matches" (flat:126) and "is 25 lines in both v0.1.7 and v0.1.8 (it was
   716 lines before the removal)" (flat:127). Quote for the positive side:
   the pre-deletion file read by commit (flat:92, flat:443).
3. NEW. A documented env var name can be wrong while the doc reads as an
   instruction. Quote: "that env var name only exists in the *dev task
   scripts* and in the docs" (flat:138). The name the code writes is
   `OPENSHELL_ENDPOINT` (flat:155).
4. NEW. A container callback that must survive a bind address needs the
   mechanism named, not a flag repeated. The driver sets the `extra_hosts`
   field, and host networking does not copy the host's `/etc/hosts` when that
   field is present. Quote: "So when the driver *does* set `extra_hosts` in
   host mode, the container gets a **fresh** `/etc/hosts`" (flat:296).
5. NEW. Read a pinned release tree, not `main`, when the question is about
   what an installed package does. The deletion the report rests on happened
   before `v0.1.0`, so a reading of `main` alone cannot show it (flat:86-92).
6. PROJECT-SPECIFIC FACT. The supervisor runs with `network_mode: "host"`,
   the workload with `network_mode: "none"`, and the callback name is an
   `/etc/hosts` alias. These belong in a record about the two workshops.

## What should not become a skill

- The tonic, rustls, and rustls-webpki reading (flat:378-437). It answers one
  question about hostname verification in the versions in `Cargo.lock`, and
  those versions move.
- The `docker_supervisor_networking` and `extra_hosts` details as a recipe.
  They are facts about OpenShell v0.1.8, and the spike that used them already
  records the effect.
- The observation that the doc page is wrong (flat:186), read as a skill
  about OpenShell docs. A later release may correct it.
