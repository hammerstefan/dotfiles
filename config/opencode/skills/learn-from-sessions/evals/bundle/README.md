# Evaluation bundle: monitor-agent session extraction

This directory is the evidence for an evaluation of the `learn-from-sessions`
skill. Four lightweight `opencode-go` models run the skill on the same frozen
evidence, and a judge scores each result against `answer-key.md`.

## What was read

`monitor-agent` held 80 sessions across the main checkout
`~/git/monitor-agent` and seven worktrees. Forty-eight of them had no digest on
2026-11-14, and each got one in this refresh. Every session was exported with
`scripts/sessions` from the skill, flattened with `flatten.jq`, and digested by
one `opencode-go/deepseek-v4-pro` subagent on the flattened file alone.

## Counting

- `digests/` holds 105 digests.
- 80 of them match a session that `scripts/sessions list` returns today.
- 25 come from the 2026-11-13 run. Their sessions lived in worktrees that no
  longer exist, so a digest and its transcript are the only copies.
- Three of the 48 new digests are forks with a byte-identical conversation to
  `ses_e2a79290dffeekXpV7absQgR8u`. They say so and carry no separate lesson.

The phase handoff said "digests (80)". That count omitted the 25 digests from
deleted worktrees, which several clusters rest on. All 105 are committed.

## Files

- `digests/<session id>.md`: one digest per session.
- `clusters-v2.md`: 38 clusters. Each cluster is `kept`, `updated`, `new` or
  `retired`, and each evidence line is a quote with a session id and a line.
- `bundle.json`: the nine digests the evaluation runs on, the clusters each one
  carries, and the clusters outside the bundle.
- `answer-key.md`: per bundle digest, the required lessons, the file each should
  become, and the quote.
- `verify-quotes.py`: checks every quote in `clusters-v2.md` against the
  flattened transcript. It exits 1 on a defect. The 2026-11-14 run resolved
  99 of 99.
- `flatten.jq`: the `jq` filter that turns an export into the flattened text the
  line anchors refer to.

## Transcripts

Transcripts are not committed. They weigh 59 MB and grow with each session.
They stay at `/tmp/opencode/learn-from-sessions-eval/transcripts/`, with the
flattened files at `/tmp/opencode/learn-from-sessions-eval/flat/`. Recreate one:

```sh
scripts/sessions export <session id> --out transcripts/<session id>.json
jq -r -f flatten.jq transcripts/<session id>.json > flat/<session id>.txt
```

The 25 older transcripts are at
`/tmp/opencode/hwt-wrapup-monitor-agent/transcripts/`.

## Reproduce the quote check

```sh
python3 verify-quotes.py clusters-v2.md
```

It reads `flat/` in the current directory first, then the older run's `flat/`.
