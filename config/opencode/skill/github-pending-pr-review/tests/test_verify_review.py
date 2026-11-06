"""Tests for the pending-review verification against remote state.

The remote shapes used here are the ones GitHub actually returns. The
review-scoped endpoint returns the legacy comment shape, which holds the
diff position but no line and no side. The pull-request-scoped endpoint
returns the full shape, which holds all of them.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from verify_review import VerificationError, verify  # noqa: E402

REVIEW_ID = 5802085411
HEAD_SHA = "9f8b6cb5f1d603b7d91addda1f14faf99c4f8305"

PATCH = """@@ -5,4 +5,5 @@ def function():
 one
-two
+TWO
 three
 four
"""

FILES = [{"filename": "src/example.py", "patch": PATCH}]

REQUESTED = [
    {"path": "src/example.py", "line": 6, "side": "RIGHT", "body": "Could we?"}
]


def legacy_comment(**overrides):
    """The review-scoped endpoint's shape: a position, no line and no side."""
    base = {
        "id": 4493860220,
        "pull_request_review_id": REVIEW_ID,
        "path": "src/example.py",
        "position": 3,
        "body": "Could we?",
        "commit_id": HEAD_SHA,
    }
    base.update(overrides)
    return base


def full_comment(**overrides):
    """The pull-request-scoped endpoint's shape: the line and the side."""
    base = {
        "id": 4493860220,
        "pull_request_review_id": REVIEW_ID,
        "path": "src/example.py",
        "position": 3,
        "line": 6,
        "side": "RIGHT",
        "body": "Could we?",
        "commit_id": HEAD_SHA,
    }
    base.update(overrides)
    return base


def graphql_comment(**overrides):
    """GraphQL states the line but has no side field."""
    base = {
        "databaseId": 4493860220,
        "pullRequestReview": {"id": "PRR_example"},
        "path": "src/example.py",
        "line": 6,
        "body": "Could we?",
    }
    base.update(overrides)
    return base


class VerifyTest(unittest.TestCase):
    def test_a_comment_with_only_a_position_is_verified_through_the_patch(self):
        report = verify(FILES, REQUESTED, [legacy_comment()], REVIEW_ID, HEAD_SHA)
        self.assertEqual(report["failures"], [])
        self.assertEqual(report["verified"], 1)
        self.assertEqual(report["comments"][0]["verified_by"], "diff_position")
        self.assertEqual(report["comments"][0]["line"], 6)
        self.assertEqual(report["comments"][0]["side"], "RIGHT")

    def test_a_comment_with_the_full_shape_is_verified_directly(self):
        report = verify(FILES, REQUESTED, [full_comment()], REVIEW_ID, HEAD_SHA)
        self.assertEqual(report["failures"], [])
        self.assertEqual(
            report["comments"][0]["verified_by"], "api_fields_and_diff_position"
        )

    def test_a_graphql_line_is_checked_against_the_position(self):
        report = verify(
            FILES,
            REQUESTED,
            [legacy_comment(), graphql_comment()],
            REVIEW_ID,
            HEAD_SHA,
            "PRR_example",
        )
        self.assertEqual(report["failures"], [])
        self.assertEqual(
            report["comments"][0]["verified_by"], "api_line_and_diff_position"
        )

    def test_a_graphql_line_that_contradicts_the_position_is_refused(self):
        report = verify(
            FILES,
            REQUESTED,
            [legacy_comment(), graphql_comment(line=5)],
            REVIEW_ID,
            HEAD_SHA,
            "PRR_example",
        )
        self.assertTrue(report["failures"])
        self.assertIn("maps to line 6", report["failures"][0])

    def test_the_api_line_and_the_position_must_agree(self):
        report = verify(FILES, REQUESTED, [full_comment(line=5)], REVIEW_ID, HEAD_SHA)
        self.assertTrue(report["failures"])
        self.assertIn("maps to line 6", report["failures"][0])

    def test_a_comment_on_another_anchor_is_refused(self):
        report = verify(
            FILES, REQUESTED, [legacy_comment(position=1)], REVIEW_ID, HEAD_SHA
        )
        self.assertTrue(report["failures"])
        self.assertIn(
            "no remote comment with that body sits on that anchor",
            report["failures"][0],
        )

    def test_a_body_that_does_not_match_is_refused(self):
        report = verify(
            FILES,
            REQUESTED,
            [legacy_comment(body="Something else")],
            REVIEW_ID,
            HEAD_SHA,
        )
        self.assertTrue(report["failures"])
        self.assertIn("whose body matches", report["failures"][0])

    def test_a_missing_comment_is_refused(self):
        report = verify(FILES, REQUESTED, [], REVIEW_ID, HEAD_SHA)
        self.assertTrue(report["failures"])

    def test_an_unexpected_comment_is_refused(self):
        report = verify(
            FILES,
            REQUESTED,
            [legacy_comment(), legacy_comment(id=4493860221, position=4)],
            REVIEW_ID,
            HEAD_SHA,
        )
        self.assertTrue(report["failures"])
        self.assertTrue(
            any("was not requested" in failure for failure in report["failures"])
        )

    def test_a_graphql_record_without_the_review_node_id_is_left_out(self):
        report = verify(
            FILES, REQUESTED, [legacy_comment(), graphql_comment()], REVIEW_ID, HEAD_SHA
        )
        self.assertEqual(report["failures"], [])
        self.assertEqual(report["verified"], 1)
        self.assertEqual(report["skipped_remote_comments"]["unattributed"], 1)

    def test_a_graphql_record_of_another_review_is_left_out(self):
        report = verify(
            FILES,
            REQUESTED,
            [legacy_comment(), graphql_comment()],
            REVIEW_ID,
            HEAD_SHA,
            "PRR_other",
        )
        self.assertEqual(report["failures"], [])
        self.assertEqual(report["verified"], 1)
        self.assertEqual(report["skipped_remote_comments"]["unattributed"], 1)

    def test_a_comment_of_another_review_is_ignored(self):
        report = verify(
            FILES,
            REQUESTED,
            [legacy_comment(), legacy_comment(id=1, pull_request_review_id=99)],
            REVIEW_ID,
            HEAD_SHA,
        )
        self.assertEqual(report["failures"], [])
        self.assertEqual(report["verified"], 1)

    def test_a_reply_is_not_counted_as_a_requested_comment(self):
        report = verify(
            FILES,
            REQUESTED,
            [legacy_comment(), legacy_comment(id=7, in_reply_to_id=4493860220)],
            REVIEW_ID,
            HEAD_SHA,
        )
        self.assertEqual(report["failures"], [])
        self.assertEqual(report["remote_replies"], [7])

    def test_a_comment_of_another_commit_is_refused(self):
        report = verify(
            FILES,
            REQUESTED,
            [legacy_comment(commit_id="0" * 40)],
            REVIEW_ID,
            HEAD_SHA,
        )
        self.assertTrue(report["failures"])
        self.assertTrue(any("belongs to commit" in f for f in report["failures"]))

    def test_a_missing_patch_is_refused(self):
        report = verify(
            [{"filename": "src/example.py"}],
            REQUESTED,
            [legacy_comment()],
            REVIEW_ID,
            HEAD_SHA,
        )
        self.assertTrue(report["failures"])
        self.assertTrue(any("omitted the patch" in f for f in report["failures"]))

    def test_a_position_outside_the_patch_is_refused(self):
        report = verify(
            FILES, REQUESTED, [legacy_comment(position=999)], REVIEW_ID, HEAD_SHA
        )
        self.assertTrue(report["failures"])
        self.assertTrue(any("no verifiable anchor" in f for f in report["failures"]))

    def test_two_comments_with_one_body_are_told_apart_by_anchor(self):
        requested = [
            {"path": "src/example.py", "line": 6, "side": "RIGHT", "body": "Same."},
            {"path": "src/example.py", "line": 5, "side": "RIGHT", "body": "Same."},
        ]
        report = verify(
            FILES,
            requested,
            [
                legacy_comment(body="Same.", position=3),
                legacy_comment(id=9, body="Same.", position=1),
            ],
            REVIEW_ID,
            HEAD_SHA,
        )
        self.assertEqual(report["failures"], [])
        self.assertEqual(report["verified"], 2)

    def test_a_requested_line_that_is_not_a_positive_integer_is_refused(self):
        report = verify(FILES, REQUESTED, [legacy_comment()], REVIEW_ID, HEAD_SHA)
        self.assertEqual(report["failures"], [])
        report = verify(
            FILES,
            [
                {
                    "path": "src/example.py",
                    "line": 0,
                    "side": "RIGHT",
                    "body": "Could we?",
                }
            ],
            [legacy_comment()],
            REVIEW_ID,
            HEAD_SHA,
        )
        self.assertTrue(
            any("positive integer" in failure for failure in report["failures"])
        )

    def test_a_requested_side_that_is_not_left_or_right_is_refused(self):
        report = verify(
            FILES,
            [
                {
                    "path": "src/example.py",
                    "line": 6,
                    "side": "left",
                    "body": "Could we?",
                }
            ],
            [legacy_comment()],
            REVIEW_ID,
            HEAD_SHA,
        )
        self.assertTrue(
            any("LEFT or RIGHT" in failure for failure in report["failures"])
        )

    def test_a_remote_comment_with_an_empty_body_is_not_a_match(self):
        report = verify(
            FILES, REQUESTED, [legacy_comment(body="")], REVIEW_ID, HEAD_SHA
        )
        self.assertTrue(report["failures"])

    def test_an_empty_comment_list_is_refused(self):
        with self.assertRaises(VerificationError):
            verify(FILES, [], [legacy_comment()], REVIEW_ID, HEAD_SHA)

    def test_a_files_payload_that_is_not_an_array_is_refused(self):
        with self.assertRaises(VerificationError):
            verify({}, REQUESTED, [legacy_comment()], REVIEW_ID, HEAD_SHA)


class RealDataTest(unittest.TestCase):
    """The shapes GitHub returned for canonical/cpc-medic pull request 4."""

    PATCH = """@@ -40,6 +40,8 @@ var (
 \tfirst
-\tsecond
+\tsecond
+\tthird
 \tfourth
"""

    FILES = [{"filename": "cmd/example.go", "patch": PATCH}]

    def test_the_review_scoped_shape_has_no_line_and_no_side(self):
        remote = [
            {
                "id": 4493860220,
                "pull_request_review_id": 5802085411,
                "path": "cmd/example.go",
                "position": 3,
                "body": "Could we?",
                "commit_id": HEAD_SHA,
            }
        ]
        requested = [
            {"path": "cmd/example.go", "line": 41, "side": "RIGHT", "body": "Could we?"}
        ]
        report = verify(self.FILES, requested, remote, 5802085411, HEAD_SHA)
        self.assertEqual(report["failures"], [])
        self.assertEqual(report["comments"][0]["verified_by"], "diff_position")

    def test_the_pull_request_scoped_shape_has_the_line_and_the_side(self):
        remote = [
            {
                "id": 4493860220,
                "pull_request_review_id": 5802085411,
                "path": "cmd/example.go",
                "position": 3,
                "line": 41,
                "side": "RIGHT",
                "body": "Could we?",
                "commit_id": HEAD_SHA,
            }
        ]
        requested = [
            {"path": "cmd/example.go", "line": 41, "side": "RIGHT", "body": "Could we?"}
        ]
        report = verify(self.FILES, requested, remote, 5802085411, HEAD_SHA)
        self.assertEqual(report["failures"], [])
        self.assertEqual(
            report["comments"][0]["verified_by"], "api_fields_and_diff_position"
        )


if __name__ == "__main__":
    unittest.main()
