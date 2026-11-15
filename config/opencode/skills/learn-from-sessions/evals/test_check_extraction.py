#!/usr/bin/env python3
"""Test `scripts/check-extraction` against a checkout built for the test.

Every check is proved in both directions: it passes on a clean extraction and
fails on a planted defect. A check that cannot fail proves nothing, so a test
that only asserts the pass would let a broken check ship.

The checkout is a real `git init` repository, because the write-scope and
ignore checks ask git. No network, no session store, no OpenCode.

Run it from anywhere:

    python3 -m pytest config/opencode/skills/learn-from-sessions/evals/test_check_extraction.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPT = SKILL_DIR / "scripts" / "check-extraction"

SESSIONS = ["ses_aaaaaaaaaaaaaaaaaaaaaa", "ses_bbbbbbbbbbbbbbbbbbbbbb"]

REPORT = """# Extraction report

## Lessons and the files they became

| lesson | file |
| --- | --- |
| a rule | `AGENTS.md` |

## The concern map

Concern A: `.opencode/skills/planted/SKILL.md`.

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

## Completeness pass

The digests were read again against this report. No required lesson was left out.

## Self-review

Verdict: ready. Each criterion passes.

## Sessions read

- `ses_aaaaaaaaaaaaaaaaaaaaaa`: a lesson.
- `ses_bbbbbbbbbbbbbbbbbbbbbb`: a lesson.

Not read: none of the two sessions was skipped.

## Corrected claims outside the repository

None.

## Alternatives chosen against

- Nothing needed a decision.
"""


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True
    )


def commit(repo: Path, message: str) -> None:
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=check",
            "-c",
            "user.email=check@example.invalid",
            "commit",
            "-q",
            "-m",
            message,
        ],
        check=True,
        capture_output=True,
    )


def make_repo(root: Path) -> Path:
    """A checkout with one baseline commit and one written skill."""
    repo = root / "checkout"
    repo.mkdir()
    (repo / "README.md").write_text("baseline\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    git(repo, "add", "README.md")
    commit(repo, "baseline")
    skill = repo / ".opencode" / "skills" / "planted" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: planted\ndescription: planted\n---\n", encoding="utf-8"
    )
    (repo / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
    (root / "state").mkdir()
    (root / "state" / "extraction.md").write_text(REPORT, encoding="utf-8")
    digests = root / "digests"
    digests.mkdir()
    for session in SESSIONS:
        (digests / f"{session}.md").write_text("# digest\n", encoding="utf-8")
    return repo


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return make_repo(tmp_path)


def run_check(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(repo), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


def rows(proc: subprocess.CompletedProcess[str]) -> dict[str, dict]:
    return {row["gate"]: row for row in json.loads(proc.stdout)}


def test_clean_fixture_passes_every_check(repo: Path) -> None:
    proc = run_check(repo, "--digests", str(repo.parent / "digests"), "--json")
    assert proc.returncode == 0, proc.stderr
    result = rows(proc)
    assert set(result) == {
        "3 write scope",
        "4 extraction report",
        "5 no secrets or private paths",
        "6 skills are not ignored",
        "7 sessions read and not read",
        "8 citation claims",
        "9 completeness pass",
    }
    for gate, row in result.items():
        assert row["passed"], f"{gate}: {row['detail']}"
        assert row["findings"] == []


def test_write_scope_fails_on_a_change_outside_the_allowlist(repo: Path) -> None:
    tests = repo / "tests"
    tests.mkdir()
    (tests / "test_planted.py").write_text("pass\n", encoding="utf-8")
    git(repo, "add", "tests/test_planted.py")
    proc = run_check(repo, "--digests", str(repo.parent / "digests"), "--json")
    assert proc.returncode == 1
    row = rows(proc)["3 write scope"]
    assert not row["passed"]
    assert row["detail"] == "1 path(s) outside the allowlist"
    assert row["findings"] == ["tests/test_planted.py (A): outside the allowlist"]


def test_report_fails_when_a_required_section_is_missing(repo: Path) -> None:
    report = repo.parent / "state" / "extraction.md"
    report.write_text(
        report.read_text(encoding="utf-8").replace("## The concern map", "## Map"),
        encoding="utf-8",
    )
    proc = run_check(repo, "--digests", str(repo.parent / "digests"), "--json")
    assert proc.returncode == 1
    row = rows(proc)["4 extraction report"]
    assert not row["passed"]
    assert row["detail"] == "missing section(s): concern map"
    assert row["findings"] == ["missing: concern map"]


def test_secret_check_fails_on_a_credential_in_a_written_file(repo: Path) -> None:
    scripts = repo / "scripts"
    scripts.mkdir()
    (scripts / "planted.sh").write_text(
        "#!/bin/sh\ntoken: Bearer abcdefghijklmnop\n", encoding="utf-8"
    )
    proc = run_check(repo, "--digests", str(repo.parent / "digests"), "--json")
    assert proc.returncode == 1
    row = rows(proc)["5 no secrets or private paths"]
    assert not row["passed"]
    assert row["detail"] == "1 possible secret or private path"
    assert "scripts/planted.sh:2: bearer token" in row["findings"][0]


def test_ignore_check_fails_on_a_skill_a_gitignore_hides(repo: Path) -> None:
    (repo / ".gitignore").write_text(".opencode/\n", encoding="utf-8")
    git(repo, "add", ".gitignore")
    commit(repo, "ignore the skills directory")
    proc = run_check(repo, "--digests", str(repo.parent / "digests"), "--json")
    assert proc.returncode == 1
    row = rows(proc)["6 skills are not ignored"]
    assert not row["passed"]
    assert row["detail"] == "1 written skill(s) are ignored"
    assert row["findings"] == [
        ".opencode/skills/planted/SKILL.md: silently ignored by a .gitignore rule"
    ]


def test_sessions_fail_when_the_report_omits_a_session(repo: Path) -> None:
    report = repo.parent / "state" / "extraction.md"
    report.write_text(
        report.read_text(encoding="utf-8").replace(
            "- `ses_aaaaaaaaaaaaaaaaaaaaaa`: a lesson.\n", ""
        ),
        encoding="utf-8",
    )
    proc = run_check(repo, "--digests", str(repo.parent / "digests"), "--json")
    assert proc.returncode == 1
    row = rows(proc)["7 sessions read and not read"]
    assert not row["passed"]
    assert row["detail"] == "1 session-accounting problem(s)"
    assert row["findings"] == [
        "session not named in the report: ses_aaaaaaaaaaaaaaaaaaaaaa"
    ]


def test_sessions_fail_when_the_report_does_not_say_what_it_did_not_read(
    repo: Path,
) -> None:
    report = repo.parent / "state" / "extraction.md"
    report.write_text(
        report.read_text(encoding="utf-8").replace(
            "Not read: none of the two sessions was skipped.\n", ""
        ),
        encoding="utf-8",
    )
    proc = run_check(repo, "--digests", str(repo.parent / "digests"), "--json")
    assert proc.returncode == 1
    row = rows(proc)["7 sessions read and not read"]
    assert not row["passed"]
    assert row["findings"] == [
        "the report does not say which sessions it did not read (or that none was skipped)"
    ]


def test_no_digests_skips_accounting_instead_of_failing(repo: Path) -> None:
    proc = run_check(repo, "--json")
    assert proc.returncode == 0, proc.stderr
    row = rows(proc)["7 sessions read and not read"]
    assert row["passed"]
    assert row["detail"].startswith("skipped:")
    assert row["findings"] == []


def test_a_missing_repo_is_a_usage_error(tmp_path: Path) -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(tmp_path / "absent")],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 2
    assert "is not a directory" in proc.stderr


def rewrite_report(repo: Path, old: str, new: str) -> None:
    report = repo.parent / "state" / "extraction.md"
    text = report.read_text(encoding="utf-8")
    assert old in text, f"fixture no longer holds: {old}"
    report.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_claims_fail_on_a_path_the_checkout_does_not_hold(repo: Path) -> None:
    rewrite_report(
        repo,
        "None ran, because this fixture has nothing to run.",
        "The mechanical gates did run `scripts/measure.py` on the skills.",
    )
    proc = run_check(repo, "--digests", str(repo.parent / "digests"), "--json")
    assert proc.returncode == 1
    row = rows(proc)["8 citation claims"]
    assert not row["passed"]
    assert row["detail"] == "1 citation(s) the checkout does not support"
    assert "scripts/measure.py" in row["findings"][0]
    assert "not in the checkout" in row["findings"][0]


def test_claims_fail_on_a_line_past_the_end_of_the_file(repo: Path) -> None:
    rewrite_report(repo, "| a rule | `AGENTS.md` |", "| a rule | `AGENTS.md:900` |")
    proc = run_check(repo, "--digests", str(repo.parent / "digests"), "--json")
    assert proc.returncode == 1
    row = rows(proc)["8 citation claims"]
    assert not row["passed"]
    assert "AGENTS.md has 1 line(s)" in row["findings"][0]


def test_claims_accept_a_path_the_report_marks_as_new(repo: Path) -> None:
    rewrite_report(
        repo,
        "None ran, because this fixture has nothing to run.",
        "Add `scripts/new-check.py` and run it with the other checks.",
    )
    proc = run_check(repo, "--digests", str(repo.parent / "digests"), "--json")
    row = rows(proc)["8 citation claims"]
    assert row["passed"], row["findings"]


def test_claims_fail_on_a_remote_command_in_a_checkout_with_no_remote(
    repo: Path,
) -> None:
    rewrite_report(
        repo,
        "| git | `git --version` | 2.43.0 | 2.43.0 |",
        "| git | `git --version` | 2.43.0 | 2.43.0 |\n"
        "| the pull request fields | `gh pr list --json number` | gh 2.104.0 | "
        "accepted, `[]` |",
    )
    proc = run_check(repo, "--digests", str(repo.parent / "digests"), "--json")
    assert proc.returncode == 1
    row = rows(proc)["8 citation claims"]
    assert not row["passed"]
    assert "needs a git remote" in row["findings"][0]


def test_claims_accept_a_remote_command_that_names_its_repository(repo: Path) -> None:
    rewrite_report(
        repo,
        "| git | `git --version` | 2.43.0 | 2.43.0 |",
        "| git | `git --version` | 2.43.0 | 2.43.0 |\n"
        "| the pull request fields | `gh pr list --repo owner/name --json number` "
        "| gh 2.104.0 | accepted |",
    )
    proc = run_check(repo, "--digests", str(repo.parent / "digests"), "--json")
    row = rows(proc)["8 citation claims"]
    assert row["passed"], row["findings"]


def test_claims_accept_a_skill_written_as_id_over_skill_md(repo: Path) -> None:
    rewrite_report(
        repo,
        "| a rule | `AGENTS.md` |",
        "| a rule | `planted/SKILL.md` |",
    )
    proc = run_check(repo, "--digests", str(repo.parent / "digests"), "--json")
    row = rows(proc)["8 citation claims"]
    assert row["passed"], row["findings"]


def test_completeness_fails_when_the_report_does_not_record_it(repo: Path) -> None:
    rewrite_report(
        repo,
        "## Completeness pass\n\nThe digests were read again against this report. "
        "No required lesson was left out.\n\n",
        "",
    )
    proc = run_check(repo, "--digests", str(repo.parent / "digests"), "--json")
    assert proc.returncode == 1
    row = rows(proc)["9 completeness pass"]
    assert not row["passed"]
    assert row["detail"] == "the report does not record the completeness pass"
