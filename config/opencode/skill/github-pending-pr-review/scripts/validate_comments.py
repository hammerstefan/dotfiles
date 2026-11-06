#!/usr/bin/env python3
"""Validate pending-review comment inputs against GitHub PR file patches.

The checks here are the ones a reviewer cannot be trusted to make by eye: that
every anchor is a line GitHub will actually accept, that a body survives the
round trip byte for byte, and that a suggested change is well formed and
applies to the lines it is anchored to. Wording is not checked, because the
user owns the wording.

A suggested change is a claim about the file's content, so it is checked
against the file. GitHub applies the block of a ``suggestion`` block over the
lines the comment is anchored to: one line when the comment names one line,
the whole range when the comment names a range. A block that repeats the
anchored lines changes nothing, a block that is not the last block of the
comment does not carry the Commit suggestion button, and a block whose fence
is indented is a plain code block. The validator refuses all of them.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from diff_positions import PatchError, build_index  # noqa: E402


MAX_BODY_CHARS = 65_536
SUGGESTION_INFO = "suggestion"
FENCE = "```"
CLOSING_FENCE_RE = re.compile(r"^`{3,}$")
REQUIRED_KEYS = {"path", "line", "side", "body"}
OPTIONAL_KEYS = {"start_line", "start_side"}


class ValidationError(ValueError):
    """Raised when input cannot be proven safe and commentable."""


class Fence:
    """One fenced block found in a comment body."""

    def __init__(
        self,
        info: str,
        content: list[str],
        closed: bool,
        start: int = 0,
        end: int = 0,
    ) -> None:
        self.info = info
        self.content = content
        self.closed = closed
        self.start = start
        self.end = end

    @property
    def is_suggestion(self) -> bool:
        return self.info.lower() == SUGGESTION_INFO


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read valid JSON from {path}: {exc}") from exc


def fenced_blocks(body: str) -> list[Fence]:
    """Return the top-level fenced blocks of a body, in order.

    A fence closes on a line of backticks alone. A line that opens a fence
    with an info string, such as ```` ```suggestion ````, does not close it.

    Each block carries the line numbers it spans, so that the position of a
    suggestion block inside the body can be checked.
    """
    lines = body.split("\n")
    blocks: list[Fence] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped.startswith(FENCE):
            index += 1
            continue
        info = stripped[len(FENCE) :].strip()
        cursor = index + 1
        closed = False
        while cursor < len(lines):
            if CLOSING_FENCE_RE.match(lines[cursor].strip()):
                closed = True
                break
            cursor += 1
        blocks.append(Fence(info, lines[index + 1 : cursor], closed, index, cursor))
        index = cursor + 1 if closed else len(lines)
    return blocks


def check_fences(body: str, label: str) -> list[Fence]:
    """Check the fenced blocks of a body and return them."""
    blocks = fenced_blocks(body)
    for block in blocks:
        if not block.closed:
            raise ValidationError(f"{label}.body holds an unclosed code fence")
    suggestions = [block for block in blocks if block.is_suggestion]
    if len(suggestions) > 1:
        raise ValidationError(
            f"{label}.body holds {len(suggestions)} suggestion blocks; GitHub "
            "applies at most one"
        )
    return blocks


def leading_space(text: str) -> str:
    """The whitespace a line starts with."""
    return text[: len(text) - len(text.lstrip())]


def check_suggestion(
    body: str,
    side: str,
    label: str,
    anchored_lines: list[str],
    allow_indent_change: bool = False,
) -> list[str] | None:
    """Check that a suggested change applies to the lines it is anchored to.

    Returns the lines of the suggestion when the body carries one, and None
    when it carries none. A body without a suggestion is allowed: a comment
    that asks a question without offering an edit is a valid comment.
    """
    blocks = check_fences(body, label)
    suggestion = next((block for block in blocks if block.is_suggestion), None)
    if suggestion is None:
        return None
    if side == "LEFT":
        raise ValidationError(
            f"{label} carries a suggestion block on a LEFT anchor; a suggested "
            "change replaces lines in the file's new content, which a deleted "
            "line does not have. Quote the replacement text instead"
        )
    if not any(line.strip() for line in suggestion.content):
        raise ValidationError(
            f"{label}.body holds an empty suggestion block; a suggested change "
            "must contain the replacement lines"
        )
    if list(suggestion.content) == list(anchored_lines):
        raise ValidationError(
            f"{label}.body repeats the anchored lines unchanged; a suggested "
            "change that changes nothing cannot be committed. Drop the "
            "suggestion block and write the comment in prose"
        )
    if blocks[-1] is not suggestion:
        raise ValidationError(
            f"{label}.body holds a suggestion block that is not the last block; "
            "a suggestion ends the comment, so the explanation belongs above "
            "it and no other block follows it"
        )
    trailing = body.split("\n")[suggestion.end + 1 :]
    if any(line.strip() for line in trailing):
        raise ValidationError(
            f"{label}.body holds text after the suggestion block; a suggestion "
            "ends the comment, so the explanation belongs above it"
        )
    if leading_space(body.split("\n")[suggestion.start]):
        raise ValidationError(
            f"{label}.body opens the suggestion block with an indented fence; "
            "the fence starts in the first column, the way GitHub's own comment "
            "box writes it, so that GitHub reads the block as a suggestion"
        )
    if not allow_indent_change:
        # The block replaces the anchored lines, so its first line sits where
        # the first anchored line sits. A different indent would reformat the
        # line instead of changing it.
        first = suggestion.content[0]
        if leading_space(first) != leading_space(anchored_lines[0]):
            raise ValidationError(
                f"{label}.body suggests a change that starts at "
                f"{leading_space(first)!r} while the anchored line starts at "
                f"{leading_space(anchored_lines[0])!r}; a suggested change "
                "replaces the anchored line, so it must keep the line's "
                "indentation. Quote the replacement text instead, or rerun "
                "the validator with --allow-indent-change when the change is "
                "a deliberate re-indentation"
            )
    return list(suggestion.content)


def commentable_lines(patch: str) -> dict[tuple[int, str], str]:
    """The commentable anchors of one file's diff, with their text."""
    try:
        index = build_index(patch)
    except PatchError as exc:
        raise ValidationError(f"cannot read the patch: {exc}") from exc
    return {anchor: index.texts.get(anchor, "") for anchor in index.anchors}


def suggestion_lines(body: str) -> list[str] | None:
    """The lines of the suggestion block of a body, when it carries one."""
    blocks = fenced_blocks(body)
    suggestion = next((block for block in blocks if block.is_suggestion), None)
    if suggestion is None:
        return None
    return list(suggestion.content)


def validate(
    files: Any,
    comments: Any,
    allow_literal_backslash_n: bool,
    allow_indent_change: bool = False,
) -> list[dict[str, Any]]:
    if not isinstance(files, list):
        raise ValidationError("files JSON must be an array")
    if not isinstance(comments, list) or not comments:
        raise ValidationError("comments JSON must be a non-empty array")

    patches: dict[str, dict[tuple[int, str], str]] = {}
    for index, entry in enumerate(files):
        if not isinstance(entry, dict) or not isinstance(entry.get("filename"), str):
            raise ValidationError(f"files[{index}] lacks a string filename")
        filename = entry["filename"]
        if filename in patches:
            raise ValidationError(f"duplicate changed-file entry for {filename!r}")
        patch = entry.get("patch")
        if isinstance(patch, str) and patch:
            patches[filename] = commentable_lines(patch)
        else:
            patches[filename] = {}

    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str]] = set()
    for index, comment in enumerate(comments):
        label = f"comments[{index}]"
        if not isinstance(comment, dict):
            raise ValidationError(f"{label} must be an object")
        keys = set(comment)
        if not REQUIRED_KEYS <= keys or keys - (REQUIRED_KEYS | OPTIONAL_KEYS):
            raise ValidationError(
                f"{label} must contain exactly {sorted(REQUIRED_KEYS)} and may "
                f"add {sorted(OPTIONAL_KEYS)}"
            )

        path = comment["path"]
        line = comment["line"]
        side = comment["side"]
        body = comment["body"]
        start_line = comment.get("start_line")
        start_side = comment.get("start_side")
        if not isinstance(path, str) or not path or "\x00" in path:
            raise ValidationError(f"{label}.path must be a non-empty string")
        if path not in patches:
            raise ValidationError(f"{label}.path is not a changed file: {path!r}")
        if isinstance(line, bool) or not isinstance(line, int) or line <= 0:
            raise ValidationError(f"{label}.line must be a positive integer")
        if side not in {"LEFT", "RIGHT"}:
            raise ValidationError(f"{label}.side must be LEFT or RIGHT")
        if not isinstance(body, str) or not body.strip():
            raise ValidationError(f"{label}.body must be a non-empty string")
        if len(body) > MAX_BODY_CHARS:
            raise ValidationError(
                f"{label}.body exceeds the {MAX_BODY_CHARS}-character safety limit"
            )
        if "\\n" in body and not allow_literal_backslash_n:
            raise ValidationError(
                f"{label}.body contains literal backslash-n; use real newlines or "
                "explicitly allow literal text"
            )
        if (start_line is None) != (start_side is None):
            raise ValidationError(
                f"{label} must name start_line and start_side together; a range "
                "comment names both"
            )
        if start_line is not None:
            if (
                isinstance(start_line, bool)
                or not isinstance(start_line, int)
                or start_line <= 0
            ):
                raise ValidationError(f"{label}.start_line must be a positive integer")
            if start_side != side:
                raise ValidationError(
                    f"{label}.start_side must be {side}; it names the side of "
                    "the whole range"
                )
            if start_line > line:
                raise ValidationError(
                    f"{label}.start_line must not be after line; line is the "
                    "last line of the range"
                )
        if not patches[path]:
            raise ValidationError(
                f"cannot validate {label}: GitHub omitted the patch for {path!r}"
            )
        first = start_line if start_line is not None else line
        missing = [
            number
            for number in range(first, line + 1)
            if (number, side) not in patches[path]
        ]
        if missing:
            raise ValidationError(
                f"{label} anchor {path}:{line} {side} is not commentable in the "
                f"retrieved PR patch; the lines {missing} are not in the diff, "
                "and a comment covers a contiguous run of the lines that are"
            )
        anchored_lines = [
            patches[path][(number, side)] for number in range(first, line + 1)
        ]
        check_suggestion(body, side, label, anchored_lines, allow_indent_change)
        unique_anchor = (path, line, side)
        if unique_anchor in seen:
            raise ValidationError(f"duplicate comment anchor: {unique_anchor!r}")
        seen.add(unique_anchor)
        normalized.append(
            {
                "path": path,
                "line": line,
                "side": side,
                "body": body,
                **(
                    {"start_line": start_line, "start_side": start_side}
                    if start_line is not None
                    else {}
                ),
            }
        )

    return normalized


def notes(normalized: list[dict[str, Any]], files: Any) -> list[str]:
    """The observations worth a second look, none of them a failure."""
    patches: dict[str, dict[tuple[int, str], str]] = {}
    if isinstance(files, list):
        for entry in files:
            if not isinstance(entry, dict) or not isinstance(
                entry.get("filename"), str
            ):
                continue
            patch = entry.get("patch")
            if isinstance(patch, str) and patch:
                try:
                    patches[entry["filename"]] = commentable_lines(patch)
                except ValidationError:
                    continue

    found: list[str] = []
    for index, comment in enumerate(normalized):
        lines = suggestion_lines(comment["body"])
        if lines is None:
            continue
        start = comment.get("start_line", comment["line"])
        count = comment["line"] - start + 1
        if len(lines) < count:
            found.append(
                f"comments[{index}] suggests {len(lines)} line(s) for a range of "
                f"{count}; every line of the range that the block does not "
                "repeat is deleted when the maintainer commits the suggestion"
            )
    return found


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--files", required=True, type=Path)
    parser.add_argument("--comments", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--allow-literal-backslash-n", action="store_true")
    parser.add_argument(
        "--allow-indent-change",
        action="store_true",
        help=(
            "accept a suggestion whose first line changes the indentation of "
            "the anchored line, for a deliberate re-indentation"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        files = load_json(args.files)
        normalized = validate(
            files,
            load_json(args.comments),
            args.allow_literal_backslash_n,
            args.allow_indent_change,
        )
    except (ValidationError, OSError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1
    try:
        with args.output.open("w", encoding="utf-8") as stream:
            json.dump(normalized, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    except OSError as exc:
        print(f"cannot write {args.output}: {exc}", file=sys.stderr)
        return 1
    with_suggestion = sum(
        1 for comment in normalized if suggestion_lines(comment["body"]) is not None
    )
    print(
        f"validated {len(normalized)} comment(s); {with_suggestion} carry a "
        f"one-click suggestion, {len(normalized) - with_suggestion} do not"
    )
    for note in notes(normalized, files):
        print(f"note: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
