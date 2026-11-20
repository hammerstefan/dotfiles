// The indicator of the soft compaction in the prompt footer.
//
// The server part writes the state of the mode into the metadata of the
// session. This module turns that state into the label and the tone of the
// indicator, so that the rule can be tested without a terminal.

const LABELS = {
  armed: "◆ cmp({threshold})",
  "wrapping-up": "◆ cmp({threshold}) · wrapping up",
  compacting: "◆ cmp({threshold}) · compacting",
}

const TONES = {
  armed: "muted",
  "wrapping-up": "warning",
  compacting: "active",
}

/**
 * A token count as a short number: `400000` is `400k` and `1000000` is `1m`.
 * A count that is not a round number keeps one decimal.
 */
export const formatTokens = (value) => {
  if (typeof value !== "number" || !Number.isFinite(value) || value <= 0) return undefined
  if (value % 1_000_000 === 0) return `${value / 1_000_000}m`
  if (value % 1_000 === 0) return `${value / 1_000}k`
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}m`
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}k`
  return String(value)
}

/** The label and the tone of the indicator, or undefined when the mode is off. */
export const indicator = (state) => {
  const status = state?.status
  if (!status || status === "off") return undefined
  const threshold = formatTokens(state?.threshold) ?? "?"
  const label = (LABELS[status] ?? LABELS.armed).replace("{threshold}", threshold)
  return {
    label,
    tone: TONES[status] ?? TONES.armed,
  }
}

export const internals = { LABELS, TONES }
