# ses_e25c6c126ffeouNkivBC3BEYRs: Review project guidance prose

## What the person asked for

USER 1 (line 3): "You are a subagent spawned by another session."

USER 1 (line 4): "Read-only readability review of group PROJECT GUIDANCE in repo /home/stefan.hammer@canonical.com/.herdr/worktrees/monitor-agent/review-writing. Review EVERY listed file: AGENTS.md; GLOSSARY.md; .kb/agents.md; .kb/domain-docs.md; .kb/issue-tracker.md; .kb/project.md; .kb/requirements-format.md; .kb/spec-kit.md; .kb/spikes.md; .kb/topologies.md; .kb/writing-style.md. Apply .kb/writing-style.md where appropriate. Focus on wording, reader navigation, ambiguous referents, order, duplication, and clarity. Return (1) every file examined, (2) up to 12 high-value actionable findings with exact path:line, quoted phrase, reader cost, and concrete suggested revision, (3) separate minor editorial suggestions if worthwhile, (4) any cross-file duplication or contradiction, with specific lines. Distinguish genuine ambiguity from deliberate normative wording, and avoid speculative technical claims. Do not edit or create files."

## What was produced, and whether it worked

The agent read the 11 listed files in full and reported at line 8: "I read all 11 files in full". It applied `.kb/writing-style.md` and left normative words alone, at line 8: "Words in capitals, such as MUST and SHALL, are deliberate rules, and I did not report them as problems."

The review returned 12 substantive findings, 16 readability suggestions, and a cross-file duplication and contradiction list. Each finding carries an id, a file and line, a severity, a confidence, a quoted phrase, a reader cost, and a suggested revision.

Substantive findings:

- RDB-1, `.kb/spikes.md:49`, medium, high (line 12). Quoted: "is committed on `main` in the same commit as the record". "record" names two documents, so "the record" is ambiguous. Fix: name the findings record.
- RDB-2, `.kb/topologies.md:67`, medium, high (line 14). Quoted: "the content delivery network address that §4 names". §4 names no address. Fix: give the address in §4, or point to where it is written. "The author must give this fact."
- RDB-3, `.kb/project.md:20`, medium, high (line 16). Quoted: "Neither urgency nor a bug-fix framing makes it maintenance." No scoped text defines the maintenance exception. Fix: "Urgency or a bug-fix label does not remove the need for the record."
- RDB-4, `.kb/project.md:18`, medium, medium (line 18). Quoted: "in the same commit, or in a Spec Kit stack, in the base pull request". The second clause replaces the first for stacked work, but reads as a free choice. Fix: write the stacked case as its own sentence.
- RDB-5, `AGENTS.md:100` against `.kb/issue-tracker.md:104`, medium, high (line 20). Quoted: "the frontier is the open children without an assignee". The tracker also drops children with an open blocker. The two definitions disagree. Fix: "the open children without an open blocker or an assignee", or cite the tracker.
- RDB-6, `GLOSSARY.md:3` and other lines, medium, medium (line 22). Quoted: "Workshops" and "Workshop project" with a capital, "the workshop that runs hermes" in lower case. The glossary never defines the split. Fix: one entry for Workshop the tool and workshop one instance. Also choose one spelling for "Hermes Agent" and "hermes".
- RDB-7, `GLOSSARY.md:57`, medium, medium (line 24). Quoted: "The operator runs it with every workshop lifecycle command." "workshop lifecycle command" is undefined. Fix: list the commands, or add a glossary entry.
- RDB-8, `GLOSSARY.md:65` and `:80`, medium, medium (line 26). Quoted: "a fixed set of verbs" and "restricting its verbs". "Verb" is undefined. Fix: add a "Verb" entry, or link to where the set is listed.
- RDB-9, `GLOSSARY.md:75`, low, medium (line 28). Quoted: "It does not limit the reach behind a request that runs code the caller wrote." The exception it states is unclear. Fix: "A bound does not limit a request that runs code that the caller wrote."
- RDB-10, `.kb/writing-style.md:27`, low, medium (line 30). Quoted: "state a plan or an intention as one". "as one" means either "as a plan" or "in one sentence". Fix: "State a plan or an intention as a plan".
- RDB-11, `.kb/topologies.md:14`, low, medium (line 32). Quoted: "one `.kb` entry explains it". "entry" can mean a file, a section, or a line. Fix: "one section of a `.kb/*.md` file explains it."
- RDB-12, `.kb/issue-tracker.md:105`, low, medium (line 34). Quoted: "First in map order wins." "map order" is undefined. Fix: name the order, for example "the order of the map's sub-issue list".

Readability suggestions (lines 40 to 55), each a banned word from `.kb/writing-style.md` or a duplication:

- RDS-1, `.kb/spikes.md:19`. Quoted: "A spike lives on its own branch". "lives in" is banned. Write "Each spike has its own branch named `spike/<name>`."
- RDS-2, `.kb/spikes.md:47`. Quoted: "The conclusion lands on main". "lands" is banned. Write "is committed on main".
- RDS-3, `.kb/spikes.md:52`. Quoted: "The spike branch carries no `adr/` changes." "carries" is banned. Write "has no".
- RDS-4, `.kb/spikes.md:57`. Quoted: "the research branch itself does not merge". "itself" is banned. Drop it.
- RDS-5, `.kb/spec-kit.md:14`. Quoted: "land the regenerated output as its own commit". "land" is banned. Write "commit".
- RDS-6, `.kb/spec-kit.md:57` and `.kb/requirements-format.md:58`. Quoted: "Why requirements, not specs". The two files give the same rationale. Keep it in one file and cite it from the other.
- RDS-7, `.kb/spec-kit.md:63` and `.kb/requirements-format.md:96`. Quoted: "Delivering a feature". The move-and-`git add` steps appear in both. Keep the steps in `.kb/requirements-format.md` and cite them.
- RDS-8, `.kb/requirements-format.md:15` and `.kb/spec-kit.md:19`. Quoted: "it is moved to `requirements/NNN-slug/requirements.md`". §1 repeats §2 of the other. Keep the law in one file.
- RDS-9, `.kb/requirements-format.md:99`. Quoted: "rewrite the deposit". "deposit" is undefined. Define it once.
- RDS-10, `.kb/issue-tracker.md:46`. Quoted: "(`gh` 2.94+, and the host runs 2.104.0)". The host version appears three times. State it once at line 76.
- RDS-11, `.kb/project.md:34`. Quoted: "The repository holds the knowledge base, the architecture decision records". One sentence lists eight items. Use a bulleted list.
- RDS-12, `.kb/project.md:29`. Quoted: "monitor-agent is a personal monitoring system built on the Hermes Agent and run inside a Workshop." Lines 43 to 44 repeat it. Delete one.
- RDS-13, `AGENTS.md:116`. Quoted: "A handoff that forbids a push, on work that belongs on a pull request: commit." The rule is hidden in a tangled construction. Write "When a handoff forbids a push for work that belongs on a pull request, commit the work."
- RDS-14, `AGENTS.md:82`. Quoted: "`scripts/check-retired-names.py` reads the ref." The sentence does not say which ref or what it is read for.
- RDS-15, `.kb/domain-docs.md:49`. Quoted: "A definition document for a later ticket states the contract". This document kind has no storage location. State where it is stored.
- RDS-16, `GLOSSARY.md:43`. Quoted: "verify probes ... the plane proxy". "verify probes" is undefined and "plane proxy" is a second name for "Proxy". Write "the proxy".

Cross-file duplication and contradiction (lines 57 to 65):

- Contradiction: the frontier definition at `AGENTS.md:100` against `.kb/issue-tracker.md:104-105` (RDB-5).
- Duplication: `.kb/spec-kit.md:57-61` and `.kb/requirements-format.md:58-63` give the same rationale (RDS-6).
- Duplication: `.kb/spec-kit.md:63-70` and `.kb/requirements-format.md:96-105` give the same steps (RDS-7).
- Duplication: `.kb/spec-kit.md:19-22` and `.kb/requirements-format.md:15-18` state the same law (RDS-8).
- Duplication: the dead-link rule for `blob` URLs is at `AGENTS.md:116-120` and `.kb/issue-tracker.md:115-118`. Keep it in `.kb/issue-tracker.md` and cite it.
- Duplication: the research-branch pull request step is at `.kb/spikes.md:55-58` and `.kb/issue-tracker.md:119-122`. Acceptable, because `.kb/spikes.md` already names where the step is stated.
- Not a defect: `.kb/agents.md:13` tells the reader of `.kb/agents.md` to read `.kb/agents.md`. Law §2 requires this line.

The review ended with a `review-json` block (line 67) holding RDB-1 to RDB-12, and a `review-readability-json` block holding RDS-1 to RDS-16 with `readability_coverage` status complete and no limitations.

Nothing was committed, branched, or changed. The review was read-only. The findings are a candidate set. No chair verified them. Nothing ran a test, a check, or a command beyond reading files.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

(none found)

## Failures, their cause, and the fix

(none found)

## Candidate lessons

- ALREADY WRITTEN: a readability review splits substantive findings from editorial suggestions, with ids RDB-N and RDS-N. Quote at line 34 (RDB-12) and the two JSON blocks at line 67. Already in `agent/review-readability.md`.
- ALREADY WRITTEN: words in capitals such as MUST and SHALL are deliberate rules, not readability problems. Quote at line 8: "Words in capitals, such as MUST and SHALL, are deliberate rules, and I did not report them as problems." Already in the safeguards of `~/.config/opencode/prompt/readability-criteria.md`.
- ALREADY WRITTEN: when a fact is missing, the reviewer asks for it instead of inventing it. Quote at line 14: "The author must give this fact." Already in `agent/review-readability.md` and `readability-criteria.md`.
- PROJECT-SPECIFIC FACT: the 28 findings name specific files and lines in monitor-agent guidance. They belong in the review record, not a skill.

## What should not become a skill

- The 12 substantive findings and 16 suggestions are file-and-line-specific fixes for monitor-agent guidance. They are project facts, not a method.
- The review output shape, RDB-N findings and RDS-N suggestions with the two JSON blocks, is already written in `agent/review-readability.md`. A skill that restated it would repeat it.
