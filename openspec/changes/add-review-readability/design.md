## Context

The council is implemented as Markdown agent and command contracts. Specialists emit a `review-json` array; the chair emits `review-council-json`; the coordinator dispatches reviewers and separately persists human-attention items. The Python writer validates a closed set of reviewer names. Existing OpenSpec capabilities cover prior-review routing, which this change preserves.

## Goals / Non-Goals

**Goals:** Review human-facing text in any file type; separate clarity defects from optional editorial suggestions; make selection, adjudication, volume limits, failure reporting, and persistence agree.

**Non-Goals:** General factual verification, comprehensive documentation audits, automatic rewrites, machine-only or generated/third-party text review, changes to approval rules, or editorial persistence as human-attention items.

## Decisions

### 1. Dedicated specialist with audience-aware scope

Use the approved `github-copilot/claude-opus-5.5` model, confirmed in the available model catalog. This is a user choice, not a performance claim. Follow existing read-only permissions, using native V2 `subagent` for the new agent's delegation denial. Keep existing compatible agent locations. Review changed text and newly introduced clarity problems for diff scopes; review current contents for path scopes. Surrounding text provides context only. Default audience is a competent developer new to the project, unless the text targets end users or another evident audience.

Use native V2 frontmatter consistently in the touched coordinator, triage, chair,
and human agents: move legacy `temperature` under `request.body` and use
`subagent` permission actions. V2 documentation warns against mixing legacy and
native fields within an agent. The running service's cached definitions showed
legacy temperatures and the native permissions list in request-body extras,
rather than enforcing the intended agent permissions. Preserve the temperature
values and permission resources while fixing the touched definitions; use fresh
configuration for evaluation.

### 2. Two structured specialist channels

Keep `review-json` unchanged for substantive findings, with IDs `RDB-1`, category `readability`, and the usual severity, confidence, evidence, and fix fields. Append exactly one `review-readability-json` object:

```json
{
  "readability_suggestions": [
    {
      "file": "docs/setup.md",
      "items": [
        {
          "id": "RDS-1",
          "line": 12,
          "original": "Safe source excerpt.",
          "problem": "Concrete readability problem.",
          "suggested_edit": "Meaning-preserving rewrite or exact structural edit."
        }
      ]
    }
  ],
  "readability_coverage": {"status": "complete", "limitations": []}
}
```

Every file is repository-relative, every line is a positive integer in the scoped source, and all text fields are non-empty and redacted where needed. IDs are unique. Up to 50 suggestions, each collection entry contains one item. Above 50, group all suggestions by file; a group retains every distinct problem with representative locations and edits. At most 200 entries (individual suggestions or file groups) are reportable. Grouping is not permission to drop distinct issues; if context/tool/output limits prevent representing a whole group, report incomplete coverage and the omitted files/problems. Once 200 entries are reached, stop and disclose remaining coverage, if any. Repeated instances of one problem can share a representative item.

`readability_coverage.status` is `complete` or `incomplete` for the specialist; `limitations` names unreviewed files, unreported locations/problems, and reasons as precisely as available. The chair adds `not_selected` and `failed` statuses. It preserves existing fields and adds these same two top-level fields to `review-council-json`. Empty lists are valid. Malformed channels are rejected independently, recorded as partial reviewer failure, and cannot invalidate successful unrelated reviewers. Raw output is always untrusted and redacted before display.

An explicit second collection avoids encoding suggestions as low-severity findings, which would incorrectly apply finding limits and could pollute verdict or persistence calculations. Keeping existing finding fields avoids breaking consumers.

### 3. Selection precedence

Normalize scope and apply exclusions first; empty scope dispatches nobody and creates no artifact. Explicit `--only` wins. Otherwise fixed modes always include readability for non-empty scopes. Auto triage inspects content, including comments, docstrings, error/help/UI strings, config/test descriptions, and agent instructions, rather than relying on extensions. Auto readability requires relevant human-facing text after exclusions; readability focus makes selection mandatory when such text exists. The low-budget cap applies to the other auto-selected specialists only. `--no-human` affects only the later human-attention pass.

### 4. Chair and human-attention separation

The chair verifies scoped source, substantive impact, real editorial value, and meaning-preserving rewrites. It rejects personal taste and scope violations. A suggestion duplicating any verified substantive root cause is dropped, even if that finding is later suppressed by severity or count limits. Editorial suggestions never affect verdict, substantive counts, or unresolved material disagreements. The chair may correct an edit only when source evidence supports it; it never invents missing facts. It records coverage failures explicitly.

The coordinator passes both channels to the chair and renders verified suggestions separately. Human review sees the full report for context but cannot convert editorial items into human-attention items. Its summary copies finding IDs/count only from `verified_findings`. Add `review-readability` to the Python writer's reviewer allowlist; preserve all persisted field names and strict unknown-field rejection. Independent `/review-human` remains a single-agent advisory workflow.

### 5. Validation

Use dependency-free Python `unittest` for the actual writer compatibility boundary: all eight reviewers, readability-only and failed-readability summaries, unchanged independent mode, and rejection of editorial fields. Use a checked-in scenario matrix for the prompt contracts and quality cases, with recorded results distinguishing static checks from live model behavior. Validate OpenSpec and JSON examples. Council review itself remains read-only and cannot execute tests.

## Risks / Trade-offs

- Extra model cost in fast/low-budget reviews → explicitly accepted in the plan; machine-only auto scopes skip readability.
- Editorial preferences masquerading as defects → separate channels, impact requirements, and independent chair verification.
- Large editorial outputs exceed context → grouping and 200-entry cap, plus explicit incomplete coverage at every stage.
- New reviewer rejected by persistence → update and regression-test the closed reviewer set only.
- Prompt compliance is probabilistic → record behavior-evaluation limits honestly; static checks prove structure, not review quality.

## Migration Plan

Ship agent, coordinator, triage, chair, command/template, and writer allowlist together. Existing consumers read named finding fields; none consumes a closed chair-result schema. Roll back these changes together if needed; existing human-attention artifacts require no migration.

## Open Questions

None for implementation. Live model evaluation availability will be recorded during validation.
