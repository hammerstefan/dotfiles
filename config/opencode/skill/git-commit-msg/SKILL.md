---
name: git-commit-msg
description: Analyze staged git changes and generate a conventional commit message. Use when the user asks to "commit", "write a commit message", "stage and commit", or needs a conventional commit for staged changes.
---

Provide a commit message for the staged changes. Follow these rules:

- Use a conventional commit prefix: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`, `ci:`, `style:`
- Scope is optional: `feat(auth): add session timeout`
- Write in first person as the developer. Never use "we".
- Imperative mood, concise (1-2 sentences max).
- Do not add newlines within a sentence.
- Avoid en dashes, em dashes, and other non-standard characters.
- Do not mention yourself in the message (no co-author statement).
- Provide the message in a codeblock.
- Do not run git commit.
