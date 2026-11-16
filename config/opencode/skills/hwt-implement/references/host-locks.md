# Shared host resources

Several sessions on one host meet at one resource: a virtual machine name, a
container, a port, a database, a package cache, a runner. Some resources fail
loudly when two holders use them. Others, like two conformance runs that each
read the host's instance list before and after, corrupt each other's records
while both exit zero. Assume the quiet kind.

## Find the resource before you write the brief

Ask three questions of the ticket, not of the tooling:

1. What does this work change outside the repository?
2. What does it read that another change could move under it?
3. What does it spend time on that only one session can hold at once?

The answer names the resource. Write it in the notes under `## Host resources`.
Use one line: what it is, the name this session gives its own instance, and the
lock that serializes it.

## Name everything nameable

A unique name removes a class of collision without any coordination. Examples: a
VM (`conf-vm-111`), an image alias (`conf-image-117`), a temp directory
(`/tmp/opencode/<run>/111`), or a port when the tool allows one. Take the
ticket number as the discriminator. Prefer names the tool checks (`lxc` refuses
a duplicate instance). A refused duplicate costs a lost run. A shared name
corrupts two runs.

## Lock what cannot be named

Some resources are single-instance by design. Serialize them with a directory
lock, which is atomic on every filesystem this host uses:

```sh
lock=/tmp/opencode/locks/<resource>.lock
if mkdir "$lock" 2>/dev/null; then
    printf 'ticket=%s pid=%s host=%s at=%s\n' 111 "$$" "$(hostname)" "$(date -u +%FT%TZ)" > "$lock/holder"
else
    cat "$lock/holder" 2>/dev/null || echo "holder file unreadable"
fi
```

Release it on every exit path, including a fault:

```sh
trap 'rm -rf /tmp/opencode/locks/<resource>.lock' EXIT
```

## Take a lock over only with evidence

A lock left behind blocks every later session. So a stale lock needs a rule that
someone can check, rather than a timeout someone guessed. Break a lock only when
all three points hold:

1. `cat <lock>/holder` names a process that is gone (`kill -0 <pid>` fails).
2. The instance that holder named is absent (`lxc list`, `docker ps`, or the
   named path).
3. The lock is older than the longest run this resource realistically takes.

Record the takeover in the decision log, with the output of the three commands.
A lock taken without that evidence can destroy another session's live run.

## Report the state you leave

The person needs to know the host is clean: no VM, no image, no lock, no
container, no temp directory from this session. Check it with the resource's own
listing command before the report, not from memory, and quote the line.
