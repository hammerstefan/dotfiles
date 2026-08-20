Prioritize retrieval-led reasoning over pretrained-knowledge-led reasoning.

## OpenSpec Workflow (mandatory across all projects)

For any project that uses OpenSpec, all standard OpenSpec work **must**
be done through the OpenSpec skills defined in the project's
`.opencode/skills/openspec-*/` (or the equivalent project skill set).
Do not perform OpenSpec operations ad-hoc. The following operations
have dedicated skills and must be invoked via the `skill` tool:

- `openspec-new-change` — starting a new change (artifact workflow)
- `openspec-propose` — full proposal (design + specs + tasks) in one step
- `openspec-continue-change` — progressing an existing change
- `openspec-apply-change` — implementing tasks from a change
- `openspec-sync-specs` — syncing delta specs to main specs
- `openspec-archive-change` — finalizing and archiving a change

Before performing any of the above, load the corresponding skill
(`skill` tool with the skill name) and follow its instructions. This
ensures artifacts (`proposal.md`, `tasks.md`, specs, etc.) are
produced consistently and stay in sync.

If a project does not use OpenSpec, this rule does not apply.
