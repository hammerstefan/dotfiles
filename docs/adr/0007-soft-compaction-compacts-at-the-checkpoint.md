# The soft compaction compacts at the checkpoint, not at the idle event

The `soft-compact` plugin watches a session and, when the context reaches the
threshold, asks the agent to wrap up. It then waits for the session to go idle
before it asks OpenCode to compact. That wait has no timeout, and a session that
another plugin keeps busy never goes idle. The goal mode is such a plugin: it
steers "continue toward the goal" into the running turn, so the session stays
busy for as long as the goal runs.

On 2026-11-20 a session armed at 300,000 tokens reached 301,358 tokens, wrapped
up, recorded its checkpoint, and stayed in `wrapping-up` for the rest of the
run. Its last idle transition was 18 seconds before the wrap-up.

So the plugin compacts when the agent records its checkpoint. The checkpoint is
the agent's own signal that it stopped: the wrap-up instruction asks it to
finish the step it is in, record its state and its next steps, and stop.
OpenCode runs an admitted compaction at the next step boundary, so the work in
flight finishes before the summary is made. The idle event stays as the second
signal, for a session that stops without recording a checkpoint.

## Considered Options

- **Wait for the idle event only.** Rejected: the goal mode never lets a
  session go idle, so the mode never compacts the sessions that need it most.
- **Compact as soon as the wrap-up prompt is admitted.** Rejected: the agent
  would be compacted before it recorded its state, and the summary would be all
  the state the next agent has.
- **Give the wait a timeout and compact after it.** Rejected: a timeout cuts
  the work in flight at an arbitrary point. The checkpoint says where the work
  stopped, so the plugin does not have to guess.
- **Ask the goal mode to pause the session.** Rejected: the goal belongs to the
  other plugin. The soft compaction has to work with whatever keeps the session
  busy.

## Consequences

- The checkpoint tool asks for the compaction. The plugin does not wait for the
  session to go idle, and a session that keeps working is compacted at the
  boundary after the checkpoint.
- The checkpoint of an earlier round is removed when the session is armed, so a
  checkpoint always belongs to the current round.
- The focus instruction of the summary request lives in the shared state. Every
  instance of the plugin finds it there, and only the first one to come gives it
  to the summary request.
- The server loads the plugin once per app, so several instances share the
  storage and the events. A lock directory in the state directory keeps one flow
  at a time per session across all of them. Without it, one measured round sent
  eight wrap-up prompts, one from each instance that woke up at the same time.
- A session that stops without recording a checkpoint still compacts on the
  idle event.
