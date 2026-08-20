# CPC Components Reference

Jira components in the CPC project (`CPC☁️-ENG`, project id `10003`). This is the canonical list of components for cloud image work.

## Known components (as of 2026-06-03)

| Cloud | Component | Component ID | Notes |
|---|---|---|---|
| IBM | `ibm` | 10006 | Parent / generic. Often paired with `ibm-vpc` or `ibm-classic`. |
| IBM | `ibm-vpc` | 13400 | IBM Cloud VPC Next Gen Guest |
| IBM | `ibm-classic` | - | IBM Classic infrastructure (Softlayer). Use `~` to fuzzy-match. |
| IBM | `ibm-guest` | - | Older naming. Still appears in some legacy tickets, rarely used in 2024+. |
| AWS | `aws` | - | Amazon Web Services - generic |
| AWS | `aws-gadget` | - | The aws snap gadget (CI image build, NOT what we usually want) |
| Azure | `azure` | - | Microsoft Azure |
| GCP | `gcp` | - | Google Cloud Platform |

Some component IDs are missing from this list because the warthogs API doesn't always expose them. Use the component **name** in JQL (`component = ibm`) - not the ID.

## How to look up components dynamically

If you're unsure whether a component exists, or want the latest list:

```
atlassian_getJiraProjectIssueTypesMetadata(
  cloudId="220bceb6-6b32-4813-90eb-68d67c9445db",
  projectIdOrKey="CPC",
  maxResults=50
)
```

This returns issue type metadata. Component IDs appear in the schema when you fetch a specific issue type's fields.

For a fast component-name-to-ticket check, search by component name directly:

```
atlassian_searchJiraIssuesUsingJql(
  cloudId="220bceb6-6b32-4813-90eb-68d67c9445db",
  jql="project = CPC AND component = ibm-vpc ORDER BY created DESC",
  maxResults=10
)
```

If 0 results, the component name is wrong. If results, the name is correct and you have current data.

## Cloud → component mapping for the skill

When the user says:
- "ibm" / "IBM" / "ibm cloud" → `["ibm", "ibm-vpc", "ibm-classic", "ibm-guest"]`
- "aws" / "amazon" / "ec2" → `["aws"]` (avoid `aws-gadget` - it's a different thing)
- "azure" / "microsoft" → `["azure"]`
- "gcp" / "google cloud" → `["gcp"]`
- "classic" → `["ibm-classic"]`
- "vpc" → `["ibm-vpc"]`
- "guest" → `["ibm-guest"]`

If the user just says "cloud" or doesn't specify, use the union of all: `["ibm", "ibm-vpc", "ibm-classic", "aws", "azure", "gcp"]` and rely on the keyword filter to narrow.

## Component gotchas

1. **`aws-gadget` ≠ `aws`.** The `aws-gadget` component is for the snap that runs inside AWS instances. Tickets about "aws-gadget refresh" are not cloud image refreshes - they are snap refreshes. Filter them out.
2. **Multi-component tickets are common.** A single ticket can have `ibm` + `ibm-vpc` (e.g. CPC-11050 has both). Don't assume one component per ticket.
3. **Components get renamed.** `ibm-guest` was the original; later tickets use just `ibm` or `ibm-vpc`. Don't be surprised if a 2024 ticket has `ibm-guest` and a 2026 ticket has just `ibm`.
4. **No component ≠ wrong project.** Some CPC tickets have no components set. Don't filter on component presence alone - always pair with a summary/description keyword.
