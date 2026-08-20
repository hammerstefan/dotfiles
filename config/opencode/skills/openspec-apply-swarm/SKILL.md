---
name: openspec-apply-swarm
description: Apply tasks from an OpenSpec change in parallel using swarm decomposition, file-reservation isolation, and an orchestrator-owned tasks.md. Use when a change has 30+ tasks across multiple spec groups and parallel execution will speed up completion. Triggers on requests to "parallelize", "swarm", "distribute", or "split across agents" an OpenSpec apply.
license: MIT
compatibility: Requires openspec CLI, hive beads, swarmmail file reservations, and Task tool subagent support.
metadata:
  author: openspec
  version: "1.0"
  generatedBy: "manual"
---

# Skill: openspec-apply-swarm

Apply tasks from an OpenSpec change in parallel using swarm decomposition, file-reservation isolation, and an orchestrator-owned `tasks.md`.

**Input**: Optionally specify a change name. If omitted, infer from context or auto-select the only active change. If ambiguous, list and prompt.

This skill is a strict superset of `openspec-apply-change`: every guarantee in that skill (state machine handling, context-file reading, pause-on-blocker semantics) still applies. The additions are:

- **Decomposition**: the 119-task flat list becomes an epic of ~10 group-level subtasks, one per `## N.` heading in `tasks.md`.
- **Isolation**: file reservations (not worktrees) prevent the `db.py` / `handlers/jira_create/__init__.py` collision that bites naïve parallelism.
- **Single writer for `tasks.md`**: only the orchestrator flips checkboxes. Subtasks report which task IDs they finished; the orchestrator updates the file in a single edit.
- **Per-wave verification**: §8 (lint + typecheck + test) runs after every wave, not just at the end. Catches contract drift early.

---

## Steps

### 1. Select the change and pre-flight

**Source of truth for swarm health: `swarm doctor`, NOT `swarm_init`.**

`swarm_init` reports false-positive "degraded" warnings ("issue tracking", "file reservations", "agent communication") that the actual `swarm doctor` check shows are healthy. Always run `swarm doctor` first; if it says "All required dependencies installed", proceed regardless of `swarm_init` warnings.

Common gotchas that `swarm_init` reports but `swarm doctor` clears:
- `beads` not available — the swarm plugin's old name for HIVE; ignore
- `agent-mail` not available — deprecated, replaced by `swarm-mail` (embedded, always works)
- `semantic-memory` / `cass` not available — optional features for cross-session agent history, not required for a single-session apply

```bash
# Always: confirm health before doing anything
swarm doctor
```

If you need cross-session persistence (apply spans > 1 session or you want hive cells to survive a session restart):

```bash
# Start HIVE daemon (idempotent, port 4483)
nohup swarm serve > ~/.config/swarm-tools/logs/hive.log 2>&1 &
```

Then proceed:

```bash
openspec status --change "<name>" --json
openspec instructions apply --change "<name>" --json
```

Parse the JSON. Confirm:
- `state` is `ready` (not `blocked` or `all_done`)
- `schemaName` is one you know how to partition (currently `spec-driven`)
- `contextFiles` exists for proposal / specs / design / tasks

If `state` is `blocked`, abort and suggest `openspec-continue-change`. If `all_done`, abort and suggest `openspec-archive-change`.

Initialize the swarm session:

```python
swarm_init(project_path="<cwd>", isolation="reservation")
swarmmail_init(project_path="<cwd>", agent_name="orchestrator",
               task_description="Apply <name> via swarm")
```

**Always announce**: `Using change: <name> (schema: <schemaName>). Override with /opsx-apply-swarm <other>.`

### 2. Derive the partition

Parse `tasks.md` to extract `## N. <Group>` headings. For each group, collect its checkbox lines and scan the description text for file paths matching `src/...` or `tests/...` (regex `[\w/._-]+\.(py|md|yaml|json)` near the strings `src/` or `tests/`).

```python
# pseudocode — implement inline, not as a separate script
groups = parse_h2_headings(tasks_md_path)
for g in groups:
    g.files = extract_file_paths(g.task_text)
    g.task_ids = [t.id for t in tasks if t.id in g.id_range]
```

Build a default DAG by numeric ordering (`§1` before `§1a` before `§2` …). Numeric lex order is a safe conservative default because the human who wrote the spec already encoded dependencies in the heading numbers.

**Always show the partition to the orchestrator before proceeding** — a confirmation gate. The orchestrator can override:
- Add or remove groups
- Edit the file list per group
- Add cross-group dependencies (`§3a` actually needs `§6` not just `§1b`)
- Rename a group

Use the `question` tool with a multi-option prompt if any of these are non-obvious. Do not skip this gate; an unverified partition causes silent merge conflicts.

### 3. Create the epic and subtask beads

```python
hive_create_epic(
    epic_title="Apply <name> via swarm",
    epic_description="<link to proposal.md, design.md, the derived partition table, and the DAG>",
    subtasks=[{
        "title": g.heading,
        "priority": g.priority,        # 0 = foundation, 3 = final gate
        "files": g.files,
        # parent_id is set per subtask below to encode the DAG
    } for g in groups],
)
```

Then walk the derived DAG and set `parent_id` on each subtask so `hive_ready` returns them in dependency order. For `spec-driven`, a common encoding:

```
§1           (no parent)
§1a, §1b     (parent: §1)
§2, §3a, §4  (parent: §1a/§1b/§1b respectively)
§3           (parent: §2)
§5           (parent: §1a, §2, §4)
§6           (parent: §1b, §4, §5)
§9, §10      (parent: §6)
§8           (parent: §9, §10)  # serial gate
```

### 4. Get a strategy (advisory only)

```python
swarm_select_strategy(task="apply <name>", codebase_context="<partition summary>")
```

Expected: `feature-based` (groups are feature boundaries, not file boundaries). If the strategy returns `risk-based` or `file-based`, treat as a hint that the partition is wrong and revisit step 2.

### 5. Dispatch loop

**Per-group reservation strategy (decision table):**

| Group's file ownership | Reservation | Why |
|---|---|---|
| Disjoint file set vs all other groups in this wave | `swarmmail_reserve(paths, exclusive=true)` | Safe, no contention |
| Shares a file with another group in the same wave (function-level partition) | **No file reservation** | `swarmmail_reserve` is file-level; two groups can't both hold exclusive on the same file. Rely on subtask prompt to enforce function-level scope, then verify with `git diff` after the wave. |
| Same files as a group in a different wave | Reservation released before that wave starts | No contention by definition |
| New file creation (e.g., `learning/rules.py`) | Reserve the path before dispatch | Prevents two groups from both creating the same file |

If the partition has a function-level collision that worries you, **serialize the colliding groups** (one wave instead of parallel) and lose the parallelism. Function-level trust is a speedup; serialization is a safety net.

**Per-group subagent type (decision table):**

| Group character | Recommended subagent_type | Why |
|---|---|---|
| Pure DB schema / methods on existing file | `general` | Default; no specialist edge |
| New module in `learning/` (rules, rag) | `mm3` | Code-tuned for the codebase |
| Hot-file integration (`_store_extracted_fields` modification) | `glm` | Strong on edge cases, defensive logic |
| Pure-Python algorithm with explicit numerical constraints (cosine_similarity) | `deepseek` | Stronger reasoning for the constraint set |
| Tests (per-spec, edge cases) | `glm` | Good at enumeration and edge cases |
| Mechanical additions (tracing spans, boilerplate) | `qwen` | Fast for well-specified work |
| Large group (10+ tasks) on cross-file integration | `glm` or `deepseek` | Reasoning matters more than speed |

**Concurrency model (how to actually run workers in parallel):**

- Within a wave, dispatch N workers in a SINGLE message with N `Task` tool calls (foreground). The system runs them concurrently.
- Across waves, wait for all workers in the previous wave to complete before dispatching the next. Do NOT pipeline waves.
- For waves with 1 worker, foreground is fine.
- Background mode (`background=true`) is for work you don't need to wait on; you get a notification when done. Not needed here because the orchestrator does closeout after each wave.

**Dispatch loop (concrete):**

```python
while not all_done:
    ready = hive_ready()  # unblocked, highest-priority subtask

    if ready is None and in_flight > 0:
        # Wait for an in-flight subtask to finish
        wait_for_swarm_complete_or_progress()
        continue

    if ready is None and in_flight == 0:
        break  # nothing to do, nothing running → done or stuck

    # Reserve files for this group (skip if function-level partition)
    if not function_level_partition(ready):
        swarmmail_reserve(
            paths=ready.files,
            ttl_seconds=3600,
            reason=f"<group-name> applying — exclusive edit",
        )

    # Build the subtask prompt
    prompt = swarm_subtask_prompt(
        agent_name=f"worker-<group-slug>",
        bead_id=ready.id,
        epic_id=epic.id,
        subtask_title=ready.title,
        subtask_description=read_swarm_spawn_subtask_template(ready),
        files=ready.files,
        shared_context=build_shared_context(ready, partition_table, dag),
    )

    # Spawn the subtask via the Task tool
    Task(subagent_type=<chosen above>, prompt=prompt)

    in_flight += 1
```

The subtask template must include **all** of these non-negotiables:

```
You are a worker subtask in a swarm that is applying the OpenSpec change "<name>".

Your group: <group-name>
Reserved files (you may edit ONLY these):
  <one per line, copied from the reservation>

You MUST NOT:
  - Edit openspec/changes/<name>/tasks.md (the orchestrator owns that file)
  - Edit any file outside the reservation list
  - Create new files without sending a message to "orchestrator" with importance=blocker
  - Flip checkboxes in tasks.md; report finished task IDs instead

Read these context files once at the start:
  <contextFiles from openspec instructions apply --json>

Implement the tasks in your group's task list. The tasks file lives at
openspec/changes/<name>/tasks.md; the relevant section is delimited by the
heading <group-name>. Use the IDs from `openspec instructions apply --json`
when reporting back.

When done, call swarm_complete(bead_id=<your-id>, files_touched=[...]).
When blocked, call swarm_progress(status=blocked, message=...).
```

### 6. On subtask completion

When a subtask reports `done`:

1. **Verify with the source of truth** — re-run `openspec instructions apply --change <name> --json` and confirm `progress.complete` increased by the expected count. If it didn't, the subtask reported success but didn't actually edit anything → mark as failed and retry.
2. **Release reservations** — `swarmmail_release(paths=<reserved-for-this-group>)`.
3. **Flip the checkboxes** — single edit to `tasks.md`, toggling `[ ]` → `[x]` for each completed task ID. This is the only time the orchestrator writes to that file.
4. **Run the per-wave verification gate** (see step 7).
5. **Mark the subtask bead closed** — `hive_close(id=<subtask-id>, reason="<N> tasks complete")`.
6. **Loop** to step 5.

When a subtask reports `blocked`:

1. Hold the in-flight count; do not dispatch new groups.
2. Read the blocker's message (`swarmmail_read_message`).
3. Show the user the blocker with `question` if it requires a design decision.
4. On resolution, send guidance back via `swarmmail_send` to the blocked worker and let it resume.

### 7. Per-wave verification gate

After every wave (not just at the end), run the verification gate. For a Python/uv project, the **concrete, working command** is:

```python
result = bash(command="""
  uv run ruff check src/ &&
  uv run pyright src/ &&
  uv run --env-file .test-env pytest --ignore=tests/e2e -q
""", description="Run lint+typecheck+tests for wave <N>")
```

**Notes on the command:**
- **`--ignore=tests/e2e`** is mandatory for projects with E2E tests that require external infrastructure (real Mattermost / real LLM). The `tests/e2e/` directory typically has tests that try to connect to a real server and will fail with `httpx.ConnectError: Connection refused` or similar. Without `--ignore`, the wave gate always fails on E2E setup errors unrelated to the code.
- **`-q`** is preferred over `-x` for waves with 50+ tests: `-x` stops on first failure which can hide the failure pattern across the wave. Use `-x` only when you want to debug a specific failure.

**Pre-existing test failure handling (CRITICAL):**

If the verification gate fails on a test that is **unrelated to the wave's work** (e.g., a test in a file the wave didn't touch, or a test for a function that didn't exist before this change):

1. **Do NOT roll back the wave.** The wave is fine; the failure pre-exists it.
2. **File a bug cell** under the epic:
   ```python
   hive_create(
       title="Pre-existing test failure: <test_name>",
       type="bug",
       priority=2,
       description="Discovered during W<N> verification gate (<date>). Pre-exists W<N> work; unrelated to <files-touched-by-wave>.\n\nFailing test: <test_id>\n  <assertion>\n\n<one-paragraph root cause hypothesis>\n\nReproduce: <pytest command>\n\nDisposition: deferred to a later wave if the function is touched, or a standalone fix afterwards.",
       parent_id=epic_id,
   )
   ```
3. **Continue** the wave. The pre-existing failure is now tracked; the wave is green for its actual scope.

If the verification gate fails on a test that **is** related to the wave's work, treat it as a real regression: roll back the wave, send `needs_changes` review to the offending worker, re-dispatch only that group. Do not advance the DAG.

**Pre-existing failures discovered in W1 (current spec):**
- `tests/test_jira_recovery.py::TestExtractCandidateIssues::test_bare_issue_dict` — pre-exists W1 work, fails on `_extract_candidate_issues()`. Not in scope; filed as bug cell.

If a wave passes cleanly (zero failures, including pre-existing), the next wave's gate is also run cleanly. If a pre-existing failure is present, accept it and proceed.

### 8. Optional adversarial review (between major waves)

For changes that touch a hot file (in this codebase, `handlers/jira_create/__init__.py`), call `swarm_adversarial_review` after the group that last edited that file. This is the VDD pattern — fresh-context hostile review, not a self-review.

### 9. Mark the epic complete

When `openspec instructions apply --change <name> --json` returns `state: "all_done"`:

```python
hive_close(id=epic.id, reason="All N groups complete, verification gate passed")
swarm_complete(bead_id=epic.id, ...)
```

Then suggest `openspec-archive-change` to the user (this skill does not archive — that's a separate workflow).

---

## Common pitfalls (lessons from real runs)

1. **`swarm_init` "degraded" warnings are false positives.** The plugin's init logic is out of sync with its own CLI. Always run `swarm doctor` for ground truth. The "degraded" features (issue tracking, file reservations, agent communication) actually work in embedded mode.

2. **`@joelhooks/beads` is a wrong package name.** `swarm_init` recommends `npm i -g @joelhooks/beads` but that package does not exist. The actual package is `@beads/bd` (npm) or `brew install beads` (Homebrew). For swarm issue tracking, you don't need either — HIVE is part of the `opencode-swarm-plugin` package and works in embedded mode.

3. **`agent-mail serve` is deprecated.** Don't try to start it. The replacement (`swarm-mail`) is embedded and always works.

4. **File reservations are file-level, not function-level.** When two groups in the same wave need to edit the same file at different functions, file-level exclusive reservations conflict. Either (a) serialize the groups, or (b) skip the file reservation and rely on subtask prompt discipline + post-wave `git diff` verification.

5. **`SQLITE_BUSY` from `swarmmail_health` is a false positive when `swarm serve` is running.** The HIVE daemon holds the SQLite file open; the embedded tools still work via WAL mode. Don't tear down the daemon because of this warning.

6. **Workers auto-close cells via `swarm_complete`.** The orchestrator does NOT need to call `hive_close` for subtasks. Only the epic closure at the end is manual.

7. **Workers do NOT flip `tasks.md` checkboxes.** They report finished task IDs in their `swarm_complete` summary. The orchestrator flips the boxes in a single edit. Multiple writers to `tasks.md` race and lose state.

8. **`hive_ready` returns by priority, ignoring wave structure.** All beads have `parent_id=epic_id` and no explicit `dependencies`, so the system treats all 12 as ready. The orchestrator (you) MUST enforce wave order explicitly — do not trust `hive_ready` to dispatch in DAG order.

9. **Subagent prompts must enumerate exact function names.** Saying "edit the handler" is too vague; the worker will over-edit. Say "edit ONLY the 4 call sites of `upsert_conversation_field` at lines X, Y, Z" with explicit function names. Verbose prompts prevent scope creep.

10. **`swarm_subtask_prompt` generates the full prompt for you.** Don't hand-write worker prompts. Pass `bead_id`, `epic_id`, `title`, `description`, `files`, `shared_context` — the tool returns the complete prompt verbatim. Use the result as the `prompt=` arg to `Task(...)`.

11. **Pre-existing test failures are common in legacy codebases.** Expect at least 1-2 unrelated test failures on any non-trivial codebase. File them as bug cells, do not roll back the wave. The wave's success is judged by what IT changed, not the whole test suite.

12. **E2E tests will fail without infrastructure.** Always `--ignore=tests/e2e` in the verification gate unless you're running the E2E infrastructure (Podman + real Mattermost + real LLM).

13. **`swarm_complete` may report success before the cell is actually closed.** Always verify with `hive_query(id=bead_id)` after the worker returns. The cell status should be `closed`.

14. **Don't trust the worker's self-report alone.** Verify the diff: `git diff --stat` should show changes only in the reserved files. If a worker edited `db.py` for tasks §2 didn't ask for, that's a scope violation. Send `needs_changes` review and re-dispatch.

15. **The pre-flight question gate is not optional.** Pause on partition ambiguity. A wrong partition (e.g., overlapping file ownership with no reservation) produces silent corruption that the verification gate may not catch.

16. **`swarm_complete` requires `start_time` (Unix epoch ms) — NOT in the plugin's default schema.** The OpenCode swarm plugin's TypeScript wrapper at `~/.config/opencode/plugin/swarm.ts` declares a `swarm_complete` schema missing the `start_time` parameter that the actual `swarm` CLI requires. Workers that follow the plugin schema get rejected with `"Missing required parameters: start_time"` and the cell never closes. **Fix at two levels**:
    - **Patch the plugin** (one-time): add `start_time: tool.schema.number().describe("REQUIRED: task start time in Unix epoch ms...")` to the `swarm_complete` definition in `~/.config/opencode/plugin/swarm.ts`. Reload OpenCode.
    - **Patch the worker prompt** (per-dispatch): the `swarm_subtask_prompt` does NOT include `start_time` in the example. Add a section to the worker prompt:
      ```
      ## CRITICAL: swarm_complete requires start_time
      Capture at task start: import time; start_time = int(time.time() * 1000)
      Pass to swarm_complete at task end.
      ```
    - **Fallback if neither fix is applied**: have the worker NOT call `swarm_complete`. Instead, have it report a summary. The orchestrator (you) calls `swarm_complete` on its behalf with `start_time = int(time.time() * 1000)` at the time of the worker's first progress report (approximation, but works).

---

## Critical rules (encode these as project-level AGENTS.md rules or risk silent corruption)

1. **The orchestrator is the only writer to `tasks.md`.** Subtasks report finished task IDs; the orchestrator flips the checkboxes in one edit. Multiple writers will race and lose state.
2. **Subtasks never touch a file outside their reservation.** If they need to, they send a `blocker` message to the orchestrator and stop. The orchestrator rebalances the partition and re-dispatches.
3. **Reservations are exclusive and time-bounded.** A reservation that expires (default 1h) is released automatically; the subtask must complete or renew before then. The orchestrator watches for expiry via `swarmmail_inbox`.
4. **§8-style verification gates are mandatory between waves.** A green wave is the contract for the next wave's starting state. Use `--ignore=tests/e2e` and handle pre-existing failures via bug cells.
5. **No silent file creation.** If a subtask needs a new file (e.g., a new module), it asks the orchestrator first. The orchestrator updates the partition table and adds the path to the next group's reservation.
6. **Numeric heading order is not the dependency graph.** It's a safe default, not a guarantee. Always confirm the DAG with the user in step 2.
7. **The orchestrator enforces wave order, not `hive_ready`.** All subtask beads are unblocked from the system's perspective; the DAG is encoded in the orchestrator's dispatch loop, not in the cell `dependencies` field.

---

## Output during execution

```
## Applying: <name> via swarm (schema: <schemaName>)

Partition: 12 groups derived from tasks.md
DAG confirmed by user at <timestamp>

Wave 1/4: dispatching §1 (DB Schema, 6 tasks)
  reserved: src/mattermost_monitor/db.py
  ✓ worker-§1 reported 6 tasks complete
  ✓ progress: 6/119 (was 0)
  ✓ verification gate passed

Wave 2/4: dispatching §1a, §1b, §2, §3a, §4 in parallel
  reserved §1a: db.py (methods), handlers/jira_create/__init__.py
  reserved §1b: db.py (training_examples)
  ...
```

## Output on completion

```
## Implementation Complete (swarm)

**Change:** <name>
**Schema:** <schemaName>
**Progress:** 119/119 tasks complete ✓
**Waves:** 4 (12 groups)
**Verification gate:** passed on wave 4
**Reservations released:** all

Ready to archive. Run /opsx-archive to finalize.
```

## Output on pause (blocker)

```
## Implementation Paused (swarm)

**Change:** <name>
**Wave:** 2/4
**Progress:** 27/119 tasks complete

### Blocker from worker-§3a
"<message>"

**Options:**
1. <resolution 1>
2. <resolution 2>
3. Other approach

What would you like to do?
```

---

## Guardrails

- **Always show the partition before dispatch.** An unverified partition is the #1 source of merge conflicts.
- **Never let a subtask write to `tasks.md`.** Single writer, full stop.
- **Always re-read state with the CLI after a subtask reports done.** Trust nothing; verify with `openspec instructions apply --json`.
- **Run the verification gate after every wave, not just at the end.** Catch contract drift early.
- **Hold dispatch on any blocked subtask.** Don't fan out further until the blocker is resolved.
- **Release reservations promptly** after a group completes. Leaked reservations block future groups.
- **Don't use worktree isolation** for this workflow. Worktrees fork `tasks.md`; you'd have to merge checkbox state across worktrees, which is unsolved.
- **Don't use `swarm_complete` to mark a subtask done before verification passes.** The tool's gate will catch this, but the orchestrator should not call it speculatively.
- **Pause on ambiguous partition decisions.** If the user can't confirm the DAG in step 2, abort — don't guess.

---

## When NOT to use this skill

- **< 30 tasks total.** The orchestration overhead exceeds the parallelism win. Use `openspec-apply-change` instead.
- **Single-file change.** No parallelism possible; reservations are pure overhead.
- **No clear `## N.` groupings in `tasks.md`.** The partition derivation depends on headings. If absent, fall back to `openspec-apply-change`.
- **The schema isn't `spec-driven`** and you don't have a custom partition logic for it. The partition derivation is hard-coded for `spec-driven` heading style.
- **The codebase has > 5% pre-existing test failure rate.** Every wave's gate will be noisy; the pre-existing failure handling will dominate. Fix the test suite first or use `openspec-apply-change` with manual gate management.

## See also

- `openspec-apply-change` — the sequential baseline this skill extends
- `openspec-archive-change` — the next step after this skill reports `all_done`
- `swarm_adversarial_review` — for VDD-style review of high-risk groups

---

## Quick reference: commands you'll actually use

```bash
# Health (do this first; ignore swarm_init warnings)
swarm doctor

# Start HIVE for cross-session persistence (optional but recommended)
nohup swarm serve > ~/.config/swarm-tools/logs/hive.log 2>&1 &

# HIVE state query
hive_query --json
hive_cells --status open
hive_cells --ready

# File reservation (orchestrator-side, exclusive)
swarmmail_reserve --paths src/foo.py --reason "W2/§1a" --ttl_seconds 1800 --exclusive
swarmmail_release --reservation_ids 5

# OpenSpec state (source of truth for tasks.md)
openspec status --change <name> --json
openspec instructions apply --change <name> --json

# Verification gate (concrete, working command)
uv run ruff check src/ && \
  uv run pyright src/ && \
  uv run --env-file .test-env pytest --ignore=tests/e2e -q

# Inbox check for blocker messages
swarmmail_inbox --limit 5
```

## Quick reference: dispatch sequence (no thinking, copy-paste)

```python
# 1. Reserve (skip for function-level partitions)
swarmmail_reserve(paths=[...], ttl_seconds=1800, exclusive=True, reason="...")

# 2. Generate prompt (always — saves writing it yourself)
prompt = swarm_subtask_prompt(
    agent_name="worker-w<N>-<group-slug>",
    bead_id=<bead-id>, epic_id=<epic-id>,
    subtask_title=<title>, subtask_description=<desc>,
    files=[...], shared_context=<ctx>,
)

# 3. Spawn worker
Task(subagent_type=<chosen>, prompt=prompt)

# 4. On completion: verify, release, flip tasks.md checkboxes, run gate
openspec instructions apply --change <name> --json   # verify progress increased
swarmmail_release(reservation_ids=[...])               # release
# (single edit to tasks.md to flip [ ] → [x] for the reported task IDs)
# (run the verification gate command from above)
# (hive_close for the subtask bead)
```
