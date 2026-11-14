# ses_e3536c40affegAmiHGj8lD3Vkm: Research LXD bridge ACL mechanics

## What the person asked for

The session holds one prompt. It was written by the spawning session
(`ses_e35403258ffeVHpL6OjWM92vaG`), not by the human, and no human turn
appears in this transcript (flat:2-30).

- "Research LXD 6.10.1 network ACL mechanics for BRIDGED (non-OVN) networks."
- "Use webfetch against raw.githubusercontent.com and the GitHub API, and
  context7 with library id `/canonical/lxd`. Do NOT guess."
- "The LXD source is at https://github.com/canonical/lxd. The 6.10 LTS
  branch is `6.10/stable`. Tag for 6.10.1 is likely `lxd-6.10.1`."
- "Does LXD 6.10.x support `lxc network set <bridge> security.acls=<acl>` (a
  NETWORK-level ACL on a bridge network)?"
- "For a bridged network with a network-level ACL, WHERE in the host's packet
  path are the ACL rules applied?"
- "CRITICAL: for the EGRESS rules of a bridge network ACL, what is matched as
  "source"?"
- "Is traffic between two instances on the SAME bridge ever seen by those ACL
  rules?"
- "Can a bridged NIC device (an instance NIC with `network: <bridge>`) accept
  `security.acls` / `security.acls.default.egress.action` in 6.10.x?"
- "If you cannot confirm something from upstream, say "not confirmed" rather
  than guessing. Be thorough but return a compact report, not file dumps."

## What was produced, and whether it worked

One prose report with file paths and short quotes (flat:44-209). No file was
written and no commit was made, which matches a read-only research task.

- The report states the ref it pinned: tag `lxd-6.10.1`, commit
  `5510feb789168953a87959e807055c28fc67ac49` (flat:44).
- Q1 is answered with the bridge config keys and the validation call
  (flat:50-81). The report says the network-level key exists for
  `network-bridge`.
- Q2 is answered with the nftables chains `acl`, `aclin`, `aclout`, `aclfwd`
  and the xtables jumps from INPUT, OUTPUT, and FORWARD (flat:85-127).
- Q3 is answered with the rule rendering, `iifname "<bridge>" ip saddr {...}`
  and `-i <bridge> --source ...`, plus the statement that `rule.Source` is
  copied from the ACL rule (flat:131-165).
- Q4 is answered with the doc quote about intra-bridge firewalls and the
  xtables `! -o <bridge>` exclusion (flat:169-186).
- Q5 is answered with the absence of the keys from the bridged NIC option
  list and the literal error (flat:190-208).
- Not readable: the transcript clip starts at flat:209. The answer to Q6, the
  `drop` against `reject` question, and the report's closing paragraph cannot
  be read from this file.

The report agreed with the design the parent adopted for the fence. It states
that a rule can name a source (`flat:161`) and also that the source is not
constrained to the bridge subnet (flat:164). The later spike prompt repeats
that the agent bridge rules must not name a source address.

## Corrections the person made

(none found). The correction ran the other way. The child contradicted the
prompt's own premise: "Note: the `6.10/stable` branch path does not resolve on
the GitHub mirror (404)." (flat:44)

## Conventions, commands and values stated and written down nowhere

- The raw URL shape that worked, which the prompt did not give:
  `https://raw.githubusercontent.com/canonical/lxd/lxd-6.10.1/<path>`
  (flat:44).
- The literal device rejection: `Invalid device option "security.acls"`
  (flat:204).
- The valid rule actions, quoted from source:
  `var ValidActions = []string{"allow", "drop", "reject"}` (flat:81).
- The nftables chain names `aclin`, `aclout`, `aclfwd`, `acl` (flat:106).
- The exclusion the xtables driver writes for same-bridge forwarding:
  `"FORWARD", "-i", networkName, "!", "-o", networkName` (flat:114).

These are upstream facts about LXD, so they belong in a record. The two that
the repository has no home for are the chain names and the jump points.

## Failures, their cause, and the fix

Four `webfetch` calls answered 404 at the start (flat:211-218): three raw files
under `6.10/stable`, and the API lookup
`api.github.com/repos/canonical/lxd/branches/6.10/stable`. The cause the child
recorded is that the ref does not resolve in that URL shape. The fix was to
list the tags, take the tag commit, list its tree, and fetch raw URLs under
the tag (flat:219-220).

What the log does not show is any query of the branch list or of
`git/matching-refs`. The run therefore never separated "the branch does not
exist" from "a slash in a ref cannot be used in that URL". It reported the
first reading.

Checked outside this session, read only: `git/matching-refs/heads/6.10` on
`canonical/lxd` returns an empty list, and the same 404 still answers for a
slashed ref. So the conclusion holds, and the command that produced it could
not have shown it.

## Candidate lessons

1. NEW. A 404 from a URL that holds a slash in the ref is not evidence about
   the ref, because the same answer comes back for a branch that exists. The
   check is a ref listing, such as `git/matching-refs/heads/<prefix>`, run
   against a prefix known to exist as a control. Quote: "the `6.10/stable`
   branch path does not resolve on the GitHub mirror (404)" (flat:44). The
   four 404s are at flat:211-218.
2. NEW. Hand a research child a ref that was shown to exist, and let it fetch
   the tree listing before any file. The prompt said "The 6.10 LTS branch is
   `6.10/stable`. Tag for 6.10.1 is likely `lxd-6.10.1`." (flat:6). The
   branch name was wrong, and the tag was right (flat:44).
3. NEW. An inference drawn from code that is absent needs a label. The report
   answers Q4 for the nftables driver with "This is kernel/netfilter
   semantics" (flat:184), which rests on no quote, while the same report
   marks other gaps "not confirmed" as the prompt asked. Quote: "the chain is
   an **inet-family (L3)** filter hook, so purely L2-switched intra-bridge
   frames never traverse it" (flat:184).
4. NEW. A code reading of "what the rule matches" does not answer "what the
   instance cannot change". Quote: "A rule with `source=10.0.0.5/32` **does**
   distinguish two instances on the same bridge by their fixed IP"
   (flat:161). The same answer states the caveat at flat:164, that the source
   is not constrained to the bridge subnet. The parent's "CRITICAL" framing
   (flat:22) invites the stronger reading, which the source-claim probe later
   disproved (`research/separate-bridges.md`, `research/two-bridge-gateway.md`).
5. ALREADY WRITTEN. LXD 6.10.1 rejects `security.acls` on a bridged NIC, with
   `Invalid device option`. `research/acl-fence.md`, Verdict and Gotchas.
6. ALREADY WRITTEN. `security.acls.default.egress.action=allow` is needed on a
   network that holds an ACL, or the network loses its own egress.
   `research/separate-bridges.md`, Gotchas.
7. PROJECT-SPECIFIC FACT. The chain names, the jump points, and the fact that
   an egress rule also matches traffic to the host belong in a record under
   `research/`, not in a skill.

## What should not become a skill

- "Use webfetch against raw.githubusercontent.com and the GitHub API, and
  context7 with library id `/canonical/lxd`" (flat:4). The tool choice and one
  library id describe this task.
- The tag commit `5510feb789168953a87959e807055c28fc67ac49` (flat:44). A pin is
  a value for a record.
- "Be thorough but return a compact report, not file dumps" (flat:30). Read as
  a candidate about report shape, it restates the output the parent asked for
  and gives no rule a later session could apply.
- The finding that the xtables driver excludes same-interface forwarding. It
  is a fact about one upstream version, and the fence design no longer depends
  on intra-bridge filtering.
