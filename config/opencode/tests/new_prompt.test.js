// Tests for new-prompt/tui.js.
//
// Run with: bun test config/opencode/tests/new_prompt.test.js
//
// The plugin is a TUI plugin. It registers a slash command that keeps the text
// typed after it, creates a session, runs the named command in that session,
// and focuses the session. The tests stub the plugin context OpenCode hands a
// TUI plugin and assert the calls the plugin makes.

import { describe, expect, test } from "bun:test"
import plugin, { internals } from "../new-prompt/tui.js"

const { USAGE, parseSlashHead, start } = internals

const DIRECTORY = "/tmp/opencode/new-prompt-tests"
const DEFAULT_DIRECTORY = "/tmp/opencode/new-prompt-default"

/**
 * A plugin context shaped like the one OpenCode hands a V2 TUI plugin. Every
 * call the plugin makes is recorded so the test can assert on them.
 */
const createContext = ({ commands = ["init", "review"], tabs = true, fail } = {}) => {
  const calls = []
  const toasts = []
  let counter = 0
  const context = {
    location: { directory: DIRECTORY },
    keymap: {
      layer: (factory) => calls.push({ layer: factory() }),
    },
    client: {
      command: {
        list: async () => ({ location: context.location, data: commands.map((name) => ({ name })) }),
      },
      session: {
        create: async (input) => {
          calls.push({ create: input })
          if (fail?.create) throw fail.create
          counter += 1
          return { id: `ses_${counter}` }
        },
        command: async (input) => {
          calls.push({ command: input })
          if (fail?.command) throw fail.command
        },
        prompt: async (input) => {
          calls.push({ prompt: input })
          if (fail?.prompt) throw fail.prompt
        },
        remove: async (input) => {
          calls.push({ remove: input })
        },
      },
    },
    data: {
      location: { default: () => ({ directory: DEFAULT_DIRECTORY }) },
      session: { sync: async (sessionID) => calls.push({ sync: sessionID }) },
    },
    ui: {
      tabs: {
        enabled: () => tabs,
        // The real tab API returns false without focusing when tabs are off.
        focus: (sessionID) => {
          if (!tabs) return false
          calls.push({ focus: sessionID })
          return true
        },
      },
      router: { navigate: (destination) => calls.push({ navigate: destination }) },
      toast: { show: (options) => toasts.push(options) },
    },
  }
  return { context, calls, toasts }
}

describe("the slash command", () => {
  test("keeps the text typed after it so the command can read its arguments", () => {
    const { context, calls } = createContext()
    plugin.setup(context)
    const command = calls[0].layer.commands[0]
    expect(command.slash).toEqual({ name: "new-prompt", aliases: ["np"], arguments: true })
  })
})

describe("parseSlashHead", () => {
  test("splits the command from its arguments", () => {
    expect(parseSlashHead("/review pr 100")).toEqual({ name: "review", arguments: "pr 100" })
    expect(parseSlashHead("/review")).toEqual({ name: "review", arguments: "" })
    expect(parseSlashHead("/team/review pr 100")).toEqual({ name: "team/review", arguments: "pr 100" })
  })

  test("treats text without a leading slash as a plain prompt", () => {
    expect(parseSlashHead("fix the bug")).toBeUndefined()
  })
})

describe("start", () => {
  test("creates a session, runs the command in it, and focuses it", async () => {
    const { context, calls } = createContext()
    await start(context, "/review pr 100")
    expect(calls).toContainEqual({ create: { location: { directory: DIRECTORY } } })
    expect(calls).toContainEqual({ command: { sessionID: "ses_1", name: "review", text: "pr 100" } })
    expect(calls).toContainEqual({ sync: "ses_1" })
    expect(calls).toContainEqual({ focus: "ses_1" })
  })

  test("sends plain text to the new session as a prompt", async () => {
    const { context, calls } = createContext()
    await start(context, "fix the bug")
    expect(calls).toContainEqual({ prompt: { sessionID: "ses_1", text: "fix the bug" } })
    expect(calls.some((call) => call.command)).toBe(false)
  })

  test("navigates to the session when tabs are disabled", async () => {
    const { context, calls } = createContext({ tabs: false })
    await start(context, "/review pr 100")
    expect(calls).toContainEqual({ navigate: { type: "session", sessionID: "ses_1" } })
    expect(calls.some((call) => call.focus)).toBe(false)
  })

  test("rejects an unknown command before it creates a session", async () => {
    const { context, calls, toasts } = createContext()
    await start(context, "/nope pr 100")
    expect(calls.some((call) => call.create)).toBe(false)
    expect(toasts).toEqual([{ title: "new-prompt", message: `Unknown command: /nope. ${USAGE}`, variant: "error" }])
  })

  test("reports empty input", async () => {
    const { context, calls, toasts } = createContext()
    await start(context, "   ")
    expect(calls.some((call) => call.create)).toBe(false)
    expect(toasts).toEqual([{ title: "new-prompt", message: USAGE, variant: "error" }])
  })

  test("drops a session that never received its prompt", async () => {
    const { context, calls, toasts } = createContext({ fail: { command: new Error("server refused") } })
    await start(context, "/review pr 100")
    expect(calls).toContainEqual({ remove: { sessionID: "ses_1" } })
    expect(calls.some((call) => call.focus)).toBe(false)
    expect(toasts).toEqual([{ title: "new-prompt", message: "server refused", variant: "error" }])
  })

  test("falls back to the default location when the TUI has none", async () => {
    const { context, calls } = createContext()
    context.location = undefined
    await start(context, "/review pr 100")
    expect(calls).toContainEqual({ create: { location: { directory: DEFAULT_DIRECTORY } } })
  })
})
