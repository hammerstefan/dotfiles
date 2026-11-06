"""Static prompt checks, not proof that a model finds every ambiguous term."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AmbiguityContracts(unittest.TestCase):
    def test_shared_scan_covers_terms_beyond_opening_prose(self):
        criteria = (ROOT / "prompt/readability-criteria.md").read_text()
        for required in (
            "## Ambiguous-Term Scan",
            "every list item",
            "all distinct audience-relevant ambiguities",
            "abbreviations",
            "roles",
            "threshold",
            "guardrails",
            "Slash compounds",
            "Lifecycle and state terms",
            "Do not assume that an unread dependency defines a term",
            "Do not invent expansions or thresholds",
            "incomplete coverage",
            "Do not\nreclassify substantive defects to bypass filters",
        ):
            with self.subTest(required=required):
                self.assertIn(required, criteria)

    def test_both_review_paths_require_shared_scan(self):
        for path in (
            "agent/review-readability.md",
            "agent/review-ticket-readability.md",
            "command/review-council.md",
            "command/review-ticket.md",
        ):
            with self.subTest(path=path):
                text = (ROOT / path).read_text()
                self.assertIn("shared Ambiguous-Term Scan", text)
                self.assertIn("all distinct", text)

    def test_ticket_preserves_ambiguities_and_repository_preserves_filters(self):
        ticket = (ROOT / "agent/review-ticket-readability.md").read_text()
        self.assertIn("source-backed open question with related_ids", ticket)
        self.assertIn("Retain unresolved wording in the draft", ticket)
        repo = (ROOT / "agent/review-readability.md").read_text()
        self.assertIn("report only ambiguities introduced or", repo)
        self.assertIn("Preserve the existing severity/finding filters", repo)
        self.assertIn('skill({"id": "asd-ste100"})', repo)

    def test_ticket_skill_scope_stays_inside_the_ticket_flow(self):
        """The ticket command must not push its skill rules into repository reviews."""
        command = (ROOT / "command/review-ticket.md").read_text()
        self.assertIn(
            "Apply its writing guidance to Jira feedback, drafts, and questions only",
            command,
        )
        self.assertIn("Do not apply this skill to repository council reviews", command)

    def test_ticket_terms_table_uses_validated_feedback_without_new_json_fields(self):
        command = (ROOT / "command/review-ticket.md").read_text()
        reviewer = (ROOT / "agent/review-ticket-readability.md").read_text()
        coordinator = (ROOT / "agent/review-ticket-coordinator.md").read_text()
        self.assertLess(
            command.index("## Undefined and Ambiguous Terms"),
            command.index("## Clarity Feedback"),
        )
        self.assertIn(
            "| Term or phrase | Source location | Missing meaning | "
            "Clarification needed | References |",
            command,
        )
        for required in (
            "table only from validated",
            "one row per distinct unresolved term",
            "Keep different meanings in separate rows",
            "`open_questions` IDs whose `related_ids`",
            "Escape pipes",
            "Do not add keys to `review-ticket-json`",
        ):
            with self.subTest(required=required):
                self.assertIn(required, command)
        self.assertIn("each distinct undefined or ambiguous term", reviewer)
        self.assertIn("exact safe term or phrase as `original`", reviewer)
        self.assertIn("Do not label ordinary", reviewer)
        self.assertIn("table from validated", coordinator)

    def test_ticket_terms_table_distinguishes_empty_and_incomplete_scans(self):
        for path in (
            "command/review-ticket.md",
            "agent/review-ticket-readability.md",
        ):
            text = (ROOT / path).read_text()
            with self.subTest(path=path):
                self.assertIn(
                    "No undefined or ambiguous terms found for the intended audience.",
                    text,
                )
                self.assertIn("Terminology scan incomplete; see Coverage.", text)
                self.assertIn("available reviewed text", " ".join(text.split()))


if __name__ == "__main__":
    unittest.main()
