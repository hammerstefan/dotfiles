# ses_e3536c34bffey6q3CKBXR1ghqH: Research OpenShell remote gateway

## What the person asked for

The session holds one prompt, written by the spawning session
(`ses_e35403258ffeVHpL6OjWM92vaG`). No human turn appears in this transcript
(flat:2-26).

- "Research how to run an OpenShell gateway on a NON-LOOPBACK address with TLS
  and drive it from a REMOTE OpenShell CLI in a different container."
- "Context: OpenShell v0.1.8 (docs at https://docs.nvidia.com/openshell/latest/llms.txt).
  The gateway is a systemd user service. Locally it binds
  https://127.0.0.1:17670 with mutual TLS."
- "How do I make the gateway bind to a specific non-loopback address instead
  of 127.0.0.1:17670? Which config key (`bind_address` in
  `[openshell.gateway]`?) and/or which CLI flag / environment variable?"
- "What flags does it take (e.g. --server-san)? What files does it write
  (names and locations: ca.crt, tls.crt, tls.key, jwt/signing.pem,
  jwt/public.pem, jwt/kid)?"
- "Does `gateway add` OVERWRITE or DELETE an mTLS bundle that was copied in
  beforehand, or does it leave it alone?"
- "What environment variable makes the CLI and the gateway share ONE TLS
  directory? (the prior spike used OPENSHELL_LOCAL_TLS_DIR)."
- "FILE TRANSFER: how does a client move a FILE produced inside a sandbox back
  to the client machine? ... If the only path is `sandbox exec` stdout, say so
  explicitly."
- "Where the upstream is ambiguous or you cannot confirm, say "not confirmed"
  rather than guessing. Return a compact report."

## What was produced, and whether it worked

One prose report with source paths and doc quotes (flat:36-270). No file was
written and no commit was made, which matches a read-only research task. The
whole log is `webfetch` and `curl` reads against upstream (flat:273-339).

- Q1 is answered from the packaged unit verbatim, with both the
  `gateway.env` route and a systemd drop-in route, and with the precedence
  order (flat:44-110).
- Q2 is answered with the argument list, a file table, and the statement
  "**Yes** it writes a CLI CLIENT certificate (`client/tls.crt` /
  `client/tls.key`), not only server material." (flat:146).
- Q3 is answered with the bundle layout, the `metadata.json` field list, the
  exact `gateway add` command, the answer that a remote add leaves a
  pre-copied bundle alone, and two ways to register without the add
  (flat:177-255).
- Q4 is only partly readable. The resolution chain is listed (flat:261-268),
  and the transcript clip starts at flat:271.
- Not readable: the answers to Q5, Q6, Q7, and Q8. They fall inside the
  clipped region. The file-transfer answer the prompt singled out cannot be
  read from this transcript.
- Not verified in any session: the report is a reading of source and docs. No
  gateway was started and no `openshell gateway add` was run here.

The later spike confirms three of the report's claims by measurement: the
client ignores `OPENSHELL_LOCAL_TLS_DIR`, the bundle lives under
`gateways/<name>/mtls/`, and the active gateway is named one level above the
`gateways` directory (`research/two-bridge-gateway.md`, Gotchas).

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

Values the child derived and no repository file holds:

- The argument split: the flag is `--bind-address <IP>` plus `--port <PORT>`,
  and "the env var takes an **IP only**." (flat:53).
- The TOML side takes a full socket: "`pub bind_address: Option<SocketAddr>`"
  with `bind_address = "10.0.0.5:17670"` (flat:55-63).
- The instruction the child drew from that: "**Set both halves explicitly.**"
  (flat:66).
- The precedence line it relied on: "Gateway CLI flag > gateway OPENSHELL_*
  env var > TOML file > built-in default" (flat:66).
- The packaged unit's certificate step:
  `ExecStartPre=/usr/bin/openshell-gateway generate-certs --output-dir ${OPENSHELL_LOCAL_TLS_DIR} --server-san host.openshell.internal`
  (flat:79).
- The client bundle path and its three files:
  `$XDG_CONFIG_HOME/openshell/gateways/<name>/mtls/` with `ca.crt`,
  `tls.crt`, `tls.key` (flat:186-192).
- The two refusal messages it quoted: "mTLS certificates for gateway '{name}'
  were not found." (flat:209) and "Gateway '{name}' already exists. Remove it
  first with: openshell gateway remove {name}" (flat:222).

The repository has no file that states any of these. A search of
`git/monitor-agent` for `server-san` and `bind_address` returns nothing.

## Failures, their cause, and the fix

(none found). The tool log holds no `!! FAILED` line, which is unusual for a
session of this length. The child fetched the tree listing first (flat:282),
then read the files by path, so it never guessed a path that did not exist.

## Candidate lessons

1. NEW. A gateway setting split across two names needs both halves named in
   the record. The flag and `OPENSHELL_BIND_ADDRESS` take an IP, the TOML
   `bind_address` takes `IP:port`, and the file's socket is applied only when
   the flag or variable was not set. Quote: "the env var takes an **IP only**."
   (flat:53) and "the TOML socket is applied only when the flag/env was *not*
   explicitly set" (flat:66).
2. NEW. A certificate generator that owns the whole bundle turns a small SAN
   difference into a new CA for every client already issued. Quote: "a
   required SAN missing -> **regenerates the whole bundle**, i.e. a **new
   CA**" (flat:161), and "If you regenerate manually with only `--server-san
   10.0.0.5`, the next unit start sees `host.openshell.internal` missing ->
   regenerates -> your IP SAN is lost and the CA changes." (flat:163). The
   consequence for a plan is that the SAN set in the unit's `ExecStartPre`
   must not change between runs.
3. NEW. A registration subcommand can carry three different meanings by flag,
   and the wrong one is silent. Quote: "A plain `https://` endpoint with
   **neither** `--local` nor `--remote` is registered as an **edge/cloud
   gateway** (`auth_mode: "cloudflare_jwt"`) and the CLI opens a browser. **You
   must pass `--remote`.**" (flat:207). Quote for the copy rule: "For
   `--remote`, `imported_mtls_dir` is `None` and the pre-existing `mtls/` dir
   is only *checked*." (flat:218).
4. NEW. A bundle that must be moved between two containers is a credential
   with a required cleanup path. The child names the copy the generator always
   writes and the permissions it sets (flat:148). The spike then had to delete
   the copy in a trap, and a run that stops early leaves it
   (`research/two-bridge-gateway.md`, Gotchas).
5. ALREADY WRITTEN. The client ignores `OPENSHELL_LOCAL_TLS_DIR`, the bundle
   path is `gateways/<name>/mtls/`, and `active_gateway` is one level above
   `gateways`. `research/two-bridge-gateway.md`, Gotchas.
6. PROJECT-SPECIFIC FACT. The file list `ca.crt`, `client/tls.crt`,
   `client/tls.key`, `jwt/signing.pem`, `jwt/public.pem`, `jwt/kid` belongs in
   a record about the plane workshop, not in a skill.

## What should not become a skill

- The exact TOML snippet and the drop-in text (flat:57-100). They are inputs
  for one workshop definition.
- The `metadata.json` field list (flat:197). It is a format of one upstream
  version.
- The advice to hand-write `metadata.json` instead of running `gateway add`
  (flat:228). The child gives `XDG_CONFIG_HOME` as the cleaner route.
  A skill that teaches the hand-written route would teach a workaround for a
  problem a supported flag solves.
- The observation that the child answered from source without a measurement
  (flat:38). That is a property of this task. The obligation to say what was
  run and what was not is already a law in `.kb/writing-style.md` §6.
