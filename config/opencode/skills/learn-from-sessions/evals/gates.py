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
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import checks  # noqa: E402  (the runtime's checks, so both verdicts agree)

RUN_TIMEOUT_S = 45 * 60

BUNDLE = Path(__file__).resolve().parent / "bundle" / "bundle.json"


def git(checkout: Path, *args: str) -> subprocess.CompletedProcess:
    """One git call in the checkout."""
    return checks.git(checkout, *args)


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
    return checks.check_write_scope(checkout)


def gate_4_report(run: Path) -> tuple[bool, str, list[str]]:
    """state/extraction.md exists and holds every section the skill requires."""
    return checks.check_report(run / "state" / "extraction.md")


def gate_5_no_secrets(run: Path) -> tuple[bool, str, list[str]]:
    """No credential, token or private path appears in anything written."""
    return checks.check_secrets(run / "checkout", run / "state" / "extraction.md")


def gate_6_not_ignored(run: Path) -> tuple[bool, str, list[str]]:
    """For every skill written, git check-ignore -q <path> exits 1."""
    checkout = run / "checkout"
    if not checkout.is_dir():
        return False, "checkout/ is missing", []
    return checks.check_not_ignored(checkout)


def gate_7_sessions(run: Path, bundle: Path) -> tuple[bool, str, list[str]]:
    """The run names the sessions it read and the ones it did not."""
    report = run / "state" / "extraction.md"
    if not report.is_file():
        return False, "state/extraction.md is missing", []
    try:
        ids = [
            entry["id"]
            for entry in json.loads(bundle.read_text(encoding="utf-8"))["digests"]
        ]
    except (OSError, KeyError, json.JSONDecodeError) as error:
        return False, f"cannot read the bundle at {bundle}: {error}", []
    return checks.check_sessions(report, ids)


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
