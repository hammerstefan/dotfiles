"""Tests for the command line behavior of the bundled scripts."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL / "scripts"

PATCH = """@@ -5,4 +5,5 @@ def function():
 one
-two
+TWO
 three
 four
"""

FILES = [{"filename": "src/example.py", "patch": PATCH}]

COMMENTS = [{"path": "src/example.py", "line": 6, "side": "RIGHT", "body": "Could we?"}]

REMOTE = [
    {
        "id": 1,
        "pull_request_review_id": 42,
        "path": "src/example.py",
        "position": 3,
        "body": "Could we?",
        "commit_id": "abc",
    }
]


def run(script, *arguments):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )


class ValidatorCommandTest(unittest.TestCase):
    def test_the_validator_writes_the_validated_list(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = root / "files.json"
            comments = root / "comments.json"
            output = root / "out.json"
            files.write_text(json.dumps(FILES), encoding="utf-8")
            comments.write_text(json.dumps(COMMENTS), encoding="utf-8")
            result = run(
                "validate_comments.py",
                "--files",
                str(files),
                "--comments",
                str(comments),
                "--output",
                str(output),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text()), COMMENTS)

    def test_the_validator_overwrites_its_output_on_a_rerun(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = root / "files.json"
            comments = root / "comments.json"
            output = root / "out.json"
            files.write_text(json.dumps(FILES), encoding="utf-8")
            comments.write_text(json.dumps(COMMENTS), encoding="utf-8")
            for _ in range(2):
                result = run(
                    "validate_comments.py",
                    "--files",
                    str(files),
                    "--comments",
                    str(comments),
                    "--output",
                    str(output),
                )
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text()), COMMENTS)

    def test_the_validator_reports_a_bad_anchor_without_writing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = root / "files.json"
            comments = root / "comments.json"
            output = root / "out.json"
            files.write_text(json.dumps(FILES), encoding="utf-8")
            comments.write_text(
                json.dumps([dict(COMMENTS[0], line=999)]), encoding="utf-8"
            )
            result = run(
                "validate_comments.py",
                "--files",
                str(files),
                "--comments",
                str(comments),
                "--output",
                str(output),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("not commentable", result.stderr)
            self.assertFalse(output.exists())

    def test_the_validator_reports_the_suggestion_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = root / "files.json"
            comments = root / "comments.json"
            output = root / "out.json"
            files.write_text(json.dumps(FILES), encoding="utf-8")
            comments.write_text(
                json.dumps(
                    [
                        dict(
                            COMMENTS[0],
                            body="Could we rename this?\n\n```suggestion\nTWO, please\n```\n",
                        ),
                        dict(COMMENTS[0], line=5),
                    ]
                ),
                encoding="utf-8",
            )
            result = run(
                "validate_comments.py",
                "--files",
                str(files),
                "--comments",
                str(comments),
                "--output",
                str(output),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("1 carry a one-click suggestion", result.stdout)
            self.assertIn("1 do not", result.stdout)

    def test_the_validator_refuses_a_suggestion_that_changes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = root / "files.json"
            comments = root / "comments.json"
            output = root / "out.json"
            files.write_text(json.dumps(FILES), encoding="utf-8")
            comments.write_text(
                json.dumps([dict(COMMENTS[0], body="```suggestion\nTWO\n```\n")]),
                encoding="utf-8",
            )
            result = run(
                "validate_comments.py",
                "--files",
                str(files),
                "--comments",
                str(comments),
                "--output",
                str(output),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("changes nothing", result.stderr)
            self.assertFalse(output.exists())

    def test_the_validator_accepts_a_deliberate_re_indentation_with_the_flag(self):
        indented = [
            {
                "filename": "src/example.py",
                "patch": "@@ -1,2 +1,2 @@\n-    old\n+    new\n",
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = root / "files.json"
            comments = root / "comments.json"
            output = root / "out.json"
            files.write_text(json.dumps(indented), encoding="utf-8")
            comments.write_text(
                json.dumps(
                    [
                        {
                            "path": "src/example.py",
                            "line": 1,
                            "side": "RIGHT",
                            "body": "Could we dedent this?\n\n```suggestion\nnew\n```\n",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            result = run(
                "validate_comments.py",
                "--files",
                str(files),
                "--comments",
                str(comments),
                "--output",
                str(output),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("indentation", result.stderr)

            result = run(
                "validate_comments.py",
                "--files",
                str(files),
                "--comments",
                str(comments),
                "--output",
                str(output),
                "--allow-indent-change",
            )
            self.assertEqual(result.returncode, 0, result.stderr)


class AnchorTextCommandTest(unittest.TestCase):
    def test_it_prints_the_anchored_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = root / "files.json"
            files.write_text(json.dumps(FILES), encoding="utf-8")
            result = run(
                "anchor_text.py",
                "--files",
                str(files),
                "--path",
                "src/example.py",
                "--line",
                "6",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("range: 6..6", result.stdout)
            self.assertIn("TWO", result.stdout)

    def test_it_prints_json_on_request(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = root / "files.json"
            files.write_text(json.dumps(FILES), encoding="utf-8")
            result = run(
                "anchor_text.py",
                "--files",
                str(files),
                "--path",
                "src/example.py",
                "--line",
                "7",
                "--start-line",
                "6",
                "--json",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["lines"], ["TWO", "three"])
            self.assertEqual(payload["start_line"], 6)
            self.assertEqual(payload["end_line"], 7)

    def test_it_refuses_a_line_outside_the_patch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = root / "files.json"
            files.write_text(json.dumps(FILES), encoding="utf-8")
            result = run(
                "anchor_text.py",
                "--files",
                str(files),
                "--path",
                "src/example.py",
                "--line",
                "99",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("does not hold", result.stderr)


class VerifierCommandTest(unittest.TestCase):
    def test_the_verifier_prints_the_report_as_json_on_standard_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = root / "files.json"
            comments = root / "comments.json"
            remote = root / "remote.json"
            files.write_text(json.dumps(FILES), encoding="utf-8")
            comments.write_text(json.dumps(COMMENTS), encoding="utf-8")
            remote.write_text(json.dumps(REMOTE), encoding="utf-8")
            result = run(
                "verify_review.py",
                "--files",
                str(files),
                "--comments",
                str(comments),
                "--remote",
                str(remote),
                "--review-id",
                "42",
                "--head-sha",
                "abc",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["verified"], 1)
            self.assertEqual(report["failures"], [])

    def test_the_verifier_overwrites_its_output_on_a_rerun(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = root / "files.json"
            comments = root / "comments.json"
            remote = root / "remote.json"
            output = root / "verification.json"
            files.write_text(json.dumps(FILES), encoding="utf-8")
            comments.write_text(json.dumps(COMMENTS), encoding="utf-8")
            remote.write_text(json.dumps(REMOTE), encoding="utf-8")
            for _ in range(2):
                result = run(
                    "verify_review.py",
                    "--files",
                    str(files),
                    "--comments",
                    str(comments),
                    "--remote",
                    str(remote),
                    "--review-id",
                    "42",
                    "--head-sha",
                    "abc",
                    "--output",
                    str(output),
                )
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text())["verified"], 1)

    def test_the_verifier_reports_an_unverifiable_anchor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = root / "files.json"
            comments = root / "comments.json"
            remote = root / "remote.json"
            files.write_text(json.dumps(FILES), encoding="utf-8")
            comments.write_text(json.dumps(COMMENTS), encoding="utf-8")
            remote.write_text(
                json.dumps([dict(REMOTE[0], position=999)]), encoding="utf-8"
            )
            result = run(
                "verify_review.py",
                "--files",
                str(files),
                "--comments",
                str(comments),
                "--remote",
                str(remote),
                "--review-id",
                "42",
                "--head-sha",
                "abc",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("unverified", result.stderr)


if __name__ == "__main__":
    unittest.main()
