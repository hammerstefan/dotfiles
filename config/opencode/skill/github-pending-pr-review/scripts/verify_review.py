#!/usr/bin/env python3
"""Verify a pending review against what GitHub actually stored.

The check answers one question: does every comment GitHub holds sit on the
anchor the request named, with the body the request named? It answers that
question from the API alone, and it says which evidence it used. A comment
that names a range is checked against the start line of that range too,
because the range is what a suggested change replaces.

GitHub exposes the anchor of a review comment in two ways, and they are not
always available together. The review-scoped endpoint
``GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/comments``
returns the legacy comment shape, which omits ``line`` and ``side``. The
pull-request-scoped endpoint ``GET /repos/{owner}/{repo}/pulls/{pull_number}/comments``
returns the full shape, with ``line`` and ``side``. A GraphQL query of the
review's comments returns ``line`` but has no ``side`` field at all.

So the anchor is taken from the API when the API states it, and is otherwise
derived from the diff position against the file's patch, using the convention
in ``diff_positions``. Every comment carries the position GitHub reported, so
a derived anchor can be checked against the anchor that was requested.

The script never guesses. A comment whose anchor cannot be established from
either source is reported as unverified, and the script exits non-zero.

A record is only used when it can be attributed to the review. The REST
endpoints name the review numerically. A GraphQL record names it by node id,
so a GraphQL source needs ``--review-node-id`` as well as ``--review-id``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from diff_positions import PatchError, PatchIndex, build_index  # noqa: E402


class VerificationError(ValueError):
    """Raised when the remote state cannot be verified."""


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read valid JSON from {path}: {exc}") from exc


def entry_id(entry: dict[str, Any]) -> int | None:
    for key in ("id", "databaseId"):
        value = entry.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None


def entry_field(entry: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in entry and entry[name] is not None:
            return entry[name]
    return None


def collect(
    entries: list[dict[str, Any]], review_id: int, review_node_id: str | None = None
) -> tuple[dict[int, dict[str, Any]], dict[str, int]]:
    """Merge every remote record for one review, keyed by comment id.

    Records from different endpoints are merged, and the first record that
    states a field supplies it. Bodies are compared across records so a
    disagreement between endpoints is visible.

    A record that cannot be attributed to this review is left out. The REST
    endpoints name the review numerically. A GraphQL record names it by node
    id, so it is only taken when that node id is given.
    """
    merged: dict[int, dict[str, Any]] = {}
    skipped = {"other_review": 0, "unattributed": 0}
    for entry in entries:
        if not isinstance(entry, dict):
            skipped["unattributed"] += 1
            continue
        identifier = entry_id(entry)
        if identifier is None:
            skipped["unattributed"] += 1
            continue
        owner = entry.get("pull_request_review_id")
        if owner is None:
            review = entry.get("pullRequestReview")
            node_id = review.get("id") if isinstance(review, dict) else None
            if review_node_id is None or node_id != review_node_id:
                skipped["unattributed"] += 1
                continue
        elif owner != review_id:
            skipped["other_review"] += 1
            continue
        record = merged.setdefault(
            identifier,
            {"id": identifier, "reply_to": None, "bodies": set()},
        )
        reply_to = entry.get("in_reply_to_id")
        if reply_to is not None:
            record["reply_to"] = reply_to
        body = entry_field(entry, "body")
        if isinstance(body, str) and body:
            record["bodies"].add(body)
        for field, names in (
            ("path", ("path",)),
            ("line", ("line",)),
            ("side", ("side",)),
            ("start_line", ("start_line",)),
            ("start_side", ("start_side",)),
            ("position", ("position",)),
            ("commit", ("commit_id", "commit")),
        ):
            value = entry_field(entry, *names)
            if isinstance(value, dict):
                value = value.get("oid")
            if value is not None and record.get(field) is None:
                record[field] = value
    return merged, skipped


def patch_index_for(files: list[dict[str, Any]], path: str) -> PatchIndex:
    for entry in files:
        if not isinstance(entry, dict) or entry.get("filename") != path:
            continue
        patch = entry.get("patch")
        if not isinstance(patch, str) or not patch.strip():
            raise VerificationError(f"GitHub omitted the patch for {path!r}")
        try:
            return build_index(patch)
        except PatchError as exc:
            raise VerificationError(
                f"cannot read the patch for {path!r}: {exc}"
            ) from exc
    raise VerificationError(f"{path!r} is not a changed file of this pull request")


def resolve_anchor(
    record: dict[str, Any], index: PatchIndex
) -> tuple[tuple[int, str] | None, str | None, str | None]:
    """Establish the anchor of a remote comment.

    Returns the anchor, the evidence that established it, and the reason it
    could not be established. A GraphQL query states the line but has no side
    field, so the side comes from the diff position and the line is checked
    against it.
    """
    line = record.get("line")
    side = record.get("side")
    api_line = line if isinstance(line, int) and not isinstance(line, bool) else None
    api_side = side if side in {"LEFT", "RIGHT"} else None

    position = record.get("position")
    position_anchor = None
    if isinstance(position, int) and not isinstance(position, bool) and position >= 1:
        position_anchor = index.anchor_of(position)

    if position_anchor:
        if api_line is not None and api_line != position_anchor[0]:
            return (
                None,
                None,
                f"the API states line {api_line} but position {position} maps "
                f"to line {position_anchor[0]}",
            )
        if api_side is not None and api_side != position_anchor[1]:
            return (
                None,
                None,
                f"the API states side {api_side} but position {position} maps "
                f"to side {position_anchor[1]}",
            )
        if api_line is not None and api_side is not None:
            return position_anchor, "api_fields_and_diff_position", None
        if api_line is not None:
            return position_anchor, "api_line_and_diff_position", None
        if api_side is not None:
            return position_anchor, "api_side_and_diff_position", None
        return position_anchor, "diff_position", None

    if api_line is not None and api_side is not None:
        return (api_line, api_side), "api_fields", None
    if not isinstance(position, int) or isinstance(position, bool) or position < 1:
        return None, None, "the comment carries no diff position"
    return None, None, f"position {position} is not a commentable line of the patch"


def range_failures(
    label: str, identifier: int, comment: dict[str, Any], record: dict[str, Any]
) -> list[str]:
    """Check that the remote comment covers the range the request named.

    A comment that names a range is anchored to more than one line, and the
    start of that range is what a suggested change replaces. The remote
    comment reports the start line when it covers a range, so the two are
    compared. A remote comment that covers a range the request did not name
    is a failure too, because the request could not have produced it.
    """
    failures: list[str] = []
    requested_start = comment.get("start_line")
    remote_start = record.get("start_line")
    remote_start_is_int = isinstance(remote_start, int) and not isinstance(
        remote_start, bool
    )
    if requested_start is not None:
        if not remote_start_is_int:
            failures.append(
                f"{label} remote comment {identifier} does not report the "
                "start line of the requested range"
            )
        elif remote_start != requested_start:
            failures.append(
                f"{label} requested a range that starts at line "
                f"{requested_start} but the remote comment starts at "
                f"{remote_start}"
            )
    elif remote_start_is_int:
        failures.append(
            f"{label} remote comment {identifier} covers a range that starts "
            f"at line {remote_start} and the request did not name one"
        )

    requested_side = comment.get("start_side")
    remote_side = record.get("start_side")
    if (
        requested_side is not None
        and remote_side is not None
        and remote_side != requested_side
    ):
        failures.append(
            f"{label} requested a range on the {requested_side} side but the "
            f"remote comment starts on the {remote_side} side"
        )
    return failures


def verify(
    files: Any,
    requested: Any,
    remote_entries: list[dict[str, Any]],
    review_id: int,
    head_sha: str | None,
    review_node_id: str | None = None,
) -> dict[str, Any]:
    if not isinstance(files, list):
        raise VerificationError("files JSON must be an array")
    if not isinstance(requested, list) or not requested:
        raise VerificationError("comments JSON must be a non-empty array")

    merged, skipped = collect(remote_entries, review_id, review_node_id)
    replies = sorted(
        identifier for identifier, record in merged.items() if record.get("reply_to")
    )
    top_level = {
        identifier: record
        for identifier, record in merged.items()
        if not record.get("reply_to")
    }

    failures: list[str] = []
    results: list[dict[str, Any]] = []
    used: set[int] = set()
    index_cache: dict[str, PatchIndex | None] = {}

    for position, comment in enumerate(requested):
        label = f"comments[{position}]"
        if not isinstance(comment, dict):
            failures.append(f"{label} is not an object")
            continue
        path = comment.get("path")
        line = comment.get("line")
        side = comment.get("side")
        body = comment.get("body")
        if not isinstance(path, str) or not isinstance(body, str):
            failures.append(f"{label} lacks a path or body")
            continue
        if isinstance(line, bool) or not isinstance(line, int) or line <= 0:
            failures.append(f"{label}.line must be a positive integer")
            continue
        if side not in {"LEFT", "RIGHT"}:
            failures.append(f"{label}.side must be LEFT or RIGHT")
            continue

        same_path = [
            record for record in top_level.values() if record.get("path") == path
        ]
        if not same_path:
            failures.append(f"{label} has no remote comment on {path!r}")
            continue
        same_body = [record for record in same_path if body in record["bodies"]]
        if not same_body:
            failures.append(
                f"{label} has no remote comment on {path!r} whose body matches "
                "the request exactly"
            )
            continue

        if path not in index_cache:
            try:
                index_cache[path] = patch_index_for(files, path)
            except VerificationError as exc:
                index_cache[path] = None
                failures.append(str(exc))
        index = index_cache[path]
        if index is None:
            continue

        chosen: list[tuple[dict[str, Any], tuple[int, str], str]] = []
        for record in same_body:
            anchor, evidence, reason = resolve_anchor(record, index)
            if anchor is None:
                failures.append(
                    f"{label} remote comment {record['id']} has no verifiable "
                    f"anchor: {reason}"
                )
                continue
            if anchor == (line, side):
                chosen.append((record, anchor, evidence or ""))
        if not chosen:
            failures.append(
                f"{label} requested {path}:{line} {side} but no remote comment "
                f"with that body sits on that anchor"
            )
            continue
        if len(chosen) > 1:
            failures.append(
                f"{label} matches {len(chosen)} remote comments with the same "
                "path, body and anchor; the anchors cannot be told apart"
            )
            continue

        record, anchor, evidence = chosen[0]
        identifier = record["id"]
        used.add(identifier)

        if len(record["bodies"]) > 1:
            failures.append(
                f"{label} remote comment {identifier} reports different bodies "
                "in different API responses"
            )

        failures.extend(range_failures(label, identifier, comment, record))

        commit = record.get("commit")
        if head_sha and isinstance(commit, str) and commit != head_sha:
            failures.append(
                f"{label} remote comment {identifier} belongs to commit "
                f"{commit[:12]}, not the reviewed head {head_sha[:12]}"
            )

        results.append(
            {
                "path": path,
                "line": anchor[0],
                "side": anchor[1],
                "start_line": comment.get("start_line"),
                "position": record.get("position"),
                "verified_by": evidence,
                "comment_id": identifier,
                "body_matched": True,
            }
        )

    unexpected = sorted(set(top_level) - used)
    for identifier in unexpected:
        failures.append(
            f"remote comment {identifier} belongs to this review but was not requested"
        )
    if len(top_level) != len(requested):
        failures.append(
            f"the review holds {len(top_level)} top-level comment(s) but "
            f"{len(requested)} were requested"
        )

    return {
        "review_id": review_id,
        "head_sha": head_sha,
        "requested": len(requested),
        "remote_top_level": len(top_level),
        "remote_replies": replies,
        "skipped_remote_comments": skipped,
        "verified": len(results),
        "comments": results,
        "failures": failures,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--files", required=True, type=Path)
    parser.add_argument("--comments", required=True, type=Path)
    parser.add_argument(
        "--remote",
        required=True,
        type=Path,
        action="append",
        help="a JSON array of remote review comments; repeat for each endpoint",
    )
    parser.add_argument("--review-id", required=True, type=int)
    parser.add_argument(
        "--review-node-id",
        help=(
            "the GraphQL node id of the review, needed to attribute GraphQL "
            "records to it"
        ),
    )
    parser.add_argument("--head-sha")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    remote_entries: list[dict[str, Any]] = []
    try:
        for path in args.remote:
            payload = load_json(path)
            if not isinstance(payload, list):
                raise VerificationError(f"{path} does not hold a JSON array")
            remote_entries.extend(payload)
        report = verify(
            load_json(args.files),
            load_json(args.comments),
            remote_entries,
            args.review_id,
            args.head_sha,
            args.review_node_id,
        )
    except (VerificationError, OSError) as exc:
        print(f"verification failed: {exc}", file=sys.stderr)
        return 1

    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        try:
            with args.output.open("w", encoding="utf-8") as stream:
                stream.write(text)
        except OSError as exc:
            print(f"cannot write {args.output}: {exc}", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(text)

    if report["failures"]:
        for failure in report["failures"]:
            print(f"unverified: {failure}", file=sys.stderr)
        return 1
    print(f"verified {report['verified']} comment(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
