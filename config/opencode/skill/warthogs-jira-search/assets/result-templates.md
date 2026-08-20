# Result Templates

Three templates, picked by result count. Prefer the more compact format when in doubt - the user can always ask for more detail.

## Full ticket (1 result)

When a single ticket matches, show everything that matters at a glance.

```
[**CPC-XXXX**](https://warthogs.atlassian.net/browse/CPC-XXXX) - <summary>

| Field | Value |
|---|---|
| Status | <status> |
| Priority | <priority> |
| Type | <issuetype> |
| Assignee | <assignee or "Unassigned"> |
| Reporter | <reporter> |
| Team | <team name or "—"> |
| Sprint | <sprint line or "—"> |
| Story Points | <points or "—"> |
| Created | <created date> |
| Updated | <updated date> |
| Due | <due date or "—"> |
| Components | <components or "—"> |
| Labels | <labels or "—"> |
| Fix versions | <fixVersions or "—"> |

**Description:**
<description body, plain text - if very long, summarize in 2-3 sentences and note "full description has N chars">

**Linked issues (blocks / blocked by / relates to):**
- <type> [<KEY>](https://warthogs.atlassian.net/browse/<KEY>) - <summary> (<status>) [if any]
- …

**Watchers:** <count> | **Comments:** <count>
```

Notes:
- Description text in Jira often has custom markup, mentions (`@user`), smart links, dates. Strip these for the table; keep the substance in the body.
- If `assignee IS EMPTY`, say "Unassigned" not "null".
- If `due date` is empty, say "—".
- **Sprint format**: For one active/future sprint, show `<name> (<state>, <start> → <end>)` — e.g. `i/o pulse 2026#11 (active, 2026-05-22 → 2026-06-06)`. For multiple sprints, comma-separate. For empty, "—".
- **Team**: show just the team `name` field, e.g. `cpc-ibm-oracle`. If empty, "—".
- **Story Points**: show the number, or "—" if empty.

## Moderate (2-5 results)

Show enough to differentiate without overloading.

```
Found N tickets matching "<keywords>":

| Key | Summary | Status | Sprint | Created | Priority |
|---|---|---|---|---|---|
| [CPC-XXXX](https://warthogs.atlassian.net/browse/CPC-XXXX) | <summary> | <status> | <sprint or —> | <YYYY-MM-DD> | <priority> |
| … |

Want full details on any of these? Give me a key.
```

Notes:
- 5-6 columns max. Drop priority/sprint if they make the table too wide for the terminal.
- Truncate summary to ~70 chars if needed; show the rest on hover / drill-down.
- **Sprint column** (when included): show the active/future sprint name only, e.g. `i/o pulse 2026#11`. If multiple, comma-separate. If empty, "—". Don't show sprint dates in this view — drill-down has them.
- If the user asked specifically about sprints, swap the columns: put Sprint earlier and add State (`active` / `future` / `closed`).

## Concise table (6+ results)

When there are many, just orient the user.

```
Found N tickets matching "<keywords>" (newest first):

| Key | Summary | Status | Created |
|---|---|---|---|
| [CPC-XXXX](https://warthogs.atlassian.net/browse/CPC-XXXX) | <summary> | <status> | <YYYY-MM-DD> |
| … |

Showing top N. Want full details on any? Give me a key, or ask me to filter (e.g. "only Untriaged", "just Classic", "since 2026").
```

Notes:
- 4 columns. Status is a single word ("Done", "Untriaged", "Rejected", etc.) when possible.
- Truncate summary hard at ~60 chars.
- Cap at 20 rows in the table even if there are more. Note "Showing top 20 of N - ask for more".
- Always offer next-step filters the user might want.

## Special cases

### Empty result

```
No tickets in CPC match "<keywords>" in the last 3 months.

Possible reasons:
- The work is filed under a different keyword (try a broader search)
- The work is in another project (out of scope for this skill)
- The work hasn't been filed yet
```

### Single result via ticket key

Same as "Full ticket" above, but skip the closing drill-down offer.

### Result from a discovery pass

When the result came from Tier 3 (discovery) instead of a keyword match, add a note:

> Note: some of these were matched on component (`ibm-vpc`) rather than the keyword `<keywords>`. Check the summaries to confirm relevance.
