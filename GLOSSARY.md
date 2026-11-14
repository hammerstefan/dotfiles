# Herdr worktree workflow

How an ask becomes a worktree with its own session, and what happens to that
worktree once the work is done.

## Language

**Worktree session**:
An OpenCode session whose directory is a worktree checkout or a path under it,
including the child sessions of one.
_Avoid_: branch session, space session

**Source worktree**:
The worktree a wrapup reads and then closes.
_Avoid_: old worktree, target worktree

**Wrapup**:
The operation that turns the sessions of a source worktree into repo-level
skills, guidance and memory, opens a pull request, and closes the source
worktree.
_Avoid_: cleanup, teardown, harvest

**Reflection session**:
The session a wrapup spawns, in a worktree of its own, to read the transcripts
and produce the wrapup's output.
_Avoid_: summariser, wrapup session

**Trigger session**:
The worktree session a wrapup runs from, and whose export its brief quotes. The
trigger session's own tree is excluded from the sessions to read, because it is
the ask rather than the work.
_Avoid_: current session, main session

**Trace**:
The trigger session's export: the person's words quoted in the brief, and the
file the reflection session reads when a quote is ambiguous or the work landed
somewhere the brief cannot see.
_Avoid_: log, dump

**Lesson**:
A correction, convention or procedure that the sessions demonstrate and a
future session would otherwise have to learn again.
_Avoid_: insight, takeaway, learning

**Digest**:
A structured summary of one worktree session, produced from its transcript, and
the only input the synthesis reads in full.
_Avoid_: summary, abstract

**Concern**:
One kind of change in a wrapup's pull request — skills, guidance documents, or
glossary — each carried by its own commit.
_Avoid_: topic, section

**Focus**:
The space, tab and pane the Herdr window shows and gives the keyboard to. A
space spawned for another session opens behind the one that spawned it, without
taking the focus.
_Avoid_: selection, active space
