// Tests for plugins/soft-compact/index.js.
//
// Run with: bun test config/opencode/tests/soft_compact.test.js
//
// The decisions that can be wrong without the server are pure and take their
// inputs directly: the command line, the threshold, and the size of the
// context. The sequence is exercised through a stubbed plugin context that
// records the prompts, the compaction request and the instruction entries, and
// that delivers the server events the plugin listens for.

import { afterEach, beforeEach, describe, expect, test } from "bun:test"
import { mkdtemp, rm, writeFile } from "node:fs/promises"
import { tmpdir } from "node:os"
import { join } from "node:path"
import plugin, { internals } from "../plugins/soft-compact/index.js"
import { formatTokens, indicator } from "../plugins/soft-compact/indicator.js"

const { contextTokens, lockDirectory, normalizeConfig, parseCommand, parseThreshold, withLock } = internals

const SESSION = "ses_soft_compact"

/** An assistant message with the token usage the TUI counts. */
const assistant = (tokens) => ({
  id: "msg_assistant",
  type: "assistant",
  tokens: { input: 0, output: 0, reasoning: 0, cache: { read: 0, write: 0 }, ...tokens },
})

/** The agent answers the wrap-up prompt with a step of its own, and then stops. */
const agentTurn = async (harness) => {
  harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
  await flush()
  harness.events.push({ type: "session.idle", data: { sessionID: SESSION } })
  await flush()
}

/** Let the plugin finish the work it started from an event. */
const flush = async () => {
  for (let index = 0; index < 20; index++) await new Promise((resolve) => setTimeout(resolve, 0))
}

/** An event stream the test drives, with the shape the plugin expects. */
const createEventStream = () => {
  const listeners = new Set()
  const push = (event) => {
    for (const listener of [...listeners]) listener(event)
  }
  const subscribe = async function* (options) {
    const queue = []
    let wake
    const listener = (event) => {
      queue.push(event)
      wake?.()
    }
    listeners.add(listener)
    const abort = () => wake?.()
    options?.signal?.addEventListener("abort", abort)
    try {
      while (!options?.signal?.aborted) {
        if (queue.length === 0) {
          await new Promise((resolve) => {
            wake = resolve
          })
          wake = undefined
          continue
        }
        yield queue.shift()
      }
    } finally {
      listeners.delete(listener)
    }
  }
  return { push, subscribe }
}

/** A plugin context shaped like the one OpenCode hands a V2 promise plugin. */
const createContext = ({ messages = [], stored, storage: shared } = {}) => {
  const calls = {
    prompts: [],
    compactions: [],
    hooks: new Map(),
    commands: new Map(),
    tools: new Map(),
    updates: [],
    entries: [],
    removed: [],
  }
  const storage = shared ?? new Map(stored ? Object.entries(stored) : [])
  const events = createEventStream()
  const state = { messages, failContext: false, session: { id: SESSION, time: { idle: 2, busy: 1 }, metadata: {} } }
  const context = {
    location: { directory: "/tmp/opencode/soft-compact-tests" },
    storage: {
      get: async (key) => storage.get(key),
      set: async (key, value) => {
        storage.set(key, value)
      },
    },
    command: {
      transform: async (callback) => {
        callback({ add: (definition) => calls.commands.set(definition.name, definition) })
        return { dispose: async () => {} }
      },
    },
    tool: {
      transform: async (callback) => {
        callback({ add: (definition) => calls.tools.set(definition.name, definition) })
        return { dispose: async () => {} }
      },
    },
    session: {
      hook: async (name, callback) => {
        calls.hooks.set(name, callback)
        return { dispose: async () => {} }
      },
      prompt: async (input) => {
        calls.prompts.push(input)
        return { id: `msg_${calls.prompts.length}` }
      },
      compact: async (input) => {
        calls.compactions.push(input)
        return { id: `msg_compact_${calls.compactions.length}` }
      },
      context: async () => {
        if (state.failContext) throw new Error("the context is not available")
        return state.messages
      },
      get: async () => state.session,
      update: async (input) => {
        calls.updates.push(input)
        state.session = { ...state.session, metadata: input.metadata }
      },
      instructions: {
        entry: {
          put: async (input) => {
            calls.entries.push(input)
          },
          remove: async (input) => {
            calls.removed.push(input)
          },
        },
      },
    },
    event: { subscribe: (options) => events.subscribe(options) },
  }
  return { context, calls, events, state, storage }
}

/** Arm the session through the command, the way a person does. */
const runCommand = async (calls, text) => {
  const command = calls.commands.get("soft-compact")
  await command.execute({ sessionID: SESSION, prompt: { text }, delivery: "steer" })
}

describe("the command line", () => {
  test("an empty line arms the session with the default threshold", () => {
    expect(parseCommand("")).toEqual({ action: "arm" })
  })

  test("off and status are the two other commands", () => {
    expect(parseCommand("off")).toEqual({ action: "off" })
    expect(parseCommand("STATUS")).toEqual({ action: "status" })
  })

  test("a threshold arms the session", () => {
    expect(parseCommand("300k")).toEqual({ action: "arm", threshold: 300_000 })
    expect(parseCommand("400000")).toEqual({ action: "arm", threshold: 400_000 })
  })

  test("the rest of the line is the instruction of the session", () => {
    expect(parseCommand("300k finish the build first")).toEqual({
      action: "arm",
      threshold: 300_000,
      instruction: "finish the build first",
    })
  })

  test("an unknown argument is refused", () => {
    expect(parseCommand("soon")).toEqual({ action: "unknown", argument: "soon" })
  })

  test("a threshold accepts k and m", () => {
    expect(parseThreshold("400k")).toBe(400_000)
    expect(parseThreshold("1m")).toBe(1_000_000)
    expect(parseThreshold("1.5m")).toBe(1_500_000)
    expect(parseThreshold("0")).toBeUndefined()
    expect(parseThreshold("many")).toBeUndefined()
  })
})

describe("the size of the context", () => {
  test("it counts the last assistant message like the TUI does", () => {
    const tokens = contextTokens([assistant({ input: 100, output: 20, reasoning: 5, cache: { read: 300, write: 2 } })])
    expect(tokens).toBe(427)
  })

  test("a session without an assistant message has no context", () => {
    expect(contextTokens([])).toBe(0)
    expect(contextTokens([{ type: "user" }])).toBe(0)
  })

  test("the messages before the last compaction do not count", () => {
    const tokens = contextTokens([
      assistant({ input: 900_000 }),
      { type: "compaction", status: "completed" },
      assistant({ input: 1000 }),
    ])
    expect(tokens).toBe(1000)
  })
})

describe("the configuration", () => {
  test("an unusable value falls back to the default", () => {
    const config = normalizeConfig({ threshold: "soon", intervalMs: -1 })
    expect(config.threshold).toBe(400_000)
    expect(config.intervalMs).toBe(30_000)
  })

  test("a usable value is kept", () => {
    const config = normalizeConfig({ threshold: 250_000, intervalMs: 5000 })
    expect(config.threshold).toBe(250_000)
    expect(config.intervalMs).toBe(5000)
  })
})

describe("the sequence", () => {
  let cleanup
  let harness
  let directory

  beforeEach(async () => {
    directory = await mkdtemp(join(tmpdir(), "opencode-soft-compact-"))
    process.env.OPENCODE_CONFIG_DIR = directory
    process.env.XDG_STATE_HOME = directory
    harness = createContext()
    cleanup = await plugin.setup(harness.context)
  })

  afterEach(async () => {
    cleanup?.()
    delete process.env.OPENCODE_CONFIG_DIR
    delete process.env.XDG_STATE_HOME
    await rm(directory, { recursive: true, force: true })
  })

  test("the session is armed with the threshold of the command", async () => {
    await runCommand(harness.calls, "300k")
    const state = harness.storage.get("sessions")
    expect(state[SESSION].threshold).toBe(300_000)
    expect(state[SESSION].phase).toBe("armed")
  })

  test("a context under the threshold changes nothing", async () => {
    await runCommand(harness.calls, "300k")
    harness.state.messages = [assistant({ input: 299_999 })]
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    expect(harness.calls.prompts).toHaveLength(0)
    expect(harness.calls.compactions).toHaveLength(0)
  })

  test("a context over the threshold asks the agent to wrap up", async () => {
    await runCommand(harness.calls, "300k")
    harness.state.messages = [assistant({ input: 310_000 })]
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    expect(harness.calls.prompts).toHaveLength(1)
    const prompt = harness.calls.prompts[0]
    expect(prompt.sessionID).toBe(SESSION)
    expect(prompt.delivery).toBe("steer")
    expect(prompt.text).toContain("310000")
    expect(prompt.text).toContain("300000")
    expect(prompt.text).toContain("soft_compact_checkpoint")
    expect(harness.state.session.metadata.softCompact.status).toBe("wrapping-up")
  })

  test("the agent may bring its own instruction", async () => {
    await runCommand(harness.calls, "300k finish the build first")
    harness.state.messages = [assistant({ input: 310_000 })]
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    expect(harness.calls.prompts[0].text).toContain("finish the build first")
    expect(harness.calls.prompts[0].text).not.toContain("soft_compact_checkpoint")
  })

  test("the session is compacted when the agent stops", async () => {
    await runCommand(harness.calls, "300k")
    harness.state.messages = [assistant({ input: 310_000 })]
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    await agentTurn(harness)
    expect(harness.calls.compactions).toEqual([{ sessionID: SESSION }])
    expect(harness.storage.get("sessions")[SESSION].phase).toBe("compacting")
  })

  test("the session is compacted when the checkpoint is recorded", async () => {
    await runCommand(harness.calls, "300k")
    harness.state.messages = [assistant({ input: 310_000 })]
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    expect(harness.calls.compactions).toHaveLength(0)

    // The agent records its state and stops. The session never goes idle,
    // because another plugin keeps it busy.
    const tool = harness.calls.tools.get("soft_compact_checkpoint")
    const result = await tool.execute(
      { checkpoint: "## State\nWritten\n\n## Next Steps\nTested" },
      { sessionID: SESSION },
    )
    expect(result.content).toContain("recorded")
    expect(harness.calls.compactions).toEqual([{ sessionID: SESSION }])
    expect(harness.storage.get("sessions")[SESSION].phase).toBe("compacting")
  })

  test("a checkpoint outside a wrap-up records the state and compacts nothing", async () => {
    await runCommand(harness.calls, "300k")
    const tool = harness.calls.tools.get("soft_compact_checkpoint")
    await tool.execute({ checkpoint: "## State\nWritten" }, { sessionID: SESSION })
    expect(harness.calls.entries).toHaveLength(1)
    expect(harness.calls.compactions).toHaveLength(0)
    expect(harness.storage.get("sessions")[SESSION].phase).toBe("armed")
  })

  test("the summary request is told what to keep", async () => {
    await runCommand(harness.calls, "300k")
    harness.state.messages = [assistant({ input: 310_000 })]
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    await agentTurn(harness)
    const event = { sessionID: SESSION, system: [] }
    await harness.calls.hooks.get("compaction")(event)
    expect(event.system).toHaveLength(1)
    expect(event.system[0].text).toContain("Focus the summary on the work that is left")
    expect(event.system[0].text).toContain("does not replace the summary format")
  })

  test("the agent continues after the compaction", async () => {
    await runCommand(harness.calls, "300k")
    harness.state.messages = [assistant({ input: 310_000 })]
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    await agentTurn(harness)
    harness.events.push({ type: "session.compaction.ended", data: { sessionID: SESSION, reason: "manual" } })
    await flush()
    expect(harness.calls.prompts).toHaveLength(2)
    expect(harness.calls.prompts[1].text).toContain("Continue the remaining work")
    expect(harness.storage.get("sessions")[SESSION].phase).toBe("armed")
  })

  test("the mode waits for new work after a compaction", async () => {
    await runCommand(harness.calls, "15k")
    harness.state.messages = [assistant({ input: 19_234 })]
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    await agentTurn(harness)
    harness.events.push({ type: "session.compaction.ended", data: { sessionID: SESSION, reason: "manual" } })
    await flush()
    expect(harness.calls.prompts).toHaveLength(2)

    // The size right after the compaction is the floor the session starts from.
    harness.state.messages = [assistant({ input: 19_234 })]
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    expect(harness.calls.prompts).toHaveLength(2)

    // New work that grows the context past the floor triggers the next round.
    harness.state.messages = [assistant({ input: 39_234 })]
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    expect(harness.calls.prompts).toHaveLength(3)
  })

  test("a compaction the plugin did not ask for does not restart the agent", async () => {
    await runCommand(harness.calls, "300k")
    harness.events.push({ type: "session.compaction.ended", data: { sessionID: SESSION, reason: "auto" } })
    await flush()
    expect(harness.calls.prompts).toHaveLength(0)
    expect(harness.storage.get("sessions")[SESSION].phase).toBe("armed")
  })

  test("off disarms the session", async () => {
    await runCommand(harness.calls, "300k")
    await runCommand(harness.calls, "off")
    expect(harness.storage.get("sessions")[SESSION]).toBeUndefined()
  })

  test("status reports the phase and the context", async () => {
    await runCommand(harness.calls, "300k")
    harness.state.messages = [assistant({ input: 12_000 })]
    await runCommand(harness.calls, "status")
    const notice = harness.state.session.metadata.softCompact
    expect(notice.status).toBe("armed")
    expect(notice.threshold).toBe(300_000)
    expect(notice.message).toContain("armed")
    expect(notice.message).toContain("12000")
  })
})

describe("the recovery", () => {
  let cleanup
  let harness
  let directory

  beforeEach(async () => {
    directory = await mkdtemp(join(tmpdir(), "opencode-soft-compact-"))
    process.env.OPENCODE_CONFIG_DIR = directory
    process.env.XDG_STATE_HOME = directory
  })

  afterEach(async () => {
    cleanup?.()
    delete process.env.OPENCODE_CONFIG_DIR
    delete process.env.XDG_STATE_HOME
    await rm(directory, { recursive: true, force: true })
  })

  test("two triggers at once admit one wrap-up prompt", async () => {
    harness = createContext()
    cleanup = await plugin.setup(harness.context)
    await runCommand(harness.calls, "300k")
    harness.state.messages = [assistant({ input: 310_000 })]
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    expect(harness.calls.prompts).toHaveLength(1)
  })

  test("two instances that share the storage admit one wrap-up prompt", async () => {
    const storage = new Map()
    const first = createContext({ storage })
    const second = createContext({ storage })
    const firstCleanup = await plugin.setup(first.context)
    const secondCleanup = await plugin.setup(second.context)
    cleanup = () => {
      firstCleanup?.()
      secondCleanup?.()
    }
    await runCommand(first.calls, "300k")
    first.state.messages = [assistant({ input: 310_000 })]
    second.state.messages = [assistant({ input: 310_000 })]
    first.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    second.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    const prompts = first.calls.prompts.length + second.calls.prompts.length
    expect(prompts).toBe(1)
  })

  test("two instances that share the storage admit one compaction", async () => {
    const storage = new Map()
    const first = createContext({ storage })
    const second = createContext({ storage })
    const firstCleanup = await plugin.setup(first.context)
    const secondCleanup = await plugin.setup(second.context)
    cleanup = () => {
      firstCleanup?.()
      secondCleanup?.()
    }
    await runCommand(first.calls, "300k")
    first.state.messages = [assistant({ input: 310_000 })]
    second.state.messages = [assistant({ input: 310_000 })]
    first.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    second.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    const tool = first.calls.tools.get("soft_compact_checkpoint")
    await tool.execute({ checkpoint: "## State\nWritten" }, { sessionID: SESSION })
    await flush()
    const compactions = first.calls.compactions.length + second.calls.compactions.length
    expect(compactions).toBe(1)
  })

  test("a context that cannot be read does not become a floor", async () => {
    harness = createContext()
    cleanup = await plugin.setup(harness.context)
    await runCommand(harness.calls, "300k")
    harness.state.messages = [assistant({ input: 310_000 })]
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    await agentTurn(harness)
    harness.events.push({ type: "session.compaction.ended", data: { sessionID: SESSION, reason: "manual" } })
    await flush()

    harness.state.failContext = true
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    const entry = harness.storage.get("sessions")[SESSION]
    expect(entry.floorPending).toBe(true)
    expect(entry.floor).toBe(0)
  })

  test("a session that was compacting when the plugin loaded is resumed", async () => {
    harness = createContext({
      stored: {
        sessions: {
          [SESSION]: { threshold: 300_000, phase: "compacting", armedAt: 0, floor: 0 },
        },
      },
      messages: [{ type: "compaction", status: "completed" }],
    })
    cleanup = await plugin.setup(harness.context)
    await flush()
    expect(harness.calls.prompts).toHaveLength(1)
    expect(harness.calls.prompts[0].text).toContain("Continue the remaining work")
    expect(harness.storage.get("sessions")[SESSION].phase).toBe("armed")
  })
})

describe("the lock of a session", () => {
  let directory

  beforeEach(async () => {
    directory = await mkdtemp(join(tmpdir(), "opencode-soft-compact-"))
    process.env.XDG_STATE_HOME = directory
  })

  afterEach(async () => {
    delete process.env.XDG_STATE_HOME
    await rm(directory, { recursive: true, force: true })
  })

  test("two instances do not work on a session at the same time", async () => {
    const order = []
    const first = withLock(SESSION, async () => {
      order.push("first in")
      await new Promise((resolve) => setTimeout(resolve, 50))
      order.push("first out")
    })
    const second = withLock(SESSION, async () => {
      order.push("second in")
      order.push("second out")
    })
    await Promise.all([first, second])
    expect(order).toEqual(["first in", "first out", "second in", "second out"])
  })

  test("the lock of a session is a directory in the state directory", async () => {
    expect(lockDirectory(SESSION)).toBe(
      join(directory, "opencode", "locks", `soft-compact-${SESSION}.lock`),
    )
  })
})

describe("the indicator", () => {
  test("the mode that is off has no indicator", () => {
    expect(indicator(undefined)).toBeUndefined()
    expect(indicator({ status: "off" })).toBeUndefined()
  })

  test("an armed mode shows the threshold it was set to", () => {
    expect(indicator({ status: "armed", threshold: 400_000 })).toEqual({
      label: "◆ cmp(400k)",
      tone: "muted",
    })
  })

  test("the phases of a cycle show what the mode is doing", () => {
    expect(indicator({ status: "wrapping-up", threshold: 400_000 })).toEqual({
      label: "◆ cmp(400k) · wrapping up",
      tone: "warning",
    })
    expect(indicator({ status: "compacting", threshold: 400_000 })).toEqual({
      label: "◆ cmp(400k) · compacting",
      tone: "active",
    })
  })

  test("a threshold that is not known leaves the number out", () => {
    expect(indicator({ status: "armed" }).label).toBe("◆ cmp(?)")
  })

  test("a token count is short", () => {
    expect(formatTokens(400_000)).toBe("400k")
    expect(formatTokens(1_000_000)).toBe("1m")
    expect(formatTokens(15_000)).toBe("15k")
    expect(formatTokens(1_234_567)).toBe("1.2m")
    expect(formatTokens(500)).toBe("500")
    expect(formatTokens(0)).toBeUndefined()
    expect(formatTokens(undefined)).toBeUndefined()
  })
})

describe("the configuration file", () => {
  let cleanup
  let harness
  let directory

  beforeEach(async () => {
    directory = await mkdtemp(join(tmpdir(), "opencode-soft-compact-"))
    process.env.OPENCODE_CONFIG_DIR = directory
    process.env.XDG_STATE_HOME = directory
  })

  afterEach(async () => {
    cleanup?.()
    delete process.env.OPENCODE_CONFIG_DIR
    delete process.env.XDG_STATE_HOME
    await rm(directory, { recursive: true, force: true })
  })

  test("the instruction of the file reaches the agent", async () => {
    await writeFile(
      join(directory, "soft-compact.json"),
      JSON.stringify({ instruction: "Finish the migration, then stop." }),
      "utf8",
    )
    harness = createContext()
    cleanup = await plugin.setup(harness.context)
    await runCommand(harness.calls, "300k")
    harness.state.messages = [assistant({ input: 310_000 })]
    harness.events.push({ type: "session.step.ended", data: { sessionID: SESSION } })
    await flush()
    expect(harness.calls.prompts[0].text).toContain("Finish the migration, then stop.")
  })
})

describe("the checkpoint tool", () => {
  let cleanup
  let harness
  let directory

  beforeEach(async () => {
    directory = await mkdtemp(join(tmpdir(), "opencode-soft-compact-"))
    process.env.OPENCODE_CONFIG_DIR = directory
    process.env.XDG_STATE_HOME = directory
    harness = createContext()
    cleanup = await plugin.setup(harness.context)
  })

  afterEach(async () => {
    cleanup?.()
    delete process.env.OPENCODE_CONFIG_DIR
    delete process.env.XDG_STATE_HOME
    await rm(directory, { recursive: true, force: true })
  })

  test("the tool records the state and the next steps", async () => {
    await runCommand(harness.calls, "300k")
    const tool = harness.calls.tools.get("soft_compact_checkpoint")
    const result = await tool.execute(
      { checkpoint: "## State\nThe plugin is written\n\n## Next Steps\nWrite the tests" },
      { sessionID: SESSION },
    )
    expect(result.content).toContain("recorded")
    expect(harness.calls.entries).toHaveLength(1)
    expect(harness.calls.entries[0].key).toBe("soft-compact-checkpoint")
    expect(harness.calls.entries[0].value).toContain("The plugin is written")
    expect(harness.calls.entries[0].value).toContain("Write the tests")
  })

  test("the tool accepts the text of a Code Mode call", async () => {
    await runCommand(harness.calls, "300k")
    const tool = harness.calls.tools.get("soft_compact_checkpoint")
    await tool.execute("## State\nWritten\n\n## Next Steps\nTested", { sessionID: SESSION })
    expect(harness.calls.entries[0].value).toContain("Written")
    expect(harness.calls.entries[0].value).toContain("Tested")
  })

  test("the tool records nothing when the mode is off", async () => {
    const tool = harness.calls.tools.get("soft_compact_checkpoint")
    const result = await tool.execute({ checkpoint: "Something" }, { sessionID: SESSION })
    expect(result.content).toContain("not armed")
    expect(harness.calls.entries).toHaveLength(0)
  })
})
