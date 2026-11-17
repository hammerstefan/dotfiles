// OpenCode V2 TUI plugin: /new-prompt
//
// "/new-prompt /review pr 100" opens a new session, runs "/review pr 100" in
// it, and focuses that session. A session tab opens with it when tabs are
// enabled.
//
// Why a TUI plugin and not a command file:
// - A command file always runs in the session that invoked it. Only a plugin
//   can create a second session.
// - Tabs are client-local state, so only the TUI can open and focus one.
//
// Why the server command API and not expanded text:
// - `session.command` dispatches the named command in the target session, so
//   the command keeps its own agent, model and template. Sending the expanded
//   text as a plain prompt would drop all of that.
//
// The new session sits in the directory the TUI currently sits in and uses the
// project's default agent and model.
//
// This plugin lives in a directory on purpose: the TUI plugin loader skips a
// local plugin that is a plain file and only loads a local directory or a
// package. The directory's `tui.js` is the TUI part.
//
// Registered in cli.json as "./new-prompt". A directory beside cli.json does
// not load on its own; only the "plugins" subdirectory is discovered without
// being listed.

const USAGE = "Usage: /new-prompt /review pr 100"

/**
 * Split the argument text the way the TUI splits a slash command: the first
 * token is the command name, the rest are its arguments. Text without a
 * leading slash is a plain prompt for the new session.
 */
const parseSlashHead = (text) => {
  if (!text.startsWith("/")) return undefined
  const body = text.slice(1)
  const end = body.search(/[ \t\n]/)
  if (end === -1) return { name: body, arguments: "" }
  return { name: body.slice(0, end), arguments: body.slice(end + 1) }
}

const fail = (context, message) => {
  context.ui.toast.show({ title: "new-prompt", message, variant: "error" })
}

const start = async (context, input) => {
  const raw = (input ?? "").trim()
  if (!raw) {
    fail(context, USAGE)
    return
  }
  const head = parseSlashHead(raw)
  const directory = (context.location ?? context.data.location.default()).directory
  let sessionID
  try {
    if (head) {
      // Check the command exists before creating a session, so an unknown name
      // leaves nothing behind.
      const known = await context.client.command.list({ location: { directory } })
      if (!known.data.some((command) => command.name === head.name)) {
        fail(context, `Unknown command: /${head.name}. ${USAGE}`)
        return
      }
    }
    const created = await context.client.session.create({ location: { directory } })
    // The generated client unwraps `session.create` but leaves `command.list`
    // wrapped, so the session id sits on the session itself.
    sessionID = created.id
    if (head) await context.client.session.command({ sessionID, name: head.name, text: head.arguments })
    else await context.client.session.prompt({ sessionID, text: raw })
  } catch (error) {
    // A session that never received its prompt is clutter: drop it.
    if (sessionID) await context.client.session.remove({ sessionID }).catch(() => undefined)
    fail(context, typeof error === "string" ? error : (error?.message ?? String(error)))
    return
  }
  await context.data.session.sync(sessionID)
  // Focusing the session opens its tab when tabs are enabled. Without tabs,
  // navigate to the session instead.
  if (!context.ui.tabs.focus(sessionID)) context.ui.router.navigate({ type: "session", sessionID })
}

export default {
  id: "new-prompt",
  setup(context) {
    context.keymap.layer(() => ({
      mode: "global",
      commands: [
        {
          id: "session.new-prompt",
          title: "New session with a command",
          description: "Run a command in a new session",
          slash: { name: "new-prompt", aliases: ["np"], arguments: true },
          run: (input) => start(context, input),
        },
      ],
    }))
  },
}

export const internals = { USAGE, parseSlashHead, start }

