# OpenCode session lifecycle

How a long session keeps its work while its context is compacted, and the
vocabulary the OpenCode plugins use for it.

## Language

**Soft compaction**:
The guided end of a long session: the agent wraps up and records where it
stopped, the session is compacted with the summary focused on the work that is
left, and the agent continues from the checkpoint.
_Avoid_: auto compaction, compaction mode

**Soft compaction mode**:
The armed state of a session, in which a plugin watches the context and compacts
the session when it grows past the soft threshold.
_Avoid_: monitoring, watch mode

**Soft threshold**:
The context usage at which a soft compaction starts.
_Avoid_: compaction limit, buffer, cap

**Context usage**:
The size of the conversation the model would receive now: the input, output,
reasoning and cache tokens of the last assistant message, summed.
_Avoid_: context size, token count

**Wrap-up**:
The step in which the agent finishes what it is doing, records its state and
next steps, and stops, so that the session can be compacted.
_Avoid_: checkpoint, pause, shutdown

**Checkpoint**:
The record the agent keeps of its state and next steps. It is stored as a
session instruction, so it outlives a compaction. The plugin compacts the
session when the checkpoint is recorded, because a session that another plugin
keeps busy never goes idle.
_Avoid_: summary, handoff, notes

**Focused compaction**:
A compaction whose summary request carries an instruction about what the summary
has to keep.
_Avoid_: guided compaction, biased compaction

**Native compaction**:
OpenCode's own automatic compaction near the context limit. It stays on under a
soft compaction and is the safety net for it.
_Avoid_: built-in compaction, auto compaction
