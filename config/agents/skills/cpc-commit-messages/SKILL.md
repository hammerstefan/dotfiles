---
name: cpc-commit-messages
description: Use ONLY when the user asks to write, rewrite, review, or format a Git commit message, commit summary, footer, or Conventional Commits-style history entry. Trigger on commit message, commit title, Conventional Commits, CPC-0008, Co-Authored-By, BREAKING-CHANGE, or squashing guidance.
---

# CPC Commit Messages

Use this skill only for Git commit message work.

## Goal

Produce commit messages that follow CPC-0008 and Conventional Commits.

## Rules

- Keep one logical change per commit.
- Use present tense.
- Start the summary with a type: `feat`, `fix`, `build`, `ci`, `docs`, `perf`, `refactor`, `style`, `test`, or `chore`.
- Optionally add a scope: `type(scope): summary`.
- Use `!` after the type for breaking changes, and include a `BREAKING-CHANGE:` footer.
- Do not end the summary with a period.
- Keep every line at 70 characters or fewer.
- Separate summary, body, and footers with blank lines.
- Put intent and context in the body, not implementation details.
- Use footers like `Co-Authored-By:` when relevant.
- Keep commit text understandable without external issue trackers.

## Workflow

1. Read the user's change description.
2. If the change mixes unrelated work, call that out and suggest splitting it.
3. Draft a commit summary that matches the change type.
4. Add a short body explaining why the change exists.
5. Add required footers when the user mentions co-authors or breaking changes.
6. If the user asks for review, check the message against the rules above and point out violations.

## Output Style

- Be concise.
- Prefer one best commit message unless the user asks for alternatives.
- If context is missing, ask for the minimal detail needed to name the change well.
