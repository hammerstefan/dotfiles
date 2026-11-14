A session quote is evidence, not a fact. The session may have been wrong, and
the tool it described may have moved since. Check every claim before you write
it, when the claim is one a reader could test:

- a command, a flag, a path, a version, a default, an exit code.
- what a tool accepts, refuses or prints.
- what the repository does today.

# Run it

Run every example before you write it, and show its output. Type the command.
Use `git branch <name>` for a rule about branch names, `--help` and `--version`
for a flag, and `find` for a path.

Record the command and its result in the extraction report, one line per claim,
with the version.

# Name the scope

A claim without a scope is not a claim a reader can test.

- "`lxc` has no `-p`" is false on this host. "`lxc exec` refuses `-p` on
  6.10.1" is a claim a reader can check.
- Name the version you tested. Name the subcommand you tested.
- A blanket claim about a binary must be split per subcommand or dropped. A
  binary is not one behaviour.

# Reaching every copy

A false claim is usually copied. Search the repository for other copies: skills,
`AGENTS.md`, `GLOSSARY.md`, scripts, the knowledge base. Correct every copy in
the same change. When a copy lives outside the repository, correct it where it
lives and name it in the extraction report.

Commit messages repeat claims too. When a commit message on the caller's branch
restates a claim you corrected, name it in the extraction report. The caller
corrects it before the push.

# What you cannot check

A claim you could not check is "not checked". Never state it as a fact. Say in
the extraction report which claims you checked and which you did not.

A preference is not a claim. "I prefer short paragraphs" needs no test. "The
linter accepts this" does.
