---
description: Save review TODOs from the current session's verification report to @review-todo.md
agent: build
---

Save the outstanding review issues from the current OpenSpec verification into `./review-todo.md`, preserving the structure used by the existing file in this repo.

**Input**: Optionally specify a change name as the first argument (e.g., `/save-review-todos mcp-integration-jira-handler`). If omitted, infer from conversation context. If vague or ambiguous, prompt the user with the **question** tool to pick a change from `openspec list --json`.

---

## Context Sources

You have the full opencode session in scope. Use it in this order of preference:

1. **Verification report in conversation** — if `/opsx-verify` or `/review` was just run, its CRITICAL/WARNING/SUGGESTION output is already in context. Use that directly; do NOT re-run verification.
2. **Existing `@review-todo.md`** — read the file currently at `./review-todo.md` to learn:
   - The exact format (heading levels, ID scheme `(C1)`, `(W1)`, `(S1)`, `**DONE**` marker, **Reference**/**Resolution** blocks)
   - The change name in the H1 title
   - Which items are already marked `[x]` **DONE** (preserve them)
3. **Change artifacts** — if neither of the above is sufficient, prompt the user to run `/opsx-verify` or `/review` first

Never run `/opsx-verify` or `/review`.

---

## Steps

1. **Confirm the change scope**
   - If `$1` is provided, use it.
   - Otherwise infer from the most recent verification or from the existing `@review-todo.md` H1.
   - If still unclear, run `openspec list --json` and ask the user via the **question** tool.

2. **Collect issues**
   - From the verification output in context, group items into three buckets: `CRITICAL`, `WARNING`, `SUGGESTION`.
   - Drop items already marked DONE in the existing `@review-todo.md` only if they no longer appear in the new verification (i.e. they are truly resolved). Preserve their `**Resolution**` block as a historical record.
   - Renumber sequentially within each bucket using the existing scheme: `(C1)`, `(C2)`, …; `(W1)`, `(W2)`, …; `(S1)`, `(S2)`, … — keep IDs stable when re-saving so the file's history stays readable.

3. **Compose the file**
   - Use the format spec below verbatim.
   - Include every section (`## CRITICAL`, `## WARNING`, `## SUGGESTION`, `## Notes`) even if a section is empty — write `_None._` in that case so the structure stays consistent.
   - The `## Notes` section should capture: the source of the issues (e.g. "from `/opsx-verify` run on YYYY-MM-DD"), how to re-verify after fixes, and any pre-existing infra caveats (E2E, etc.) carried over from the prior file.

4. **Write to `./review-todo.md`**
   - Use the `write` tool to overwrite the file. The `read` of the existing file is required first if opencode's edit-safety check applies.
   - After writing, print a one-line summary: `Saved N critical / M warning / K suggestion → ./review-todo.md`.

---

## Output Format

Match the existing file's shape exactly. Do not invent new fields. Do not collapse sections.

```markdown
# Review TODOs: `<change-name>`

<one-line subtitle describing the source of these items, e.g.
"Outstanding issues from the OpenSpec verification report.">

## CRITICAL

- [ ] **(C<n>) <short title>** (`<file>:<line-range>`)
  - <one- or two-sentence description of the issue>
  - **Reference**: `<file>:<line>`, `<spec-or-design-path>:<line>`

- [x] **(C<n>) <short title>** (`<file>:<line-range>`) — **DONE**
  - <original description>
  - **Reference**: `<file>:<line>`, `<spec-or-design-path>:<line>`
  - **Resolution**:
    - <bullet describing the fix>
    - <bullet describing test coverage added>

## WARNING

<same shape, prefixed `(W<n>)`>

## SUGGESTION

<same shape, prefixed `(S<n>)`>

## Notes

- <source of the issues>
- <how to re-verify, e.g. "Re-run `uv run ruff check src/ && uv run pyright src/ && uv run --env-file .test-env pytest` after working through any of the above.">
- <any pre-existing infra caveats>
```

Code references use the `file.ext:line` form, not full markdown links. IDs are zero-padded only if the existing file padded them — match the file's prior convention.

---

## Guardrails

- **Never re-run `/opsx-verify` when the report is already in context.** Trust the session.
- **Preserve DONE items** with their `**Resolution**` block unless the issue is genuinely reopened by the new verification. Deleting resolutions erases history.
- **Stable IDs**: keep `(C2)`, `(W1)` etc. aligned with the previous file so cross-references in commits and chat stay valid. Only re-number if you are explicitly told to.
- **Empty sections are still sections**: write `_None._` rather than dropping `## CRITICAL` etc. — the structure is part of the contract.
- **No invented file paths or line numbers.** Every `file.ext:line` must come from a real `read`/`grep` hit or the verification output. If unsure, omit the reference and say so in the bullet.
- **One verification source per save.** Do not merge reports from two different changes into the same `review-todo.md`.
- **Don't touch code.** This command only writes `./review-todo.md`. Implementation work is a follow-up `/opsx-apply` (or equivalent) pass.
- **Ask before overwriting an unrelated file.** If `./review-todo.md` exists but its H1 references a different change, confirm with the user before clobbering it.
