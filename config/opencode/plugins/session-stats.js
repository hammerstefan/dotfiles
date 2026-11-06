// OpenCode V2 plugin: session-stats
//
// Aggregates cost, token usage, and generation throughput for the current
// session tree by walking parent and child sessions and summing
// assistant-message usage. Exposes a single `session_tree_stats` tool that
// returns a markdown snapshot.
//
// V2 plugin-context API (verified against OpenCode 2.2.5):
// - `ctx.session.get({ sessionID })` resolves to a `Session.Info` object.
// - `ctx.session.list({ parentID, directory, limit, cursor })` resolves to a
//   page `{ data: Session.Info[], cursor }`. The `parentID` filter is served by
//   the server, so the tree can be indexed without a per-parent request.
// - `ctx.session.context({ sessionID })` resolves to `{ data:
//   Session.Message.Info[] }`.
// - There is no `ctx.session.children()` and no `ctx.session.messages()`.
//   Calling either throws, so the tree is built from one paginated
//   `ctx.session.list()` call and messages come from `ctx.session.context()`.
// - The tool execute context exposes no `directory`, so the session directory
//   comes from the session info and falls back to `ctx.location.directory`.
// - Assistant messages carry `type: "assistant"` (not `role`), the agent id in
//   `agent`, and the model in `model: { providerID, id, variant }`.
//
// The plugin context reads sessions over HTTP from the OpenCode server. That
// client can hold a stale service endpoint, for example when the service is
// restarted while a long-lived server keeps the old address. The read then
// fails at the transport level and reports no HTTP status. Every read is
// therefore retried against the service API using the endpoint from the
// service descriptor, and no single failed read aborts the report.
//
// Throughput uses the same definition as the TUI's "tok/s" footer:
//   tokens  = output + reasoning tokens of the measured steps
//   seconds = sum of (time.streamed - time.created) over the measured steps
//   TPS     = tokens / seconds
// `time.streamed` is the end of the generation window, so tool execution time
// is excluded. Steps without a `time.streamed` stamp are not measurable and
// are reported separately instead of silently skewing the average.

import { readFile } from "node:fs/promises"
import { homedir } from "node:os"
import { join } from "node:path"

const MAX_SESSIONS = 10_000
const MAX_LIST_PAGES = 50
const LIST_PAGE_SIZE = 200

/** @typedef {{ input:number, output:number, reasoning:number, cacheRead:number, cacheWrite:number }} Tokens */
/** @typedef {{ sessions:Set<string>, messages:number, cost:number, tokens:Tokens, generatedTokens:number, generationMs:number, measuredSteps:number, unmeasuredSteps:number }} Aggregate */
/** @typedef {{ sessionID:string, parentID:string|undefined, title:string, depth:number, cost:number, tokens:Tokens, messages:number, generatedTokens:number, generationMs:number, measuredSteps:number, unmeasuredSteps:number, agents:Map<string,Aggregate>, models:Map<string,Aggregate> }} SessionStats */

const emptyTokens = () => ({
  input: 0,
  output: 0,
  reasoning: 0,
  cacheRead: 0,
  cacheWrite: 0,
})

const emptyAggregate = () => ({
  sessions: new Set(),
  messages: 0,
  cost: 0,
  tokens: emptyTokens(),
  generatedTokens: 0,
  generationMs: 0,
  measuredSteps: 0,
  unmeasuredSteps: 0,
})

const addTokens = (target, source) => {
  target.input += source.input
  target.output += source.output
  target.reasoning += source.reasoning
  target.cacheRead += source.cacheRead
  target.cacheWrite += source.cacheWrite
}

const addAggregate = (target, source) => {
  target.messages += source.messages
  target.cost += source.cost
  addTokens(target.tokens, source.tokens)
  target.generatedTokens += source.generatedTokens
  target.generationMs += source.generationMs
  target.measuredSteps += source.measuredSteps
  target.unmeasuredSteps += source.unmeasuredSteps
}

const messageTokens = (message) => ({
  input: message.tokens?.input ?? 0,
  output: message.tokens?.output ?? 0,
  reasoning: message.tokens?.reasoning ?? 0,
  cacheRead: message.tokens?.cache?.read ?? 0,
  cacheWrite: message.tokens?.cache?.write ?? 0,
})

const isRecord = (value) => typeof value === "object" && value !== null

/** Unwrap a plugin-context payload that may or may not carry a `data` envelope. */
const unwrap = (value) => (isRecord(value) && "data" in value ? value.data : value)

/** Normalise a plugin-context payload into `{ data, cursor }`. */
const pageOf = (value) => {
  if (isRecord(value) && Array.isArray(value.data)) return { data: value.data, cursor: value.cursor }
  if (Array.isArray(value)) return { data: value, cursor: undefined }
  return { data: [], cursor: undefined }
}

/** Human-readable reason for a thrown value. */
const describeError = (error) => (error instanceof Error ? error.message : String(error))

/**
 * Location of the live OpenCode service descriptor.
 *
 * The service writes `{ id, version, url, pid, password }` here on start, so
 * the file always describes the server that is currently running.
 */
const serviceDescriptorPath = () => {
  const state = process.env.XDG_STATE_HOME ?? join(homedir(), ".local", "state")
  return join(state, "opencode", "service.json")
}

/**
 * Read the live service endpoint, or undefined when no service is running.
 *
 * The password is the basic-auth secret the service requires; the username is
 * always `opencode`.
 */
export const readServiceEndpoint = async () => {
  try {
    const raw = await readFile(serviceDescriptorPath(), "utf8")
    const parsed = JSON.parse(raw)
    if (typeof parsed?.url !== "string" || parsed.url.length === 0) return undefined
    return {
      url: parsed.url,
      password: typeof parsed.password === "string" ? parsed.password : undefined,
    }
  } catch {
    return undefined
  }
}

/** Perform one request against the OpenCode service API. */
const serviceRequest = async (endpoint, pathname, query) => {
  const url = new URL(pathname, endpoint.url)
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value === undefined || value === null) continue
    url.searchParams.set(key, String(value))
  }
  const headers = {}
  if (endpoint.password !== undefined) {
    const credentials = Buffer.from(`opencode:${endpoint.password}`).toString("base64")
    headers.authorization = `Basic ${credentials}`
  }
  const response = await fetch(url, { headers })
  if (!response.ok) throw new Error(`GET ${pathname} failed with HTTP ${response.status}`)
  return response.json()
}

/**
 * Session data access for the plugin.
 *
 * Every read goes through the plugin context first. The plugin context talks
 * to the OpenCode server over HTTP, and that client can point at a stale
 * service endpoint: the service is restarted, or another OpenCode instance
 * rewrites the service descriptor, and the long-lived server keeps the old
 * address. The read then fails at the transport level, with no HTTP status to
 * report.
 *
 * When that happens the read is retried against the service API directly,
 * using the endpoint from the service descriptor, which always names the
 * server that is running. Recovered degradations are collected in `notes`;
 * data that could not be recovered at all is collected in `failures`.
 */
export const createSessionService = (ctx, options = {}) => {
  const endpointResolver = options.endpointResolver ?? readServiceEndpoint
  const request = options.request ?? serviceRequest
  const notes = []
  const failures = []

  const withFallback = async (label, primary, fallback) => {
    try {
      return await primary()
    } catch (error) {
      notes.push(`${label} failed (${describeError(error)}); retried through the service API`)
      try {
        return await fallback()
      } catch (fallbackError) {
        failures.push(
          `${label} failed (${describeError(error)}); the service API fallback failed too (${describeError(fallbackError)})`,
        )
        throw fallbackError
      }
    }
  }

  const endpoint = async () => {
    const resolved = await endpointResolver()
    if (!resolved) throw new Error("no OpenCode service endpoint is available")
    return resolved
  }

  return {
    notes,
    failures,
    async get(sessionID) {
      const info = await withFallback(
        `session lookup for ${sessionID}`,
        async () => unwrap(await ctx.session.get({ sessionID })),
        async () => unwrap(await request(await endpoint(), `/api/session/${encodeURIComponent(sessionID)}`)),
      )
      if (!info?.id) throw new Error(`session lookup for ${sessionID} returned no session record`)
      return info
    },
    async list(params) {
      return withFallback(
        "session listing",
        async () => pageOf(await ctx.session.list(params)),
        async () => pageOf(await request(await endpoint(), "/api/session", params)),
      )
    },
    async context(sessionID) {
      return withFallback(
        `message lookup for ${sessionID}`,
        async () => pageOf(await ctx.session.context({ sessionID })).data,
        async () =>
          pageOf(
            await request(await endpoint(), `/api/session/${encodeURIComponent(sessionID)}/context`),
          ).data,
      )
    },
  }
}

const isAssistant = (message) => message?.type === "assistant" || message?.role === "assistant"

const agentName = (info) => info?.agent ?? info?.mode ?? "unknown"

const modelName = (info) => {
  const model = info?.model
  if (model && typeof model === "object") {
    const base = `${model.providerID ?? "unknown"}/${model.id ?? "unknown"}`
    return model.variant ? `${base} (${model.variant})` : base
  }
  if (info?.providerID || info?.modelID) {
    return `${info.providerID ?? "unknown"}/${info.modelID ?? "unknown"}`
  }
  return "unknown"
}

/**
 * Generation window of one assistant step.
 *
 * `measured` is the provider generation span in milliseconds, or undefined when
 * the step carries no `time.streamed` stamp and therefore cannot be measured.
 */
const measureStep = (message, tokens = messageTokens(message)) => {
  const created = message.time?.created
  const streamed = message.time?.streamed
  const generated = tokens.output + tokens.reasoning
  const measured =
    typeof created === "number" && typeof streamed === "number"
      ? Math.max(0, streamed - created)
      : undefined
  return { generated, measured }
}

/** Output tokens per second, using OpenCode's own "tok/s" definition. */
const throughput = (aggregate) => {
  if (aggregate.generatedTokens <= 0 || aggregate.generationMs <= 0) return undefined
  return aggregate.generatedTokens / (aggregate.generationMs / 1000)
}

const formatCost = (cost) => `$${cost.toFixed(6)}`
const formatNumber = (value) => value.toLocaleString("en-US")
const escapeCell = (value) =>
  String(value ?? "")
    .replaceAll("|", "\\|")
    .replaceAll("\n", " ")

const formatTps = (value) => (value === undefined ? "n/a" : value.toFixed(1))

const formatDuration = (milliseconds) => {
  const seconds = milliseconds / 1000
  if (seconds >= 3600) return `${(seconds / 3600).toFixed(2)} h`
  if (seconds >= 60) return `${(seconds / 60).toFixed(1)} min`
  return `${seconds.toFixed(1)} s`
}

export const internals = {
  measureStep,
  throughput,
  formatTps,
  formatDuration,
  unwrap,
  pageOf,
  createSessionService,
  readServiceEndpoint,
  serviceDescriptorPath,
}

export default {
  id: "session-stats",
  async setup(ctx) {
    await ctx.tool.transform((editor) => {
      editor.add({
        name: "session_tree_stats",
        description:
          "Read and deterministically aggregate cost, token usage, and output throughput (tokens per second) for the current OpenCode session tree",
        input: {
          type: "object",
          properties: {},
          additionalProperties: false,
        },
        async execute(_input, context) {
          const sessionID = context.sessionID
          const signal = context.signal ?? context.abort
          const checkAbort = () => {
            if (signal?.aborted) throw new Error("session statistics request aborted")
          }

          const service = createSessionService(ctx)
          const failures = service.failures

          // A session lookup can fail when the server cannot serve its own API
          // (for example a long-lived background server with a stale plugin
          // instance). The service retries such a read against the service API,
          // and the report continues without the session record when that also
          // fails.
          let currentSession
          try {
            currentSession = await service.get(sessionID)
          } catch {
            // The failure is already recorded by the service.
          }
          const directory = currentSession?.location?.directory ?? ctx.location?.directory

          // One paginated listing gives the whole tree: every session carries its
          // parent id, so indexing by parent is enough to walk down from the root.
          const byParent = new Map()
          const known = new Map()
          let cursor
          let truncated = false
          let listed = false
          for (let page = 0; page < MAX_LIST_PAGES; page++) {
            checkAbort()
            const params = { directory, limit: LIST_PAGE_SIZE }
            if (cursor) params.cursor = cursor
            let result
            try {
              result = await service.list(params)
            } catch {
              // The failure is already recorded by the service.
              break
            }
            listed = true
            for (const session of result.data) {
              if (!session?.id) continue
              known.set(session.id, session)
              if (!session.parentID) continue
              const bucket = byParent.get(session.parentID) ?? []
              bucket.push(session)
              byParent.set(session.parentID, bucket)
            }
            const next = result.cursor?.next
            if (!next) break
            cursor = next
            if (known.size >= MAX_SESSIONS) {
              truncated = true
              break
            }
          }
          if (truncated) {
            failures.push(
              `session listing reached the ${MAX_SESSIONS.toLocaleString("en-US")} session limit; the tree may be incomplete`,
            )
          }
          if (currentSession) known.set(currentSession.id, currentSession)

          // Resolve the root of the tree by walking up through parent ids.
          let root = currentSession ?? known.get(sessionID)
          if (!root) {
            failures.push(`session ${sessionID} is not in the session listing; the tree root is unknown`)
            root = { id: sessionID, parentID: undefined, title: "unknown" }
          }
          const ancestors = new Set([root.id])
          while (root.parentID) {
            if (ancestors.has(root.parentID)) {
              throw new Error(`cycle detected while resolving parent ${root.parentID}`)
            }
            ancestors.add(root.parentID)
            const parent = known.get(root.parentID)
            if (parent) {
              root = parent
              continue
            }
            try {
              root = await service.get(root.parentID)
            } catch {
              // The failure is already recorded by the service.
              failures.push(`the tree root is unknown because parent ${root.parentID} is unavailable`)
              break
            }
          }

          const queue = [{ session: root, depth: 0 }]
          const discovered = new Set()
          /** @type {Array<{ session:any, depth:number }>} */
          const sessions = []

          while (queue.length > 0) {
            checkAbort()
            const current = queue.shift()
            if (!current || discovered.has(current.session.id)) continue
            if (discovered.size >= MAX_SESSIONS) {
              throw new Error(
                `session tree exceeds the ${MAX_SESSIONS.toLocaleString("en-US")} session limit`,
              )
            }

            discovered.add(current.session.id)
            sessions.push(current)

            const children = (byParent.get(current.session.id) ?? []).slice()
            children.sort((a, b) => a.id.localeCompare(b.id))
            for (const child of children) {
              if (discovered.has(child.id)) {
                failures.push(`${child.id}: duplicate or cyclic child reference ignored`)
                continue
              }
              queue.push({ session: child, depth: current.depth + 1 })
            }
          }

          /** @type {SessionStats[]} */
          const stats = []
          for (const entry of sessions) {
            checkAbort()
            let messages
            try {
              messages = await service.context(entry.session.id)
            } catch {
              // The failure is already recorded by the service.
              failures.push(`${entry.session.id}: message lookup failed`)
              continue
            }

            const item = {
              sessionID: entry.session.id,
              parentID: entry.session.parentID,
              title: entry.session.title,
              depth: entry.depth,
              cost: 0,
              tokens: emptyTokens(),
              messages: 0,
              generatedTokens: 0,
              generationMs: 0,
              measuredSteps: 0,
              unmeasuredSteps: 0,
              agents: new Map(),
              models: new Map(),
            }

            for (const message of messages) {
              if (!isAssistant(message)) continue
              const tokens = messageTokens(message)
              const agent = agentName(message)
              const model = modelName(message)

              const agentAggregate = item.agents.get(agent) ?? emptyAggregate()
              const modelAggregate = item.models.get(model) ?? emptyAggregate()

              // Throughput window: the provider generation span of this step.
              const { generated, measured } = measureStep(message, tokens)

              item.messages += 1
              item.cost += message.cost ?? 0
              addTokens(item.tokens, tokens)
              agentAggregate.sessions.add(entry.session.id)
              agentAggregate.messages += 1
              agentAggregate.cost += message.cost ?? 0
              addTokens(agentAggregate.tokens, tokens)
              item.agents.set(agent, agentAggregate)
              modelAggregate.sessions.add(entry.session.id)
              modelAggregate.messages += 1
              modelAggregate.cost += message.cost ?? 0
              addTokens(modelAggregate.tokens, tokens)
              item.models.set(model, modelAggregate)

              if (measured === undefined) {
                item.unmeasuredSteps += 1
                agentAggregate.unmeasuredSteps += 1
                modelAggregate.unmeasuredSteps += 1
                continue
              }
              item.generatedTokens += generated
              item.generationMs += measured
              item.measuredSteps += 1
              agentAggregate.generatedTokens += generated
              agentAggregate.generationMs += measured
              agentAggregate.measuredSteps += 1
              modelAggregate.generatedTokens += generated
              modelAggregate.generationMs += measured
              modelAggregate.measuredSteps += 1
            }
            stats.push(item)
          }

          const total = emptyAggregate()
          const byAgent = new Map()
          const byModel = new Map()

          for (const item of stats) {
            total.sessions.add(item.sessionID)
            addAggregate(total, item)

            for (const [agent, agentStats] of item.agents) {
              const agentAggregate = byAgent.get(agent) ?? emptyAggregate()
              for (const id of agentStats.sessions) agentAggregate.sessions.add(id)
              addAggregate(agentAggregate, agentStats)
              byAgent.set(agent, agentAggregate)
            }

            for (const [model, modelStats] of item.models) {
              const modelAggregate = byModel.get(model) ?? emptyAggregate()
              for (const id of modelStats.sessions) modelAggregate.sessions.add(id)
              addAggregate(modelAggregate, modelStats)
              byModel.set(model, modelAggregate)
            }
          }

          const rootStats = stats.find((item) => item.sessionID === root.id)
          const rootCost = rootStats?.cost ?? 0
          const maximumDepth = sessions.reduce(
            (maximum, item) => Math.max(maximum, item.depth),
            0,
          )
          const lines = [
            "# Session Tree Statistics",
            "",
            `**Root session:** \`${root.id}\``,
            `**Sessions discovered:** ${formatNumber(sessions.length)}`,
            `**Sessions aggregated:** ${formatNumber(stats.length)}`,
            `**Maximum depth:** ${formatNumber(maximumDepth)}`,
            `**Assistant messages:** ${formatNumber(total.messages)}`,
            `**Total cost:** ${formatCost(total.cost)}`,
            `**Root cost:** ${formatCost(rootCost)}`,
            `**Subagent cost:** ${formatCost(total.cost - rootCost)}`,
            "",
            "## Tokens",
            "",
            "| Input | Output | Reasoning | Cache read | Cache write |",
            "|---:|---:|---:|---:|---:|",
            `| ${formatNumber(total.tokens.input)} | ${formatNumber(total.tokens.output)} | ${formatNumber(total.tokens.reasoning)} | ${formatNumber(total.tokens.cacheRead)} | ${formatNumber(total.tokens.cacheWrite)} |`,
            "",
            "## Throughput",
            "",
            "Output tokens per second, measured over the provider generation window only. Tool execution time is excluded.",
            "",
            `**Output TPS:** ${formatTps(throughput(total))} tok/s`,
            `**Generated tokens:** ${formatNumber(total.generatedTokens)}`,
            `**Generation time:** ${formatDuration(total.generationMs)}`,
            `**Measured steps:** ${formatNumber(total.measuredSteps)} of ${formatNumber(total.messages)}`,
            ...(total.unmeasuredSteps > 0
              ? [
                  `**Unmeasured steps:** ${formatNumber(total.unmeasuredSteps)} (no generation window recorded)`,
                ]
              : []),
            "",
            "## By Agent",
            "",
            "| Agent | Sessions | Messages | Steps | Cost | Input | Output | Reasoning | Cache read | Cache write | TPS |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ...[...byAgent.entries()]
              .sort(([left], [right]) => left.localeCompare(right))
              .map(
                ([agent, value]) =>
                  `| ${escapeCell(agent)} | ${value.sessions.size} | ${value.messages} | ${value.measuredSteps} | ${formatCost(value.cost)} | ${formatNumber(value.tokens.input)} | ${formatNumber(value.tokens.output)} | ${formatNumber(value.tokens.reasoning)} | ${formatNumber(value.tokens.cacheRead)} | ${formatNumber(value.tokens.cacheWrite)} | ${formatTps(throughput(value))} |`,
              ),
            "",
            "## By Model",
            "",
            "| Model | Sessions | Messages | Steps | Cost | Input | Output | Reasoning | Cache read | Cache write | TPS |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ...[...byModel.entries()]
              .sort(([left], [right]) => left.localeCompare(right))
              .map(
                ([model, value]) =>
                  `| ${escapeCell(model)} | ${value.sessions.size} | ${value.messages} | ${value.measuredSteps} | ${formatCost(value.cost)} | ${formatNumber(value.tokens.input)} | ${formatNumber(value.tokens.output)} | ${formatNumber(value.tokens.reasoning)} | ${formatNumber(value.tokens.cacheRead)} | ${formatNumber(value.tokens.cacheWrite)} | ${formatTps(throughput(value))} |`,
              ),
            "",
            "## Session Tree",
            "",
            "| Depth | Session | Agent | Model | Messages | Steps | TPS | Cost | Title |",
            "|---:|---|---|---|---:|---:|---:|---:|---|",
            ...stats
              .sort(
                (left, right) =>
                  left.depth - right.depth ||
                  left.sessionID.localeCompare(right.sessionID),
              )
              .map((item) => {
                const agents = [...item.agents.keys()].sort().join(", ") || "none"
                const models = [...item.models.keys()].sort().join(", ") || "none"
                return `| ${item.depth} | \`${item.sessionID}\` | ${escapeCell(agents)} | ${escapeCell(models)} | ${item.messages} | ${item.measuredSteps} | ${formatTps(throughput(item))} | ${formatCost(item.cost)} | ${escapeCell(item.title)} |`
              }),
            "",
            "## Completeness",
            "",
            "Message counts cover each session's active context, which excludes messages before its last compaction.",
            "",
            failures.length === 0
              ? "Complete for all usage recorded when the snapshot was taken."
              : `Partial result: ${failures.length} issue(s) occurred.`,
            "",
            "This snapshot excludes usage recorded after aggregation, including this command's final assistant response.",
          ]

          if (!listed) {
            failures.push("the session listing is unavailable; the tree may be incomplete")
          }

          if (failures.length > 0) {
            lines.push("", "### Issues", "", ...failures.sort().map((failure) => `- ${failure}`))
          }

          if (service.notes.length > 0) {
            lines.push(
              "",
              "### Recovered degradations",
              "",
              ...[...new Set(service.notes)].sort().map((note) => `- ${note}`),
            )
          }

          return {
            title: "Session tree statistics",
            content: lines.join("\n"),
            metadata: {
              rootSessionID: root.id,
              sessions: sessions.length,
              aggregatedSessions: stats.length,
              totalCost: total.cost,
              outputTPS: throughput(total),
              generatedTokens: total.generatedTokens,
              generationMilliseconds: total.generationMs,
              measuredSteps: total.measuredSteps,
              complete: failures.length === 0,
              notes: service.notes.length,
            },
          }
        },
      })
    })
  },
}
