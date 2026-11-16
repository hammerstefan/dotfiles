#!/usr/bin/env python3
"""Plan, render and spawn hwt worktree sessions for tracker issues.

Verbs:
  plan    preflight each issue, derive its branch, and find the files and host
          commands it shares with the others
  render  render one brief and one goal per issue from a plan and per-issue notes
  spawn   dry-run hwt, check what it printed, inject the checkout path, spawn

The plan is the single source of truth for every rendered brief, so the shared
blocks (sibling table, host rules, autonomy) cannot drift between briefs.

Exit codes: 0 ok, 1 refused or failed, 2 bad usage.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ARTICLES = {
    "a",
    "an",
    "and",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}
LEADING_VERBS = {
    "add",
    "apply",
    "audit",
    "build",
    "choose",
    "close",
    "conclude",
    "create",
    "cut",
    "debug",
    "decide",
    "define",
    "document",
    "drop",
    "extract",
    "fix",
    "grill",
    "implement",
    "investigate",
    "keep",
    "land",
    "make",
    "measure",
    "move",
    "provision",
    "record",
    "refresh",
    "remove",
    "rename",
    "replace",
    "resolve",
    "retire",
    "run",
    "split",
    "state",
    "stop",
    "teach",
    "test",
    "update",
    "verify",
    "write",
}
HOST_PREFIXES = (
    "just ",
    "lxc ",
    "docker ",
    "systemctl ",
    "workshop ",
    "gh ",
    "uv run ",
    "scripts/",
    "monitor-agent",
    "make ",
    "npm ",
    "bun ",
    "pytest ",
    "terraform ",
    "kubectl ",
)
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
REFERENCE_RE = re.compile(r"#(\d{1,5})\b")
REQUIRED_SECTIONS = ("Why", "What to do", "Done when", "Goal")
SECTION_RE = re.compile(r"^## +(.+?)\s*$", re.MULTILINE)


def fail(message: str, code: int = 1) -> "NoReturn":  # type: ignore[name-defined]
    print(f"hwt-implement: {message}", file=sys.stderr)
    raise SystemExit(code)


class Refusal(Exception):
    """One issue cannot be spawned; the run records it and continues."""


def run(
    argv: list[str], cwd: str | None = None, check: bool = False
) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            argv, cwd=cwd, capture_output=True, text=True, check=False
        )
    except OSError as exc:
        fail(f"cannot run {argv[0]}: {exc}")
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        fail(f"{' '.join(argv[:3])} failed: {detail}")
    return result


def git(repo: str, *args: str, check: bool = False) -> subprocess.CompletedProcess:
    return run(["git", "-C", repo, *args], check=check)


def repo_root(path: str) -> str:
    result = git(path, "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        fail(f"not a git repository: {path}")
    return result.stdout.strip()


def default_branch(repo: str) -> str:
    result = git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip().split("/", 1)[-1]
    return "main"


def choose_base(repo: str, explicit: str | None) -> tuple[str, str]:
    if explicit:
        return explicit, "passed with --base"
    current = git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    branch = default_branch(repo)
    if current in (branch, f"origin/{branch}"):
        return "HEAD", f"the checkout is on {branch}"
    return (
        f"origin/{branch}",
        f"the checkout is on {current}, which is not {branch}; "
        f"basing on origin/{branch} keeps unrelated commits out of the pull request",
    )


def gh_json(argv: list[str]) -> dict:
    result = run(["gh", *argv])
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        fail(f"gh {' '.join(argv[:2])} failed: {detail}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        fail(f"gh returned no JSON: {exc}")
    return {}


def issue_facts(number: int) -> dict:
    facts = gh_json(
        [
            "issue",
            "view",
            str(number),
            "--json",
            "number,title,state,labels,assignees,body,url",
        ]
    )
    facts["labels"] = [label["name"] for label in facts.get("labels", [])]
    facts["assignees"] = [who["login"] for who in facts.get("assignees", [])]
    return facts


def issue_graph(number: int) -> tuple[int, list[dict]]:
    """Return the child count and the open blockers of one issue."""
    repository = gh_json(["repo", "view", "--json", "owner,name"])
    owner = repository["owner"]["login"]
    name = repository["name"]
    query = f"""
query {{
  repository(owner: "{owner}", name: "{name}") {{
    issue(number: {number}) {{
      subIssues(first: 100) {{ totalCount }}
      blockedBy(first: 20) {{ nodes {{ number title state }} }}
    }}
  }}
}}
"""
    result = run(["gh", "api", "graphql", "-f", f"query={query}"])
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        fail(f"gh api graphql failed for #{number}: {detail}")
    node = json.loads(result.stdout)["data"]["repository"]["issue"]
    open_blockers = [
        {"number": item["number"], "title": item["title"]}
        for item in node["blockedBy"]["nodes"]
        if item["state"] == "OPEN"
    ]
    return node["subIssues"]["totalCount"], open_blockers


def slug_for(title: str) -> str:
    words = re.sub(r"[^a-z0-9 ]+", " ", title.lower()).split()
    if words and words[0] in LEADING_VERBS | {"re", "pre", "non"}:
        words = words[1:]
    kept = [word for word in words if word not in ARTICLES]
    return "-".join(kept[:4]) or "issue"


def space_name_for(number: int, slug: str) -> str:
    """The Herdr space's name: the issue number, then the slug's first three words."""
    return f"#{number} " + "-".join(slug.split("-")[:3])


def prefix_for(labels: set[str], override: str | None) -> str:
    if override:
        return override
    if labels & {"bug", "defect", "fix"}:
        return "fix"
    if labels & {"documentation", "docs"}:
        return "docs"
    return "feat"


def claims_of(body: str, repo: str) -> list[str]:
    """Backticked repository paths, with or without an extension.

    A path claim is a backticked token that holds a slash and no space, and is
    either an existing directory in the repository or has a file extension. That
    keeps real paths such as ``agent/.workshop/hermes/hooks/setup-base`` and drops
    a branch name or a snap channel that happens to hold a slash. Absolute
    paths, URLs, flags and host commands name the host, not a file this ticket
    owns.
    """
    found = set()
    for token in BACKTICK_RE.findall(body):
        candidate = token.strip()
        if candidate.startswith("./"):
            candidate = candidate[2:]
        if (
            " " in candidate
            or "://" in candidate
            or "/" not in candidate
            or candidate.startswith(("-", "~", "/"))
            or candidate.endswith("/")
            or candidate.startswith(HOST_PREFIXES)
        ):
            continue
        if not re.match(r"^[A-Za-z0-9_.][A-Za-z0-9_./-]*$", candidate):
            continue
        first = candidate.split("/", 1)[0]
        has_extension = "." in candidate.rsplit("/", 1)[-1]
        if has_extension or (Path(repo) / first).exists():
            found.add(candidate)
    return sorted(found)


def host_commands_of(body: str) -> list[str]:
    found = set()
    for token in BACKTICK_RE.findall(body):
        stripped = token.strip()
        for prefix in HOST_PREFIXES:
            if stripped.startswith(prefix):
                found.add(stripped)
                break
    return sorted(found)


def branch_state(repo: str, branch: str) -> tuple[bool, str]:
    exists = (
        git(repo, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}").returncode
        == 0
    )
    worktree = ""
    listing = git(repo, "worktree", "list", "--porcelain").stdout
    for block in listing.split("\n\n"):
        if f"branch refs/heads/{branch}" in block:
            for line in block.splitlines():
                if line.startswith("worktree "):
                    worktree = line.split(" ", 1)[1]
    return exists, worktree


def verb_plan(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo or ".")
    base, base_reason = choose_base(repo, args.base)
    issues = []
    for number in args.issues:
        facts = issue_facts(number)
        children, open_blockers = issue_graph(number)
        labels = set(facts["labels"])
        slug = slug_for(facts["title"])
        space_name = space_name_for(facts["number"], slug)
        branch = f"{prefix_for(labels, args.prefix)}/{slug}"
        exists, worktree = branch_state(repo, branch)
        issues.append(
            {
                "number": facts["number"],
                "title": facts["title"],
                "url": facts["url"],
                "state": facts["state"],
                "labels": sorted(labels),
                "assignees": facts["assignees"],
                "children": children,
                "open_blockers": open_blockers,
                "slug": slug,
                "space_name": space_name,
                "branch": branch,
                "branch_exists": exists,
                "worktree": worktree,
                "claims": claims_of(facts.get("body", ""), repo),
                "host_commands": host_commands_of(facts.get("body", "")),
                "references": sorted(
                    {int(ref) for ref in REFERENCE_RE.findall(facts.get("body", ""))}
                    - {facts["number"]}
                ),
            }
        )

    own = {issue["number"] for issue in issues}
    claim_map: dict[str, set[int]] = {}
    command_map: dict[str, set[int]] = {}
    for issue in issues:
        for path in issue["claims"]:
            claim_map.setdefault(path, set()).add(issue["number"])
        for command in issue["host_commands"]:
            command_map.setdefault(command, set()).add(issue["number"])

    plan = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo": repo,
        "base": base,
        "base_reason": base_reason,
        "issues": issues,
        "overlaps": [
            {"path": path, "issues": sorted(owners)}
            for path, owners in sorted(claim_map.items())
            if len(owners) > 1
        ],
        "shared_host_commands": [
            {"command": command, "issues": sorted(owners)}
            for command, owners in sorted(command_map.items())
            if len(owners) > 1
        ],
        "cross_references": [
            {
                "issue": issue["number"],
                "names": [ref for ref in issue["references"] if ref in own],
            }
            for issue in issues
            if [ref for ref in issue["references"] if ref in own]
        ],
    }

    if args.json:
        json_path = Path(args.json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(plan, indent=2) + "\n")

    print(f"hwt-implement: {repo}  base {base} ({base_reason})")
    for issue in issues:
        flags = []
        if issue["state"] != "OPEN":
            flags.append(issue["state"].lower())
        if issue["assignees"]:
            flags.append("claimed by " + ",".join(issue["assignees"]))
        if issue["branch_exists"]:
            flags.append("branch exists")
        if issue["worktree"]:
            flags.append(f"checked out at {issue['worktree']}")
        blocker_text = ", ".join(
            f"#{blocker['number']} {blocker['title']}"
            for blocker in issue["open_blockers"]
        )
        print(
            f"#{issue['number']:<5} {issue['branch']:<44} "
            f"children={issue['children']} "
            f"blocked_by={blocker_text or '-'}"
            + (f"  [{'; '.join(flags)}]" if flags else "")
        )
        print(f"       {issue['title']}")
        if issue["claims"]:
            print(f"       files: {', '.join(issue['claims'])}")
        if issue["host_commands"]:
            print(f"       host:  {', '.join(issue['host_commands'])}")
    if plan["overlaps"]:
        print("contested files (two sessions would edit them):")
        for overlap in plan["overlaps"]:
            print(
                f"  {overlap['path']} <- "
                + ", ".join(f"#{number}" for number in overlap["issues"])
            )
    if plan["shared_host_commands"]:
        print("shared host commands (serialize these):")
        for shared in plan["shared_host_commands"]:
            print(
                f"  {shared['command']} <- "
                + ", ".join(f"#{number}" for number in shared["issues"])
            )
    return 0


def parse_notes(path: Path, slug: str) -> dict[str, str]:
    if not path.is_file():
        fail(f"no notes for {slug}: {path} is missing")
    text = path.read_text()
    sections: dict[str, str] = {}
    matches = list(SECTION_RE.finditer(text))
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1).strip().lower()] = text[start:end].strip()
    missing = [name for name in REQUIRED_SECTIONS if name.lower() not in sections]
    if missing:
        fail(
            f"{path} is missing sections: {', '.join('## ' + name for name in missing)}"
        )
    return sections


def sibling_table(issues: list[dict], current: int, order: dict[int, int]) -> str:
    others = [issue for issue in issues if issue["number"] != current]
    if not others:
        return ""
    lines = [
        "",
        "Other sessions work the sibling tickets at the same time, from the same",
        "base. A file two of you edit conflicts at merge, so read the row before you",
        "edit:",
        "",
        "| Ticket | Branch | Files it owns | Merge order |",
        "| --- | --- | --- | --- |",
    ]
    for issue in others:
        owned = issue.get("owned") or ", ".join(
            f"`{path}`" for path in issue.get("claims", [])
        )
        lines.append(
            f"| #{issue['number']} | `{issue['branch']}` | {owned or 'unstated'} "
            f"| {order.get(issue['number'], '-')} |"
        )
    lines.append("")
    return "\n".join(lines)


def verb_render(args: argparse.Namespace) -> int:
    plan_path = Path(args.plan)
    if not plan_path.is_file():
        fail(f"no plan at {plan_path}; run the plan verb first")
    plan = json.loads(plan_path.read_text())
    notes_dir = Path(args.notes)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    template = Path(args.template).read_text()

    order_list = (
        [int(number) for number in args.merge_order.split(",") if number.strip()]
        if args.merge_order
        else [issue["number"] for issue in plan["issues"]]
    )
    order = {number: index + 1 for index, number in enumerate(order_list)}

    autonomy = ""
    if args.autonomous:
        body = Path(args.autonomy).read_text().replace("<run dir>", str(out.resolve()))
        autonomy = (
            "# Autonomous mode\n\n" + re.sub(r"\A# .*\n+", "", body).strip() + "\n"
        )

    rendered = []
    for issue in plan["issues"]:
        slug = issue["slug"]
        sections = parse_notes(notes_dir / f"{slug}.md", slug)
        owned = sections.get("files owned", "").strip()
        issue["owned"] = owned.splitlines()[0].strip() if owned else ""
        rendered.append((issue, sections))

    for issue, sections in rendered:
        slug = issue["slug"]
        host_line = sections.get("host resources", "").strip() or (
            "This ticket needs no shared host resource. Keep off the host for it."
        )
        claims = issue["claims"]
        claims_line = (
            "This issue names these files: "
            + ", ".join(f"`{path}`" for path in claims)
            + ". Read them before you edit. The row for this ticket in the table "
            "below is what it owns, and a shared file belongs to one session only."
            if claims
            else "This issue names no file. Read the code before you edit, and keep the diff to what the change needs."
        )
        extra = sections.get("extra rules", "").strip()
        extra_rules = ""
        if extra:
            extra_rules = "\n".join(
                f"- {line.lstrip('- ').strip()}"
                for line in extra.splitlines()
                if line.strip()
            )
        values = {
            "CHECKOUT": "PENDING: from the spawn dry run",
            "REPO": plan["repo"],
            "BRANCH": issue["branch"],
            "BASE": plan["base"],
            "ASK": args.ask
            or f"Implement #{issue['number']} — {issue['title']} — with the `{args.implement_skill}` skill.",
            "WHY": sections["why"],
            "RULES_POINTER": args.rules_pointer,
            "IMPLEMENT_SKILL": args.implement_skill,
            "IMPLEMENT_SKILL_PATH": args.implement_skill_path,
            "ISSUE_REF": f"#{issue['number']}",
            "ISSUE_URL": issue["url"],
            "ISSUE_NUMBER": str(issue["number"]),
            "CLAIMS": claims_line,
            "HOST_LINE": host_line,
            "SIBLING_TABLE": sibling_table(
                plan["issues"], issue["number"], order
            ).strip(),
            "STEPS": sections["what to do"],
            "EXTRA_RULES": extra_rules,
            "DELIVERY": args.delivery,
            "AUTONOMY": autonomy.strip(),
            "DONE_WHEN": sections["done when"],
        }
        brief = template
        for key, value in values.items():
            brief = brief.replace("{{" + key + "}}", value)
        leftover = re.findall(r"\{\{[A-Z_]+\}\}", brief)
        if leftover:
            fail(
                f"unfilled placeholders for {slug}: {', '.join(sorted(set(leftover)))}"
            )
        prompt_path = out / f"hwt-prompt-{slug}.md"
        goal_path = out / f"hwt-goal-{slug}.md"
        prompt_path.write_text(brief.rstrip() + "\n")
        goal_path.write_text(sections["goal"].strip() + "\n")
        print(f"hwt-implement: rendered {prompt_path} and {goal_path}")

    plan["merge_order"] = order_list
    plan["autonomous"] = bool(args.autonomous)
    (out / "plan-rendered.json").write_text(json.dumps(plan, indent=2) + "\n")
    return 0


def verify_dry_run(
    text: str, repo: str, branch: str, goal: str, space_name: str
) -> str:
    checkout = ""
    for line in text.splitlines():
        if line.startswith("hwt: repository"):
            printed = line.split("hwt: repository", 1)[1].strip()
            if Path(printed).resolve() != Path(repo).resolve():
                raise Refusal(f"dry run names repository {printed}, not {repo}")
        elif line.startswith("hwt: checkout"):
            checkout = line.split("hwt: checkout", 1)[1].strip().split(" ", 1)[0]
            if branch not in line:
                raise Refusal(f"dry run checkout does not name {branch}: {line}")
        elif line.startswith("hwt: goal"):
            printed = line.split("hwt: goal", 1)[1].strip()
            if printed != goal.strip():
                raise Refusal(
                    "dry run goal does not match the goal file: "
                    f"printed {printed!r}, file {goal.strip()!r}"
                )
        elif line.startswith("hwt: herdr") and space_name not in line:
            raise Refusal(f"dry run space line does not name {space_name}: {line}")
        elif line.startswith("hwt: focus") and "stays on" not in line:
            raise Refusal(f"dry run would move the window: {line}")
    if not checkout:
        raise Refusal("dry run printed no checkout line")
    return checkout


def verb_spawn(args: argparse.Namespace) -> int:
    repo = repo_root(args.repo or ".")
    out = Path(args.out)
    plan_path = out / "plan-rendered.json"
    if not plan_path.is_file():
        fail(f"no rendered plan at {plan_path}; run the render verb first")
    plan = json.loads(plan_path.read_text())
    wanted = {int(number) for number in args.only.split(",")} if args.only else None
    hwt = ["hwt", "-r", repo, "-b", plan["base"], "--agent", args.agent, "--no-focus"]
    if args.model:
        hwt += ["--model", args.model]

    spawned = []
    refused: list[dict] = []
    for issue in plan["issues"]:
        if wanted is not None and issue["number"] not in wanted:
            continue
        slug = issue["slug"]
        prompt_path = out / f"hwt-prompt-{slug}.md"
        goal_path = out / f"hwt-goal-{slug}.md"
        if not prompt_path.is_file() or not goal_path.is_file():
            fail(f"render the briefs first: {prompt_path} or {goal_path} is missing")
        goal = goal_path.read_text()

        dry = run(
            [
                hwt[0],
                "-n",
                *hwt[1:],
                "--task-file",
                str(prompt_path),
                "--goal-file",
                str(goal_path),
                "--space-name",
                issue["space_name"],
                issue["branch"],
            ]
        )
        if dry.returncode != 0:
            detail = (dry.stderr or dry.stdout).strip().splitlines()
            refused.append(
                {
                    "issue": issue,
                    "reason": "hwt refused the dry run: "
                    + (detail[-1] if detail else f"exit {dry.returncode}"),
                }
            )
            continue
        try:
            checkout = verify_dry_run(
                dry.stdout, repo, issue["branch"], goal, issue["space_name"]
            )
        except Refusal as exc:
            refused.append({"issue": issue, "reason": str(exc)})
            continue

        brief = prompt_path.read_text()
        brief = re.sub(r"(?m)^Checkout: .*$", f"Checkout: {checkout}", brief, count=1)
        prompt_path.write_text(brief)

        if not args.go:
            print(
                f"hwt-implement: planned #{issue['number']} {issue['branch']} "
                f"-> {checkout} (space {issue['space_name']})"
            )
            spawned.append(
                {
                    "issue": issue,
                    "checkout": checkout,
                    "space_name": issue["space_name"],
                    "space": "",
                    "spawned": False,
                }
            )
            continue

        real = run(
            [
                hwt[0],
                *hwt[1:],
                "--task-file",
                str(prompt_path),
                "--goal-file",
                str(goal_path),
                "--space-name",
                issue["space_name"],
                issue["branch"],
            ]
        )
        if real.returncode != 0:
            detail = (real.stderr or real.stdout).strip().splitlines()
            refused.append(
                {
                    "issue": issue,
                    "reason": "hwt refused the spawn: "
                    + (detail[-1] if detail else f"exit {real.returncode}"),
                }
            )
            continue
        printed = [
            line
            for line in real.stdout.splitlines()
            if line.startswith("hwt: ") and "->" in line
        ]
        space = ""
        blob = real.stdout[real.stdout.find("{") : real.stdout.rfind("}") + 1]
        if blob.strip().startswith("{"):
            try:
                space = json.loads(blob).get("space", "")
            except json.JSONDecodeError:
                space = ""
        upstream = git(
            repo, "rev-parse", "--abbrev-ref", f"{issue['branch']}@{{upstream}}"
        )
        if upstream.returncode == 0:
            git(repo, "branch", "--unset-upstream", issue["branch"])
        print(printed[0] if printed else f"hwt-implement: spawned {issue['branch']}")
        spawned.append(
            {
                "issue": issue,
                "checkout": checkout,
                "space_name": issue["space_name"],
                "space": space,
                "spawned": True,
            }
        )

    manifest = [
        f"# Run {plan['generated_at']}",
        "",
        f"Repository: {plan['repo']}",
        f"Base: {plan['base']} ({plan['base_reason']})",
        f"Autonomous: {plan.get('autonomous', False)}",
        f"Merge order: {', '.join('#' + str(n) for n in plan.get('merge_order', []))}",
        "",
        "| Issue | Branch | Checkout | Space name | Space | Spawned |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for entry in spawned:
        issue = entry["issue"]
        manifest.append(
            f"| #{issue['number']} {issue['title']} | `{issue['branch']}` "
            f"| {entry['checkout']} | {entry['space_name']} "
            f"| {entry['space'] or '-'} "
            f"| {'yes' if entry['spawned'] else 'planned only'} |"
        )
    if plan.get("overlaps"):
        manifest += ["", "## Contested files", ""]
        manifest += [
            f"- `{overlap['path']}`: "
            + ", ".join(f"#{number}" for number in overlap["issues"])
            for overlap in plan["overlaps"]
        ]
    manifest += ["", "## Briefs", ""]
    manifest += [
        f"- #{entry['issue']['number']}: {out / ('hwt-prompt-' + entry['issue']['slug'] + '.md')}"
        + f" and {out / ('hwt-goal-' + entry['issue']['slug'] + '.md')}"
        for entry in spawned
    ]
    if refused:
        manifest += ["", "## Refused", ""]
        manifest += [
            f"- #{entry['issue']['number']} {entry['issue']['title']}: {entry['reason']}"
            for entry in refused
        ]
    (out / "manifest.md").write_text("\n".join(manifest) + "\n")
    print(f"hwt-implement: manifest {out / 'manifest.md'}")
    for entry in refused:
        print(
            f"hwt-implement: refused #{entry['issue']['number']} "
            f"{entry['issue']['title']}: {entry['reason']}",
            file=sys.stderr,
        )
    return 1 if refused else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="hwt_implement.py", description=__doc__)
    sub = parser.add_subparsers(dest="verb", required=True)

    plan = sub.add_parser("plan", help="preflight issues and find their overlaps")
    plan.add_argument("issues", nargs="+", type=int)
    plan.add_argument("--repo", default=".")
    plan.add_argument("--base", default=None)
    plan.add_argument("--prefix", default=None, help="branch prefix, e.g. fix")
    plan.add_argument("--json", default=None, help="write the plan to this path")
    plan.set_defaults(func=verb_plan)

    render = sub.add_parser("render", help="render briefs and goals")
    render.add_argument("--plan", required=True)
    render.add_argument("--notes", required=True)
    render.add_argument("--out", required=True)
    render.add_argument(
        "--template",
        default=str(
            Path(__file__).resolve().parent.parent / "references" / "brief-template.md"
        ),
    )
    render.add_argument(
        "--autonomy",
        default=str(
            Path(__file__).resolve().parent.parent / "references" / "autonomy.md"
        ),
    )
    render.add_argument("--autonomous", action="store_true")
    render.add_argument(
        "--merge-order", default=None, help="issue numbers, first merge first"
    )
    render.add_argument("--ask", default=None)
    render.add_argument(
        "--rules-pointer",
        default="Read at least `.kb/agents.md`, `.kb/project.md`, and `.kb/issue-tracker.md`.",
    )
    render.add_argument("--implement-skill", default="implement")
    render.add_argument(
        "--implement-skill-path",
        default=str(Path.home() / ".agents" / "skills" / "implement"),
    )
    render.add_argument(
        "--delivery",
        default=(
            "Push this branch and open one pull request that closes this issue, marked "
            "ready. Never merge, never force-push, never push another branch, and never "
            "touch another worktree's branch."
        ),
    )
    render.set_defaults(func=verb_render)

    spawn = sub.add_parser("spawn", help="dry-run, verify, then spawn")
    spawn.add_argument("--out", required=True)
    spawn.add_argument("--repo", default=".")
    spawn.add_argument("--agent", default="opencode")
    spawn.add_argument("--model", default=None)
    spawn.add_argument("--only", default=None, help="issue numbers, comma separated")
    spawn.add_argument(
        "--go", action="store_true", help="spawn; without it, dry run only"
    )
    spawn.set_defaults(func=verb_spawn)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
