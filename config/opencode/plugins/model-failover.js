// OpenCode V2 plugin: model-failover
//
// When a provider cannot serve a request, move the session to the next model
// in a configured chain instead of stopping the turn. Built for coding-plan
// quotas: minimax-coding-plan -> zai-coding-plan -> opencode-go deepseek flash.
//
// Why the `retry` hook and not `experimental.model.resolve`:
// - `experimental.model.resolve` runs before every request and is the natural
//   place for routing, but the runner rejects any model from another provider
//   ("Same provider only", session/runner/model.ts). It cannot cross plans.
// - `retry` fires for every provider failure, including the ones the built-in
//   policy calls non-retryable (Authentication, QuotaExceeded), because the
//   hook runs before the decision is honoured (session/runner/retry.ts). The
//   ChatGPT provider already relies on that to force `retry: false`.
// - The hook is awaited, `session.switchModel` projects `ModelSelected` to the
//   session row, and the retry attempt re-runs `prepareContext`, which reads
//   `session.model` again (session/runner/llm.ts). The request therefore goes
//   to the new provider, and auto-compaction is re-estimated against its
//   context window.
//
// V2 plugin-context API (verified against OpenCode 2.3.0):
// - A plugin is a default export `{ id, setup(ctx) }` (`setup` may be async).
// - `ctx.session.hook(name, callback)` registers within the plugin scope;
//   `callback` may return a promise. Mutating the event object in place is the
//   contract: for `retry`, set `event.decision = { retry, delay }`.
// - `ctx.session.switchModel({ sessionID, model })` takes a model ref
//   `{ providerID, id, variant? }`.
// - `ctx.model.list()` resolves to `{ data: Model.Info[] }` and holds only the
//   models this location can actually serve, so it doubles as a credentials
//   check. `Model.Info.id` is the ref id, `Model.Info.providerID` the provider.
// - `ctx.session.hook("prompt", ...)` runs for each admitted prompt, which is
//   where the per-turn switch budget is reset.
//
// Behaviour, in order of precedence:
// - Request-scoped failures never switch: another model would fail the same
//   way (invalid request, content filter, unsupported operation, no route,
//   transport, timeout, tool and permission errors).
// - Plan failures switch immediately: authentication (an exhausted or revoked
//   plan surfaces as 401/403/permission_denied), quota, budget, model budget,
//   free and chatgpt limits.
// - Throttles and provider-internal failures first spend the native retries
//   (about 84 seconds), then switch. A throttle asking for more than a minute
//   switches at once; waiting that long on a dead plan is worse than moving.
// - A plan failure cools the whole provider for `cooldownMinutes`, so later
//   sessions skip it, and it disqualifies that provider's remaining models for
//   the current decision: they would refuse the same plan. A throttle cools
//   only the model that answered, leaving a lighter model on the same plan
//   usable. A model with no cooldown entry is never assumed healthy without
//   asking `ctx.model.list()`.
// - A session may switch at most `chain.length - 1` times per turn. The budget
//   resets on the next prompt, so a recovered plan is retried next turn.
// - Nothing here can break the turn: every failure inside the plugin is caught
//   and logged, and the failure is rethrown only to the caller's own effect.

import { appendFile, mkdir, readFile } from "node:fs/promises"
import { homedir } from "node:os"
import { dirname, join } from "node:path"

const CONFIG_FILENAME = "model-failover.json"
const LOG_FILENAME = "model-failover.log"

/** The chain file lives beside the plugin, in the active global config directory. */
const configDirectory = () => process.env.OPENCODE_CONFIG_DIR ?? join(homedir(), ".config", "opencode")
const stateDirectory = () => join(process.env.XDG_STATE_HOME ?? join(homedir(), ".local", "state"), "opencode")

/** Model list staleness. Only failure paths read it, so a short cache is enough. */
const MODELS_TTL_MS = 60_000

/** A provider that asks for longer than this is treated as a plan limit, not a throttle. */
const LONG_RETRY_AFTER_MS = 60_000

const DEFAULTS = {
  enabled: true,
  chains: [],
  cooldownMinutes: 30,
  rateLimitAttempts: 4,
  switchDelayMs: 250,
}

/**
 * The provider will not serve this request again soon. A different provider is
 * the only way forward, so switch on the first failure.
 */
const EXHAUSTED = new Set([
  "provider.auth",
  "provider.quota",
  "provider.budget-limit",
  "provider.model-budget-limit",
  "provider.free-limit",
  "provider.chatgpt-limit",
])

/** Transient at the provider, but not at this model: give the native retries a chance first. */
const FLAKY = new Set([
  "provider.rate-limit",
  "provider.internal",
  "provider.unknown",
  "provider.invalid-output",
  "unreachable",
])

/**
 * Every remaining error is request-scoped or client-scoped: a different model
 * would reject it identically, or the network is down for every provider. The
 * list is documentation of what must never switch; the default branch already
 * refuses anything unrecognized.
 */
const NEVER_SWITCH = new Set([
  "provider.invalid-request",
  "provider.content-filter",
  "provider.unsupported-operation",
  "provider.no-route",
  "provider.transport",
  "provider.timeout",
  "permission.rejected",
  "tool.execution",
  "unknown",
])

/** Parse `provider/model` or `provider/model#variant`, the same shape the model picker writes. */
const parseRef = (value) => {
  if (typeof value !== "string") return undefined
  const trimmed = value.trim()
  const hash = trimmed.indexOf("#")
  const variant = hash === -1 ? undefined : trimmed.slice(hash + 1)
  const target = hash === -1 ? trimmed : trimmed.slice(0, hash)
  const slash = target.indexOf("/")
  if (slash <= 0 || slash === target.length - 1) return undefined
  if (variant !== undefined && variant.length === 0) return undefined
  return {
    providerID: target.slice(0, slash),
    id: target.slice(slash + 1),
    ...(variant === undefined ? {} : { variant }),
  }
}

const refKey = (ref) => `${ref.providerID}/${ref.id}`
const sameRef = (a, b) => a.providerID === b.providerID && a.id === b.id

/** Coerce the config file into the shape the decision uses, dropping whatever cannot be understood. */
const normalizeConfig = (raw) => {
  const value = raw === null || typeof raw !== "object" ? {} : raw
  const chains = Array.isArray(value.chains)
    ? value.chains
        .map((chain) => (Array.isArray(chain) ? chain.map(parseRef).filter(Boolean) : []))
        // A chain shorter than two entries cannot fail over to anything.
        .filter((chain) => chain.length > 1)
        .map((chain) => chain.filter((ref, index) => index === 0 || !sameRef(ref, chain[index - 1])))
    : []
  const finite = (candidate, fallback) =>
    typeof candidate === "number" && Number.isFinite(candidate) && candidate >= 0 ? candidate : fallback
  return {
    enabled: value.enabled !== false,
    chains,
    cooldownMinutes: finite(value.cooldownMinutes, DEFAULTS.cooldownMinutes),
    rateLimitAttempts: finite(value.rateLimitAttempts, DEFAULTS.rateLimitAttempts),
    switchDelayMs: finite(value.switchDelayMs, DEFAULTS.switchDelayMs),
  }
}

/** Read the chain file. A missing or unreadable file disables failover instead of failing the plugin. */
const loadConfig = async (path = join(configDirectory(), CONFIG_FILENAME)) => {
  try {
    return normalizeConfig(JSON.parse(await readFile(path, "utf8")))
  } catch (error) {
    if (error?.code === "ENOENT") return normalizeConfig({})
    throw error
  }
}

/**
 * Whether a failure should move the session to another model.
 * `attempt` is the number of the attempt about to be made, so the first
 * failure of a step reports 2 (session/runner/retry.ts increments before it
 * reports). `rateLimitAttempts: 4` therefore means "after three failures".
 */
const classify = ({ error, attempt, rateLimitAttempts }) => {
  const type = typeof error?.type === "string" ? error.type : ""
  if (EXHAUSTED.has(type)) return "exhausted"
  if (type === "provider.rate-limit" && (error?.retryAfterMs ?? 0) >= LONG_RETRY_AFTER_MS) return "exhausted"
  if (FLAKY.has(type)) return attempt >= rateLimitAttempts ? "throttled" : "wait"
  // Request-scoped failures, and any failure this plugin does not recognize,
  // keep the built-in decision: moving the session would not change the
  // outcome, and guessing at an unfamiliar error is worse than retrying.
  return "never"
}

/**
 * Pick the next model for a failed one, or return undefined to leave the
 * built-in retry decision alone.
 *
 * `available` holds `provider/model` keys the location can serve; `cooling`
 * holds the provider and model keys inside their cooldown; `switches` is how
 * many times this session already moved during the current turn.
 *
 * A plan failure disqualifies the whole provider for this decision: another
 * model on an exhausted plan would refuse the same way. A throttle disqualifies
 * only the model that returned it, so a lighter model on the same plan is still
 * worth a try.
 */
const plan = ({ config, model, verdict, available, cooling, switches, now }) => {
  if (!config.enabled) return undefined
  const chain = config.chains.find((candidate) => candidate.some((ref) => sameRef(ref, model)))
  if (!chain) return undefined
  const index = chain.findIndex((ref) => sameRef(ref, model))
  // The last model in a chain has nowhere to go, and the turn may not exceed
  // one switch per remaining link.
  if (index < 0 || index >= chain.length - 1) return undefined
  if (switches >= chain.length - 1) return undefined
  const candidate = chain
    .slice(index + 1)
    .find(
      (ref) =>
        available.has(refKey(ref)) &&
        (cooling.providers.get(ref.providerID) ?? 0) <= now &&
        (cooling.models.get(refKey(ref)) ?? 0) <= now &&
        !(verdict === "exhausted" && ref.providerID === model.providerID),
    )
  if (!candidate) return undefined
  return { model: candidate, reason: verdict }
}

/** Append one line to the switch log. Observability only; never throws. */
const createLog = (path = join(stateDirectory(), LOG_FILENAME)) => async (record) => {
  try {
    await mkdir(dirname(path), { recursive: true })
    await appendFile(path, `${JSON.stringify({ time: new Date().toISOString(), ...record })}\n`, "utf8")
  } catch {
    // A missing state directory must not affect a turn.
  }
}

/** Per-process failover state: provider and model cooldowns, and each session's switch budget. */
const createState = () => {
  const providers = new Map()
  const models = new Map()
  const switches = new Map()
  const cool = (map, key, now, minutes) => map.set(key, now + minutes * 60_000)
  return {
    cooling: { providers, models },
    // A plan failure refuses the whole provider; a throttle refuses one model.
    coolProvider: (providerID, now, minutes) => cool(providers, providerID, now, minutes),
    coolModel: (ref, now, minutes) => cool(models, refKey(ref), now, minutes),
    isCooling: (ref, now) =>
      (providers.get(ref.providerID) ?? 0) > now || (models.get(refKey(ref)) ?? 0) > now,
    count: (sessionID) => switches.get(sessionID) ?? 0,
    charge: (sessionID) => switches.set(sessionID, (switches.get(sessionID) ?? 0) + 1),
    reset: (sessionID) => switches.delete(sessionID),
  }
}

export default {
  id: "model-failover",
  async setup(ctx) {
    const log = createLog()
    let config
    try {
      config = await loadConfig()
    } catch (error) {
      await log({ action: "disabled", reason: "unreadable config", message: String(error?.message ?? error) })
      return
    }
    if (!config.enabled || config.chains.length === 0) return

    // One line per load: the plugin reloads with the service and whenever its
    // files change, so this is the cheap way to confirm what is armed.
    await log({
      action: "ready",
      chains: config.chains.map((chain) => chain.map(refKey).join(" -> ")),
      cooldownMinutes: config.cooldownMinutes,
      rateLimitAttempts: config.rateLimitAttempts,
    })

    const state = createState()
    let models = undefined

    const available = async () => {
      if (models !== undefined && models.until > Date.now()) return models.keys
      const listed = await ctx.model.list()
      const keys = new Set(
        (listed?.data ?? [])
          .filter((model) => model && model.enabled !== false)
          .map((model) => refKey({ providerID: model.providerID, id: model.id })),
      )
      models = { keys, until: Date.now() + MODELS_TTL_MS }
      return keys
    }

    // A new prompt starts a new turn, so a plan that recovered is tried again.
    await ctx.session.hook("prompt", (event) => {
      state.reset(event.sessionID)
    })

    await ctx.session.hook("retry", async (event) => {
      try {
        const verdict = classify({
          error: event.error,
          attempt: event.attempt,
          rateLimitAttempts: config.rateLimitAttempts,
        })
        if (verdict === "never" || verdict === "wait") return
        const now = Date.now()
        const decision = plan({
          config,
          model: event.model,
          verdict,
          available: await available(),
          cooling: state.cooling,
          switches: state.count(event.sessionID),
          now,
        })
        if (!decision) return
        // Switch first: forcing a retry without a working target would spend
        // another request on the provider that just refused this one.
        await ctx.session.switchModel({ sessionID: event.sessionID, model: decision.model })
        event.decision = { retry: true, delay: config.switchDelayMs }
        state.charge(event.sessionID)
        if (verdict === "exhausted") state.coolProvider(event.model.providerID, now, config.cooldownMinutes)
        else state.coolModel(event.model, now, config.cooldownMinutes)
        await log({
          action: "switch",
          sessionID: event.sessionID,
          from: refKey(event.model),
          to: refKey(decision.model),
          reason: decision.reason,
          error: event.error?.type,
          attempt: event.attempt,
        })
      } catch (error) {
        // Never turn a failover attempt into a failed turn: the built-in retry
        // decision stays in force.
        await log({
          action: "error",
          sessionID: event.sessionID,
          from: refKey(event.model),
          message: String(error?.message ?? error),
        })
      }
    })
  },
}

export const internals = {
  CONFIG_FILENAME,
  DEFAULTS,
  EXHAUSTED,
  FLAKY,
  NEVER_SWITCH,
  LONG_RETRY_AFTER_MS,
  normalizeConfig,
  loadConfig,
  configDirectory,
  stateDirectory,
  parseRef,
  refKey,
  classify,
  plan,
  createState,
  createLog,
}
