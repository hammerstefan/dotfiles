# ses_e321e9151ffeTbwYCErDGc6Jm7: Issue #22 agent workshop provisioning decision

## What the person asked for

- Message 1 (flat line 2), the hwt brief for ticket #22, "Decide the agent workshop provisioning and hermes configuration". Its Ask line: "@hwt for EACH ticket you identified".
- Message 2 (flat line 181), two lines in one message: "document those dpendencies on those tickets" and "rebase and merge this change to main".
- Message 3 (flat line 218): "@review-deepseek changes made by this branch"

## What was produced, and whether it worked

- `adr/0005-the-agent-workshop-installs-hermes-through-a-project-sdk.md` and one row in `adr/README.md`, committed as `d3a1166` and pushed.
- Fast-forward merged into local `main` in the main checkout, `5c7528a` to `d3a1166`, then pushed. The push also published the previously unpushed `5c7528a`.
- Issue #22 resolved with comment 6814249828 and closed. One line appended to the map's `## Decisions so far`.
- Three dependency comments on sibling tickets: #17 (comment 6824462192), #21 (comment 6824470232), and #20 (comment 6824470908). No GitHub blocked-by edges were added.
- After the review, eight findings fixed in `c6b0b8d`, fast-forward merged to `main` and pushed. `main` and the branch both sit at that commit on origin.
- ADR 0005 is on `main` today. Its record number is the one this session took.
- Verified by the agent, first hand: the hermes provider keys, `${VAR}` substitution, the command helper contract, the child-process environment filter, `terminal.env_passthrough`, the local backend's approval behavior, the toolset list, the installer script, the definition schema against the installed `workshop` 0.9.9 CLI, and the secret plug and slot shape.
- Not verified: the speed of `workshopctl get-secret` against the helper's default timeout, which entry points in a container read `/etc/environment`, and what a child process sees for `MONITOR_LLM_API_KEY`.
- The record on `main` states what the review changed. The agent's summary of the merge in prose is wrong: "The merge is done: `main` is at 5c7522... pushed through 5c7522 → 5c7522+commit" (flat line 191). The commit is `d3a1166`.

## Corrections the person made

- The agent's report ended with a "Dependencies on sibling tickets" section in prose and an offer: "Say the word and I will add the edges." The person then wrote "document those dpendencies on those tickets" (message 2, flat line 182). The dependencies went onto the tickets as comments.
- The agent reported the record as written on a branch with no pull request, and said "Nothing to proceed." The person then wrote "rebase and merge this change to main" (message 2, flat line 183), which overrides the brief's "Do not merge into `main`, do not rebase".
- The agent then reported "I used comments and did not add GitHub native blocked-by edges. Edges change the frontier query that the two parallel sessions run, and charting #24's full blocker set (the fence, the plane build, the port, the address) is a mapping call." The person did not answer this point.

## Conventions, commands and values stated and written down nowhere

- Record number reservation, from the brief: "Two other sessions work in parallel on this map, so if you write a record, take number `0005`. It is yours alone."
- The dependency note form the agent chose, with no repository rule behind it: one comment per blocker, each stating "what it must produce and which frontier item consumes it". The agent named the reason it avoided native edges: "Edges change the frontier query that the two parallel sessions run."
- The person's own phrase for the dependency work, with their spelling: "document those dpendencies on those tickets".
- The person grants the merge and the rebase per branch. This is the third session in this batch where the brief forbids both and the person asks for both.
- The upstream fact that decided the helper: the agent confirmed `secrets.command` "verbatim in the upstream example config", and `agent.disabled_toolsets` "verbatim in the live configuration page's 'Global Toolset Disable' section".

## Failures, their cause, and the fix

- `!! FAILED edit` at flat line 315 and again at flat line 318: `Could not find oldString in adr/0005-...md. It must match exactly, including whitespace and indentation.` The agent's `oldString` used a line wrap that the file did not have. The tool's error names the closest lines, 11 and 12. The fix was to read lines 1 to 16 and reissue with the exact wrap, which succeeded at flat line 321.
- `!! FAILED hindsight_reflect` at flat line 337: `tool.input-incomplete ... The output token limit (stop reason: length) was reached before you could complete the arguments.` The input excerpt is 660916 characters of repeated text, and it repeats one idea over and over: "The dependency list names the blockers". The cause is a composed query that ran away. The agent dropped the call: "That reflect call was unnecessary and returned nothing useful. The dependency convention is already in `.kb/issue-tracker.md`, which I read earlier." (flat line 195)
- The review child said the record was "not ready to stand as written" on one blocker and two unverified-key findings. The agent checked the two keys against live pages and rejected both. Its account: "So the reviewer's two 'unverified key' findings are factually wrong on correctness, but right that the record cites no source of verification for them." (flat line 229)
- The agent's reason for the reviewer's error: "The reviewer only had the research record, which predates the key's documentation." (flat line 260)

## Candidate lessons

1. NEW. A dependency that the resolution comment states belongs in the record's Consequences as well. A reader of the record alone must see it. Quote: "The mechanism was already stated in the resolution comment and the #20 note. The ADR now carries it too, so a reader of the record alone sees it." (assistant, flat line 249)
2. NEW. A reviewer that has only an older research record reports a correct key as unverified. A review brief must name the date of each source it relies on, or the author rejects findings against a live page. Quote: "The reviewer only had the research record, which predates the key's documentation." (assistant, flat line 260)
3. NEW. An "unverified key" finding is answered with the live page and the exact YAML form, and the finding is then rejected rather than fixed. Quote: "`agent.disabled_toolsets` is confirmed verbatim in the live configuration page's 'Global Toolset Disable' section, and `secrets.command` in the upstream example config." (assistant, flat line 229)
4. NEW. A fast-forward merge into the main checkout followed by `git push origin main` publishes every unpushed commit that `main` already holds. Check `git log origin/main..main` before the push. Quote: "Pushed `main`. This published your previously unpushed reconciliation commit 5c7528a along with d3a1166." (assistant, flat line 215)
5. NEW. A long composed query to a reflection tool can exceed the output budget and return nothing. The knowledge base file that already holds the rule answers the question instead. Quote: "That reflect call was unnecessary and returned nothing useful." (assistant, flat line 195)
6. NEW. An edit to a wrapped paragraph needs the exact wrap, so read the region before choosing the `oldString`. This session failed twice on the same paragraph (flat lines 315 and 318).
7. ALREADY WRITTEN. The record numbering rule. `adr/README.md` states "one higher than the last record in the index or in any open pull request". The agent still wrote "0003 and 0004 are still free for them" (flat line 217) while the #19 branch held 0004. The rebase in that branch then hit the index conflict this session had called clean.
8. ALREADY WRITTEN. The eight disabled toolsets with a reason each, the two secret plugs, the operator acts, and the refresh and restore behavior. ADR 0005 and `.kb/agent-workshop.md` carry them.
9. PROJECT-SPECIFIC FACT. The choice of `local` for `terminal.backend`, `approvals.mode: off`, and `${MONITOR_LLM_*}` as the placeholder names. They are the decision, in ADR 0005.

## What should not become a skill

- The eight toolsets and the reason for each. They are a decision with upstream facts behind it, and ADR 0005 states them.
- The keyring item names and the `workshop connect` lines. `.kb/agent-workshop.md` holds them as operator instructions.
- The observation that a reviewer disagreed. It is a record of one review, and the two rejected findings do not outlive their upstream pages.
