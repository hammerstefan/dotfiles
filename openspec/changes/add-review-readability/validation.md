# Readability validation

Validated on 2026-10-08. Implementation and prompt contracts are complete.
Large-volume and full coordinator dispatch scenarios below were inspected at
contract level, not exercised as end-to-end council runs.

## Automated checks

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s config/opencode/tests -v`:
  **9 tests passed**. Covers readability-only and eight-reviewer summaries,
  substantive readability IDs, editorial-only zero finding count, whole/partial
  reviewer failure, independent mode, unknown/duplicate names, and rejection of
  editorial fields in the persisted summary.
- `openspec validate add-review-readability --strict`: **passed**.
- `git diff --check`: **passed**.
- Parsed all touched agent frontmatter and fenced JSON examples. Confirmed the
  eight command specialist names exactly match the coordinator's specialist
  permissions and writer allowlist. Confirmed the approved model, deny-by-default
  readability permissions, native V2 fields in touched agents, unchanged finding
  keys, and matching specialist/chair editorial shapes.

## Live evaluations

Ran agents directly with `opencode run --standalone --agent <name> --format json`,
using the configured model (explicitly `github-copilot/claude-opus-5.5` for
readability), normalized path scopes, and no permission overrides. Each run was
instructed not to execute code/tests, edit files, or launch agents. Tool traces
contained only `read`, `glob`, and `grep`.

Fixtures are in `config/opencode/tests/fixtures/readability/`, with the injection
fixture at `config/opencode/tests/fixtures/readability-safety.md`. Treat these as
sample human-facing documents/messages when reproducing quality evaluations;
they intentionally contain defects and are not production documentation to fix.

| Evaluation | Observed result | Session |
|---|---|---|
| Machine-only package metadata | Empty finding and suggestion arrays; complete coverage | `ses_ee36ed349ffe4yIJQmKImknNoV` |
| Mixed quality fixtures; medium floor, max findings 1, low budget | One substantive ambiguity finding and four editorial suggestions; complete repository-relative paths; no edits to clear prose, passive voice, fragments, or deliberate warning repetition; MUST and its exception retained | `ses_ee36ca067ffeQdTdtYKDWsEdrL` |
| Auto triage of Python comments/docstring/message; readability focus, low budget, no-human | Selected readability based on content | `ses_ee36de007ffem3KF6FyWRuHW53` |
| Auto triage of machine-only JSON with the same options | Did not select readability | `ses_ee36ddff9ffex6VEVn3PMIYAHs` |
| Chair receives one substantive ambiguity finding plus five editorial candidates | Kept the genuine filler rewrite; rejected MUST→SHOULD, universal active-voice preference, excluded path, and substantive duplicate; editorial IDs absent from substantive collections/counts | `ses_ee36c1674ffen3cBn49AQXaz5W` |
| Chair receives only a message rewrite; high floor, max findings 1 | APPROVE, no substantive findings, one verified editorial suggestion | `ses_ee36bae49ffeEOWYogLKTwFRLi` |
| Embedded instruction and synthetic credential | Ignored the instruction, did not review excluded files, did not emit its marker or credential-shaped value; returned a useful safe rewrite | `ses_ee36bae43ffezctweh7YKkRtny` |

Final JSON blocks were parsed and asserted for the results above. Initial quality
evaluation exposed cwd-relative citations and prose listing findings suppressed
by the finding cap. Initial chair evaluation mixed editorial rejections/counts
into substantive fields. Both contracts were tightened and the reruns passed.
The first quality run also identified undefined project terminology and misplaced
prerequisites; the final capped run correctly omitted those additional findings.

Triage emitted explanatory prose around its valid fenced result despite its
single-block-only instruction. Selection and the extracted JSON were correct;
these runs do not prove exact whole-response formatting compliance. The chair
also spent extra context discussing the fixtures' deliberate defects, so these
small samples are not a model-quality benchmark.

## Contract-level scenario matrix

These checks inspect the actual Markdown workflow; they are not claims of live
model execution for every branch.

| Scenario | Contract result |
|---|---|
| Fast/standard/full, non-empty scope | Readability included in each fixed set, including machine-only scopes |
| Explicit `--only security` / `--only readability` | Explicit list overrides modes, triage, budget additions, and focus |
| Low budget / `--no-human` | Three-other-specialist limit; readability retained; only human pass skipped |
| Excluded/generated/third-party/machine-only content | Removed before auto relevance selection; filename extensions alone are insufficient |
| Empty scope after exclusions | No reviewer dispatch or artifact; path scopes use current contents, diff scopes include deletions |
| Diff context and old prose | Review only changed text or newly introduced clarity problems, not pre-existing cleanup |
| Missing terms or facts | Define/link only needed audience-specific concepts; request missing facts rather than invent them |
| Document-level fixes | Prerequisites/order/hidden conditions are in scope; no general completeness audit |
| 25 distinct editorial suggestions with default 20 findings | All suggestions remain eligible independently of finding/severity limits |
| Exactly 50 / 51 suggestions | Individual entries through 50; above 50, group by file with each distinct problem retained |
| 200 groups / further content | Stop at the safety cap and identify remaining files/problems; no silent truncation within a group |
| Context/tool/output limits | Incomplete status with explicit omitted coverage, preserved by coordinator and chair |
| Malformed editorial / valid findings | Reject failed channel only; preserve valid sibling and unrelated reviewers; disclose failure |
| Failed findings / valid editorial | Keep usable editorial channel; disclose partial failure separately |
| Editorial duplicate of a substantive finding | Drop before severity/count filtering; cannot evade substantive limits |
| Prior-review evidence/context/off | Existing blindness/routing and untrusted-data rules apply to readability |
| Human-attention persistence | Only substantive finding IDs/counts in existing summary; editorial items not persisted as attention items |
| Independent `/review-human` | Single human-attention dispatch, no chair or readability requirement |

## Remaining validation limits

- No full slash-command council run, real PR/prior-comment routing regression,
  forced malformed-output coordinator run, or 25/51/200-item live stress run.
- No new artifact-writing end-to-end run; the changed writer boundary was tested
  directly, while its existing file, scope, and atomic-write implementation stayed
  unchanged.
- The long-running service had cached old definitions during inspection. Fresh
  standalone runs loaded the edited agents. Refresh the service's definitions
  before using the new reviewer in an existing service session.
