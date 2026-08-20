---
description: Retain important knowledge from the current session
agent: build
---

Review the current session for durable information worth remembering.

Retain only:
- Decisions and their rationale
- Rejected approaches and why
- Non-obvious fixes or lessons
- New project conventions
- Explicit user preferences

Do not retain:
- Secrets, credentials, or sensitive personal data
- File contents or facts already documented in the repository
- Greetings, scheduling, routine actions, or transient debugging output

If qualifying information exists, call `hindsight_retain` exactly once with a rich, self-contained account preserving relevant context and rationale. Do not call `hindsight_recall` in this turn.

If nothing qualifies, do not call the tool and report: `No durable session information to retain.`
