// Tests for plugins/session-stats.js.
//
// Run with: bun test config/opencode/tests/session_stats.test.js
//
// The plugin talks to the OpenCode V2 server through the plugin context, so
// the tests stub that context with the shapes the server actually returns:
// `ctx.session.get` resolves to a Session.Info, `ctx.session.list` resolves to
// a `{ data, cursor }` page, and `ctx.session.context` resolves to a
// `{ data }` envelope of Session.Message.Info records.

import { afterEach, beforeEach, describe, expect, test } from "bun:test"
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises"
import { tmpdir } from "node:os"
import { join } from "node:path"
import sessionStats, { internals } from "../plugins/session-stats.js"

const DIRECTORY = "/tmp/opencode/session-stats-tests"

const session = (id, parentID, title) => ({
  id,
  parentID,
  title,
  location: { directory: DIRECTORY },
})

const assistant = ({ agent, model, created, streamed, output, reasoning, cost = 0 }) => ({
  id: `msg_${agent}_${created}`,
  type: "assistant",
  agent,
  model,
  time: streamed === undefined ? { created } : { created, streamed, completed: streamed + 100 },
  tokens: { input: 10, output, reasoning, cache: { read: 0, write: 0 } },
  cost,
})

const FIXTURE = {
  sessions: [
    session("ses_root", undefined, "Root"),
    session("ses_child", "ses_root", "Child"),
    session("ses_grandchild", "ses_child", "Grandchild"),
    session("ses_other", undefined, "Unrelated root"),
  ],
  messages: {
    ses_root: [
      { id: "msg_user", type: "user", time: { created: 500 } },
      assistant({
        agent: "build",
        model: { providerID: "anthropic", id: "claude-sonnet-5-5" },
        created: 1000,
        streamed: 3000,
        output: 100,
        reasoning: 50,
        cost: 0.01,
      }),
      // No `streamed` stamp: this step cannot be measured.
      assistant({
        agent: "build",
        model: { providerID: "anthropic", id: "claude-sonnet-5-5" },
        created: 5000,
        streamed: undefined,
        output: 7,
        reasoning: 3,
      }),
    ],
    ses_child: [
      assistant({
        agent: "review",
        model: { providerID: "openai", id: "gpt-5.6" },
        created: 0,
        streamed: 4000,
        output: 200,
        reasoning: 0,
        cost: 0.02,
      }),
    ],
    ses_grandchild: [
      assistant({
        agent: "review",
        model: { providerID: "openai", id: "gpt-5.6" },
        created: 10000,
        streamed: 13000,
        output: 60,
        reasoning: 40,
      }),
    ],
  },
}

// The plugin reads the live service descriptor to find the OpenCode server.
// The tests point that lookup at a temporary directory so a real server is
// never contacted.
const originalFetch = globalThis.fetch
const originalStateHome = process.env.XDG_STATE_HOME
let stateHome

beforeEach(async () => {
  stateHome = await mkdtemp(join(tmpdir(), "opencode-session-stats-"))
  process.env.XDG_STATE_HOME = stateHome
})

afterEach(async () => {
  globalThis.fetch = originalFetch
  if (originalStateHome === undefined) delete process.env.XDG_STATE_HOME
  else process.env.XDG_STATE_HOME = originalStateHome
  await rm(stateHome, { recursive: true, force: true })
})

/** Write a service descriptor that points at a stubbed OpenCode server. */
const writeServiceDescriptor = async ({ url = "http://127.0.0.1:65535", password = "secret" } = {}) => {
  const directory = join(stateHome, "opencode")
  await mkdir(directory, { recursive: true })
  await writeFile(
    join(directory, "service.json"),
    JSON.stringify({ id: "test-service", version: "2.2.5", url, pid: 1, password }),
  )
}

/** Serve the OpenCode service API from the fixture data. */
const serveServiceApi = ({ sessions = FIXTURE.sessions, messages = FIXTURE.messages } = {}) => {
  const byId = new Map(sessions.map((item) => [item.id, item]))
  const json = (body, status = 200) =>
    new Response(JSON.stringify(body), {
      status,
      headers: { "content-type": "application/json" },
    })
  const seen = []
  globalThis.fetch = async (input) => {
    const target = typeof input === "string" ? input : input instanceof URL ? input.href : input.url
    const url = new URL(target)
    seen.push(url.toString())
    if (url.pathname === "/api/session") {
      const directory = url.searchParams.get("directory")
      const data = sessions.filter(
        (item) => !directory || item.location?.directory === directory,
      )
      return json({ data, cursor: { previous: null, next: null } })
    }
    const context = url.pathname.match(/^\/api\/session\/([^/]+)\/context$/)
    if (context) {
      const id = decodeURIComponent(context[1])
      return json({ data: messages[id] ?? [] })
    }
    const session = url.pathname.match(/^\/api\/session\/([^/]+)$/)
    if (session) {
      const id = decodeURIComponent(session[1])
      const found = byId.get(id)
      if (!found) return json({ message: "not found" }, 404)
      return json({ data: found })
    }
    return json({ message: "not found" }, 404)
  }
  return seen
}

const registerTool = async ({
  sessions,
  messages,
  wrapGet = false,
  failGetFor = [],
  failList = false,
  failContextFor = [],
} = {}) => {
  const registered = {}
  const byId = new Map((sessions ?? FIXTURE.sessions).map((item) => [item.id, item]))
  const ctx = {
    location: { directory: DIRECTORY },
    tool: {
      transform: async (mutate) => {
        await mutate({ add: (tool) => void (registered[tool.name] = tool) })
      },
    },
    session: {
      get: async ({ sessionID }) => {
        if (failGetFor.includes(sessionID)) {
          throw new Error("session lookup failed with HTTP unknown")
        }
        const found = byId.get(sessionID)
        if (!found) throw new Error(`unknown session ${sessionID}`)
        return wrapGet ? { data: found } : found
      },
      list: async () => {
        if (failList) throw new Error("session listing failed with HTTP unknown")
        return {
          data: [...byId.values()],
          cursor: { previous: null, next: null },
        }
      },
      context: async ({ sessionID }) => {
        if (failContextFor.includes(sessionID)) {
          throw new Error("message lookup failed with HTTP unknown")
        }
        return { data: messages?.[sessionID] ?? FIXTURE.messages[sessionID] ?? [] }
      },
      // The V2 plugin context exposes neither of these. A regression that uses
      // them must fail loudly instead of silently reporting zeros.
      children: async () => {
        throw new Error("ctx.session.children does not exist in the V2 plugin context")
      },
      messages: async () => {
        throw new Error("ctx.session.messages does not exist in the V2 plugin context")
      },
    },
  }
  await sessionStats.setup(ctx)
  return registered
}

const run = async (options) => {
  const registered = await registerTool(options)
  expect(Object.keys(registered)).toContain("session_tree_stats")
  return registered.session_tree_stats.execute(
    {},
    { sessionID: "ses_child", messageID: "msg_1", signal: new AbortController().signal },
  )
}

describe("session tree discovery", () => {
  test("the tree spans the root, the current session, and its descendants", async () => {
    const result = await run()
    expect(result.content).toContain("**Sessions discovered:** 3")
    expect(result.content).toContain("**Root session:** `ses_root`")
    expect(result.content).toContain("**Maximum depth:** 2")
  })

  test("an unrelated root session stays out of the tree", async () => {
    const result = await run()
    expect(result.content).toContain("ses_root")
    expect(result.content).toContain("ses_child")
    expect(result.content).toContain("ses_grandchild")
    expect(result.content).not.toContain("ses_other")
    expect(result.content).not.toContain("Unrelated root")
  })

  test("a data envelope on the session lookup is tolerated", async () => {
    const result = await run({ wrapGet: true })
    expect(result.metadata.rootSessionID).toBe("ses_root")
    expect(result.metadata.sessions).toBe(3)
  })
})

describe("throughput", () => {
  test("tokens per second follow the TUI definition", async () => {
    const result = await run()
    // 450 generated tokens over 9000 ms of generation window.
    expect(result.metadata.outputTPS).toBe(50)
    expect(result.content).toContain("**Output TPS:** 50.0 tok/s")
    expect(result.content).toContain("**Generated tokens:** 450")
  })

  test("a step without a generation window is excluded and counted", async () => {
    const result = await run()
    expect(result.metadata.measuredSteps).toBe(3)
    expect(result.content).toContain("**Measured steps:** 3 of 4")
    expect(result.content).toContain("**Unmeasured steps:** 1")
  })

  test("each agent reports its own throughput", async () => {
    const result = await run()
    // build: 150 tokens over 2000 ms. review: 300 tokens over 7000 ms.
    expect(result.content).toContain("| build |")
    expect(result.content).toContain("| review |")
    expect(result.content).toContain("75.0")
    expect(result.content).toContain("42.9")
  })

  test("each model reports its own throughput", async () => {
    const result = await run()
    expect(result.content).toContain("anthropic/claude-sonnet-5-5")
    expect(result.content).toContain("openai/gpt-5.6")
  })
})

describe("usage totals", () => {
  test("cost and token counts cover every aggregated session", async () => {
    const result = await run()
    expect(result.metadata.totalCost).toBeCloseTo(0.03, 10)
    expect(result.content).toContain("**Total cost:** $0.030000")
    expect(result.content).toContain("**Root cost:** $0.010000")
    expect(result.content).toContain("**Subagent cost:** $0.020000")
  })

  test("the report states the compaction limit of the message window", async () => {
    const result = await run()
    expect(result.content).toContain("excludes messages before its last compaction")
  })
})

describe("resilience", () => {
  test("a session without a title does not break the report", async () => {
    const sessions = [
      ...FIXTURE.sessions,
      session("ses_untitled", "ses_root", undefined),
    ]
    const result = await run({ sessions })
    expect(result.content).toContain("ses_untitled")
    expect(result.metadata.complete).toBe(true)
  })

  test("a failed session lookup degrades to a partial result", async () => {
    const result = await run({ failGetFor: ["ses_child"] })
    expect(result.metadata.complete).toBe(false)
    expect(result.content).toContain("session lookup for ses_child failed")
    // The listing still supplies the tree, so the report is still produced.
    expect(result.content).toContain("**Sessions discovered:**")
    expect(result.content).toContain("ses_grandchild")
  })

  test("a failed message lookup skips that session and marks the report partial", async () => {
    const result = await run({ failContextFor: ["ses_grandchild"] })
    expect(result.metadata.complete).toBe(false)
    expect(result.content).toContain("ses_grandchild: message lookup failed")
    expect(result.content).toContain("**Sessions aggregated:** 2")
  })

  test("a failed session listing does not abort the report", async () => {
    const result = await run({ failList: true })
    expect(result.metadata.complete).toBe(false)
    expect(result.content).toContain("the session listing is unavailable")
    expect(result.content).toContain("**Sessions discovered:**")
  })
})

describe("service API fallback", () => {
  test("a failed session lookup is retried through the service API", async () => {
    await writeServiceDescriptor()
    const seen = serveServiceApi()
    const result = await run({ failGetFor: ["ses_child"] })
    expect(result.metadata.complete).toBe(true)
    expect(result.content).toContain("retried through the service API")
    expect(result.content).toContain("**Sessions discovered:** 3")
    expect(seen.some((url) => url.includes("/api/session/ses_child"))).toBe(true)
  })

  test("a failed session listing is retried through the service API", async () => {
    await writeServiceDescriptor()
    const seen = serveServiceApi()
    const result = await run({ failList: true })
    expect(result.metadata.complete).toBe(true)
    expect(result.content).toContain("**Sessions discovered:** 3")
    expect(seen.some((url) => url.startsWith("http://127.0.0.1:65535/api/session?"))).toBe(true)
  })

  test("a failed message lookup is retried through the service API", async () => {
    await writeServiceDescriptor()
    const seen = serveServiceApi()
    const result = await run({ failContextFor: ["ses_grandchild"] })
    expect(result.metadata.complete).toBe(true)
    expect(result.content).toContain("**Sessions aggregated:** 3")
    expect(seen.some((url) => url.includes("/api/session/ses_grandchild/context"))).toBe(true)
  })

  test("the service API request carries the service credentials", async () => {
    await writeServiceDescriptor()
    serveServiceApi()
    const stub = globalThis.fetch
    const seen = []
    globalThis.fetch = async (input, init) => {
      seen.push(init?.headers?.authorization)
      return stub(input, init)
    }
    const result = await run({ failGetFor: ["ses_child"] })
    expect(result.metadata.complete).toBe(true)
    expect(seen.length).toBeGreaterThan(0)
    const credentials = Buffer.from("opencode:secret").toString("base64")
    expect(seen.every((value) => value === `Basic ${credentials}`)).toBe(true)
  })

  test("without a service descriptor the report stays partial", async () => {
    const result = await run({ failGetFor: ["ses_child"] })
    expect(result.metadata.complete).toBe(false)
    expect(result.content).toContain("no OpenCode service endpoint is available")
  })
})

describe("throughput helpers", () => {
  test("a missing streamed stamp leaves the step unmeasured", () => {
    const measured = internals.measureStep({
      time: { created: 10 },
      tokens: { output: 5, reasoning: 5 },
    })
    expect(measured.generated).toBe(10)
    expect(measured.measured).toBeUndefined()
  })

  test("a negative window is clamped to zero", () => {
    const measured = internals.measureStep({
      time: { created: 100, streamed: 40 },
      tokens: { output: 5, reasoning: 0 },
    })
    expect(measured.measured).toBe(0)
  })

  test("throughput is undefined without tokens or time", () => {
    expect(internals.throughput({ generatedTokens: 0, generationMs: 1000 })).toBeUndefined()
    expect(internals.throughput({ generatedTokens: 100, generationMs: 0 })).toBeUndefined()
    expect(internals.throughput({ generatedTokens: 100, generationMs: 2000 })).toBe(50)
  })
})
