// OpenCode V2 plugin: review-tools
//
// Ports the former V1 custom tools `review_inspect` and
// `write_review_human_report` (config/opencode/tools/*.ts) to the V2 plugin
// API. V2 does not run V1 plugin implementations, so these are re-registered
// here via ctx.tool.transform. Tool names are unchanged so the existing
// agent permission rules (`action: review_inspect` etc.) keep matching.
//
// Porting notes versus the V1 files:
// - zod schemas became JSON Schema; the zod `.refine` safety rules that JSON
//   Schema cannot express are enforced at the top of `execute` instead.
// - The V2 tool execute context exposes sessionID/agent/messageID/id/
//   progress/signal but no worktree or directory, so the V1 `context.worktree`
//   is re-derived per session: ctx.session.get(...) -> location.directory ->
//   `git rev-parse --show-toplevel`, cached per session.
// - `context.abort` became `context.signal` (with a fallback shim like
//   plugins/session-stats.js uses).

const MAX_OUTPUT_BYTES = 8 * 1024 * 1024
const MAX_ERROR_BYTES = 64 * 1024
const MAX_COMMANDS_PER_CALLER = 20
const MAX_REMOTE_CALLS_PER_CALLER = 5
const MAX_BYTES_PER_CALLER = 24 * 1024 * 1024
const MAX_COMMANDS_PER_WORKTREE = 300
const MAX_REMOTE_CALLS_PER_WORKTREE = 80
const MAX_BYTES_PER_WORKTREE = 384 * 1024 * 1024
const MAX_WINDOW_MILLISECONDS = 10 * 60 * 1000
const COMMAND_TIMEOUT_MILLISECONDS = 60 * 1000

const MAX_TRANSPORT_BYTES = 1024 * 1024
const MAX_WRITER_OUTPUT_BYTES = 16 * 1024
const MAX_WRITER_ERROR_BYTES = 64 * 1024
const MAX_TRACKED_INVOCATIONS = 10_000
const MAX_CACHED_WORKTREES = 200

const callerBudgets = new Map()
const worktreeBudgets = new Map()
const attemptedInvocations = new Set()
const sessionWorktrees = new Map()

const PR_DISCUSSION_QUERY = `query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviews(first: 100) {
        pageInfo { hasNextPage endCursor }
        nodes {
          author { login }
          state
          body
          url
          createdAt
        }
      }
      reviewThreads(first: 100) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          originalLine
          originalStartLine
          startLine
          diffSide
          startDiffSide
          subjectType
          comments(first: 50) {
            pageInfo { hasNextPage endCursor }
            nodes {
              id
              author { login }
              body
              url
              createdAt
              path
              line
              originalLine
              originalStartLine
              startLine
              originalCommit { oid }
            }
          }
        }
      }
      comments(first: 100) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          author { login }
          body
          url
          createdAt
        }
      }
    }
  }
}`

const PR_DISCUSSION_PROJECTION = `{
  pr: {
    reviews: {
      hasNextPage: .data.repository.pullRequest.reviews.pageInfo.hasNextPage,
      nodes: [.data.repository.pullRequest.reviews.nodes[] | {
        author: .author.login,
        state,
        body: (.body // "")[0:2000],
        url,
        createdAt
      }]
    },
    threads: {
      hasNextPage: .data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage,
      nodes: [.data.repository.pullRequest.reviewThreads.nodes[] | {
        id,
        isResolved,
        isOutdated,
        path,
        line,
        originalLine,
        originalStartLine,
        startLine,
        diffSide,
        startDiffSide,
        subjectType,
        comments: {
          hasNextPage: .comments.pageInfo.hasNextPage,
          nodes: [.comments.nodes[] | {
            id,
            author: .author.login,
            body: (.body // "")[0:2000],
            url,
            createdAt,
            path,
            line,
            originalLine,
            originalStartLine,
            startLine,
            originalCommit: .originalCommit.oid
          }]
        }
      }]
    },
    issueComments: {
      hasNextPage: .data.repository.pullRequest.comments.pageInfo.hasNextPage,
      nodes: [.data.repository.pullRequest.comments.nodes[] | {
        id,
        author: .author.login,
        body: (.body // "")[0:2000],
        url,
        createdAt
      }]
    }
  }
}`

const commitIdSchema = { type: "string", pattern: "^[0-9a-f]{40}([0-9a-f]{24})?$" }
const revisionSchema = { type: "string", minLength: 1, maxLength: 512 }
const optionalPathSchema = { type: ["string", "null"], minLength: 1, maxLength: 512 }
const prNumberSchema = { type: "integer", minimum: 1, maximum: 2_147_483_647 }

const operationBranch = (operation, properties, required) => ({
  type: "object",
  properties: { operation: { const: operation }, ...properties },
  required: ["operation", ...required],
  additionalProperties: false,
})

const requestSchema = {
  oneOf: [
    operationBranch("status", {}, []),
    operationBranch("uncommitted_diff", { staged: { type: "boolean" }, path: optionalPathSchema }, [
      "staged",
      "path",
    ]),
    operationBranch("show", { revision: commitIdSchema, path: optionalPathSchema }, ["revision", "path"]),
    operationBranch("resolve", { revision: revisionSchema }, ["revision"]),
    operationBranch("first_parent", { revision: commitIdSchema }, ["revision"]),
    operationBranch("merge_base", { left: commitIdSchema, right: commitIdSchema }, ["left", "right"]),
    operationBranch(
      "range_diff",
      { base: commitIdSchema, reviewed: commitIdSchema, path: optionalPathSchema },
      ["base", "reviewed", "path"],
    ),
    operationBranch("pr_metadata", { number: prNumberSchema }, ["number"]),
    operationBranch("pr_diff", { number: prNumberSchema }, ["number"]),
    operationBranch("pr_discussion", { number: prNumberSchema }, ["number"]),
  ],
}

const assertRepositoryPath = (value) => {
  if (typeof value !== "string") return
  const unsafe =
    value.length < 1 ||
    value.length > 512 ||
    value.startsWith("/") ||
    value.includes("\\") ||
    value.split("/").some((segment) => segment === "" || segment === "." || segment === "..")
  if (unsafe) throw new Error("path must be a canonical repository-relative POSIX path")
}

const assertRevision = (value) => {
  if (typeof value !== "string") return
  if (value.length < 1 || /\s/.test(value) || value.startsWith("-")) {
    throw new Error("revision must be a safe Git revision")
  }
}

const assertRequestSafety = (value) => {
  for (const key of ["path", "revision", "base", "reviewed", "left", "right"]) {
    const item = value[key]
    if (item === undefined || item === null) continue
    if (key === "path") assertRepositoryPath(item)
    else assertRevision(item)
  }
}

const budgetFor = (budgets, key) => {
  const now = Date.now()
  for (const [candidate, value] of budgets) {
    if (now - value.started >= MAX_WINDOW_MILLISECONDS) budgets.delete(candidate)
  }
  const existing = budgets.get(key)
  if (!existing || now - existing.started >= MAX_WINDOW_MILLISECONDS) {
    const replacement = {
      started: now,
      commands: 0,
      remoteCalls: 0,
      bytes: 0,
    }
    budgets.set(key, replacement)
    return replacement
  }
  return existing
}

const readBounded = async (stream, maximum, abort) => {
  const chunks = []
  let total = 0
  for await (const chunk of stream) {
    total += chunk.byteLength
    if (total > maximum) {
      abort()
      throw new Error("read-only review inspection exceeded its output safety limit")
    }
    chunks.push(chunk)
  }
  const output = new Uint8Array(total)
  let offset = 0
  for (const chunk of chunks) {
    output.set(chunk, offset)
    offset += chunk.byteLength
  }
  return output
}

const decode = (bytes, fatal) => new TextDecoder("utf-8", { fatal }).decode(bytes)

const validateReservation = (budget, command, byteReservation, limits, label) => {
  const nextCommands = budget.commands + 1
  const nextRemoteCalls = budget.remoteCalls + Number(command[0] === "gh")
  if (nextCommands > limits.commands) {
    throw new Error(`review inspection exceeded its ${label} command budget`)
  }
  if (nextRemoteCalls > limits.remoteCalls) {
    throw new Error(`review inspection exceeded its ${label} remote-call budget`)
  }
  if (budget.bytes + byteReservation > limits.bytes) {
    throw new Error(`review inspection exceeded its ${label} byte budget`)
  }
}

const applyReservation = (budget, command, byteReservation) => {
  const nextCommands = budget.commands + 1
  const nextRemoteCalls = budget.remoteCalls + Number(command[0] === "gh")
  budget.commands = nextCommands
  budget.remoteCalls = nextRemoteCalls
  budget.bytes += byteReservation
}

const run = async (command, cwd, signal, caller) => {
  const callerBudget = budgetFor(callerBudgets, `${cwd}:${caller}`)
  const worktreeBudget = budgetFor(worktreeBudgets, cwd)
  const byteReservation = MAX_OUTPUT_BYTES + MAX_ERROR_BYTES
  validateReservation(
    callerBudget,
    command,
    byteReservation,
    {
      commands: MAX_COMMANDS_PER_CALLER,
      remoteCalls: MAX_REMOTE_CALLS_PER_CALLER,
      bytes: MAX_BYTES_PER_CALLER,
    },
    "caller",
  )
  validateReservation(
    worktreeBudget,
    command,
    byteReservation,
    {
      commands: MAX_COMMANDS_PER_WORKTREE,
      remoteCalls: MAX_REMOTE_CALLS_PER_WORKTREE,
      bytes: MAX_BYTES_PER_WORKTREE,
    },
    "shared worktree",
  )
  applyReservation(callerBudget, command, byteReservation)
  applyReservation(worktreeBudget, command, byteReservation)

  const controller = new AbortController()
  const forwardAbort = () => controller.abort()
  signal.addEventListener("abort", forwardAbort, { once: true })
  let actualBytes
  try {
    const process = Bun.spawn(command, {
      cwd,
      stdin: "ignore",
      stdout: "pipe",
      stderr: "pipe",
      signal: controller.signal,
      timeout: COMMAND_TIMEOUT_MILLISECONDS,
      killSignal: "SIGKILL",
    })
    const [stdout, stderr, exitCode] = await Promise.all([
      readBounded(process.stdout, MAX_OUTPUT_BYTES, () => controller.abort()),
      readBounded(process.stderr, MAX_ERROR_BYTES, () => controller.abort()),
      process.exited,
    ])
    actualBytes = stdout.byteLength + stderr.byteLength
    if (exitCode !== 0) {
      const detail = decode(stderr, false).trim()
      throw new Error(detail.slice(0, 2000) || "read-only review inspection failed")
    }
    return decode(stdout, true)
  } finally {
    if (actualBytes !== undefined) {
      const unusedBytes = byteReservation - actualBytes
      callerBudget.bytes -= unusedBytes
      worktreeBudget.bytes -= unusedBytes
    }
    signal.removeEventListener("abort", forwardAbort)
  }
}

const runGit = async (args_, cwd, signal, caller) =>
  run(
    [
      "git",
      "-c",
      "core.pager=cat",
      "-c",
      "core.hooksPath=/dev/null",
      "-c",
      "core.fsmonitor=false",
      "-c",
      "diff.external=",
      "-c",
      "diff.trustExitCode=false",
      "-c",
      "filter.lfs.process=",
      "-c",
      "filter.lfs.smudge=cat",
      "-c",
      "filter.lfs.required=false",
      ...args_,
    ],
    cwd,
    signal,
    caller,
  )

const buildInspectCommand = (value) => {
  let command
  let gitArguments
  switch (value.operation) {
    case "status":
      gitArguments = ["status", "--short", "--untracked-files=all"]
      break
    case "uncommitted_diff":
      gitArguments = ["--no-pager", "diff", "--no-ext-diff", "--no-textconv"]
      if (value.staged) gitArguments.push("--cached")
      if (value.path) gitArguments.push("--", value.path)
      break
    case "show":
      gitArguments = [
        "--no-pager",
        "show",
        "--no-ext-diff",
        "--no-textconv",
        "--format=fuller",
        value.revision,
      ]
      if (value.path) gitArguments.push("--", value.path)
      break
    case "resolve":
      gitArguments = ["rev-parse", "--verify", "--end-of-options", `${value.revision}^{commit}`]
      break
    case "first_parent":
      gitArguments = ["rev-list", "--parents", "-n", "1", value.revision]
      break
    case "merge_base":
      gitArguments = ["merge-base", "--", value.left, value.right]
      break
    case "range_diff":
      gitArguments = [
        "--no-pager",
        "diff",
        "--no-ext-diff",
        "--no-textconv",
        value.base,
        value.reviewed,
      ]
      if (value.path) gitArguments.push("--", value.path)
      break
    case "pr_metadata":
      command = [
        "gh",
        "api",
        "-X",
        "GET",
        `repos/{owner}/{repo}/pulls/${value.number}`,
        "--jq",
        "{number: .number, url: .html_url, base_ref: .base.ref, base_revision: .base.sha, base_repository: .base.repo.full_name, head_ref: .head.ref, head_revision: .head.sha, head_repository: .head.repo.full_name}",
      ]
      break
    case "pr_diff":
      command = ["gh", "pr", "diff", String(value.number), "--color=never"]
      break
    case "pr_discussion":
      command = [
        "gh",
        "api",
        "graphql",
        "-f",
        `query=${PR_DISCUSSION_QUERY}`,
        "-F",
        "owner={owner}",
        "-F",
        "name={repo}",
        "-F",
        `number=${value.number}`,
        "--jq",
        PR_DISCUSSION_PROJECTION,
      ]
      break
  }
  return { command, gitArguments }
}

const gitToplevel = async (directory) => {
  const process = Bun.spawn(["git", "-C", directory, "rev-parse", "--show-toplevel"], {
    stdin: "ignore",
    stdout: "pipe",
    stderr: "pipe",
  })
  const [stdout, exitCode] = await Promise.all([
    readBounded(process.stdout, 4096, () => process.kill()),
    process.exited,
  ])
  if (exitCode !== 0) {
    throw new Error(`unable to resolve the git worktree for the session directory ${directory}`)
  }
  return decode(stdout, false).trim()
}

export default {
  id: "review-tools",
  async setup(ctx) {
    const worktreeFor = async (sessionID) => {
      const cached = sessionWorktrees.get(sessionID)
      if (cached) return cached
      const response = await ctx.session.get({ sessionID })
      const info = response?.data ?? response
      const directory = info?.location?.directory ?? info?.directory
      if (!directory) {
        throw new Error("unable to resolve the session directory for review inspection")
      }
      const worktree = await gitToplevel(directory)
      if (sessionWorktrees.size >= MAX_CACHED_WORKTREES) {
        const oldest = sessionWorktrees.keys().next().value
        if (oldest) sessionWorktrees.delete(oldest)
      }
      sessionWorktrees.set(sessionID, worktree)
      return worktree
    }

    await ctx.tool.transform((editor) => {
      editor.add({
        name: "review_inspect",
        description:
          "Inspect review scopes using fixed read-only Git and GitHub argument arrays; never executes arbitrary shell syntax",
        input: {
          type: "object",
          properties: { request: requestSchema },
          required: ["request"],
          additionalProperties: false,
        },
        async execute(input, context) {
          const signal = context.signal ?? context.abort
          const value = input.request
          assertRequestSafety(value)
          const { command, gitArguments } = buildInspectCommand(value)
          const worktree = await worktreeFor(context.sessionID)
          const output = gitArguments
            ? await runGit(gitArguments, worktree, signal, context.sessionID)
            : await run(command, worktree, signal, context.sessionID)
          return {
            title: `Review inspection: ${value.operation}`,
            content: output,
            metadata: { operation: value.operation, bytes: Buffer.byteLength(output, "utf8") },
          }
        },
      })

      editor.add({
        name: "write_review_human_report",
        description:
          "Validate and atomically persist a non-empty review-human report under .opencode/reviews in the current Git worktree",
        input: {
          type: "object",
          properties: {
            payload: {
              description: "Candidate review-human JSON object; the Python writer is the schema authority",
            },
          },
          required: ["payload"],
          additionalProperties: false,
        },
        async execute(input, context) {
          const signal = context.signal ?? context.abort
          const invocation = `${context.sessionID}:${context.messageID}`
          if (attemptedInvocations.has(invocation)) {
            throw new Error("human-review report persistence is limited to one attempt per command")
          }
          if (attemptedInvocations.size >= MAX_TRACKED_INVOCATIONS) {
            const oldest = attemptedInvocations.values().next().value
            if (oldest) attemptedInvocations.delete(oldest)
          }
          attemptedInvocations.add(invocation)
          const worktree = await worktreeFor(context.sessionID)
          const encoded = JSON.stringify(input.payload)
          if (encoded === undefined || Buffer.byteLength(encoded, "utf8") > MAX_TRANSPORT_BYTES) {
            throw new Error("human-review report exceeds the transport safety limit")
          }
          const script = `${import.meta.dir}/../script/write-review-human-report.py`
          const controller = new AbortController()
          const forwardAbort = () => controller.abort()
          signal.addEventListener("abort", forwardAbort, { once: true })
          const [stdout, stderr, exitCode] = await (async () => {
            const process = Bun.spawn(
              ["python3", script, "--stdin", "--worktree", worktree],
              {
                cwd: worktree,
                stdin: "pipe",
                stdout: "pipe",
                stderr: "pipe",
                signal: controller.signal,
                timeout: 120_000,
                killSignal: "SIGKILL",
              },
            )
            process.stdin.write(encoded)
            process.stdin.end()
            return Promise.all([
              readBounded(process.stdout, MAX_WRITER_OUTPUT_BYTES, () => controller.abort()),
              readBounded(process.stderr, MAX_WRITER_ERROR_BYTES, () => controller.abort()),
              process.exited,
            ])
          })().finally(() => signal.removeEventListener("abort", forwardAbort))
          if (exitCode !== 0) {
            const detail = decode(stderr, false).trim()
            throw new Error(
              detail.startsWith("ERROR:")
                ? detail.slice("ERROR:".length).trim().slice(0, 2000)
                : "human-review report persistence failed",
            )
          }

          let result
          try {
            result = JSON.parse(stdout)
          } catch {
            throw new Error("human-review report writer returned malformed output")
          }
          if (
            !result ||
            typeof result !== "object" ||
            !("path" in result) ||
            typeof result.path !== "string" ||
            !("status" in result) ||
            typeof result.status !== "string" ||
            !("items" in result) ||
            typeof result.items !== "number"
          ) {
            throw new Error("human-review report writer returned an invalid result")
          }

          return {
            title: "Human-review report persisted",
            content: `Artifact: ${result.path}`,
            metadata: result,
          }
        },
      })
    })
  },
}
