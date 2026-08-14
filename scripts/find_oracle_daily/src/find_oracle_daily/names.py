"""Pure parsing of Oracle Cloud image records into Candidate objects.

No I/O. `parse`/`parse_all` are total functions of the input records.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Anchored at both ends. Non-matching names are silently discarded by the
# caller (parse() returns None). The trailing `$` is load-bearing: an
# unrecognized future suffix (e.g. "-platform-v2") must fail to match rather
# than be treated as a known variant.
_NAME_RE = re.compile(
    r"^daily-ubuntu-paravirtualized-"
    r"(?P<arch>amd64|arm64)-"
    r"(?P<family>server|minimal)-"
    r"(?P<version>\d\d\.\d\d)-"
    r"(?P<suite>[a-z]+)-"
    r"v(?P<serial>\d{8})"
    r"(?:\.(?P<rebuild>\d+))?"
    r"(?P<tail>-platform)?$"
)


@dataclass(frozen=True)
class Candidate:
    """A single parsed, filterable image candidate."""

    ocid: str
    display_name: str
    arch: str
    family: str
    version: str
    suite: str
    serial: int
    rebuild: int
    tail: str
    launch_mode: str | None
    firmware: str | None
    time_created: str | None


def parse(record: dict) -> Candidate | None:
    """Parse a single `oci compute image list` record into a Candidate.

    Returns None if the display name does not match the expected grammar.
    """
    display_name = record.get("display-name") or ""
    match = _NAME_RE.match(display_name)
    if match is None:
        return None

    groups = match.groupdict()
    launch_options = record.get("launch-options") or {}
    firmware = (
        launch_options.get("firmware") if isinstance(launch_options, dict) else None
    )

    return Candidate(
        ocid=record.get("id", ""),
        display_name=display_name,
        arch=groups["arch"],
        family=groups["family"],
        version=groups["version"],
        suite=groups["suite"],
        serial=int(groups["serial"]),
        rebuild=int(groups["rebuild"] or 0),
        tail=groups["tail"] or "",
        launch_mode=record.get("launch-mode"),
        firmware=firmware,
        time_created=record.get("time-created"),
    )


def parse_all(records: list[dict]) -> list[Candidate]:
    """Parse all records, silently discarding any that do not match."""
    candidates = []
    for record in records:
        candidate = parse(record)
        if candidate is not None:
            candidates.append(candidate)
    return candidates
