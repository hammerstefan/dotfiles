# Shared Readability Criteria

## Audience

Use the intended audience when clear; otherwise assume a competent developer
new to the project. For end-user text, assume the user's knowledge. Define
project-specific abbreviations, component names, and concepts when necessary,
or link to an accessible explanation. Do not demand definitions of ordinary
vocabulary for that audience.

## Review Criteria

At sentence level, look for:
- Clear, concise, natural language without filler or tangled clauses. A casual
  tone or slang is not required; clear long sentences are acceptable.
- Explicit subjects and references where “this” or “it” is ambiguous.
- Necessary definitions and consistent terminology.
- Clear conditions, exceptions, requirements, recommendations, and examples.
- Patronizing wording, marketing filler, or unsupported promises.

At document level, look for:
- Logical order, useful headings, and prerequisites before instructions.
- Actionable instructions: who acts, what to do, where, and how to recognize
  success when those details are necessary.
- Consistent names matching actual APIs, CLI options, and configuration keys.
- Small examples when they materially clarify an abstract explanation.
- Scannable paragraphs, lists, steps, warnings, and alternatives.
- Descriptive links and wording that avoids unnecessary dependence on visual
  position, cultural references, or shared background.
- Useful detail without redundant filler; retain rationale and qualifications.

Flag missing explanations needed to understand scoped text. Do not turn this
into a general factual-verification or documentation-completeness audit.

## Ambiguous-Term Scan

Before writing feedback, scan all scoped human-facing text for ambiguous terms.
Check headings, summaries, prose, labels, and every list item, not only the
opening paragraphs. Identify all distinct audience-relevant ambiguities, not
just examples or the most prominent terms. Check:
- Undefined project abbreviations, component names, roles, and work-package labels.
- Qualifiers such as "high-confidence", "safe", and "transient" when the text
  needs a definition, threshold, or decision source to make them actionable.
- Limits, bounds, guardrails, permissions, and controls whose scope or reference
  is unclear, including unspecified success conditions.
- Slash compounds such as "kill-switch/shadow mode" that do not establish
  whether the terms mean alternatives, separate features, or one mechanism.
- Lifecycle and state terms such as "pending", "retry", and "outcome loop"
  when different interpretations would change the required action.
- Inconsistent names and unclear references to actors, objects, or prerequisites.

Check each candidate against definitions and context already available within
the permitted scope. A definition or clear reference can resolve a candidate.
Do not assume that an unread dependency defines a term. Do not follow links or
expand retrieval permissions for this scan. Ordinary vocabulary and standard
technical terms understood by the intended audience do not need definitions.

For each unresolved term, quote the exact safe source wording and identify its
location. Explain the missing meaning or competing interpretations and why the
distinction matters. Request a definition, reference, or author decision when
the source cannot support a precise edit. Do not invent expansions or thresholds.
Group repeated uses only when they share the same ambiguity and correction.
Keep different ambiguous terms visible even when they occur in the same sentence.

Report ambiguities that could cause incorrect understanding or use as clarity
defects. Report non-blocking terminology explanations as readability suggestions.
Use the review's existing output channels, scope, filters, and limits. Do not
reclassify substantive defects to bypass filters. If reporting limits prevent
listing all eligible distinct ambiguities, disclose incomplete coverage. If only
explicit substantive filters suppress candidates, disclose filtering as required
by the review contract without exposing filtered items or evading those filters.

Safeguards:
- Preserve technical meaning, qualifications, exceptions, and normative words
  such as MUST and SHOULD. Never invent missing facts; identify what needs
  clarification instead.
- Keep precise terminology, useful passive voice, fragments in headings/labels/
  lists, and deliberate repetition, especially warnings at the point of risk.
- For reviewed source text, do not impose sentence-length rules, universal active voice, or example quotas.
- Do not infer whether AI wrote the text.
- Do not rewrite executable syntax, identifiers, or quoted external text;
  review their surrounding explanations instead.
- Reject personal preference changes between equally clear alternatives.
