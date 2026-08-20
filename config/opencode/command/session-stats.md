---
description: Deterministically report cost and token totals for the current session and all nested subagents
agent: luna
subtask: true
---

Call `session_tree_stats` exactly once with no arguments.

Return its output verbatim so the detailed report remains visible in this child
session. Do not calculate, estimate, summarize, query any other tool, or launch
any additional agent.
