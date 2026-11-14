#!/usr/bin/env python3
"""Grade the learn-from-sessions instructions against the evals in evals.json.

The subject is what an extraction reads: `SKILL.md`, every file under
`references/`, and the `review-agent-instructions` skill this skill links for
the five criteria. The linked file is graded too, because a review criterion
this skill refuses to restate still has to be stated somewhere the reader reads.

These checks are deterministic, so a change to the wording can be measured
before it reaches an extraction. They check that an instruction is present, not
that an extraction obeyed it; a real extraction is the final check.

Usage:
    grade.py            # grade SKILL.md, references/ and the linked criteria
    grade.py --json     # machine-readable result
    grade.py --verbose  # show the matched text for each pass

Exit 0 when every expectation and every structural check passes, 1 when one
fails, 2 on a usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
EVALS = Path(__file__).resolve().parent / "evals.json"
LINKED = SKILL_DIR.parent / "review-agent-instructions" / "SKILL.md"
REFERENCES = SKILL_DIR / "references"
SCRIPT = SKILL_DIR / "scripts" / "sessions"


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


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def read_own() -> str:
    """This skill's own instructions, as one normalised text."""
    parts = [(SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")]
    for path in sorted(REFERENCES.glob("*.md")):
        parts.append(path.read_text(encoding="utf-8"))
    return norm("\n\n".join(parts))


def read_subject() -> str:
    """This skill's instructions plus the skill it links for the criteria."""
    text = read_own()
    if LINKED.is_file():
        text += "\n\n" + norm(LINKED.read_text(encoding="utf-8"))
    return text


# The evals whose lesson this skill deliberately delegates to the linked
# review-agent-instructions skill: the description budget and triggers, and the
# lean body. Every other lesson must be stated here, or a change that deletes it
# from this skill would still pass on the linked copy.
LINKED_EVALS = {3, 9, 14, 16}


# Each check is (eval id, expectation index, description, function). A function
# takes the normalised subject text and returns (passed, evidence).
def check_run_example(b: str):
    run = find(b, r"run (every|each|the) (example|command)")
    then = find(b, r"(before (you )?(write|commit|stage))|(show (its|the) output)")
    return bool(run and then), evidence(b, r"run (every|each|the) (example|command)")


def check_command_and_result(b: str):
    ok = find(b, r"commands?[^.]{0,200}(result|output)") and find(
        b, r"extraction report"
    )
    return bool(ok), evidence(b, r"commands?[^.]{0,200}(result|output)")


def check_quote_is_evidence(b: str):
    ok = find(b, r"quote[s]?[^.]{0,80}evidence") and find(
        b, r"(not a fact|not fact|rather than a fact)"
    )
    return bool(ok), evidence(b, r"quote[s]?[^.]{0,80}evidence")


def check_version(b: str):
    ok = find(b, r"(name|record|state|give)[^.]{0,60}version") or find(
        b, r"version[^.]{0,60}(tested|you tested)"
    )
    return bool(ok), evidence(b, r"version")


def check_subcommand(b: str):
    return bool(find(b, r"sub-?command")), evidence(b, r"sub-?command")


def check_no_blanket(b: str):
    ok = find(b, r"blanket") and find(b, r"(split|drop|per sub-?command)")
    return bool(ok), evidence(b, r"blanket")


def check_word_cap(b: str):
    ok = find(b, r"(under|below|at most|fewer than) (twenty-five|25) words") or find(
        b, r"sentence (under|below|at most|fewer than) (twenty-five|25)"
    )
    return bool(ok), evidence(
        b, r"(twenty-five|25) words?|sentence under (twenty-five|25)"
    )


def check_trigger_phrases(b: str):
    ok = find(b, r"trigger phrase") and find(
        b, r"(keep|preserve|verbatim|survive|unchanged)"
    )
    return bool(ok), evidence(b, r"trigger phrase")


def check_description_budget(b: str):
    pattern = r"(under|below|at most|fewer than) (sixty|60) words"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_description_is_only_text(b: str):
    pattern = r"description[^.]{0,180}(injected|only text|only thing|before it loads)"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_script_exit_code(b: str):
    ok = all(
        find(b, p)
        for p in (
            r"script",
            r"exit (code|status)",
            r"(mechanical|banned.word|grep|header|collision|file list)",
        )
    )
    return bool(ok), evidence(b, r"exit (code|status)")


def check_script_runs_with_checks(b: str):
    return bool(find(b, r"with the other checks")), evidence(
        b, r"with the other checks"
    )


def check_linter_on_changes(b: str):
    ok = find(b, r"linter") and find(b, r"(every|each|all) changed file")
    return bool(ok), evidence(b, r"linter")


def check_counts_in_report(b: str):
    ok = find(b, r"counts?[^.]{0,140}extraction report")
    return bool(ok), evidence(b, r"counts?[^.]{0,140}extraction report")


def check_justify_findings(b: str):
    ok = find(b, r"hard finding") and find(b, r"(justif|named and|name it)")
    return bool(ok), evidence(b, r"hard finding")


FALSE_CLAIMS = r"(global directory|not loadable)"


def check_no_false_claim(b: str):
    match = find(b, FALSE_CLAIMS)
    return match is None, "" if match is None else sentence_at(b, match.start())


def check_true_reason(b: str):
    return bool(find(b, r"session start|discovered at session start")), evidence(
        b, r"session start"
    )


def check_what_ran(b: str):
    ok = (
        find(b, r"what you ran") or find(b, r"which evals") or find(b, r"evals you ran")
    )
    return bool(ok), evidence(b, r"(what you ran|which evals|evals you ran)")


def check_five_criteria(b: str):
    needed = ["context efficiency", "reliability", "description", "script", "style"]
    missing = [word for word in needed if word not in b]
    if missing:
        return False, "missing: " + ", ".join(missing)
    if not find(b, r"for each criterion"):
        return False, "the words appear, but not as the self-review criteria"
    return True, "the self-review names all five"


def check_no_unconditional_skip(b: str):
    if not find(b, r"run its evals"):
        return False, "the instructions never say to run the evals"
    if find(b, r"skip (its )?eval"):
        return False, evidence(b, r"skip (its )?eval")
    return True, evidence(b, r"run its evals")


def check_verdict_agrees(b: str):
    ok = find(b, r"verdict") and find(b, r"agree")
    return bool(ok), evidence(b, r"verdict")


def check_other_copies(b: str):
    ok = find(b, r"other cop(y|ies)") or find(b, r"search the repository")
    return bool(ok), evidence(b, r"(other cop(y|ies)|search the repository)")


def check_commit_messages(b: str):
    return bool(find(b, r"commit message")), evidence(b, r"commit message")


def check_conventions_first(b: str):
    pattern = r"read the repository's[^.]{0,80}(agents\.md|existing skills)"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_correct_existing(b: str):
    pattern = r"instead of repeating"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_check_can_fail(b: str):
    return bool(find(b, r"planted defect")), evidence(b, r"planted defect")


def check_test_command(b: str):
    return bool(find(b, r"test command")), evidence(b, r"test command")


def check_counts_before_after(b: str):
    pattern = r"before and after"
    return bool(find(b, pattern) and find(b, r"count")), evidence(b, pattern)


def check_no_new_finding(b: str):
    pattern = r"add no new finding"
    return bool(find(b, pattern)), evidence(b, pattern)


def check_generic_word(b: str):
    pattern = r"generic word"
    return bool(find(b, pattern) and find(b, r"trigger")), evidence(b, pattern)


def check_rename_references(b: str):
    ok = find(b, r"rename") and find(b, r"every one")
    return bool(ok), evidence(b, r"rename")


def check_skill_body_lean(b: str):
    ok = find(b, r"body loads on every trigger") and find(
        b, r"(needs|needed)[^.]{0,40}(on every trigger|then)"
    )
    return bool(ok), evidence(b, r"body loads on every trigger")


def check_references(b: str):
    return bool(find(b, r"references/")), evidence(b, r"references/")


def check_stages_only(b: str):
    ok = find(b, r"stage") and find(b, r"commit(s)? nothing|never commit")
    return bool(ok), evidence(b, r"commit(s)? nothing|never commit")


def check_concern_map(b: str):
    ok = find(b, r"concern map") and find(b, r"commit")
    return bool(ok), evidence(b, r"concern map")


def check_branch_is_callers(b: str):
    ok = find(b, r"caller's") and find(b, r"never (create|switch)")
    return bool(ok), evidence(b, r"never (create|switch)")


def check_concern_map_message(b: str):
    ok = find(b, r"concern map") and find(b, r"commit message")
    return bool(ok), evidence(b, r"commit message")


def check_checked_section(b: str):
    return bool(find(b, r"checked section")), evidence(b, r"checked section")


def check_report_sessions(b: str):
    ok = find(b, r"sessions you read")
    return bool(ok), evidence(b, r"sessions you read")


def check_report_verdict(b: str):
    return bool(find(b, r"verdict")), evidence(b, r"verdict")


CHECKS = {
    (1, 0): ("every example is run before it is written", check_run_example),
    (1, 1): (
        "the command and result are recorded in the extraction report",
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
    (4, 1): ("the script runs with the other checks", check_script_runs_with_checks),
    (5, 0): ("the linter runs on every changed file", check_linter_on_changes),
    (5, 1): ("the linter counts reach the extraction report", check_counts_in_report),
    (5, 2): (
        "each remaining hard finding is named and justified",
        check_justify_findings,
    ),
    (6, 0): ("the false 'global directory' claim is gone", check_no_false_claim),
    (6, 1): ("the true reason names session start", check_true_reason),
    (6, 2): ("the run says which evals it ran", check_what_ran),
    (6, 3): (
        "the instructions never tell the session to skip evals",
        check_no_unconditional_skip,
    ),
    (7, 0): ("the self-review names all five criteria", check_five_criteria),
    (7, 1): ("the verdict must agree with the findings", check_verdict_agrees),
    (8, 0): ("a corrected claim is searched for in other copies", check_other_copies),
    (8, 1): (
        "a repeating commit message is named for the caller",
        check_commit_messages,
    ),
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
    (16, 0): (
        "the skill body holds only what every trigger needs",
        check_skill_body_lean,
    ),
    (16, 1): ("long reference material moves into references/", check_references),
    (17, 0): ("the extraction stages and commits nothing", check_stages_only),
    (17, 1): ("the extraction records the concern map", check_concern_map),
    (17, 2): ("the branch stays the caller's", check_branch_is_callers),
    (18, 0): ("the concern map carries a commit message", check_concern_map_message),
    (18, 1): ("the report holds a Checked section", check_checked_section),
    (18, 2): ("the report names the sessions read and not read", check_report_sessions),
    (18, 3): ("the report holds the verdict", check_report_verdict),
}


def structure_problems() -> list[str]:
    """The failures a text match cannot see."""
    problems = []
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    fields = frontmatter(skill)
    if fields.get("name") != SKILL_DIR.name:
        problems.append(
            f"the frontmatter name {fields.get('name')!r} is not {SKILL_DIR.name!r}"
        )
    description = fields.get("description", "")
    if not description:
        problems.append("the frontmatter has no description")
    else:
        if len(description.split()) > 60:
            problems.append(
                f"the description is {len(description.split())} words, over 60"
            )
        for sentence in re.split(r"(?<=[.!?])\s+", description):
            if len(sentence.split()) > 25:
                problems.append(f"a description sentence is over 25 words: {sentence}")
    if "{{" in skill or "}}" in skill:
        problems.append("an unfilled placeholder remains")
    for name in ("digest.md", "claims.md"):
        if not (REFERENCES / name).is_file():
            problems.append(f"references/{name} is missing")
    if not SCRIPT.is_file():
        problems.append("scripts/sessions is missing")
    elif not SCRIPT.stat().st_mode & 0o111:
        problems.append("scripts/sessions is not executable")
    if not LINKED.is_file():
        problems.append(
            f"the linked criteria file {LINKED} is missing; the five criteria "
            "cannot be graded"
        )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Grade the learn-from-sessions instructions."
    )
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--verbose", action="store_true", help="show matched text")
    args = parser.parse_args()

    for path in (SKILL_DIR / "SKILL.md", EVALS):
        if not path.is_file():
            print(f"grade: {path} is missing", file=sys.stderr)
            return 2

    own = read_own()
    subject = read_subject()
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
            checked = subject if case["id"] in LINKED_EVALS else own
            ok, why = entry[1](checked)
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

    structure = structure_problems()

    if args.json:
        print(
            json.dumps(
                {
                    "passed": passed,
                    "counted": counted,
                    "unmapped": unmapped,
                    "rate": round(passed / counted, 3) if counted else 0,
                    "structure": structure,
                    "results": results,
                },
                indent=2,
            )
        )
    else:
        print(
            f"learn-from-sessions evals: {passed}/{counted} expectations pass "
            f"({round(100 * passed / counted) if counted else 0}%)"
        )
        if unmapped:
            print(f"{unmapped} expectation(s) have no check; add one to CHECKS.")
        for problem in structure:
            print(f"structure: {problem}")
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

    return 0 if counted and not unmapped and not structure and passed == counted else 1


if __name__ == "__main__":
    sys.exit(main())
