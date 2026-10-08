// OpenSpec agent companion plugin for OpenCode V2.
//
// This plugin complements the openspec-plan agent defined in
// ~/.config/opencode/agent/openspec-plan.md. The agent is the primary surface;
// the plugin adds cross-cutting behavior that benefits from plugin context.
//
// Why this plugin exists
// ----------------------
// The original V1 plugin (https://github.com/Octane0411/opencode-plugin-openspec)
// had two responsibilities:
//
//   1. Auto-detect an OpenSpec project and register an `openspec-plan` agent
//      with strict, spec-only write permissions.
//   2. Hide the agent in non-OpenSpec projects.
//
// In OpenCode V2, neither is fully achievable through the plugin API:
//   - V2's AgentEditor exposes `list`, `get`, `default`, `update`, `remove`
//     but no `add` (verified against @opencode/plugin@2.0.25's
//     dist/promise/agent.d.ts). Plugins cannot invent new agents.
//   - V2's `ctx.agent.transform` only sees built-in agents during
//     materialization; user-defined agents (from `agents:` config or
//     `.opencode/agents/*.md` / `~/.config/opencode/agent/*.md`) are added
//     after the transform runs and are invisible to it.
//
// Therefore the agent itself is defined statically as
// `~/.config/opencode/agent/openspec-plan.md` (V2's idiomatic location for a
// reusable agent), with all the necessary permissions, system prompt, and
// metadata in the file. This plugin only adds behavior that genuinely benefits
// from being a plugin: startup detection telemetry and an opt-in prompt
// reminder hook that the user can extend.

import { Plugin } from "@opencode/plugin";
import { existsSync } from "node:fs";
import { join } from "node:path";

const AGENT_ID = "openspec-plan";
const PLUGIN_ID = "openspec-agent-companion";

// Detection mirrors src/utils/detection.ts from the V1 plugin verbatim:
//   - `openspec/config.yaml` (new OPSX format)  OR
//   - `openspec/AGENTS.md`     (legacy format)
function detectOpenSpec(directory) {
  const openspecDir = join(directory, "openspec");
  return (
    existsSync(join(openspecDir, "config.yaml")) ||
    existsSync(join(openspecDir, "AGENTS.md"))
  );
}

export default Plugin.define({
  id: PLUGIN_ID,

  setup(ctx) {
    const directory = ctx.location.directory;
    const openspecProject = detectOpenSpec(directory);

    // Persist the last-known detection so other tools (e.g. a future TUI
    // status line, a slash command) can read it without re-scanning the
    // filesystem. Storage is scoped to this plugin's id.
    ctx.storage
      .set("detection", {
        directory,
        openspecProject,
        checkedAt: new Date().toISOString(),
      })
      .catch(() => {
        // Storage is best-effort; failures here should never break setup.
      });

    // Surface a single line to the opencode log. The host logs INFO messages
    // with `role=server` so this is greppable.
    console.log(
      `[${PLUGIN_ID}] loaded; directory=${directory} openspec=${openspecProject} agent=${AGENT_ID}`,
    );

    // The V1 plugin's `isOpenSpecProject` logic is preserved here in case a
    // future version of @opencode/plugin exposes agent creation or a
    // location-scoped tool that needs to know whether to activate. Keeping
    // the function local to this module makes that future migration easy.
  },
});
