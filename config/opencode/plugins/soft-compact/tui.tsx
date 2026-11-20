// OpenCode TUI plugin: soft-compact
//
// Shows the phases of the soft compaction as toasts, and the armed mode in the
// prompt footer, the way the built-in goal indicator shows a running goal.
//
// The metadata of the session is the channel between the two parts: the server
// part owns the state and writes it, and the TUI has no access to the storage
// of the plugin.
//
// This file is TypeScript with JSX because the footer holds elements, and the
// terminal renderer only has elements through JSX. OpenCode transpiles the
// plugin with the OpenTUI JSX runtime, so no build step belongs here.
//
// The indicator sits in the `prompt.footer` slot, the same slot the built-in
// goal indicator uses, so it stands next to the token count and the goal. The
// `prompt.footer.status` slot is the other candidate: it holds the spinner and
// the location label, which is the left of the composer.

/** @jsxImportSource @opentui/solid */

import { Show } from "solid-js"
import { indicator } from "./indicator.js"

/** The color of the indicator, from the theme of the terminal. */
const color = (context, tone) => {
  if (tone === "warning") return context.theme.text.feedback.warning.base
  if (tone === "active") return context.theme.text.base
  return context.theme.text.muted
}

export default {
  id: "soft-compact.tui",

  setup(context) {
    const stop = context.data.on("session.metadata.updated", (event) => {
      const notice = event.data?.metadata?.softCompact
      if (!notice?.message) return
      const route = context.ui.router.current()
      if (route?.type !== "session" || route.sessionID !== event.data.sessionID) return
      context.ui.toast.show({
        title: "Soft compaction",
        message: notice.message,
        variant: notice.variant ?? "info",
      })
    })

    context.ui.slot({
      append: "prompt.footer",
      render: (props) => {
        const state = () => context.data.session.get(props.sessionID ?? "")?.metadata?.softCompact
        const shown = () => indicator(state())
        return (
          <Show when={shown()}>
            {(current) => (
              <text fg={color(context, current().tone)} wrapMode="none">
                {current().label}
              </text>
            )}
          </Show>
        )
      },
    })

    return () => stop()
  },
}
