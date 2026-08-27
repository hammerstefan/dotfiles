import { tool } from "@opencode-ai/plugin"

const MAX_TRANSPORT_BYTES = 1024 * 1024
const MAX_WRITER_OUTPUT_BYTES = 16 * 1024
const MAX_WRITER_ERROR_BYTES = 64 * 1024
const MAX_TRACKED_INVOCATIONS = 10_000
const attemptedInvocations = new Set<string>()

const readBounded = async (stream: ReadableStream<Uint8Array>, maximum: number, abort: () => void) => {
  const chunks: Uint8Array[] = []
  let total = 0
  for await (const chunk of stream) {
    total += chunk.byteLength
    if (total > maximum) {
      abort()
      throw new Error("human-review report writer exceeded its output safety limit")
    }
    chunks.push(chunk)
  }
  const output = new Uint8Array(total)
  let offset = 0
  for (const chunk of chunks) {
    output.set(chunk, offset)
    offset += chunk.byteLength
  }
  return new TextDecoder("utf-8", { fatal: false }).decode(output)
}

export default tool({
  description:
    "Validate and atomically persist a non-empty review-human report under .opencode/reviews in the current Git worktree",
  args: {
    payload: tool.schema
      .unknown()
      .describe("Candidate review-human JSON object; the Python writer is the schema authority"),
  },
  async execute(args, context) {
    context.metadata({ title: "Persist human-review attention report" })
    const invocation = `${context.sessionID}:${context.messageID}`
    if (attemptedInvocations.has(invocation)) {
      throw new Error("human-review report persistence is limited to one attempt per command")
    }
    if (attemptedInvocations.size >= MAX_TRACKED_INVOCATIONS) {
      const oldest = attemptedInvocations.values().next().value
      if (oldest) attemptedInvocations.delete(oldest)
    }
    attemptedInvocations.add(invocation)
    const script = `${import.meta.dir}/../script/write-review-human-report.py`
    const encoded = JSON.stringify(args.payload)
    if (encoded === undefined || Buffer.byteLength(encoded, "utf8") > MAX_TRANSPORT_BYTES) {
      throw new Error("human-review report exceeds the transport safety limit")
    }
    const controller = new AbortController()
    const forwardAbort = () => controller.abort()
    context.abort.addEventListener("abort", forwardAbort, { once: true })
    const [stdout, stderr, exitCode] = await (async () => {
      const process = Bun.spawn(
        ["python3", script, "--stdin", "--worktree", context.worktree],
        {
          cwd: context.worktree,
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
    })().finally(() => context.abort.removeEventListener("abort", forwardAbort))
    if (exitCode !== 0) {
      const detail = stderr.trim()
      throw new Error(
        detail.startsWith("ERROR:")
          ? detail.slice("ERROR:".length).trim().slice(0, 2000)
          : "human-review report persistence failed",
      )
    }

    let result: unknown
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
      output: `Artifact: ${result.path}`,
      metadata: result,
    }
  },
})
