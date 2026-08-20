---
name: warthogs-jira-search
description: Search and look up Jira tickets in the Canonical warthogs.atlassian.net instance, scoped to the CPC project (CPC☁️-ENG). Use this skill whenever the user asks to find, look up, list, search, or check the status of Jira tickets at Canonical - especially for cloud image refreshes, IBM/AWS/Azure/GCP cloud work, or any CPC ticket. Trigger on phrases like "find jira tickets", "search jira for", "latest jira tickets for X", "look up CPC-1234", "what's the status of Y", "show me what's in our sprint", or any request mentioning a CPC ticket key. Read-only - does not create, edit, or transition tickets.
---

# warthogs-jira-search

Search the CPC project on warthogs.atlassian.net. Read-only. Returns ticket keys, summaries, status, and (when needed) full details.

## When to trigger

- User mentions a CPC ticket key (e.g. `CPC-11050`, `CPC-7627`) → look it up directly
- User wants to find tickets on a topic ("ibm guest image refreshes", "aws image refresh", "vpc refresh")
- User asks for status / "what's the latest" / "show me recent"
- User mentions Jira + Canonical / warthogs / cloud-images / any cloud (ibm, aws, azure, gcp)
- User asks about "my team", "team tickets", "cpc-ibm-oracle" → search for team `cpc-ibm-oracle`

Do **not** trigger for: creating tickets, transitioning status, comments, or non-CPC projects (PEI, PEL, PEK, CPCCVE, etc. - those are out of scope for v1).

## Connection constants

These are stable for the warthogs instance - hardcode them.

- cloudId: `220bceb6-6b32-4813-90eb-68d67c9445db`
- Base URL: `https://warthogs.atlassian.net`
- Project: `CPC` (id `10003`, name `CPC☁️-ENG`)
- Default project filter: always `project = CPC` unless user explicitly asks about another project (politely redirect if so)

Always use the `atlassian_*` MCP tools - never call the Jira REST API directly.

## Workflow

### Step 1: Parse the request

Extract from the user's message:

- **Ticket key** - matches `CPC-\d+`. If present, go to Step 2A.
- **Topic keywords** - 1-3 words. "image refresh", "vpc refresh", "kernel", "fips"
- **Target cloud** - ibm / aws / azure / gcp / none / multi
- **Team flag** - "my team", "team tickets", "cpc-ibm-oracle" → go to Step 2C
- **Date hint** - "latest", "this year", "Q3 2025", "May 2026", "since 2024", or absent
- **Status hint** - "open", "untriaged", "done", "in progress", or absent

### Step 2A: Ticket key present

If the user gave a specific key, fetch it directly with custom fields:

```
atlassian_getJiraIssue(
  cloudId="220bceb6-6b32-4813-90eb-68d67c9445db",
  issueIdOrKey="CPC-11050",
  fields=["summary", "status", "priority", "issuetype", "assignee", "reporter",
          "created", "updated", "duedate", "components", "labels", "fixVersions",
          "description", "issuelinks", "customfield_10020", "customfield_10001",
          "customfield_10024", "customfield_10614"]
)
```

The custom fields are: Sprint (`customfield_10020`), Team (`customfield_10001`), Story Points (`customfield_10024`), Acceptance Criteria (`customfield_10614`). See `references/cpc-custom-fields.md` for the full mapping.

Use the **full ticket** output template from `assets/result-templates.md`. Stop here - do not run any other queries.

### Step 2B: Topic search

Otherwise, build a parallel JQL plan and fire it.

**Default date window**: 3 months back from today. Override only if the user specified a date or said "latest" / "recent" (then use 3 months) or "this year" (then `>= startOfYear()`) or "all time" (then no date filter).

**JQL tiers to run in parallel** (use `atlassian_searchJiraIssuesUsingJql`):

- **Tier 1 - Narrow** (when a cloud was identified):
  `project = CPC AND component in (<cloud-components>) AND (summary ~ "<kw>" OR description ~ "<kw>") AND created >= "<3mo-ago>" ORDER BY created DESC`

  Look up `<cloud-components>` from `references/cpc-components.md`.

- **Tier 2 - Medium** (no cloud or cloud unknown):
  `project = CPC AND (summary ~ "<kw>" OR description ~ "<kw>") AND created >= "<3mo-ago>" ORDER BY created DESC`

- **Tier 3 - Discovery** (only if Tier 1 + Tier 2 return <3 results, or cloud was identified and Tier 1 was empty):
  `project = CPC AND component in (<cloud-components>) ORDER BY created DESC` (top 30)

  This catches drift like our CPC-11050 case where the title dropped the `[ibm-guest]` prefix.

Fire all applicable tiers in **one message, parallel tool calls**. Then:
- Union the results by key
- Dedupe
- **Post-filter noise** - drop unrelated refreshes (see `references/cpc-naming-conventions.md` § noise patterns). E.g. `aws-gadget` snap refresh, `SSDLC` threat-model refresh, `cpc-image-import` GitHub Action refresh.

### Step 2C: Team search

If the user asks about "my team", "team tickets", "cpc-ibm-oracle", or similar, search for tickets assigned to team `cpc-ibm-oracle`:

```
project = CPC AND customfield_10001 = "cpc-ibm-oracle" ORDER BY created DESC
```

Use `customfield_10001` for the Team field. Apply the same date window as Step 2B unless the user specifies otherwise. Use the Moderate (2-5 results) or Concise table (6+ results) template based on result count.

### Step 3: Format output

Pick the template based on result count:

| Count | Template | File |
|---|---|---|
| 1 | Full ticket | `assets/result-templates.md` § "Full ticket (1 result)" |
| 2-5 | Moderate | `assets/result-templates.md` § "Moderate (2-5 results)" |
| 6+ | Concise table | `assets/result-templates.md` § "Concise table (6+ results)" |

When in doubt, prefer the more compact format - the user can always ask for more detail.

### Step 4: Offer drill-down

After showing results, end with one of:
- 1 result: skip (already shown in full)
- 2+ results: "Want full details on any of these? Give me a key (e.g. `CPC-11050`)."

Do **not** auto-fetch all details - keep it short and let the user pick.

## Why this design

The hardcoded cloudId, project, and component map exist because we hit naming drift in real queries: the user asked for "ibm guest image refresh" and the 2026 tickets had dropped that prefix entirely. A static, narrow query misses them; a discovery pass catches the drift. The 3-month default catches everything reasonable without burying the user in old Done tickets.

The skill is read-only by design - the user's first request was "find the latest tickets", not "create me a ticket". Lower friction, lower risk.

## Common pitfalls to avoid

1. **Don't trust a single fuzzy query.** Always pair a narrow query with a discovery query on the same component. Naming drift is the norm, not the exception.
2. **Don't filter by `status != Done` blindly.** `Rejected` is in the Done status category but is not actually done. `Untriaged` is in `To Do` and represents work that hasn't been picked up - often exactly what the user wants.
3. **Don't include unrelated refreshes.** Snap refreshes, SSDLC artifacts, and CI image refreshes share the "refresh" keyword with cloud image refreshes. Filter aggressively.
4. **Don't over-fetch fields.** Default `searchJiraIssuesUsingJql` returns summary, description, status, issuetype, priority, created. Add more only if the output template needs them.
5. **Don't guess ticket keys.** If the user said "the one from May 2026" but there are 3 matching tickets, show all 3 - don't pick one.

## References

- `references/jql-cheatsheet.md` - JQL operators, date functions, fuzzy matching tips
- `references/cpc-components.md` - known component names per cloud + how to discover new ones
- `references/cpc-custom-fields.md` - custom field IDs (Sprint, Team, Story Points, etc.) and how to query them
- `references/cpc-naming-conventions.md` - naming drift, date formats, status gotchas, noise patterns
- `assets/result-templates.md` - the three output templates (full / moderate / concise)
