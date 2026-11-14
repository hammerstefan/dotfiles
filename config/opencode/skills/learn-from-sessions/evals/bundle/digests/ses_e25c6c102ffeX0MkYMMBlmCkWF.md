# ses_e25c6c102ffeX0MkYMMBlmCkWF: Review network research reports

## What the person asked for

The session is a `review-readability` child, spawned by a review-council
coordinator. Its model is `github-copilot/claude-opus-5.5`. It ran in
`~/.herdr/worktrees/monitor-agent/review-writing`. One USER turn carried the
whole task. The directive, USER 1 (line 4):

> Read-only readability review of group NETWORK/PROXY RESEARCH in repo
> /home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/review-writing.
> Review ALL five files: research/acl-fence.md, research/iron-proxy-plane.md,
> research/separate-bridges.md, research/two-bridge-gateway.md,
> research/two-workshop.md. Use .kb/writing-style.md as guidance. Return every
> file examined; up to 12 actionable readability findings (path:line, quote,
> what reader misreads, concrete revision), separate optional small editorials,
> and cross-file overlap where reports repeat without clarifying distinct
> result. Preserve historical observations and avoid guessing current status.
> Do not edit files.

## What was produced, and whether it worked

The agent read five research files and three instruction files, then returned
one report. The report has these parts:

- 9 substantive findings, IDs `RDB-1` through `RDB-9`, each with a severity of
  high, medium, or low (lines 10-53).
- 8 editorial suggestions, IDs `RDS-1` through `RDS-8` (lines 57-64).
- One "Repeated text across files" section (lines 66-73).
- A `review-json` block listing the 9 findings (line 75).
- A `review-readability-json` block listing the 8 suggestions, grouped by file
  (line 85, clipped in the flat file; the full text is in the raw export).

The nine findings are:

- `RDB-1` high, `research/iron-proxy-plane.md:32` (line 10). The Verdict
  states the 403 refusal as a property of the committed configuration, while
  lines 49-54 say the branch policy has `warn: true` and forwards unlisted
  hosts.
- `RDB-2` medium, `research/iron-proxy-plane.md:19` (line 15). "Committed
  policy" names two files, the project-directory file and the spike-branch
  file, and the reader cannot tell which the Verdict is about.
- `RDB-3` medium, `research/iron-proxy-plane.md:67` (line 20). Two startup
  record statements seem to contradict: one names the management listener and
  the next says the proxy record does not.
- `RDB-4` medium, `research/iron-proxy-plane.md:17` (line 25). The file says
  "every claim the ticket asks about holds" but never names the ticket.
- `RDB-5` medium, `research/two-workshop.md:171` (line 30). A measured result
  also appears in the "Not verified" list, so the reader cannot tell whether
  it was measured.
- `RDB-6` low, `research/two-workshop.md:44` (line 35). "Two things do not
  hold" is followed by "A third finding is narrower", so the reader counts DNS
  as a third failure.
- `RDB-7` medium, `research/separate-bridges.md:19` (line 40). "Gateway" has
  three meanings, and line 91 does not say which bridge owns `10.252.0.1`.
- `RDB-8` low, `research/acl-fence.md:65` (line 45). "Both" has no clear
  referent.
- `RDB-9` low, `research/two-bridge-gateway.md:40` (line 50). "One result
  needs a name" explains nothing.

The eight suggestions are:

- `RDS-1` `research/iron-proxy-plane.md:1` (line 57). The title "The v0.56.0
  binary in the plane workshop" does not name the product.
- `RDS-2` `research/iron-proxy-plane.md:111` (line 58). "audit records" should
  be "per-request records" to match the rest of the file.
- `RDS-3` `research/iron-proxy-plane.md:135` (line 59). "the container that
  was running on the day" gives no date.
- `RDS-4` `research/acl-fence.md:19` (line 60). The apply script and verify
  probe are never introduced.
- `RDS-5` `research/acl-fence.md:7` (line 61). "Workshop" and "workshop" are
  not used with one capitalization.
- `RDS-6` `research/separate-bridges.md:14` (line 62). "A rule that names no
  source address is enough" does not say what the rule is enough for.
- `RDS-7` `research/two-bridge-gateway.md:53` (line 63). "The sandbox work
  works under the fence" repeats the word "work".
- `RDS-8` `research/two-workshop.md:153` (line 64). A historical item should
  point to `research/separate-bridges.md`, which later measured that approach.

The shape of one substantive finding, from the `review-json` block (line 77):

```json
{"id":"RDB-1","file":"research/iron-proxy-plane.md","line":32,
"category":"readability","severity":"high","confidence":"high",
"title":"Verdict states refusal without the warn:true condition",
"rationale":"...","suggested_fix":"...","out_of_scope":false}
```

Fields: `id`, `file`, `line`, `category` (always "readability"),
`severity` (critical, high, medium, or low), `confidence` (high, medium, or
low), `title`, `rationale`, `suggested_fix`, and `out_of_scope` (boolean).

The shape of one editorial suggestion, from the `review-readability-json`
block (line 85, clipped):

```json
{"file":"research/iron-proxy-plane.md","items":[
  {"id":"RDS-1","line":1,"original":"The v0.56.0 binary in the plane workshop",
   "problem":"The title does not name the product.",
   "suggested_edit":"The iron-proxy v0.56.0 binary in the plane workshop"}]}
```

Fields: `id` (`RDS-<n>`), `line`, `original`, `problem`, `suggested_edit`,
grouped by `file`.

The report ended with `finish: stop`. The session outcome is "succeeded". No
file was edited. The tool log shows eight `read` calls and one `skill` call,
all completed (lines 87-94). No write or edit ran.

One gap: the directive names `.kb/writing-style.md` as guidance, but the tool
log does not show a read of that file. The agent instead read
`~/.config/opencode/prompt/readability-criteria.md` (line 89). The report's
own prose follows the readability feedback policy, not the repository style.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

- The five review targets, USER 1 (line 4): `research/acl-fence.md`,
  `research/iron-proxy-plane.md`, `research/separate-bridges.md`,
  `research/two-bridge-gateway.md`, `research/two-workshop.md`.
- The finding cap, USER 1 (line 4): "up to 12 actionable readability findings".
- The finding shape, USER 1 (line 4): "(path:line, quote, what reader
  misreads, concrete revision)".
- The editorial channel, USER 1 (line 4): "separate optional small editorials".
- The cross-file check, USER 1 (line 4): "cross-file overlap where reports
  repeat without clarifying distinct result".
- The historical-preservation rule, USER 1 (line 4): "Preserve historical
  observations and avoid guessing current status."
- The read-only rule, USER 1 (line 4): "Do not edit files."

Most of these are the review council's normal contract. The finding cap of 12,
the historical-preservation rule, and the cross-file overlap check are
specific to this invocation. They are not in the monitor-agent repository.

## Failures, their cause, and the fix

(none found)

## Candidate lessons

- L1. A readability review returns two channels: `review-json` for substantive
  findings and `review-readability-json` for editorial suggestions. Each
  finding carries `id`, `file`, `line`, `category`, `severity`, `confidence`,
  `title`, `rationale`, `suggested_fix`, `out_of_scope`. Each suggestion
  carries `id`, `line`, `original`, `problem`, `suggested_edit`, grouped by
  file. Source: the `review-json` block (line 75) and the
  `review-readability-json` block (line 85). Mark: ALREADY WRITTEN, in
  `~/.config/opencode/agent/review-readability.md` and
  `~/.config/opencode/command/review-council.md`. Not in the monitor-agent
  repository.
- L2. When a later research record repeats the same Gotchas or "Not verified"
  items as an earlier spike, name what the later spike added instead of
  repeating the text. Source: "in each later file, mark the items that were
  already found in an earlier spike, for example 'Same as `two-workshop.md`'.
  Then keep only the result that is new. Do not delete the historical
  observations." (line 73). Mark: NEW. `.kb/spikes.md` states the README
  structure but does not state the cross-file deduplication rule.
- L3. A review of a research record treats the record as a historical
  snapshot and does not guess its current status. Source: "Preserve historical
  observations and avoid guessing current status." USER 1 (line 4). Mark: NEW.
  Adjacent to `.opencode/skills/review-a-change/SKILL.md`, which says to "name
  the date of every source the review reads".
- L4. The nine findings and eight suggestions are concrete edits to specific
  research files, for example the three meanings of "gateway" in
  `research/separate-bridges.md` (line 40) and the `warn: true` condition in
  `research/iron-proxy-plane.md` (line 10). Mark: PROJECT-SPECIFIC FACT.
  These belong in the research records, not in a skill.

## What should not become a skill

- The individual `RDB-` and `RDS-` entries. Each is a one-off correction to a
  named file and line. The digest lists them for the record. A skill that
  restated them would not help the next session.
- The two-channel output shape from L1. It is the review council's global
  contract in the dotfiles. Restating it in the monitor-agent repository would
  duplicate a contract that already has one source and would drift from it.
