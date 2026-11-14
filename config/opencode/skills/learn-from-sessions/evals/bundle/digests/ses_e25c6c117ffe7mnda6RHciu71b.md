# ses_e25c6c117ffe7mnda6RHciu71b: Review ADR and requirements

## What the person asked for

USER 1 (line 3): "You are a subagent spawned by another session."

USER 1 (line 4): "Read-only readability review of group DECISIONS AND REQUIREMENTS in repo /home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/review-writing."

USER 1 (line 4): "Review EVERY tracked adr/*.md (README and nine numbered records: 0001,0002,0004,0005,0006,0007,0008,0009,0010) and requirements/002-proxy-egress-fence/requirements.md."

USER 1 (line 4): "Read .kb/writing-style.md and adr/README.md for conventions; ADRs and requirements target ASD-STE100 so flag unclear phrasing without altering accepted decisions."

USER 1 (line 4): "Return exact files examined, up to 12 actionable nonduplicated issues (path:line, quote, reader impact, concrete revision), and separate minor editorial suggestions."

USER 1 (line 4): "Check cross-document terminology and link clarity. Do not edit files."

## What was produced, and whether it worked

The reviewer read 11 files and returned 12 substantive findings (RDB-1 through RDB-12) and 12 editorial suggestions (RDS-1 through RDS-12). It edited no file. No commit, branch, or pull request resulted. The session held one USER turn and one reply.

Files examined (ASSISTANT, lines 9-19): adr/README.md, the nine records 0001, 0002, 0004, 0005, 0006, 0007, 0008, 0009, 0010, and requirements/002-proxy-egress-fence/requirements.md. The reviewer also read .kb/writing-style.md (line 21).

The reply met the caller's shape. It named exact files, gave 12 issues, and kept editorial suggestions in a separate list. The findings are the reviewer's claims. This digest does not re-check them against the current files.

The 12 substantive findings, with the review-json file, line, severity, and confidence (lines 27-90, and the review-json block at line 154):

- RDB-1: a link names the wrong destination. adr/README.md:39, medium, high (line 27).
- RDB-2: the 0001 record says ADR 0008 removes a fence rule that the record never gives. adr/0001-hermes-runs-in-a-fenced-agent-workshop-and-a-plane-workshop-proxy-mediates-its-web-egress.md:76, medium, high (line 33).
- RDB-3: the 0005 record has the same removes contradiction. adr/0005-the-agent-workshop-installs-hermes-through-a-project-sdk.md:137, medium, high (line 38).
- RDB-4: the reasons in the 0002 record do not match ADR 0008. adr/0002-dns-in-the-agent-workshop-stays-unfenced.md:28, medium, medium (line 43).
- RDB-5: the records disagree about whether the setup steps run at restore. adr/0006-the-plane-workshop-installs-the-proxy-from-a-pinned-release.md:33, medium, medium (line 48).
- RDB-6: the count of env_passthrough names does not agree. adr/0007-the-agent-workshop-sets-the-proxy-variables-in-both-letter-cases.md:43, medium, high (line 54).
- RDB-7: two phrases in one sentence contradict each other. adr/0005-the-agent-workshop-installs-hermes-through-a-project-sdk.md:215, medium, medium (line 59).
- RDB-8: FR-028 can include a stash instance. requirements/002-proxy-egress-fence/requirements.md:49, medium, medium (line 65).
- RDB-9: the phases in the 0010 record are not defined. adr/0010-the-control-service-bounds-the-request-surface-and-runs-agent-code-as-the-operator.md:21, medium, high (line 71).
- RDB-10: replaces its own earlier decision conflicts with the README rules. adr/0001-hermes-runs-in-a-fenced-agent-workshop-and-a-plane-workshop-proxy-mediates-its-web-egress.md:20, medium, medium (line 76).
- RDB-11: the README index has no 0003 and does not say why. adr/README.md:11, low, medium (line 81).
- RDB-12: the 0008 record announces two measurements and then gives four. adr/0008-the-model-call-reaches-the-llm-endpoint-through-the-plane-proxy.md:22, low, high (line 86).

The 12 editorial suggestions (RDS-1 through RDS-12) are at lines 94-152. Each has a file and line, an original excerpt, a problem, and a concrete edit. Examples:

- RDS-4: one object is called tunnel listener, CONNECT listener port, listener port, and proxy port. The 0006 file line 20 and the 0007 file line 38 (line 109).
- RDS-5: the requirements file says Committed proxy configuration file where the records say the committed proxy policy file (line 114).
- RDS-12: the fence ticket does not identify a ticket. The 0006 file line 135 (line 149).

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

(none found)

The caller stated the review scope, the file set, and the cap of 12 issues. Those are invocation parameters, not repository conventions. The two stated conventions are already written down. The ASD-STE100 target is in adr/README.md and .kb/requirements-format.md §6. The issue shape of path, line, quote, reader impact, and concrete revision is in ~/.config/opencode/agent/review-readability.md.

## Failures, their cause, and the fix

(none found)

The tool log (lines 158-173) holds 16 reads and one skill call, all successful. No FAILED entry.

## Candidate lessons

- A readability finding carries these fields: id, file, line, category, severity, confidence, title, rationale, suggested_fix, out_of_scope. Quote (line 156): `{"id":"RDB-1","file":"adr/README.md","line":39,"category":"readability","severity":"medium","confidence":"high"`. The flat file clips the rest at line 156. ALREADY WRITTEN. ~/.config/opencode/agent/review-readability.md.
- Editorial suggestions are a separate channel with ids RDS-1 and up, and each carries an original excerpt, a problem, and a concrete edit. Quote (line 94): "1. **RDS-1** — the 0009 file, lines 33–37." ALREADY WRITTEN. ~/.config/opencode/command/review-council.md.
- A decision record that cites a later record removing a rule must first state that rule. Quote (line 35): "The Decision lists only two allow rules: the proxy and the resolver. It then says that ADR 0008 "removes the rule for the LLM endpoint"." ALREADY WRITTEN. adr/README.md (a record cannot be misread) and .kb/writing-style.md §4.
- PROJECT-SPECIFIC FACT. The review found documents that contradict each other or themselves. Quote (line 6): "In several places one document contradicts another, or contradicts itself." The specific defects belong in a ticket or pull request, not a skill.

## What should not become a skill

- The 12 findings and 12 suggestions are one-time defects in specific documents. They belong in a pull request that fixes adr/*.md and requirements/002-proxy-egress-fence/requirements.md. A skill cannot carry them.
- The review-json and suggestion shapes are the review child's existing contract. They are written in ~/.config/opencode/agent/review-readability.md and ~/.config/opencode/command/review-council.md. A new skill would repeat them.
