#!/usr/bin/env python3
"""Verify that every quote in clusters-v2.md resolves in its session transcript.

Each evidence bullet must have this shape, on one line:

    - `ses_<id>` line <n>: "<quote>"

The quote is checked against `flat/<id>.txt` in the new state directory first and
in the old state directory second. Exit 0 when every quote resolves, 1 otherwise.

    verify_quotes.py clusters-v2.md

Output, one line per quote:

    OK   <id> line <n>            exact match at the anchored line
    MOVE <id> line <n> -> <m>     exact match, but at another line
    FAIL <id> line <n>            no exact match anywhere in the transcript
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

NEW = Path("/tmp/opencode/learn-from-sessions-eval/flat")
OLD = Path("/tmp/opencode/hwt-wrapup-monitor-agent/flat")

BULLET = re.compile(
    r'^- `(?P<id>ses_[A-Za-z0-9]+)` (?P<kind>digest )?line (?P<line>\d+): "(?P<q>.*)"\s*$'
)

DIGEST_BASES = [
    Path("/tmp/opencode/learn-from-sessions-eval/digests"),
    Path("/tmp/opencode/hwt-wrapup-monitor-agent/digests"),
]


def norm(text: str) -> str:
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def transcript(sid: str) -> list[str] | None:
    for base in (NEW, OLD):
        path = base / f"{sid}.txt"
        if path.exists():
            return path.read_text(errors="replace").splitlines()
    return None


def digest(sid: str) -> list[str] | None:
    for base in DIGEST_BASES:
        path = base / f"{sid}.md"
        if path.exists():
            return path.read_text(errors="replace").splitlines()
    return None


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: verify_quotes.py <clusters.md>", file=sys.stderr)
        return 2
    text = Path(sys.argv[1]).read_text()
    lines = [ln.rstrip("\n") for ln in text.splitlines()]
    checked = ok = 0
    failures: list[str] = []
    for raw in lines:
        m = BULLET.match(raw)
        if not m:
            continue
        checked += 1
        sid = m.group("id")
        n = int(m.group("line"))
        is_digest = bool(m.group("kind"))
        quote = norm(m.group("q"))
        if len(quote) < 12:
            print(f"FAIL {sid} line {n}: quote is too short to verify")
            failures.append(raw)
            continue
        body = digest(sid) if is_digest else transcript(sid)
        if body is None:
            print(
                f"FAIL {sid} line {n}: no {'digest' if is_digest else 'transcript'} found"
            )
            failures.append(raw)
            continue
        window = norm(" ".join(body[max(0, n - 3) : n + 2]))
        if quote in window:
            print(f"OK   {sid} line {n}")
            ok += 1
            continue
        whole = norm(" ".join(body))
        pos = whole.find(quote)
        if pos >= 0:
            before = whole[:pos]
            where = before.count("\n") if "\n" in before else None
            # Recover a line number from the character offset in the joined body.
            acc = 0
            hit = None
            for i, ln in enumerate(body, start=1):
                acc += len(norm(ln)) + 1
                if acc > pos:
                    hit = i
                    break
            print(f"MOVE {sid} line {n} -> {hit}")
            ok += 1
            continue
        print(f"FAIL {sid} line {n}")
        failures.append(raw)
    print(f"\n{ok}/{checked} quotes resolved")
    if failures:
        print(f"{len(failures)} defect(s):")
        for f in failures:
            print(f"  {f}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
