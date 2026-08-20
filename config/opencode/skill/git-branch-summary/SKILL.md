---
name: git-branch-summary
description: Summarize all git commits on your branch since diverging from main into a title and description. Use when the user asks to "summarize the branch", "write a PR description", "write an MR description", or needs a summary of branch changes for a pull request or merge request.
---

Provide a branch summary title and body that concisely summarizes the branch changes as they have diverged from master/main. Follow these rules:

- Write in first person as the developer. Never use "we".
- Avoid en dashes, em dashes, and other non-standard characters.
- Do not mention yourself in the message.
- If the branch affects production-facing behavior, include a post-deployment checklist.
- If the changes warrant QA, provide QA notes.
- Provide this in a codeblock that uses markdown.
