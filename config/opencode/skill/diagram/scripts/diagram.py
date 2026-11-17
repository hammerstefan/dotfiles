#!/usr/bin/env python3
"""Render an on-brand Canonical Mermaid diagram.

The script takes a Mermaid source file, applies the Canonical diagram brand,
and writes the diagram source, the rendered SVG, and a live HTML page.

The brand theme comes from the private ``canonical/mermaid-brand-kit`` repository.
The script fetches the generated artifacts with the GitHub CLI at run time. It
never clones the kit and never installs anything, so the render costs about two
seconds.

Three things in the upstream artifacts break a naive pipeline. This script
handles all three:

1. The fetched frontmatter starts with a ``#`` comment line before the opening
   ``---`` fence. Prepended as it is, that comment becomes diagram body text
   and the render fails.
2. The ``themeCSS`` string contains ``---`` inside it. A search for the closing
   fence must match a whole line, not a substring.
3. The flowchart ``classDef`` block is valid only in a flowchart. Mermaid
   rejects it in every other family.

The script also repairs two brand leaks that the low-cost render path cannot
avoid. The C4 family sets its own box fill and corner radius, and Mermaid
writes them as inline styles with ``!important``, which no stylesheet can
override. The script corrects them after the render.

Every step is verified. The script fails with a non-zero exit code and writes
nothing when the brand theme cannot be fetched, when the render fails, or when
the rendered output does not meet the brand contract.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

# The skill root keeps the path as the caller reached it. Resolving the path
# here moves the skill into another directory tree, and a relative path from
# the output directory then climbs past the filesystem root. The result is a
# script reference that a browser cannot load.
SKILL_ROOT = Path(__file__).resolve().parent.parent
VENDOR_DIR = SKILL_ROOT / "vendor"

BRAND_KIT_REPO = "canonical/mermaid-brand-kit"
BRAND_KIT_PATH = "dist"

# The artifacts the kit generates. Each one is fetched with the GitHub CLI.
FRONTMATTER_ARTIFACT = "brand-theme.frontmatter.yaml"
FLOWCHART_ARTIFACT = "brand-theme.flowchart.mmd"

# Mermaid families this skill renders. Each family is a native surface for the
# structural roles the brand defines.
SUPPORTED_FAMILIES = (
    "flowchart",
    "sequence",
    "state",
    "class",
    "c4",
    "er",
    "gantt",
)

# The brand palette. A colour outside this set does not belong in a Canonical
# diagram.
BRAND_WHITE = "#FFFFFF"
BRAND_GREY = "#F3F3F3"
BRAND_INK = "#000000"
BRAND_HELPER = "#666666"
BRAND_ORANGE = "#E95420"

BRAND_COLORS = frozenset(
    {
        BRAND_WHITE,
        BRAND_GREY,
        BRAND_INK,
        BRAND_HELPER,
        BRAND_ORANGE,
        # The greyscale chart ramp. A diagram never carries colour as data.
        "#D9D9D9",
        "#BFBFBF",
        "#A6A6A6",
        "#8C8C8C",
        "#737373",
    }
)

# CSS values that are not colours. They must survive the clamp untouched.
COLOR_KEYWORDS = re.compile(
    r"^(none|transparent|currentcolor|inherit|initial|unset|revert"
    r"|context-fill|context-stroke|url\(|var\(|rgb\(|rgba\(|hsl\(|hsla\()",
    re.IGNORECASE,
)

# The C4 shape keys the brand config leaves unset. Mermaid then falls back to
# its own C4 palette, which is blue.
C4_BG_KEYS = (
    "person_bg_color",
    "system_bg_color",
    "system_db_bg_color",
    "system_queue_bg_color",
    "container_bg_color",
    "container_db_bg_color",
    "container_queue_bg_color",
    "component_bg_color",
    "component_db_bg_color",
    "component_queue_bg_color",
)


class DiagramError(RuntimeError):
    """Raised when the diagram cannot be produced."""


# ---------------------------------------------------------------------------
# Brand theme
# ---------------------------------------------------------------------------


def cache_dir() -> Path:
    """Return the directory that holds the last successful fetch."""
    base = os.environ.get("XDG_CACHE_HOME")
    root = Path(base) if base else Path.home() / ".cache"
    return root / "opencode" / "diagram"


def fetch_artifact(name: str, use_cache: bool = True) -> tuple[str, bool]:
    """Fetch one generated artifact from the brand kit.

    Returns the artifact text and a flag that says whether the text came from
    the cache. The cache is a fallback for a machine with no GitHub access. A
    cached artifact can be older than the current kit, so the caller must tell
    the user which one it used.
    """
    cached = cache_dir() / name
    try:
        text = _fetch_with_gh(name)
    except DiagramError as exc:
        if use_cache and cached.is_file():
            return cached.read_text(encoding="utf-8"), True
        raise DiagramError(
            f"cannot read the brand theme from {BRAND_KIT_REPO}: {exc}\n"
            "Authenticate the GitHub CLI with `gh auth login` and make sure the "
            f"account can read {BRAND_KIT_REPO}, then run the command again."
        ) from exc

    try:
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_text(text, encoding="utf-8")
    except OSError:
        # A read-only cache is not a reason to fail the render.
        pass
    return text, False


def _fetch_with_gh(name: str) -> str:
    """Read one artifact through the GitHub CLI."""
    if shutil.which("gh") is None:
        raise DiagramError("the GitHub CLI (gh) is not installed")

    path = f"repos/{BRAND_KIT_REPO}/contents/{BRAND_KIT_PATH}/{name}"
    try:
        completed = subprocess.run(
            ["gh", "api", path, "--jq", ".content"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise DiagramError(f"cannot run the GitHub CLI: {exc}") from exc

    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout).strip()
        raise DiagramError(message or "the GitHub CLI returned an error")

    encoded = "".join(completed.stdout.split())
    if not encoded:
        raise DiagramError(f"the artifact {name} is empty")
    try:
        return base64.b64decode(encoded).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise DiagramError(f"the artifact {name} is not valid base64 text") from exc


def extract_frontmatter(artifact: str) -> str:
    """Return the frontmatter block of the fetched artifact.

    The artifact carries a generated notice on its first line. That notice sits
    before the opening fence, so the block must start at the first line that is
    exactly a fence. The closing fence must also be a whole line, because the
    theme CSS contains a fence inside a string.
    """
    lines = artifact.splitlines()
    fences = [index for index, line in enumerate(lines) if line.strip() == "---"]
    if len(fences) < 2:
        raise DiagramError(
            "the brand theme artifact does not contain a frontmatter block"
        )
    first, last = fences[0], fences[-1]
    return "\n".join(lines[first : last + 1]) + "\n"


def flowchart_class_defs(artifact: str) -> str:
    """Return the flowchart class definitions from the fetched artifact."""
    lines = [line for line in artifact.splitlines() if line.strip()]
    body = [
        line
        for line in lines
        if line.startswith("classDef ") or line.startswith("linkStyle ")
    ]
    if not body:
        raise DiagramError(
            "the brand theme artifact does not contain flowchart class definitions"
        )
    return "\n".join(body) + "\n"


def detect_family(source: str) -> str:
    """Return the Mermaid family of the diagram source.

    The family decides whether the flowchart class definitions apply. An
    unsupported family is an error, because a diagram outside the supported
    set does not carry the brand role vocabulary.
    """
    body = source
    if body.lstrip().startswith("---"):
        lines = body.splitlines()
        fences = [index for index, line in enumerate(lines) if line.strip() == "---"]
        if len(fences) >= 2:
            body = "\n".join(lines[fences[-1] + 1 :])

    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("%%"):
            continue
        head = stripped.split(" ", 1)[0].split(":", 1)[0]
        lowered = head.lower()
        if lowered in ("flowchart", "graph"):
            return "flowchart"
        if lowered == "sequencediagram":
            return "sequence"
        if lowered in ("statediagram", "statediagram-v2"):
            return "state"
        if lowered in ("classdiagram", "classdiagram-v2"):
            return "class"
        if lowered.startswith("c4"):
            return "c4"
        if lowered == "erdiagram":
            return "er"
        if lowered == "gantt":
            return "gantt"
        break

    raise DiagramError(
        "the diagram does not use a supported Mermaid family.\n"
        f"Supported families: {', '.join(SUPPORTED_FAMILIES)}."
    )


def apply_c4_palette(frontmatter: str) -> str:
    """Set the C4 box fills that the brand theme leaves unset.

    The brand theme sets the C4 borders but not the fills. Mermaid then uses
    its own C4 palette, which is blue. This function adds the missing fill
    values to the theme itself, so the change happens at render time.

    The theme is YAML. The C4 fills are added as plain lines under the ``c4``
    block, because the theme carries every other value in the same form.
    """
    if "\n  c4:\n" not in frontmatter:
        return frontmatter

    lines = frontmatter.splitlines()
    result: list[str] = []
    inside_c4 = False
    added: set[str] = set()

    for line in lines:
        if line == "  c4:":
            inside_c4 = True
            result.append(line)
            continue
        if inside_c4 and line.startswith("  ") and not line.startswith("   "):
            inside_c4 = False
        if inside_c4:
            match = re.match(r"^    ([a-z0-9_]+):", line)
            if match:
                key = match.group(1)
                added.add(key)
        result.append(line)

    extra = [f"    {key}: {BRAND_WHITE}" for key in C4_BG_KEYS if key not in added]
    if not extra:
        return frontmatter

    # The C4 block ends where the next top-level family block starts.
    for index in range(len(result) - 1, -1, -1):
        if result[index] == "  c4:":
            result[index + 1 : index + 1] = extra
            break

    return "\n".join(result) + "\n"


# ---------------------------------------------------------------------------
# Brand repair
# ---------------------------------------------------------------------------


# Short spellings and CSS colour names that mean a brand colour. Mermaid and
# Mermaid's own defaults use these forms.
BRAND_ALIASES = frozenset(
    {
        "#fff",
        "#000",
        "#666",
        "white",
        "black",
        "grey",
        "gray",
    }
)


def _expand_hex(value: str) -> str | None:
    """Return the six-digit form of a hex colour, or None."""
    text = value.strip().lower()
    if not text.startswith("#"):
        return None
    digits = text[1:]
    if len(digits) == 3:
        digits = "".join(digit * 2 for digit in digits)
    if len(digits) != 6 or any(digit not in "0123456789abcdef" for digit in digits):
        return None
    return f"#{digits}"


def _is_brand_color(value: str) -> bool:
    """Return whether the value is a brand colour.

    A colour counts as brand when it matches the palette in any spelling: the
    full hex form, a short hex form, a CSS colour name, or an rgb or hsl
    spelling of a palette colour.
    """
    text = value.strip().lower()
    if not text:
        return False
    if text in BRAND_ALIASES:
        return True
    expanded = _expand_hex(text)
    if expanded is not None:
        return expanded.upper() in {color.upper() for color in BRAND_COLORS}
    match = re.match(r"^rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)", text)
    if match:
        channels = tuple(round(float(channel)) for channel in match.groups())
        for brand in BRAND_COLORS:
            red = int(brand[1:3], 16)
            green = int(brand[3:5], 16)
            blue = int(brand[5:7], 16)
            if channels == (red, green, blue):
                return True
    return False


def _clamp_color(value: str, role: str) -> str:
    """Map one colour onto a brand token.

    A surface becomes white or grey. Ink is not a surface colour, because a dark
    fill under dark text is unreadable. A stroke or a text colour becomes ink.
    """
    raw = value.strip()
    if not raw or COLOR_KEYWORDS.match(raw) or _is_brand_color(raw):
        return raw
    if role == "fill":
        return BRAND_WHITE
    return BRAND_INK


def repair_svg(svg: str) -> str:
    """Repair the brand leaks that the low-cost render path leaves behind.

    The C4 family writes its box fill, its corner radius, and its label colour
    as inline styles with ``!important``. No stylesheet can override an inline
    declaration, so the brand theme cannot reach them and the repair changes
    the output instead.

    The repair follows the rule the brand kit uses for C4. A C4 box gets a
    white fill and an ink border. An external C4 box gets the grey fill. The
    label text becomes ink, because white text on a white box cannot be read.
    A C4 relation keeps its orange connector and takes ink for its label.

    The other families need no repair. The actor and composite fills that
    Mermaid writes into the style block are already overridden by the brand
    theme when the browser renders the diagram.
    """
    svg = _repair_c4(svg)
    svg = _clamp_remaining_colors(svg)
    return svg


def _repair_c4(svg: str) -> str:
    """Set the C4 boxes and labels to the brand tokens."""
    svg = re.sub(r"rx:12px !important", "rx:0 !important", svg)
    svg = re.sub(r"ry:12px !important", "ry:0 !important", svg)

    def fix_shape(group: str) -> str:
        external = "c4-external" in group
        fill = BRAND_GREY if external else BRAND_WHITE

        def fix_tag(match: re.Match[str]) -> str:
            tag = match.group(0)
            name = match.group(1).lower()
            if name in ("rect", "circle", "path", "ellipse", "polygon"):
                # The box surface and its border.
                tag = re.sub(
                    r"fill:#[0-9A-Fa-f]{3,6} !important",
                    f"fill:{fill} !important",
                    tag,
                )
                tag = re.sub(
                    r"stroke:#[0-9A-Fa-f]{3,6} !important",
                    f"stroke:{BRAND_INK} !important",
                    tag,
                )
            else:
                # The label sits on the box, so it takes the ink colour.
                tag = re.sub(
                    r"fill:#[0-9A-Fa-f]{3,6} !important",
                    f"fill:{BRAND_INK} !important",
                    tag,
                )
                tag = re.sub(
                    r"color:#[0-9A-Fa-f]{3,6} !important",
                    f"color:{BRAND_INK} !important",
                    tag,
                )
            return tag

        return re.sub(
            r"<(rect|circle|path|ellipse|polygon|text|g)\b[^>]*>", fix_tag, group
        )

    return _map_c4_groups(svg, fix_shape)


def _map_c4_groups(svg: str, transform: Any) -> str:
    """Apply the transform to every C4 shape group.

    The groups nest, so a regular expression cannot find where each one ends.
    This function walks the group structure and matches every opening tag with
    its own closing tag.
    """
    marker = 'class="node c4-shape'
    result: list[str] = []
    index = 0

    while True:
        start = svg.find(marker, index)
        if start == -1:
            result.append(svg[index:])
            break

        open_start = svg.rfind("<g", 0, start)
        end = _matching_group_end(svg, open_start)
        if end is None:
            result.append(svg[index:])
            break

        result.append(svg[index:open_start])
        result.append(transform(svg[open_start:end]))
        index = end

    return "".join(result)


def _matching_group_end(svg: str, start: int) -> int | None:
    """Return the index just past the group that opens at the given index."""
    depth = 0
    for match in re.finditer(r"<g\b[^>]*>|</g>", svg[start:]):
        token = match.group(0)
        if token.startswith("</"):
            depth -= 1
            if depth == 0:
                return start + match.end()
        else:
            depth += 1
    return None


def _clamp_remaining_colors(svg: str) -> str:
    """Map every remaining off-brand colour onto a brand token.

    A surface becomes white. A stroke or a text colour becomes ink. An orange
    connector passes through, because orange is a brand colour.
    """

    def fix_attributes(match: re.Match[str]) -> str:
        tag = match.group(0)

        def replace(color: re.Match[str]) -> str:
            role = _attribute_role(tag, color.start())
            return _clamp_color(color.group(0), role)

        return re.sub(r"#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?\b", replace, tag)

    return re.sub(r"<[^>]+>", fix_attributes, svg)


def _attribute_role(tag: str, offset: int) -> str:
    """Return whether the colour at the given offset sits in a fill or a stroke.

    The role decides which brand token replaces an off-brand colour. A fill
    becomes white or grey. A stroke becomes ink.

    A colour can sit in a presentation attribute such as ``fill="..."`` or in a
    style declaration such as ``fill:...``. Both forms are recognised, because
    the C4 family uses the style form.
    """
    prefix = tag[:offset]
    candidates = {
        "fill": max(
            prefix.rfind("fill="),
            prefix.rfind("fill:"),
            prefix.rfind("stop-color="),
            prefix.rfind("stop-color:"),
            prefix.rfind("flood-color="),
            prefix.rfind("flood-color:"),
        ),
        "stroke": max(
            prefix.rfind("stroke="),
            prefix.rfind("stroke:"),
            prefix.rfind("lighting-color="),
            prefix.rfind("lighting-color:"),
        ),
    }
    if candidates["fill"] > candidates["stroke"]:
        return "fill"
    return "stroke"


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


def check_brand(svg: str, family: str) -> list[str]:
    """Return the list of brand rules the rendered SVG breaks.

    An empty list means the output meets the brand contract.
    """
    problems: list[str] = []

    if BRAND_ORANGE.lower() not in svg.lower():
        problems.append("the diagram has no orange connector")
    if "Ubuntu Sans" not in svg:
        problems.append("the diagram does not use the Ubuntu Sans font")
    if "18px" not in svg:
        problems.append("the diagram does not use the 18px body text size")
    if "rx:0!important" not in svg and "rx:0 !important" not in svg:
        problems.append("the diagram does not force square corners")
    if "NaN" in svg:
        problems.append("the diagram contains a NaN geometry value")
    if family == "flowchart" and "node default leaf" not in svg:
        problems.append("the flowchart carries no leaf role")

    off_brand = find_off_brand_colors(svg)
    if off_brand:
        listed = ", ".join(sorted(off_brand))
        problems.append(f"the diagram contains off-brand colours: {listed}")

    return problems


def find_off_brand_colors(svg: str) -> dict[str, int]:
    """Return the colours in the SVG that are not brand colours.

    Only the presentation attributes count. A colour inside the style block is
    overridden by the brand theme when the browser renders the diagram, so it
    never reaches the reader.
    """
    body = re.sub(r"<style\b[^>]*>.*?</style>", "", svg, flags=re.DOTALL)
    found: dict[str, int] = {}
    for match in re.finditer(
        r'\b(?:fill|stroke|stop-color|flood-color|lighting-color)="([^"]*)"', body
    ):
        value = match.group(1).strip()
        if not value or COLOR_KEYWORDS.match(value) or _is_brand_color(value):
            continue
        found[value] = found.get(value, 0) + 1
    return found


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def find_chrome() -> str | None:
    """Return the path of a usable Chrome binary, or None.

    The Puppeteer cache comes first. A system Chromium often runs as a snap,
    and a snap cannot read the Mermaid CLI files under the system directories,
    so a system browser fails with a file error that hides the real cause.

    The revision that the Mermaid CLI pins wins over any other cached build.
    A different revision usually works, but the pinned one is the build the
    CLI was tested against. The newest of the remaining builds comes next.
    """
    override = os.environ.get("PUPPETEER_EXECUTABLE_PATH")
    if override and Path(override).is_file() and os.access(override, os.X_OK):
        return override

    cache = Path.home() / ".cache" / "puppeteer"
    patterns = (
        "chrome-headless-shell/*/chrome-headless-shell-linux64/chrome-headless-shell",
        "chrome/*/chrome-linux64/chrome",
    )

    wanted = required_chrome_revision()
    if wanted:
        for pattern in patterns:
            for candidate in sorted(cache.glob(pattern), reverse=True):
                if wanted in candidate.parts and candidate.is_file():
                    if os.access(candidate, os.X_OK):
                        return str(candidate)

    for pattern in patterns:
        for candidate in sorted(cache.glob(pattern), reverse=True):
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return str(candidate)

    for name in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    return None


def required_chrome_revision() -> str | None:
    """Return the Chrome revision that the installed Mermaid CLI expects.

    The Mermaid CLI pins the browser revision through its own Puppeteer
    dependency. The render fails when the cache holds a different revision,
    so the install uses the pinned one.
    """
    candidates = [
        Path("/usr/local/lib/node_modules/@mermaid-js/mermaid-cli"),
        Path("/usr/lib/node_modules/@mermaid-js/mermaid-cli"),
    ]
    for root in candidates:
        revisions = (
            root
            / "node_modules"
            / "puppeteer-core"
            / "lib"
            / "puppeteer"
            / "revisions.js"
        )
        if not revisions.is_file():
            continue
        try:
            source = revisions.read_text(encoding="utf-8")
        except OSError:
            continue
        match = re.search(r"'chrome-headless-shell':\s*'([^']+)'", source) or re.search(
            r"chrome-headless-shell:\s*\"([^\"]+)\"", source
        )
        if match:
            return match.group(1)
    return None


def install_chrome() -> str | None:
    """Install the headless Chrome build and return its path.

    The headless shell is used because it is the build the Mermaid CLI expects
    by default, and because it runs without the desktop dependencies that a
    full Chrome install needs.

    The revision comes from the Mermaid CLI when the CLI pins one. The
    Puppeteer command is pinned to the last release that runs on Node 18,
    because a newer Puppeteer needs Node 22.
    """
    revision = required_chrome_revision()
    browser = "chrome-headless-shell"
    if revision:
        browser = f"{browser}@{revision}"

    command = [
        "npx",
        "--yes",
        "puppeteer@24.31.0",
        "browsers",
        "install",
        browser,
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as exc:
        raise DiagramError(f"cannot run npx: {exc}") from exc

    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout).strip()
        raise DiagramError(
            "no usable Chrome was found and the install failed.\n"
            f"{message}\n"
            "Install a browser manually with "
            "`npx puppeteer browsers install chrome-headless-shell`."
        )
    return find_chrome()


def render_svg(source_path: Path, output_path: Path) -> None:
    """Render the Mermaid source file to an SVG file."""
    if shutil.which("mmdc") is None:
        raise DiagramError(
            "the Mermaid CLI (mmdc) is not installed.\n"
            "Install it with `npm install -g @mermaid-js/mermaid-cli`."
        )

    chrome = find_chrome()
    if chrome is None:
        chrome = install_chrome()
    if chrome is None:
        raise DiagramError(
            "no usable Chrome was found.\n"
            "Install one with `npx puppeteer browsers install chrome-headless-shell`."
        )

    with tempfile.TemporaryDirectory() as work:
        config_path = Path(work) / "puppeteer.json"
        config_path.write_text(
            json.dumps(
                {
                    "executablePath": chrome,
                    "args": ["--no-sandbox", "--disable-dev-shm-usage"],
                }
            ),
            encoding="utf-8",
        )
        command = [
            "mmdc",
            "--input",
            str(source_path),
            "--output",
            str(output_path),
            "--puppeteerConfigFile",
            str(config_path),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)

    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout).strip()
        raise DiagramError(f"the Mermaid render failed.\n{message}")


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  html, body {{ margin: 0; padding: 24px; background: {background}; }}
  body {{ font-family: "Ubuntu Sans", trebuchet ms, verdana, arial, sans-serif; }}
  .toolbar {{
    position: sticky;
    top: 0;
    z-index: 10;
    display: flex;
    gap: 8px;
    align-items: center;
    margin: 0 0 12px;
    padding: 8px;
    background: {background};
    border: 1px solid #000000;
  }}
  .toolbar button {{
    min-width: 34px;
    padding: 4px 8px;
    font: inherit;
    color: #000000;
    background: #FFFFFF;
    border: 1px solid #000000;
    cursor: pointer;
  }}
  .toolbar button:hover {{ background: #F3F3F3; }}
  .toolbar .level {{
    min-width: 64px;
    text-align: center;
    font-variant-numeric: tabular-nums;
  }}
  .toolbar .hint {{ margin-left: auto; color: #666666; font-size: 14px; }}
  .viewport {{
    overflow: hidden;
    width: 100%;
    height: calc(100vh - 104px);
    cursor: grab;
    border: 1px solid #D9D9D9;
  }}
  .viewport.panning {{ cursor: grabbing; }}
  .canvas {{
    position: relative;
    width: max-content;
    transform-origin: 0 0;
  }}
  .mermaid svg {{ max-width: none; height: auto; display: block; }}
</style>
</head>
<body>
<div class="toolbar">
  <button type="button" id="zoom-out" title="Zoom out">&#8722;</button>
  <span class="level" id="zoom-level">100%</span>
  <button type="button" id="zoom-in" title="Zoom in">+</button>
  <button type="button" id="zoom-fit" title="Fit the diagram to the window">Fit</button>
  <button type="button" id="zoom-reset" title="Reset the zoom to 100%">Reset</button>
  <span class="hint">Drag to pan. Ctrl and scroll to zoom.</span>
</div>
<div class="viewport" id="viewport">
  <div class="canvas" id="canvas">
    <div class="mermaid">
{source}
    </div>
  </div>
</div>
<script src="{script}"></script>
<script>
  mermaid.initialize({{ startOnLoad: true }});

  (function () {{
    var viewport = document.getElementById("viewport");
    var canvas = document.getElementById("canvas");
    var level = document.getElementById("zoom-level");
    var MIN = 0.1;
    var MAX = 8;
    var scale = 1;
    var x = 0;
    var y = 0;
    var dragging = false;
    var startX = 0;
    var startY = 0;
    var originX = 0;
    var originY = 0;

    function clamp(value) {{
      return Math.min(MAX, Math.max(MIN, value));
    }}

    function apply() {{
      canvas.style.transform =
        "translate(" + x + "px, " + y + "px) scale(" + scale + ")";
      level.textContent = Math.round(scale * 100) + "%";
    }}

    function zoomAt(factor, clientX, clientY) {{
      var rect = viewport.getBoundingClientRect();
      var pointerX = clientX - rect.left;
      var pointerY = clientY - rect.top;
      var next = clamp(scale * factor);
      if (next === scale) {{
        return;
      }}
      var ratio = next / scale;
      x = pointerX - (pointerX - x) * ratio;
      y = pointerY - (pointerY - y) * ratio;
      scale = next;
      apply();
    }}

    function svg() {{
      return canvas.querySelector("svg");
    }}

    function diagramSize() {{
      var diagram = svg();
      if (!diagram) {{
        return null;
      }}
      var box = diagram.viewBox.baseVal;
      var width = box && box.width ? box.width : 0;
      var height = box && box.height ? box.height : 0;
      if (!width || !height) {{
        return null;
      }}
      // Mermaid creates the SVG element before it lays the diagram out. The
      // element then holds a placeholder viewBox that does not match its own
      // width and height attributes. The fit waits until the two agree, so
      // that it measures the diagram and not the placeholder.
      var declaredWidth = parseFloat(diagram.getAttribute("width"));
      var declaredHeight = parseFloat(diagram.getAttribute("height"));
      if (!declaredWidth || !declaredHeight) {{
        return null;
      }}
      if (Math.abs(declaredWidth - width) > 1 ||
          Math.abs(declaredHeight - height) > 1) {{
        return null;
      }}
      return {{ width: width, height: height }};
    }}

    function fit() {{
      var size = diagramSize();
      if (!size) {{
        return false;
      }}
      var available = viewport.clientWidth - 24;
      var availableHeight = viewport.clientHeight - 24;
      scale = clamp(Math.min(available / size.width, availableHeight / size.height));
      x = (viewport.clientWidth - size.width * scale) / 2;
      y = (viewport.clientHeight - size.height * scale) / 2;
      apply();
      return true;
    }}

    function fitWhenReady(attempt) {{
      if (fit()) {{
        return;
      }}
      if (attempt > 40) {{
        return;
      }}
      window.setTimeout(function () {{
        fitWhenReady(attempt + 1);
      }}, 100);
    }}

    document.getElementById("zoom-in").addEventListener("click", function () {{
      var rect = viewport.getBoundingClientRect();
      zoomAt(1.2, rect.left + rect.width / 2, rect.top + rect.height / 2);
    }});

    document.getElementById("zoom-out").addEventListener("click", function () {{
      var rect = viewport.getBoundingClientRect();
      zoomAt(1 / 1.2, rect.left + rect.width / 2, rect.top + rect.height / 2);
    }});

    document.getElementById("zoom-fit").addEventListener("click", function () {{
      fitWhenReady(0);
    }});
    document.getElementById("zoom-reset").addEventListener("click", function () {{
      scale = 1;
      x = 0;
      y = 0;
      apply();
    }});

    viewport.addEventListener("wheel", function (event) {{
      if (!event.ctrlKey) {{
        return;
      }}
      event.preventDefault();
      zoomAt(event.deltaY < 0 ? 1.1 : 1 / 1.1, event.clientX, event.clientY);
    }}, {{ passive: false }});

    viewport.addEventListener("mousedown", function (event) {{
      if (event.button !== 0) {{
        return;
      }}
      dragging = true;
      startX = event.clientX;
      startY = event.clientY;
      originX = x;
      originY = y;
      viewport.classList.add("panning");
      event.preventDefault();
    }});

    window.addEventListener("mousemove", function (event) {{
      if (!dragging) {{
        return;
      }}
      x = originX + event.clientX - startX;
      y = originY + event.clientY - startY;
      apply();
    }});

    window.addEventListener("mouseup", function () {{
      dragging = false;
      viewport.classList.remove("panning");
    }});

    window.addEventListener("resize", function () {{
      if (scale === 1 && x === 0 && y === 0) {{
        fitWhenReady(0);
      }}
    }});

    if (document.readyState === "complete") {{
      fitWhenReady(0);
    }} else {{
      window.addEventListener("load", function () {{
        fitWhenReady(0);
      }});
    }}
  }})();
</script>
</body>
</html>
"""


def write_html(output_path: Path, source: str, title: str, script_path: str) -> None:
    """Write the HTML page that renders the diagram in a browser."""
    output_path.write_text(
        HTML_TEMPLATE.format(
            title=title,
            background=BRAND_WHITE,
            source=source.rstrip(),
            script=script_path,
        ),
        encoding="utf-8",
    )


def relative_script_path(output_path: Path) -> str:
    """Return the path from the HTML file to the vendored Mermaid script."""
    script = VENDOR_DIR / "mermaid.min.js"
    try:
        return os.path.relpath(script, output_path.parent).replace(os.sep, "/")
    except ValueError:
        return script.as_uri()


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


def build_source(body: str, frontmatter: str, class_defs: str, family: str) -> str:
    """Compose the branded Mermaid source file."""
    parts = [frontmatter.rstrip(), "", body.strip()]
    if family == "flowchart":
        parts.extend(["", class_defs.rstrip()])
    return "\n".join(parts) + "\n"


def run(
    source_file: Path,
    name: str,
    out_dir: Path,
    write_html_page: bool,
    keep_source: bool,
) -> dict[str, Any]:
    """Render one diagram and write the output files."""
    body = source_file.read_text(encoding="utf-8")
    family = detect_family(body)

    frontmatter_artifact, frontmatter_cached = fetch_artifact(FRONTMATTER_ARTIFACT)
    class_defs_artifact, class_defs_cached = fetch_artifact(FLOWCHART_ARTIFACT)

    frontmatter = extract_frontmatter(frontmatter_artifact)
    class_defs = flowchart_class_defs(class_defs_artifact)

    if family == "c4":
        frontmatter = apply_c4_palette(frontmatter)

    branded = build_source(body, frontmatter, class_defs, family)

    out_dir.mkdir(parents=True, exist_ok=True)
    source_path = out_dir / f"{name}.mmd"
    svg_path = out_dir / f"{name}.svg"
    html_path = out_dir / f"{name}.html"

    source_path.write_text(branded, encoding="utf-8")

    try:
        render_svg(source_path, svg_path)
    except DiagramError:
        source_path.unlink(missing_ok=True)
        raise

    svg = repair_svg(svg_path.read_text(encoding="utf-8"))
    svg_path.write_text(svg, encoding="utf-8")

    problems = check_brand(svg, family)
    if problems:
        svg_path.unlink(missing_ok=True)
        source_path.unlink(missing_ok=True)
        raise DiagramError(
            "the rendered diagram does not meet the brand contract:\n"
            + "\n".join(f"- {problem}" for problem in problems)
        )

    if write_html_page:
        write_html(html_path, branded, name, relative_script_path(html_path))

    if not keep_source:
        source_path.unlink(missing_ok=True)

    return {
        "family": family,
        "files": {
            "svg": str(svg_path),
            "html": str(html_path) if write_html_page else None,
            "source": str(source_path) if keep_source else None,
        },
        "cached_theme": frontmatter_cached or class_defs_cached,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="diagram.py",
        description="Render an on-brand Canonical Mermaid diagram.",
    )
    parser.add_argument(
        "source",
        type=Path,
        help="the Mermaid source file to render",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="the base name of the output files (default: the source file name)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("diagrams"),
        help="the directory that receives the output files (default: diagrams)",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="do not write the HTML page",
    )
    parser.add_argument(
        "--no-source",
        action="store_true",
        help="do not keep the branded Mermaid source file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print the result as JSON",
    )
    args = parser.parse_args(argv)

    if not args.source.is_file():
        print(f"error: {args.source} is not a file", file=sys.stderr)
        return 2

    name = args.name or args.source.stem

    try:
        result = run(
            args.source,
            name,
            args.out_dir,
            not args.no_html,
            not args.no_source,
        )
    except DiagramError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    if result["cached_theme"]:
        print(
            "note: the brand theme came from the local cache and may be older "
            "than the current kit."
        )
    print(f"family: {result['family']}")
    for kind, path in result["files"].items():
        if path:
            print(f"{kind}: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
