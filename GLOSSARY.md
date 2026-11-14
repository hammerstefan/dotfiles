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
The operation that closes a source worktree: an extraction over its sessions,
a pull request, and the close.
_Avoid_: cleanup, teardown, harvest

**Extraction**:
The operation that turns session evidence into repository-level knowledge. It
produces one digest per session, a synthesis against the existing conventions, a
check of every claim, and a staged change. A wrapup runs one.
_Avoid_: harvest, mining, distillation

**Staged change**:
The knowledge an extraction produced in the repository and did not commit,
grouped into concerns. The extraction commits nothing. Its caller commits.
_Avoid_: pending change, working tree

**Extraction report**:
The record an extraction hands to the steps after it. It holds each lesson and
where it landed, the claims checked, the counts and evals, the self-review
verdict, and the concerns. A pull request body, a memory document and a wrapup
report come from it.
_Avoid_: findings file, summary

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
A structured summary of one worktree session, produced by an extraction from
its transcript, and the only input the synthesis reads in full.
_Avoid_: summary, abstract

**Concern**:
One kind of change in an extraction's staged change, such as skills, guidance or
glossary. It records the paths that belong to it, so a wrapup can commit each as
its own commit.
_Avoid_: topic, section

**Focus**:
The space, tab and pane the Herdr window shows and gives the keyboard to. A
space spawned for another session opens behind the one that spawned it, without
taking the focus.
_Avoid_: selection, active space
