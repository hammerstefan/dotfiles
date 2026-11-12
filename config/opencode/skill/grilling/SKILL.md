---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round, then wait for the user's answers before the next round.

## Ask a round

Ask the whole frontier in **one call to the `question` tool**, one entry per question:

- `header`: `Q<n> <short title>`, at most 30 characters — the tool's own limit.
- `question`: the question body. Several paragraphs if it needs them; say what the decision is and what it costs.
- `options`: the choices, at least two. **Put your recommended answer first and label it "(Recommended)"**, and give every option a description saying what it means. Do not add an "Other" or catch-all option — the tool always offers a free-text answer on its own.
- `multiple`: only when several answers can be true at once.

Word each question so "yes" accepts your recommended answer.

The tool returns the answers, and the interview goes on. The user may leave a question unanswered: it comes back as "Unanswered". Ask it again in the next round, or leave it out and say that you left it open — never guess on their behalf.

If the tool reports that it could not show the question to the user, ask the round in plain text instead.

## Each round reshapes the tree

Settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, a codebase), find it yourself; dispatch a sub-agent when it takes a while. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

## When it ends

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Then summarise what was settled — one line per decision, with the reasoning that decided it — and list what you did not verify.

Do not act on the plan until the user confirms you have reached a shared understanding.
