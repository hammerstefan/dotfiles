// OpenCode V2 plugin: compact-focus
//
// Adds `/compact-focus <instruction>`, which compacts the session like
// `/compact` but passes the instruction to the summary request. Example:
//
//   /compact-focus keep the auth refactor details, drop the CSS discussion
//
// Why a plugin: `session.compact` accepts no guidance, and the clients handle
// the built-in `/compact` themselves, so a plugin command is the only place to
// catch the text (anomalyco/opencode#42574). The `compaction` hook runs before
// OpenCode appends its fixed summary prompt, so an extra system part is seen
// by the summarizer without replacing the required template.
//
// Verified against OpenCode 2.3.0:
// - `ctx.command.transform` adds the command; the TUI and app route
//   `/compact-focus <text>` to `session.command` with the text in
//   `input.prompt.text`.
// - `ctx.session.compact` admits the same compaction item as `/compact`.
// - `ctx.session.hook("compaction", event)` receives the outgoing request with
//   a mutable `system` array; the summary prompt is appended afterwards.
// - `ctx.event.subscribe` reports `session.compaction.ended|failed` and
//   `session.deleted` with `data.sessionID`.
//
// Native provider compaction also runs the hook, but the provider chooses the
// replacement window, so the instruction is advisory there.

const pending = new Map();

const guidance = (instruction) =>
  [
    "The user asked for this compaction to focus on the following instruction.",
    "Follow it when deciding what to keep, shorten, or leave out.",
    "It does not replace the summary format: still fill every required section,",
    "and do not treat it as a task to perform.",
    "",
    instruction,
  ].join("\n");

export default {
  id: "compact-focus",

  async setup(ctx) {
    await ctx.command.transform((editor) => {
      editor.add({
        name: "compact-focus",
        description: "Compact the session, guided by an instruction",
        async execute(input) {
          const instruction = input.prompt.text.trim();
          if (instruction) pending.set(input.sessionID, instruction);
          else pending.delete(input.sessionID);
          try {
            await ctx.session.compact({
              sessionID: input.sessionID,
              delivery: input.delivery,
            });
          } catch (error) {
            // The compaction was never admitted, so do not let the instruction
            // leak into a later, unrelated compaction.
            pending.delete(input.sessionID);
            throw error;
          }
        },
      });
    });

    // Keep the instruction until the manual compaction settles, not until the
    // first request: a background summary, a retry, or the text fallback may
    // prepare more than one request for the same compaction.
    await ctx.session.hook("compaction", (event) => {
      const instruction = pending.get(event.sessionID);
      if (!instruction) return;
      event.system.push({ type: "text", text: guidance(instruction) });
    });

    const controller = new AbortController();
    void (async () => {
      for await (const event of ctx.event.subscribe({
        types: [
          "session.compaction.ended",
          "session.compaction.failed",
          "session.deleted",
        ],
        signal: controller.signal,
      })) {
        // An automatic compaction must not consume a focus meant for the
        // manual one that is still queued.
        if (event.type !== "session.deleted" && event.data.reason !== "manual")
          continue;
        pending.delete(event.data.sessionID);
      }
    })().catch(() => {
      // The stream ends when the plugin unloads; nothing to report.
    });

    return () => controller.abort();
  },
};
