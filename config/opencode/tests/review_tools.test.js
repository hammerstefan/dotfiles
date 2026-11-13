// Concurrency and budget tests for plugins/review-tools.js.
//
// Run with: bun test config/opencode/tests/review_tools.test.js
//
// Every test uses its own temporary working directory, which gives it fresh
// budget windows and a fresh admission queue, because the plugin keys caller
// budgets by "<cwd>:<caller>", worktree budgets and gates by "<cwd>".

import { afterAll, describe, expect, test } from "bun:test"
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import reviewTools, { internals } from "../plugins/review-tools.js"

const MAX_OUTPUT_BYTES = 8 * 1024 * 1024
const MAX_ERROR_BYTES = 64 * 1024
const RESERVATION_BYTES = MAX_OUTPUT_BYTES + MAX_ERROR_BYTES
const MAX_BYTES_PER_CALLER = 24 * 1024 * 1024
const MAX_BYTES_PER_WORKTREE = 384 * 1024 * 1024
const MAX_COMMANDS_PER_CALLER = 20
const MAX_REMOTE_CALLS_PER_CALLER = 5
const MAX_QUEUED_PER_WORKTREE = 32

const RESERVATIONS_PER_CALLER = Math.floor(MAX_BYTES_PER_CALLER / RESERVATION_BYTES)
const RESERVATIONS_PER_WORKTREE = Math.floor(MAX_BYTES_PER_WORKTREE / RESERVATION_BYTES)

const pause = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds))

const scratchRoot = join(tmpdir(), "opencode", "review-tools-tests")
mkdirSync(scratchRoot, { recursive: true })
const scratchDirs = []

const scratchDir = (label) => {
  const dir = mkdtempSync(join(scratchRoot, `${label}-`))
  scratchDirs.push(dir)
  return dir
}

afterAll(() => {
  for (const dir of scratchDirs) rmSync(dir, { recursive: true, force: true })
})

const callerWindow = (cwd, caller) => {
  const state = internals.debugState()
  const entry = state.callers.find(([key]) => key === `${cwd}:${caller}`)
  if (!entry) throw new Error(`no caller window for ${cwd}:${caller}`)
  return entry[1]
}

const worktreeWindow = (cwd) => {
  const state = internals.debugState()
  const entry = state.worktrees.find(([key]) => key === cwd)
  if (!entry) throw new Error(`no worktree window for ${cwd}`)
  return entry[1]
}

const queuedCount = (cwd) => {
  const state = internals.debugState()
  const entry = state.queuedPerWorktree.find(([key]) => key === cwd)
  return entry ? entry[1] : 0
}

describe("admission queue", () => {
  test("several small concurrent calls from one caller all succeed", async () => {
    const cwd = scratchDir("concurrent")
    const results = await Promise.allSettled(
      Array.from({ length: 5 }, () => internals.run(["echo", "ok"], cwd, undefined, "caller")),
    )
    for (const result of results) {
      expect(result.status).toBe("fulfilled")
      expect(result.value).toBe("ok\n")
    }
    const window = callerWindow(cwd, "caller")
    expect(window.inFlight).toBe(0)
    expect(window.commands).toBe(5)
  }, 20000)

  test("a third call waits for the caller byte budget instead of failing", async () => {
    const cwd = scratchDir("queue-behind")
    const start = Date.now()
    const first = internals.run(["sleep", "0.5"], cwd, undefined, "caller")
    const second = internals.run(["sleep", "0.5"], cwd, undefined, "caller")
    const queuedStart = Date.now()
    let queuedElapsed = 0
    const queued = internals.run(["echo", "ok"], cwd, undefined, "caller", {
      queueWaitMilliseconds: 10000,
    }).then((value) => {
      queuedElapsed = Date.now() - queuedStart
      return value
    })
    await Promise.all([first, second, queued])
    expect(queuedElapsed).toBeGreaterThanOrEqual(300)
    expect(Date.now() - start).toBeLessThan(10000)
  }, 20000)

  test("caller budgets are independent inside one worktree", async () => {
    const cwd = scratchDir("independent-callers")
    const start = Date.now()
    const calls = []
    for (const caller of ["alpha", "beta"]) {
      for (let i = 0; i < RESERVATIONS_PER_CALLER; i += 1) {
        calls.push(internals.run(["sleep", "0.4"], cwd, undefined, caller))
      }
    }
    const results = await Promise.allSettled(calls)
    for (const result of results) expect(result.status).toBe("fulfilled")
    const elapsed = Date.now() - start
    expect(elapsed).toBeGreaterThanOrEqual(350)
    expect(elapsed).toBeLessThan(2000)
  }, 20000)

  test("the shared worktree byte budget queues calls across callers", async () => {
    const cwd = scratchDir("worktree-contention")
    const calls = []
    for (let i = 0; i <= RESERVATIONS_PER_WORKTREE; i += 1) {
      calls.push(internals.run(["sleep", "0.3"], cwd, undefined, `worker-${i}`))
    }
    const results = await Promise.allSettled(calls)
    for (const result of results) expect(result.status).toBe("fulfilled")
    const window = worktreeWindow(cwd)
    expect(window.inFlight).toBe(0)
    expect(queuedCount(cwd)).toBe(0)
  }, 30000)
})

describe("genuinely exhausted quotas fail fast", () => {
  test("the caller command budget rejects without queuing", async () => {
    const cwd = scratchDir("command-budget")
    for (let i = 0; i < MAX_COMMANDS_PER_CALLER; i += 1) {
      await internals.run(["echo", "x"], cwd, undefined, "caller")
    }
    await expect(internals.run(["echo", "x"], cwd, undefined, "caller")).rejects.toThrow(
      "review inspection exceeded its caller command budget",
    )
  }, 20000)

  test("the caller remote-call budget rejects without queuing", async () => {
    const cwd = scratchDir("remote-budget")
    for (let i = 0; i < MAX_REMOTE_CALLS_PER_CALLER; i += 1) {
      await internals
        .run(["gh", "review-tools-unlikely-subcommand"], cwd, undefined, "caller")
        .catch(() => undefined)
    }
    const window = callerWindow(cwd, "caller")
    expect(window.remoteCalls).toBe(MAX_REMOTE_CALLS_PER_CALLER)
    await expect(
      internals.run(["gh", "review-tools-unlikely-subcommand"], cwd, undefined, "caller"),
    ).rejects.toThrow("review inspection exceeded its caller remote-call budget")
  }, 20000)

  test("consumed bytes alone forbid another reservation", async () => {
    const cwd = scratchDir("byte-budget")
    const large = join(cwd, "large.txt")
    writeFileSync(large, "x".repeat(6 * 1024 * 1024))
    for (let i = 0; i < 3; i += 1) {
      await internals.run(["cat", large], cwd, undefined, "caller")
    }
    const window = callerWindow(cwd, "caller")
    expect(window.bytes).toBeGreaterThan(MAX_BYTES_PER_CALLER - RESERVATION_BYTES)
    const start = Date.now()
    await expect(internals.run(["cat", large], cwd, undefined, "caller")).rejects.toThrow(
      "review inspection exceeded its caller byte budget",
    )
    expect(Date.now() - start).toBeLessThan(1000)
  }, 30000)
})

describe("every exit path settles the reservation", () => {
  test("over-limit output charges the clamp and frees the in-flight slot", async () => {
    const cwd = scratchDir("over-limit")
    const huge = join(cwd, "huge.txt")
    writeFileSync(huge, "x".repeat(9 * 1024 * 1024))
    await expect(internals.run(["cat", huge], cwd, undefined, "caller")).rejects.toThrow(
      "read-only review inspection exceeded its output safety limit",
    )
    const window = callerWindow(cwd, "caller")
    expect(window.inFlight).toBe(0)
    expect(window.bytes).toBeGreaterThanOrEqual(MAX_OUTPUT_BYTES)
    expect(window.bytes).toBeLessThanOrEqual(RESERVATION_BYTES)
    await expect(internals.run(["echo", "ok"], cwd, undefined, "caller")).resolves.toBe("ok\n")
  }, 30000)

  test("a command failing with stderr charges only consumed bytes", async () => {
    const cwd = scratchDir("stderr-failure")
    await expect(
      internals.run(["sh", "-c", "echo boom >&2; exit 3"], cwd, undefined, "caller"),
    ).rejects.toThrow("boom")
    const window = callerWindow(cwd, "caller")
    expect(window.inFlight).toBe(0)
    expect(window.bytes).toBeGreaterThan(0)
    expect(window.bytes).toBeLessThan(RESERVATION_BYTES)
    await expect(internals.run(["echo", "ok"], cwd, undefined, "caller")).resolves.toBe("ok\n")
  }, 20000)

  test("a spawn failure refunds the whole reservation", async () => {
    const cwd = scratchDir("spawn-failure")
    await expect(
      internals.run(["review-tools-definitely-missing-binary"], cwd, undefined, "caller"),
    ).rejects.toThrow()
    const window = callerWindow(cwd, "caller")
    expect(window.inFlight).toBe(0)
    expect(window.bytes).toBe(0)
  }, 20000)

  test("a command timeout settles the reservation", async () => {
    const cwd = scratchDir("command-timeout")
    await expect(
      internals.run(["sleep", "2"], cwd, undefined, "caller", { commandTimeoutMilliseconds: 200 }),
    ).rejects.toThrow("read-only review inspection failed")
    const window = callerWindow(cwd, "caller")
    expect(window.inFlight).toBe(0)
    await expect(internals.run(["echo", "ok"], cwd, undefined, "caller")).resolves.toBe("ok\n")
  }, 20000)
})

describe("queue cancellation and bounds", () => {
  test("aborting while queued rejects the waiting call", async () => {
    const cwd = scratchDir("abort-queued")
    const controller = new AbortController()
    const inFlight = [
      internals.run(["sleep", "0.8"], cwd, undefined, "caller"),
      internals.run(["sleep", "0.8"], cwd, undefined, "caller"),
    ]
    const queued = internals.run(["echo", "ok"], cwd, controller.signal, "caller", {
      queueWaitMilliseconds: 10000,
    })
    await pause(150)
    controller.abort()
    await expect(queued).rejects.toThrow(
      "review inspection was aborted while waiting for inspection capacity",
    )
    expect(queuedCount(cwd)).toBe(0)
    await Promise.all(inFlight)
    expect(callerWindow(cwd, "caller").inFlight).toBe(0)
    await expect(internals.run(["echo", "ok"], cwd, undefined, "caller")).resolves.toBe("ok\n")
  }, 20000)

  test("an already aborted signal rejects before reserving", async () => {
    const cwd = scratchDir("abort-before")
    const controller = new AbortController()
    controller.abort()
    await expect(
      internals.run(["echo", "ok"], cwd, controller.signal, "caller"),
    ).rejects.toThrow("review inspection was aborted before it started")
    const state = internals.debugState()
    expect(state.callers.find(([key]) => key === `${cwd}:caller`)).toBeUndefined()
    expect(queuedCount(cwd)).toBe(0)
  }, 20000)

  test("waiting past the queue wait limit rejects with the wait message", async () => {
    const cwd = scratchDir("wait-timeout")
    const inFlight = [
      internals.run(["sleep", "0.8"], cwd, undefined, "caller"),
      internals.run(["sleep", "0.8"], cwd, undefined, "caller"),
    ]
    const queued = internals.run(["echo", "ok"], cwd, undefined, "caller", {
      queueWaitMilliseconds: 150,
    })
    await expect(queued).rejects.toThrow(
      "review inspection timed out waiting for inspection capacity",
    )
    await Promise.all(inFlight)
    await expect(internals.run(["echo", "ok"], cwd, undefined, "caller")).resolves.toBe("ok\n")
    expect(queuedCount(cwd)).toBe(0)
  }, 20000)

  test("a saturated queue rejects the next call immediately", async () => {
    const cwd = scratchDir("saturation")
    const inFlight = [
      internals.run(["sleep", "1"], cwd, undefined, "caller"),
      internals.run(["sleep", "1"], cwd, undefined, "caller"),
    ]
    const queued = []
    for (let i = 0; i < MAX_QUEUED_PER_WORKTREE; i += 1) {
      queued.push(
        internals
          .run(["echo", "ok"], cwd, undefined, "caller", { queueWaitMilliseconds: 30000 })
          .then(
            () => "fulfilled",
            (error) => error.message,
          ),
      )
    }
    const saturated = internals.run(["echo", "ok"], cwd, undefined, "caller", {
      queueWaitMilliseconds: 30000,
    })
    await expect(saturated).rejects.toThrow("review inspection queue is saturated")
    await Promise.all(inFlight)
    const outcomes = await Promise.all(queued)
    const fulfilled = outcomes.filter((outcome) => outcome === "fulfilled").length
    const commandBudget = outcomes.filter(
      (outcome) => outcome === "review inspection exceeded its caller command budget",
    ).length
    expect(fulfilled + commandBudget).toBe(MAX_QUEUED_PER_WORKTREE)
    expect(fulfilled).toBeGreaterThan(0)
    expect(queuedCount(cwd)).toBe(0)
  }, 30000)
})

describe("budget window rollover", () => {
  test("in-flight reservations carry into the successor window", async () => {
    const cwd = scratchDir("rollover")
    const straddling = internals.run(["sleep", "0.6"], cwd, undefined, "caller", {
      windowMilliseconds: 250,
    })
    await pause(320)
    await internals.run(["echo", "ok"], cwd, undefined, "caller", { windowMilliseconds: 250 })
    let window = callerWindow(cwd, "caller")
    expect(window.commands).toBe(2)
    expect(window.inFlight).toBe(1)
    expect(window.bytes).toBeGreaterThan(RESERVATION_BYTES)
    await straddling
    window = callerWindow(cwd, "caller")
    expect(window.inFlight).toBe(0)
    expect(window.commands).toBe(2)
    expect(window.bytes).toBeLessThan(100000)
  }, 20000)

  test("a fully settled expired window resets its attempt counts", async () => {
    const cwd = scratchDir("window-reset")
    await internals.run(["echo", "a"], cwd, undefined, "caller", { windowMilliseconds: 250 })
    await internals.run(["echo", "b"], cwd, undefined, "caller", { windowMilliseconds: 250 })
    await pause(320)
    await internals.run(["echo", "c"], cwd, undefined, "caller", { windowMilliseconds: 250 })
    const window = callerWindow(cwd, "caller")
    expect(window.commands).toBe(1)
    expect(window.inFlight).toBe(0)
    expect(window.bytes).toBeLessThan(100000)
  }, 20000)
})

describe("inspection command construction", () => {
  test("pr_diff without a path keeps the whole-diff command", () => {
    for (const request of [
      { operation: "pr_diff", number: 4 },
      { operation: "pr_diff", number: 4, path: null },
    ]) {
      const { command } = internals.buildInspectCommand(request)
      expect(command).toEqual(["gh", "pr", "diff", "4", "--color=never"])
    }
  })

  test("pr_diff with a path selects one file through the files API", () => {
    const path = 'src/we"ird.txt'
    const { command } = internals.buildInspectCommand({
      operation: "pr_diff",
      number: 4,
      path,
    })
    expect(command.slice(0, 6)).toEqual([
      "gh",
      "api",
      "--paginate",
      "-X",
      "GET",
      "repos/{owner}/{repo}/pulls/4/files",
    ])
    expect(command).toContain("-F")
    expect(command).toContain("per_page=100")
    const projection = command[command.length - 1]
    expect(projection).toBe(
      `.[] | select(.filename == ${JSON.stringify(path)}) | (.patch // "")`,
    )
    expect(projection).toContain('"src/we\\"ird.txt"')
  })

  test("pr_files builds the changed-file inventory command", () => {
    const { command } = internals.buildInspectCommand({ operation: "pr_files", number: 7 })
    expect(command.slice(0, 6)).toEqual([
      "gh",
      "api",
      "--paginate",
      "-X",
      "GET",
      "repos/{owner}/{repo}/pulls/7/files",
    ])
    const projection = command[command.length - 1]
    expect(projection.startsWith(".[] | {filename,")).toBe(true)
    expect(projection).toContain("previous_filename")
  })
})

describe("human report writer", () => {
  const registerTools = async (repo) => {
    const registered = {}
    const ctx = {
      tool: {
        transform: async (mutate) => {
          await mutate({ add: (tool) => void (registered[tool.name] = tool) })
        },
      },
      session: {
        get: async () => ({ data: { location: { directory: repo } } }),
      },
    }
    await reviewTools.setup(ctx)
    return registered
  }

  const scratchRepo = (label) => {
    const repo = scratchDir(label)
    const git = (args) => {
      const result = Bun.spawnSync(["git", "-C", repo, ...args])
      if (result.exitCode !== 0) throw new Error(`git ${args.join(" ")} failed`)
      return result.stdout.toString()
    }
    git(["init", "-q"])
    git(["config", "user.email", "review-tools@example.com"])
    git(["config", "user.name", "review tools test"])
    writeFileSync(join(repo, "README.md"), "scratch\n")
    git(["add", "README.md"])
    git(["commit", "-q", "-m", "scratch commit"])
    return { repo, git }
  }

  const reportPayload = (head) => ({
    invocation: "independent",
    scope: {
      kind: "uncommitted",
      value: "uncommitted",
      reviewed_revision: null,
      base_revision: head,
    },
    focus: [],
    exclusions: [],
    direction: "",
    status: "REQUIRED",
    items: [
      {
        id: "HUM-001",
        priority: "REQUIRED",
        attention_types: ["judgment-gap"],
        category: "coverage",
        title: "Confirm the recovery procedure",
        locations: [{ path: "README.md", line: 1, source: "reviewed" }],
        confidence: "high",
        impact_level: "low",
        impact: "The recovery step is unverified.",
        evidence: "README.md line 1 documents the scratch setup.",
        uncertainty_sources: ["environment-validation"],
        why_human: "The recovery step needs a human decision.",
        needed_capability: "Confirm the procedure on a real host.",
        human_action: "Run the recovery once and record the outcome.",
      },
    ],
    council_summary: null,
  })

  test("a valid report persists and its result parses", async () => {
    const { repo, git } = scratchRepo("writer-success")
    const head = git(["rev-parse", "HEAD"]).trim()
    const registered = await registerTools(repo)
    const result = await registered.write_review_human_report.execute(
      { payload: reportPayload(head) },
      {
        sessionID: "writer-success",
        messageID: "message-1",
        signal: new AbortController().signal,
      },
    )
    expect(result.title).toBe("Human-review report persisted")
    expect(result.content).toBe(`Artifact: ${result.metadata.path}`)
    expect(result.metadata.status).toBe("REQUIRED")
    expect(result.metadata.items).toBe(1)
    const persisted = join(repo, result.metadata.path)
    expect(existsSync(persisted)).toBe(true)
    const stored = JSON.parse(readFileSync(persisted, "utf8"))
    expect(stored.items[0].id).toBe("HUM-001")
  }, 30000)

  test("a second attempt from the same command is refused", async () => {
    const { repo, git } = scratchRepo("writer-retry")
    const head = git(["rev-parse", "HEAD"]).trim()
    const registered = await registerTools(repo)
    const context = {
      sessionID: "writer-retry",
      messageID: "message-1",
      signal: new AbortController().signal,
    }
    await registered.write_review_human_report.execute(
      { payload: reportPayload(head) },
      context,
    )
    await expect(
      registered.write_review_human_report.execute({ payload: reportPayload(head) }, context),
    ).rejects.toThrow("limited to one attempt per command")
  }, 30000)

  test("an invalid payload surfaces the writer's error detail", async () => {
    const { repo } = scratchRepo("writer-invalid")
    const registered = await registerTools(repo)
    await expect(
      registered.write_review_human_report.execute(
        { payload: { unexpected: true } },
        {
          sessionID: "writer-invalid",
          messageID: "message-1",
          signal: new AbortController().signal,
        },
      ),
    ).rejects.toThrow(/candidate/)
  }, 30000)
})

describe("registered tool", () => {
  test("three concurrent operations through execute all succeed", async () => {
    const repo = scratchDir("integration")
    const git = (args) => {
      const result = Bun.spawnSync(["git", "-C", repo, ...args])
      if (result.exitCode !== 0) throw new Error(`git ${args.join(" ")} failed`)
    }
    git(["init", "-q"])
    git(["config", "user.email", "review-tools@example.com"])
    git(["config", "user.name", "review tools test"])
    writeFileSync(join(repo, "README.md"), "scratch\n")
    git(["add", "README.md"])
    git(["commit", "-q", "-m", "scratch commit"])

    const registered = {}
    const ctx = {
      tool: {
        transform: async (mutate) => {
          await mutate({ add: (tool) => void (registered[tool.name] = tool) })
        },
      },
      session: {
        get: async () => ({ data: { location: { directory: repo } } }),
      },
    }
    await reviewTools.setup(ctx)
    expect(Object.keys(registered)).toContain("review_inspect")

    const context = {
      sessionID: "review-tools-integration",
      messageID: "message-1",
      id: "tool-1",
      signal: new AbortController().signal,
    }
    const statuses = await Promise.all([
      registered.review_inspect.execute({ request: { operation: "status" } }, context),
      registered.review_inspect.execute({ request: { operation: "status" } }, context),
      registered.review_inspect.execute({ request: { operation: "status" } }, context),
    ])
    for (const status of statuses) {
      expect(status.title).toBe("Review inspection: status")
      expect(status.content).toBe("")
      expect(status.metadata.operation).toBe("status")
    }
    const resolved = await registered.review_inspect.execute(
      { request: { operation: "resolve", revision: "HEAD" } },
      context,
    )
    expect(resolved.content).toMatch(/^[0-9a-f]{40}\n$/)
    expect(queuedCount(repo)).toBe(0)
  }, 30000)
})
