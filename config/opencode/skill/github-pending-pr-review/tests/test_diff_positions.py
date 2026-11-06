"""Tests for the diff position mapping.

The positions in the fixture below were computed by hand from GitHub's
documented rule, and the same rule was checked against live GitHub data while
the skill was being written.
"""

import json
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from diff_positions import PatchError, build_index, build_indexes  # noqa: E402

# Three hunks. Positions count lines down from the first hunk header, so the
# first header is position 0 and every later line, including the header of a
# later hunk, consumes one position.
#
#   pos 0  @@ -1,3 +1,4 @@
#   pos 1   alpha            RIGHT new line 1
#   pos 2  -beta             LEFT  old line 2
#   pos 3  +BETA             RIGHT new line 2
#   pos 4  +GAMMA            RIGHT new line 3
#   pos 5   gamma            RIGHT new line 4
#   pos 6  @@ -10,2 +11,3 @@
#   pos 7   delta            RIGHT new line 11
#   pos 8  +epsilon          RIGHT new line 12
#   pos 9   zeta             RIGHT new line 13
#   pos 10 @@ -20,3 +22,2 @@
#   pos 11  eta              RIGHT new line 22
#   pos 12  theta            RIGHT new line 23
#   pos 13 -iota             LEFT  old line 22
#   pos 14 \ No newline at end of file
MULTI_HUNK_PATCH = """@@ -1,3 +1,4 @@
 alpha
-beta
+BETA
+GAMMA
 gamma
@@ -10,2 +11,3 @@
 delta
+epsilon
 zeta
@@ -20,3 +22,2 @@
 eta
 theta
-iota
\\ No newline at end of file
"""

SINGLE_HUNK_PATCH = """@@ -5,4 +5,5 @@ def function():
 one
-two
+TWO
 three
 four
"""


class BuildIndexTest(unittest.TestCase):
    def test_positions_follow_the_documented_rule(self):
        index = build_index(MULTI_HUNK_PATCH)
        self.assertEqual(index.anchor_of(0), None)
        self.assertEqual(index.anchor_of(1), (1, "RIGHT"))
        self.assertEqual(index.anchor_of(2), (2, "LEFT"))
        self.assertEqual(index.anchor_of(3), (2, "RIGHT"))
        self.assertEqual(index.anchor_of(4), (3, "RIGHT"))
        self.assertEqual(index.anchor_of(5), (4, "RIGHT"))
        self.assertEqual(index.anchor_of(6), None)
        self.assertEqual(index.anchor_of(7), (11, "RIGHT"))
        self.assertEqual(index.anchor_of(8), (12, "RIGHT"))
        self.assertEqual(index.anchor_of(9), (13, "RIGHT"))
        self.assertEqual(index.anchor_of(10), None)
        self.assertEqual(index.anchor_of(11), (22, "RIGHT"))
        self.assertEqual(index.anchor_of(12), (23, "RIGHT"))
        self.assertEqual(index.anchor_of(13), (22, "LEFT"))
        self.assertEqual(index.anchor_of(14), None)

    def test_anchor_and_position_are_inverses(self):
        index = build_index(MULTI_HUNK_PATCH)
        for (line, side), position in index.anchors.items():
            self.assertEqual(index.anchor_of(position), (line, side))
            self.assertEqual(index.position_of(line, side), position)

    def test_a_later_hunk_header_consumes_a_position(self):
        index = build_index(MULTI_HUNK_PATCH)
        # Position 6 is the header of the second hunk, so the first line of
        # that hunk is position 7 and not position 6.
        self.assertIsNone(index.anchor_of(6))
        self.assertEqual(index.anchor_of(7), (11, "RIGHT"))

    def test_no_newline_marker_is_not_commentable(self):
        index = build_index(MULTI_HUNK_PATCH)
        # The marker follows the line it applies to, so it holds the next
        # position and names no anchor of its own.
        self.assertIsNone(index.anchor_of(14))
        self.assertEqual(len(index.anchors), 11)

    def test_context_lines_are_on_the_right_side(self):
        index = build_index(SINGLE_HUNK_PATCH)
        self.assertEqual(index.anchor_of(1), (5, "RIGHT"))
        self.assertEqual(index.anchor_of(2), (6, "LEFT"))
        self.assertEqual(index.anchor_of(3), (6, "RIGHT"))
        self.assertEqual(index.anchor_of(4), (7, "RIGHT"))

    def test_a_patch_without_a_hunk_header_is_refused(self):
        with self.assertRaises(PatchError):
            build_index(" just some text\n")

    def test_an_empty_patch_is_refused(self):
        with self.assertRaises(PatchError):
            build_index("   \n")

    def test_an_unrecognized_patch_line_is_refused(self):
        with self.assertRaises(PatchError):
            build_index("@@ -1,2 +1,2 @@\n?broken\n")

    def test_a_patch_with_leading_lines_still_counts_from_the_header(self):
        index = build_index("diff --git a/f b/f\n" + SINGLE_HUNK_PATCH)
        self.assertEqual(index.anchor_of(1), (5, "RIGHT"))

    def test_a_patch_that_names_one_anchor_twice_is_refused(self):
        patch = "@@ -1,2 +1,2 @@\n alpha\n@@ -1,2 +1,2 @@\n alpha\n"
        with self.assertRaises(PatchError):
            build_index(patch)

    def test_a_patch_with_carriage_returns_is_read(self):
        index = build_index(SINGLE_HUNK_PATCH.replace("\n", "\r\n"))
        self.assertEqual(index.anchor_of(3), (6, "RIGHT"))

    def test_build_indexes_skips_files_without_a_patch(self):
        files = [
            {"filename": "with-patch.txt", "patch": SINGLE_HUNK_PATCH},
            {"filename": "without-patch.txt"},
            {"filename": "empty-patch.txt", "patch": ""},
        ]
        indexes = build_indexes(files)
        self.assertEqual(list(indexes), ["with-patch.txt"])


class CommandLineTest(unittest.TestCase):
    def test_the_command_line_reports_the_anchor(self):
        import subprocess
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            files = Path(directory) / "files.json"
            files.write_text(
                json.dumps([{"filename": "a.txt", "patch": SINGLE_HUNK_PATCH}]),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(
                        Path(__file__).resolve().parent.parent
                        / "scripts"
                        / "diff_positions.py"
                    ),
                    "--files",
                    str(files),
                    "--path",
                    "a.txt",
                    "--position",
                    "3",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {"path": "a.txt", "position": 3, "line": 6, "side": "RIGHT"},
        )

    def test_the_command_line_overwrites_its_output_on_a_rerun(self):
        import subprocess
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            files = Path(directory) / "files.json"
            output = Path(directory) / "out.json"
            files.write_text(
                json.dumps([{"filename": "a.txt", "patch": SINGLE_HUNK_PATCH}]),
                encoding="utf-8",
            )
            script = str(
                Path(__file__).resolve().parent.parent / "scripts" / "diff_positions.py"
            )
            for _ in range(2):
                result = subprocess.run(
                    [
                        sys.executable,
                        script,
                        "--files",
                        str(files),
                        "--path",
                        "a.txt",
                        "--position",
                        "3",
                        "--output",
                        str(output),
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(output.read_text()),
                {"path": "a.txt", "position": 3, "line": 6, "side": "RIGHT"},
            )


if __name__ == "__main__":
    unittest.main()
