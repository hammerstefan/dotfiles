---
name: diagram
description: Create an on-brand Canonical Mermaid diagram from a description, a document, or an existing Mermaid source. The skill fetches the brand theme from the canonical/mermaid-brand-kit. It renders the diagram with the stock Mermaid CLI. It writes the source, the SVG, and a live HTML page. Use when the user asks for a diagram, a chart, an architecture picture, a sequence diagram, a state machine, or a class model. Also use for a C4 context, an entity relationship diagram, or a Gantt chart. Also use when the user says "draw this", "diagram this", or "make a picture of". Do not trigger for a chart of measured data that belongs in a spreadsheet. Do not trigger for a bitmap or a photograph. Do not trigger for an image that already exists.
compatibility: Requires Python 3, the Mermaid CLI (mmdc), the GitHub CLI (gh) with access to the private canonical/mermaid-brand-kit repository, and a Chrome build.
---

# Diagram

Create an on-brand Canonical Mermaid diagram. The workflow has four steps:
choose the family, author the source, render it, and check the result.

## Before you start

Check that the tools are present. Run each command and stop if one fails.

```bash
python3 --version
mmdc --version
gh auth status
```

The GitHub CLI must read the private `canonical/mermaid-brand-kit` repository.
The script fetches the brand theme from that repository at run time. It never
clones the repository and it never installs a package.

## Step 1: Choose the family

Choose the Mermaid family from the meaning of the content. Do not default to a
flowchart. A flowchart says "these things connect in this direction". When the
content does not say that, another family says it better.

| The content describes | Use |
|---|---|
| Steps, a flow, a pipeline, a dependency | `flowchart` |
| A conversation between actors over time | `sequence` |
| States and the transitions between them | `state` |
| Types with attributes and their relationships | `class` |
| People, systems, and containers at one or two levels | `c4` |
| Entities and their cardinality | `er` |
| Work over time with durations | `gantt` |

These seven families are the supported set. The script rejects any other
family.

Ask the user when no family fits. Do not force a poor fit. A flowchart that
invents arrows misrepresents the content, and a sequence diagram for a static
inventory misrepresents it in a different way.

## Step 2: Author the source

Write the Mermaid source to a file. Keep it free of frontmatter, because the
script adds the brand theme.

**Never invent structure.** The source must contain only the nodes, the
connections, and the labels that the content actually states. An arrow that
the content does not state is a false claim about the system. If the content
leaves a relationship ambiguous, leave it out and tell the user.

For a flowchart, use the brand roles on every node:

| Role | Use for | Looks like |
|---|---|---|
| `:::leaf` | A normal item, a component, a service | Grey fill, thin black border |
| `:::child` | The same as `leaf` | Grey fill, thin black border |
| `:::panel` | A group that holds other items | Transparent, thin black border, bold label |
| `:::parent` | The same as `panel` | Transparent, thin black border, bold label |
| `:::section` | A top-level group | Transparent, thick black border, bold label |
| `:::annotation` | A note that explains, not a thing | No border, grey text |
| `:::highlight` | The one thing to look at | Black fill, white text |

Use `:::highlight` at most once per diagram. It marks a single focus.

Never use orange as a box colour. Orange is a connector colour only.

## Step 3: Render it

```bash
python3 "<skill-directory>/scripts/diagram.py" <source.mmd> --name <name> --out-dir diagrams
```

The script writes three files into the output directory:

- `<name>.mmd` — the branded source, with the theme inlined. Keep it, so the
  diagram can be edited and re-rendered later.
- `<name>.svg` — the rendered diagram.
- `<name>.html` — a page that renders the diagram live in a browser.

The script writes nothing and exits with a non-zero code in three cases. It
cannot fetch the theme. The render fails. The output does not meet the brand
contract. Read the error message. It names the problem.

Use `--no-html` to skip the HTML page. Use `--no-source` to drop the source
file. Use `--json` to print the result as JSON.

## Step 4: Check the result

The script checks the rendered SVG against the brand contract. That check
covers colour, font, text size, corner shape, and geometry. It cannot see a
layout problem, so look at the picture as well.

Render a PNG and read it:

```bash
mmdc --input diagrams/<name>.mmd --output /tmp/<name>.png --backgroundColor white
```

Then read `/tmp/<name>.png` with the read tool. Check that:

- no label overlaps another label or a line
- no text is cut off at the edge of the diagram
- the nodes are in a sensible order for the content
- the highlight lands on the element the user cares about, if one exists

Fix the source and render again when the layout is wrong. Do not report a
diagram that you have not looked at.

## Report the result

Tell the user the paths of the SVG and the HTML page. Name the family you
used. State anything that is missing, such as a relationship you left out
because the content did not state it.

## Notes on the brand theme

The theme comes from the private `canonical/mermaid-brand-kit` repository. The
script reads two generated files from it. Three properties of those files
break a naive pipeline, and the script handles all three:

1. The frontmatter file starts with a `#` comment before the opening `---`
   fence. Prepended as it is, that comment becomes diagram text.
2. The theme CSS contains `---` inside it. The closing fence must be found by
   matching a whole line.
3. The flowchart class definitions are valid only in a flowchart. Mermaid
   rejects them in every other family.

The script caches the last successful fetch under
`~/.cache/opencode/diagram/`. It uses the cache only when the fetch fails,
and it says so when it does. A cached theme can be older than the current one.

## Known limits

- The C4 family draws the person as a plain circle. The brand kit replaces it
  with a canonical person icon, and that replacement needs the kit's own
  renderer.
- The Mermaid CLI in Mermaid 12 does not ship the ELK layout engine, so a
  flowchart uses the Dagre layout. The brand kit prefers ELK.
- The HTML page loads the Mermaid JavaScript from `vendor/mermaid.min.js`
  inside this skill directory. Move the page and it stops working, because the
  script reference is relative.
- The theme does not embed the Ubuntu Sans font file. A machine without
  Ubuntu Sans installed falls back to another sans-serif face.
- The script needs a Chrome build that matches the revision the Mermaid CLI
  pins. It reads that revision from the installed CLI and installs the exact
  build when the Puppeteer cache does not hold it.

## Tests

```bash
cd "<skill-directory>" && python3 -m unittest discover -s tests
```
