# CPC Custom Fields

Custom field IDs in the CPC project (`CPC☁️-ENG`, project id `10003`). These IDs are stable for this Jira instance but can differ across other Atlassian instances. Always use the `key` (e.g. `customfield_10020`) in API calls.

## Field reference

| Field | Field ID | Type | Notes |
|---|---|---|---|
| **Sprint** | `customfield_10020` | array of sprint objects | From `com.pyxis.greenhopper.jira:gh-sprint`. The Jira agile/scrum sprint field. |
| **Story Points** | `customfield_10024` | number | Float field. Often empty. |
| **Team** | `customfield_10001` | team object | Atlassian team field. References a team by id/name. |
| **Acceptance Criteria** | `customfield_10614` | string (plain text) | Free-form text. |
| **Start date** | `customfield_10015` | date (YYYY-MM-DD) | When work started on the ticket. |
| **Properties** | `customfield_10615` | array of options | Multi-checkbox. Values: Security, Regression, Roadmap Item, Technical Debt. |
| **Reviewers** | `customfield_10042` | array of users | Multi-user picker. |
| **Bug Link** | `customfield_10596` | string (URL) | Link to external bug tracker (Launchpad, etc.). |
| **Vendor Access** | `customfield_10880` | array of groups | Restricts ticket visibility. |
| **Project** | `customfield_16165` | atlas-project | Cross-project linking. |

## Sprint field shape (customfield_10020)

Sprint is an **array** of objects. Most tickets have 0 or 1 sprint, but a ticket can be in multiple sprints over its lifetime.

```json
{
  "id": 33648,
  "name": "i/o pulse 2026#12",
  "state": "future",
  "boardId": 890,
  "goal": "",
  "startDate": "2026-06-08T16:54:05.041Z",
  "endDate": "2026-06-21T00:00:00.000Z"
}
```

Fields:
- `name` - human-readable name. Pattern: `<team> pulse <year>#<N>`. Examples seen: `i/o pulse 2026#11`, `workflow pulse 2026#11`, `gcp pulse 2026#12`.
- `state` - `future`, `active`, or `closed`. Most-recent sprint is usually `active` or `future`.
- `boardId` - Jira board the sprint belongs to. Different boards per team.
- `startDate` / `endDate` - ISO 8601. Two-week sprints typical.
- `goal` - free text, often empty.

## Team field shape (customfield_10001)

```json
{
  "id": "3c65dfcf-36b7-4000-ade9-0707e32f28b9",
  "name": "cpc-ibm-oracle",
  "title": "cpc-ibm-oracle",
  "avatarUrl": "",
  "isVisible": true,
  "isVerified": false,
  "isShared": true
}
```

The `name` is what users see. Examples: `cpc-ibm-oracle`, `cpc-i-o`, `cpc-workflow`, `cpc-gcp`, `cpc-aws`.

## How to fetch these fields

**In `atlassian_searchJiraIssuesUsingJql`:**

```
fields=["summary", "status", "customfield_10020", "customfield_10001", "customfield_10024"]
```

The default field set includes `summary, description, status, issuetype, priority, created` - it does NOT include custom fields. You must opt in.

**In `atlassian_getJiraIssue`:**

```
fields=["summary", "status", "customfield_10020", "customfield_10001", "customfield_10024"]
```

Same opt-in model.

## How to filter on these fields in JQL

**Sprint:**
- `Sprint = "i/o pulse 2026#11"` - exact match
- `Sprint ~ "i/o pulse"` - fuzzy (recommended; tolerates renaming)
- `Sprint IS NOT EMPTY` - any sprint
- `Sprint IS EMPTY` - no sprint
- For open sprint: combine with status filters, e.g. `Sprint = "i/o pulse 2026#11" AND statusCategory NOT IN (Done)`

**Team:**
- `Team = "cpc-ibm-oracle"` - exact
- `Team ~ "ibm"` - fuzzy

**Story Points:**
- `Story Points > 3`
- `Story Points IS EMPTY`

## How to discover new custom fields

If a field name doesn't match what you have here, or you're working in a new project:

```
atlassian_getJiraIssueTypeMetaWithFields(
  cloudId="220bceb6-6b32-4813-90eb-68d67c9445db",
  projectIdOrKey="CPC",
  issueTypeId="10013",  # Task
  maxResults=100
)
```

Look for entries with `"custom": "..."` in the schema. The `fieldId` is the custom field ID; the `name` is the display name.

## Common patterns

**Active work in a team's current sprint:**
```
project = CPC AND Sprint ~ "i/o pulse 2026#11" AND statusCategory NOT IN (Done) ORDER BY updated DESC
```

**Tickets in a team, no sprint assigned (untriaged work):**
```
project = CPC AND Team = "cpc-ibm-oracle" AND Sprint IS EMPTY
```

**Story points rollup for a team in a sprint** (you'll need to aggregate client-side):
```
project = CPC AND Sprint ~ "i/o pulse 2026#11" AND Story Points IS NOT EMPTY
```

**Acceptance criteria review** (story/feature work with ACs):
```
project = CPC AND Acceptance Criteria IS NOT EMPTY AND status = "In Review"
```

## Display formatting

When showing the Sprint field to a user, render like this:

- **Single sprint, active**: `i/o pulse 2026#11` (active, ends 2026-06-06)
- **Single sprint, future**: `i/o pulse 2026#12` (future, 2026-06-08 → 2026-06-21)
- **Multiple sprints** (rare): `i/o pulse 2026#11, i/o pulse 2026#12`
- **Empty**: `—` (not assigned to a sprint)

For Team: show just `cpc-ibm-oracle` (the `name`/`title`).
