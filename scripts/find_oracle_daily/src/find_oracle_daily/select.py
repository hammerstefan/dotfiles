"""Pure filtering and selection logic over parsed Candidate objects.

No I/O. All functions are total, deterministic functions of their inputs.
"""

from __future__ import annotations

import re

from find_oracle_daily.names import Candidate

_VERSION_RE = re.compile(r"^\d\d\.\d\d$")


def suite_matches(candidate: Candidate, suite_arg: str) -> bool:
    """Compare `suite_arg` against version if it looks like YY.MM, else codename."""
    if _VERSION_RE.match(suite_arg):
        return candidate.version == suite_arg
    return candidate.suite == suite_arg


def filter_candidates(
    candidates: list[Candidate],
    suite: str,
    arch: str,
    family: str,
) -> list[Candidate]:
    """Filter candidates by suite (codename or version), arch, and family."""
    return [
        c
        for c in candidates
        if suite_matches(c, suite) and c.arch == arch and c.family == family
    ]


def _sort_key(candidate: Candidate) -> tuple[int, int]:
    return (candidate.serial, candidate.rebuild)


def select_winners(
    candidates: list[Candidate], serial: int | None = None
) -> list[Candidate]:
    """Return every candidate sharing the winning selection key.

    If `serial` is given, restrict to candidates with that exact serial and
    return all of them (letting the caller detect ambiguity within a single
    pinned serial too). Otherwise select by the maximum
    (serial, rebuild) key and return every candidate sharing it.

    Returns an empty list if there are no candidates (or none match the
    pinned serial).
    """
    pool = candidates
    if serial is not None:
        pool = [c for c in candidates if c.serial == serial]

    if not pool:
        return []

    winning_key = max(_sort_key(c) for c in pool)
    return [c for c in pool if _sort_key(c) == winning_key]
