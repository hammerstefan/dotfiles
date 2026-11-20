# Soft compaction steers the agent before it compacts

The `soft-compact` plugin watches the context of a session and, when it reaches
the threshold, asks the agent to wrap up, waits for it to stop, and only then
asks OpenCode to compact, with the summary focused on the work that is left.
OpenCode's own automatic compaction stays on as the safety net, and the
threshold is an absolute token count rather than a share of the model window.

## Considered Options

- `compaction.auto` and `compaction.buffer` alone. They compact without warning,
  and the agent never records where it stopped, so the summary is all the state
  the next agent has.
- Interrupt the agent when the threshold is reached. The timing is exact, but it
  cuts off work in flight, such as a half-written file or a test that was about
  to run.
- Wait for the native threshold and guide that compaction. The request comes too
  late: the context is already at the limit, so the request that has to fit is
  the one that does not.

## Consequences

The mode waits without a timeout. A session that never stops stays in
`wrapping-up`, and the native automatic compaction is what ends it. ADR 0007
replaces this wait with the checkpoint of the agent, because a session that
another plugin keeps busy never goes idle.

A compaction leaves the context at the size of the checkpoint and the kept
tail, so the mode measures that size as the floor the session starts from and
waits for new work before the next compaction. Without that, a threshold below
the size a compaction leaves would compact the session again and again.
