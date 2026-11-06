#!/usr/bin/env python3
"""Print the lines a review comment covers, exactly as the file has them now.

A suggested change replaces the lines its comment is anchored to. Writing one
that applies cleanly means building the replacement from the lines that are
there, not from memory of what the file looked like. This script prints
exactly those lines, taken from the pull request's patch.

The arguments match the comment fields of the review API: ``--line`` is the
last line of the range and ``--start-line`` its first. A comment without a
``start_line`` covers the single line that ``--line`` names.

The plain output is the header, then the lines themselves, one per line,
after a ``text:`` marker. The JSON output holds the same lines as a list.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from diff_positions import PatchError, build_index  # noqa: E402


class AnchorError(ValueError):
    """Raised when the anchored lines cannot be read."""


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AnchorError(f"cannot read valid JSON from {path}: {exc}") from exc


def anchored_lines(
    files: Any, path: str, start_line: int, line: int, side: str
) -> list[str]:
    """The text of the lines the anchor covers, in order."""
    if not isinstance(files, list):
        raise AnchorError("files JSON must be an array")
    for entry in files:
        if not isinstance(entry, dict) or entry.get("filename") != path:
            continue
        patch = entry.get("patch")
        if not isinstance(patch, str) or not patch.strip():
            raise AnchorError(f"GitHub omitted the patch for {path!r}")
        try:
            index = build_index(patch)
        except PatchError as exc:
            raise AnchorError(f"cannot read the patch for {path!r}: {exc}") from exc
        missing = [
            number
            for number in range(start_line, line + 1)
            if (number, side) not in index.texts
        ]
        if missing:
            raise AnchorError(
                f"the diff of {path!r} does not hold the lines {missing} on the "
                f"{side} side"
            )
        return [index.texts[(number, side)] for number in range(start_line, line + 1)]
    raise AnchorError(f"{path!r} is not a changed file of this pull request")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--files", required=True, type=Path)
    parser.add_argument("--path", required=True)
    parser.add_argument(
        "--line",
        required=True,
        type=int,
        help="the last line of the range the comment covers",
    )
    parser.add_argument(
        "--start-line",
        type=int,
        help="the first line of the range the comment covers",
    )
    parser.add_argument("--side", default="RIGHT", choices=["LEFT", "RIGHT"])
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    start_line = args.start_line if args.start_line is not None else args.line
    if start_line > args.line:
        print(
            "the start line of a range must not be after its last line",
            file=sys.stderr,
        )
        return 1
    try:
        lines = anchored_lines(
            load_json(args.files), args.path, start_line, args.line, args.side
        )
    except AnchorError as exc:
        print(f"cannot read the anchored lines: {exc}", file=sys.stderr)
        return 1

    if args.json:
        result = {
            "path": args.path,
            "side": args.side,
            "start_line": start_line,
            "end_line": args.line,
            "count": len(lines),
            "lines": lines,
        }
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        return 0

    print(f"path: {args.path}")
    print(f"side: {args.side}")
    print(f"range: {start_line}..{args.line}")
    print(f"count: {len(lines)}")
    print("text:")
    for text in lines:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
