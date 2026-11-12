---
name: herdr-app-mod
description: Write, change, or debug a mod for the Herdr desktop app (herdr-app) — a panel, button, layout, or gpui view under ~/.config/herdr-app. Use when the task is to add or change a herdr-app panel, button, badge or layout, when a mod renders nothing, never updates, ignores its timer, does nothing when clicked, or when work touches ~/.config/herdr-app, herdr-plugins/mods, or a mod's main.js. Not for driving Herdr's spaces, tabs, panes or agents (that is the herdr skill) and not for herdr-core.
---

# herdr-app mods

`herdr-app --skill` and `~/.config/herdr-app/AGENTS.md` are the app's own
guide: commands, layout files, theme, `check` and `shot`. Read them first.
This file is what they do not say — how a mod actually runs, and the traps
that cost live debugging.

## Only visible copies run

A mod is instantiated once per place a layout shows it: a block, a stack
child, a float, a pane. Every copy is created, but **only the copies the
window is drawing run**: a copy that is not drawn gets its `init`, then its
`cx.timer` never fires and its `render` never runs.

Not drawn means a layout node with `"hidden": true`, an inactive child of a
`"type": "stack"` node, or a pane mod in a tab or space that is not shown.

So a watcher, poller or background worker in a sidebar panel column does
nothing while the panel is closed — which is most of the time. Nothing
errors; it simply never acts. A questions watcher lived in the panel column
and, with the panel closed, had never polled once.

Keep always-on copies in an always-visible row, at zero size:

```json
{ "id": "my-watch", "type": "block", "size": { "px": 0 },
  "content": { "mod": "my-mod", "props": { "watch": true } } }
```

A zero-width block in the status bar row runs its copy on schedule and draws
nothing; give it width and the same copy draws a chip. The block must be
*visible*: a hidden node or an unselected stack child kills it at any size.

A mod pane follows the same rule: split it only into the tab in front. A pane
created in a hidden tab never resumes its first `await exec(...)`, so it sits
empty when the person arrives.

**Probe, do not guess.** A copy that seems dead may simply not be drawn. Add
a temporary trace (`exec("sh", ["-c", 'printf "%s\\n" "$1" >> /tmp/x', "sh", line])`),
or make the block visible, or select it with
`herdr-app do layout.select '{"stack":"<stack>","child":"<id>"}'` and watch
the poll resume.

## Copies share one context

All copies of one mod run in one JavaScript context. `props()` is reliable
inside `init`; after an `await` it can answer for a different copy. Read the
props once and keep them:

```js
const own = props() ?? {};
this.kind = own.watch ? "watch" : own.pane ? "pane" : "column";
this.autoOpen = own.autoOpen !== false;
```

Two consequences:

- A pane copy has no id of its own: `props().pane` is injected for header
  mods only. Tell the copy which **tab** it is in (`props.tab`), then find
  the pane in `panes()` by `{mod, tab}`.
- Gate side effects by copy. One writer per shared key, one toast. A newborn
  pane copy that publishes "0 waiting" blanks a badge the watcher just set.

## `run()` returns null

`run("tab.new", …)`, `run("pane.split", …)` and the `layout.*` commands all
return null; the result exists only in the world. Poll `spaces()` or
`panes()` for it, and expect a lag. Record a pending marker before spawning,
or a second click in that window spawns a duplicate.

Mods inherit the app's PATH, not a login shell's: resolve a program to an
absolute path (for example `home() + "/.opencode/bin/opencode"`) before
`exec` or `tab.new` uses it.

## Shared state is the channel

`shared(key)` / `setShared(key, value)` is persisted, and a write re-renders
every mod. Use it for cross-copy coordination and for extension points that
other mods read.

- The sidebar's Files and Changes buttons come from the shipped `tabs` mod:
  a panel needs its id in `shared("workspace.panels")` and a block in the
  `panel-body` stack. That mod remembers the open panel **per space** in
  `data/tabs/store.json`; a stale id there re-opens the panel after a layout
  edit, so clear it.
- Herdr replaces its own mods on every start, so a shipped mod cannot be
  edited in place: clone it (`mod.clone`) or keep a fork in a repo and deploy
  it. To add a button to the tab bar, fork `mods/tabs` and have it read a
  shared registry; `herdr-plugins/mods/panel-tabs/` is a worked example.
- `run("layout.select", {stack, child})` plus `layout.show` / `layout.hide`
  `{id}` switch panels.
- `notify({title, body, level, action: {name: "agent.focus", args: {terminal}}})`
  is the "take the person to the agent that needs them" toast.
- A mod that lists agents calls `setAgentOrder(addresses)` on render; without
  it `agent.next` and `agent.prev` follow the model's order, not your list.

## The UI facts that bite

- Use theme colors. `muted` is a 60% mix of foreground and background: fine
  for a label, too dim for body text. `dim` is dimmer still.
- Give a flex child that holds text `min_w(0)`, or its content pushes the
  column wider than the window instead of truncating.
- `herdr-app ls` lists terminals only. A mod pane appears only in `panes()`
  and in screenshots.

## Testing

After each change:

```sh
herdr-app check <mod folder>   # loads and renders once; errors are exact
herdr-app status               # layout, focus, overlays, file and mod errors
herdr-app shot /tmp/mod.png    # the app's own last frame; look at it
```

`check` renders once: it exercises neither timers nor async polling, and its
shared state starts empty. A passing check proves the first render, not the
behaviour.

There is no pointer automation on the person's display. Test a click path by
driving the mod headlessly — a loader that maps `herdr`, `gpui-kit` and
`gpui-base` to stubs, an element stub that records calls, and a click helper
that runs the handler the mod attached — or ask the person to click. Never
infer that a click works from the fact that the handler exists.

## Done means

- `herdr-app check` passes, `herdr-app status` shows no errors, and you
  looked at `shot`.
- The copy that must run is drawn: not hidden, not an unselected stack child,
  in the front tab.
- Props-derived identity is captured in `init`; no `props()` after an await.
- Exactly one copy publishes each shared key.
- The click path was exercised headlessly or by the person.
