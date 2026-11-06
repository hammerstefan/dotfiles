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
