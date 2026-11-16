---
name: diagram-options
description: Build one HTML page that compares several options of a decision, with a diagram of each option and the steps that the option changes marked in a shaded band. Use this skill whenever a decision has two or more candidate directions, layers, or implementations, and the reader needs to see how they differ. Use it when the user asks for "a comparison of the options", "one page for the options", "show the options side by side", "highlight what each option changes", "a diagram per option", or when they ask for a decision write-up that holds pictures of the alternatives. Do not use it for a single diagram with no alternatives, and do not use it for a chart of measured data that belongs in a spreadsheet.
compatibility: Requires Python 3. The Canonical brand theme needs the diagram skill and the GitHub CLI (gh) with access to the private canonical/mermaid-brand-kit repository, and a Chrome build. Without the diagram skill, the Mermaid CLI (mmdc) renders the diagrams with the default style.
---

# Diagram options

Build one page that holds the options of a decision, a description of each
option, and a diagram of each option with the steps that the option changes in
a shaded band.

The page is the artifact. A reader compares the options in one place, sees
what each option changes, and reads why.

## Before you start

Check that the tools are present. Run each command and stop if one fails.

```bash
python3 --version
mmdc --version
gh auth status
```

The script needs the `diagram` skill for the Canonical brand theme. It falls
back to the Mermaid CLI on its own when the skill is not installed, and the
page says that the theme is missing.

## Step 1: Write the spec

The spec is one JSON object. Write it to a file outside the repository, in
`~/tmp`, because the spec is temporary and the page is the artifact.

```json
{
  "title": "Which layer restores the fence placement",
  "subtitle": "A decision ticket for the map.",
  "question": "The question the page answers.",
  "baseline_note": "these steps are the same in every option",
  "legend": "The shaded band holds the steps that the option changes.",
  "situation": ["What happens today, one line per fact."],
  "participants": [{"id": "S", "name": "Control service"}],
  "actors": [{"name": "Control service", "role": "runs the verb."}],
  "options": [
    {
      "id": "option-a",
      "name": "Option A",
      "headline": "The headline of the option.",
      "restores": "The short answer for the table.",
      "changes": "The short answer for the table.",
      "leaves_open": "The short answer for the table.",
      "what": "A paragraph that says what the option does.",
      "window": "A paragraph that says what it does to the window.",
      "why": ["One reason per line."],
      "diagram": {
        "highlight_label": "THE LABEL OF THE BAND",
        "highlight_note_over": "S,P",
        "prefix": ["The steps that every option shares."],
        "steps": ["The steps that this option changes."]
      }
    }
  ],
  "answer": {"summary": "The answer.", "detail": "The reason for the answer."},
  "not_verified": ["What no run has tested."]
}
```

The fields that the page needs:

- `title`, `question`, `situation`, `actors`, `answer`, and at least one option.
- One option needs `id`, `name`, `headline`, and a diagram.
- `id` holds lower case letters, digits, and dashes. It names the files.
- `restores`, `changes`, and `leaves_open` are the three short columns of the
  comparison table at the top of the page.
- `what`, `window`, and `why` are the prose of the option.

The diagram of an option takes one of two forms:

- `diagram` holds `prefix`, `steps`, and `highlight_label`. The script writes
  the Mermaid source and puts the steps in a shaded band that carries the
  label. This is the usual form.
- `diagram` holds `prefix` and `bands`. Each band holds `steps` and its own
  `highlight_label`, so an option that changes two separate places gets two
  bands.
- `source` names a Mermaid file that is already written. The script uses it
  as it is, and the band is in that file.

## Step 2: Build the page

```bash
python3 "<skill-directory>/scripts/build_options_page.py" <spec.json>
```

The script writes a fresh directory under `~/tmp`, named
`diagram-options-<slug>-<timestamp>`, and holds:

- `<option-id>.mmd` — the branded Mermaid source of every option.
- `<option-id>.svg` — the rendered diagram of every option.
- `options.html` — the page, with the diagram of every option inlined as SVG,
  so the page needs no JavaScript and opens in any browser.

Pass `--out-dir <directory>` to choose the directory, and `--open` to open the
page in the browser of the host.

Nothing is written to the repository. The directory under `~/tmp` is the whole
artifact, and it can be removed with `rm -rf`.

## Step 3: Check the result

Read the page. Check that:

- every option has its section, its description, and its diagram
- the band holds the steps that the option changes, and the label names the
  change
- the comparison table names the same options as the sections
- no label overlaps another label, and no text is cut off at the edge

Render a diagram to a PNG and read it, when a diagram holds many steps:

```bash
mmdc --input <directory>/<option-id>.mmd --output /tmp/<option-id>.png --backgroundColor white
```

## Report the result

Tell the user the path of the page and the path of the directory. Name the
options the page holds. State what was not verified, when the spec says so.

## Notes

- The band is a `rect` in the Mermaid source, so the steps that an option
  changes read as one block. The colour is a pale tint of the accent colour
  of the page.
- The note of the band names the change, so a reader who sees only the
  diagram knows what the option does.
- The `baseline_note` at the top of the page marks the steps that every
  option shares, so the eye goes to the difference.
- The script checks the spec before it writes anything. It writes nothing and
  exits with code 2 when the spec does not hold what the page needs, and the
  message names every problem.
- The script never writes outside the directory it chose, and two runs never
  share a directory.
- The example spec in `examples/fence-options.json` is a complete spec of a
  four-option decision. Copy it and edit it as the starting point.
