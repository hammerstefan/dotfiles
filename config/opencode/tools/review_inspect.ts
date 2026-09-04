import { tool } from "@opencode-ai/plugin"

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

type Budget = {
  started: number
  commands: number
  remoteCalls: number
  bytes: number
}

const callerBudgets = new Map<string, Budget>()
const worktreeBudgets = new Map<string, Budget>()

const repositoryPath = tool.schema
  .string()
  .min(1)
  .max(512)
  .refine(
    (value) =>
      !value.startsWith("/") &&
      !value.includes("\\") &&
      !value.split("/").some((segment) => segment === "" || segment === "." || segment === ".."),
    "must be a canonical repository-relative POSIX path",
  )

const revision = tool.schema
  .string()
  .min(1)
  .max(512)
  .refine((value) => !/\s/.test(value) && !value.startsWith("-"), "must be a safe Git revision")

const commitId = tool.schema.string().regex(/^[0-9a-f]{40}(?:[0-9a-f]{24})?$/)

const request = tool.schema.discriminatedUnion("operation", [
  tool.schema.object({ operation: tool.schema.literal("status") }).strict(),
  tool.schema
    .object({
      operation: tool.schema.literal("uncommitted_diff"),
      staged: tool.schema.boolean(),
      path: repositoryPath.nullable(),
    })
    .strict(),
  tool.schema
    .object({ operation: tool.schema.literal("show"), revision: commitId, path: repositoryPath.nullable() })
    .strict(),
  tool.schema.object({ operation: tool.schema.literal("resolve"), revision }).strict(),
  tool.schema.object({ operation: tool.schema.literal("first_parent"), revision: commitId }).strict(),
  tool.schema
    .object({ operation: tool.schema.literal("merge_base"), left: commitId, right: commitId })
    .strict(),
  tool.schema
    .object({
      operation: tool.schema.literal("range_diff"),
      base: commitId,
      reviewed: commitId,
      path: repositoryPath.nullable(),
    })
    .strict(),
  tool.schema
    .object({
      operation: tool.schema.literal("pr_metadata"),
      number: tool.schema.number().int().min(1).max(2_147_483_647),
    })
    .strict(),
  tool.schema
    .object({
      operation: tool.schema.literal("pr_diff"),
      number: tool.schema.number().int().min(1).max(2_147_483_647),
    })
    .strict(),
  tool.schema
    .object({
      operation: tool.schema.literal("pr_discussion"),
      number: tool.schema.number().int().min(1).max(2_147_483_647),
    })
    .strict(),
])

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

const budgetFor = (budgets: Map<string, Budget>, key: string) => {
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

const readBounded = async (stream: ReadableStream<Uint8Array>, maximum: number, abort: () => void) => {
  const chunks: Uint8Array[] = []
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

const validateReservation = (
  budget: Budget,
  command: string[],
  byteReservation: number,
  limits: { commands: number; remoteCalls: number; bytes: number },
  label: string,
) => {
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

const applyReservation = (budget: Budget, command: string[], byteReservation: number) => {
  const nextCommands = budget.commands + 1
  const nextRemoteCalls = budget.remoteCalls + Number(command[0] === "gh")
  budget.commands = nextCommands
  budget.remoteCalls = nextRemoteCalls
  budget.bytes += byteReservation
}

const run = async (command: string[], cwd: string, signal: AbortSignal, caller: string) => {
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
  let actualBytes: number | undefined
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
      const detail = new TextDecoder("utf-8", { fatal: false }).decode(stderr).trim()
      throw new Error(detail.slice(0, 2000) || "read-only review inspection failed")
    }
    return new TextDecoder("utf-8", { fatal: true }).decode(stdout)
  } finally {
    if (actualBytes !== undefined) {
      const unusedBytes = byteReservation - actualBytes
      callerBudget.bytes -= unusedBytes
      worktreeBudget.bytes -= unusedBytes
    }
    signal.removeEventListener("abort", forwardAbort)
  }
}

const runGit = async (arguments_: string[], cwd: string, signal: AbortSignal, caller: string) =>
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
      ...arguments_,
    ],
    cwd,
    signal,
    caller,
  )

export default tool({
  description:
    "Inspect review scopes using fixed read-only Git and GitHub argument arrays; never executes arbitrary shell syntax",
  args: { request },
  async execute(args, context) {
    context.metadata({ title: `Review inspection: ${args.request.operation}` })
    const value = args.request
    let command: string[]
    let gitArguments: string[] | undefined
    switch (value.operation) {
      case "status":
        gitArguments = ["status", "--short", "--untracked-files=all"]
        command = []
        break
      case "uncommitted_diff":
        gitArguments = ["--no-pager", "diff", "--no-ext-diff", "--no-textconv"]
        if (value.staged) gitArguments.push("--cached")
        if (value.path) gitArguments.push("--", value.path)
        command = []
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
        command = []
        break
      case "resolve":
        gitArguments = ["rev-parse", "--verify", "--end-of-options", `${value.revision}^{commit}`]
        command = []
        break
      case "first_parent":
        gitArguments = ["rev-list", "--parents", "-n", "1", value.revision]
        command = []
        break
      case "merge_base":
        gitArguments = ["merge-base", "--", value.left, value.right]
        command = []
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
        command = []
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
    const output = gitArguments
      ? await runGit(gitArguments, context.worktree, context.abort, context.sessionID)
      : await run(command, context.worktree, context.abort, context.sessionID)
    return {
      title: `Review inspection: ${value.operation}`,
      output,
      metadata: { operation: value.operation, bytes: Buffer.byteLength(output, "utf8") },
    }
  },
})
