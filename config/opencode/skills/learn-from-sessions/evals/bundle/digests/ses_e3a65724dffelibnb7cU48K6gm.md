# ses_e3a65724dffelibnb7cU48K6gm: New repo AGENTS setup following medic patterns

Positions are line numbers in `flat/ses_e3a65724dffelibnb7cU48K6gm.txt`, with the
USER timestamp where there is one. An "answer" is text the person typed into a
question tool result. The tool log holds no `!! FAILED` entry.

## What the person asked for

- "I want to set up a new repo for development. This will eventually be a custom,
  personal monitoring system based off hermes running inside workshop. Your job is
  to set up the AGENTS instructions in this repo following the patterns
  established by ~/git/medic. This includes requirements/spec/adr/kb setup and
  instructions. Ask me for anything that is unclear" (L3, 1794316618098)
- "is the repo .kb setup and instructions consistent with
  https://github.com/canonical/knowledge-base ?" (L90, 1794317377521)
- "instructions for writing ADR and requirements should mandate following
  asd-ste100 standard and suggest using the ast-ste100 skill. this should not be
  applied for documents written in the .kb directories" (L163, 1794403155594)
- "cherrypick the commit to main, and keep it on this branch for now. work in temp
  dirs, there is an active session running in the cwd branch" (L197, 1794403869672)
- "document a kb what the \"spike\" dir is and how agents are to use it /grill-me"
  (L203, 1794403928929)
- "yes, capture the research record" (L271, 1794407784983)

Answers typed into the question tool, in the person's own words:

- "Install specify CLI". This overrode the option marked "(Recommended)", "Copy
  from medic" (question tool call at L321).
- "adapt it, drop anything that does not immediately fit, including Test
  Observer/C3. We will add our terminology over time" (same question call, on
  `writing-style.md`).
- "Migrate to upstream (Recommended)" (question tool call at L353).
- "record findings with branch name, keep branch, do not merge to main. the
  findings record points to the branch that can be used to investigate further"
  (question tool call at L381).
- "Strict probe only (Recommended)", "research/ directory (Recommended)",
  "Mandate the sections (Recommended)", "lock + *.env rules (Recommended)",
  "ADR on main (Recommended)", "On request only (Recommended)", "Both branches
  (Recommended)" (question tool calls at L380 to L387).

## What was produced, and whether it worked

Seven commit objects came from this session: three made on `main`, two made on
`spike/acl-fence`, and a cherry-picked copy of each of those two on `main`
(`b2d4772` copies `69128eb`, `472cf45` copies `832b307`):

| Commit | Branch | Content |
|---|---|---|
| `5d74ac0` | main | first bootstrap, 37 files: `AGENTS.md`, `.kb/`, `adr/README.md`, `requirements/AGENTS.md`, `.gitignore`, Spec Kit 1.3.3 |
| `37238a0` | main | migration to the upstream `canonical/knowledge-base` convention, `.kb/agents.md` replaced byte for byte |
| `69128eb` | spike/acl-fence | ASD-STE100 mandate in `.kb/requirements-format.md` §6 and `adr/README.md` |
| `b2d4772` | main | cherry-picked copy of `69128eb` through a temporary worktree |
| `832b307` | spike/acl-fence | `.kb/spikes.md`, the `AGENTS.md` index entry, two `.gitignore` rules |
| `472cf45` | main | cherry-picked copy of `832b307` through a temporary worktree |
| `b0147cc` | main | `research/acl-fence.md`, 95 lines, one file |

Verified: every hash resolves in the main checkout, and `.kb/spikes.md`,
`.kb/requirements-format.md` §6, the `adr/README.md` ASD-STE100 bullet and
`research/acl-fence.md` are present with the content the session describes. The
`.gitignore` rules were checked with `git check-ignore` in the session, and
`.kb/spikes.md` §4 states them today.

Not verified: the worktree in `/tmp/opencode` was removed and cannot be checked.
The requirements checker and justfile recipes that medic has were never written,
so nothing enforces "only `requirements.md` is committed" except `.gitignore`.

## Corrections the person made

1. The agent reported the copy was done. The person then asked "is the repo .kb
   setup and instructions consistent with https://github.com/canonical/knowledge-base ?"
   (L90). The agent answered: "the answer is **no, not with the current version
   of that repo**" (L96), and replaced the work with a migration (`37238a0`).
2. The agent chose between copying medic's Spec Kit output and installing the
   tool. The person answered "Install specify CLI" (question tool call at L321)
   against the option the agent had marked "(Recommended)". The agent then
   found "Spec Kit has moved to 1.0 since medic pinned 0.5.1.dev0" (L23) and used
   1.3.3.
3. The agent offered "Copy verbatim" for medic's writing style. The person
   answered "adapt it, drop anything that does not immediately fit, including
   Test Observer/C3. We will add our terminology over time".
4. After the agent committed into the shared working tree, the person said
   "cherrypick the commit to main, and keep it on this branch for now. work in
   temp dirs, there is an active session running in the cwd branch" (L197). The
   agent then did "the cherry-pick through a temporary worktree in
   `/tmp/opencode`" (L199).
5. On the findings record, the agent asked "what happens to the branch and
   directory?" and offered "Record, then delete (Recommended)". The person
   answered with a different rule in their own words: "record findings with
   branch name, keep branch, do not merge to main" (question tool call at L381).

## Conventions, commands and values stated and written down nowhere

- "work in temp dirs, there is an active session running in the cwd branch"
  (L197). No file in the repository states this.
- "keep it on this branch for now" (L197). A document change may sit on the
  feature branch and `main` at the same time.
- The Spec Kit bootstrap commands appear in no repository file.
  `uv tool install specify-cli`, then
  `specify init --here --force --non-interactive --integration opencode`
  (tool log). `.kb/spec-kit.md` §1 says only "Change it by re-running Spec Kit".
- The findings record section list, taken from the record already on `main`:
  "exactly Question, Verdict, Findings, Gotchas, Not verified, Branch, Records,
  no \"What was run\"" (L283). `.kb/spikes.md` §3 and its Concepts name the parts,
  not that order under those headings.
- "Medic gitignores" `.workshop.lock`, and `.gitignore` takes it globally
  (L194, then `.kb/spikes.md` §4).
- The commit safety rule the agent applied and the person did not state: "No
  remote, so rewriting my own commit is completely safe" (L173).
- `git check-ignore -v` on a candidate path, plus a positive check that a
  template path is still trackable, before committing a new ignore rule
  (L237, and the command in the tool log at L391).

## Failures, their cause, and the fix

1. `git add -A` committed another session's files. Ran:
   `git add -A && git commit` (tool log). The agent's account, quoted: "My `git add -A`
   swept those unrelated files into my docs commit, and the commit landed on the
   spike branch rather than main" (L171). Cause: the index was never inspected,
   and a parallel session had created `spike/acl-fence` and three untracked
   files since the previous turn. Fix: `git reset --soft HEAD~1`,
   `git restore --staged` on the three foreign paths, then a commit of the two
   documents, which gave `69128eb` (tool log). Safe only because the repository
   had no remote at that moment.
2. The header-spacing check could not fail. The agent's account: "my
   header-spacing checker only looked at one line before each header, so it can
   never count 2 blanks" (L135). Cause: the check read one preceding line, so two
   empty lines and one were scored the same. Fix: the second script compared two
   preceding lines and ran against the upstream file as ground truth (L137, tool
   log).
3. A header inside a fenced code block was reported as a header. The agent's
   account: "line 46 of `.kb/agents.md` is the `# Knowledge Base` example inside
   upstream's own fenced code block, which the naive checker reads as a header"
   (L137). Fix: identified as a false positive and no file was changed.

## Candidate lessons

1. NEW. When the person says to follow another repository's conventions, check
   that repository's copy against the upstream source first. Quote: "is the repo
   .kb setup and instructions consistent with
   https://github.com/canonical/knowledge-base ?" (L90). `.kb/agents.md` states
   how to update itself from upstream, not that a repository copied from a
   sibling may be stale.
2. NEW. Stage explicit paths in a shared checkout, and check `git status` before
   the commit. Quote: "work in temp dirs, there is an active session running in
   the cwd branch" (L197), against the failure at L171.
3. NEW. Commit on a branch that another session is using from a temporary
   worktree, and let the shared checkout alone. Quote: the agent's plan, "[...]
   do the cherry-pick through a temporary worktree in `/tmp/opencode`, which
   shares the repo's object store" (L199). The quote is the agent's claim. The
   result (`472cf45`) is present, so the method held once.
4. NEW. Test a check script against a known good input and a known bad input
   before trusting a clean run. Quote: "my header-spacing checker only looked at
   one line before each header, so it can never count 2 blanks" (L135).
5. NEW. A check that reads lines must ignore headings inside fenced code blocks.
   Quote: "which the naive checker reads as a header" (L137).
6. NEW. Install the current tool rather than copying a sibling repository's
   pinned generated output. Quote: the answer "Install specify CLI", against the
   agent's "(Recommended)" option "Copy from medic", and the agent's finding
   "Spec Kit has moved to 1.0 since medic pinned 0.5.1.dev0" (L23).
7. NEW. Write a new `research/` record against the section list of the record
   already on `main`. Quote: "Precedent confirmed: exactly Question, Verdict,
   Findings, Gotchas, Not verified, Branch, Records" (L283).
8. ALREADY WRITTEN. ASD-STE100 governs records and requirements, and `.kb/`
   documents follow the writing style instead. `.kb/requirements-format.md` §6,
   `adr/README.md` Conventions. Quote: L163.
9. ALREADY WRITTEN. `.kb/agents.md` is replaced wholesale from upstream and is
   never edited by hand. `.kb/agents.md` §3 and "Version updates".
10. ALREADY WRITTEN. The spike laws: one question, own branch and directory,
    never merged, `research/` record, README sections, `.workshop.lock` and
    `spike/**/*.env` untracked, on request only, no Spec Kit. `.kb/spikes.md`
    §1 to §7.
11. PROJECT-SPECIFIC FACT. "This repository was initialized with Spec Kit 1.3.3
    using the `opencode` integration" (`.kb/spec-kit.md`). The exact `specify
    init` flags belong beside it, not in a skill.

## What should not become a skill

- The `ast-ste100` spelling in the request (L163). The installed skill is
  `asd-ste100`, and the agent resolved it without asking. One occurrence.
- The comparison table of medic against upstream (L100 to L109). It records one
  repository's state on one day, and `37238a0` replaced it.
- The per-file migration order and the rename of `requirements/AGENTS.md`. The
  law in `.kb/agents.md` covers the rule and the history covers the rest.
- The `git reset --soft` recovery sequence. The preventive rule is candidate 2,
  and a recovery recipe invites misuse on a remote that others use.
- The choice to skip the justfile, the requirements checker and the Workshop
  definition. That was a scope answer for that day.
- The `.workshop.lock` and `state.env` decisions as separate lessons. They are
  in `.kb/spikes.md` §4 and in `.gitignore`.
