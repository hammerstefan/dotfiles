# ses_e340ed5deffemDfYui2pY4R3NE: Create private monitor-agent origin repo

Positions are line numbers in `flat/ses_e340ed5deffemDfYui2pY4R3NE.txt`, with the
USER timestamp where there is one. An "answer" is text the person typed into a
question tool result. The tool log holds no `!! FAILED` entry.

## What the person asked for

- "create private hammestefan/monitor-agent gh repo as this repo's origin"
  (L3, 1794422962456)
- "push all the branches" (L22, 1794423067936)
- "@setup-matt-pocock-skills" (L40, 1794423103224)
- "yes" (L239, 1794423977499), to "Want me to commit and push them (something
  like `docs: add the issue tracker and domain doc conventions to the knowledge
  base`)?"

Answers typed into the question tool, in the person's own words:

- "hammerstefan (Recommended)", after the agent reported that `hammestefan`
  does not exist (question tool call at L249).
- "GitHub Issues (Recommended)" (question tool call at L264).
- "reconcile these instructions with the extant agent/kb instructions" (question
  tool call at L265), which the agent offered as "Write as drafted
  (Recommended)" or "Edit first".
- "Write as drafted (Recommended)" (question tool call at L276), for the
  reconciled drafts.

## What was produced, and whether it worked

- A private GitHub repository `hammerstefan/monitor-agent`, created with
  `gh repo create hammerstefan/monitor-agent --private --source . --remote origin`
  (tool log). Visibility was read back with
  `gh repo view hammerstefan/monitor-agent --json name,owner,visibility` and the
  agent reported "private" (L17).
- The remote was set to `git@github.com:hammerstefan/monitor-agent.git` (L18).
  The agent says it matches the GitHub CLI protocol setting (L18). The host
  setting itself was not inspected in this session.
- Seven branches pushed with `git push origin --all --set-upstream` (tool log):
  `main`, `spike/acl-fence`, `spike/openshell-in-workshop`,
  `spike/separate-bridges`, `spike/two-bridge-gateway`, `spike/two-workshop`, and
  `spike-openshell-gateway`. Tags were not pushed (L38).
- Commit `a8839c7`, "docs: add the issue tracker and domain doc conventions",
  3 files and 162 insertions, pushed to `origin/main` (L243). `a8839c7` resolves
  in the main checkout, and `.kb/issue-tracker.md`, `.kb/domain-docs.md` and the
  `## Agent skills` block in `AGENTS.md` are present with the content described.

Verified: the commit, the two `.kb` documents, the `AGENTS.md` index entries and
the `## Agent skills` section. Also checked in the session: the style scan over
the three changed files and the count of index entries against the count of
`.kb/*.md` files (tool log).

Not verified: whether the push reached the remote. The session ran `git push
origin main` and the agent reported "`e335806..a8839c7`" (L244), and nothing in
this digest confirms the remote state today. Whether the installed skills read
the config as the agent claims is also unverified beyond the agent's grep.

## Corrections the person made

1. The agent proposed a full draft with `docs/agents/issue-tracker.md` and
   `docs/agents/domain.md` and asked "Write these three pieces now?". The person
   answered "reconcile these instructions with the extant agent/kb instructions"
   (question tool call at L265). The agent then wrote "Good call [...] reconciling
   properly means reading the extant conventions first, then checking how the
   installed skills actually consume this config before I fix paths and
   cross-references" (L122), and rewrote both documents into `.kb/`.
2. The agent took the repository owner from the request. The person confirmed
   "hammerstefan (Recommended)" after the agent reported "`hammestefan` doesn't
   exist on GitHub" and asked "This looks like a typo, but I don't want to
   assume" (L9, L10).

## Conventions, commands and values stated and written down nowhere

- `gh api users/hammestefan --jq '{login: .login, type: .type}'`, used to prove
  the owner does not exist before creating anything (tool log). No file states
  this check.
- `gh repo create <owner>/<repo> --private --source . --remote origin` (tool
  log). No file states it.
- `git push origin --all --set-upstream` (tool log). The reason it matters is in
  `.kb/spikes.md` §7, "The branch is kept", so the remote must receive the spike
  branches and not only `main`. No file states the push command.
- The installed skills do not hardcode `docs/agents/` (agent's finding, L124).
  They read the config that `AGENTS.md` provides. The agent's quote: "The
  installed skills don't reference `docs/agents/` at all" (L124).
- Triage labels are omitted because the `triage` skill is not installed (L57).
- The person's account name is `hammerstefan`. `.kb/issue-tracker.md` §1 states
  `hammerstefan/monitor-agent`, so the value is recorded.
- The agent's stated reason to move the config out of `docs/agents/`: "No
  `docs/agents/` directory. The kb is this repo's documented home for
  agent-oriented knowledge" (L134). The `.kb/` location is recorded in
  `AGENTS.md` and `.kb/domain-docs.md` §2. The rule that a skill's own default
  path yields to the knowledge base is not stated as a law.

## Failures, their cause, and the fix

1. The first draft wrote two documents to `docs/agents/` and appended a block
   that pointed there. Cause: the agent applied the skill's seed template
   before reading the repository's own conventions and before checking how the
   installed skills find the config. Fix: the person's answer at L265 started a
   reconciliation, the agent read `.kb/agents.md`, `.kb/project.md`,
   `adr/README.md`, `.kb/writing-style.md`, `.kb/requirements-format.md` and
   `.kb/spec-kit.md`, grepped the installed skills for `docs/agents`, and wrote
   `.kb/issue-tracker.md` and `.kb/domain-docs.md` instead. The wrong-tree files
   were never created.
2. The owner in the request did not exist. `gh api users/hammestefan` returned
   nothing usable, so the agent stopped and asked instead of creating a
   repository under a guessed owner (tool log, L9). Nothing failed.
3. The blank-line check reported a defect that was not one. The agent's account:
   "the one awk report was a cross-file artifact of my scan script (the
   `# Preface` of `domain-docs.md` read against the last line of the previous
   file), not a formatting defect" (L225). Cause: the `awk` script kept the
   previous line across file boundaries instead of resetting on `FNR == 1`. Fix:
   the report was read as a script fault and the files were left unchanged. The
   same class of false positive cost a second look in the sibling session
   `ses_e3a65724dffelibnb7cU48K6gm`.

## Candidate lessons

1. NEW. Verify that the owner in a repository request exists before creating
   anything, and ask when it does not match the authenticated account. Quote:
   "The account `hammestefan` doesn't exist on GitHub. Which owner should the
   private `monitor-agent` repo be created under?" (L249, agent) and the person's
   answer "hammerstefan (Recommended)".
2. NEW. Read an installed skill's consumption of its config before choosing
   where to write that config. Quote: "The installed skills don't reference
   `docs/agents/` at all" (L124), and the person's correction "reconcile these
   instructions with the extant agent/kb instructions" (L265).
3. NEW. Push every branch when spike branches are kept. Quote: "push all the
   branches" (L22). `.kb/spikes.md` §7 says the branch is kept, and no file says
   the remote must hold it.
4. NEW. Reset accumulator state at `FNR == 1` when one check script reads
   several files. Quote: "the one awk report was a cross-file artifact of my scan
   script" (L225).
5. ALREADY WRITTEN. The owner is `hammerstefan/monitor-agent`, and the `gh` CLI
   runs every issue operation from inside a clone. `.kb/issue-tracker.md` §1.
6. ALREADY WRITTEN. Decision records go under `adr/`, and `docs/adr/` is never
   created. `.kb/domain-docs.md` §2. This is what overrode the skill's default.
7. ALREADY WRITTEN. An issue is intake and never a requirement, and accepted
   work is committed as `requirements/NNN-slug/requirements.md` in a pull request
   stack. `.kb/issue-tracker.md` §2.
8. ALREADY WRITTEN. `AGENTS.md` starts with the ordered list of every
   `.kb/*.md` file, and the `## Agent skills` block follows it. `.kb/agents.md`
   §4 and the file itself.
9. PROJECT-SPECIFIC FACT. The `triage` skill is not installed, so no label
   section exists in `AGENTS.md`. A later installation changes the answer.
10. PROJECT-SPECIFIC FACT. The repository was created private under
    `hammerstefan`, and tags were not pushed. Neither belongs in a skill.

## What should not become a skill

- The `hammestefan` misspelling itself. The rule worth keeping is candidate 1.
  The typo is one event.
- The full text of the two `.kb` documents. They are in the repository, and
  repeating them in a skill would give two copies that drift.
- The `gh repo create` flag set. It already ran here, and the flags are in the
  `gh` help text that a later run reads.
- The instruction to add a `## Agent skills` block. That block came from the
  `setup-matt-pocock-skills` skill, which the person already holds outside the
  repository.
- The remark that `/to-tickets`, `/to-spec`, `/wayfinder` and the other skills
  "will now pick up the tracker from AGENTS.md" (L235). It is an untested claim
  about other skills, and the sibling lessons do not depend on it.
