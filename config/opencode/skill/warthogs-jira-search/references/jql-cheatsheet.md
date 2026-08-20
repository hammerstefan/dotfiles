# JQL Cheatsheet for warthogs-jira-search

JQL = Jira Query Language. Used by `atlassian_searchJiraIssuesUsingJql(jql="...")`. This cheatsheet is a quick reference for the operators and functions you'll use most.

## Operators

| Operator | Meaning | Example |
|---|---|---|
| `=` | exact match | `status = "In Progress"` |
| `!=` | not equal | `status != Done` |
| `~` | fuzzy contains (case-insensitive, ignores word order) | `summary ~ "image refresh"` |
| `!~` | does not fuzzy contain | `summary !~ "test"` |
| `IN (...)` | in list | `component in (ibm, ibm-vpc)` |
| `NOT IN (...)` | not in list | `status NOT IN (Done, Closed)` |
| `AND`, `OR`, `NOT` | boolean | `status = Open AND priority = High` |
| `IS EMPTY` / `IS NOT EMPTY` | null check | `assignee IS EMPTY` |
| `WAS` | historical value | `WAS in ("In Progress")` |
| `WAS NOT` | not historically | `WAS NOT in ("Done")` |
| `CHANGED` | field changed | `status CHANGED AFTER "2026-01-01"` |

**Default to `~` (fuzzy).** It's case-insensitive and tolerates typos and word reordering. Use `=` only when you have an exact enum value (status names, exact keys, exact component names).

## Date functions

| Function | Example | Notes |
|---|---|---|
| `now()` | `created >= now()` | right now (UTC) |
| `now("-3M")` | `created >= now("-3M")` | 3 months ago. M=month, w=week, d=day, h=hour |
| `startOfMonth()` | `created >= startOfMonth()` | first day of this month |
| `startOfYear()` | `created >= startOfYear()` | Jan 1 of this year |
| `endOfMonth()` | `created <= endOfMonth()` | last day of this month |
| `endOfWeek()` | `created <= endOfWeek()` | end of this week |
| Literal date | `created >= "2026-01-01"` | ISO format YYYY-MM-DD. Always quote. |

**This skill's default date window: `created >= now("-3M")`.** Override when the user specifies a different range.

## Sorting

`ORDER BY <field> [ASC|DESC]`

- `ORDER BY created DESC` - newest first (most common, "latest")
- `ORDER BY updated DESC` - most recently touched (catches comments)
- `ORDER BY priority DESC, created DESC` - urgent first, then newest

`DESC` for "latest", `ASC` for "oldest". No comma-separated multi-field sorting in some clients - check.

## Result limits

`maxResults` parameter on `atlassian_searchJiraIssuesUsingJql`. Range 1-100. Default in the tool is 50.

- For discovery passes: use 30 (a reasonable cap)
- For "show me everything" with no date filter: use 100 and warn if you hit the cap
- For known small result sets: 20 is plenty

## Common field names

- `summary` - ticket title
- `description` - body text
- `status` - current status name (e.g. "Done", "In Progress", "Untriaged")
- `statusCategory` - high-level: "To Do" / "In Progress" / "Done"
- `priority` - "Highest", "High", "Medium", "Low", "Lowest"
- `assignee` / `reporter` - user account
- `created` / `updated` / `resolutiondate` - dates
- `duedate` - explicit due date
- `component` / `components` - Jira components (singleton vs multi - try both)
- `label` / `labels` - free-form tags
- `fixVersion` / `affectedVersion` - version tracking
- `project` - project key (always `CPC` for us)
- `type` / `issuetype` - Task, Story, Bug, Epic
- `parent` - for subtasks, the parent ticket
- `linkedIssue` - for blocked-by / blocks relationships

For exact field names available in this warthogs instance, the `getJiraIssueTypeMetaWithFields` tool gives the schema.

## Parentheses matter

`a AND b OR c` is ambiguous. Always parenthesize:

```
(status = "In Progress" OR status = "Untriaged") AND priority = "High"
```

Not:

```
status = "In Progress" OR status = "Untriaged" AND priority = "High"
```

(The second parses as `status = "In Progress" OR (status = "Untriaged" AND priority = "High")` - probably not what you want.)

## Debugging a query that returns nothing

1. Drop the date filter - is it too restrictive?
2. Drop the component filter - is the component name wrong?
3. Switch `~` to a less restrictive search
4. Run a discovery query (no keywords, just `project = CPC ORDER BY created DESC`) to see what's actually in the project
5. Check for typos in field names - `summary` not `Summary`, `created` not `Create Date`

## Useful recipes

**Active work in a project:**
`project = CPC AND statusCategory NOT IN (Done) ORDER BY updated DESC`

**Created in last N months:**
`project = CPC AND created >= now("-6M") ORDER BY created DESC`

**Unassigned and untriaged:**
`project = CPC AND assignee IS EMPTY AND status = Untriaged`

**Overdue (no resolved, has due date in past):**
`project = CPC AND duedate < now() AND resolutiondate IS EMPTY`

**Tickets I reported:**
`project = CPC AND reporter = currentUser()`

**Tickets blocking a specific ticket:**
`project = CPC AND issueFunction in linkedIssuesOf("CPC-1234", "is blocked by")`

**Active sprint work for a team:**
`project = CPC AND Sprint ~ "i/o pulse 2026#11" AND statusCategory NOT IN (Done) ORDER BY updated DESC`

**Untriaged work in a team (no sprint):**
`project = CPC AND Team = "cpc-ibm-oracle" AND Sprint IS EMPTY`

**Story points rollup for a sprint** (aggregate client-side):
`project = CPC AND Sprint ~ "i/o pulse 2026#11" AND Story Points IS NOT EMPTY`

## Custom fields

CPC's project has many custom fields (Sprint, Team, Story Points, Acceptance Criteria, etc.). For the full list of field IDs and shapes, see `references/cpc-custom-fields.md`.

Quick reference for the most useful ones:

| Field | JQL key | Notes |
|---|---|---|
| Sprint | `Sprint` | Fuzzy match name. `Sprint ~ "i/o pulse"` or `Sprint IS NOT EMPTY`. |
| Team | `Team` | `Team = "cpc-ibm-oracle"`. |
| Story Points | `Story Points` | Numeric. `Story Points > 3`. |
| Acceptance Criteria | `Acceptance Criteria` | Free text. `IS NOT EMPTY` to find tickets with ACs. |

**Note:** The underlying field IDs (`customfield_10020`, `customfield_10001`, etc.) are needed for `fields=[]` in API calls. JQL uses the friendly name (`Sprint`, `Team`, `Story Points`).
