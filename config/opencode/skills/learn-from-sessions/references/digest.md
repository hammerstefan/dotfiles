You are reading session transcripts to turn them into knowledge. An export is
`{info, messages}`. In `messages[]`, `type` is `user`, `assistant` or
`synthetic`. A user message's words are `.text`. An assistant's words are in
`.content[]`, and its items are `text`, `reasoning` or `tool`. A tool call's
input is `.state.input`. Its failure is `.state.error`. A `synthetic` message is
harness injection, not the person.

Flatten an export with `jq`, or read it in slices. Never paste a whole
transcript into your own context. A finished session runs to megabytes, and the
digest exists so that the synthesis does not have to hold it.

```sh
jq -r '.messages[] | select(.type=="user") | .text' <export>
jq -r '.messages[] | select(.type=="assistant")
       | .content[]? | select(.type=="tool")
       | "\(.name): \(.state.input)"' <export>
jq -r '.messages[] | select(.type=="assistant")
       | .content[]? | select(.type=="text") | .text' <export>
```

# The digest

One digest per session, written to `<state>/digests/<id>.md`. It has this shape:

- what the person asked for, in their words.
- what it produced, and whether it worked.
- every correction the person made to the agent's behaviour, quoted.
- conventions, commands and values they stated that the repository does not
  record.
- failures, their cause, and the correction that ended them.
- candidate lessons, each with the message it came from.
- what here should *not* become a skill, and why.

Keep every detail that a skill could need. The digest is how the evidence
reaches the synthesis, so a detail dropped here is a detail the synthesis cannot
check.

A digest is a claim about a transcript. Quote it. Never paraphrase a transcript
into a fact. When a quote is ambiguous, the synthesis reads that part of the
export itself.

# One subagent per session

Run them in parallel and in the background. Give each subagent exactly one
export path, the path to write its digest, this file, and nothing else. A
subagent that receives several sessions writes a weaker digest of each.

When one session is the whole evidence, write one digest from it and say so in
the extraction report.
