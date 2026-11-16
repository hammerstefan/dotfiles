#!/usr/bin/env python3
"""Grade the hwt-wrapup brief against the evals in evals.json.

The subject is the instructions the reflection session reads: `brief.md.tmpl`
and `SKILL.md`. The extraction's own lessons moved to the `learn-from-sessions`
suite when the extraction became a skill, so these checks cover what the wrapup
still does after it: the delegation, the commits, the pull request body, the
retention and the close.

Usage:
    grade.py                    # grade this skill's template and SKILL.md
    grade.py --brief FILE       # grade a rendered brief instead of the template
    grade.py --render           # render a fresh brief with scripts/hwt-wrapup and grade it
    grade.py --json             # machine-readable result
    grade.py --verbose          # show the matched text for each pass

Exit 0 when every expectation passes, 1 when one fails, 2 on a usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
EVALS = Path(__file__).resolve().parent / "evals.json"

STEPS = 9
HEADINGS = (
    "# Sessions to read",
    "# The trigger session's trace",
    "# Rules",
    "# What to do",
)


def norm(text: str) -> str:
    text = text.replace("\u2019", "'").replace("\u2014", "-")
    return re.sub(r"\s+", " ", text.lower()).strip()


def find(text: str, pattern: str) -> re.Match | None:
    return re.search(pattern, text)


def sentence_at(text: str, start: int) -> str:
    """The sentence around a match, for evidence."""
    left = max(text.rfind(". ", 0, start), text.rfind("\n", 0, start))
    right = text.find(". ", start)
    if right == -1:
        right = min(len(text), start + 160)
    return text[left + 1 : right + 1].strip()[:220]


def evidence(text: str, pattern: str) -> str:
    match = find(text, pattern)
    if not match:
        return ""
    return sentence_at(text, match.start())


# Each check is (eval id, expectation index, description, function). A function
# takes the normalised brief and skill text and returns (passed, evidence).
def check_names_skill(b: str, s: str):
    return bool(find(b, r"learn-from-sessions")), evidence(b, r"learn-from-sessions")


def check_loaded_before(b: str, s: str):
    ok = find(b, r"load[^.]{0,80}learn-from-sessions") and find(b, r"write nothing")
    return bool(ok), evidence(b, r"load[^.]{0,80}learn-from-sessions")


def check_stops_when_missing(b: str, s: str):
    ok = find(b, r"cannot be loaded") and find(b, r"write nothing")
    return bool(ok), evidence(b, r"cannot be loaded")


def check_one_concern(b: str, s: str):
    pattern = r"one concern per commit"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_paths_from_report(b: str, s: str):
    ok = find(b, r"concern map") and find(b, r"extraction report")
    return bool(ok), evidence(b, r"concern map")


def check_clean_tree(b: str, s: str):
    ok = find(b, r"git status --porcelain") and find(b, r"print nothing")
    return bool(ok), evidence(b, r"git status --porcelain")


def check_checked_section(b: str, s: str):
    pattern = r"checked[^.]{0,40}section"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_linter_counts(b: str, s: str):
    ok = find(b, r"linter counts") and find(b, r"\bbody\b")
    return bool(ok), evidence(b, r"linter counts")


def check_evals_in_body(b: str, s: str):
    pattern = r"evals (run or not|run or not run|you ran)"
    return bool(find(b, pattern) and find(b, r"\bbody\b")), evidence(b, pattern)


def check_verdict_in_body(b: str, s: str):
    ok = find(b, r"verdict") and find(b, r"\bbody\b")
    return bool(ok), evidence(b, r"verdict")


def check_never_merge(b: str, s: str):
    pattern = r"never merge the pull request and never force-push, unless"
    return bool(find(b, pattern)), evidence(b, r"never merge the pull request")


def check_never_force_push(b: str, s: str):
    pattern = r"never force-push, unless the person chose"
    return bool(find(b, pattern)), evidence(b, r"never force-push")


def check_close_after_pr(b: str, s: str):
    pattern = r"not before the pull request is open"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_dirty(b: str, s: str):
    ok = find(b, r"dirty") and find(b, r"close nothing")
    return bool(ok), evidence(b, r"dirty")


def check_busy(b: str, s: str):
    pattern = r"busy within the last day"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_keeps_branch(b: str, s: str):
    pattern = r"keeps the branch"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_asks_about_space(b: str, s: str):
    ok = find(b, r"ask about this space") and find(b, r"question")
    return bool(ok), evidence(b, r"ask about this space")


def check_report_sessions(b: str, s: str):
    ok = find(b, r"sessions read") and find(b, r"any you did not")
    return bool(ok), evidence(b, r"sessions read")


def check_report_claims(b: str, s: str):
    ok = find(b, r"claims checked") and find(b, r"ones you did not")
    return bool(ok), evidence(b, r"claims checked")


def check_commit_message(b: str, s: str):
    ok = find(b, r"commit message") and find(b, r"must not repeat")
    return bool(ok), evidence(b, r"commit message")


def check_external_copy(b: str, s: str):
    ok = find(b, r"outside this repository") and find(b, r"correct it")
    return bool(ok), evidence(b, r"outside this repository")


def check_merge_option(b: str, s: str):
    ok = find(b, r"rebase the pull request onto the base") and find(b, r"merge it")
    return bool(ok), evidence(b, r"rebase the pull request onto the base")


def check_rebase_before_merge(b: str, s: str):
    # The rendered brief names the base branch; the template names the
    # placeholder. Both count.
    ok = find(b, r"rebase origin/") and find(b, r"gh pr merge")
    return bool(ok), evidence(b, r"rebase origin/")


def check_lease_push(b: str, s: str):
    ok = find(b, r"--force-with-lease=refs/heads") and find(b, r"ls-remote")
    return bool(ok), evidence(b, r"--force-with-lease=refs/heads")


def check_closes_after_merge(b: str, s: str):
    ok = find(b, r"close this space and remove this checkout\*\*") and find(
        b, r"when the answer was"
    )
    return bool(ok), evidence(b, r"close this space and remove this checkout")


def check_conflict_leaves_pr_open(b: str, s: str):
    ok = find(b, r"rebase --abort") and find(b, r"leave the pull request open")
    return bool(ok), evidence(b, r"rebase --abort")


def check_no_admin_no_delete(b: str, s: str):
    ok = find(b, r"never pass `--admin`") and find(b, r"never pass `--delete-branch`")
    return bool(ok), evidence(b, r"never pass `--admin`")


CHECKS = {
    (1, 0): ("the brief names learn-from-sessions", check_names_skill),
    (1, 1): ("the skill is loaded before anything is written", check_loaded_before),
    (1, 2): ("the brief stops when the skill is missing", check_stops_when_missing),
    (2, 0): ("one concern per commit", check_one_concern),
    (2, 1): ("the paths and message come from the report", check_paths_from_report),
    (2, 2): ("the tree is clean after the commits", check_clean_tree),
    (3, 0): ("the Checked section reaches the body", check_checked_section),
    (3, 1): ("the linter counts reach the body", check_linter_counts),
    (3, 2): ("the evals run reach the body", check_evals_in_body),
    (3, 3): ("the verdict reaches the body", check_verdict_in_body),
    (4, 0): ("the pull request is never merged", check_never_merge),
    (4, 1): ("the branch is never force-pushed", check_never_force_push),
    (5, 0): ("the close comes after the pull request", check_close_after_pr),
    (5, 1): ("a dirty checkout closes nothing", check_dirty),
    (5, 2): ("a busy session closes nothing", check_busy),
    (5, 3): ("the branch is kept", check_keeps_branch),
    (5, 4): ("the session asks before closing its space", check_asks_about_space),
    (6, 0): ("the report names the sessions read and not read", check_report_sessions),
    (6, 1): ("the report names the claims checked and not", check_report_claims),
    (7, 0): ("a repeating commit message is corrected", check_commit_message),
    (7, 1): ("an outside copy is corrected where it lives", check_external_copy),
    (8, 0): ("the question offers the merge option", check_merge_option),
    (8, 1): ("the branch is rebased before the merge", check_rebase_before_merge),
    (8, 2): ("the rebased branch is pushed with a lease", check_lease_push),
    (8, 3): ("both are closed after the merge", check_closes_after_merge),
    (8, 4): ("a conflict leaves the pull request open", check_conflict_leaves_pr_open),
    (8, 5): ("no --admin and no --delete-branch", check_no_admin_no_delete),
}


def render_brief(worktree: Path) -> Path:
    """Render a fresh brief with the repository's hwt-wrapup script."""
    script = worktree / "scripts/hwt-wrapup"
    if not script.is_file():
        for parent in worktree.parents:
            candidate = parent / "scripts/hwt-wrapup"
            if candidate.is_file():
                script = candidate
                break
        else:
            raise FileNotFoundError("scripts/hwt-wrapup not found above the worktree")
    state = Path(tempfile.mkdtemp(prefix="hwt-wrapup-eval-"))
    proc = subprocess.run(
        [sys.executable, str(script), "--dry-run", "--state", str(state)],
        cwd=worktree,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip())
    brief = state / "brief.md"
    if not brief.is_file():
        raise RuntimeError(f"{brief} was not written")
    return brief


def structural_problems(brief: Path) -> list[str]:
    """The failures a template-only grade cannot see."""
    text = brief.read_text(encoding="utf-8")
    problems = []
    if "{{" in text or "}}" in text:
        problems.append("an unfilled placeholder remains")
    for number in range(1, STEPS + 1):
        if f"\n{number}. **" not in text:
            problems.append(f"step {number} is missing")
    for heading in HEADINGS:
        if heading not in text:
            problems.append(f"the {heading} heading is missing")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Grade the hwt-wrapup brief.")
    parser.add_argument("--brief", metavar="FILE", help="grade a rendered brief")
    parser.add_argument(
        "--render",
        action="store_true",
        help="render a fresh brief with scripts/hwt-wrapup and grade it",
    )
    parser.add_argument("--worktree", metavar="DIR", help="worktree to render from")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--verbose", action="store_true", help="show matched text")
    args = parser.parse_args()

    if args.render:
        try:
            brief_path = render_brief(
                Path(args.worktree) if args.worktree else Path.cwd()
            )
        except (OSError, RuntimeError) as error:
            print(f"grade: could not render: {error}", file=sys.stderr)
            return 2
        problems = structural_problems(brief_path)
        if problems:
            print("grade: the rendered brief is not sound:", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
            return 1
    else:
        brief_path = Path(args.brief) if args.brief else SKILL_DIR / "brief.md.tmpl"
    skill_path = SKILL_DIR / "SKILL.md"
    for path in (brief_path, skill_path, EVALS):
        if not path.is_file():
            print(f"grade: {path} is missing", file=sys.stderr)
            return 2

    brief = norm(brief_path.read_text(encoding="utf-8"))
    skill = norm(skill_path.read_text(encoding="utf-8"))
    cases = json.loads(EVALS.read_text(encoding="utf-8"))["evals"]

    results = []
    passed = 0
    counted = 0
    unmapped = 0
    for case in cases:
        for index, text in enumerate(case["expectations"]):
            entry = CHECKS.get((case["id"], index))
            if entry is None:
                unmapped += 1
                results.append(
                    {
                        "eval": case["id"],
                        "name": case["name"],
                        "expectation": text,
                        "passed": None,
                        "evidence": "no check",
                    }
                )
                continue
            counted += 1
            ok, why = entry[1](brief, skill)
            passed += 1 if ok else 0
            results.append(
                {
                    "eval": case["id"],
                    "name": case["name"],
                    "expectation": text,
                    "passed": ok,
                    "evidence": why,
                }
            )

    if args.json:
        print(
            json.dumps(
                {
                    "passed": passed,
                    "counted": counted,
                    "unmapped": unmapped,
                    "rate": round(passed / counted, 3) if counted else 0,
                    "results": results,
                },
                indent=2,
            )
        )
    else:
        print(
            f"hwt-wrapup evals: {passed}/{counted} expectations pass "
            f"({round(100 * passed / counted) if counted else 0}%)"
        )
        if unmapped:
            print(f"{unmapped} expectation(s) have no check; add one to CHECKS.")
        print()
        current = None
        for row in results:
            if row["eval"] != current:
                current = row["eval"]
                print(f"eval {current}  {row['name']}")
            mark = "PASS" if row["passed"] else "FAIL"
            print(f"  [{mark}] {row['expectation']}")
            if args.verbose or row["passed"] is False:
                if row["evidence"]:
                    print(f"         {row['evidence']}")
        print()

    return 0 if counted and not unmapped and passed == counted else 1


if __name__ == "__main__":
    sys.exit(main())
