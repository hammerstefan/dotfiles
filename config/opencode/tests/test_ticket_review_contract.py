"""Static/schema and synthetic transport checks, not claims of model compliance.

Run: PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s config/opencode/tests -v
Schema/frontmatter tests require the validation environment's jsonschema/PyYAML.
No production dependency is added; absent validation packages are reported as skips.
"""

from copy import deepcopy
import fnmatch
import importlib.util
import json
from pathlib import Path
import re
import unittest

try:
    import jsonschema
    import yaml
except ImportError:
    jsonschema = yaml = None

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "mock_ticket_mcp", ROOT / "tests/mock_ticket_mcp.py"
)
mock = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mock)


def effective(rules, action, resource):
    """Local evaluation of documented last-match wildcard rules, not the runtime."""
    effect = "ask"
    for rule in rules:
        pattern = (
            str(Path(rule["resource"]).expanduser())
            if rule["resource"].startswith("~/")
            else rule["resource"]
        )
        if fnmatch.fnmatchcase(action, rule["action"]) and fnmatch.fnmatchcase(
            resource, pattern
        ):
            effect = rule["effect"]
    return effect


class AcceptanceCriteriaContracts(unittest.TestCase):
    """Static prompt guards; these do not prove agent execution or discovery."""

    def test_discovery_uses_verified_scoped_metadata_without_guessing(self):
        command = (ROOT / "command/review-ticket.md").read_text()
        compact = " ".join(command.split())
        for required in (
            "`--acceptance-field` overrides automatic discovery",
            "Do not mutate the frozen invocation options",
            "skip all metadata discovery and supplemental acceptance reads",
            "returned `project.id`",
            "returned `issuetype.id`",
            "`requiredFieldsOnly: false`",
            "`maxResults: 200`",
            "exact name `acceptance criteria`",
            "pagination metadata proves the list is complete",
            "Do not fetch additional pages",
            "Zero matches is NOT proof",
            "use `question` before reviewer dispatch",
            "one exact custom field ID",
            "If no answer is available, pause",
        ):
            with self.subTest(required=required):
                self.assertIn(required, compact)

    def test_supplemental_read_preserves_primary_revision_and_coverage(self):
        command = (ROOT / "command/review-ticket.md").read_text()
        compact = " ".join(command.split())
        for required in (
            '`fields: [resolved_field_id, "updated"]`',
            "`updateHistory: false`",
            "Compare the returned `updated` with the primary snapshot",
            "unavailable timestamp",
            "Never combine fields from different revisions",
            "primary review target, not optional context",
            "Append it to `selected_fields` even if its read fails",
            "including acceptance criteria",
            "at most eight issue reads",
            "exactly one `proposal.additional_fields` entry",
            "no additional-field entry when no ID was resolved",
        ):
            with self.subTest(required=required):
                self.assertIn(
                    required,
                    compact.lower() if required.startswith("at most") else compact,
                )
        self.assertIn("### Acceptance Criteria", command)

    def test_reviewer_checks_each_criterion_without_inventing_requirements(self):
        reviewer = (ROOT / "agent/review-ticket-readability.md").read_text()
        compact = " ".join(reviewer.split())
        for required in (
            "Review every acceptance criterion",
            "observable completion condition",
            "consistency with the summary and description",
            "Do not invent tests, thresholds, requirements",
            "Retain both meanings in their respective drafts",
            "unavailable still needs an entry with null text",
            "do not move or duplicate them into a separate field",
        ):
            with self.subTest(required=required):
                self.assertIn(required, compact)


@unittest.skipIf(yaml is None, "PyYAML/jsonschema validation packages unavailable")
class TicketContracts(unittest.TestCase):
    def frontmatter(self, name):
        return yaml.safe_load(
            (ROOT / f"agent/{name}.md").read_text().split("---", 2)[1]
        )

    def test_coordinator_only_allows_named_reads_and_reviewer(self):
        rules = self.frontmatter("review-ticket-coordinator")["permissions"]
        for action in (
            "execute",
            "atlassian_getAccessibleAtlassianResources",
            "atlassian_getJiraIssue",
            "atlassian_getJiraIssueTypeMetaWithFields",
        ):
            self.assertEqual(effective(rules, action, "*"), "allow")
        for action in (
            "atlassian_updateJiraIssue",
            "atlassian_addCommentToJiraIssue",
            "atlassian_getJiraProjectIssueTypesMetadata",
            "shell",
            "edit",
            "webfetch",
            "write_review_human_report",
        ):
            self.assertEqual(effective(rules, action, "*"), "deny")
        self.assertEqual(
            effective(rules, "subagent", "review-ticket-readability"), "allow"
        )
        self.assertEqual(effective(rules, "subagent", "general"), "deny")
        self.assertEqual(effective(rules, "read", str(ROOT / "opencode.json")), "deny")
        for name in (
            "readability-criteria.md",
            "review-ticket.schema.json",
        ):
            installed = Path(f"~/.config/opencode/prompt/{name}").expanduser()
            self.assertEqual(effective(rules, "read", str(installed)), "allow")
            self.assertEqual(
                effective(rules, "read", str(installed.resolve())), "allow"
            )

    def test_snapshot_reviewer_only_allows_canonical_instructions(self):
        agent = self.frontmatter("review-ticket-readability")
        self.assertEqual(agent["model"], "github-copilot/claude-opus-5.5")
        self.assertEqual(
            agent["permissions"][0],
            {"action": "*", "resource": "*", "effect": "deny"},
        )
        self.assertEqual(
            effective(agent["permissions"], "skill", "asd-ste100"), "allow"
        )
        for action in (
            "read",
            "execute",
            "shell",
            "edit",
            "subagent",
            "atlassian_getJiraIssue",
        ):
            self.assertEqual(effective(agent["permissions"], action, "*"), "deny")
        self.assertEqual(
            effective(agent["permissions"], "skill", "other-skill"), "deny"
        )
        criteria = Path(
            "~/.config/opencode/prompt/readability-criteria.md"
        ).expanduser()
        self.assertEqual(
            effective(agent["permissions"], "read", str(criteria)), "allow"
        )
        self.assertEqual(
            effective(agent["permissions"], "read", str(criteria.resolve())), "allow"
        )
        self.assertEqual(
            effective(agent["permissions"], "read", str(ROOT / "opencode.json")), "deny"
        )

    def test_shared_criteria_extraction_keeps_all_rules(self):
        criteria = (ROOT / "prompt/readability-criteria.md").read_text()
        for text in (
            "MUST and SHOULD",
            "ordinary",
            "passive voice",
            "Never invent",
            "Do not infer",
            "equally clear",
            "prerequisites before instructions",
        ):
            self.assertIn(text, criteria)
        repo = (ROOT / "agent/review-readability.md").read_text()
        self.assertIn("~/.config/opencode/prompt/readability-criteria.md", repo)
        self.assertIn("If the file is unavailable, stop", repo)
        self.assertNotIn("At sentence level", repo)
        self.assertIn("```review-json", repo)
        self.assertIn("```review-readability-json", repo)
        self.assertNotIn("atlassian_", repo)

    def test_command_guards_and_limits(self):
        command = (ROOT / "command/review-ticket.md").read_text()
        for text in (
            "eight issue reads",
            "64 KiB",
            "128 KiB",
            "50 returned comments",
            "updateHistory",
            "more than five",
            "Do not retry",
            "Invalid results",
            "No council",
        ):
            self.assertIn(text, command)

    def test_ste_skill_is_loaded_directly_without_duplicated_rules(self):
        rules = self.frontmatter("review-ticket-coordinator")["permissions"]
        self.assertEqual(effective(rules, "skill", "asd-ste100"), "allow")
        self.assertEqual(effective(rules, "skill", "other-skill"), "deny")
        self.assertFalse((ROOT / "prompt/ticket-ste100.md").exists())
        coordinator = (ROOT / "agent/review-ticket-coordinator.md").read_text()
        reviewer = (ROOT / "agent/review-ticket-readability.md").read_text()
        command = (ROOT / "command/review-ticket.md").read_text()
        self.assertIn('skill({"id": "asd-ste100"})', coordinator)
        self.assertIn("reviewer must load `asd-ste100` itself", coordinator)
        self.assertIn('skill({"id": "asd-ste100"})', reviewer)
        self.assertIn("complete tool result", reviewer)
        self.assertIn("report/JSON format", reviewer)
        self.assertIn("before any MCP call", command)
        self.assertIn("Stop if the skill is unavailable", command)
        self.assertNotIn(
            "asd-ste100", (ROOT / "agent/review-readability.md").read_text()
        )
        for text in (coordinator, reviewer, command):
            self.assertNotIn("ticket-ste100.md", text)
            self.assertNotIn("20 words", text)
            self.assertNotIn("25 words", text)


@unittest.skipIf(jsonschema is None, "jsonschema validation package unavailable")
class TicketResultSchema(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads(
            (ROOT / "prompt/review-ticket.schema.json").read_text()
        )
        jsonschema.Draft202012Validator.check_schema(self.schema)
        agent = (ROOT / "agent/review-ticket-readability.md").read_text()
        self.result = json.loads(
            re.search(r"```review-ticket-json\n(.*?)\n```", agent, re.S)[1]
        )

    def test_documented_example_valid(self):
        jsonschema.validate(self.result, self.schema)

    def test_resolved_acceptance_uses_existing_primary_field_contract(self):
        self.result["coverage"]["reviewed_fields"].append("customfield_10001")
        self.result["proposal"]["additional_fields"] = [
            {
                "field_id": "customfield_10001",
                "text": "The client MUST download a CSV file to finish.",
                "status": "ready",
            }
        ]
        jsonschema.validate(self.result, self.schema)
        self.result["proposal"]["additional_fields"][0]["text"] = None
        self.result["proposal"]["additional_fields"][0]["status"] = "incomplete"
        self.result["proposal"]["status"] = "incomplete"
        self.result["coverage"]["reviewed_fields"].remove("customfield_10001")
        self.result["coverage"]["status"] = "incomplete"
        self.result["coverage"]["limitations"] = [
            "Acceptance criteria unavailable: changed snapshot timestamp."
        ]
        jsonschema.validate(self.result, self.schema)

    def test_unknown_fields_rejected(self):
        for target in (self.result, self.result["proposal"], self.result["ticket"]):
            target["unexpected"] = "not valid"
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(self.result, self.schema)
            del target["unexpected"]

    def test_incomplete_requires_limitations_and_proposal_status(self):
        self.result["coverage"]["status"] = "incomplete"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(self.result, self.schema)
        self.result["coverage"]["limitations"] = ["Selected context unavailable"]
        self.result["proposal"]["status"] = "incomplete"
        jsonschema.validate(self.result, self.schema)

    def test_question_prevents_ready(self):
        self.result["open_questions"] = [
            {
                "id": "TQ-1",
                "location": {
                    "issue_key": "CPC-1234",
                    "field_id": "description",
                    "heading_path": [],
                    "block": 1,
                },
                "question": "Which target is intended?",
                "related_ids": [],
            }
        ]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(self.result, self.schema)
        self.result["proposal"]["status"] = "needs_clarification"
        jsonschema.validate(self.result, self.schema)

    def test_invalid_locations_and_ids_rejected(self):
        item = {
            "id": "TED-1",
            "location": {
                "issue_key": "CPC-1234",
                "field_id": "description",
                "heading_path": [],
                "block": 1,
            },
            "original": "Text",
            "problem": "Wordy",
            "suggested_edit": "Short text",
        }
        self.result["readability_suggestions"] = [item]
        jsonschema.validate(self.result, self.schema)
        for block in (0, -1, True, "1"):
            item["location"]["block"] = block
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(self.result, self.schema)

    def test_empty_and_withheld_proposals_are_structurally_valid(self):
        self.result["proposal"]["description"] = ""
        jsonschema.validate(self.result, self.schema)
        self.result["proposal"]["description"] = None
        self.result["proposal"]["status"] = "incomplete"
        self.result["coverage"]["status"] = "incomplete"
        self.result["coverage"]["limitations"] = ["Description unavailable"]
        jsonschema.validate(self.result, self.schema)

    def test_withheld_field_cannot_claim_ready(self):
        for field in ("summary", "description"):
            with self.subTest(field=field):
                candidate = deepcopy(self.result)
                candidate["proposal"][field] = None
                with self.assertRaises(jsonschema.ValidationError):
                    jsonschema.validate(candidate, self.schema)


class SyntheticRetrieval(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(mock.FIXTURES.read_text())
        self.args = {
            "cloudId": "mock-cloud",
            "issueIdOrKey": "TASK-1",
            "fields": ["summary", "description", "updated"],
            "updateHistory": False,
            "responseContentFormat": "adf",
        }

    def test_default_read_filters_fields(self):
        result = mock.call("getJiraIssue", self.args, self.fixture)
        self.assertEqual(set(result["fields"]), {"summary", "description", "updated"})

    def test_history_and_broad_reads_rejected_by_mock(self):
        for change in ({"updateHistory": True}, {"fields": []}, {"fields": ["*all"]}):
            with self.assertRaises(ValueError):
                mock.call("getJiraIssue", self.args | change, self.fixture)

    def test_acceptance_field_read_is_explicit_and_comments_are_opt_in(self):
        args = self.args | {"issueIdOrKey": "TASK-2"}
        default = mock.call("getJiraIssue", args, self.fixture)
        self.assertNotIn("comment", default["fields"])
        explicit = mock.call(
            "getJiraIssue",
            args | {"fields": ["customfield_10001", "comment"]},
            self.fixture,
        )
        self.assertEqual(explicit["fields"]["comment"]["total"], 2)
        self.assertIn("customfield_10001", explicit["fields"])

    def metadata(self, issue_type="101", **overrides):
        return mock.call(
            "getJiraIssueTypeMetaWithFields",
            {
                "cloudId": "mock-cloud",
                "projectIdOrKey": "100",
                "issueTypeId": issue_type,
                "startAt": 0,
                "maxResults": 200,
                "requiredFieldsOnly": False,
            }
            | overrides,
            self.fixture,
        )

    def test_discovery_transport_and_minimal_acceptance_read(self):
        primary = mock.call(
            "getJiraIssue",
            self.args
            | {
                "issueIdOrKey": "TASK-11",
                "fields": ["summary", "description", "updated", "project", "issuetype"],
            },
            self.fixture,
        )
        saved = deepcopy(primary)
        self.assertEqual(primary["fields"]["project"]["id"], "100")
        self.assertEqual(primary["fields"]["issuetype"]["id"], "101")
        self.assertNotIn("customfield_10001", primary["fields"])
        metadata = self.metadata()
        self.assertTrue(metadata["isLast"])
        field = metadata["values"][1]
        self.assertEqual(field["name"], "Acceptance Criteria")
        self.assertFalse(field["required"])
        acceptance = mock.call(
            "getJiraIssue",
            self.args
            | {"issueIdOrKey": "TASK-11", "fields": [field["fieldId"], "updated"]},
            self.fixture,
        )
        self.assertEqual(set(acceptance["fields"]), {"customfield_10001", "updated"})
        self.assertEqual(acceptance["fields"]["updated"], primary["fields"]["updated"])
        self.assertEqual(acceptance["fields"]["customfield_10001"]["type"], "doc")
        self.assertEqual(primary, saved)

    def test_metadata_requires_optional_fields_and_one_bounded_page(self):
        for overrides in (
            {"requiredFieldsOnly": True},
            {"requiredFieldsOnly": None},
            {"startAt": 200},
            {"maxResults": 1000},
            {"cloudId": "guessed-cloud"},
        ):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                self.metadata(**overrides)

    def test_unresolved_metadata_fixtures(self):
        ambiguous = self.metadata("102")
        self.assertEqual(len(ambiguous["values"]), 2)
        self.assertEqual(
            {
                " ".join(field["name"].split()).casefold()
                for field in ambiguous["values"]
            },
            {"acceptance criteria"},
        )
        partial = self.metadata("103")
        self.assertFalse(partial["isLast"])
        self.assertGreater(partial["total"], len(partial["values"]))
        absent = self.metadata("104")
        self.assertTrue(absent["isLast"])
        self.assertEqual(absent["values"][0]["fieldId"], "summary")
        unknown = self.metadata("106")
        self.assertNotIn("isLast", unknown)
        self.assertNotIn("total", unknown)
        with self.assertRaises(ValueError):
            self.metadata("105")

    def test_acceptance_null_absent_changed_revision_and_wrong_key(self):
        def acceptance(key):
            return mock.call(
                "getJiraIssue",
                self.args
                | {"issueIdOrKey": key, "fields": ["customfield_10001", "updated"]},
                self.fixture,
            )

        self.assertIsNone(acceptance("TASK-12")["fields"]["customfield_10001"])
        self.assertNotIn("customfield_10001", acceptance("TASK-13")["fields"])
        primary = mock.call(
            "getJiraIssue", self.args | {"issueIdOrKey": "TASK-14"}, self.fixture
        )
        self.assertNotEqual(
            acceptance("TASK-14")["fields"]["updated"], primary["fields"]["updated"]
        )
        self.assertNotEqual(acceptance("TASK-15")["key"], "TASK-15")

    def test_null_absent_mismatch_and_unavailable_fixtures(self):
        empty = mock.call(
            "getJiraIssue", self.args | {"issueIdOrKey": "TASK-3"}, self.fixture
        )
        missing = mock.call(
            "getJiraIssue", self.args | {"issueIdOrKey": "TASK-4"}, self.fixture
        )
        wrong = mock.call(
            "getJiraIssue", self.args | {"issueIdOrKey": "TASK-7"}, self.fixture
        )
        self.assertIsNone(empty["fields"]["description"])
        self.assertNotIn("description", missing["fields"])
        self.assertNotEqual(wrong["key"], "TASK-7")
        with self.assertRaises(ValueError):
            mock.call(
                "getJiraIssue", self.args | {"issueIdOrKey": "TASK-8"}, self.fixture
            )

    def test_large_adf_and_multiple_site_fixtures(self):
        large = mock.call(
            "getJiraIssue", self.args | {"issueIdOrKey": "TASK-9"}, self.fixture
        )
        self.assertGreater(len(large["fields"]["description"].encode()), 65536)
        adf = mock.call(
            "getJiraIssue", self.args | {"issueIdOrKey": "TASK-5"}, self.fixture
        )
        self.assertEqual(
            adf["fields"]["description"]["content"][-1]["type"], "mediaSingle"
        )
        self.assertEqual(
            len(mock.call("getAccessibleAtlassianResources", {}, self.fixture, True)), 2
        )

    def test_mutation_stub_is_inert(self):
        original = deepcopy(self.fixture)
        with self.assertRaises(ValueError):
            mock.call("updateJiraIssue", {}, self.fixture)
        self.assertEqual(self.fixture, original)


if __name__ == "__main__":
    unittest.main()
