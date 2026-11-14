# ses_e34b265feffe9BZkiM63DEuZVg: LXD bridged NIC ACL rejection

## What the person asked for

The session holds one prompt, written by the spawning session
(`ses_e35403258ffeVHpL6OjWM92vaG`). No human turn appears in this transcript
(flat:2-26).

- "Answer one question from upstream LXD source: why can an LXD network ACL
  not be attached to a bridged instance NIC (the `nic` device that points at a
  bridge network), when the same ACL attaches fine to an OVN NIC and to a
  bridge network as a whole?"
- "Use the exact LXD tag `lxd-6.10.1` on the GitHub mirror."
- "(Note: the `6.10/stable` branch path 404s on the mirror)" with the
  instruction to use the tag.
- "The exact mechanism that rejects it: which function builds the allowed
  option list for a bridged NIC, that `security.acls` is absent from it, and
  where the leftover key raises the error. Give the literal error text."
- "Why that is a deliberate design boundary rather than an oversight: what the
  ACL implementation needs from the NIC that a bridged NIC does not have."
- "Whether there is any per-instance hook at all on a bridged NIC that could
  carry ACLs (for example `security.mac_filtering`, `security.ipv4_filtering`,
  `security.port_isolation`)", and what each one does, "so the answer can
  say plainly whether an equivalent per-instance egress filter exists on a
  bridge."
- "Whether a newer LXD release (6.11, 7.x, or main) adds `security.acls` to a
  bridged NIC. Check the same file on `main` and say yes or no with the
  quote."
- "Do not speculate: if a claim cannot be confirmed from the source, say "not
  confirmed"."

## What was produced, and whether it worked

One five-part answer with quotes, about 125 lines (flat:30-155). No file was
written and no commit was made, which matches a read-only research task.

- The mechanism is answered end to end: the bridged NIC option list, the
  validator wiring, the leftover key, and the literal rejection (flat:34-81).
- The contrast against the OVN NIC is answered with its option list and with
  `UpdatableFields` (flat:85-95).
- The design question is answered with one doc quote about bridge
  limitations and with the code asymmetry, a per-network firewall chain
  against an OVN port group (flat:99-126).
- The per-instance hook question is answered with the implementation of each
  key, not with the option names (flat:128-139).
- The newer-release question is answered for `main`, and the child says 6.11
  could not be checked separately (flat:143-155).
- Not verified by the child, and it says so: LXD 6.11. It also leaves open
  whether a `lxd-vm` runtime differs, which the prompt did not ask.

The prompt repeats the first child's finding as a standing note, that "the
`6.10/stable` branch path 404s on the mirror", with the instruction to use
the tag (flat:8). This session's log has no failed fetch, so the note did its
work.

## Corrections the person made

(none found)

## Conventions, commands and values stated and written down nowhere

- The ref to use, as the parent handed it over: "Use the exact LXD tag
  `lxd-6.10.1` on the GitHub mirror." (flat:6).
- The literal error the answer quotes: `Invalid device option
  "security.acls"` (flat:78).
- The scope line the answer rests on: `supportedNetTypes := []string{"bridge",
  "ovn"}` (flat:126).
- The design line it quotes: "Unlike OVN ACLs, bridge ACLs apply only at the
  boundary between the bridge and the LXD host." (flat:101).
- The workaround it names, that `security.ipv4_filtering` implies
  `security.mac_filtering` (flat:130).

The rejection text and the "no per-instance ACL on a bridge" verdict are in
`research/acl-fence.md`. The reason the key is rejected, and the statement
that no equivalent egress filter exists at the instance level, appear in no
record.

## Failures, their cause, and the fix

(none found). The tool log holds no `!! FAILED` line. It also holds no failed
`curl`, because the child polled each candidate path with a status code
before reading it (flat:167, flat:186, flat:193).

One check deserves a name even though it passed. The 6.11 answer came from a
status code on one raw path and from a match count on the same path (flat:193).
The command that decides a missing tag, a tag listing, was not run. Checked
outside this session, read only: the tag list on `canonical/lxd` holds
`lxd-6.10.1`, `lxd-6.10.0`, and no `lxd-6.11`, so the conclusion holds.

## Candidate lessons

1. NEW. Two options are not equivalent until the code that implements each is
   read. The answer refuses an equivalence on the strength of what the keys
   do. Quote: "This is anti-spoofing on the host-side veth: it pins the
   allowed **source** MAC/IP set" (flat:135), next to "no" for an equivalent
   egress filter (flat:139).
2. NEW. A "why is this missing" question needs two things: the code asymmetry
   that leaves the feature nowhere to attach, and the doc line that states
   the limitation. Quote: "Bridge = network-level chain on the bridge
   interface." and "OVN = per-NIC logical switch port + port group."
   (flat:110, flat:115), with the doc line at flat:101.
3. NEW. A 404 on one raw path is not a tag listing. The answer states "There
   is no `lxd-6.11` tag on the mirror" (flat:155) from the check at flat:193.
   The same lesson arose in `ses_e3536c40affegAmiHGj8lD3Vkm`, where four
   slashed-URL 404s became a claim about a branch. A tag or branch list, or
   `git/matching-refs`, is the check.
4. NEW. Put a proven environment fact at the top of the child prompt. The
   parent repeated a note that "the `6.10/stable` branch path 404s on the
   mirror" from an earlier child, and this session had no failed fetch
   (flat:8).
5. ALREADY WRITTEN. The rejection of `security.acls` on a bridged NIC, and
   the command that shows it, are in `research/acl-fence.md`.
6. ALREADY WRITTEN. The answer's first sentence uses an intensifier that
   `.kb/writing-style.md` lists under Banned words. The sentence is at
   flat:32. The law applies to "an agent's replies to the person it works
   with", so a research child's prose is covered.
7. PROJECT-SPECIFIC FACT. The option lists, the wiring function, and the
   `InstanceSetupBridgeFilter` behaviour belong in a record about why the
   fence uses a bridge ACL and not an instance ACL.

## What should not become a skill

- The file list the prompt handed over (flat:10-16). The paths are specific to
  the 6.10 tree, and the child found them on its own anyway.
- The description of `security.mac_filtering`, `security.ipv4_filtering`, and
  `security.port_isolation` (flat:130, flat:136). It restates upstream docs for
  one release.
- The finding that `main` still lacks the key (flat:143-153). It is a fact
  about one date, and the prompt's own rule, "Do not speculate" (flat:26),
  already covers how to report it.
