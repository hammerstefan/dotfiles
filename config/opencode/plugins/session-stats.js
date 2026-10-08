// OpenCode V2 plugin: session-stats
//
// Aggregates cost and token usage for the current session tree by walking
// parent and child sessions and summing assistant-message usage. Exposes a
// single `session_tree_stats` tool that returns a markdown snapshot.

const MAX_SESSIONS = 10_000
const MAX_MESSAGES_PER_SESSION = 100_000

/** @typedef {{ input:number, output:number, reasoning:number, cacheRead:number, cacheWrite:number }} Tokens */
/** @typedef {{ sessions:Set<string>, messages:number, cost:number, tokens:Tokens }} Aggregate */
/** @typedef {{ sessionID:string, parentID:string|undefined, title:string, depth:number, cost:number, tokens:Tokens, messages:number, agents:Map<string,Aggregate>, models:Map<string,Aggregate> }} SessionStats */

const emptyTokens = () => ({
  input: 0,
  output: 0,
  reasoning: 0,
  cacheRead: 0,
  cacheWrite: 0,
})

const addTokens = (target, source) => {
  target.input += source.input
  target.output += source.output
  target.reasoning += source.reasoning
  target.cacheRead += source.cacheRead
  target.cacheWrite += source.cacheWrite
}

const messageTokens = (message) => ({
  input: message.tokens.input,
  output: message.tokens.output,
  reasoning: message.tokens.reasoning,
  cacheRead: message.tokens.cache.read,
  cacheWrite: message.tokens.cache.write,
})

const formatCost = (cost) => `$${cost.toFixed(6)}`
const formatNumber = (value) => value.toLocaleString("en-US")
const escapeCell = (value) => value.replaceAll("|", "\\|").replaceAll("\n", " ")

const buildAggregate = () => ({
  sessions: new Set(),
  messages: 0,
  cost: 0,
  tokens: emptyTokens(),
})

const aggregateInto = (target, source) => {
  target.sessions.add(source.sessionID)
  target.messages += source.messages
  target.cost += source.cost
  addTokens(target.tokens, source.tokens)
}

export default {
  id: "session-stats",
  async setup(ctx) {
    await ctx.tool.transform((editor) => {
      editor.add({
        name: "session_tree_stats",
        description:
          "Read and deterministically aggregate cost and token usage for the current OpenCode session tree",
        input: {
          type: "object",
          properties: {},
          additionalProperties: false,
        },
        async execute(_input, context) {
          const sessionID = context.sessionID
          const directory = context.directory
          const signal = context.signal ?? context.abort
          const checkAbort = () => {
            if (signal?.aborted) throw new Error("session statistics request aborted")
          }

          const failures = []

          const getSession = async (id) => {
            const response = await ctx.session.get({ sessionID: id, directory })
            if (!response.data) {
              const status = response.response?.status ?? "unknown"
              throw new Error(`session lookup failed with HTTP ${status}`)
            }
            return response.data
          }

          let root = await getSession(sessionID)
          const ancestors = new Set([root.id])
          while (root.parentID) {
            if (ancestors.has(root.parentID)) {
              throw new Error(`cycle detected while resolving parent ${root.parentID}`)
            }
            ancestors.add(root.parentID)
            root = await getSession(root.parentID)
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

            const response = await ctx.session.children({
              sessionID: current.session.id,
              directory,
            })
            if (!response.data) {
              const status = response.response?.status ?? "unknown"
              failures.push(
                `${current.session.id}: child lookup failed with HTTP ${status}`,
              )
              continue
            }

            const children = response.data
              .slice()
              .sort((a, b) => a.id.localeCompare(b.id))
            for (const child of children) {
              if (child.parentID !== current.session.id) {
                failures.push(
                  `${child.id}: API returned parent ${child.parentID ?? "<none>"}, expected ${current.session.id}`,
                )
                continue
              }
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
            const response = await ctx.session.messages({
              sessionID: entry.session.id,
              directory,
              limit: MAX_MESSAGES_PER_SESSION,
            })
            if (!response.data) {
              const status = response.response?.status ?? "unknown"
              failures.push(
                `${entry.session.id}: message lookup failed with HTTP ${status}`,
              )
              continue
            }
            const messages = response.data
            if (messages.length >= MAX_MESSIONS_PER_SESSION) {
              failures.push(
                `${entry.session.id}: reached the ${MAX_MESSAGES_PER_SESSION.toLocaleString("en-US")} message limit; totals may be incomplete`,
              )
            }

            const item = {
              sessionID: entry.session.id,
              parentID: entry.session.parentID,
              title: entry.session.title,
              depth: entry.depth,
              cost: 0,
              tokens: emptyTokens(),
              messages: 0,
              agents: new Map(),
              models: new Map(),
            }

            for (const message of messages) {
              if (message.info.role !== "assistant") continue
              const assistant = message.info
              const tokens = messageTokens(assistant)
              const agent = assistant.mode || "unknown"
              const model = `${assistant.providerID}/${assistant.modelID}`

              const agentAggregate = item.agents.get(agent) ?? buildAggregate()
              const modelAggregate = item.models.get(model) ?? buildAggregate()

              item.messages += 1
              item.cost += assistant.cost
              addTokens(item.tokens, tokens)
              agentAggregate.sessions.add(entry.session.id)
              agentAggregate.messages += 1
              agentAggregate.cost += assistant.cost
              addTokens(agentAggregate.tokens, tokens)
              item.agents.set(agent, agentAggregate)
              modelAggregate.sessions.add(entry.session.id)
              modelAggregate.messages += 1
              modelAggregate.cost += assistant.cost
              addTokens(modelAggregate.tokens, tokens)
              item.models.set(model, modelAggregate)
            }
            stats.push(item)
          }

          const total = buildAggregate()
          const byAgent = new Map()
          const byModel = new Map()

          for (const item of stats) {
            aggregateInto(total, item)

            for (const [agent, agentStats] of item.agents) {
              const agentAggregate = byAgent.get(agent) ?? buildAggregate()
              for (const id of agentStats.sessions) agentAggregate.sessions.add(id)
              agentAggregate.messages += agentStats.messages
              agentAggregate.cost += agentStats.cost
              addTokens(agentAggregate.tokens, agentStats.tokens)
              byAgent.set(agent, agentAggregate)
            }

            for (const [model, modelStats] of item.models) {
              const modelAggregate = byModel.get(model) ?? buildAggregate()
              for (const id of modelStats.sessions) modelAggregate.sessions.add(id)
              modelAggregate.messages += modelStats.messages
              modelAggregate.cost += modelStats.cost
              addTokens(modelAggregate.tokens, modelStats.tokens)
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
            "## By Agent",
            "",
            "| Agent | Sessions | Messages | Cost | Input | Output | Reasoning | Cache read | Cache write |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ...[...byAgent.entries()]
              .sort(([left], [right]) => left.localeCompare(right))
              .map(
                ([agent, value]) =>
                  `| ${escapeCell(agent)} | ${value.sessions.size} | ${value.messages} | ${formatCost(value.cost)} | ${formatNumber(value.tokens.input)} | ${formatNumber(value.tokens.output)} | ${formatNumber(value.tokens.reasoning)} | ${formatNumber(value.tokens.cacheRead)} | ${formatNumber(value.tokens.cacheWrite)} |`,
              ),
            "",
            "## By Model",
            "",
            "| Model | Sessions | Messages | Cost | Input | Output | Reasoning | Cache read | Cache write |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ...[...byModel.entries()]
              .sort(([left], [right]) => left.localeCompare(right))
              .map(
                ([model, value]) =>
                  `| ${escapeCell(model)} | ${value.sessions.size} | ${value.messages} | ${formatCost(value.cost)} | ${formatNumber(value.tokens.input)} | ${formatNumber(value.tokens.output)} | ${formatNumber(value.tokens.reasoning)} | ${formatNumber(value.tokens.cacheRead)} | ${formatNumber(value.tokens.cacheWrite)} |`,
              ),
            "",
            "## Session Tree",
            "",
            "| Depth | Session | Agent | Model | Messages | Cost | Title |",
            "|---:|---|---|---|---:|---:|---|",
            ...stats
              .sort(
                (left, right) =>
                  left.depth - right.depth ||
                  left.sessionID.localeCompare(right.sessionID),
              )
              .map((item) => {
                const agents = [...item.agents.keys()].sort().join(", ") || "none"
                const models = [...item.models.keys()].sort().join(", ") || "none"
                return `| ${item.depth} | \`${item.sessionID}\` | ${escapeCell(agents)} | ${escapeCell(models)} | ${item.messages} | ${formatCost(item.cost)} | ${escapeCell(item.title)} |`
              }),
            "",
            "## Completeness",
            "",
            failures.length === 0
              ? "Complete for all usage recorded when the snapshot was taken."
              : `Partial result: ${failures.length} issue(s) occurred.`,
            "",
            "This snapshot excludes usage recorded after aggregation, including this command's final assistant response.",
          ]

          if (failures.length > 0) {
            lines.push("", ...failures.sort().map((failure) => `- ${failure}`))
          }

          return {
            title: "Session tree statistics",
            content: lines.join("\n"),
            metadata: {
              rootSessionID: root.id,
              sessions: sessions.length,
              aggregatedSessions: stats.length,
              totalCost: total.cost,
              complete: failures.length === 0,
            },
          }
        },
      })
    })
  },
}
