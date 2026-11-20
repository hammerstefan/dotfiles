# Glossary Map

## Contexts

- [Herdr worktree workflow](./GLOSSARY.md): how an ask becomes a worktree with
  its own session, and how the worktree closes.
- [OpenCode session lifecycle](./config/opencode/GLOSSARY.md): how a long
  session keeps its work while its context is compacted.

## Relationships

- Herdr worktree workflow → OpenCode session lifecycle: a worktree session is
  an OpenCode session, so a soft compaction applies to it like any other.
