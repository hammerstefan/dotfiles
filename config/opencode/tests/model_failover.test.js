// Tests for plugins/model-failover.js.
//
// Run with: bun test config/opencode/tests/model_failover.test.js
//
// The decision (which failure switches, and to what) is pure and takes the
// model list, the cooldowns and the switch budget as inputs. The hook wiring is
// exercised through a stubbed plugin context that records `session.hook`
// registrations and `session.switchModel` calls, which is the contract the
// OpenCode server offers the plugin.

import { afterEach, beforeEach, describe, expect, test } from "bun:test"
import { mkdtemp, rm, writeFile } from "node:fs/promises"
import { tmpdir } from "node:os"
import { join } from "node:path"
import failover, { internals } from "../plugins/model-failover.js"

const {
  normalizeConfig,
  loadConfig,
  parseRef,
  refKey,
  classify,
  plan,
  createState,
  configDirectory,
} = internals

const MINIMAX = { providerID: "minimax-coding-plan", id: "MiniMax-M3" }
const GLM = { providerID: "zai-coding-plan", id: "glm-5.3" }
const DEEPSEEK = { providerID: "openrouter", id: "deepseek/deepseek-v4.1-flash" }
const OTHER = { providerID: "github-copilot", id: "gpt-6-sol" }

const error = (type, extra = {}) => ({ type, message: `${type} failed`, ...extra })

const decide = ({
  model = MINIMAX,
  chain = [MINIMAX, GLM, DEEPSEEK],
  failure = error("provider.auth"),
  attempt = 2,
  availableModels = chain,
  providers = new Map(),
  models = new Map(),
  switches = 0,
  now = 1_000,
  overrides = {},
} = {}) => {
  const config = { ...normalizeConfig({ chains: [chain.map(refKey)] }), ...overrides }
  const verdict = classify({ error: failure, attempt, rateLimitAttempts: config.rateLimitAttempts })
  if (verdict === "never" || verdict === "wait") return undefined
  return plan({
    config,
    model,
    verdict,
    available: new Set(availableModels.map(refKey)),
    cooling: { providers, models },
    switches,
    now,
  })
}

/** A plugin context shaped like the one OpenCode hands a V2 promise plugin. */
const createContext = ({ models = [MINIMAX, GLM, DEEPSEEK], switchModel } = {}) => {
  const hooks = new Map()
  const switches = []
  const context = {
    location: { directory: "/tmp/opencode/model-failover-tests" },
    model: {
      list: async () => ({ location: context.location, data: models.map((model) => ({ ...model, enabled: true })) }),
    },
    session: {
      hook: async (name, callback) => {
        hooks.set(name, callback)
        return { dispose: async () => {} }
      },
      switchModel: async (input) => {
        switches.push(input)
        if (switchModel) await switchModel(input)
      },
    },
  }
  return { context, hooks, switches }
}

let directory
let previousConfigDir
let previousStateHome

beforeEach(async () => {
  directory = await mkdtemp(join(tmpdir(), "model-failover-"))
  previousConfigDir = process.env.OPENCODE_CONFIG_DIR
  previousStateHome = process.env.XDG_STATE_HOME
  process.env.OPENCODE_CONFIG_DIR = directory
  process.env.XDG_STATE_HOME = directory
})

afterEach(async () => {
  if (previousConfigDir === undefined) delete process.env.OPENCODE_CONFIG_DIR
  else process.env.OPENCODE_CONFIG_DIR = previousConfigDir
  if (previousStateHome === undefined) delete process.env.XDG_STATE_HOME
  else process.env.XDG_STATE_HOME = previousStateHome
  await rm(directory, { recursive: true, force: true })
})

/** Write a chain file into the temporary config directory the plugin reads. */
const configure = async (value) => {
  await writeFile(join(directory, "model-failover.json"), JSON.stringify(value), "utf8")
}

describe("parseRef", () => {
  test("reads provider and model, and keeps a variant", () => {
    expect(parseRef("minimax-coding-plan/MiniMax-M3")).toEqual(MINIMAX)
    expect(parseRef("openrouter/deepseek/deepseek-v4.1-flash#thinking")).toEqual({
      ...DEEPSEEK,
      variant: "thinking",
    })
    expect(parseRef("  zai-coding-plan/glm-5.3  ")).toEqual(GLM)
  })

  test("rejects values that are not a provider/model pair", () => {
    for (const value of ["", "minimax", "/model", "provider/", "provider/model#", 42, undefined, null]) {
      expect(parseRef(value)).toBeUndefined()
    }
  })
})

describe("normalizeConfig", () => {
  test("keeps two-or-more-entry chains and drops adjacent duplicates", () => {
    const normalized = normalizeConfig({
      chains: [["a/one", "a/one", "b/two"], ["a/one"], ["a/one", "nope"], "b/two"],
    })
    expect(normalized.chains).toEqual([[{ providerID: "a", id: "one" }, { providerID: "b", id: "two" }]])
  })

  test("falls back to defaults for missing or unusable values", () => {
    expect(normalizeConfig(undefined)).toEqual({
      enabled: true,
      chains: [],
      cooldownMinutes: 30,
      rateLimitAttempts: 4,
      switchDelayMs: 250,
    })
    expect(normalizeConfig({ cooldownMinutes: -1, rateLimitAttempts: "soon", switchDelayMs: Infinity })).toMatchObject({
      cooldownMinutes: 30,
      rateLimitAttempts: 4,
      switchDelayMs: 250,
    })
    expect(normalizeConfig({ enabled: false }).enabled).toBe(false)
  })

  test("reads the chain file from the active config directory and tolerates a missing file", async () => {
    expect(configDirectory()).toBe(directory)
    expect(await loadConfig()).toMatchObject({ chains: [] })
    await configure({ chains: [[refKey(MINIMAX), refKey(GLM)]] })
    expect((await loadConfig()).chains).toHaveLength(1)
  })

  test("surfaces unreadable JSON so setup can disable itself", async () => {
    await writeFile(join(directory, "model-failover.json"), "{oops", "utf8")
    await expect(loadConfig()).rejects.toThrow()
  })
})

describe("classify", () => {
  test("switches at once when the plan itself is gone", () => {
    for (const type of [
      "provider.auth",
      "provider.quota",
      "provider.budget-limit",
      "provider.model-budget-limit",
      "provider.free-limit",
      "provider.chatgpt-limit",
    ]) {
      expect(classify({ error: error(type), attempt: 2, rateLimitAttempts: 4 })).toBe("exhausted")
    }
  })

  test("spends the native retries on throttles and provider-internal failures", () => {
    expect(classify({ error: error("provider.rate-limit"), attempt: 2, rateLimitAttempts: 4 })).toBe("wait")
    expect(classify({ error: error("provider.rate-limit"), attempt: 3, rateLimitAttempts: 4 })).toBe("wait")
    expect(classify({ error: error("provider.rate-limit"), attempt: 4, rateLimitAttempts: 4 })).toBe("throttled")
    expect(classify({ error: error("provider.internal"), attempt: 4, rateLimitAttempts: 4 })).toBe("throttled")
  })

  test("treats a throttle that asks for more than a minute as a plan limit", () => {
    const failure = error("provider.rate-limit", { retryAfterMs: 15 * 60_000 })
    expect(classify({ error: failure, attempt: 2, rateLimitAttempts: 4 })).toBe("exhausted")
    const brief = error("provider.rate-limit", { retryAfterMs: 5_000 })
    expect(classify({ error: brief, attempt: 2, rateLimitAttempts: 4 })).toBe("wait")
  })

  test("never switches for a failure another model would share", () => {
    for (const type of [
      "provider.invalid-request",
      "provider.content-filter",
      "provider.unsupported-operation",
      "provider.no-route",
      "provider.transport",
      "provider.timeout",
      "permission.rejected",
      "tool.execution",
      "unknown",
    ]) {
      expect(classify({ error: error(type), attempt: 9, rateLimitAttempts: 4 })).toBe("never")
    }
  })
})

describe("plan", () => {
  test("moves to the next healthy model in the chain", () => {
    expect(decide()).toEqual({ model: GLM, reason: "exhausted" })
  })

  test("skips a provider that is cooling down", () => {
    const providers = new Map([["zai-coding-plan", 2_000]])
    expect(decide({ providers, now: 1_000 })).toEqual({ model: DEEPSEEK, reason: "exhausted" })
    expect(decide({ providers, now: 2_001 })).toEqual({ model: GLM, reason: "exhausted" })
  })

  test("skips a model that is cooling down", () => {
    const models = new Map([[refKey(GLM), 2_000]])
    expect(decide({ failure: error("provider.internal"), attempt: 4, models, now: 1_000 })).toEqual({
      model: DEEPSEEK,
      reason: "throttled",
    })
    expect(decide({ failure: error("provider.internal"), attempt: 4, models, now: 2_001 })).toEqual({
      model: GLM,
      reason: "throttled",
    })
  })

  test("never hops to another model on a plan that just refused", () => {
    const miniFlash = { providerID: "minimax-coding-plan", id: "MiniMax-M3.1-Flash" }
    const chain = [MINIMAX, miniFlash, GLM, DEEPSEEK]
    expect(decide({ chain })).toEqual({ model: GLM, reason: "exhausted" })
    // A throttle is a property of the model, so the lighter one on the same plan is tried.
    expect(decide({ chain, failure: error("provider.internal"), attempt: 4 })).toEqual({
      model: miniFlash,
      reason: "throttled",
    })
  })

  test("skips a candidate the location cannot serve", () => {
    expect(decide({ availableModels: [MINIMAX, DEEPSEEK] })).toEqual({ model: DEEPSEEK, reason: "exhausted" })
    expect(decide({ availableModels: [MINIMAX] })).toBeUndefined()
  })

  test("leaves models outside the chain alone", () => {
    expect(decide({ model: OTHER })).toBeUndefined()
  })

  test("stops at the end of the chain and at the per-turn budget", () => {
    expect(decide({ model: GLM })).toEqual({ model: DEEPSEEK, reason: "exhausted" })
    expect(decide({ model: DEEPSEEK })).toBeUndefined()
    expect(decide({ model: MINIMAX, switches: 1 })).toEqual({ model: GLM, reason: "exhausted" })
    expect(decide({ model: MINIMAX, switches: 2 })).toBeUndefined()
  })

  test("does nothing while a throttle still has native retries left", () => {
    expect(decide({ failure: error("provider.rate-limit"), attempt: 3 })).toBeUndefined()
  })

  test("does nothing for request-scoped failures or when disabled", () => {
    expect(decide({ failure: error("provider.invalid-request") })).toBeUndefined()
    expect(decide({ overrides: { enabled: false } })).toBeUndefined()
  })
})

describe("state", () => {
  test("counts switches per session and cools providers and models separately", () => {
    const state = createState()
    expect(state.count("ses_a")).toBe(0)
    state.charge("ses_a")
    state.charge("ses_a")
    expect(state.count("ses_a")).toBe(2)
    state.reset("ses_a")
    expect(state.count("ses_a")).toBe(0)

    state.coolProvider("zai-coding-plan", 5_000, 30)
    expect(state.isCooling(GLM, 5_000)).toBe(true)
    expect(state.isCooling(DEEPSEEK, 5_000)).toBe(false)
    expect(state.isCooling(GLM, 5_000 + 30 * 60_000)).toBe(false)

    state.coolModel(DEEPSEEK, 5_000, 30)
    expect(state.isCooling(DEEPSEEK, 5_000)).toBe(true)
    // A model cooldown leaves the rest of its provider alone.
    expect(state.isCooling({ providerID: "openrouter", id: "deepseek/deepseek-v4-flash" }, 5_000)).toBe(false)
  })
})

describe("setup", () => {
  test("registers the prompt and retry hooks when a chain is configured", async () => {
    await configure({ chains: [[refKey(MINIMAX), refKey(GLM), refKey(DEEPSEEK)]] })
    const { context, hooks } = createContext()
    await failover.setup(context)
    expect([...hooks.keys()].sort()).toEqual(["prompt", "retry"])
  })

  test("registers nothing without a chain", async () => {
    await configure({ chains: [] })
    const { context, hooks } = createContext()
    await failover.setup(context)
    expect(hooks.size).toBe(0)
  })

  test("registers nothing when the chain file is unreadable", async () => {
    await writeFile(join(directory, "model-failover.json"), "{oops", "utf8")
    const { context, hooks } = createContext()
    await failover.setup(context)
    expect(hooks.size).toBe(0)
  })

  test("switches the session and forces the retry on a plan failure", async () => {
    await configure({ chains: [[refKey(MINIMAX), refKey(GLM), refKey(DEEPSEEK)]] })
    const { context, hooks, switches } = createContext()
    await failover.setup(context)

    const event = { sessionID: "ses_a", model: MINIMAX, error: error("provider.auth"), attempt: 2, decision: { retry: false } }
    await hooks.get("retry")(event)

    expect(switches).toEqual([{ sessionID: "ses_a", model: GLM }])
    expect(event.decision).toEqual({ retry: true, delay: 250 })
  })

  test("keeps its hands off a transient failure the native retry still covers", async () => {
    await configure({ chains: [[refKey(MINIMAX), refKey(GLM), refKey(DEEPSEEK)]] })
    const { context, hooks, switches } = createContext()
    await failover.setup(context)

    const event = { sessionID: "ses_a", model: MINIMAX, error: error("provider.rate-limit"), attempt: 2, decision: { retry: true, delay: 2_000 } }
    await hooks.get("retry")(event)

    expect(switches).toEqual([])
    expect(event.decision).toEqual({ retry: true, delay: 2_000 })
  })

  test("skips a lighter model on the plan that just refused", async () => {
    const miniFlash = { providerID: "minimax-coding-plan", id: "MiniMax-M3.1-Flash" }
    await configure({ chains: [[refKey(MINIMAX), refKey(miniFlash), refKey(GLM)]] })
    const { context, hooks, switches } = createContext({ models: [MINIMAX, miniFlash, GLM] })
    await failover.setup(context)

    const event = { sessionID: "ses_a", model: MINIMAX, error: error("provider.quota"), attempt: 2, decision: { retry: false } }
    await hooks.get("retry")(event)

    expect(switches.map((entry) => refKey(entry.model))).toEqual([refKey(GLM)])
    expect(event.decision).toEqual({ retry: true, delay: 250 })
  })


  test("leaves the retry decision alone when the switch itself fails", async () => {
    await configure({ chains: [[refKey(MINIMAX), refKey(GLM), refKey(DEEPSEEK)]] })
    const { context, hooks } = createContext({
      switchModel: async () => {
        throw new Error("server unavailable")
      },
    })
    await failover.setup(context)

    const event = { sessionID: "ses_a", model: MINIMAX, error: error("provider.auth"), attempt: 2, decision: { retry: false } }
    await expect(hooks.get("retry")(event)).resolves.toBeUndefined()
    expect(event.decision).toEqual({ retry: false })
  })

  test("spends one switch per turn and starts over on the next prompt", async () => {
    await configure({ chains: [[refKey(MINIMAX), refKey(GLM), refKey(DEEPSEEK)]] })
    const { context, hooks, switches } = createContext()
    await failover.setup(context)

    const fail = (model) => {
      const event = { sessionID: "ses_a", model, error: error("provider.quota"), attempt: 2, decision: { retry: false } }
      return hooks.get("retry")(event).then(() => event)
    }

    // First turn: minimax -> glm -> deepseek, then the chain is spent for the turn.
    expect((await fail(MINIMAX)).decision).toEqual({ retry: true, delay: 250 })
    expect((await fail(GLM)).decision).toEqual({ retry: true, delay: 250 })
    expect((await fail(DEEPSEEK)).decision).toEqual({ retry: false })
    expect(switches.map((entry) => refKey(entry.model))).toEqual([refKey(GLM), refKey(DEEPSEEK)])

    // Next turn: glm is cooling down, so minimax skips it.
    await hooks.get("prompt")({ sessionID: "ses_a" })
    expect((await fail(MINIMAX)).decision).toEqual({ retry: true, delay: 250 })
    expect(refKey(switches.at(-1).model)).toBe(refKey(DEEPSEEK))
  })
})
