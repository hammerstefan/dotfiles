You are starting work in a fresh git worktree.

Checkout: {{CHECKOUT}}
Repository: {{REPO}}  Branch: {{BRANCH}}  Base: {{BASE}}

# Ask

{{ASK}}

# Why

{{WHY}}

# Where things stand

- `AGENTS.md` and every file it points at are the repository rules. {{RULES_POINTER}}
- The `{{IMPLEMENT_SKILL}}` skill lives at `{{IMPLEMENT_SKILL_PATH}}` with
  `disable-model-invocation: true`, so it is absent from the skill catalog. Load
  it with the skill tool, id `{{IMPLEMENT_SKILL}}`. Check it on disk with
  `sed -n '1,5p' {{IMPLEMENT_SKILL_PATH}}/SKILL.md`.
- The issue is {{ISSUE_REF}} ({{ISSUE_URL}}). Read it with
  `gh issue view {{ISSUE_NUMBER}}`.
- {{CLAIMS}}
- {{HOST_LINE}}

{{SIBLING_TABLE}}

# What to do

{{STEPS}}

# Rules

- Read `AGENTS.md` and every file it points at before editing.
{{EXTRA_RULES}}
- Commit on `{{BRANCH}}`. {{DELIVERY}}
- Ask before anything that destroys host state or spends money. When you need a
  decision, a credential, or a value only the person has, ask for it with the
  `question` tool and wait. Do not guess it, and do not stop to ask in prose.

{{AUTONOMY}}

# Done when

{{DONE_WHEN}}

# Report

Before the report, call `todowrite` once with every item still remaining — work
only the person can finish, a step you could not run, a check you did not
verify, a decision still open — one todo each, each one `pending`, and nothing
that is already done. That list is how the person sees what is left after this
session stops; it replaces any earlier list, so write all of it, and write an
empty list when nothing remains rather than an invented todo.

Finish with: what you did, what you found, what you did not verify, and what you
need from the person.
