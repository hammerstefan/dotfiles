#!/usr/bin/env python3
"""Validate pending-review comment inputs against GitHub PR file patches.

The checks here are the ones a reviewer cannot be trusted to make by eye: that
every anchor is a line GitHub will actually accept, that a body survives the
round trip byte for byte, and that a suggested change is well formed. Wording
is not checked, because the user owns the wording.
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


class ValidationError(ValueError):
    """Raised when input cannot be proven safe and commentable."""


class Fence:
    """One fenced block found in a comment body."""

    def __init__(
        self,
        info: str,
        content: list[str],
        closed: bool,
    ) -> None:
        self.info = info
        self.content = content
        self.closed = closed

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
        blocks.append(Fence(info, lines[index + 1 : cursor], closed))
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
    body: str, side: str, label: str, anchored_text: str | None = None
) -> None:
    """Check that a suggested change can be applied where it is anchored."""
    blocks = check_fences(body, label)
    suggestion = next((block for block in blocks if block.is_suggestion), None)
    if suggestion is None:
        return
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
    if anchored_text is None:
        return
    # The block replaces the anchored lines, so its first line sits where the
    # anchored line sits. A different indent would reformat the line instead
    # of changing it.
    first = suggestion.content[0]
    if leading_space(first) != leading_space(anchored_text):
        raise ValidationError(
            f"{label}.body suggests a change that starts at "
            f"{leading_space(first)!r} while the anchored line starts at "
            f"{leading_space(anchored_text)!r}; a suggested change replaces the "
            "anchored line, so it must keep the line's indentation. Quote the "
            "replacement text instead"
        )


def commentable_lines(patch: str) -> dict[tuple[int, str], str]:
    """The commentable anchors of one file's diff, with their text."""
    try:
        index = build_index(patch)
    except PatchError as exc:
        raise ValidationError(f"cannot read the patch: {exc}") from exc
    return {anchor: index.texts.get(anchor, "") for anchor in index.anchors}


def validate(
    files: Any, comments: Any, allow_literal_backslash_n: bool
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

    allowed_keys = {"path", "line", "side", "body"}
    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str]] = set()
    for index, comment in enumerate(comments):
        label = f"comments[{index}]"
        if not isinstance(comment, dict):
            raise ValidationError(f"{label} must be an object")
        if set(comment) != allowed_keys:
            raise ValidationError(
                f"{label} must contain exactly {sorted(allowed_keys)}"
            )

        path = comment["path"]
        line = comment["line"]
        side = comment["side"]
        body = comment["body"]
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
        anchor = (line, side)
        if not patches[path]:
            raise ValidationError(
                f"cannot validate {label}: GitHub omitted the patch for {path!r}"
            )
        if anchor not in patches[path]:
            raise ValidationError(
                f"{label} anchor {path}:{line} {side} is not commentable in the "
                "retrieved PR patch"
            )
        check_suggestion(body, side, label, patches[path][anchor])
        unique_anchor = (path, line, side)
        if unique_anchor in seen:
            raise ValidationError(f"duplicate comment anchor: {unique_anchor!r}")
        seen.add(unique_anchor)
        normalized.append({"path": path, "line": line, "side": side, "body": body})

    return normalized


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--files", required=True, type=Path)
    parser.add_argument("--comments", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--allow-literal-backslash-n", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        normalized = validate(
            load_json(args.files),
            load_json(args.comments),
            args.allow_literal_backslash_n,
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
    print(f"validated {len(normalized)} comment(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
