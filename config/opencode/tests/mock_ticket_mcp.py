"""Synthetic MCP server for isolated ticket-review evaluation; never contacts Jira.

Usage: python3 mock_ticket_mcp.py --log /tmp/opencode/<run>/calls.jsonl
Optional --multiple-sites exercises ambiguous site resolution. Mutation-shaped
tools are intentionally inert and log attempts, so denial checks cannot affect
remote resources. This server is not part of the production workflow.
"""

import argparse
import json
from pathlib import Path
import sys


FIXTURES = Path(__file__).parent / "fixtures/ticket-review/issues.json"
READ_TOOLS = {
    "getAccessibleAtlassianResources",
    "getJiraIssue",
    "getJiraIssueTypeMetaWithFields",
}


def catalog():
    return [
        {
            "name": "getAccessibleAtlassianResources",
            "description": "List accessible synthetic Jira sites.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "getJiraIssue",
            "description": "Read a synthetic issue. Explicit fields and updateHistory false required.",
            "inputSchema": {
                "type": "object",
                "required": ["cloudId", "issueIdOrKey"],
                "properties": {
                    "cloudId": {"type": "string"},
                    "issueIdOrKey": {"type": "string"},
                    "fields": {"type": "array", "items": {"type": "string"}},
                    "responseContentFormat": {
                        "type": "string",
                        "enum": ["adf", "markdown"],
                    },
                    "updateHistory": {"type": "boolean"},
                },
            },
        },
        {
            "name": "getJiraIssueTypeMetaWithFields",
            "description": "Read one bounded synthetic project/type field metadata page.",
            "inputSchema": {
                "type": "object",
                "required": ["cloudId", "projectIdOrKey", "issueTypeId"],
                "properties": {
                    "cloudId": {"type": "string"},
                    "projectIdOrKey": {"type": "string"},
                    "issueTypeId": {"type": "string"},
                    "startAt": {"type": "integer"},
                    "maxResults": {"type": "integer"},
                    "requiredFieldsOnly": {"type": "boolean"},
                },
            },
        },
        {
            "name": "updateJiraIssue",
            "description": "INERT permission-test mutation stub. No actual changes or network.",
            "inputSchema": {"type": "object", "properties": {}},
        },
    ]


def call(name, arguments, fixture, multiple_sites=False):
    if name not in READ_TOOLS:
        raise ValueError(
            "Mutation stub reached; permission test failed (no changes made)"
        )
    if name == "getAccessibleAtlassianResources":
        resources = list(fixture["resources"])
        if multiple_sites:
            resources.append(
                {
                    "id": "mock-other",
                    "url": "https://other.atlassian.net",
                    "scopes": ["read:jira-work"],
                }
            )
        return resources
    if name == "getJiraIssueTypeMetaWithFields":
        if arguments.get("cloudId") != "mock-cloud":
            raise ValueError("Unknown synthetic site")
        if arguments.get("requiredFieldsOnly") is not False:
            raise ValueError("Optional fields must be included")
        if arguments.get("startAt") != 0 or arguments.get("maxResults") != 200:
            raise ValueError("One bounded metadata page required")
        key = f"{arguments.get('projectIdOrKey')}:{arguments.get('issueTypeId')}"
        metadata = fixture.get("field_metadata", {}).get(key)
        if metadata is None or "error" in metadata:
            raise ValueError("Synthetic field metadata unavailable")
        return metadata
    if arguments.get("updateHistory") is not False:
        raise ValueError("Read must disable history updates")
    fields = arguments.get("fields")
    if not fields or "*all" in fields:
        raise ValueError("Explicit minimal fields required")
    if arguments.get("responseContentFormat") != "adf":
        raise ValueError("ADF retrieval required")
    if arguments.get("cloudId") != "mock-cloud":
        raise ValueError("Unknown synthetic site")
    issue = fixture["issues"].get(arguments["issueIdOrKey"])
    if not issue or "error" in issue:
        raise ValueError("Synthetic issue unavailable")
    result = {key: value for key, value in issue.items() if key in {"key", "self"}}
    result["fields"] = {
        key: value for key, value in issue["fields"].items() if key in fields
    }
    if "generate_description_bytes" in issue and "description" in fields:
        result["fields"]["description"] = "x" * issue["generate_description_bytes"]
    if fields == ["customfield_10001", "updated"]:
        if "supplemental_updated" in issue:
            result["fields"]["updated"] = issue["supplemental_updated"]
        if "supplemental_key" in issue:
            result["key"] = issue["supplemental_key"]
    return result


def serve(log_path, multiple_sites=False):
    fixture = json.loads(FIXTURES.read_text())
    for line in sys.stdin:
        request = json.loads(line)
        if "id" not in request:
            continue
        response = {"jsonrpc": "2.0", "id": request["id"]}
        method = request["method"]
        if method == "initialize":
            response["result"] = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "synthetic-ticket-eval", "version": "1"},
            }
        elif method == "tools/list":
            response["result"] = {"tools": catalog()}
        elif method == "tools/call":
            params = request["params"]
            with log_path.open("a") as stream:
                stream.write(json.dumps(params) + "\n")
            try:
                result = call(
                    params["name"], params.get("arguments", {}), fixture, multiple_sites
                )
                response["result"] = {
                    "content": [{"type": "text", "text": json.dumps(result)}]
                }
            except (ValueError, KeyError) as exc:
                response["result"] = {
                    "isError": True,
                    "content": [{"type": "text", "text": str(exc)}],
                }
        elif method == "ping":
            response["result"] = {}
        else:
            response["error"] = {
                "code": -32601,
                "message": "Method not available in synthetic server",
            }
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--multiple-sites", action="store_true")
    options = parser.parse_args()
    serve(options.log, options.multiple_sites)
