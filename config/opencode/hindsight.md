# Hindsight memory protocol

You have three long-term memory tools: `hindsight_retain`, `hindsight_recall`,
`hindsight_reflect`. Use them like this:

1. **Recall first.** Before any non-trivial task (new feature, refactor,
   non-obvious bug fix, architectural decision), call `hindsight_recall` with
   a query that names the area. Look for: prior decisions in this area,
   rejected approaches, known bugs, project conventions.
2. **Reflect when synthesizing.** When the user asks a question that needs
   synthesis across many memories ("what's our testing strategy?",
   "why did we choose Postgres over SQLite?"), call `hindsight_reflect`
   instead of `hindsight_recall`. Reflect runs an agentic loop and
   reasons across the bank.
3. **Retain at the end.** When you finish a task that involved a real
   decision, a rejected approach, a non-obvious fix, or a new project
   convention, call `hindsight_retain` with a *rich, full-context*
   description. The server extracts facts; do not pre-summarize.

   Cardinally: **never call `hindsight_retain` and `hindsight_recall` in
   the same turn.** Retain is async; the new memory will not be available
   in this turn. Trust the auto-retain hook on session idle, and use
   explicit `hindsight_retain` only at the end of a task.

4. **Trust auto-recall.** Memories already injected at the top of this
   system prompt are real. If you find yourself wanting to call
   `hindsight_recall` for a query that the system context already
   answered, do not.
5. **What belongs in memory vs. in code.** Decisions and *why* go in
   memory. File contents, type signatures, and current state go in code.
   Do not retain things that are already in `AGENTS.md` or in the repo.
6. **Be specific about people.** When a preference belongs to a
   specific teammate ("Alice asked for X"), name them. The bank's
   `directives` cover project-wide rules; per-person preferences are
   just facts in the bank.

## Things to never do
- Do not retain greetings, planning chatter, or scheduling.
- Do not retain file contents the agent just read.
- Do not retain "we discussed X" without a *what was decided* and *why*.
- Do not call `hindsight_retain` for transient debug output.
