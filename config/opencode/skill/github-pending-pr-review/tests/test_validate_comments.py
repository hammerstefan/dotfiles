"""Tests for the pending-review comment validator."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_comments import ValidationError, fenced_blocks, validate  # noqa: E402

PATCH = """@@ -5,4 +5,5 @@ def function():
 one
-two
+TWO
 three
 four
"""

FILES = [{"filename": "src/example.py", "patch": PATCH}]

TWO_HUNKS = """@@ -5,2 +5,3 @@ def function():
 one
+TWO
@@ -20,2 +21,3 @@ def other():
 alpha
+beta
"""

TWO_HUNK_FILES = [{"filename": "src/example.py", "patch": TWO_HUNKS}]

COLLABORATIVE_BODY = (
    "Could we make this explicit here?\n"
    "\n"
    "We could change this to:\n"
    "\n"
    "```suggestion\n"
    "TWO, please\n"
    "```\n"
)

SUGGESTION_BODY = "We could change this to:\n\n```suggestion\nTWO, please\n```\n"

QUOTED_BODY = "Could we clarify this?\n\nWe could change this to `TWO`.\n"


def comment(**overrides):
    base = {"path": "src/example.py", "line": 6, "side": "RIGHT", "body": "Hello."}
    base.update(overrides)
    return base


class ValidateTest(unittest.TestCase):
    def test_a_valid_comment_is_accepted(self):
        result = validate(FILES, [comment()], False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["line"], 6)

    def test_the_body_survives_unchanged(self):
        result = validate(FILES, [comment(body=COLLABORATIVE_BODY)], False)
        self.assertEqual(result[0]["body"], COLLABORATIVE_BODY)
        self.assertIn("\n\n", result[0]["body"])
        self.assertNotIn("\\n", result[0]["body"])

    def test_a_collaborative_body_with_a_suggestion_is_accepted(self):
        result = validate(FILES, [comment(body=COLLABORATIVE_BODY)], False)
        self.assertEqual(result[0]["body"], COLLABORATIVE_BODY)

    def test_a_quoted_replacement_is_accepted(self):
        result = validate(FILES, [comment(body=QUOTED_BODY)], False)
        self.assertEqual(result[0]["body"], QUOTED_BODY)

    def test_a_deleted_line_is_accepted_on_the_left_side(self):
        result = validate(FILES, [comment(line=6, side="LEFT")], False)
        self.assertEqual(result[0]["side"], "LEFT")

    def test_a_context_line_is_accepted_on_the_right_side(self):
        result = validate(FILES, [comment(line=5, side="RIGHT")], False)
        self.assertEqual(result[0]["line"], 5)

    def test_a_path_outside_the_changed_files_is_refused(self):
        with self.assertRaises(ValidationError):
            validate(FILES, [comment(path="other.py")], False)

    def test_a_line_outside_the_patch_is_refused(self):
        with self.assertRaises(ValidationError):
            validate(FILES, [comment(line=999)], False)

    def test_an_unsupported_side_is_refused(self):
        with self.assertRaises(ValidationError):
            validate(FILES, [comment(side="MIDDLE")], False)

    def test_a_duplicate_anchor_is_refused(self):
        with self.assertRaises(ValidationError):
            validate(FILES, [comment(), comment()], False)

    def test_a_missing_patch_is_refused(self):
        files = [{"filename": "src/example.py"}]
        with self.assertRaises(ValidationError):
            validate(files, [comment()], False)

    def test_an_unexpected_key_is_refused(self):
        with self.assertRaises(ValidationError):
            validate(FILES, [comment(extra="value")], False)

    def test_an_empty_body_is_refused(self):
        with self.assertRaises(ValidationError):
            validate(FILES, [comment(body="   ")], False)

    def test_literal_backslash_n_is_refused_by_default(self):
        with self.assertRaises(ValidationError):
            validate(FILES, [comment(body="First.\\n\\nSecond.")], False)

    def test_literal_backslash_n_is_allowed_when_asked_for(self):
        result = validate(FILES, [comment(body="First.\\n\\nSecond.")], True)
        self.assertEqual(result[0]["body"], "First.\\n\\nSecond.")

    def test_an_empty_comment_list_is_refused(self):
        with self.assertRaises(ValidationError):
            validate(FILES, [], False)


class RangeCommentTest(unittest.TestCase):
    """A range comment names the first line of the range it covers."""

    def test_a_range_comment_is_accepted(self):
        result = validate(
            FILES,
            [comment(line=7, side="RIGHT", start_line=6, start_side="RIGHT")],
            False,
        )
        self.assertEqual(result[0]["start_line"], 6)
        self.assertEqual(result[0]["start_side"], "RIGHT")
        self.assertEqual(result[0]["line"], 7)

    def test_a_comment_without_a_range_carries_no_start_line(self):
        result = validate(FILES, [comment()], False)
        self.assertNotIn("start_line", result[0])
        self.assertNotIn("start_side", result[0])

    def test_a_start_line_without_a_start_side_is_refused(self):
        with self.assertRaises(ValidationError) as caught:
            validate(FILES, [comment(start_line=6)], False)
        self.assertIn("together", str(caught.exception))

    def test_a_start_side_without_a_start_line_is_refused(self):
        with self.assertRaises(ValidationError):
            validate(FILES, [comment(start_side="RIGHT")], False)

    def test_a_start_side_that_differs_from_the_side_is_refused(self):
        with self.assertRaises(ValidationError) as caught:
            validate(FILES, [comment(start_line=6, start_side="LEFT")], False)
        self.assertIn("start_side", str(caught.exception))

    def test_a_start_line_after_the_last_line_is_refused(self):
        with self.assertRaises(ValidationError) as caught:
            validate(FILES, [comment(line=6, start_line=7, start_side="RIGHT")], False)
        self.assertIn("must not be after line", str(caught.exception))

    def test_a_start_line_that_is_not_a_positive_integer_is_refused(self):
        with self.assertRaises(ValidationError):
            validate(FILES, [comment(start_line=0, start_side="RIGHT")], False)

    def test_a_range_that_spans_a_gap_in_the_diff_is_refused(self):
        with self.assertRaises(ValidationError) as caught:
            validate(
                TWO_HUNK_FILES,
                [comment(line=21, side="RIGHT", start_line=6, start_side="RIGHT")],
                False,
            )
        self.assertIn("contiguous", str(caught.exception))

    def test_a_range_that_ends_outside_the_diff_is_refused(self):
        with self.assertRaises(ValidationError):
            validate(
                TWO_HUNK_FILES,
                [comment(line=99, side="RIGHT", start_line=21, start_side="RIGHT")],
                False,
            )


class SuggestionBlockTest(unittest.TestCase):
    def test_a_well_formed_suggestion_is_accepted(self):
        result = validate(FILES, [comment(body=SUGGESTION_BODY)], False)
        self.assertEqual(len(result), 1)

    def test_a_suggestion_on_a_deleted_line_is_refused(self):
        with self.assertRaises(ValidationError) as caught:
            validate(
                FILES,
                [comment(line=6, side="LEFT", body=SUGGESTION_BODY)],
                False,
            )
        self.assertIn("LEFT", str(caught.exception))

    def test_an_unclosed_suggestion_is_refused(self):
        body = "We could change this to:\n\n```suggestion\nTWO, please\n"
        with self.assertRaises(ValidationError):
            validate(FILES, [comment(body=body)], False)

    def test_two_suggestions_are_refused(self):
        body = "```suggestion\nTWO, please\n```\n\n```suggestion\nTHREE\n```\n"
        with self.assertRaises(ValidationError):
            validate(FILES, [comment(body=body)], False)

    def test_an_empty_suggestion_is_refused(self):
        body = "We could change this to:\n\n```suggestion\n```\n"
        with self.assertRaises(ValidationError):
            validate(FILES, [comment(body=body)], False)

    def test_a_suggestion_inside_a_quoted_code_block_is_not_a_suggestion(self):
        body = (
            "The example reads:\n\n```text\nuse the word ```suggestion``` here\n```\n"
        )
        blocks = fenced_blocks(body)
        self.assertEqual(len(blocks), 1)
        self.assertFalse(blocks[0].is_suggestion)
        validate(FILES, [comment(body=body)], False)

    def test_a_plain_code_block_is_accepted(self):
        body = "The example reads:\n\n```python\nprint('x')\n```\n"
        result = validate(FILES, [comment(body=body)], False)
        self.assertEqual(len(result), 1)


class SuggestionShapeTest(unittest.TestCase):
    """A suggestion has to be a change GitHub can commit in one click."""

    def test_a_suggestion_that_repeats_the_anchored_line_is_refused(self):
        body = "We could change this to:\n\n```suggestion\nTWO\n```\n"
        with self.assertRaises(ValidationError) as caught:
            validate(FILES, [comment(body=body)], False)
        self.assertIn("changes nothing", str(caught.exception))

    def test_a_suggestion_that_repeats_the_anchored_range_is_refused(self):
        body = "We could change this to:\n\n```suggestion\nTWO\nthree\n```\n"
        with self.assertRaises(ValidationError):
            validate(
                FILES,
                [comment(line=7, start_line=6, start_side="RIGHT", body=body)],
                False,
            )

    def test_a_suggestion_that_is_not_the_last_block_is_refused(self):
        body = "```suggestion\nTWO, please\n```\n\n```python\nprint('x')\n```\n"
        with self.assertRaises(ValidationError) as caught:
            validate(FILES, [comment(body=body)], False)
        self.assertIn("last block", str(caught.exception))

    def test_text_after_the_suggestion_block_is_refused(self):
        body = "We could change this to:\n\n```suggestion\nTWO, please\n```\n\nDone.\n"
        with self.assertRaises(ValidationError) as caught:
            validate(FILES, [comment(body=body)], False)
        self.assertIn("after the suggestion block", str(caught.exception))

    def test_an_indented_suggestion_fence_is_refused(self):
        body = "We could change this to:\n\n  ```suggestion\n  TWO, please\n  ```\n"
        with self.assertRaises(ValidationError) as caught:
            validate(FILES, [comment(body=body)], False)
        self.assertIn("first column", str(caught.exception))

    def test_a_suggestion_that_keeps_the_anchored_lines_around_the_change(self):
        body = "We could change this to:\n\n```suggestion\nTWO, please\nthree\n```\n"
        result = validate(
            FILES,
            [comment(line=7, start_line=6, start_side="RIGHT", body=body)],
            False,
        )
        self.assertEqual(len(result), 1)


class FencedBlocksTest(unittest.TestCase):
    def test_blocks_are_found_in_order(self):
        blocks = fenced_blocks("a\n```suggestion\nx\n```\nb\n```python\ny\n```\n")
        self.assertEqual(len(blocks), 2)
        self.assertTrue(blocks[0].is_suggestion)
        self.assertFalse(blocks[1].is_suggestion)

    def test_an_unclosed_block_is_reported(self):
        blocks = fenced_blocks("```suggestion\nx\n")
        self.assertFalse(blocks[0].closed)

    def test_a_block_carries_the_lines_it_spans(self):
        blocks = fenced_blocks("a\n```suggestion\nx\n```\n")
        self.assertEqual(blocks[0].start, 1)
        self.assertEqual(blocks[0].end, 3)


class SuggestionIndentTest(unittest.TestCase):
    """A suggested change replaces the anchored line, so it keeps its indent."""

    INDENTED_PATCH = """@@ -1,3 +1,4 @@
 def function():
-    old
+    new
     keep
"""

    FILES = [{"filename": "src/example.py", "patch": INDENTED_PATCH}]

    def test_a_suggestion_with_the_same_indent_is_accepted(self):
        body = "Could we rename this?\n\n```suggestion\n    renamed\n```\n"
        result = validate(self.FILES, [comment(line=2, body=body)], False)
        self.assertEqual(len(result), 1)

    def test_a_suggestion_that_drops_the_indent_is_refused(self):
        body = "Could we rename this?\n\n```suggestion\nrenamed\n```\n"
        with self.assertRaises(ValidationError) as caught:
            validate(self.FILES, [comment(line=2, body=body)], False)
        self.assertIn("indentation", str(caught.exception))

    def test_a_suggestion_that_adds_indent_is_refused(self):
        body = "Could we rename this?\n\n```suggestion\n        renamed\n```\n"
        with self.assertRaises(ValidationError):
            validate(self.FILES, [comment(line=2, body=body)], False)

    def test_a_deliberate_re_indentation_is_accepted_when_asked_for(self):
        body = "Could we dedent this?\n\n```suggestion\nrenamed\n```\n"
        result = validate(self.FILES, [comment(line=2, body=body)], False, True)
        self.assertEqual(len(result), 1)

    def test_a_quoted_replacement_is_not_checked_for_indent(self):
        body = "Could we rename this?\n\nWe could change this to `renamed`.\n"
        result = validate(self.FILES, [comment(line=2, body=body)], False)
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
