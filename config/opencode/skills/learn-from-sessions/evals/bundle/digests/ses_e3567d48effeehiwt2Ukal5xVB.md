# ses_e3567d48effeehiwt2Ukal5xVB: LXD network ACLs for hermes egress

## What the person asked for

- "in github.com/canonical/cpc-actions/pull/10 they discuss an option to use LXD network acls to control workshop egress. evaluate and consider this path for our project to separate hermes from the general network and route hermes to one or more proxies (possibly the openshell proxy as a default)" (USER msg 1, flat line 3)

No other user message follows. The transcript ends in the middle of the agent's work: the last assistant line is "Found a likely candidate: `canonical/workshop#927` ... Let me read it and check for the linked PR." (line 7), and the tool log ends with the issue and comment fetches (tool lines 33 to 35).

## What was produced, and whether it worked

- No evaluation, no verdict, no document and no file. The session produced no answer to the request.
- What it did establish, in the agent's words: the named pull request is not the discussion. "The PR you pointed me at (`canonical/cpc-actions#10`) is your own commit-checker fix" and "its thread has no comments and nothing about LXD ACLs" (line 5).
- The replacement thread it found: "Found a likely candidate: `canonical/workshop#927`" with the title "declarative per-workshop network policy / egress control" (line 7).
- Verified by tool output: the pull request was read through `gh pr view`, `gh api repos/canonical/cpc-actions/pulls/10`, the issue comments and the review comments, and then the org-wide searches (tool log lines 9, 12, 15 to 32).
- No file was changed and no commit was made.
- The person asked the same question again in a new session, ses_e35651f4cffe6xJc5a1FCZtryq, with the corrected URL `https://github.com/canonical/workshop/issues/927`. That session produced the evaluation this one did not.

## Corrections the person made

- (none found)

## Conventions, commands and values stated and written down nowhere

- The person's exact pointer and its missing scheme: "in github.com/canonical/cpc-actions/pull/10" (line 3). The agent resolved it as `canonical/cpc-actions` pull request 10.
- The person's goal statement for this path, reused word for word in the next session: "separate hermes from the general network and route hermes to one or more proxies (possibly the openshell proxy as a default)" (line 3). No repository file in the main checkout states this framing of the requirement.
- The person stated no command, flag or ticket key. The `gh search` forms in the tool log are the agent's.

## Failures, their cause, and the fix

- The pointer was wrong. What ran: `gh pr view 10 --repo canonical/cpc-actions --comments`. Result: no discussion of LXD ACLs. Cause: the pull request is the person's own commit-checker change, and the discussion is in another repository.
- The fix the agent chose was an org-wide search, in this order: `gh search prs --owner canonical "network acl egress"`, then "workshop egress", then `gh search issues --owner canonical "egress proxy workshop"`, then "openshell proxy", then a repository list filtered on workshop, hermes, openshell and cpc (tool log lines 18 to 22). One of those searches surfaced `canonical/workshop#927`.
- No tool call failed. No `!! FAILED` line exists in the tool log.
- The session itself stopped before it answered. The cause is not recorded in the transcript. The person restarted the request in another session.

## Candidate lessons

- A pointer from the person can name the wrong repository or the wrong thread. Quote: "its thread has no comments and nothing about LXD ACLs" (line 5), followed by "Let me find the discussion you mean." NEW. No file in the repository tells an agent how to recover from a wrong pointer.
- Recover from a wrong pointer with an org-wide search rather than with more reads of the named object. The commands that found the thread are `gh search prs --owner canonical "network acl egress"` and `gh search issues --owner canonical "egress proxy workshop"` (tool log lines 18 and 20). NEW, and it is the method behind the previous line.
- A session that cannot finish the request says so before it stops. This session stopped after finding the thread, and the person repeated the whole request in ses_e35651f4. NEW, with the caveat that the transcript records no cause for the stop.
- `canonical/workshop#927` is the thread that asks for declarative per-workshop egress control. ALREADY WRITTEN (`adr/0001`, Context: "Workshop plans egress control in the workshop definition" and "It has not shipped that control.").

## What should not become a skill

- The full sequence of `gh search` calls. It is one recovery, and the repository's issue workflow is already stated in `.kb/issue-tracker.md`.
- "Read the linked pull request before searching." The agent did read it, and the read is what proved the pointer wrong.
- Any LXD or OpenShell fact. This session measured nothing.
