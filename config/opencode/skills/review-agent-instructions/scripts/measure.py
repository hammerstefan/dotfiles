#!/usr/bin/env python3
"""Measure the mechanical parts of a skill or an agent instruction.

Usage:
    measure.py PATH [PATH ...]
    measure.py --json PATH [PATH ...]

A directory is read as <dir>/SKILL.md. Exit 1 when a hard rule fails:
missing frontmatter, a missing name or description, a name that does not
match the skill directory, a description over 60 words, or a description
sentence over 25 words. Placeholders, style characters and body size are
reported, never fatal: a skill may document a template, and the
repository's linter owns the style rules.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DESCRIPTION_WORDS = 60
SENTENCE_WORDS = 25


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, text
    meta: dict[str, str] = {}
    index = 1
    while index < end:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", lines[index])
        if not match:
            index += 1
            continue
        key, value = match.group(1), match.group(2).strip()
        if value in (">", "|", ">-", "|-"):
            block: list[str] = []
            index += 1
            while index < end and (
                lines[index].startswith(" ") or not lines[index].strip()
            ):
                block.append(lines[index].strip())
                index += 1
            value = " ".join(part for part in block if part)
        elif len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        meta[key] = value
        index += 1
    return meta, "\n".join(lines[end + 1 :])


def words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def sentences(text: str) -> list[str]:
    return [part for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part]


def measure(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    meta, body = split_frontmatter(text)
    description = meta.get("description", "")
    description_parts = sentences(description)
    longest = max((words(part) for part in description_parts), default=0)
    hard: list[str] = []
    is_skill = path.name == "SKILL.md"

    if is_skill:
        if not meta:
            hard.append("no frontmatter")
        if not meta.get("name"):
            hard.append("no name in the frontmatter")
        if not description:
            hard.append("no description in the frontmatter")
        if meta.get("name") and meta["name"] != path.parent.name:
            hard.append(
                f"name {meta['name']!r} does not match the directory "
                f"{path.parent.name!r}"
            )
        if words(description) > DESCRIPTION_WORDS:
            hard.append(
                f"the description has {words(description)} words "
                f"(budget {DESCRIPTION_WORDS})"
            )
        for part in description_parts:
            if words(part) > SENTENCE_WORDS:
                hard.append(
                    f"a description sentence has {words(part)} words "
                    f"(budget {SENTENCE_WORDS}): {part[:80]!r}"
                )

    placeholders = len(re.findall(r"\{\{[^}]+\}\}", text))

    return {
        "path": str(path),
        "name": meta.get("name", ""),
        "name_matches": (not is_skill) or meta.get("name") == path.parent.name,
        "description_words": words(description),
        "description_sentences": len(description_parts),
        "longest_sentence": longest,
        "body_words": words(body),
        "body_lines": len(body.splitlines()),
        "placeholders": placeholders,
        "em_dashes": text.count("\u2014"),
        "semicolons": text.count(";"),
        "hard": hard,
    }


def show(result: dict) -> None:
    print(result["path"])
    if result["name"]:
        state = "ok" if result["name_matches"] else "MISMATCH"
        print(f"  name          {result['name']}  ({state})")
    print(
        f"  description   {result['description_words']} words, "
        f"{result['description_sentences']} sentences, "
        f"longest {result['longest_sentence']}"
    )
    print(f"  body          {result['body_words']} words, {result['body_lines']} lines")
    print(f"  placeholders  {result['placeholders']}")
    print(f"  em dashes     {result['em_dashes']}")
    print(f"  semicolons    {result['semicolons']}")
    if result["hard"]:
        print("  hard          FAIL")
        for problem in result["hard"]:
            print(f"                - {problem}")
    else:
        print("  hard          none")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", metavar="PATH")
    parser.add_argument("--json", action="store_true", help="print JSON")
    args = parser.parse_args()

    results = []
    for raw in args.paths:
        path = Path(raw)
        if path.is_dir():
            path = path / "SKILL.md"
        if not path.is_file():
            print(f"measure: {path} is missing", file=sys.stderr)
            return 2
        results.append(measure(path))

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            show(result)
            print()

    return 1 if any(result["hard"] for result in results) else 0


if __name__ == "__main__":
    sys.exit(main())
