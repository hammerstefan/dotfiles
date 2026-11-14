# ses_e2571af5bffeMWFmj71Q1iKsdE: Rename monitor-agent dev daemon

## What the person asked for

USER 1 (line 3):

- "change "monitor-agent-verb-daemon" to "monitor-agent-dev-daemon" to indicate this will only be used by the dev process and workshop" (line 3)
- "critique" (line 4)

## What was produced, and whether it worked

The agent produced a critique and made no change. It read the code and the
records first, then recommended keeping `-verb-daemon`. No commit, branch,
pull request, or record was produced. Nothing was verified. The agent ended
by offering to make the change with a migration note and to run the
retired-name check:

- "If you still want it, say so and I will make the change with the migration note and `scripts/check-retired-names.py monitor-agent-verb-daemon` run over the working tree." (line 44)

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

(none found)

The person stated one value, the rename's justification, and it is quoted in
the first section. The person stated no command, flag, path, ticket key, or
naming rule.

## Failures, their cause, and the fix

(none found)

## Candidate lessons

- ALREADY WRITTEN. Name the service for what it does. The quote: "Name the service for what it does, as `monitor-agent-verb-daemon` names the verb set." (line 16). It restates `.opencode/skills/workshop-host-authority/SKILL.md` line 101.
- ALREADY WRITTEN. `-dev` is a word the glossary avoids for the development workshop. The quote: "`GLOSSARY.md:25-27` fixes "Development workshop" and lists "dev container" as a word to avoid." (line 20). It restates `GLOSSARY.md`.
- NEW. A rename of a running control-service unit strands host state, and the fix is ordered. The quotes: "`~/.config/systemd/user/monitor-agent-verb-daemon.service` stays linked, and if it was active the old daemon keeps running as the operator on the old socket." (line 32), and "Both are fixable, but only if you do it in order: `just dev down` on the old commit first, then `up` on the new one, and say so in the change." (line 36). The `retire-a-name` skill sweeps the tree, branches, and tracker, but states no host runtime state and no down-then-up order.
- PROJECT-SPECIFIC FACT. The `-dev` name inverts the risk. The quote: "wrong in the dangerous direction: this service runs as the operator with the operator's full reach" (line 21). The control service is the highest-authority path in the repository, and `-dev` makes it read like tooling.
- ALREADY WRITTEN. A decided name is copied into an ADR, so a rename changes a decided literal. The quote: "You are editing a decided literal in an accepted record, not prose." (line 28). `retire-a-name` states the ADR copy, and `adr/README.md` states the deprecation path.

## What should not become a skill

- The alternative name `monitor-agent-dev-control-daemon` (line 40). It is a one-off name suggestion for one service, not a rule.
- The question that gates the rename: "is a non-development control service actually planned? If the answer is "not yet", the distinction is premature" (line 42). It is a reasoning step about one request, not a repository convention.
- The premise check that the caller, not the daemon, is development-only (line 14). It is a critique of one request's justification, not a rule.
