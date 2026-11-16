#!/usr/bin/env python3
"""Build one page that holds the diagrams of several options and their descriptions.

The script takes a JSON spec that describes a decision with several options.
It writes the Mermaid source of every option, renders each one, and writes a
single HTML page that holds the descriptions, a comparison table, and the
diagram of every option with the differing steps in a shaded band.

The output directory defaults to a fresh directory under ``~/tmp``, so a run
leaves nothing in the repository and two runs never share a directory.

The script depends on the ``diagram`` skill for the Canonical brand theme. When
that skill is not installed, it falls back to the Mermaid CLI on its own, and
the page says that the theme is missing.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# The diagram skill renders with the Canonical brand theme. The skill is
# global, and the path holds the skill in its installed place.
DIAGRAM_SCRIPT = Path.home() / ".config/opencode/skill/diagram/scripts/diagram.py"

# The default parent of the output directory. The files are temporary, and
# the user's home is the place a browser can read.
DEFAULT_PARENT = Path.home() / "tmp"

# The colour of the band that holds the steps an option changes. The band is
# a pale tint of the accent colour of the page.
BAND_RGB = "255, 233, 219"

# The accent colour of the Canonical brand.
ACCENT = "#E95420"

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")

PAGE_CSS = """
  :root {
    --accent: #E95420;
    --ink: #111111;
    --muted: #555555;
    --line: #d6d6d6;
  }
  body {
    margin: 0 auto;
    max-width: 1100px;
    padding: 2.5rem 1.5rem 5rem;
    font-family: Ubuntu Sans, "Ubuntu", "Trebuchet MS", Verdana, Arial, sans-serif;
    color: var(--ink);
    line-height: 1.55;
    background: #ffffff;
  }
  h1 { font-size: 1.9rem; margin: 0 0 0.4rem; }
  h2 { font-size: 1.25rem; margin: 2.5rem 0 0.3rem; }
  h3 { font-size: 1rem; margin: 1.2rem 0 0.3rem; color: var(--muted); }
  p { margin: 0.5rem 0; }
  ul { margin: 0.4rem 0 0.8rem; padding-left: 1.2rem; }
  li { margin: 0.25rem 0; }
  code {
    font-family: "Ubuntu Mono", "DejaVu Sans Mono", monospace;
    font-size: 0.92em;
    background: #f3f3f3;
    padding: 0.05em 0.3em;
    border-radius: 3px;
  }
  .lead { font-size: 1.05rem; color: var(--muted); }
  .panel {
    border: 1px solid var(--line);
    border-left: 4px solid var(--accent);
    padding: 0.8rem 1.1rem;
    margin: 1.2rem 0;
    background: #fbfbfb;
  }
  .figure {
    border: 1px solid var(--line);
    padding: 0.8rem;
    margin: 1rem 0 0;
    overflow-x: auto;
    background: #ffffff;
  }
  .figure svg { width: 100%; height: auto; display: block; }
  .label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--accent);
    font-weight: 700;
  }
  .key {
    background: #fff1e9;
    border-left: 4px solid var(--accent);
    padding: 0.5rem 0.8rem;
    margin: 0.7rem 0;
  }
  .answer {
    border: 2px solid var(--accent);
    padding: 1rem 1.2rem;
    margin: 2rem 0 0;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 1.2rem 0 0;
    font-size: 0.95rem;
  }
  th, td {
    border: 1px solid var(--line);
    padding: 0.45rem 0.6rem;
    text-align: left;
    vertical-align: top;
  }
  th { background: #f3f3f3; }
  details { margin: 0.8rem 0 0; }
  summary { cursor: pointer; color: var(--muted); font-size: 0.92rem; }
  pre {
    background: #f3f3f3;
    padding: 0.8rem;
    overflow-x: auto;
    font-size: 0.85rem;
    border-radius: 3px;
  }
  hr { border: 0; border-top: 1px solid var(--line); margin: 2.5rem 0 0; }
"""


class SpecError(Exception):
    """The spec does not hold what the page needs."""


class RenderError(Exception):
    """A diagram did not render."""


# -- the spec ------------------------------------------------------------


def load_spec(path: Path) -> dict[str, Any]:
    """Read the spec and check that it holds what the page needs."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SpecError(f"cannot read the spec {path}: {exc}") from exc
    try:
        spec = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SpecError(f"the spec {path} is not JSON: {exc}") from exc
    problems = check_spec(spec)
    if problems:
        joined = "\n".join(f"  - {problem}" for problem in problems)
        raise SpecError(f"the spec {path} is not usable:\n{joined}")
    return spec


def check_spec(spec: Any) -> list[str]:
    """The list of problems that keep the page from being written."""
    problems: list[str] = []
    if not isinstance(spec, dict):
        return ["the spec holds no object"]
    if not _text(spec.get("title")):
        problems.append("the spec needs a title")
    options = spec.get("options")
    if not isinstance(options, list) or not options:
        problems.append("the spec needs a list of options")
        return problems
    seen: set[str] = set()
    for index, option in enumerate(options):
        where = f"option {index + 1}"
        if not isinstance(option, dict):
            problems.append(f"{where} holds no object")
            continue
        identifier = option.get("id")
        if not _text(identifier) or not ID_PATTERN.match(identifier):
            problems.append(f"{where} needs an id of lower case letters and digits")
        elif identifier in seen:
            problems.append(f"{where} repeats the id {identifier}")
        else:
            seen.add(identifier)
        if not _text(option.get("name")):
            problems.append(f"{where} needs a name")
        if not _text(option.get("headline")):
            problems.append(f"{where} needs a headline")
        problems.extend(_check_diagram(option, where))
    for key in ("question", "situation", "actors", "answer"):
        if key not in spec:
            problems.append(f"the spec needs {key}")
    return problems


def _check_diagram(option: dict[str, Any], where: str) -> list[str]:
    """The problems with the diagram of one option."""
    problems: list[str] = []
    diagram = option.get("diagram")
    source = option.get("source")
    if diagram is None and source is None:
        return [f"{where} needs a diagram or a source"]
    if diagram is not None:
        if not isinstance(diagram, dict):
            return [f"{where} holds a diagram that is not an object"]
        bands = diagram.get("bands")
        if bands is not None:
            if not isinstance(bands, list) or not bands:
                problems.append(f"{where} needs a list of bands in its diagram")
            else:
                for index, band in enumerate(bands):
                    problems.extend(_check_band(band, f"{where} band {index + 1}"))
        else:
            problems.extend(_check_band(diagram, where, fields=("steps",)))
    if source is not None and not _text(source):
        problems.append(f"{where} holds an empty source")
    return problems


def _check_band(
    band: Any, where: str, fields: tuple[str, ...] = ("steps",)
) -> list[str]:
    """The problems with one band of steps."""
    problems: list[str] = []
    if not isinstance(band, dict):
        return [f"{where} holds no object"]
    for key in fields:
        value = band.get(key)
        if not isinstance(value, list) or not value:
            problems.append(f"{where} needs a list of {key}")
        elif not all(_text(line) for line in value):
            problems.append(f"{where} holds an empty line in its {key}")
    if not _text(band.get("highlight_label")):
        problems.append(f"{where} needs a highlight_label")
    return problems


def _text(value: Any) -> bool:
    """True when the value is a string with something in it."""
    return isinstance(value, str) and value.strip() != ""


# -- the Mermaid source --------------------------------------------------


def mermaid_source(spec: dict[str, Any], option: dict[str, Any]) -> str:
    """The Mermaid source of the diagram of one option.

    A diagram that names a prefix and steps gets a band around the steps, so
    the steps that the option changes stand out. A diagram that names a
    source file is used as it is, and the caller holds the band.
    """
    source = option.get("source")
    if source:
        path = Path(source)
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            raise SpecError(f"cannot read the source {path}: {exc}") from exc
    diagram = option["diagram"]
    lines = ["sequenceDiagram"]
    participants = spec.get("participants") or []
    for participant in participants:
        lines.append(f"    participant {participant['id']} as {participant['name']}")
    if not participants:
        lines.append("    participant A as Actor")
    baseline_note = spec.get("baseline_note")
    if _text(baseline_note):
        first = participants[0]["id"] if participants else "A"
        last = participants[-1]["id"] if participants else "A"
        lines.append(f"    Note over {first},{last}: {baseline_note}")
    for line in diagram["prefix"]:
        lines.append(f"    {line}")
    bands = diagram.get("bands")
    if bands is None:
        bands = [diagram]
    for band in bands:
        lines.append(f"    rect rgb({BAND_RGB})")
        lines.append(
            f"    Note over {_note_over(band, participants)}: {band['highlight_label']}"
        )
        for line in band["steps"]:
            lines.append(f"    {line}")
        lines.append("    end")
    return "\n".join(lines) + "\n"


def _note_over(band: dict[str, Any], participants: list[dict[str, Any]]) -> str:
    """The actors the note of a band names."""
    note_over = band.get("highlight_note_over")
    if _text(note_over):
        return note_over
    first = participants[0]["id"] if participants else "A"
    last = participants[-1]["id"] if participants else "A"
    return f"{first},{last}"


# -- the render ----------------------------------------------------------


def render_diagram(source_path: Path, name: str, out_dir: Path) -> Path:
    """Render one Mermaid source and return the path of the SVG."""
    if DIAGRAM_SCRIPT.is_file():
        command = [
            sys.executable,
            str(DIAGRAM_SCRIPT),
            str(source_path),
            "--name",
            name,
            "--out-dir",
            str(out_dir),
            "--no-html",
        ]
    elif shutil.which("mmdc"):
        command = [
            "mmdc",
            "--input",
            str(source_path),
            "--output",
            str(out_dir / f"{name}.svg"),
            "--backgroundColor",
            "white",
        ]
    else:
        raise RenderError(
            "neither the diagram skill nor the Mermaid CLI is available, so no "
            "diagram can be rendered"
        )
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        message = (result.stderr or result.stdout).strip().splitlines()
        detail = message[-1] if message else "the render failed"
        raise RenderError(f"the diagram {name} did not render: {detail}")
    svg = out_dir / f"{name}.svg"
    if not svg.is_file():
        raise RenderError(f"the diagram {name} did not write {svg}")
    return svg


def theme_is_present() -> bool:
    """True when the brand theme is available."""
    return DIAGRAM_SCRIPT.is_file()


# -- the page ------------------------------------------------------------


def build_page(spec: dict[str, Any], options: list[dict[str, Any]]) -> str:
    """The one HTML page that holds every option."""
    parts: list[str] = []
    parts.append(_head(spec))
    parts.append(f"<h1>{html.escape(spec['title'])}</h1>")
    if _text(spec.get("subtitle")):
        parts.append(f'<p class="lead">{html.escape(spec["subtitle"])}</p>')
    parts.append("<h2>The question</h2>")
    parts.append(f"<p>{html.escape(spec.get('question', ''))}</p>")
    situation = spec.get("situation") or []
    if situation:
        parts.append("<h2>What happens today</h2>")
        parts.append("<ul>")
        for line in situation:
            parts.append(f"<li>{html.escape(line)}</li>")
        parts.append("</ul>")
    actors = spec.get("actors") or []
    if actors:
        parts.append('<div class="panel">')
        parts.append('<p><span class="label">The actors in each diagram</span></p>')
        parts.append("<ul>")
        for actor in actors:
            parts.append(
                f"<li><b>{html.escape(actor['name'])}</b> "
                f"{html.escape(actor.get('role', ''))}</li>"
            )
        parts.append("</ul>")
        parts.append("</div>")
    if _text(spec.get("legend")):
        parts.append(f'<div class="key">{html.escape(spec["legend"])}</div>')
    parts.append(_table(options))
    for option in options:
        parts.append(_option_section(spec, option))
    parts.append(_answer(spec))
    not_verified = spec.get("not_verified") or []
    if not_verified:
        parts.append("<h2>What was not verified</h2>")
        parts.append("<ul>")
        for line in not_verified:
            parts.append(f"<li>{html.escape(line)}</li>")
        parts.append("</ul>")
    if not theme_is_present():
        parts.append(
            '<div class="key">The Canonical brand theme is not installed, so the '
            "diagrams in this page carry the default Mermaid style.</div>"
        )
    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts) + "\n"


def _head(spec: dict[str, Any]) -> str:
    title = html.escape(spec.get("title", "Options"))
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{title}</title>\n<style>{PAGE_CSS}</style>\n</head>\n<body>"
    )


def _table(options: list[dict[str, Any]]) -> str:
    """The table that compares the options."""
    parts = ["<h2>The options at a glance</h2>", "<table>", "<thead><tr>"]
    for heading in ("Option", "Who restores it", "What changes", "What stays open"):
        parts.append(f"<th>{html.escape(heading)}</th>")
    parts.append("</tr></thead><tbody>")
    for option in options:
        parts.append("<tr>")
        parts.append(
            f"<td><b>{html.escape(option['name'])}</b><br>"
            f"{html.escape(option.get('headline', ''))}</td>"
        )
        for key in ("restores", "changes", "leaves_open"):
            parts.append(f"<td>{html.escape(option.get(key, ''))}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "\n".join(parts)


def _option_section(spec: dict[str, Any], option: dict[str, Any]) -> str:
    """One section of the page, with the diagram of one option."""
    parts = ["<hr>"]
    parts.append(
        f"<h2>{html.escape(option['name'])}: {html.escape(option['headline'])}</h2>"
    )
    if _text(option.get("what")):
        parts.append(f"<p>{html.escape(option['what'])}</p>")
    if _text(option.get("window")):
        parts.append("<h3>What it does to the window</h3>")
        parts.append(f"<p>{html.escape(option['window'])}</p>")
    if _text(option.get("leaves_open")):
        parts.append("<h3>What it leaves open</h3>")
        parts.append(f"<p>{html.escape(option['leaves_open'])}</p>")
    why = option.get("why") or []
    if why:
        parts.append("<h3>Why</h3>")
        parts.append("<ul>")
        for reason in why:
            parts.append(f"<li>{html.escape(reason)}</li>")
        parts.append("</ul>")
    for label in _band_labels(option):
        parts.append(f'<div class="key">{html.escape(label)}</div>')
    svg = option.get("svg_path")
    if svg:
        parts.append('<div class="figure">')
        parts.append(Path(svg).read_text(encoding="utf-8"))
        parts.append("</div>")
    source = option.get("source_path")
    if source:
        parts.append("<details><summary>The Mermaid source of this diagram</summary>")
        parts.append(
            "<pre>" + html.escape(Path(source).read_text(encoding="utf-8")) + "</pre>"
        )
        parts.append("</details>")
    return "\n".join(parts)


def _band_labels(option: dict[str, Any]) -> list[str]:
    """The labels of the bands that mark the steps an option changes."""
    diagram = option.get("diagram")
    if not isinstance(diagram, dict):
        return []
    bands = diagram.get("bands")
    if bands is None:
        bands = [diagram]
    return [
        band["highlight_label"]
        for band in bands
        if isinstance(band, dict) and _text(band.get("highlight_label"))
    ]


def _answer(spec: dict[str, Any]) -> str:
    """The box that holds the answer."""
    answer = spec.get("answer") or {}
    parts = ['<div class="answer">']
    parts.append('<p><span class="label">The answer</span></p>')
    if _text(answer.get("summary")):
        parts.append(f"<p>{html.escape(answer['summary'])}</p>")
    if _text(answer.get("detail")):
        parts.append(f"<p>{html.escape(answer['detail'])}</p>")
    parts.append("</div>")
    return "\n".join(parts)


# -- the output directory ------------------------------------------------


def unique_dir(parent: Path, slug: str) -> Path:
    """A fresh directory under the parent, so two runs never share one."""
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    candidate = parent / f"diagram-options-{slug}-{stamp}"
    counter = 1
    while candidate.exists():
        candidate = parent / f"diagram-options-{slug}-{stamp}-{counter}"
        counter += 1
    return candidate


def slug_of(title: str) -> str:
    """A short name for the title, safe in a path."""
    words = re.findall(r"[a-z0-9]+", title.lower())
    return "-".join(words[:5]) or "options"


def open_in_browser(path: Path) -> None:
    """Open the page in the browser of the host."""
    opener = shutil.which("xdg-open") or shutil.which("firefox")
    if not opener:
        return
    url = path.resolve().as_uri()
    subprocess.Popen(
        [opener, url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


# -- the run -------------------------------------------------------------


def build(spec_path: Path, out_dir: Path | None, open_page: bool) -> int:
    """Run the whole build and return the exit code."""
    spec = load_spec(spec_path)
    if out_dir is None:
        out_dir = unique_dir(DEFAULT_PARENT, slug_of(spec["title"]))
    out_dir.mkdir(parents=True, exist_ok=True)
    options: list[dict[str, Any]] = []
    for option in spec["options"]:
        name = option["id"]
        source_text = mermaid_source(spec, option)
        source_path = out_dir / f"{name}.mmd"
        source_path.write_text(source_text, encoding="utf-8")
        svg_path = render_diagram(source_path, name, out_dir)
        rendered = dict(option)
        rendered["source_path"] = str(source_path)
        rendered["svg_path"] = str(svg_path)
        options.append(rendered)
    page_path = out_dir / "options.html"
    page_path.write_text(build_page(spec, options), encoding="utf-8")
    print(f"directory: {out_dir}")
    print(f"page: {page_path}")
    for option in options:
        print(f"diagram: {option['svg_path']}")
    if open_page:
        open_in_browser(page_path)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="build_options_page.py",
        description="Build one HTML page that holds the options and their diagrams.",
    )
    parser.add_argument("spec", type=Path, help="the JSON spec of the options")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="the directory that receives the files (default: a fresh directory under ~/tmp)",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="open the page in the browser of the host",
    )
    args = parser.parse_args(argv)
    try:
        return build(args.spec, args.out_dir, args.open)
    except SpecError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except RenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
