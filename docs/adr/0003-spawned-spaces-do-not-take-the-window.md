# A space spawned for another session does not take the window

Herdr shows a new space the moment it exists, so every space `hwt` made also
moved the window to it. That is right for `/hwt`: the person asked for a session
and wants to watch it start. It is wrong for the two commands that spawn work
for someone else to do later. `/hwt-wrapup` starts a reflection session and
prints the plan in this one, and `/wayfinder-hwt` starts one session per ticket
and then reports what it spawned. Each spawn pulled the person away from the
report they were waiting for, and the wayfinder run did it once per ticket.

So a space made for another session opens behind this one. `hwt --no-focus`
reads the space the window is on, makes the space, and gives the window back to
the space it came from. Herdr keeps each space's focused pane, so selecting the
space restores the tab and pane with it. `/hwt-wrapup` and `/wayfinder-hwt`
always pass the flag; plain `/hwt` does not.

## Considered Options

- **Ask `space.new` for a focus flag.** Rejected: its arguments are `name`,
  `folder`, `tab`, `argv`, `task` and `machine` in herdr-app 0.1.15, and the app
  has no other way to make a space. This is the app's choice, not ours.
- **Have `hwt` create the checkout only and let the person open the space.**
  Rejected: `--no-space` starts no session, so the work the space was for would
  not begin, and there is no step that opens an existing checkout as a space.
- **Make every `hwt` call quiet.** Rejected: a person who typed `/hwt` asked to
  go to that session, and a session that starts in front of nobody looks like a
  failure.

## Consequences

- The new space is on screen for the instant it takes to make it, then the
  window returns. It is a flash, not a visit.
- A person who switches space while `hwt` runs chose where to be; the window is
  put back only if it is still on the new space, so that choice is kept.
- The spawned session goes unreached until its space is selected, so a report
  has to name the space. Both commands do, and the wrapup's plan already prints
  its id.
- The flag costs one `herdr-app status` and one `space.select` per spawn, and
  needs no state beyond the space id the window was on.
