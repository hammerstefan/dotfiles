#!/usr/bin/env python3
"""Grade the hwt-wrapup brief against the evals in evals.json.

The subject is the instructions the reflection session reads: `brief.md.tmpl`
and `SKILL.md`. These checks are deterministic, so a change to the wording can
be measured before it reaches a reflection session. They check that an
instruction is present, not that a reflection session obeyed it; a real wrapup
is the final check.

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
def check_run_example(b: str, s: str):
    run = find(b, r"run (every|each|the) (example|command)")
    then = find(b, r"(before (you )?(write|commit|stage))|(show (its|the) output)")
    return bool(run and then), evidence(b, r"run (every|each|the) (example|command)")


def check_command_and_result(b: str, s: str):
    ok = find(b, r"commands?[^.]{0,200}(result|output)") and find(
        b, r"pull request body"
    )
    return bool(ok), evidence(b, r"commands?[^.]{0,200}(result|output)")


def check_quote_is_evidence(b: str, s: str):
    ok = find(b, r"quote[s]?[^.]{0,80}evidence") and find(
        b, r"(not a fact|not fact|rather than a fact)"
    )
    return bool(ok), evidence(b, r"quote[s]?[^.]{0,80}evidence")


def check_version(b: str, s: str):
    ok = find(b, r"(name|record|state|give)[^.]{0,60}version") or find(
        b, r"version[^.]{0,60}(tested|you tested)"
    )
    return bool(ok), evidence(b, r"version")


def check_subcommand(b: str, s: str):
    return bool(find(b, r"sub-?command")), evidence(b, r"sub-?command")


def check_no_blanket(b: str, s: str):
    ok = find(b, r"blanket") and find(b, r"(split|drop|per sub-?command)")
    return bool(ok), evidence(b, r"blanket")


def check_word_cap(b: str, s: str):
    ok = find(b, r"(under|below|at most|fewer than) (twenty-five|25) words") or find(
        b, r"25-word"
    )
    return bool(ok), evidence(b, r"(twenty-five|25) words")


def check_trigger_phrases(b: str, s: str):
    ok = find(b, r"trigger phrase") and find(
        b, r"(keep|preserve|verbatim|survive|unchanged)"
    )
    return bool(ok), evidence(b, r"trigger phrase")


def check_description_budget(b: str, s: str):
    pattern = r"(under|below|at most|fewer than) (sixty|60) words"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_description_is_only_text(b: str, s: str):
    pattern = r"description[^.]{0,180}(injected|only text|only thing|before it loads)"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_script_exit_code(b: str, s: str):
    ok = all(
        find(b, p)
        for p in (
            r"script",
            r"exit (code|status)",
            r"(mechanical|banned.word|grep|header|collision|file list)",
        )
    )
    return bool(ok), evidence(b, r"exit (code|status)")


def check_script_runs_in_verify(b: str, s: str):
    pattern = r"(run|runs)[^.]{0,80}step 7"
    return bool(find(b, r"step 7")), evidence(b, pattern)


def check_linter_on_changes(b: str, s: str):
    ok = find(b, r"linter") and find(b, r"(every|each|all) changed file")
    return bool(ok), evidence(b, r"linter")


def check_counts_in_body(b: str, s: str):
    ok = find(b, r"counts?[^.]{0,140}pull request body")
    return bool(ok), evidence(b, r"counts?[^.]{0,140}pull request body")


def check_justify_findings(b: str, s: str):
    ok = find(b, r"hard finding") and find(b, r"(justif|named and|name it)")
    return bool(ok), evidence(b, r"hard finding")


FALSE_CLAIMS = r"(global directory|not loadable)"


def check_no_false_claim(b: str, s: str):
    match = find(b, FALSE_CLAIMS)
    return match is None, "" if match is None else sentence_at(b, match.start())


def check_true_reason(b: str, s: str):
    return bool(find(b, r"session start|discovered at session start")), evidence(
        b, r"session start"
    )


def check_what_ran(b: str, s: str):
    ok = (
        find(b, r"what you ran") or find(b, r"which evals") or find(b, r"evals you ran")
    )
    return bool(ok), evidence(b, r"(what you ran|which evals|evals you ran)")


def check_five_criteria(b: str, s: str):
    needed = ["context efficiency", "reliability", "description", "script", "style"]
    missing = [word for word in needed if word not in b]
    if missing:
        return False, "missing: " + ", ".join(missing)
    if not find(b, r"for each criterion"):
        return False, "the words appear, but not as the self-review criteria"
    return True, "the self-review names all five"


def check_no_unconditional_skip(b: str, s: str):
    if not find(b, r"run its evals"):
        return False, "the brief never says to run the evals"
    if find(b, r"skip (its )?eval"):
        return False, evidence(b, r"skip (its )?eval")
    return True, evidence(b, r"run its evals")


def check_verdict_agrees(b: str, s: str):
    ok = find(b, r"verdict") and find(b, r"agree")
    return bool(ok), evidence(b, r"verdict")


def check_other_copies(b: str, s: str):
    ok = find(b, r"other cop(y|ies)") or find(b, r"search the repository")
    return bool(ok), evidence(b, r"(other cop(y|ies)|search the repository)")


def check_commit_messages(b: str, s: str):
    return bool(find(b, r"commit message")), evidence(b, r"commit message")


def check_conventions_first(b: str, s: str):
    pattern = r"read the repository's[^.]{0,80}(agents\.md|existing skills)"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_correct_existing(b: str, s: str):
    pattern = r"instead of repeating"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_check_can_fail(b: str, s: str):
    return bool(find(b, r"planted defect")), evidence(b, r"planted defect")


def check_test_command(b: str, s: str):
    return bool(find(b, r"test command")), evidence(b, r"test command")


def check_counts_before_after(b: str, s: str):
    pattern = r"before and after"
    return bool(find(b, pattern) and find(b, r"count")), evidence(b, pattern)


def check_no_new_finding(b: str, s: str):
    pattern = r"add no new finding"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_generic_word(b: str, s: str):
    pattern = r"generic word"
    return bool(find(b, pattern) and find(b, r"trigger")), evidence(b, pattern)


def check_rename_references(b: str, s: str):
    ok = find(b, r"rename") and find(b, r"every one")
    return bool(ok), evidence(b, r"rename")


def check_digest_page(b: str, s: str):
    pattern = r"one page at most"
    return bool(find(b, pattern)), evidence(b, pattern)


CHECKS = {
    (1, 0): (
        "the brief requires the example to be run before it is written",
        check_run_example,
    ),
    (1, 1): (
        "the command and result are recorded in the pull request",
        check_command_and_result,
    ),
    (1, 2): ("a session quote is evidence, not a fact", check_quote_is_evidence),
    (2, 0): ("a tool claim names the version tested", check_version),
    (2, 1): ("a flag or behaviour claim names the subcommand tested", check_subcommand),
    (2, 2): ("a blanket claim is split or dropped", check_no_blanket),
    (3, 0): ("a description sentence stays under 25 words", check_word_cap),
    (3, 1): ("the person's trigger phrases survive", check_trigger_phrases),
    (3, 2): (
        "the description is the only text OpenCode shows",
        check_description_is_only_text,
    ),
    (4, 0): (
        "a mechanical check becomes a script with an exit code",
        check_script_exit_code,
    ),
    (4, 1): ("the script runs in the verification pass", check_script_runs_in_verify),
    (5, 0): ("the linter runs on every changed file", check_linter_on_changes),
    (5, 1): ("the linter counts reach the pull request body", check_counts_in_body),
    (5, 2): (
        "each remaining hard finding is named and justified",
        check_justify_findings,
    ),
    (6, 0): ("the false 'global directory' claim is gone", check_no_false_claim),
    (6, 1): ("the true reason names session start", check_true_reason),
    (6, 2): ("the brief asks what ran and what did not", check_what_ran),
    (6, 3): (
        "the brief never tells the session to skip evals",
        check_no_unconditional_skip,
    ),
    (7, 0): ("the self-review names all five criteria", check_five_criteria),
    (7, 1): ("the verdict must agree with the findings", check_verdict_agrees),
    (8, 0): ("a corrected claim is searched for in other copies", check_other_copies),
    (8, 1): ("commit messages are corrected too", check_commit_messages),
    (9, 0): (
        "the whole description is capped, not only each sentence",
        check_description_budget,
    ),
    (10, 0): (
        "the conventions are read before a rule is written",
        check_conventions_first,
    ),
    (10, 1): ("an existing rule is corrected, not repeated", check_correct_existing),
    (11, 0): ("a check must fail on a planted defect", check_check_can_fail),
    (12, 0): ("the repository's test command runs", check_test_command),
    (13, 0): (
        "the linter counts are compared before and after",
        check_counts_before_after,
    ),
    (13, 1): ("the change adds no new linter finding", check_no_new_finding),
    (14, 0): ("a generic description word is not a trigger", check_generic_word),
    (15, 0): ("a rename updates every reference", check_rename_references),
    (16, 0): ("a digest is capped at one page", check_digest_page),
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
    for number in range(1, 14):
        if f"\n{number}. **" not in text:
            problems.append(f"step {number} is missing")
    for heading in ("# Sessions to read", "# Rules", "# What to do"):
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
