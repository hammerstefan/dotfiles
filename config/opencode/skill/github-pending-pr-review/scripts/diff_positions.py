#!/usr/bin/env python3
"""Map GitHub diff positions onto blob line numbers and diff sides.

GitHub documents ``position`` as "the number of lines down from the first '@@'
hunk header in the file". The line just below that first header is position 1.
Every later line of the file's diff consumes one position, and that includes
the header of a later hunk, so the counter never restarts.

That reading was checked against live GitHub data rather than assumed. Eleven
comments on canonical/cpc-medic pull request 4 and one comment on
kubernetes/kubernetes pull request 26, which lands in a third hunk, all map
back to the line and side GitHub reports. Counting later hunk headers as
consuming a position is the only reading that reproduces all of them.

The module also carries the anchor rules used everywhere else: an added line
is on the RIGHT side of the diff, a removed line is on the LEFT side, and an
unchanged context line is on the RIGHT side, which is what GitHub documents
for context lines.

Everything here is deterministic. A patch either maps to a position or it
does not, and the module refuses to guess when the patch is malformed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
NO_NEWLINE_MARKER = "\\"


class PatchError(ValueError):
    """Raised when a patch cannot be parsed into positions."""


class PatchIndex:
    """The commentable anchors of one file's diff and their diff positions."""

    def __init__(
        self,
        anchors: dict[tuple[int, str], int],
        positions: dict[int, tuple[int, str]],
        texts: dict[tuple[int, str], str],
    ) -> None:
        self.anchors = anchors
        self.positions = positions
        self.texts = texts

    def position_of(self, line: int, side: str) -> int | None:
        """The diff position of a blob line and side, or None when absent."""
        return self.anchors.get((line, side))

    def anchor_of(self, position: int) -> tuple[int, str] | None:
        """The blob line and side at a diff position, or None when absent."""
        return self.positions.get(position)

    def text_of(self, line: int, side: str) -> str | None:
        """The text of a blob line, or None when the line is absent."""
        return self.texts.get((line, side))


def build_index(patch: str) -> PatchIndex:
    """Index one file's diff.

    Raises PatchError when the patch has no hunk header or holds a line that
    is neither a hunk header nor a diff line.
    """
    if not isinstance(patch, str) or not patch.strip():
        raise PatchError("patch is empty")

    lines = patch.replace("\r\n", "\n").split("\n")
    lines = [line[:-1] if line.endswith("\r") else line for line in lines]
    if lines and lines[-1] == "":
        # A patch ends with a newline. The blank line it leaves behind is not
        # part of the diff.
        lines.pop()
    first_hunk = None
    for index, line in enumerate(lines):
        if HUNK_RE.match(line):
            first_hunk = index
            break
    if first_hunk is None:
        raise PatchError("patch holds no hunk header")

    anchors: dict[tuple[int, str], int] = {}
    positions: dict[int, tuple[int, str]] = {}
    texts: dict[tuple[int, str], str] = {}

    old_line: int | None = None
    new_line: int | None = None
    for index in range(first_hunk, len(lines)):
        line = lines[index]
        # Position counts lines down from the first hunk header, so the first
        # header is position 0 and the line below it is position 1.
        position = index - first_hunk
        match = HUNK_RE.match(line)
        if match:
            old_line = int(match.group(1))
            new_line = int(match.group(3))
            continue
        if line.startswith(NO_NEWLINE_MARKER):
            # A content line of a unified diff starts with a space, a plus or
            # a minus, so a line that starts with a backslash can only be the
            # marker that says the file has no trailing newline. The marker
            # always follows the line it applies to, so it never changes the
            # position of a commentable line. It still consumes a position,
            # matching the count of every line in the diff.
            continue
        if line.startswith("+"):
            if new_line is None:
                raise PatchError("added line before any hunk header")
            anchor = (new_line, "RIGHT")
            text = line[1:]
            new_line += 1
        elif line.startswith("-"):
            if old_line is None:
                raise PatchError("removed line before any hunk header")
            anchor = (old_line, "LEFT")
            text = line[1:]
            old_line += 1
        elif line.startswith(" "):
            if new_line is None:
                raise PatchError("context line before any hunk header")
            anchor = (new_line, "RIGHT")
            text = line[1:]
            old_line += 1
            new_line += 1
        else:
            raise PatchError(f"unrecognized patch line: {line[:80]!r}")
        if anchor in anchors:
            # Both counters advance monotonically, so a well formed patch
            # never names the same anchor twice. A patch that does is
            # malformed, and a malformed patch is not trusted.
            raise PatchError(f"patch names the anchor {anchor} twice")
        anchors[anchor] = position
        positions[position] = anchor
        texts[anchor] = text

    return PatchIndex(anchors, positions, texts)


def build_indexes(files: Iterable[Any]) -> dict[str, PatchIndex]:
    """Index every changed file that carries a patch."""
    indexes: dict[str, PatchIndex] = {}
    for entry in files:
        if not isinstance(entry, dict):
            continue
        filename = entry.get("filename")
        if not isinstance(filename, str) or not filename:
            continue
        patch = entry.get("patch")
        if not isinstance(patch, str) or not patch.strip():
            continue
        try:
            indexes[filename] = build_index(patch)
        except PatchError:
            continue
    return indexes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--files", required=True, type=Path)
    parser.add_argument("--path", required=True)
    parser.add_argument("--position", required=True, type=int)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        with args.files.open("r", encoding="utf-8") as stream:
            files = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"cannot read valid JSON from {args.files}: {exc}", file=sys.stderr)
        return 1

    indexes = build_indexes(files if isinstance(files, list) else [])
    index = indexes.get(args.path)
    if index is None:
        print(
            f"no usable patch for {args.path!r}; the position cannot be mapped",
            file=sys.stderr,
        )
        return 1

    anchor = index.anchor_of(args.position)
    if anchor is None:
        print(
            f"position {args.position} is not a commentable line in {args.path!r}",
            file=sys.stderr,
        )
        return 1

    line, side = anchor
    result = {"path": args.path, "position": args.position, "line": line, "side": side}
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        try:
            with args.output.open("w", encoding="utf-8") as stream:
                stream.write(text)
        except OSError as exc:
            print(f"cannot write {args.output}: {exc}", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
