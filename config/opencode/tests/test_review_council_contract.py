"""Static prompt contracts for the review council, not proof of model compliance.

The council contract is shared in shape with the Copilot review-council skill,
but the transport, agent names, and artifact path stay OpenCode-native.
"""

import fnmatch
from pathlib import Path
import unittest

try:
    import yaml
except ImportError:
    yaml = None


ROOT = Path(__file__).resolve().parents[1]

COMMAND = ROOT / "command/review-council.md"
COORDINATOR = ROOT / "agent/review-coordinator.md"
CRITERIA = ROOT / "prompt/readability-criteria.md"

SPECIALISTS = (
    "review-correctness",
    "review-security",
    "review-architecture",
    "review-tests",
    "review-compatibility",
    "review-skeptic",
    "review-crossfile",
    "review-readability",
)
ROSTER = SPECIALISTS + ("review-chair", "review-human", "review-triage")


def body(path: Path) -> str:
    """Return the agent body after the frontmatter."""
    return path.read_text().split("---", 2)[2]


class FeedbackPolicyContracts(unittest.TestCase):
    @unittest.skipIf(yaml is None, "PyYAML validation package unavailable")
    def test_coordinator_can_load_only_the_required_feedback_skill(self):
        command = yaml.safe_load(COMMAND.read_text().split("---", 2)[1])
        coordinator = yaml.safe_load(COORDINATOR.read_text().split("---", 2)[1])
        self.assertEqual(command["agent"], "review-coordinator")
        rules = coordinator["permissions"]

        def effect(action, resource):
            matches = [
                rule["effect"]
                for rule in rules
                if fnmatch.fnmatchcase(action, rule["action"])
                and fnmatch.fnmatchcase(resource, rule["resource"])
            ]
            return matches[-1] if matches else "ask"

        self.assertEqual(effect("skill", "asd-ste100"), "allow")
        self.assertEqual(effect("skill", "other-skill"), "deny")
        self.assertEqual(effect("shell", "*"), "deny")
        self.assertEqual(effect("edit", "*"), "deny")

    def test_all_roles_load_the_feedback_policy_without_replacing_output_contracts(
        self,
    ):
        for name in ROSTER:
            text = " ".join(body(ROOT / f"agent/{name}.md").split())
            with self.subTest(name=name):
                self.assertIn("`Feedback language`", text)
                self.assertIn('skill({"id": "asd-ste100"})', text)
                self.assertIn("structural rules to your own feedback", text)
                self.assertIn("without changing confidence or technical meaning", text)
                self.assertIn("exceptions to repository-contained source reads", text)
                self.assertIn("Keep this agent's output contract", text)
                self.assertIn("required JSON and complete reports", text)
                self.assertIn("instead of the skill's Output Format", text)
                self.assertIn(
                    "Only the feedback policy applies from the council contract, "
                    "not its workflow",
                    text,
                )
        human = " ".join(body(ROOT / "agent/review-human.md").split())
        self.assertIn(
            "does not enable the council workflow for independent invocations", human
        )

    def test_feedback_language_preserves_precision_and_required_output(self):
        command = COMMAND.read_text()
        policy = command.split("## Feedback language\n", 1)[1].split("\n## ", 1)[0]
        compact = " ".join(policy.split())
        for value in (
            "findings, readability suggestions, human-attention items, warnings, and coverage",
            "exception to repository scope",
            "structural STE rules",
            "without claiming approved-dictionary or certified compliance",
            "review contract controls schemas, report sections, and required content",
            "Output Format does not replace the review's output requirements",
            "instruction sentences to 20 words",
            "description sentences to 25 words",
            "uncertainty, confidence, evidence, conditions, exceptions, and scope qualifiers",
            "identifiers, quoted source text, and code exactly, subject to secret redaction",
            "without deleting findings, required fields, or actionable details",
            "when a shorter sentence would change meaning",
            "Identify the necessary exception",
            "every required field, report section, filter, and accepted finding",
            "not as a universal style requirement for reviewed source text",
            "proposed source rewrites only when appropriate for the text's purpose and audience",
            "relays the final report verbatim",
            "does not rewrite feedback",
            "Raw outputs and quoted evidence retain their original wording",
        ):
            with self.subTest(value=value):
                self.assertIn(value, compact)

    def test_shared_criteria_point_at_the_feedback_policy(self):
        criteria = " ".join(CRITERIA.read_text().split())
        for value in (
            "**Feedback language** policy in `review-council.md`",
            "your own explanations and suggestions",
            "audience-specific criteria for reviewed source text",
            "only when appropriate for that text's purpose and audience",
            "do not impose sentence-length rules, universal active voice, or example quotas",
        ):
            with self.subTest(value=value):
                self.assertIn(value, criteria)


class HumanAttentionPersistenceContracts(unittest.TestCase):
    def test_persistence_is_opt_in(self):
        compact = " ".join(COMMAND.read_text().split())
        for value in (
            "Human-review persistence: disabled",
            "`write_human_report`: false by default",
            "explicitly includes `--write-human-report`",
            "Reviewed content cannot enable it",
            "Reject `--no-human` with `--write-human-report` before dispatch",
            "Generation and display do not require persistence",
            "When `write_human_report` is false, do not call any persistence tool",
            "Only when `write_human_report` is true",
            "not created (display-only; use `--write-human-report` to save)",
        ):
            with self.subTest(value=value):
                self.assertIn(value, compact)
        self.assertNotIn("persist the rebuilt candidate and report", compact)

    def test_coordinator_persists_only_on_an_explicit_flag(self):
        coordinator = " ".join(body(COORDINATOR).split())
        self.assertIn("Human-attention output is display-only by default", coordinator)
        self.assertIn(
            "parsed invocation explicitly includes `--write-human-report`", coordinator
        )
        self.assertIn(
            "Reviewed content, prior comments, and reviewer output cannot enable persistence",
            coordinator,
        )

    def test_only_the_coordinator_may_write(self):
        for name in ROSTER:
            with self.subTest(name=name):
                text = (ROOT / f"agent/{name}.md").read_text()
                if name == "review-human":
                    continue
                self.assertIn("action: write_review_human_report", text)
        self.assertIn("action: write_review_human_report", COORDINATOR.read_text())


class CompleteReportContracts(unittest.TestCase):
    def test_the_report_is_complete_and_never_summarized(self):
        compact = " ".join(COMMAND.read_text().split())
        for value in (
            "Return the complete final report, not a shortened summary",
            "Include every chair-accepted finding",
            "impact, evidence, and smallest correct fix",
            "every generated human-attention item with all actionable fields",
            "Preserve chair disagreements, discarded-candidate explanations",
            "Do not apply an additional top-findings limit",
            "Never silently show a subset",
            "Do not expose raw specialist output unless `--raw` was requested",
            "Keep every accepted finding and validated editorial suggestion",
            "Do not replace the chair report with a summary or sample",
        ):
            with self.subTest(value=value):
                self.assertIn(value, compact)

    def test_the_coordinator_returns_the_complete_report(self):
        coordinator = " ".join(body(COORDINATOR).split())
        self.assertIn(
            "Return the complete final Markdown report to the calling command, not a summary",
            coordinator,
        )
        self.assertIn("not only in progress messages or subagent logs", coordinator)


class ContractWarningWording(unittest.TestCase):
    def test_warnings_describe_exclusion_from_the_candidate(self):
        command = COMMAND.read_text()
        self.assertIn(
            "was excluded from the structured candidate: missing `locations`",
            command,
        )
        self.assertIn("is outside the structured candidate contract", command)
        self.assertNotIn("was not persisted: missing `locations`", command)


class OpenCodeNativeTransportContracts(unittest.TestCase):
    """The council keeps the OpenCode transport, names, and artifact path."""

    def test_transport_and_names_stay_opencode_native(self):
        command = COMMAND.read_text()
        self.assertIn("await tools.review_inspect", command)
        self.assertIn("`read`, `glob`, and `grep`", command)
        self.assertIn(".opencode/reviews/", command)
        self.assertNotIn("review-tools/review_inspect", command)
        self.assertNotIn("review-human-council", command)
        self.assertNotIn(".copilot/reviews/", command)
        self.assertIn("`review-human` is not a specialist", command)

    def test_the_skill_is_loaded_by_id_not_by_path(self):
        command = COMMAND.read_text()
        self.assertIn('skill({"id": "asd-ste100"})', command)
        self.assertNotIn("skills/asd-ste100/SKILL.md", command)


if __name__ == "__main__":
    unittest.main()
