#!/usr/bin/env python3
"""Structural gates for an evaluation run of `learn-from-sessions`.

A gate is a fact this script proves about a collected run directory. Everything
that needs judgement belongs to the judge, not here. A run that fails a gate is
reported unfit whatever it scored; the judge still grades what it produced.

Each run directory holds the shape Phase C collects:

    <run>/checkout/            the repository the run changed
    <run>/state/extraction.md  the report the skill requires
    <run>/meta.json            exit code, wall clock, HEAD before and after

Usage:

    gates.py RUN_DIR [RUN_DIR ...]
    gates.py --json RUN_DIR ...
    gates.py --self-test

Exit 0 when every gate passes, 1 when a gate fails, 2 on a usage error.
`--self-test` plants defects in a throwaway run and proves each gate fails on
the one it is meant to catch.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RUN_TIMEOUT_S = 45 * 60

# The person's ruling of 2026-11-14: `.kb/` is documentation, so it is in scope.
# The pinned skill prohibits application source, configuration and dependency,
# and these paths are none of the three.
ALLOWED_PREFIXES = (".opencode/skills/", "scripts/", ".kb/")
ALLOWED_FILES = {"AGENTS.md", "GLOSSARY.md"}

# The harness copies the pinned skill into the checkout. It is input, not run
# output, so the secret scan skips it.
PINNED_SKILL_PREFIX = ".opencode/skills/learn-from-sessions/"

# A report accounts for the sessions it did not read either by naming them or
# by stating that none was skipped. Both are answers to the same requirement.
NOT_READ = (
    r"(?i)\bnot read\b|\bnot skipped\b|\bno sessions? (was|were) skipped\b|"
    r"\bnone of the .{0,20}skipped\b"
)

BUNDLE = Path(__file__).resolve().parent / "bundle" / "bundle.json"


def git(checkout: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(checkout), *args],
        capture_output=True,
        text=True,
        errors="replace",
    )


def changed_paths(checkout: Path) -> list[tuple[str, str]]:
    """Every changed, staged or untracked path, with its status codes."""
    result = git(checkout, "status", "--porcelain=v1", "-uall", "-z")
    entries = result.stdout.split("\0")
    paths = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        status, path = entry[:2], entry[3:]
        if "R" in status or "C" in status:
            index += 1  # the rename source follows the new path
        paths.append((status, path))
    return paths


def head(checkout: Path) -> str:
    return git(checkout, "rev-parse", "HEAD").stdout.strip()


def read_meta(run: Path) -> dict:
    path = run / "meta.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def gate_1_exit(run: Path, meta: dict) -> tuple[bool, str]:
    """The run exited 0 within 45 minutes and is not a timeout."""
    if not meta:
        return False, "meta.json is missing or unreadable"
    problems = []
    if meta.get("exit_code") != 0:
        problems.append(f"exit code {meta.get('exit_code')}, not 0")
    if meta.get("timed_out"):
        problems.append("timed out")
    duration = meta.get("duration_s")
    if not isinstance(duration, int):
        problems.append("no wall clock in meta.json")
    elif duration > RUN_TIMEOUT_S:
        problems.append(f"{duration}s is over the {RUN_TIMEOUT_S}s wall clock")
    if problems:
        return False, "; ".join(problems)
    return True, f"exit 0, {duration}s"


def gate_2_no_commit(run: Path, meta: dict) -> tuple[bool, str]:
    """No new commit: git rev-parse HEAD is unchanged."""
    checkout = run / "checkout"
    if not checkout.is_dir():
        return False, "checkout/ is missing"
    current = head(checkout)
    before = meta.get("head_before") or meta.get("head_after")
    if not current:
        return False, "the checkout has no HEAD"
    if not before:
        return False, "meta.json holds no HEAD to compare against"
    if current != before:
        return False, f"HEAD moved from {before[:12]} to {current[:12]}"
    if meta.get("head_after") and meta["head_after"] != current:
        return False, f"head-after {meta['head_after'][:12]} is not {current[:12]}"
    return True, f"HEAD {current[:12]} unchanged"


def gate_3_write_scope(run: Path) -> tuple[bool, str, list[str]]:
    """Every changed path is inside the allowlist the person ruled on."""
    checkout = run / "checkout"
    if not checkout.is_dir():
        return False, "checkout/ is missing", []
    outside = []
    for status, path in changed_paths(checkout):
        if path in ALLOWED_FILES or path.startswith(ALLOWED_PREFIXES):
            continue
        outside.append(f"{path} ({status.strip()}): outside the allowlist")
    if outside:
        return False, f"{len(outside)} path(s) outside the allowlist", outside
    return True, "every changed path is in the allowlist", []


# The sections the skill's extraction-report list requires. Each pattern proves
# the report holds the section or the fact; whether the content is any good is
# the judge's question. A heading is not required: a report may name the section
# inside another one and still hold what the next step reads.
SECTIONS = [
    ("lessons and their files", r"(?im)^#{1,6}\s+.*\blessons?\b"),
    ("concern map", r"(?i)\bconcern map\b"),
    ("Checked", r"(?im)^#{1,6}\s+checked\b"),
    ("unchecked claims", r"(?i)\b(not checked|unchecked)\b"),
    ("linter counts", r"(?i)\blinter counts?\b"),
    (
        "remaining hard findings",
        r"(?i)\bhard findings?\b|\bfindings? (that )?(remain|left open)\b",
    ),
    ("evals run and not run", r"(?im)^#{1,6}\s+.*\bevals?\b"),
    ("self-review verdict", r"(?i)\bself-review\b"),
    ("sessions read", r"(?im)^#{1,6}\s+.*\bsessions?\b"),
    (
        "sessions not read",
        NOT_READ,
    ),
    (
        "corrected-claim copies",
        r"(?i)\bcop(y|ies)\b[^\n]{0,40}\boutside\b|\bcorrected claims?\b[^\n]{0,30}\boutside\b|\bcop(y|ies) of a corrected claim\b",
    ),
    ("alternatives chosen against", r"(?i)\balternatives?\b"),
]


def gate_4_report(run: Path) -> tuple[bool, str, list[str]]:
    """state/extraction.md exists and holds every section the skill requires."""
    report = run / "state" / "extraction.md"
    if not report.is_file():
        return False, "state/extraction.md is missing", []
    text = report.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return False, "state/extraction.md is empty", []
    missing = [name for name, pattern in SECTIONS if not re.search(pattern, text)]
    if missing:
        return (
            False,
            "missing section(s): " + ", ".join(missing),
            [f"missing: {name}" for name in missing],
        )
    return True, f"all {len(SECTIONS)} required sections are present", []


SECRETS = [
    ("bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{12,}=*")),
    ("API key", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    (
        "assigned secret",
        re.compile(
            r"(?i)\b(password|passwd|secret|token|api[_-]?key)\s*[:=]\s*[\"']?[A-Za-z0-9._~+/=-]{12,}"
        ),
    ),
    ("absolute home path", re.compile(r"(?<![\w.-])/(?:home|Users)/[A-Za-z0-9._@-]+")),
]


def written_text(run: Path) -> list[tuple[str, str]]:
    """The text a run wrote: the report, and the new content of the checkout."""
    checkout = run / "checkout"
    written = []
    report = run / "state" / "extraction.md"
    if report.is_file():
        written.append(
            (
                "state/extraction.md",
                report.read_text(encoding="utf-8", errors="replace"),
            )
        )
    if not checkout.is_dir():
        return written
    diff = git(checkout, "diff", "HEAD", "--unified=0")
    added = [
        line[1:]
        for line in diff.stdout.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    written.append(("the checkout diff", "\n".join(added)))
    for _, path in changed_paths(checkout):
        if path.startswith(PINNED_SKILL_PREFIX):
            continue
        target = checkout / path
        if target.is_file():
            try:
                written.append((path, target.read_text(encoding="utf-8")))
            except UnicodeDecodeError:
                continue
    return written


def gate_5_no_secrets(run: Path) -> tuple[bool, str, list[str]]:
    """No credential, token or private path appears in anything written."""
    findings = []
    for where, text in written_text(run):
        for line_number, line in enumerate(text.splitlines(), 1):
            for name, pattern in SECRETS:
                if pattern.search(line):
                    findings.append(
                        f"{where}:{line_number}: {name}: {line.strip()[:120]}"
                    )
    if findings:
        return False, f"{len(findings)} possible secret or private path", findings
    return True, "no credential, token or private path found", []


def skill_files(checkout: Path) -> list[str]:
    """Every skill this run wrote, including one an ignore rule hides."""
    skills = []
    for path in sorted(checkout.glob(".opencode/skills/*/SKILL.md")):
        relative = path.relative_to(checkout).as_posix()
        at_head = subprocess.run(
            ["git", "-C", str(checkout), "show", f"HEAD:{relative}"],
            capture_output=True,
        )
        if at_head.returncode != 0 or at_head.stdout != path.read_bytes():
            skills.append(relative)
    return skills


def gate_6_not_ignored(run: Path) -> tuple[bool, str, list[str]]:
    """For every skill written, git check-ignore -q <path> exits 1."""
    checkout = run / "checkout"
    if not checkout.is_dir():
        return False, "checkout/ is missing", []
    ignored = []
    for path in skill_files(checkout):
        if git(checkout, "check-ignore", "-q", "--", path).returncode == 0:
            ignored.append(f"{path}: silently ignored by a .gitignore rule")
    if ignored:
        return False, f"{len(ignored)} written skill(s) are ignored", ignored
    return True, "every written skill is tracked, not ignored", []


def gate_7_sessions(run: Path, bundle: Path) -> tuple[bool, str, list[str]]:
    """The run names the sessions it read and the ones it did not."""
    report = run / "state" / "extraction.md"
    if not report.is_file():
        return False, "state/extraction.md is missing", []
    text = report.read_text(encoding="utf-8", errors="replace")
    try:
        ids = [
            entry["id"]
            for entry in json.loads(bundle.read_text(encoding="utf-8"))["digests"]
        ]
    except (OSError, KeyError, json.JSONDecodeError) as error:
        return False, f"cannot read the bundle at {bundle}: {error}", []
    # A report may shorten an id to its first 14 characters when it cites a
    # digest inline. The sessions section names the full id.
    missing = [session for session in ids if session[:14] not in text]
    problems = [f"session not named in the report: {session}" for session in missing]
    if not re.search(NOT_READ, text):
        problems.append(
            "the report does not say which sessions it did not read (or that none was skipped)"
        )
    if problems:
        return False, f"{len(problems)} session-accounting problem(s)", problems
    return True, f"all {len(ids)} sessions are accounted for", []


def evaluate(run: Path, bundle: Path = BUNDLE) -> dict:
    """Every gate's result for one run."""
    meta = read_meta(run)
    rows: list[dict] = []

    def add(label: str, passed: bool, detail: str, findings: list[str]) -> None:
        rows.append(
            {"gate": label, "passed": passed, "detail": detail, "findings": findings}
        )

    passed, detail = gate_1_exit(run, meta)
    add("1 exit within 45 minutes", passed, detail, [])
    passed, detail = gate_2_no_commit(run, meta)
    add("2 no new commit", passed, detail, [])
    for label, function in (
        ("3 write scope", gate_3_write_scope),
        ("4 extraction report", gate_4_report),
        ("5 no secrets or private paths", gate_5_no_secrets),
        ("6 skills are not ignored", gate_6_not_ignored),
    ):
        passed, detail, findings = function(run)
        add(label, passed, detail, findings)
    passed, detail, findings = gate_7_sessions(run, bundle)
    add("7 sessions read and not read", passed, detail, findings)
    return {
        "run": str(run),
        "gates": rows,
        "passed": all(row["passed"] for row in rows),
    }


def print_report(result: dict) -> None:
    print(f"== {result['run']}")
    for row in result["gates"]:
        mark = "PASS" if row["passed"] else "FAIL"
        print(f"  gate {row['gate']}: {mark} - {row['detail']}")
        for finding in row["findings"]:
            print(f"    - {finding}")
    print()


def plant_run(directory: Path, name: str) -> Path:
    """A run directory with a baseline commit and nothing else."""
    run = directory / name
    checkout = run / "checkout"
    (run / "state").mkdir(parents=True)
    checkout.mkdir()
    (checkout / "README.md").write_text("baseline\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(checkout)], check=True)
    subprocess.run(["git", "-C", str(checkout), "add", "README.md"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(checkout),
            "-c",
            "user.name=gate",
            "-c",
            "user.email=gate@example.invalid",
            "commit",
            "-q",
            "-m",
            "baseline",
        ],
        check=True,
    )
    return run


def good_report(bundle: Path) -> str:
    """A report that passes every section and session check."""
    ids = [
        entry["id"]
        for entry in json.loads(bundle.read_text(encoding="utf-8"))["digests"]
    ]
    sessions = "\n".join(f"- `{session}`: a lesson." for session in ids)
    return f"""# Extraction report

## Lessons and the files they became

| lesson | file |
| --- | --- |
| a rule | `AGENTS.md` |

## The concern map

Concern A: `AGENTS.md`. Commit message: `docs(agents): a rule`.

## Checked

| claim | command | version | result |
| --- | --- | --- | --- |
| git | `git --version` | 2.43.0 | 2.43.0 |

## Claims not checked

- none.

## Linter counts

Before and after: 0 finding(s), 0 finding(s).

## Hard findings that remain

None.

## Evals

None ran, because this fixture has nothing to run.

## Self-review

Verdict: ready. Each criterion passes.

## Sessions read

{sessions}

Not read: none of the nine sessions was skipped.

## Corrected claims outside the repository

None.

## Alternatives chosen against

- Nothing needed a decision.
"""


def self_test(bundle: Path) -> int:
    """Prove each gate fails on a planted defect before trusting its pass."""
    with tempfile.TemporaryDirectory(prefix="gates-selftest-") as directory:
        root = Path(directory)

        # Gates 3, 4, 5, 6 and 7: an outside write, an ignored skill, a bad
        # report, a secret and an unaccounted session.
        bad = plant_run(root, "bad")
        checkout = bad / "checkout"
        (checkout / "tests").mkdir()
        (checkout / "tests" / "test_planted.py").write_text("pass\n", encoding="utf-8")
        (checkout / ".opencode" / "skills" / "planted").mkdir(parents=True)
        (checkout / ".opencode" / "skills" / "planted" / "SKILL.md").write_text(
            "---\nname: planted\ndescription: planted\n---\n", encoding="utf-8"
        )
        (checkout / ".gitignore").write_text(".opencode/\n", encoding="utf-8")
        (bad / "state" / "extraction.md").write_text(
            "# Report\n\nA token: Bearer abcdefghijklmnop\n"
            "A path: /home/planted/private\n",
            encoding="utf-8",
        )
        (bad / "meta.json").write_text(
            json.dumps(
                {
                    "exit_code": 0,
                    "timed_out": False,
                    "duration_s": 10,
                    "head_before": head(checkout),
                    "head_after": head(checkout),
                }
            ),
            encoding="utf-8",
        )

        # Gate 1: the run timed out.
        timeout = plant_run(root, "timeout")
        (timeout / "state" / "extraction.md").write_text(
            good_report(bundle), encoding="utf-8"
        )
        (timeout / "meta.json").write_text(
            json.dumps(
                {
                    "exit_code": 124,
                    "timed_out": True,
                    "duration_s": RUN_TIMEOUT_S,
                    "head_before": head(timeout / "checkout"),
                    "head_after": head(timeout / "checkout"),
                }
            ),
            encoding="utf-8",
        )

        # Gate 2: a commit was made after the recorded HEAD.
        committed = plant_run(root, "committed")
        before = head(committed / "checkout")
        (committed / "state" / "extraction.md").write_text(
            good_report(bundle), encoding="utf-8"
        )
        (committed / "checkout" / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(committed / "checkout"), "add", "AGENTS.md"], check=True
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(committed / "checkout"),
                "-c",
                "user.name=gate",
                "-c",
                "user.email=gate@example.invalid",
                "commit",
                "-q",
                "-m",
                "a commit",
            ],
            check=True,
        )
        (committed / "meta.json").write_text(
            json.dumps(
                {
                    "exit_code": 0,
                    "timed_out": False,
                    "duration_s": 10,
                    "head_before": before,
                    "head_after": head(committed / "checkout"),
                }
            ),
            encoding="utf-8",
        )

        expected = {
            "bad": {"3", "4", "5", "6", "7"},
            "timeout": {"1"},
            "committed": {"2"},
        }
        failures = 0
        for name, want in expected.items():
            result = evaluate(root / name, bundle)
            failed = {
                row["gate"].split()[0] for row in result["gates"] if not row["passed"]
            }
            if failed != want:
                print(
                    f"self-test: {name} failed gates {sorted(failed)} are not {sorted(want)}"
                )
                print_report(result)
                failures += 1
            elif not result["passed"]:
                print(f"self-test: {name} failed its planted gate as expected")
        if failures:
            return 1
        print("self-test: every gate failed on its planted defect")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the structural gates over collected evaluation runs."
    )
    parser.add_argument("runs", nargs="*", type=Path, help="run directories")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument(
        "--bundle", type=Path, default=BUNDLE, help="the frozen bundle to read ids from"
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="prove each gate fails on a planted defect",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test(args.bundle)
    if not args.runs:
        parser.error("name at least one run directory, or use --self-test")
    for run in args.runs:
        if not run.is_dir():
            parser.error(f"{run} is not a directory")

    results = [evaluate(run, args.bundle) for run in args.runs]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            print_report(result)
        failed = [result for result in results if not result["passed"]]
        print(
            f"gates: {len(results) - len(failed)}/{len(results)} run(s) pass every gate"
        )
        for result in failed:
            names = ", ".join(
                row["gate"] for row in result["gates"] if not row["passed"]
            )
            print(f"  {result['run']}: failed gate(s) {names}")
    return 0 if all(result["passed"] for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
