#!/usr/bin/env python3

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
import unicodedata
from urllib.parse import quote


MAX_PAYLOAD_BYTES = 1024 * 1024
MAX_ITEMS = 500
MAX_LOCATIONS_PER_ITEM = 100
MAX_TOTAL_LOCATIONS = 1000
MAX_EVIDENCE_FILE_BYTES = 4 * 1024 * 1024
MAX_COMMAND_OUTPUT_BYTES = 6 * 1024 * 1024
COMMAND_TIMEOUT_SECONDS = 30
MAX_SAFE_SEQUENCE = 10_000
MAX_INSPECTION_COMMANDS = 250
MAX_REMOTE_REQUESTS = 50
MAX_TOTAL_INSPECTION_BYTES = 64 * 1024 * 1024
MAX_TOTAL_VALIDATION_SECONDS = 120
MAX_DISTINCT_LOCATION_FILES = 100
MAX_LOCAL_COMMIT_CACHE = 128

ATTENTION_TYPES = {
    "judgment-gap",
    "low-confidence-concern",
    "consequential-decision",
    "domain-expertise",
    "environment-validation",
}
CONFIDENCE_LEVELS = {"low", "medium", "high"}
IMPACT_LEVELS = {"critical", "high", "medium", "low"}
PRIORITIES = {"REQUIRED", "RECOMMENDED"}
REVIEWERS = {
    "review-correctness",
    "review-security",
    "review-architecture",
    "review-tests",
    "review-compatibility",
    "review-skeptic",
    "review-crossfile",
}
SCOPE_KINDS = {"uncommitted", "staged", "commit", "range", "branch", "pr", "path"}
VERDICTS = {"APPROVE", "REQUEST_CHANGES", "NEEDS_DISCUSSION"}

REVISION_RE = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
SLUG_RE = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
FINDING_ID_RE = re.compile(r"[A-Z][A-Z0-9-]{0,63}\Z")
TEMP_INPUT_RE = re.compile(
    r"review-human-candidate-[A-Za-z0-9][A-Za-z0-9.-]{0,80}\.json\Z"
)
REPOSITORY_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")

SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh(?:p|o|u|s|r)_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bxox(?:a|b|p|r|s)-[A-Za-z0-9-]{20,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{20,}\b"),
    re.compile(r"(?i)https?://[^\s/:@]+:[^\s/@]+@"),
    re.compile(
        r"(?i)\b(?:api[_ -]?key|client[_ -]?secret|password|passwd|authorization|"
        r"access[_ -]?token|refresh[_ -]?token)\b\s*[:=]\s*"
        r"(?!redacted\b|<redacted>|\[redacted\])\S+"
    ),
)


class ReportError(Exception):
    pass


class InspectionBudget:
    def __init__(self):
        self.started = time.monotonic()
        self.commands = 0
        self.remote_requests = 0
        self.bytes = 0

    def reserve(self, command):
        elapsed = time.monotonic() - self.started
        if elapsed > MAX_TOTAL_VALIDATION_SECONDS:
            raise ReportError("report validation exceeded its wall-clock safety budget")
        self.commands += 1
        if self.commands > MAX_INSPECTION_COMMANDS:
            raise ReportError(
                "report validation exceeded its inspection-command budget"
            )
        if command and command[0] == "gh":
            self.remote_requests += 1
            if self.remote_requests > MAX_REMOTE_REQUESTS:
                raise ReportError(
                    "report validation exceeded its remote-request budget"
                )

    def consume(self, stdout, stderr):
        if time.monotonic() - self.started > MAX_TOTAL_VALIDATION_SECONDS:
            raise ReportError("report validation exceeded its wall-clock safety budget")
        self.bytes += len(stdout) + len(stderr)
        if self.bytes > MAX_TOTAL_INSPECTION_BYTES:
            raise ReportError("report validation exceeded its aggregate output budget")


INSPECTION_BUDGET = InspectionBudget()
LOCAL_COMMIT_CACHE = {}


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReportError("candidate JSON contains a duplicate object key")
        result[key] = value
    return result


def parse_json(raw):
    if len(raw) > MAX_PAYLOAD_BYTES:
        raise ReportError("candidate JSON exceeds the 1 MiB safety limit")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReportError("candidate JSON must be UTF-8") from exc
    try:
        value = json.loads(text, object_pairs_hook=reject_duplicate_keys)
    except ReportError:
        raise
    except json.JSONDecodeError as exc:
        raise ReportError("candidate report is not valid JSON") from exc
    scan_strings(value, "candidate")
    return value


def scan_strings(value, field):
    if isinstance(value, dict):
        for key, child in value.items():
            scan_strings(key, f"{field} key")
            scan_strings(child, f"{field}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            scan_strings(child, f"{field}[{index}]")
        return
    if not isinstance(value, str):
        return
    if any(
        character not in {"\n", "\t"}
        and unicodedata.category(character) in {"Cc", "Cf", "Cs"}
        for character in value
    ):
        raise ReportError(f"{field} contains control or formatting characters")
    if any(pattern.search(value) for pattern in SECRET_PATTERNS):
        raise ReportError(
            f"{field} contains secret-like content; redact it before persistence"
        )


def expect_object(value, field):
    if not isinstance(value, dict):
        raise ReportError(f"{field} must be an object")
    return value


def expect_exact_keys(value, expected, field):
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        details = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if unknown:
            details.append(f"unknown {', '.join(unknown)}")
        raise ReportError(f"{field} has invalid fields ({'; '.join(details)})")


def expect_text(value, field, *, maximum, allow_empty=False):
    if not isinstance(value, str):
        raise ReportError(f"{field} must be a string")
    if not allow_empty and not value:
        raise ReportError(f"{field} must not be empty")
    if len(value) > maximum:
        raise ReportError(f"{field} exceeds its {maximum}-character limit")
    return value


def expect_enum(value, allowed, field):
    if not isinstance(value, str) or value not in allowed:
        raise ReportError(f"{field} has an unsupported value")
    return value


def expect_integer(value, field, *, minimum=0, maximum=None):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ReportError(f"{field} must be an integer")
    if value < minimum or (maximum is not None and value > maximum):
        raise ReportError(f"{field} is outside its allowed range")
    return value


def expect_list(value, field, *, minimum=0, maximum):
    if not isinstance(value, list):
        raise ReportError(f"{field} must be an array")
    if len(value) < minimum or len(value) > maximum:
        raise ReportError(f"{field} has an unsupported number of entries")
    return value


def expect_unique(values, field):
    if len(values) != len(set(values)):
        raise ReportError(f"{field} must not contain duplicates")


def expect_revision(value, field, *, required):
    if value is None and not required:
        return None
    if not isinstance(value, str) or not REVISION_RE.fullmatch(value):
        raise ReportError(f"{field} must be a full lowercase Git object ID")
    return value


def validate_repository_path(value, field):
    path = expect_text(value, field, maximum=512)
    if (
        "\\" in path
        or path.startswith("/")
        or any(unicodedata.category(character).startswith("C") for character in path)
    ):
        raise ReportError(f"{field} must be a repository-relative POSIX path")
    parts = PurePosixPath(path).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ReportError(f"{field} contains an unsafe path segment")
    if PurePosixPath(path).as_posix() != path:
        raise ReportError(f"{field} must use a canonical repository-relative path")
    return path


def validate_scope(value):
    scope = expect_object(value, "scope")
    expect_exact_keys(
        scope,
        {"kind", "value", "reviewed_revision", "base_revision"},
        "scope",
    )
    kind = expect_enum(scope["kind"], SCOPE_KINDS, "scope.kind")
    display = expect_text(scope["value"], "scope.value", maximum=512)
    reviewed = expect_revision(
        scope["reviewed_revision"], "scope.reviewed_revision", required=False
    )
    base = expect_revision(
        scope["base_revision"], "scope.base_revision", required=False
    )

    if kind in {"uncommitted", "staged"}:
        if display != kind or reviewed is not None:
            raise ReportError("worktree and index scopes have inconsistent metadata")
    elif kind == "path":
        if not display.startswith("path:") or reviewed is not None or base is not None:
            raise ReportError("path scope has inconsistent metadata")
        scoped_path = display.removeprefix("path:")
        if scoped_path != ".":
            validate_repository_path(scoped_path, "scope.value path")
    elif kind == "commit":
        if (
            not display.startswith("commit:")
            or not display.removeprefix("commit:")
            or reviewed is None
        ):
            raise ReportError("commit scope has inconsistent metadata")
    elif kind == "range":
        if (
            not display.startswith("range:")
            or ".." not in display
            or not display.removeprefix("range:").split("..", 1)[0]
            or not display.removeprefix("range:").split("..", 1)[1]
            or reviewed is None
            or base is None
        ):
            raise ReportError("range scope has inconsistent metadata")
    elif kind == "branch":
        if (
            not display.startswith("branch:")
            or not display.removeprefix("branch:")
            or reviewed is None
            or base is None
        ):
            raise ReportError("branch scope has inconsistent metadata")
    elif kind == "pr":
        if (
            not re.fullmatch(r"pr:[1-9][0-9]{0,9}", display)
            or reviewed is None
            or base is None
        ):
            raise ReportError("pull-request scope has inconsistent metadata")

    return {
        "kind": kind,
        "value": display,
        "reviewed_revision": reviewed,
        "base_revision": base,
    }


def validate_string_list(value, field, *, maximum_entries, maximum_length):
    entries = expect_list(value, field, maximum=maximum_entries)
    result = [
        expect_text(entry, f"{field}[{index}]", maximum=maximum_length)
        for index, entry in enumerate(entries)
    ]
    expect_unique(result, field)
    return result


def validate_slug_list(value, field, *, maximum_entries):
    entries = expect_list(value, field, minimum=1, maximum=maximum_entries)
    result = []
    for index, entry in enumerate(entries):
        text = expect_text(entry, f"{field}[{index}]", maximum=64)
        if not SLUG_RE.fullmatch(text):
            raise ReportError(f"{field}[{index}] must be a lowercase hyphenated slug")
        result.append(text)
    expect_unique(result, field)
    return result


def validate_location(value, item_index, location_index):
    field = f"items[{item_index}].locations[{location_index}]"
    location = expect_object(value, field)
    expect_exact_keys(location, {"path", "line", "source"}, field)
    return {
        "path": validate_repository_path(location["path"], f"{field}.path"),
        "line": expect_integer(
            location["line"], f"{field}.line", minimum=1, maximum=10_000_000
        ),
        "source": expect_enum(
            location["source"], {"reviewed", "base"}, f"{field}.source"
        ),
    }


def validate_item(value, index):
    field = f"items[{index}]"
    item = expect_object(value, field)
    expect_exact_keys(
        item,
        {
            "id",
            "priority",
            "attention_types",
            "category",
            "title",
            "locations",
            "confidence",
            "impact_level",
            "impact",
            "evidence",
            "uncertainty_sources",
            "why_human",
            "needed_capability",
            "human_action",
        },
        field,
    )
    expected_id = f"HUM-{index + 1:03d}"
    if item["id"] != expected_id:
        raise ReportError(f"{field}.id must be {expected_id}")

    attention_types = expect_list(
        item["attention_types"],
        f"{field}.attention_types",
        minimum=1,
        maximum=len(ATTENTION_TYPES),
    )
    normalized_types = [
        expect_enum(entry, ATTENTION_TYPES, f"{field}.attention_types[{type_index}]")
        for type_index, entry in enumerate(attention_types)
    ]
    expect_unique(normalized_types, f"{field}.attention_types")

    category = expect_text(item["category"], f"{field}.category", maximum=64)
    if not SLUG_RE.fullmatch(category):
        raise ReportError(f"{field}.category must be a lowercase hyphenated slug")

    locations = expect_list(
        item["locations"],
        f"{field}.locations",
        minimum=1,
        maximum=MAX_LOCATIONS_PER_ITEM,
    )
    normalized_locations = [
        validate_location(location, index, location_index)
        for location_index, location in enumerate(locations)
    ]
    location_keys = [
        (location["path"], location["line"], location["source"])
        for location in normalized_locations
    ]
    if len(location_keys) != len(set(location_keys)):
        raise ReportError(f"{field}.locations must not contain duplicates")

    return {
        "id": expected_id,
        "priority": expect_enum(item["priority"], PRIORITIES, f"{field}.priority"),
        "attention_types": normalized_types,
        "category": category,
        "title": expect_text(item["title"], f"{field}.title", maximum=160),
        "locations": normalized_locations,
        "confidence": expect_enum(
            item["confidence"], CONFIDENCE_LEVELS, f"{field}.confidence"
        ),
        "impact_level": expect_enum(
            item["impact_level"], IMPACT_LEVELS, f"{field}.impact_level"
        ),
        "impact": expect_text(item["impact"], f"{field}.impact", maximum=2000),
        "evidence": expect_text(item["evidence"], f"{field}.evidence", maximum=2000),
        "uncertainty_sources": validate_slug_list(
            item["uncertainty_sources"],
            f"{field}.uncertainty_sources",
            maximum_entries=20,
        ),
        "why_human": expect_text(item["why_human"], f"{field}.why_human", maximum=2000),
        "needed_capability": expect_text(
            item["needed_capability"], f"{field}.needed_capability", maximum=300
        ),
        "human_action": expect_text(
            item["human_action"], f"{field}.human_action", maximum=2000
        ),
    }


def validate_reviewer_list(value, field, *, minimum):
    entries = expect_list(value, field, minimum=minimum, maximum=len(REVIEWERS))
    result = [
        expect_enum(entry, REVIEWERS, f"{field}[{index}]")
        for index, entry in enumerate(entries)
    ]
    expect_unique(result, field)
    return result


def validate_council_summary(value, invocation):
    if invocation == "independent":
        if value is not None:
            raise ReportError("independent reports must set council_summary to null")
        return None
    summary = expect_object(value, "council_summary")
    expect_exact_keys(
        summary,
        {
            "verdict",
            "selected_reviewers",
            "failed_reviewers",
            "verified_finding_ids",
            "verified_finding_count",
        },
        "council_summary",
    )
    selected = validate_reviewer_list(
        summary["selected_reviewers"], "council_summary.selected_reviewers", minimum=1
    )
    failed = validate_reviewer_list(
        summary["failed_reviewers"], "council_summary.failed_reviewers", minimum=0
    )
    if not set(failed).issubset(selected):
        raise ReportError("failed reviewers must be a subset of selected reviewers")
    finding_ids = validate_string_list(
        summary["verified_finding_ids"],
        "council_summary.verified_finding_ids",
        maximum_entries=100,
        maximum_length=64,
    )
    if any(not FINDING_ID_RE.fullmatch(finding_id) for finding_id in finding_ids):
        raise ReportError("verified finding IDs have an unsupported format")
    finding_count = expect_integer(
        summary["verified_finding_count"],
        "council_summary.verified_finding_count",
        minimum=0,
        maximum=100,
    )
    if finding_count != len(finding_ids):
        raise ReportError("verified finding count does not match the ID list")
    return {
        "verdict": expect_enum(summary["verdict"], VERDICTS, "council_summary.verdict"),
        "selected_reviewers": selected,
        "failed_reviewers": failed,
        "verified_finding_ids": finding_ids,
        "verified_finding_count": finding_count,
    }


def validate_candidate(value):
    candidate = expect_object(value, "candidate")
    expect_exact_keys(
        candidate,
        {
            "invocation",
            "scope",
            "focus",
            "exclusions",
            "direction",
            "status",
            "items",
            "council_summary",
        },
        "candidate",
    )
    invocation = expect_enum(
        candidate["invocation"], {"independent", "council"}, "invocation"
    )
    scope = validate_scope(candidate["scope"])
    focus = validate_string_list(
        candidate["focus"], "focus", maximum_entries=100, maximum_length=1000
    )
    exclusions = validate_string_list(
        candidate["exclusions"], "exclusions", maximum_entries=100, maximum_length=1000
    )
    direction = expect_text(
        candidate["direction"], "direction", maximum=4000, allow_empty=True
    )
    status_value = expect_enum(candidate["status"], PRIORITIES, "status")
    raw_items = expect_list(candidate["items"], "items", minimum=1, maximum=MAX_ITEMS)
    items = [validate_item(item, index) for index, item in enumerate(raw_items)]

    total_locations = sum(len(item["locations"]) for item in items)
    if total_locations > MAX_TOTAL_LOCATIONS:
        raise ReportError("candidate report exceeds the total location safety limit")
    seen_recommended = False
    for item in items:
        if item["priority"] == "RECOMMENDED":
            seen_recommended = True
        elif seen_recommended:
            raise ReportError("REQUIRED items must appear before RECOMMENDED items")
    expected_status = (
        "REQUIRED"
        if any(item["priority"] == "REQUIRED" for item in items)
        else "RECOMMENDED"
    )
    if status_value != expected_status:
        raise ReportError("status does not match the highest item priority")

    return {
        "invocation": invocation,
        "scope": scope,
        "focus": focus,
        "exclusions": exclusions,
        "direction": direction,
        "status": status_value,
        "items": items,
        "council_summary": validate_council_summary(
            candidate["council_summary"], invocation
        ),
    }


def run_command(command, *, cwd, maximum_output=MAX_COMMAND_OUTPUT_BYTES):
    INSPECTION_BUDGET.reserve(command)
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=min(
                COMMAND_TIMEOUT_SECONDS,
                max(
                    1,
                    MAX_TOTAL_VALIDATION_SECONDS
                    - int(time.monotonic() - INSPECTION_BUDGET.started),
                ),
            ),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReportError("a required read-only inspection command failed") from exc
    if completed.returncode != 0:
        raise ReportError("a required read-only inspection command failed")
    if len(completed.stdout) > maximum_output or len(completed.stderr) > maximum_output:
        raise ReportError("a read-only inspection command exceeded its output limit")
    INSPECTION_BUDGET.consume(completed.stdout, completed.stderr)
    return completed.stdout


def run_optional_command(command, *, cwd, maximum_output=MAX_COMMAND_OUTPUT_BYTES):
    INSPECTION_BUDGET.reserve(command)
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=min(
                COMMAND_TIMEOUT_SECONDS,
                max(
                    1,
                    MAX_TOTAL_VALIDATION_SECONDS
                    - int(time.monotonic() - INSPECTION_BUDGET.started),
                ),
            ),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReportError("a required read-only inspection command failed") from exc
    if len(completed.stdout) > maximum_output or len(completed.stderr) > maximum_output:
        raise ReportError("a read-only inspection command exceeded its output limit")
    INSPECTION_BUDGET.consume(completed.stdout, completed.stderr)
    if completed.returncode != 0:
        return None
    return completed.stdout


def resolve_git_root(start):
    start_path = Path(start).expanduser().resolve(strict=True)
    if not start_path.is_dir():
        raise ReportError("worktree start path is not a directory")
    output = run_command(
        ["git", "rev-parse", "--show-toplevel"], cwd=start_path, maximum_output=4096
    )
    try:
        root = Path(output.decode("utf-8").strip()).resolve(strict=True)
    except (UnicodeDecodeError, OSError) as exc:
        raise ReportError("Git returned an invalid worktree path") from exc
    if not root.is_dir():
        raise ReportError("Git worktree root is not a directory")
    return root


def validate_worktree(start):
    requested_root = resolve_git_root(start)
    try:
        Path.cwd().resolve(strict=True).relative_to(requested_root)
    except (OSError, ValueError) as exc:
        raise ReportError(
            "report writer may only target the current Git worktree"
        ) from exc
    bare = (
        run_command(
            ["git", "rev-parse", "--is-bare-repository"],
            cwd=requested_root,
            maximum_output=64,
        )
        .decode("ascii", "strict")
        .strip()
    )
    if bare != "false":
        raise ReportError("report writer requires a non-bare Git worktree")
    if requested_root == Path(requested_root.anchor):
        raise ReportError("report writer refuses to target a filesystem root")
    parent = requested_root.parent
    while True:
        try:
            metadata = os.lstat(parent)
        except OSError as exc:
            raise ReportError("worktree ancestry could not be validated") from exc
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise ReportError("worktree ancestry contains an unsafe path component")
        if metadata.st_mode & 0o002 and not metadata.st_mode & stat.S_ISVTX:
            raise ReportError("worktree ancestry contains a world-writable directory")
        if parent == Path(parent.anchor):
            break
        parent = parent.parent
    return requested_root


def local_commit_exists(root, revision):
    cache_key = (str(root), revision)
    cached = LOCAL_COMMIT_CACHE.get(cache_key)
    if cached is not None:
        return cached
    if len(LOCAL_COMMIT_CACHE) >= MAX_LOCAL_COMMIT_CACHE:
        raise ReportError("report validation exceeded its revision-cache safety limit")
    INSPECTION_BUDGET.reserve(["git", "cat-file"])
    remaining = max(
        1,
        MAX_TOTAL_VALIDATION_SECONDS
        - int(time.monotonic() - INSPECTION_BUDGET.started),
    )
    try:
        completed = subprocess.run(
            ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
            cwd=root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=min(COMMAND_TIMEOUT_SECONDS, remaining),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReportError("a required read-only inspection command failed") from exc
    INSPECTION_BUDGET.consume(b"", b"")
    exists = completed.returncode == 0
    LOCAL_COMMIT_CACHE[cache_key] = exists
    return exists


def resolve_local_commit(root, revision, *, required=True):
    if (
        not revision
        or len(revision) > 512
        or any(character.isspace() for character in revision)
    ):
        raise ReportError("review scope contains an invalid Git revision")
    output = run_optional_command(
        ["git", "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}"],
        cwd=root,
        maximum_output=128,
    )
    if output is None:
        if required:
            raise ReportError(
                "a review-scope Git revision does not resolve to a local commit"
            )
        return None
    try:
        resolved = output.decode("ascii", "strict").strip()
    except UnicodeDecodeError as exc:
        raise ReportError("Git returned an invalid revision") from exc
    if not REVISION_RE.fullmatch(resolved):
        raise ReportError("Git returned an invalid revision")
    return resolved


def load_pr_info(root, scope):
    number = scope["value"].removeprefix("pr:")
    expression = (
        "{reviewed_revision: .head.sha, reviewed_repository: .head.repo.full_name, "
        "base_revision: .base.sha, base_repository: .base.repo.full_name}"
    )
    output = run_command(
        [
            "gh",
            "api",
            "-X",
            "GET",
            f"repos/{{owner}}/{{repo}}/pulls/{number}",
            "--jq",
            expression,
        ],
        cwd=root,
        maximum_output=4096,
    )
    try:
        info = json.loads(
            output.decode("utf-8"), object_pairs_hook=reject_duplicate_keys
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ReportError) as exc:
        raise ReportError("GitHub returned invalid pull-request metadata") from exc
    info = expect_object(info, "pull-request metadata")
    expect_exact_keys(
        info,
        {
            "reviewed_revision",
            "reviewed_repository",
            "base_revision",
            "base_repository",
        },
        "pull-request metadata",
    )
    for key in ("reviewed_revision", "base_revision"):
        revision = expect_revision(
            info[key], f"pull-request metadata.{key}", required=True
        )
        if revision != scope[key]:
            raise ReportError(
                "pull-request revisions changed or do not match the report contract"
            )
    for key in ("reviewed_repository", "base_repository"):
        repository = expect_text(info[key], f"pull-request metadata.{key}", maximum=200)
        if not REPOSITORY_RE.fullmatch(repository) or ".." in repository:
            raise ReportError("GitHub returned an invalid repository identity")
    current_repository_output = run_command(
        ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
        cwd=root,
        maximum_output=512,
    )
    try:
        current_repository = current_repository_output.decode("utf-8", "strict").strip()
    except UnicodeDecodeError as exc:
        raise ReportError(
            "GitHub returned an invalid current repository identity"
        ) from exc
    if current_repository != info["base_repository"]:
        raise ReportError(
            "pull-request base repository does not match the current repository"
        )
    return info


def validate_scope_against_repository(root, scope):
    if scope["kind"] == "pr":
        return load_pr_info(root, scope)

    kind = scope["kind"]
    display = scope["value"]
    expected_reviewed = None
    expected_base = None

    if kind in {"uncommitted", "staged"}:
        expected_base = resolve_local_commit(root, "HEAD", required=False)
    elif kind == "commit":
        expected_reviewed = resolve_local_commit(root, display.removeprefix("commit:"))
        parents_output = run_command(
            ["git", "rev-list", "--parents", "-n", "1", expected_reviewed],
            cwd=root,
            maximum_output=1024,
        )
        try:
            parent_fields = parents_output.decode("ascii", "strict").strip().split()
        except UnicodeDecodeError as exc:
            raise ReportError("Git returned invalid commit-parent metadata") from exc
        if not parent_fields or parent_fields[0] != expected_reviewed:
            raise ReportError("Git returned inconsistent commit-parent metadata")
        if len(parent_fields) > 1:
            expected_base = parent_fields[1]
    elif kind == "range":
        revision_range = display.removeprefix("range:")
        if "..." in revision_range or revision_range.count("..") != 1:
            raise ReportError("range scope must contain exactly one '..' separator")
        base_ref, reviewed_ref = revision_range.split("..", 1)
        expected_base = resolve_local_commit(root, base_ref)
        expected_reviewed = resolve_local_commit(root, reviewed_ref)
    elif kind == "branch":
        compared_ref = display.removeprefix("branch:")
        expected_reviewed = resolve_local_commit(root, "HEAD")
        compared_revision = resolve_local_commit(root, compared_ref)
        merge_base_output = run_command(
            ["git", "merge-base", expected_reviewed, compared_revision],
            cwd=root,
            maximum_output=128,
        )
        try:
            expected_base = merge_base_output.decode("ascii", "strict").strip()
        except UnicodeDecodeError as exc:
            raise ReportError("Git returned an invalid merge-base revision") from exc
        if not REVISION_RE.fullmatch(expected_base):
            raise ReportError("Git returned an invalid merge-base revision")
    elif kind == "path":
        return None

    if (
        scope["reviewed_revision"] != expected_reviewed
        or scope["base_revision"] != expected_base
    ):
        raise ReportError("resolved review revisions do not match the declared scope")
    return None


def validate_scope_path(root, scope):
    if scope["kind"] != "path":
        return
    scoped_path = scope["value"].removeprefix("path:")
    if scoped_path == ".":
        return
    current = root
    metadata = None
    for segment in PurePosixPath(scoped_path).parts:
        current = current / segment
        try:
            metadata = os.lstat(current)
        except OSError as exc:
            raise ReportError("path review scope does not exist") from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise ReportError("path review scope must not traverse symbolic links")
    if metadata is None or not (
        stat.S_ISREG(metadata.st_mode) or stat.S_ISDIR(metadata.st_mode)
    ):
        raise ReportError("path review scope must be a regular file or directory")


def safe_worktree_file(root, repository_path):
    current = root
    metadata = None
    for segment in PurePosixPath(repository_path).parts:
        current = current / segment
        try:
            metadata = os.lstat(current)
        except OSError as exc:
            raise ReportError("a cited worktree path does not exist") from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise ReportError("cited worktree paths must not traverse symbolic links")
    if metadata is None or not stat.S_ISREG(metadata.st_mode):
        raise ReportError("a cited worktree path is not a regular file")
    if metadata.st_size > MAX_EVIDENCE_FILE_BYTES:
        raise ReportError("a cited file exceeds the evidence validation size limit")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(current, flags)
        try:
            opened = os.fstat(descriptor)
            if (
                not stat.S_ISREG(opened.st_mode)
                or opened.st_size > MAX_EVIDENCE_FILE_BYTES
                or (opened.st_dev, opened.st_ino) != (metadata.st_dev, metadata.st_ino)
            ):
                raise ReportError("a cited worktree path changed during validation")
            data = read_descriptor_limited(descriptor, MAX_EVIDENCE_FILE_BYTES)
            after = os.lstat(current)
            if (after.st_dev, after.st_ino) != (opened.st_dev, opened.st_ino):
                raise ReportError("a cited worktree path changed during validation")
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise ReportError("a cited worktree file could not be read safely") from exc
    return data


def read_git_blob(root, revision, repository_path):
    tree_entry = run_command(
        ["git", "ls-tree", "-z", revision, "--", repository_path],
        cwd=root,
        maximum_output=2048,
    )
    entries = [entry for entry in tree_entry.split(b"\0") if entry]
    if len(entries) != 1 or not entries[0].startswith(
        (b"100644 blob ", b"100755 blob ")
    ):
        raise ReportError("a cited revision path is not a regular file")
    specification = f"{revision}:{repository_path}"
    size_output = run_command(
        ["git", "cat-file", "-s", specification],
        cwd=root,
        maximum_output=64,
    )
    try:
        size = int(size_output.decode("ascii").strip())
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReportError("Git returned an invalid cited-file size") from exc
    if size > MAX_EVIDENCE_FILE_BYTES:
        raise ReportError("a cited file exceeds the evidence validation size limit")
    return run_command(
        ["git", "cat-file", "blob", specification],
        cwd=root,
        maximum_output=MAX_EVIDENCE_FILE_BYTES,
    )


def read_index_blob(root, repository_path):
    index_entry = run_command(
        ["git", "ls-files", "--stage", "-z", "--", repository_path],
        cwd=root,
        maximum_output=4096,
    )
    entries = [entry for entry in index_entry.split(b"\0") if entry]
    stage_zero = [
        entry
        for entry in entries
        if entry.startswith((b"100644 ", b"100755 ")) and b" 0\t" in entry
    ]
    if len(stage_zero) != 1:
        raise ReportError("a cited index path is not a regular stage-zero file")
    specification = f":{repository_path}"
    size_output = run_command(
        ["git", "cat-file", "-s", specification],
        cwd=root,
        maximum_output=64,
    )
    try:
        size = int(size_output.decode("ascii").strip())
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReportError("Git returned an invalid cited-file size") from exc
    if size > MAX_EVIDENCE_FILE_BYTES:
        raise ReportError("a cited file exceeds the evidence validation size limit")
    return run_command(
        ["git", "cat-file", "blob", specification],
        cwd=root,
        maximum_output=MAX_EVIDENCE_FILE_BYTES,
    )


def read_github_blob(root, repository, revision, repository_path):
    endpoint = f"repos/{quote(repository, safe='/')}/contents/{quote(repository_path, safe='/')}"
    metadata_output = run_command(
        [
            "gh",
            "api",
            "-X",
            "GET",
            endpoint,
            "-f",
            f"ref={revision}",
            "--jq",
            "{type: .type, size: .size}",
        ],
        cwd=root,
        maximum_output=1024,
    )
    try:
        metadata = json.loads(
            metadata_output.decode("utf-8"), object_pairs_hook=reject_duplicate_keys
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ReportError) as exc:
        raise ReportError("GitHub returned invalid cited-file metadata") from exc
    metadata = expect_object(metadata, "GitHub cited-file metadata")
    expect_exact_keys(metadata, {"type", "size"}, "GitHub cited-file metadata")
    if metadata["type"] != "file":
        raise ReportError("a remotely cited path is not a regular file")
    size = expect_integer(
        metadata["size"],
        "GitHub cited-file metadata.size",
        minimum=0,
        maximum=MAX_EVIDENCE_FILE_BYTES,
    )
    content = run_command(
        [
            "gh",
            "api",
            "-X",
            "GET",
            endpoint,
            "-f",
            f"ref={revision}",
            "-H",
            "Accept: application/vnd.github.raw+json",
        ],
        cwd=root,
        maximum_output=MAX_EVIDENCE_FILE_BYTES,
    )
    if (
        len(content) > size
        or size - len(content) > 1
        or (size - len(content) == 1 and content.endswith(b"\n"))
    ):
        raise ReportError("remote cited-file content changed or was truncated")
    return content


def count_lines(content):
    if b"\0" in content:
        raise ReportError("cited evidence must be a text file")
    return len(content.splitlines())


def validate_locations(root, candidate, pr_info):
    scope = candidate["scope"]
    cache = {}
    scoped_path = (
        scope["value"].removeprefix("path:") if scope["kind"] == "path" else None
    )

    for item in candidate["items"]:
        for location in item["locations"]:
            repository_path = location["path"]
            if scoped_path and scoped_path != ".":
                if repository_path != scoped_path and not repository_path.startswith(
                    f"{scoped_path}/"
                ):
                    raise ReportError(
                        "a cited location falls outside the path review scope"
                    )
            cache_key = (location["source"], repository_path)
            if cache_key not in cache:
                if len(cache) >= MAX_DISTINCT_LOCATION_FILES:
                    raise ReportError(
                        "candidate report exceeds the distinct evidence-file safety limit"
                    )
                source = location["source"]
                if source == "reviewed" and scope["kind"] in {"uncommitted", "path"}:
                    content = safe_worktree_file(root, repository_path)
                elif source == "reviewed" and scope["kind"] == "staged":
                    content = read_index_blob(root, repository_path)
                else:
                    revision_key = (
                        "reviewed_revision" if source == "reviewed" else "base_revision"
                    )
                    revision = scope[revision_key]
                    if revision is None:
                        raise ReportError(
                            "a cited location references an unavailable revision side"
                        )
                    if local_commit_exists(root, revision):
                        content = read_git_blob(root, revision, repository_path)
                    elif scope["kind"] == "pr" and pr_info is not None:
                        repository_key = (
                            "reviewed_repository"
                            if source == "reviewed"
                            else "base_repository"
                        )
                        content = read_github_blob(
                            root,
                            pr_info[repository_key],
                            revision,
                            repository_path,
                        )
                    else:
                        raise ReportError(
                            "a cited revision is unavailable for location validation"
                        )
                cache[cache_key] = count_lines(content)
            line_count = cache[cache_key]
            if location["line"] > line_count:
                raise ReportError(
                    "a cited line does not exist in its declared file revision"
                )


def read_descriptor_limited(descriptor, maximum):
    chunks = []
    total = 0
    while True:
        chunk = os.read(descriptor, min(64 * 1024, maximum + 1 - total))
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)
        total += len(chunk)
        if total > maximum:
            raise ReportError("input exceeds its safety limit")


def secure_read_temp_input(path_value):
    path = Path(path_value)
    temporary_root = Path(tempfile.gettempdir()).resolve(strict=True)
    if not path.is_absolute() or path.parent.resolve(strict=True) != temporary_root:
        raise ReportError(
            "candidate input must be a direct child of the system temporary directory"
        )
    if not TEMP_INPUT_RE.fullmatch(path.name):
        raise ReportError("candidate input has an unsupported filename")
    try:
        before = os.lstat(path)
    except OSError as exc:
        raise ReportError("candidate input does not exist") from exc
    if not stat.S_ISREG(before.st_mode) or stat.S_ISLNK(before.st_mode):
        raise ReportError("candidate input must be a regular non-symlink file")
    if before.st_uid != os.getuid() or before.st_nlink != 1:
        raise ReportError("candidate input has unsafe ownership or link metadata")
    if stat.S_IMODE(before.st_mode) & 0o077:
        raise ReportError("candidate input must be private to its owner")
    if before.st_size > MAX_PAYLOAD_BYTES:
        raise ReportError("candidate JSON exceeds the 1 MiB safety limit")

    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                raise ReportError("candidate input changed during secure open")
            if (
                not stat.S_ISREG(opened.st_mode)
                or opened.st_uid != os.getuid()
                or opened.st_nlink != 1
                or stat.S_IMODE(opened.st_mode) & 0o077
            ):
                raise ReportError("candidate input changed to unsafe metadata")
            data = read_descriptor_limited(descriptor, MAX_PAYLOAD_BYTES)
            current = os.lstat(path)
            if (
                (current.st_dev, current.st_ino) != (opened.st_dev, opened.st_ino)
                or current.st_uid != os.getuid()
                or current.st_nlink != 1
                or stat.S_IMODE(current.st_mode) & 0o077
            ):
                raise ReportError("candidate input changed before cleanup")
            os.unlink(path)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise ReportError(
            "candidate input could not be read and removed safely"
        ) from exc
    if len(data) > MAX_PAYLOAD_BYTES:
        raise ReportError("candidate JSON exceeds the 1 MiB safety limit")
    return data


def read_stdin():
    data = sys.stdin.buffer.read(MAX_PAYLOAD_BYTES + 1)
    if len(data) > MAX_PAYLOAD_BYTES:
        raise ReportError("candidate JSON exceeds the 1 MiB safety limit")
    return data


def ensure_safe_directory(path, *, create, mode):
    if create:
        try:
            os.mkdir(path, mode)
        except FileExistsError:
            pass
        except OSError as exc:
            raise ReportError("report directory could not be created") from exc
    try:
        metadata = os.lstat(path)
    except OSError as exc:
        raise ReportError("report directory does not exist") from exc
    if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
        raise ReportError("report path contains a non-directory or symbolic link")
    if metadata.st_uid != os.getuid() or metadata.st_mode & 0o002:
        raise ReportError("report directory has unsafe ownership or permissions")


def ensure_gitignore(reviews_directory):
    ignore_path = reviews_directory / ".gitignore"
    try:
        descriptor = os.open(
            ignore_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0),
            0o644,
        )
    except FileExistsError:
        descriptor = None
    except OSError as exc:
        raise ReportError("review report ignore file could not be created") from exc
    if descriptor is not None:
        try:
            write_all(descriptor, b"*\n")
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    try:
        metadata = os.lstat(ignore_path)
        if not stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
            raise ReportError("review report ignore path is not a regular file")
        if metadata.st_uid != os.getuid() or metadata.st_mode & 0o002:
            raise ReportError(
                "review report ignore file has unsafe ownership or permissions"
            )
        if metadata.st_size > 64 * 1024:
            raise ReportError("review report ignore file is unexpectedly large")
        flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(ignore_path, flags)
        try:
            opened = os.fstat(descriptor)
            if (opened.st_dev, opened.st_ino) != (
                metadata.st_dev,
                metadata.st_ino,
            ):
                raise ReportError("review report ignore file changed during validation")
            content = read_descriptor_limited(descriptor, 64 * 1024).decode("utf-8")
        finally:
            os.close(descriptor)
    except (OSError, UnicodeError) as exc:
        raise ReportError("review report ignore file could not be validated") from exc
    active_lines = {
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    if not ({"*", "*.json"} & active_lines):
        raise ReportError(
            "existing .opencode/reviews/.gitignore does not ignore generated reports"
        )
    ignored = run_optional_command(
        [
            "git",
            "check-ignore",
            "--no-index",
            "--quiet",
            "--",
            ".opencode/reviews/review-human-ignore-probe.json",
        ],
        cwd=reviews_directory.parent.parent,
        maximum_output=1024,
    )
    if ignored is None:
        raise ReportError("generated human-review JSON reports are not ignored by Git")


def filename_slug(scope_value):
    slug = re.sub(r"[^A-Za-z0-9.-]+", "-", scope_value).strip(".-").lower()
    slug = re.sub(r"[-.]{2,}", "-", slug)[:48].rstrip(".-") or "scope"
    digest = hashlib.sha256(scope_value.encode("utf-8")).hexdigest()[:10]
    return f"{slug}-{digest}"


def write_all(descriptor, data):
    offset = 0
    while offset < len(data):
        written = os.write(descriptor, data[offset:])
        if written <= 0:
            raise ReportError("review report write did not make progress")
        offset += written


def persist_report(root, candidate):
    opencode_directory = root / ".opencode"
    reviews_directory = opencode_directory / "reviews"
    ensure_safe_directory(opencode_directory, create=True, mode=0o700)
    ensure_safe_directory(reviews_directory, create=True, mode=0o700)
    ensure_gitignore(reviews_directory)

    now = datetime.now(timezone.utc).replace(microsecond=0)
    timestamp = now.strftime("%Y%m%dT%H%M%SZ")
    base_name = f"{timestamp}-review-human-{filename_slug(candidate['scope']['value'])}"
    document = {
        "schema_version": 1,
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        **candidate,
    }
    encoded = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )
    if len(encoded) > MAX_PAYLOAD_BYTES + 64 * 1024:
        raise ReportError("final report exceeds the persistence safety limit")

    temporary_path = None
    descriptor = None
    for sequence in range(1, MAX_SAFE_SEQUENCE + 1):
        suffix = "" if sequence == 1 else f"-{sequence}"
        target = reviews_directory / f"{base_name}{suffix}.json"
        try:
            descriptor = os.open(
                target,
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL
                | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0),
                0o600,
            )
            temporary_path = target
            break
        except FileExistsError:
            continue
        except OSError as exc:
            raise ReportError("review report could not be created atomically") from exc
    if temporary_path is None or descriptor is None:
        raise ReportError("review report collision sequence is exhausted")

    try:
        try:
            write_all(descriptor, encoded)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        directory_descriptor = os.open(
            reviews_directory, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        )
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
        final_path = temporary_path
        temporary_path = None
    finally:
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except OSError:
                pass

    return final_path.relative_to(root).as_posix()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Validate and persist a human-review attention report"
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--stdin", action="store_true", help="read candidate JSON from standard input"
    )
    source.add_argument(
        "--input",
        help="read and remove a secure candidate file from the system temp directory",
    )
    parser.add_argument(
        "--worktree", required=True, help="path inside the current Git worktree"
    )
    return parser.parse_args()


def main():
    arguments = parse_arguments()
    raw = read_stdin() if arguments.stdin else secure_read_temp_input(arguments.input)
    candidate = validate_candidate(parse_json(raw))
    root = validate_worktree(arguments.worktree)
    validate_scope_path(root, candidate["scope"])
    pr_info = validate_scope_against_repository(root, candidate["scope"])
    validate_locations(root, candidate, pr_info)
    report_path = persist_report(root, candidate)
    print(
        json.dumps(
            {
                "path": report_path,
                "status": candidate["status"],
                "items": len(candidate["items"]),
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    try:
        main()
    except ReportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except Exception:
        print("ERROR: human-review report persistence failed", file=sys.stderr)
        raise SystemExit(1)
