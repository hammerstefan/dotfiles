# ses_e2f1ce8d1ffew0PyV7RXBPvBUT: PR 29 branch cleanup

## What the person asked for

- Message 1 (flat line 3): "pr29 merged, anything else to do on this branch?"
- Message 2 (flat line 23): "create a pr for the ADR 0001 correction"
- Message 3 (flat line 61): "@review-glm pr 31"

## What was produced, and whether it worked

- An answer to the status question in three parts: branch state, housekeeping, and follow-ups that are not this branch. It states "wayfinder/agent-workshop-build has zero commits that `origin/main` doesn't have" and "PR #29 merged as `9c9596b`".
- A named follow-up defect that the merged branch left: "`adr/0001…md:121` still says 'Every command runs as root in the persistent agent workshop container'. That contradicts ADR 0005 (hermes runs as the workshop user, which holds passwordless sudo)".
- A new worktree `adr-0001-workshop-user`, created with `worktree_create`, and the session moved into it with `session_move`.
- Branch `docs/adr-0001-workshop-user` with one commit, `e62db42`, pushed, and PR #31, titled "Correct the root claim in the agent record". It is merged today as `a283084`.
- Two edits to ADR 0001: the Context sentence on the workshop user and sudo, and the Consequences sentence on per-command isolation. The passive "is removable by the agent" became active.
- Verified: `ste-lint` on ADR 0001 gives "0 hard violations". The agent adds "the 6 advisory findings are the same lines the file had before".
- Verified on the running workshop: "Passwordless sudo confirmed on this host, in the running `agent` workshop: `id -un` → `workshop`, `sudo -n id -un` → `root`."
- Verified: `grep 'runs as root' adr/` leaves only true statements, plus ADR 0006's Context sentence that PR #30 corrects.
- A review through the `review-glm` agent on `zai-coding-plan/glm-5.3-flash`, verdict "approve with nits", and both nits applied. The PR is merged.

## Corrections the person made

- The agent ended its first answer with an offer: "Want me to merge #30 and open the ADR 0001 correction as its own change?" The person answered by naming the change: "create a pr for the ADR 0001 correction" (message 2, flat line 23). The person asked for the pull request, and did not answer the offer to merge #30.
- The person names the reviewer agent in the request: "@review-glm pr 31" (message 3, flat line 61). No correction of content follows.

## Conventions, commands and values stated and written down nowhere

- The person asks for a review by naming an agent: "@review-glm". Earlier sessions in this batch use "@review-deepseek". The agent name is the request.
- A follow-up change gets its own worktree and the session moves there: "Work is in a new herdr worktree (`adr-0001-workshop-user`), and this session moved there." (assistant, flat line 59)
- The two records that carry the same claim are corrected in two pull requests: "The two PRs touch different files, so merge order doesn't matter." (assistant, flat line 55)
- The reviewer substitution, said plainly to the person: "Note first: the `review-glm` agent is configured with `zai-coding-plan/glm-5.1`, which that provider no longer serves. I ran the same reviewer agent on `zai-coding-plan/glm-5.3-flash` instead." (assistant, flat line 79)
- The claim the change deliberately left alone, and the reason: "ADR 0001's two 'root agent' phrases still hold, because the workshop user reaches root through sudo." (assistant, flat line 57)

## Failures, their cause, and the fix

- `!! FAILED subagent` at flat line 140: `Subagent failed (sessionID: ses_e2f176fceffeeTR4CUSlvrn1yT): Model unavailable: zai-coding-plan/glm-5.1`. The cause is the `review-glm` agent's configured model, which the provider retired. The fix was a `opencode.models` search for `glm` (flat line 143), then the same agent with `"model": "zai-coding-plan/glm-5.3-flash"` (flat line 144), which ran.
- The failed spawn left a child session, `ses_e2f176fceffeeTR4CUSlvrn1yT`, with no reply. It is in this batch as its own session.
- One `trail_add` call carried a nonsense statement: `const pr = await tools.shell ? null : null;` (flat line 138). It did no harm and the trail entry was written.
- The person's first three messages each produced several empty `ASSISTANT` blocks in the flattened transcript. The tool work beneath them succeeded. The cause of the empty blocks is not stated.

## Candidate lessons

1. NEW. A named reviewer agent can pin a model the provider has retired. Run the same agent with an explicit `model`, and tell the person which model reviewed. Quote: "the `review-glm` agent is configured with `zai-coding-plan/glm-5.1`, which that provider no longer serves. I ran the same reviewer agent on `zai-coding-plan/glm-5.3-flash` instead." (assistant, flat line 79, after `!! FAILED subagent` at flat line 140)
2. NEW. An answer to "anything else to do on this branch" separates three things: the branch state, host housekeeping, and follow-ups that belong to another change. The person then picks one. Quote: "**Only housekeeping is left** (safe, optional)" and "**Follow-ups that are *not* this branch, but come straight out of it**" (assistant, flat lines 12 and 16).
3. NEW. A defect in a merged branch becomes a new branch, a new worktree, and a new pull request, and the session moves to the worktree. Quote: "Work is in a new herdr worktree (`adr-0001-workshop-user`), and this session moved there." (assistant, flat line 59)
4. NEW. A claim about what the workshop grants is checked inside the running workshop, with the command printed. Quote: "Passwordless sudo confirmed on this host, in the running `agent` workshop: `id -un` → `workshop`, `sudo -n id -un` → `root`." (assistant, flat line 54)
5. NEW. When two records carry the same wrong claim and two open pull requests correct them separately, say that the merge order does not matter and why. Quote: "The two PRs touch different files, so merge order doesn't matter." (assistant, flat line 55)
6. ALREADY WRITTEN. `ste-lint` as the first pass on a record, and the rule that a record's format and short links come from `adr/README.md` and `.kb/writing-style.md`.
7. ALREADY WRITTEN. The claim itself, that hermes runs as the workshop user with passwordless sudo. ADR 0005 states it, and `.kb/agent-workshop.md` states the run command.
8. PROJECT-SPECIFIC FACT. That ADR 0006 carries the same root claim and that PR #30 corrects it. It is a fact about two pull requests on one day.

## What should not become a skill

- The offer to merge PR #30. It is one decision the person left open.
- The `const pr = await tools.shell ? null : null;` line. It is a broken statement in one tool call, and a skill cannot prevent a stray line.
- The reviewer model name. It changes when the provider retires a model, so the lesson is the explicit `model` argument, not `glm-5.3-flash`.
