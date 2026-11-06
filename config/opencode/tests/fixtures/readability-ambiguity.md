# RAX — WP5: Safely recover transient failures

As a platform vanguard, re-run only high-confidence transient failures within
explicit safety limits. A run is one execution of a job.

## Controls

The real execution path must not be available until global and per-job controls
exist. Implement per-job guardrails and squad-level permission.

## Implementation checklist

- CTRL-001 — Implement global and per-job kill-switch/shadow mode.
- RUN-001 — Implement the run-status polling loop.
- RUN-002 — Implement the re-kick outcome loop.
- RUN-003 — Reconstruct pending kicks after restart.
- CHECK-001 — Validate the false-positive bound.

Use the existing API. Do not change this command:

```sh
jobctl retry --job example
```
