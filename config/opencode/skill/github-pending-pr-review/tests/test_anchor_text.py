"""Tests for the helper that prints the lines a comment covers."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from anchor_text import AnchorError, anchored_lines  # noqa: E402

PATCH = """@@ -5,4 +5,5 @@ def function():
 one
-two
+TWO
 three
 four
"""

FILES = [{"filename": "src/example.py", "patch": PATCH}]


class AnchoredLinesTest(unittest.TestCase):
    def test_one_line_is_returned(self):
        lines = anchored_lines(FILES, "src/example.py", 6, 6, "RIGHT")
        self.assertEqual(lines, ["TWO"])

    def test_a_range_is_returned_in_order(self):
        lines = anchored_lines(FILES, "src/example.py", 6, 7, "RIGHT")
        self.assertEqual(lines, ["TWO", "three"])

    def test_the_left_side_holds_the_old_text(self):
        lines = anchored_lines(FILES, "src/example.py", 6, 6, "LEFT")
        self.assertEqual(lines, ["two"])

    def test_the_text_keeps_its_indentation(self):
        indented = [
            {"filename": "src/example.py", "patch": "@@ -1,1 +1,1 @@\n+    old\n"}
        ]
        lines = anchored_lines(indented, "src/example.py", 1, 1, "RIGHT")
        self.assertEqual(lines, ["    old"])

    def test_a_file_outside_the_pull_request_is_refused(self):
        with self.assertRaises(AnchorError):
            anchored_lines(FILES, "other.py", 6, 6, "RIGHT")

    def test_a_line_outside_the_patch_is_refused(self):
        with self.assertRaises(AnchorError):
            anchored_lines(FILES, "src/example.py", 99, 99, "RIGHT")

    def test_a_range_that_spans_a_gap_in_the_diff_is_refused(self):
        two_hunks = [
            {
                "filename": "src/example.py",
                "patch": "@@ -1,1 +1,2 @@\n one\n+two\n@@ -9,1 +10,2 @@\n nine\n+ten\n",
            }
        ]
        with self.assertRaises(AnchorError):
            anchored_lines(two_hunks, "src/example.py", 2, 10, "RIGHT")

    def test_a_files_payload_that_is_not_an_array_is_refused(self):
        with self.assertRaises(AnchorError):
            anchored_lines({}, "src/example.py", 6, 6, "RIGHT")

    def test_a_file_without_a_patch_is_refused(self):
        with self.assertRaises(AnchorError):
            anchored_lines(
                [{"filename": "src/example.py"}], "src/example.py", 6, 6, "RIGHT"
            )


if __name__ == "__main__":
    unittest.main()
