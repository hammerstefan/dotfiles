"""The tests of the builder of the options page.

The tests do not render a diagram. They check the spec, the Mermaid source
that the script writes, and the page that the script builds. The render is
covered by running the script on the example spec.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).absolute().parent.parent / "scripts/build_options_page.py"

spec = importlib.util.spec_from_file_location("build_options_page", SCRIPT)
builder = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(builder)

EXAMPLE = Path(__file__).absolute().parent.parent / "examples/fence-options.json"


def small_spec() -> dict:
    """A spec with two options, one of them with two bands."""
    return {
        "title": "Which layer restores the placement",
        "question": "Which layer restores the placement?",
        "situation": ["The service kills the verb at its limit."],
        "actors": [{"name": "Control service", "role": "runs the verb."}],
        "participants": [
            {"id": "S", "name": "Control service"},
            {"id": "P", "name": "Fence placement"},
        ],
        "options": [
            {
                "id": "option-a",
                "name": "Option A",
                "headline": "The service applies the fence",
                "restores": "The control service",
                "changes": "The service runs the apply.",
                "leaves_open": "A run where the command is killed.",
                "what": "The service runs the apply as a separate command.",
                "window": "The window ends when the apply finishes.",
                "why": ["The service knows the verb was killed."],
                "diagram": {
                    "highlight_label": "THIS OPTION ADDS THE RESTORE",
                    "highlight_note_over": "S,P",
                    "prefix": ["S->>P: release the placement"],
                    "steps": ["S->>P: the placement is restored"],
                },
            },
            {
                "id": "option-b",
                "name": "Option B",
                "headline": "The command applies the fence",
                "restores": "The fence command",
                "changes": "The command waits for the rebuild.",
                "leaves_open": "A run where the command is killed.",
                "diagram": {
                    "prefix": ["S->>P: release the placement"],
                    "bands": [
                        {
                            "highlight_label": "THE FIRST CHANGE",
                            "steps": ["S->>P: the limit grows"],
                        },
                        {
                            "highlight_label": "THE SECOND CHANGE",
                            "steps": ["S->>P: the placement is restored"],
                        },
                    ],
                },
            },
        ],
        "answer": {"summary": "The control service restores it."},
        "not_verified": ["What the command did after the limit."],
    }


class SpecTests(unittest.TestCase):
    """The spec has to hold what the page needs."""

    def test_a_full_spec_has_no_problems(self) -> None:
        self.assertEqual(builder.check_spec(small_spec()), [])

    def test_the_example_spec_has_no_problems(self) -> None:
        self.assertEqual(builder.check_spec(json.loads(EXAMPLE.read_text())), [])

    def test_a_spec_without_a_title_is_refused(self) -> None:
        spec = small_spec()
        del spec["title"]
        self.assertIn("the spec needs a title", builder.check_spec(spec))

    def test_a_spec_without_options_is_refused(self) -> None:
        spec = small_spec()
        spec["options"] = []
        problems = builder.check_spec(spec)
        self.assertIn("the spec needs a list of options", problems)

    def test_an_option_without_a_diagram_is_refused(self) -> None:
        spec = small_spec()
        del spec["options"][0]["diagram"]
        self.assertIn("option 1 needs a diagram or a source", builder.check_spec(spec))

    def test_an_option_without_a_band_label_is_refused(self) -> None:
        spec = small_spec()
        del spec["options"][0]["diagram"]["highlight_label"]
        self.assertIn("option 1 needs a highlight_label", builder.check_spec(spec))

    def test_an_option_without_steps_is_refused(self) -> None:
        spec = small_spec()
        spec["options"][0]["diagram"]["steps"] = []
        self.assertIn("option 1 needs a list of steps", builder.check_spec(spec))

    def test_a_repeated_id_is_refused(self) -> None:
        spec = small_spec()
        spec["options"][1]["id"] = spec["options"][0]["id"]
        self.assertIn("option 2 repeats the id option-a", builder.check_spec(spec))

    def test_an_id_with_wrong_characters_is_refused(self) -> None:
        spec = small_spec()
        spec["options"][0]["id"] = "Option A"
        self.assertIn(
            "option 1 needs an id of lower case letters and digits",
            builder.check_spec(spec),
        )


class SourceTests(unittest.TestCase):
    """The Mermaid source of an option."""

    def test_the_band_holds_the_steps_of_the_option(self) -> None:
        spec = small_spec()
        source = builder.mermaid_source(spec, spec["options"][0])
        self.assertIn("    rect rgb(255, 233, 219)\n", source)
        self.assertIn("    Note over S,P: THIS OPTION ADDS THE RESTORE\n", source)
        self.assertIn("    S->>P: the placement is restored\n", source)
        self.assertTrue(source.rstrip().endswith("end"))

    def test_the_prefix_holds_the_shared_steps(self) -> None:
        spec = small_spec()
        source = builder.mermaid_source(spec, spec["options"][0])
        self.assertIn("    S->>P: release the placement\n", source)
        self.assertLess(
            source.index("release the placement"),
            source.index("rect rgb"),
            "the shared steps come before the band",
        )

    def test_several_bands_hold_several_changes(self) -> None:
        spec = small_spec()
        source = builder.mermaid_source(spec, spec["options"][1])
        self.assertEqual(source.count("    rect rgb(255, 233, 219)\n"), 2)
        self.assertIn("    Note over S,P: THE FIRST CHANGE\n", source)
        self.assertIn("    Note over S,P: THE SECOND CHANGE\n", source)

    def test_the_baseline_note_names_the_shared_steps(self) -> None:
        spec = small_spec()
        spec["baseline_note"] = "the same in every option"
        source = builder.mermaid_source(spec, spec["options"][0])
        self.assertIn("    Note over S,P: the same in every option\n", source)

    def test_the_participants_come_from_the_spec(self) -> None:
        spec = small_spec()
        source = builder.mermaid_source(spec, spec["options"][0])
        self.assertIn("    participant S as Control service\n", source)
        self.assertIn("    participant P as Fence placement\n", source)


class PageTests(unittest.TestCase):
    """The page holds every option and its description."""

    def setUp(self) -> None:
        self.spec = small_spec()
        self.options = []
        for option in self.spec["options"]:
            rendered = dict(option)
            rendered["svg_path"] = None
            self.options.append(rendered)
        self.page = builder.build_page(self.spec, self.options)

    def test_the_page_holds_the_title_and_the_question(self) -> None:
        self.assertIn("<h1>Which layer restores the placement</h1>", self.page)
        self.assertIn("Which layer restores the placement?", self.page)

    def test_the_page_holds_a_section_for_every_option(self) -> None:
        self.assertIn("<h2>Option A: The service applies the fence</h2>", self.page)
        self.assertIn("<h2>Option B: The command applies the fence</h2>", self.page)

    def test_the_page_holds_the_comparison_table(self) -> None:
        self.assertIn("<table>", self.page)
        self.assertIn("<td>The control service</td>", self.page)
        self.assertIn("<td>The fence command</td>", self.page)

    def test_the_page_holds_the_description_of_every_option(self) -> None:
        self.assertIn("The service runs the apply as a separate command.", self.page)
        self.assertIn("<h3>What it does to the window</h3>", self.page)

    def test_the_page_holds_the_label_of_every_band(self) -> None:
        self.assertIn("THIS OPTION ADDS THE RESTORE", self.page)
        self.assertIn("THE FIRST CHANGE", self.page)
        self.assertIn("THE SECOND CHANGE", self.page)

    def test_the_page_holds_the_answer_and_what_was_not_verified(self) -> None:
        self.assertIn("The control service restores it.", self.page)
        self.assertIn("What the command did after the limit.", self.page)

    def test_the_page_needs_no_javascript(self) -> None:
        self.assertNotIn("<script", self.page)


class BuildTests(unittest.TestCase):
    """The run writes the files of the page."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name) / "out"
        self.spec_path = Path(self.tmp.name) / "spec.json"
        self.spec_path.write_text(json.dumps(small_spec()), encoding="utf-8")
        self.original = builder.render_diagram
        builder.render_diagram = self.fake_render
        self.addCleanup(self.restore)

    def restore(self) -> None:
        builder.render_diagram = self.original

    def fake_render(self, source_path: Path, name: str, out_dir: Path) -> Path:
        svg = out_dir / f"{name}.svg"
        svg.write_text(
            f'<svg id="{name}"><text>{source_path.stem}</text></svg>', encoding="utf-8"
        )
        return svg

    def test_the_run_writes_the_page_and_the_diagrams(self) -> None:
        code = builder.build(self.spec_path, self.directory, False)
        self.assertEqual(code, 0)
        self.assertTrue((self.directory / "options.html").is_file())
        self.assertTrue((self.directory / "option-a.mmd").is_file())
        self.assertTrue((self.directory / "option-a.svg").is_file())
        self.assertTrue((self.directory / "option-b.mmd").is_file())

    def test_the_page_holds_the_rendered_diagram(self) -> None:
        builder.build(self.spec_path, self.directory, False)
        page = (self.directory / "options.html").read_text(encoding="utf-8")
        self.assertIn('<svg id="option-a">', page)
        self.assertEqual(page.count("<svg"), 2)

    def test_the_run_writes_nothing_outside_the_directory(self) -> None:
        before = set(Path(self.tmp.name).iterdir())
        builder.build(self.spec_path, self.directory, False)
        after = set(Path(self.tmp.name).iterdir())
        self.assertEqual(after - before, {self.directory})


class DirectoryTests(unittest.TestCase):
    """Every run gets a directory of its own."""

    def test_two_runs_never_share_a_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            first = builder.unique_dir(parent, "options")
            first.mkdir()
            second = builder.unique_dir(parent, "options")
            self.assertNotEqual(first, second)

    def test_the_directory_name_holds_the_title(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            name = builder.unique_dir(Path(tmp), builder.slug_of("Which layer?")).name
            self.assertTrue(name.startswith("diagram-options-which-layer-"))

    def test_the_slug_holds_no_unsafe_characters(self) -> None:
        slug = builder.slug_of("../../etc/passwd / Option")
        self.assertNotIn("/", slug)
        self.assertNotIn("..", slug)


if __name__ == "__main__":
    unittest.main()
