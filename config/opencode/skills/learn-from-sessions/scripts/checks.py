#!/usr/bin/env python3
"""The mechanical checks `learn-from-sessions` states as prose rules.

`SKILL.md` states rules a person can check without judgement: where a change may
land, what the extraction report must hold, that no credential is written, that
no new skill is hidden by an ignore rule, and that every session is accounted
for. Prose is enough to state such a rule and not enough to enforce it. This
module holds each one as a function so the runtime CLI and the evaluation gates
run the same code.

`scripts/check-extraction` runs these over a checkout and its extraction report.
`evals/gates.py` runs the same functions over a collected run directory, where
the checkout sits under `<run>/checkout` and the report under
`<run>/state/extraction.md`. A rule that changes here changes both verdicts.
`check_claims` is the exception: only the runtime CLI runs it, because the
evaluation's gates are the record of runs that were graded before it existed.

Each check returns `(passed, detail, findings)`. `detail` is one line that names
the outcome; `findings` is one line per defect. A check that cannot read its
input fails rather than passing, so a broken checkout is never reported ready.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

# The person's ruling of 2026-11-14: `.kb/` is documentation, so it is in scope.
# The pinned skill prohibits application source, configuration and dependency,
# and these paths are none of the three. `docs/` and `tests/` are not on the
# list: documentation belongs under `.kb/`, and a test file is application code.
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

# The sections the skill's extraction-report list requires. Each pattern proves
# the report holds the section or the fact; whether the content is any good is
# the review's question. A heading is not required: a report may name the
# section inside another one and still hold what the next step reads.
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

REPORT_DISPLAY = "state/extraction.md"

# A citation asserts a fact about the checkout, and the report makes two kinds of
# claim with one: that a path exists, and that a line holds something. Both are
# settled by the tree, so both are checked. The form is deliberately narrow: a
# repository path with an extension, or one of the two root files the skill
# writes. A bare filename, a session id and a digest name are not claims about
# the tree.
CITATION = re.compile(r"`([^`\n]+)`")
CITATION_PATH = re.compile(
    r"^(?P<path>(?:\./)?(?:[A-Za-z0-9._@+-]+/)+[A-Za-z0-9._@+-]+"
    r"\.(?:md|py|sh|json|toml|ya?ml|txt)|AGENTS\.md|GLOSSARY\.md)"
    r"(?::(?P<start>\d+)(?:-(?P<end>\d+))?)?$"
)

# The run's own artefacts sit beside the checkout, not in it. An absolute path
# points outside the repository by definition. A placeholder is not a path.
CITATION_EXEMPT_PREFIXES = ("state/", "transcripts/", "digests/")
PLACEHOLDER = re.compile(r"[<>{}]")

# A sentence that marks a path as added, absent or a test input is not claiming
# the checkout holds it. The marker is read from the citation's own line and its
# neighbours, because a report wraps a sentence and states the absence on the
# next line as often as the same one.
WINDOW_MARKERS = re.compile(
    r"(?i)\b(add|adds|added|create|creates|created|propose[sd]?|target|"
    r"absent|missing|planted|does not exist|no such|"
    r"not in (this|the) checkout|neither file|hindsight|earlier extraction|"
    r"bare remote|second clone|throwaway|scratch|/tmp/)\b|"
    r"\b(?:the same (?:directory|file)|as above|the previous)\b"
)

# A path a check script was pointed at as a fixture is not a citation. These are
# the shapes a planted defect takes, in this repository and in the graded runs.
TEST_INPUT = re.compile(
    r"(?i)(?:^|/)(?:no/such|nonexistent|not-found|bogus|fake|example)/"
)

# A report writes a skill as `<id>/SKILL.md` as often as by its full path, and
# it cites global skills the checkout does not own. Both resolve before a
# citation is called false.
GLOBAL_SKILL_ROOTS = (
    Path.home() / ".config/opencode/skills",
    Path.home() / ".agents/skills",
)

# A command that needs a remote, and the ways a command names one instead. The
# second half matters: a session may run `gh pr list --repo owner/name` in a
# checkout with no remote, and that is a real run.
REMOTE_COMMAND = re.compile(
    r"^\s*(?:gh\s+(?:pr|issue|repo|api)|git\s+(?:push|fetch|pull|ls-remote))\b"
)
REMOTE_EXEMPT = re.compile(r"--repo\b|repos/|://")


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """One git call in `repo`, with its output captured as text."""
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        errors="replace",
    )


def changed_paths(repo: Path) -> list[tuple[str, str]]:
    """Every changed, staged or untracked path, with its status codes."""
    result = git(repo, "status", "--porcelain=v1", "-uall", "-z")
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


def check_write_scope(repo: Path) -> tuple[bool, str, list[str]]:
    """Every changed path is inside the allowlist the person ruled on.

    Application code, configuration and dependencies are out of scope whatever
    the lesson, so a run that edits them changed more than the extraction.
    """
    outside = []
    for status, path in changed_paths(repo):
        if path in ALLOWED_FILES or path.startswith(ALLOWED_PREFIXES):
            continue
        outside.append(f"{path} ({status.strip()}): outside the allowlist")
    if outside:
        return False, f"{len(outside)} path(s) outside the allowlist", outside
    return True, "every changed path is in the allowlist", []


def check_report(
    report: Path, display: str = REPORT_DISPLAY
) -> tuple[bool, str, list[str]]:
    """The extraction report exists and holds every section the skill requires.

    The report is the one thing the steps after the extraction read. A missing
    section is a fact about the file, not a judgement about its content.
    """
    if not report.is_file():
        return False, f"{display} is missing", []
    text = report.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return False, f"{display} is empty", []
    missing = [name for name, pattern in SECTIONS if not re.search(pattern, text)]
    if missing:
        return (
            False,
            "missing section(s): " + ", ".join(missing),
            [f"missing: {name}" for name in missing],
        )
    return True, f"all {len(SECTIONS)} required sections are present", []


def written_text(
    repo: Path, report: Path, display: str = REPORT_DISPLAY
) -> list[tuple[str, str]]:
    """The text an extraction wrote: the report, and the new content of `repo`.

    The pinned skill is skipped because the harness copies it in; scanning it
    would report the harness's own text as the run's output.
    """
    written = []
    if report.is_file():
        written.append(
            (
                display,
                report.read_text(encoding="utf-8", errors="replace"),
            )
        )
    if not repo.is_dir():
        return written
    diff = git(repo, "diff", "HEAD", "--unified=0")
    added = [
        line[1:]
        for line in diff.stdout.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    written.append(("the checkout diff", "\n".join(added)))
    for _, path in changed_paths(repo):
        if path.startswith(PINNED_SKILL_PREFIX):
            continue
        target = repo / path
        if target.is_file():
            try:
                written.append((path, target.read_text(encoding="utf-8")))
            except UnicodeDecodeError:
                continue
    return written


def check_secrets(
    repo: Path, report: Path, display: str = REPORT_DISPLAY
) -> tuple[bool, str, list[str]]:
    """No credential, token or private path appears in anything written.

    A transcript quotes a person who may paste a token. The report and the files
    travel to a pull request, so a secret in either leaves the machine.
    """
    findings = []
    for where, text in written_text(repo, report, display):
        for line_number, line in enumerate(text.splitlines(), 1):
            for name, pattern in SECRETS:
                if pattern.search(line):
                    findings.append(
                        f"{where}:{line_number}: {name}: {line.strip()[:120]}"
                    )
    if findings:
        return False, f"{len(findings)} possible secret or private path", findings
    return True, "no credential, token or private path found", []


def skill_files(repo: Path) -> list[str]:
    """Every skill this extraction wrote, including one an ignore rule hides."""
    skills = []
    for path in sorted(repo.glob(".opencode/skills/*/SKILL.md")):
        relative = path.relative_to(repo).as_posix()
        at_head = subprocess.run(
            ["git", "-C", str(repo), "show", f"HEAD:{relative}"],
            capture_output=True,
        )
        if at_head.returncode != 0 or at_head.stdout != path.read_bytes():
            skills.append(relative)
    return skills


def check_not_ignored(repo: Path) -> tuple[bool, str, list[str]]:
    """For every skill written, `git check-ignore -q <path>` exits 1.

    A skill a `.gitignore` rule hides is a skill no later session loads, however
    well it is written. The check asks git, so the repository's whole rule set
    applies rather than a restatement of it.
    """
    ignored = []
    for path in skill_files(repo):
        if git(repo, "check-ignore", "-q", "--", path).returncode == 0:
            ignored.append(f"{path}: silently ignored by a .gitignore rule")
    if ignored:
        return False, f"{len(ignored)} written skill(s) are ignored", ignored
    return True, "every written skill is tracked, not ignored", []


def digest_ids(digests: Path) -> list[str]:
    """The session IDs a digests directory names, one `ses_*.md` file each."""
    return sorted(path.stem for path in digests.glob("ses_*.md"))


def check_sessions(
    report: Path, ids: list[str], display: str = REPORT_DISPLAY
) -> tuple[bool, str, list[str]]:
    """The run names the sessions it read and the ones it did not.

    The report may shorten an ID to its first 14 characters when it cites a
    digest inline. The sessions section names the full id.
    """
    if not report.is_file():
        return False, f"{display} is missing", []
    text = report.read_text(encoding="utf-8", errors="replace")
    missing = [session for session in ids if session[:14] not in text]
    problems = [f"session not named in the report: {session}" for session in missing]
    if not re.search(NOT_READ, text):
        problems.append(
            "the report does not say which sessions it did not read (or that none was skipped)"
        )
    if problems:
        return False, f"{len(problems)} session-accounting problem(s)", problems
    return True, f"all {len(ids)} sessions are accounted for", []


def check_sessions_against_digests(
    report: Path, digests: Path, display: str = REPORT_DISPLAY
) -> tuple[bool, str, list[str]]:
    """Session accounting with the IDs taken from a digests directory.

    The evaluation reads its frozen bundle; a live extraction has its own
    digests, one per session it read. No digest means nothing to account for,
    which is a failure rather than a pass.
    """
    if not digests.is_dir():
        return False, f"the digests directory {digests} is missing", []
    ids = digest_ids(digests)
    if not ids:
        return False, f"the digests directory {digests} holds no ses_*.md digest", []
    return check_sessions(report, ids, display)


def citation_is_checkable(path: str) -> bool:
    """Whether a cited path is a claim about this checkout at all."""
    if path.startswith(("/", "~")):
        return False
    if path.startswith(CITATION_EXEMPT_PREFIXES):
        return False
    return PLACEHOLDER.search(path) is None


def resolve_citation(repo: Path, path: str) -> Path | None:
    """The file a citation names, or None when nothing holds it.

    A report names a skill as `<id>/SKILL.md` as often as by its full path, and
    it cites global skills the checkout does not own. Both are real files, so
    both resolve before a citation is called false.
    """
    direct = repo / path
    if direct.is_file():
        return direct
    if path.endswith("/SKILL.md") and path.count("/") == 1:
        for root in (repo / ".opencode/skills", *GLOBAL_SKILL_ROOTS):
            candidate = root / path
            if candidate.is_file():
                return candidate
    return None


def context(lines: list[str], index: int) -> str:
    """The cited line and its neighbours, joined, for marker and attribution."""
    return " ".join(lines[max(0, index - 1) : index + 2])


def names_external_skill(repo: Path, window: str) -> bool:
    """Whether the sentence attributes its paths to a skill this checkout lacks.

    A report that says `scripts/measure.py` while naming
    `review-agent-instructions` is citing another skill's script, not claiming
    the checkout holds it. The attribution is checkable: the named skill exists
    globally and not in the checkout.
    """
    for token in CITATION.findall(window):
        token = token.strip()
        if re.fullmatch(r"[a-z0-9][a-z0-9-]*", token) is None:
            continue
        if (repo / ".opencode/skills" / token).is_dir():
            continue
        if any((root / token).is_dir() for root in GLOBAL_SKILL_ROOTS):
            return True
    # A report names the owner in prose as often as in backticks, as in
    # "`scripts/measure.py` (review-agent-instructions)". A bare word counts
    # only when it is the name of a skill the checkout does not hold.
    for word in re.findall(r"[a-z0-9][a-z0-9-]{3,}", window):
        if (repo / ".opencode/skills" / word).is_dir():
            continue
        if any((root / word).is_dir() for root in GLOBAL_SKILL_ROOTS):
            return True
    return False


def check_claims(
    repo: Path, report: Path, display: str = REPORT_DISPLAY
) -> tuple[bool, str, list[str]]:
    """Every repository citation in the report resolves in the checkout.

    A report that cites a file the checkout does not hold, or a line past the
    end of one, sends the next reader to trust a measurement that did not
    happen. The check reads the report only: it does not decide whether the
    measurement was honest, it decides whether the place it names exists.
    """
    if not report.is_file():
        return False, f"{display} is missing", []
    lines = report.read_text(encoding="utf-8", errors="replace").splitlines()
    findings: list[str] = []
    seen: set[tuple[str, str | None, str | None]] = set()

    for index, line in enumerate(lines):
        window = context(lines, index)
        for citation in CITATION.findall(line):
            match = CITATION_PATH.match(citation.strip())
            if match is None:
                continue
            path = match.group("path")
            if path.startswith("./"):
                path = path[2:]
            if not citation_is_checkable(path):
                continue
            if TEST_INPUT.search(path):
                continue
            if WINDOW_MARKERS.search(window) or names_external_skill(repo, window):
                continue
            key = (path, match.group("start"), match.group("end"))
            if key in seen:
                continue
            seen.add(key)

            target = resolve_citation(repo, path)
            if target is None:
                findings.append(
                    f"{display}:{index + 1}: cites `{citation.strip()}`, "
                    f"which is not in the checkout"
                )
                continue
            if match.group("start"):
                last = int(match.group("end") or match.group("start"))
                count = len(
                    target.read_text(encoding="utf-8", errors="replace").splitlines()
                )
                if last > count:
                    findings.append(
                        f"{display}:{index + 1}: cites `{citation.strip()}`, "
                        f"but {path} has {count} line(s)"
                    )

    findings.extend(remote_claims(repo, lines, display))
    if findings:
        return (
            False,
            f"{len(findings)} citation(s) the checkout does not support",
            findings,
        )
    return True, "every repository citation resolves in the checkout", []


def check_completeness(
    report: Path, display: str = REPORT_DISPLAY
) -> tuple[bool, str, list[str]]:
    """The report records what the completeness pass found.

    The pass is a second read of the digests against the report, and the report
    is where its account belongs. A missing record is a fact about the file;
    whether the pass was any good is the review's question.
    """
    if not report.is_file():
        return False, f"{display} is missing", []
    text = report.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"(?i)\bcompleteness\b", text):
        return (
            False,
            "the report does not record the completeness pass",
            ["missing: the completeness pass and what it found"],
        )
    return True, "the completeness pass is recorded", []


def remote_claims(
    repo: Path, lines: list[str], display: str = REPORT_DISPLAY
) -> list[str]:
    """Checked rows that record a command this checkout cannot have run.

    A repository with no remote cannot list or edit a pull request, so a row
    that records one as accepted was measured somewhere else. A command that
    names its repository is exempt, and so is a row that says it ran against a
    scratch or bare remote: that is a run, just not against this checkout.
    """
    if git(repo, "remote", "-v").stdout.strip():
        return []
    findings: list[str] = []
    in_checked = False
    for index, line in enumerate(lines):
        if re.match(r"(?i)^#{1,6}\s+checked\b", line):
            in_checked = True
            continue
        if in_checked and re.match(r"^#{1,6}\s", line):
            in_checked = False
        if not in_checked or not line.lstrip().startswith("|"):
            continue
        if WINDOW_MARKERS.search(context(lines, index)):
            continue
        for command in CITATION.findall(line):
            command = command.strip()
            if not REMOTE_COMMAND.match(command) or REMOTE_EXEMPT.search(command):
                continue
            findings.append(
                f"{display}:{index + 1}: the Checked section records `{command}`, "
                f"which needs a git remote, and this checkout has none"
            )
    return findings
