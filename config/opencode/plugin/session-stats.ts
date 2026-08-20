import type { Plugin } from "@opencode-ai/plugin"
import { tool } from "@opencode-ai/plugin"
import type { AssistantMessage, Session } from "@opencode-ai/sdk"

const MAX_SESSIONS = 10_000
const MAX_MESSAGES_PER_SESSION = 100_000

type Tokens = {
  input: number
  output: number
  reasoning: number
  cacheRead: number
  cacheWrite: number
}

type SessionStats = {
  session: Session
  depth: number
  cost: number
  tokens: Tokens
  messages: number
  agents: Map<string, Aggregate>
  models: Map<string, Aggregate>
}

type Aggregate = {
  sessions: Set<string>
  messages: number
  cost: number
  tokens: Tokens
}

const emptyTokens = (): Tokens => ({
  input: 0,
  output: 0,
  reasoning: 0,
  cacheRead: 0,
  cacheWrite: 0,
})

const addTokens = (target: Tokens, source: Tokens) => {
  target.input += source.input
  target.output += source.output
  target.reasoning += source.reasoning
  target.cacheRead += source.cacheRead
  target.cacheWrite += source.cacheWrite
}

const messageTokens = (message: AssistantMessage): Tokens => ({
  input: message.tokens.input,
  output: message.tokens.output,
  reasoning: message.tokens.reasoning,
  cacheRead: message.tokens.cache.read,
  cacheWrite: message.tokens.cache.write,
})

const formatCost = (cost: number) => `$${cost.toFixed(6)}`
const formatNumber = (value: number) => value.toLocaleString("en-US")
const escapeCell = (value: string) => value.replaceAll("|", "\\|").replaceAll("\n", " ")

const aggregateInto = (target: Aggregate, source: SessionStats) => {
  target.sessions.add(source.session.id)
  target.messages += source.messages
  target.cost += source.cost
  addTokens(target.tokens, source.tokens)
}

export const SessionStatsPlugin: Plugin = async ({ client }) => ({
  "tool.execute.after": async (input, output) => {
    if (input.tool !== "task" || input.args?.command !== "session-stats") return
    output.output = "Complete."
  },
  tool: {
    session_tree_stats: tool({
      description:
        "Read and deterministically aggregate cost and token usage for the current OpenCode session tree",
      args: {},
      async execute(_args, context) {
        context.metadata({ title: "Aggregate session tree statistics" })

        const failures: string[] = []
        const getSession = async (id: string) => {
          const response = await client.session.get({
            path: { id },
            query: { directory: context.directory },
          })
          if (!response.data) {
            throw new Error(`session lookup failed with HTTP ${response.response.status}`)
          }
          return response.data
        }

        let root = await getSession(context.sessionID)
        const ancestors = new Set([root.id])
        while (root.parentID) {
          if (ancestors.has(root.parentID)) {
            throw new Error(`cycle detected while resolving parent ${root.parentID}`)
          }
          ancestors.add(root.parentID)
          root = await getSession(root.parentID)
        }

        const queue: Array<{ session: Session; depth: number }> = [{ session: root, depth: 0 }]
        const discovered = new Set<string>()
        const sessions: Array<{ session: Session; depth: number }> = []

        while (queue.length > 0) {
          if (context.abort.aborted) throw new Error("session statistics request aborted")
          const current = queue.shift()
          if (!current || discovered.has(current.session.id)) continue
          if (discovered.size >= MAX_SESSIONS) {
            throw new Error(`session tree exceeds the ${MAX_SESSIONS.toLocaleString("en-US")} session limit`)
          }

          discovered.add(current.session.id)
          sessions.push(current)

          const response = await client.session.children({
            path: { id: current.session.id },
            query: { directory: context.directory },
          })
          if (!response.data) {
            failures.push(
              `${current.session.id}: child lookup failed with HTTP ${response.response.status}`,
            )
            continue
          }

          for (const child of response.data.sort((a, b) => a.id.localeCompare(b.id))) {
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

        const stats: SessionStats[] = []
        for (const entry of sessions) {
          if (context.abort.aborted) throw new Error("session statistics request aborted")
          const response = await client.session.messages({
            path: { id: entry.session.id },
            query: { directory: context.directory, limit: MAX_MESSAGES_PER_SESSION },
          })
          if (!response.data) {
            failures.push(
              `${entry.session.id}: message lookup failed with HTTP ${response.response.status}`,
            )
            continue
          }
          if (response.data.length >= MAX_MESSAGES_PER_SESSION) {
            failures.push(
              `${entry.session.id}: reached the ${MAX_MESSAGES_PER_SESSION.toLocaleString("en-US")} message limit; totals may be incomplete`,
            )
          }

          const item: SessionStats = {
            session: entry.session,
            depth: entry.depth,
            cost: 0,
            tokens: emptyTokens(),
            messages: 0,
            agents: new Map(),
            models: new Map(),
          }

          for (const message of response.data) {
            if (message.info.role !== "assistant") continue
            const assistant = message.info
            const tokens = messageTokens(assistant)
            const agent = assistant.mode || "unknown"
            const model = `${assistant.providerID}/${assistant.modelID}`
            const agentAggregate = item.agents.get(agent) ?? {
              sessions: new Set<string>(),
              messages: 0,
              cost: 0,
              tokens: emptyTokens(),
            }
            const modelAggregate = item.models.get(model) ?? {
              sessions: new Set<string>(),
              messages: 0,
              cost: 0,
              tokens: emptyTokens(),
            }

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

        const total: Aggregate = {
          sessions: new Set(),
          messages: 0,
          cost: 0,
          tokens: emptyTokens(),
        }
        const byAgent = new Map<string, Aggregate>()
        const byModel = new Map<string, Aggregate>()

        for (const item of stats) {
          aggregateInto(total, item)

          for (const [agent, agentStats] of item.agents) {
            const agentAggregate = byAgent.get(agent) ?? {
              sessions: new Set<string>(),
              messages: 0,
              cost: 0,
              tokens: emptyTokens(),
            }
            for (const id of agentStats.sessions) agentAggregate.sessions.add(id)
            agentAggregate.messages += agentStats.messages
            agentAggregate.cost += agentStats.cost
            addTokens(agentAggregate.tokens, agentStats.tokens)
            byAgent.set(agent, agentAggregate)
          }

          for (const [model, modelStats] of item.models) {
            const modelAggregate = byModel.get(model) ?? {
              sessions: new Set<string>(),
              messages: 0,
              cost: 0,
              tokens: emptyTokens(),
            }
            for (const id of modelStats.sessions) modelAggregate.sessions.add(id)
            modelAggregate.messages += modelStats.messages
            modelAggregate.cost += modelStats.cost
            addTokens(modelAggregate.tokens, modelStats.tokens)
            byModel.set(model, modelAggregate)
          }
        }

        const rootStats = stats.find((item) => item.session.id === root.id)
        const rootCost = rootStats?.cost ?? 0
        const maximumDepth = sessions.reduce((maximum, item) => Math.max(maximum, item.depth), 0)
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
          "| Depth | Session | Agent | Messages | Cost | Title |",
          "|---:|---|---|---:|---:|---|",
          ...stats
            .sort((left, right) => left.depth - right.depth || left.session.id.localeCompare(right.session.id))
            .map((item) => {
              const agents = [...item.agents.keys()].sort().join(", ") || "none"
              return `| ${item.depth} | \`${item.session.id}\` | ${escapeCell(agents)} | ${item.messages} | ${formatCost(item.cost)} | ${escapeCell(item.session.title)} |`
            }),
          "",
          "## Completeness",
          "",
          failures.length === 0
            ? "Complete for all usage recorded when the snapshot was taken."
            : `Partial result: ${failures.length} issue(s) occurred.`,
          "",
          "This snapshot excludes usage recorded after aggregation, including this command's final Luna response.",
        ]

        if (failures.length > 0) {
          lines.push("", ...failures.sort().map((failure) => `- ${failure}`))
        }

        return {
          title: "Session tree statistics",
          output: lines.join("\n"),
          metadata: {
            rootSessionID: root.id,
            sessions: sessions.length,
            aggregatedSessions: stats.length,
            totalCost: total.cost,
            complete: failures.length === 0,
          },
        }
      },
    }),
  },
})
