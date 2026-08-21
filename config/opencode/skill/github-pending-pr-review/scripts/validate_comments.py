#!/usr/bin/env python3
"""Validate pending-review comment inputs against GitHub PR file patches."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
MAX_BODY_CHARS = 65_536


class ValidationError(ValueError):
    """Raised when input cannot be proven safe and commentable."""


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read valid JSON from {path}: {exc}") from exc


def commentable_anchors(patch: str) -> set[tuple[int, str]]:
    anchors: set[tuple[int, str]] = set()
    old_line: int | None = None
    new_line: int | None = None

    for raw_line in patch.splitlines():
        match = HUNK_RE.match(raw_line)
        if match:
            old_line = int(match.group(1))
            new_line = int(match.group(3))
            continue
        if old_line is None or new_line is None or raw_line.startswith("\\"):
            continue
        if raw_line.startswith("+"):
            anchors.add((new_line, "RIGHT"))
            new_line += 1
        elif raw_line.startswith("-"):
            anchors.add((old_line, "LEFT"))
            old_line += 1
        elif raw_line.startswith(" "):
            # GitHub documents unchanged context lines on the RIGHT side.
            anchors.add((new_line, "RIGHT"))
            old_line += 1
            new_line += 1
        else:
            raise ValidationError(f"unrecognized patch line: {raw_line[:80]!r}")
    return anchors


def validate(
    files: Any, comments: Any, allow_literal_backslash_n: bool
) -> list[dict[str, Any]]:
    if not isinstance(files, list):
        raise ValidationError("files JSON must be an array")
    if not isinstance(comments, list) or not comments:
        raise ValidationError("comments JSON must be a non-empty array")

    patches: dict[str, set[tuple[int, str]]] = {}
    for index, entry in enumerate(files):
        if not isinstance(entry, dict) or not isinstance(entry.get("filename"), str):
            raise ValidationError(f"files[{index}] lacks a string filename")
        filename = entry["filename"]
        if filename in patches:
            raise ValidationError(f"duplicate changed-file entry for {filename!r}")
        patch = entry.get("patch")
        if isinstance(patch, str) and patch:
            patches[filename] = commentable_anchors(patch)
        else:
            patches[filename] = set()

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
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(normalized, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    except (ValidationError, OSError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"validated {len(normalized)} comment(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
