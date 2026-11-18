Prioritize retrieval-led reasoning over pretrained-knowledge-led reasoning.

## Skills

Repository-specific workflows are in `.opencode/skills/<id>/SKILL.md`. General
skills are in `~/.agents/skills`. Load a skill with the `skill` tool when the
request matches its task. `implement` works a spec or a ticket set,
`code-review` reviews a change, `tdd` builds test-first, and
`write-a-property-test` writes the invariant over generated input.

## OpenSpec Workflow

A project uses OpenSpec when it holds an `openspec/` directory or an
`.opencode/skills/openspec-*` skill, or the equivalent project skill set. In
such a project, standard OpenSpec work goes through those skills. Load the skill
that names the operation and follow it. The operations are
`openspec-new-change`, `openspec-propose`, `openspec-continue-change`,
`openspec-apply-change`, `openspec-sync-specs`, and `openspec-archive-change`.
Do not perform an OpenSpec operation by hand. In a project without those files,
this rule does not apply.
