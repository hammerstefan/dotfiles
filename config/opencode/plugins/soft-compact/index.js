// OpenCode V2 plugin: soft-compact
//
// Adds `/soft-compact`, which arms a session for a soft compaction. When the
// context of the session reaches a threshold, the plugin asks the agent to
// wrap up, waits for it to stop, compacts the session with the summary focused
// on the remaining work, and then lets the agent continue.
//
// Why a plugin and not a setting:
// - `compaction.auto` compacts at `window - buffer`, without warning and
//   without the agent getting a chance to close the work it has open.
// - `compaction.buffer` cannot ask the agent to record where it stopped.
// - A soft compaction is a sequence (wrap up, wait, compact, resume) that no
//   setting expresses.
//
// The sequence, in order:
// 1. `armed`. The plugin measures the context after every assistant step and
//    on a timer. It measures the number the TUI shows: the last assistant
//    message's input, output, reasoning and cache tokens, summed.
// 2. `wrapping-up`. The plugin steers a prompt that tells the agent to finish
//    what it is doing, record its state and next steps with the
//    `soft_compact_checkpoint` tool, and stop. The agent may take a few more
//    steps when that completes an operation cleanly.
// 3. `compacting`. The plugin requests the compaction when the agent stops.
//    The agent stops in one of two ways: the session goes idle, or the agent
//    records its checkpoint. The checkpoint is the better signal, because a
//    session that another plugin keeps busy never goes idle. The
//    `compaction` hook adds the focus instruction to the summary request, so
//    the summary keeps the work that is left.
// 4. `armed` again. After the compaction the plugin sends a continue prompt, so
//    the agent resumes from the checkpoint, and it keeps watching.
//
// A compaction leaves the context at the size of the checkpoint and the kept
// tail. The mode therefore measures that size as the floor the session starts
// from, and the next compaction waits until the context has grown past the
// floor by at least a tenth of the threshold. Without that, a threshold below
// the size a compaction leaves would compact the session again and again.
//
// OpenCode's own automatic compaction stays on. It is the safety net for a
// session that grows past the soft threshold, and the soft threshold normally
// sits well below it.
//
// The thresholds and the two instruction texts come from `soft-compact.json` in
// the global config directory, next to this plugin. The file is optional: the
// defaults below apply when it is absent.
//
// The TUI part shows the status of the mode in the prompt footer, next to the
// token count, the way the built-in goal indicator shows a running goal. The
// session metadata is the channel between the two parts: this part owns the
// state and writes the status there, and the TUI part reads it.
//
// The state of the armed sessions lives in the plugin storage, so it survives a
// restart. The plugin reconciles the sessions that were in the middle of a
// cycle when it loaded: a session that was compacting is either running its
// compaction, or its compaction is over, and a session that was wrapping up
// waits for its agent to stop.
//
// The server loads this plugin once per app, so several instances share the
// storage, the events and the sessions. A lock directory in the state
// directory keeps one flow at a time per session across all of them, so a
// session gets one wrap-up prompt and one compaction request.
//
// Verified against OpenCode 2.3.2:
// - `ctx.command.transform` adds the command; the TUI and the app route
//   `/soft-compact <text>` to `session.command` with the text in
//   `input.prompt.text`.
// - `ctx.session.prompt({ sessionID, text, delivery })` admits a message.
//   `delivery: "steer"` delivers it into the running turn.
// - `ctx.session.compact({ sessionID })` admits the same compaction item as
//   `/compact`. The compaction runs at the next step boundary, so the plugin
//   can request it while the session is busy.
// - `ctx.session.hook("compaction", event)` receives the outgoing summary
//   request with a mutable `system` array; OpenCode appends its summary prompt
//   after the hook runs.
// - `ctx.session.instructions.entry.put({ sessionID, key, value })` stores a
//   keyed instruction entry. It outlives a compaction, because a compaction
//   replaces the conversation and not the instructions.
// - `ctx.session.get({ sessionID })` returns the session, whose `time.idle` and
//   `time.busy` say whether the session is idle now.
// - `ctx.session.context({ sessionID })` returns the messages of the active
//   context, each assistant message carrying its token usage and each
//   compaction message carrying its status.
// - `ctx.event.subscribe` reports `session.step.ended`, `session.idle`,
//   `session.compaction.started|ended|failed` and `session.deleted`.
// - `ctx.session.update({ sessionID, metadata })` replaces the metadata of the
//   session, so the plugin reads the metadata first and writes its own key
//   next to the keys of the other plugins.
//
// Native provider compaction also runs the hook, but the provider chooses the
// replacement window, so the instruction is advisory there.

import { appendFile, mkdir, readFile, rm, stat } from "node:fs/promises"
import { homedir } from "node:os"
import { dirname, join } from "node:path"
import { setTimeout as delay } from "node:timers/promises"

const CONFIG_FILENAME = "soft-compact.json"
const LOG_FILENAME = "soft-compact.log"
const STATE_KEY = "sessions"
const METADATA_KEY = "softCompact"
const CHECKPOINT_KEY = "soft-compact-checkpoint"

/** The instruction the agent gets when the session has no own. */
const DEFAULT_INSTRUCTION = [
  "The context of this session reached {tokens} tokens, over the soft compaction threshold of {threshold}.",
  "The session is compacted as soon as you stop, and the summary keeps the work that is left.",
  "",
  "Wrap up first:",
  "- finish the step you are in, and take the few extra steps that complete it cleanly;",
  "- record your current state and your next steps with the soft_compact_checkpoint tool;",
  "- then stop and wait. Do not start new work.",
].join("\n")

/** What the summary of the compaction has to keep. */
const DEFAULT_FOCUS = [
  "Focus the summary on the work that is left:",
  "- keep the objective, the requirements, and the decisions with their reasons;",
  "- keep the work state: what is done, what is in progress, what is blocked;",
  "- keep the next move, with the exact file paths, symbols and commands;",
  "- drop settled discussion and superseded detail.",
].join("\n")

/** The prompt that starts the agent again after the compaction. */
const RESUME_PROMPT = [
  "The conversation was compacted to make room. The checkpoint above records the state and the next steps.",
  "Continue the remaining work from it.",
].join(" ")

const DEFAULTS = {
  threshold: 400_000,
  intervalMs: 30_000,
  instruction: DEFAULT_INSTRUCTION,
  focus: DEFAULT_FOCUS,
}

/** How long a waiter waits between two tries for the lock of a session. */
const LOCK_WAIT_MS = 25
/** How long a waiter waits for the lock of a session before it gives up. */
const LOCK_TIMEOUT_MS = 30_000
/** How old a lock has to be before another instance takes it over. */
const LOCK_STALE_MS = 30_000

const isRecord = (value) => typeof value === "object" && value !== null

/** Unwrap a plugin-context payload that may or may not carry a `data` envelope. */
const unwrap = (value) => (isRecord(value) && "data" in value ? value.data : value)

/** The chain file lives beside the plugin, in the active global config directory. */
const configDirectory = () => process.env.OPENCODE_CONFIG_DIR ?? join(homedir(), ".config", "opencode")

const stateDirectory = () => join(process.env.XDG_STATE_HOME ?? join(homedir(), ".local", "state"), "opencode")

/** Append one line to the phase log. Observability only; never throws. */
const createLog = (path = join(stateDirectory(), LOG_FILENAME)) => async (record) => {
  try {
    await mkdir(dirname(path), { recursive: true })
    await appendFile(path, `${JSON.stringify({ time: new Date().toISOString(), ...record })}\n`, "utf8")
  } catch {
    // A missing state directory must not affect a turn.
  }
}

/** The lock directory of a session, in the state directory. */
const lockDirectory = (sessionID) =>
  join(stateDirectory(), "locks", `soft-compact-${sessionID}.lock`)

/** The age of a lock in milliseconds, or undefined when the lock is gone. */
const lockAge = async (path) => {
  try {
    const info = await stat(path)
    return Date.now() - info.mtimeMs
  } catch {
    return undefined
  }
}

/**
 * Run the work of a session while no other plugin instance works on it.
 *
 * The lock is a directory, because `mkdir` is the only atomic operation the
 * file system offers: it fails when the directory exists. A lock that is older
 * than `LOCK_STALE_MS` belongs to an instance that died, and is taken over.
 */
const withLock = async (sessionID, work) => {
  const path = lockDirectory(sessionID)
  await mkdir(dirname(path), { recursive: true })
  const deadline = Date.now() + LOCK_TIMEOUT_MS
  for (;;) {
    try {
      await mkdir(path)
      break
    } catch (error) {
      if (error?.code !== "EEXIST") throw error
      const age = await lockAge(path)
      if (age !== undefined && age > LOCK_STALE_MS) {
        await rm(path, { recursive: true, force: true })
        continue
      }
      if (Date.now() >= deadline) throw new Error(`the lock of session ${sessionID} is held`)
      await delay(LOCK_WAIT_MS)
    }
  }
  try {
    return await work()
  } finally {
    await rm(path, { recursive: true, force: true }).catch(() => {})
  }
}

const positiveInt = (value) => {
  const number = typeof value === "number" ? value : Number.parseInt(String(value ?? ""), 10)
  if (!Number.isFinite(number) || number <= 0) return undefined
  return Math.round(number)
}

const positiveText = (value, fallback) =>
  typeof value === "string" && value.trim().length > 0 ? value.trim() : fallback

/** Read the plugin configuration, and fall back to the defaults for anything unusable. */
const normalizeConfig = (raw) => ({
  threshold: positiveInt(raw?.threshold) ?? DEFAULTS.threshold,
  intervalMs: positiveInt(raw?.intervalMs) ?? DEFAULTS.intervalMs,
  instruction: positiveText(raw?.instruction, DEFAULTS.instruction),
  focus: positiveText(raw?.focus, DEFAULTS.focus),
})

const loadConfig = async () => {
  try {
    const raw = await readFile(join(configDirectory(), CONFIG_FILENAME), "utf8")
    return normalizeConfig(JSON.parse(raw))
  } catch {
    return normalizeConfig(undefined)
  }
}

/** A threshold in tokens: `400000`, `400k` or `1m`. */
const parseThreshold = (text) => {
  const match = /^(\d+(?:\.\d+)?)\s*([km])?$/i.exec(String(text ?? "").trim())
  if (!match) return undefined
  const value = Number.parseFloat(match[1])
  if (!Number.isFinite(value) || value <= 0) return undefined
  const scale = match[2]?.toLowerCase() === "k" ? 1_000 : match[2]?.toLowerCase() === "m" ? 1_000_000 : 1
  return Math.round(value * scale)
}

/**
 * The command line of `/soft-compact`:
 * - no argument arms the session with the default threshold;
 * - `off` disarms it and `status` reports it;
 * - a threshold arms the session, and the rest of the line is the instruction
 *   that replaces the default wrap-up instruction for this session.
 */
const parseCommand = (text) => {
  const trimmed = String(text ?? "").trim()
  if (!trimmed) return { action: "arm" }
  const [first, ...rest] = trimmed.split(/\s+/)
  const keyword = first.toLowerCase()
  if (keyword === "off" || keyword === "disable") return { action: "off" }
  if (keyword === "status") return { action: "status" }
  const threshold = parseThreshold(first)
  if (threshold === undefined) return { action: "unknown", argument: first }
  const instruction = rest.join(" ").trim()
  return instruction ? { action: "arm", threshold, instruction } : { action: "arm", threshold }
}

/**
 * The size of the context the model would receive now: the last assistant
 * message with usage, after the last completed compaction. This is the number
 * the TUI shows as the context percentage.
 */
const contextTokens = (messages) => {
  const list = Array.isArray(messages) ? messages : []
  const compactionIndex = list.findLastIndex((message) => message?.type === "compaction" && message?.status === "completed")
  for (let index = list.length - 1; index > compactionIndex; index--) {
    const message = list[index]
    if (message?.type !== "assistant" || !message.tokens) continue
    const tokens = message.tokens
    return (
      (tokens.input ?? 0) +
      (tokens.output ?? 0) +
      (tokens.reasoning ?? 0) +
      (tokens.cache?.read ?? 0) +
      (tokens.cache?.write ?? 0)
    )
  }
  return 0
}

/** The wrap-up instruction for the agent, with the numbers of this session in it. */
const wrapUpInstruction = ({ tokens, threshold, instruction }) =>
  String(instruction ?? DEFAULT_INSTRUCTION)
    .replaceAll("{tokens}", String(tokens))
    .replaceAll("{threshold}", String(threshold))

/**
 * The part the summary request gets. It does not replace the summary format,
 * and it is not a task: it says what the summary has to keep.
 */
const focusGuidance = (focus) =>
  [
    "This compaction is part of a soft compaction, so the agent can continue the work after it.",
    "",
    String(focus ?? DEFAULT_FOCUS),
    "",
    "It does not replace the summary format: still fill every required section, and do not treat it as a task to perform.",
  ].join("\n")

/** Human-readable reason for a thrown value. */
const describeError = (error) => (error instanceof Error ? error.message : String(error))

export default {
  id: "soft-compact",

  async setup(ctx) {
    const config = await loadConfig()
    const log = createLog()

    const readState = async () => (await ctx.storage.get(STATE_KEY)) ?? {}
    const writeState = (state) => ctx.storage.set(STATE_KEY, state)

    /**
     * Runs the work of a session after the work that is already running for it.
     *
     * The lock is a directory in the state directory, so it also covers the
     * other instances of the plugin that the server loaded for the same
     * storage.
     */
    const withSession = async (sessionID, work) => {
      try {
        return await withLock(sessionID, work)
      } catch (error) {
        await log({
          sessionID,
          level: "error",
          message: `the work of the session did not run: ${describeError(error)}`,
        })
        return undefined
      }
    }

    /** Reads the state of a session, applies a patch, and writes it back. */
    const patchState = async (sessionID, patch) => {
      const state = await readState()
      const current = state[sessionID]
      if (!current) return undefined
      const next = { ...current, ...patch }
      state[sessionID] = next
      await writeState(state)
      return next
    }

    /**
     * Report the state of the mode to the log and to the session, where the TUI
     * part picks it up: the toast shows the message, the footer shows the status.
     */
    const announce = async (sessionID, notice) => {
      await log({ sessionID, status: notice.status, message: notice.message })
      try {
        const session = await ctx.session.get({ sessionID })
        const state = await readState()
        const entry = state[sessionID]
        const metadata = {
          ...(session?.metadata ?? {}),
          [METADATA_KEY]: {
            status: notice.status,
            threshold: entry?.threshold,
            message: notice.message,
            at: Date.now(),
            ...(notice.variant ? { variant: notice.variant } : {}),
          },
        }
        await ctx.session.update({ sessionID, metadata })
      } catch (error) {
        await log({ sessionID, level: "error", message: `the notice did not reach the session: ${describeError(error)}` })
      }
    }

    /** The size of the context of a session, or undefined when it cannot be read. */
    const measure = async (sessionID) => {
      try {
        const messages = unwrap(await ctx.session.context({ sessionID }))
        return contextTokens(messages)
      } catch (error) {
        await log({ sessionID, level: "error", message: `the context could not be read: ${describeError(error)}` })
        return undefined
      }
    }

    /** The last compaction of a session, or undefined when there is none. */
    const lastCompaction = async (sessionID) => {
      try {
        const messages = unwrap(await ctx.session.context({ sessionID }))
        if (!Array.isArray(messages)) return undefined
        return messages.findLast((message) => message?.type === "compaction")
      } catch {
        return undefined
      }
    }

    /** Whether the session is idle now, from the timestamps of the session. */
    const isIdle = async (sessionID) => {
      try {
        const session = await ctx.session.get({ sessionID })
        const { idle, busy } = session?.time ?? {}
        if (typeof idle !== "number" || typeof busy !== "number") return false
        return idle >= busy
      } catch {
        return false
      }
    }

    /** Remove the checkpoint of a session, and report why it did not go. */
    const removeCheckpoint = async (sessionID) => {
      try {
        await ctx.session.instructions.entry.remove({ sessionID, key: CHECKPOINT_KEY })
      } catch (error) {
        await log({ sessionID, level: "error", message: `the checkpoint was not removed: ${describeError(error)}` })
      }
    }

    const armSession = async (sessionID, { threshold, instruction }) => {
      const state = await readState()
      const entry = {
        threshold: threshold ?? config.threshold,
        phase: "armed",
        armedAt: Date.now(),
        floor: 0,
      }
      if (instruction) entry.instruction = instruction
      else if (config.instruction) entry.instruction = config.instruction
      state[sessionID] = entry
      await writeState(state)
      // A checkpoint of an earlier round must not be read as the checkpoint of
      // this one.
      await removeCheckpoint(sessionID)
      await announce(sessionID, {
        status: "armed",
        message: `Soft compaction armed at ${entry.threshold} tokens.`,
      })
    }

    const disarmSession = async (sessionID) => {
      const state = await readState()
      if (state[sessionID]) delete state[sessionID]
      await writeState(state)
      await removeCheckpoint(sessionID)
      await announce(sessionID, { status: "off", message: "Soft compaction disarmed." })
    }

    const reportSession = async (sessionID) => {
      const state = await readState()
      const entry = state[sessionID]
      const tokens = await measure(sessionID)
      const usage = tokens === undefined ? "an unknown size" : `${tokens} tokens`
      const message = entry
        ? `Soft compaction is ${entry.phase} at ${entry.threshold} tokens; the context is at ${usage}.`
        : `Soft compaction is off; the context is at ${usage}.`
      await announce(sessionID, { status: entry?.phase ?? "off", message })
    }

    /** Ask the agent to wrap up, and wait for it to stop. */
    const startWrapUp = async (sessionID, entry, tokens) => {
      await patchState(sessionID, {
        phase: "wrapping-up",
        contextTokens: tokens,
        agentWorked: false,
        checkpointAt: undefined,
      })
      await announce(sessionID, {
        status: "wrapping-up",
        message: `Soft compaction: the context is at ${tokens} tokens. Wrapping up.`,
      })
      try {
        await ctx.session.prompt({
          sessionID,
          text: wrapUpInstruction({
            tokens,
            threshold: entry.threshold,
            instruction: entry.instruction ?? config.instruction,
          }),
          delivery: "steer",
        })
      } catch (error) {
        await patchState(sessionID, { phase: "armed" })
        await log({ sessionID, level: "error", message: `the wrap-up prompt was not admitted: ${describeError(error)}` })
      }
    }

    /**
     * Request the compaction, with the focus instruction waiting for it.
     *
     * The focus instruction lives in the shared state, so every instance of the
     * plugin can find it and only one of them gives it to the summary request.
     */
    const startCompaction = async (sessionID) => {
      const state = await readState()
      const entry = state[sessionID]
      if (!entry || entry.phase !== "wrapping-up") return
      await patchState(sessionID, { phase: "compacting", focusPending: true })
      try {
        await ctx.session.compact({ sessionID })
      } catch (error) {
        await patchState(sessionID, { phase: "armed", focusPending: false })
        await log({ sessionID, level: "error", message: `the compaction was not admitted: ${describeError(error)}` })
        return
      }
      await announce(sessionID, {
        status: "compacting",
        message: "Soft compaction: compacting the session.",
      })
    }

    /**
     * The agent stopped. Compact now, unless the session was disarmed meanwhile.
     *
     * The session has to have done a step of its own since the wrap-up prompt,
     * or the idle event is the one that came before it.
     */
    const onIdleSession = async (sessionID) => {
      const state = await readState()
      const entry = state[sessionID]
      if (!entry || entry.phase !== "wrapping-up" || !entry.agentWorked) return
      await startCompaction(sessionID)
    }

    /** The compaction is over. Let the agent continue from the checkpoint. */
    const onCompactionEndedSession = async (sessionID) => {
      const state = await readState()
      const entry = state[sessionID]
      if (!entry) return
      if (entry.phase !== "wrapping-up" && entry.phase !== "compacting") {
        // A compaction the plugin did not ask for. The session keeps running, so
        // the plugin only watches again, from the size the compaction left.
        await patchState(sessionID, { phase: "armed", floorPending: true })
        return
      }
      await patchState(sessionID, {
        phase: "armed",
        contextTokens: undefined,
        focusPending: false,
        floorPending: true,
      })
      await announce(sessionID, {
        status: "armed",
        message: "Soft compaction: the session is compacted. Continuing.",
      })
      try {
        await ctx.session.prompt({ sessionID, text: RESUME_PROMPT, delivery: "steer" })
      } catch (error) {
        await log({ sessionID, level: "error", message: `the continue prompt was not admitted: ${describeError(error)}` })
      }
    }

    const onCompactionFailedSession = async (sessionID) => {
      const state = await readState()
      const entry = state[sessionID]
      if (!entry) return
      await patchState(sessionID, { phase: "armed", contextTokens: undefined, focusPending: false })
      await announce(sessionID, {
        status: "armed",
        variant: "error",
        message: "Soft compaction: the compaction failed. Watching again.",
      })
    }

    /** The context grew. Wrap up when it is over the threshold. */
    const triggerSession = async (sessionID) => {
      const state = await readState()
      const entry = state[sessionID]
      if (!entry || entry.phase !== "armed") return
      const tokens = await measure(sessionID)
      if (tokens === undefined) return
      if (entry.floorPending) {
        // The session was compacted. This size is the floor it now starts from,
        // so the next compaction waits for new work instead of repeating.
        await patchState(sessionID, { floor: tokens, floorPending: false })
        return
      }
      const floor = entry.floor ?? 0
      const margin = Math.max(10_000, Math.round(entry.threshold * 0.1))
      if (tokens < entry.threshold) return
      if (tokens - floor < margin) return
      await startWrapUp(sessionID, entry, tokens)
    }

    /** One flow at a time per session. */
    const arm = (sessionID, options) => withSession(sessionID, () => armSession(sessionID, options))
    const disarm = (sessionID) => withSession(sessionID, () => disarmSession(sessionID))
    const report = (sessionID) => withSession(sessionID, () => reportSession(sessionID))
    const trigger = (sessionID) => withSession(sessionID, () => triggerSession(sessionID))
    const onIdle = (sessionID) => withSession(sessionID, () => onIdleSession(sessionID))
    const compact = (sessionID) => withSession(sessionID, () => startCompaction(sessionID))
    const onCompactionEnded = (sessionID) => withSession(sessionID, () => onCompactionEndedSession(sessionID))
    const onCompactionFailed = (sessionID) => withSession(sessionID, () => onCompactionFailedSession(sessionID))

    await ctx.command.transform((editor) => {
      editor.add({
        name: "soft-compact",
        description: "Arm a soft compaction for this session: `/soft-compact [threshold|off|status] [instruction]`",
        async execute(input) {
          const request = parseCommand(input.prompt.text)
          const sessionID = input.sessionID
          if (request.action === "off") {
            await disarm(sessionID)
            return
          }
          if (request.action === "status") {
            await report(sessionID)
            return
          }
          if (request.action === "unknown") {
            const state = await readState()
            await announce(sessionID, {
              status: state[sessionID]?.phase ?? "off",
              variant: "error",
              message: `Soft compaction: "${request.argument}" is not a threshold, "off" or "status".`,
            })
            return
          }
          await arm(sessionID, { threshold: request.threshold, instruction: request.instruction })
        },
      })
    })

    /**
     * Store the checkpoint of a session, and ask for the compaction.
     *
     * The checkpoint is the agent's own signal that it stopped, so the
     * compaction does not wait for the session to go idle. A session that
     * another plugin keeps busy never goes idle, and the compaction would
     * never come.
     */
    const recordCheckpoint = async (sessionID, value) => {
      const state = await readState()
      if (!state[sessionID]) {
        return "The soft compaction mode is not armed for this session, so there is nothing to record."
      }
      try {
        await ctx.session.instructions.entry.put({
          sessionID,
          key: CHECKPOINT_KEY,
          value,
        })
      } catch (error) {
        await log({
          sessionID,
          level: "error",
          message: `the checkpoint was not stored: ${describeError(error)}`,
        })
        return `The checkpoint was not stored: ${describeError(error)}`
      }
      // The session may have been disarmed while the write was running.
      const after = await readState()
      if (!after[sessionID]) {
        await removeCheckpoint(sessionID)
        return "The soft compaction mode was disarmed, so the checkpoint was dropped."
      }
      await patchState(sessionID, { checkpointAt: Date.now() })
      await startCompaction(sessionID)
      return "The checkpoint is recorded. The session is compacted now."
    }

    /**
     * Take the focus instruction of a compaction.
     *
     * The instruction lives in the shared state, so every instance of the
     * plugin finds it, and only the first one to come gives it to the summary
     * request.
     */
    const claimFocus = async (sessionID) => {
      const state = await readState()
      const entry = state[sessionID]
      if (!entry?.focusPending) return undefined
      await patchState(sessionID, { focusPending: false })
      return focusGuidance(config.focus)
    }

    await ctx.tool.transform((editor) => {
      editor.add({
        name: "soft_compact_checkpoint",
        description:
          "Record the current state and the next steps of this session, so they survive a compaction. Use it once, right before you stop to let the session be compacted. Write two short sections: `## State` with what is done, what is in progress and what is blocked, and `## Next Steps` with the next actions in order, with the exact file paths, symbols and commands.",
        input: {
          type: "object",
          properties: {
            checkpoint: {
              type: "string",
              description: "The state and the next steps, as two short Markdown sections.",
            },
          },
          required: ["checkpoint"],
          additionalProperties: false,
        },
        // One required string field, so the model can write it directly in Code
        // Mode instead of wrapping it in an object.
        freeform: { type: "text" },
        async execute(input, context) {
          const sessionID = context.sessionID
          // Code Mode hands the text over as it stands; a normal call wraps it.
          const text = typeof input === "string" ? input : String(input.checkpoint ?? "")
          const value = text.trim()
          if (!value) {
            return { content: "The checkpoint was empty. Write the state and the next steps before stopping." }
          }
          const content = await withSession(sessionID, () => recordCheckpoint(sessionID, value))
          return { content: content ?? "The checkpoint was not recorded." }
        },
      })
    })

    await ctx.session.hook("compaction", async (event) => {
      const sessionID = event.sessionID
      if (!sessionID) return
      const guidance = await withSession(sessionID, () => claimFocus(sessionID))
      if (!guidance) return
      event.system.push({ type: "text", text: guidance })
    })

    const controller = new AbortController()
    void (async () => {
      for await (const event of ctx.event.subscribe({
        types: [
          "session.step.ended",
          "session.idle",
          "session.compaction.ended",
          "session.compaction.failed",
          "session.deleted",
        ],
        signal: controller.signal,
      })) {
        const sessionID = event.data?.sessionID
        if (!sessionID) continue
        try {
          if (event.type === "session.step.ended") {
            await withSession(sessionID, async () => {
              const entry = (await readState())[sessionID]
              const wasWrapping = entry?.phase === "wrapping-up"
              await triggerSession(sessionID)
              if (wasWrapping) {
                // The agent did a step of its own after the wrap-up prompt, so the
                // next idle event is the one that follows it.
                await patchState(sessionID, { agentWorked: true })
              }
            })
          } else if (event.type === "session.idle") await onIdle(sessionID)
          else if (event.type === "session.compaction.ended") await onCompactionEnded(sessionID)
          else if (event.type === "session.compaction.failed") await onCompactionFailed(sessionID)
          else if (event.type === "session.deleted") {
            await withSession(sessionID, async () => {
              const state = await readState()
              if (state[sessionID]) {
                delete state[sessionID]
                await writeState(state)
              }
            })
          }
        } catch (error) {
          await log({ sessionID, level: "error", message: `${event.type} failed: ${describeError(error)}` })
        }
      }
    })().catch(() => {
      // The stream ends when the plugin unloads; nothing to report.
    })

    /**
     * A session that was in the middle of a cycle when the plugin loaded needs
     * its cycle back: a compaction that ran while the plugin was gone is over,
     * and a session that was wrapping up waits for its agent to stop.
     */
    const reconcile = async () => {
      const state = await readState()
      for (const [sessionID, entry] of Object.entries(state)) {
        if (entry.phase === "compacting") {
          const compaction = await lastCompaction(sessionID)
          if (compaction?.status === "running") continue
          if (compaction?.status === "completed") await onCompactionEnded(sessionID)
          else await onCompactionFailed(sessionID)
          continue
        }
        if (entry.phase !== "wrapping-up") continue
        if (entry.checkpointAt) {
          // The agent recorded its state, but the plugin went away before the
          // compaction started.
          await compact(sessionID)
          continue
        }
        if (entry.agentWorked && (await isIdle(sessionID))) {
          await onIdle(sessionID)
        }
      }
    }

    const timer = setInterval(() => {
      void (async () => {
        const state = await readState()
        for (const [sessionID, entry] of Object.entries(state)) {
          if (entry.phase === "armed") {
            await trigger(sessionID)
            continue
          }
          if (entry.phase !== "wrapping-up") continue
          if (entry.checkpointAt) {
            // The agent recorded its state, but the compaction did not start.
            await compact(sessionID)
            continue
          }
          if (entry.agentWorked && (await isIdle(sessionID))) {
            await onIdle(sessionID)
          }
        }
      })().catch(async (error) => {
        await log({ level: "error", message: `the timer failed: ${describeError(error)}` })
      })
    }, config.intervalMs)

    void reconcile().catch(async (error) => {
      await log({ level: "error", message: `the sessions were not reconciled: ${describeError(error)}` })
    })

    return () => {
      controller.abort()
      clearInterval(timer)
    }
  },
}

export const internals = {
  configDirectory,
  contextTokens,
  describeError,
  focusGuidance,
  loadConfig,
  lockDirectory,
  normalizeConfig,
  parseCommand,
  parseThreshold,
  withLock,
  wrapUpInstruction,
  DEFAULT_FOCUS,
  DEFAULT_INSTRUCTION,
  DEFAULTS,
  RESUME_PROMPT,
}
