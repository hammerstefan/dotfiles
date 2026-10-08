"""Regression checks for readability's human-attention persistence boundary.

Run with: python3 -m unittest discover -s config/opencode/tests -v
"""

import importlib.util
from pathlib import Path
import unittest


WRITER_PATH = (
    Path(__file__).resolve().parents[1] / "script/write-review-human-report.py"
)
SPEC = importlib.util.spec_from_file_location("review_human_report", WRITER_PATH)
writer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(writer)


def summary(selected, *, failed=None, finding_ids=None):
    ids = finding_ids or []
    return {
        "verdict": "APPROVE",
        "selected_reviewers": selected,
        "failed_reviewers": failed or [],
        "verified_finding_ids": ids,
        "verified_finding_count": len(ids),
    }


class ReadabilityCouncilSummaryTests(unittest.TestCase):
    def test_readability_only_with_substantive_finding(self):
        candidate = summary(["review-readability"], finding_ids=["RDB-1"])
        self.assertEqual(
            writer.validate_council_summary(candidate, "council"), candidate
        )

    def test_editorial_only_review_needs_no_finding_ids(self):
        candidate = summary(["review-readability"])
        self.assertEqual(
            writer.validate_council_summary(candidate, "council"), candidate
        )

    def test_full_council_accepts_all_eight_reviewers(self):
        candidate = summary(
            [
                "review-correctness",
                "review-security",
                "review-architecture",
                "review-tests",
                "review-compatibility",
                "review-skeptic",
                "review-crossfile",
                "review-readability",
            ]
        )
        self.assertEqual(
            writer.validate_council_summary(candidate, "council"), candidate
        )

    def test_readability_failure_preserves_successful_reviewers(self):
        candidate = summary(
            ["review-correctness", "review-readability"],
            failed=["review-readability"],
            finding_ids=["COR-1"],
        )
        self.assertEqual(
            writer.validate_council_summary(candidate, "council"), candidate
        )

    def test_partial_failure_can_keep_readability_finding(self):
        candidate = summary(
            ["review-readability"],
            failed=["review-readability"],
            finding_ids=["RDB-1"],
        )
        self.assertEqual(
            writer.validate_council_summary(candidate, "council"), candidate
        )

    def test_editorial_fields_cannot_leak_into_summary(self):
        for field in ("readability_suggestions", "readability_coverage"):
            with self.subTest(field=field):
                candidate = summary(["review-readability"])
                candidate[field] = []
                with self.assertRaises(writer.ReportError):
                    writer.validate_council_summary(candidate, "council")

    def test_independent_mode_still_requires_null_summary(self):
        self.assertIsNone(writer.validate_council_summary(None, "independent"))
        with self.assertRaises(writer.ReportError):
            writer.validate_council_summary(
                summary(["review-readability"]), "independent"
            )

    def test_failed_reviewer_must_have_been_selected(self):
        with self.assertRaises(writer.ReportError):
            writer.validate_council_summary(
                summary(["review-security"], failed=["review-readability"]),
                "council",
            )

    def test_unknown_and_duplicate_reviewer_names_remain_invalid(self):
        for reviewers in (
            ["review-editorial"],
            ["review-readability", "review-readability"],
        ):
            with (
                self.subTest(reviewers=reviewers),
                self.assertRaises(writer.ReportError),
            ):
                writer.validate_council_summary(summary(reviewers), "council")


if __name__ == "__main__":
    unittest.main()
