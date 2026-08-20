# CPC Naming Conventions

Real-world drift we observed in the CPC project. The same work gets re-titled over time - the skill must handle this drift or it will miss tickets.

## Title prefix drift

The prefix on a refresh ticket changes over time. Same work, different prefix:

| Era | Prefix | Example |
|---|---|---|
| Pre-2024 | `[ibm-guest]` | `[ibm-guest] Classic image refresh for Q3 - Focal, Jammy and Noble` |
| 2024-2025 | `[ibm-guest]`, sometimes `[ibm]` | `[ibm] June 2024 Quarterly image refresh` |
| 2025 H2 | `[ibm-vpc]`, `[ibm-classic]` | `[ibm-vpc] VPC image refresh December 2025 - Jammy and Noble` |
| 2026+ | `[ibm]`, `[ibm-vpc]`, `[ibm-classic]`, or **no prefix at all** | `VPC Image Rrefresh June 2026 - Jammy, Noble, and Resolute` |

**Lesson:** Never rely on a prefix match. Use `summary ~ "<keyword>"` (fuzzy) without trying to match the prefix.

## Date format drift

Multiple formats appear in the wild for the same time period:

| Format | Example | Notes |
|---|---|---|
| Month + year | `May 2026`, `June 2025` | Most common in 2024+ |
| Quarter + year | `Q2 2025`, `Q3 2024` | Common 2024-H1 2025 |
| Year-month | `2025-06`, `202406` | Rare, sometimes in body text |
| Month only | `May`, `June` | Only in summary, when context is clear |
| ISO date | `2026-05-06` | Usually in description or comments |

For JQL date filtering, use the `created >= now("-3M")` style, not text matching on dates inside the title. Title dates are decorative; `created` is the ground truth.

## Cadence shift

The refresh cadence changed:

- **2024 - 2025 H1**: Quarterly. One ticket per quarter per platform (Classic, VPC).
- **2025 H2 onwards**: Monthly. The May 2025 → May 2026 gap includes both Q3 2025 tickets (rejected) and monthly 2026 tickets. A query for "latest" should pull from the monthly cycle.

When the user says "latest" or "recent" and the date filter is 3 months, this is fine. If the user wants "all time" or "Q3 2025", be explicit.

## Suite/version drift

The list of supported Ubuntu suites changes:

- **Pre-2024**: Focal, Jammy, Noble
- **2025**: Focal, Jammy, Noble (Focal usually removed by end of 2025)
- **2026**: Jammy, Noble, **Resolute** (added in 2026 - new LTS)

When parsing summaries, the suite list is informative but not load-bearing for the query - the JQL `summary ~ "refresh"` catches all of them.

## Status gotchas

Three statuses trip up naive queries:

1. **`Untriaged`** (id `12446`, category `To Do`)
   - Means "new ticket, not yet picked up". Often exactly what the user wants.
   - NOT the same as "Open" or "To Do" - it's its own status.
   - When the user asks for "active" or "open" work, include it.

2. **`Rejected`** (id `10416`, category `Done`)
   - The work was rejected/declined. Categorized as Done because the workflow closed it.
   - When the user says "what's been done", exclude these.
   - When the user says "show me everything", include them but mark them.

3. **`Done`** (id `10013`, category `Done`)
   - The real "finished" status. Default expectation.

**Filter recipes:**
- Truly active work: `statusCategory IN ("To Do", "In Progress")`
- Genuinely done: `status = Done` (not `statusCategory = Done` - that includes Rejected)
- All except closed-as-rejected: `status != Rejected`

## Noise patterns - filter these out

These keywords in summary will match "image refresh" but are NOT cloud image refreshes. Drop them from results:

| Pattern | What it actually is | Example |
|---|---|---|
| `aws-gadget refresh` | Snap refresh inside AWS instances | "invesitgate sysctl knobs updates for aws-gadget refresh" |
| `SSDLC ... refresh` | Threat model artifact refresh | "SSDLC - CPC AWS - Generate (or refresh) the Threat Model(s)" |
| `cpc-image-import` | GitHub Action for image publishing | (rare, but possible) |
| `refresh data` | Database or dataset refresh | varies |
| `Refresh ... page` | Documentation/web page refresh | varies |
| `refresh ... contract` | API contract refresh | varies |

**How to filter:** After collecting results, scan summaries for these substrings. If matched, drop. Better: be more specific in the initial query (`summary ~ "image refresh"` instead of `summary ~ "refresh"`).

## Typo tolerance

The actual warthogs data has typos. Examples we saw:

- `Rrefresh` (CPC-11050) - double-r typo
- `invesitgate` (CPC-8572) - swapped letters

**Always use `~` (fuzzy) not `=` (exact) on summary/description.** Fuzzy match is forgiving of these.

## Status of one specific edge case: parallel work

Sometimes a single refresh is split into a parent + subtasks. For example:

- CPC-10080 `[ibm] IBM VPC & Classic image refresh March 2026` (Done) - the parent
- CPC-10087 `[ibm] Classic Image Refresh March 2026 - Jammy and Noble` (Untriaged) - the classic subtask
- CPC-10088 `[ibm] VPC Image Refresh March 2026 - Jammy and Noble` (Untriaged) - the VPC subtask

When presenting results, the parent and children are separate tickets. Don't try to merge them - show both. The user can tell they're related from the title and date.
