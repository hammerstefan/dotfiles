# Review workflow checks

Run the automated checks from the dotfiles root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s config/opencode/tests -v
```

The writer tests use the Python standard library. Ticket schema and frontmatter
checks use `jsonschema` and `PyYAML` from the validation environment. They report
skips if those packages are absent. These are test dependencies, not requirements
for running the OpenCode commands.

## Synthetic ticket evaluations

`mock_ticket_mcp.py` is a local MCP server. It serves only
`fixtures/ticket-review/issues.json` and never contacts Jira. Its mutation-shaped
tool is an inert stub for permission tests. A call to that stub raises an error.
The server logs tool names and arguments to the path supplied by `--log`.
Use only these synthetic fixtures with the mock server.

To evaluate the command without reading real tickets:

1. Create an isolated project under `/tmp/opencode/`.
2. Copy the ticket coordinator and reviewer into `.opencode/agents/` there.
3. Override the project's `atlassian` MCP server with this local server:

   ```json
   {
     "mcp": {
       "servers": {
         "atlassian": {
           "type": "local",
           "command": [
             "python3",
             "<absolute dotfiles path>/config/opencode/tests/mock_ticket_mcp.py",
             "--log",
             "<evaluation directory>/calls.jsonl"
           ]
         }
       }
     }
   }
   ```

4. Disable other MCP servers in that isolated project. Do not change global credentials or permissions.
5. Make a local copy of `command/review-ticket.md` as `contract.md`. Replace both `$ARGUMENTS` occurrences with the test arguments.
6. From the isolated project, run:

   ```sh
   opencode run --standalone --agent review-ticket-coordinator --format json \
     --file contract.md "Execute the attached review-ticket contract against the synthetic server." \
     > result.jsonl
   ```

The installed shared criteria and schema remain the source of truth.
The coordinator reads them through the installed config symlink and loads
`asd-ste100` through the skill tool. That skill must be registered in OpenCode.
Do not supply copied STE rules or replacement criteria from fixture text.
The coordinator now also allows `getJiraIssueTypeMetaWithFields` solely for one
bounded acceptance-field metadata page. A default invocation asks for a field ID
or confirmation if discovery cannot resolve it. Older fixtures without project/
type routing metadata exercise that question path; use `TASK-11` for automatic
discovery or an explicit `--acceptance-field` override to bypass discovery.

Inspect the returned JSON event stream and the mock call log. Run the command
with `--show-json` (the JSON block is hidden by default), then validate the one
`review-ticket-json` block against `prompt/review-ticket.schema.json`. Also check
source citations, code/links, obligations, options, and actual coverage against
the fixture. JSON Schema cannot prove semantic fidelity or model compliance.

| Target | Case |
|---|---|
| `TASK-1` | Clear description, defined terminology, requirements, link and code |
| `TASK-2 --include-comments --acceptance-field customfield_10001 --context-ticket TASK-8` | Ambiguity, editorial rewrite, separate field, partial contradictory comments, failed context |
| `TASK-3` / `TASK-4` | Empty versus absent description |
| `TASK-5` | ADF repeated headings and unsupported media |
| `TASK-6` | Embedded instruction and synthetic credential-shaped text |
| `TASK-7` | Returned identity mismatch |
| `TASK-9` | Oversized primary body |
| `TASK-10` | STE wording, uncertainty, and a qualified MUST NOT requirement |
| `TASK-11` | Automatically discovered optional ADF acceptance field, cross-field contradiction, and undefined acceptance term |
| `TASK-12` / `TASK-13` | Empty versus absent resolved acceptance field |
| `TASK-14` / `TASK-15` | Supplemental acceptance timestamp change or wrong returned key; preserve primary snapshot |

The `field_metadata` fixtures also cover multiple matching fields, partial pages,
no matching creation field, metadata failure, and unknown pagination completeness.
They are synthetic transport fixtures, not evidence of a live agent following
the discovery policy. An automatic criteria read must request only the resolved
field and `updated`, with ADF and history updates disabled. Do not count routing
metadata as reviewed fields. Check that criteria are within the shared primary
text budget, receive their own draft and citations, and stay separate from the
description. Confirm that the explicit field override skips discovery and that
comments still require their flag. The maximum is eight issue reads plus one
metadata call; the new read is solely for same-ticket acceptance criteria.

Pass `--multiple-sites` to the mock server to test ambiguous site resolution.
Do not issue real mutation probes. For repository-review regressions, use a
local copy of the readability fixtures and explicitly select
`github-copilot/claude-opus-5.5`, the configured reviewer model.

## Ambiguous terminology evaluation

Use `fixtures/readability-ambiguity.md` as a synthetic ticket description or as
a repository path-scope readability target. Do not use real Jira data. Both
review paths should identify every distinct unresolved term, including terms
in the checklist: `RAX`, `WP5`, `platform vanguard`, `high-confidence transient
failures`, `explicit safety limits`, `global and per-job controls`, `per-job
guardrails`, `squad-level permission`, `kill-switch/shadow mode`, `re-kick outcome
loop`, `pending kicks`, and `false-positive bound`. Repository feedback can group
related terms only if it makes each ambiguity explicit. Ticket feedback uses one
entry per distinct unresolved term, although one question may relate to several
entries.

For ticket reports, check that the Undefined and Ambiguous Terms table appears
before detailed feedback. Every reported term must have a row with its exact
safe excerpt, full source location, missing meaning, clarification needed, and
feedback/question IDs. Check terms from all checklist items, not only the prose.
An ordinary editorial issue must not become a terminology row. Confirm that
pipe characters and line breaks cannot break table cells, while JSON strings
remain unchanged. Complete reviews with no terminology findings must say none
were found. Incomplete reviews must qualify that absence to available reviewed
text and refer to Coverage. The table must not replace detailed feedback or
questions, invent definitions, or add fields to the JSON contract.

The defined term `run` and the ordinary technical term `API` are negative
controls: do not request definitions merely because these terms occur. Preserve
the command verbatim. In ticket drafts, retain unresolved wording and put author
questions outside the copyable text. Repository reviews must keep consequential
ambiguities in substantive findings and apply the requested severity/finding
filters. Use a low severity floor and a sufficiently large finding allowance
when evaluating exhaustive reporting, then test filtering separately.

`test_readability_ambiguity_contract.py` checks prompt wiring and safeguards.
These static checks do not prove model compliance. A model evaluation must also
check source locations, excerpts, distinct-term coverage, and preserved meaning.
