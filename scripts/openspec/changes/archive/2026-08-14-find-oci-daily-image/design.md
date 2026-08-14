## Context

The `ubuntu-cloud-images` compartment
(`ocid1.compartment.oc1..aaaaaaaa2vkjkwqeeoai5n5gzdkmwk7ocbufwctls4zzrmdmjbxwudrug7xq`)
in `us-phoenix-1` currently holds 618 `AVAILABLE` images. Investigation of the
live data established the following facts, which drive every decision below.

**Display-name grammar** for Canonical-published images:

```
daily-ubuntu-<virt>-<arch>-<family>-<version>-<suite>-v<YYYYMMDD>[.N][-<variant>]
```

- `<virt>`: `paravirtualized` | `native`
- `<arch>`: `amd64` | `arm64`
- `<family>`: `server` | `minimal`
- `<version>` / `<suite>`: e.g. `26.04` / `resolute` — both always present
- `[.N]`: rebuild counter, observed once (`v20250604.1`)
- `<variant>` tail is a closed set across all 405 of our images:
  `''` (128), `-platform` (58), `-OKE-<k8s-version>[p]` (219). Nothing else.

**Key findings:**

1. The `-platform` suffix is a convention that was introduced mid-suite. For
   25.10 questing/amd64/server, serials through `v20260702` are bare and
   `v20260705` onward carry `-platform`. Requiring the suffix would silently
   return nothing for older suites and for 26.10 stonking/minimal.
2. No `(arch, family, suite, serial)` key has both a bare and a `-platform`
   image. Unioning the two tails therefore never introduces ambiguity.
3. `operating-system == "Ubuntu"` matches exactly our 405 images. Oracle's own
   Ubuntu platform images use `operating-system == "Canonical Ubuntu"` (33).
   The two sets are disjoint in both directions.
4. Duplicate display names exist in this compartment — 12 of them, all
   `ubuntu-*-v20251208-OKE-*` from an apparent re-publish incident. The
   invariant "one display name maps to one OCID" does not hold.
5. There is a second, legacy name family with prefix `ubuntu-` (no `daily-`).
   All 12 duplicates live there. It is OKE-dominated today.
6. `oci compute image list` returns full image records including `launch-mode`,
   `launch-options.firmware`, and `time-created`. Verbose output costs no
   extra API call.
7. There is no `arch` field in the API response. Architecture, family, suite,
   and serial are only recoverable from the display name.
8. All current `-platform` images are `PARAVIRTUALIZED` with `firmware: BIOS`.
   `native` publishing stopped after 25.04 plucky.

## Goals / Non-Goals

**Goals:**

- Resolve `(suite, arch, family)` to exactly one image OCID, deterministically.
- Guarantee that on success, stdout contains only the OCID and nothing else,
  so `IMG=$(find-oci-daily-image.sh --suite resolute)` is safe.
- Fail closed. An unrecognized name shape, no match, or an ambiguous match
  must produce a non-zero exit and an empty stdout rather than a guess.
- Accept either the codename (`resolute`) or the version (`26.04`) as the
  suite argument, without maintaining a release lookup table.
- Surface `firmware` and `launch-mode` under `-v`, since those fields
  determine whether a bare-metal boot takes ten minutes or two hours.
- Keep the parsing and selection logic pure and unit-tested, with all I/O
  isolated in a single module.
- Present as an ordinary command on `PATH` — no virtualenv activation, no
  visible Python, no `.py` extension at the call site.

**Non-Goals:**

- Multi-region support. `us-phoenix-1` is hardcoded this iteration.
- `native` virtualization. `paravirtualized` is hardcoded.
- OKE image selection.
- Caching. The ~4s per-invocation cost is accepted.
- Staleness warnings when a suite/family combination has stopped publishing.
- Launching instances or any mutating operation.

## Decisions

### D1: Platform predicate is `tail ∈ {"", "-platform"}`, not `endswith("-platform")`

The union of both tails, followed by max-by-serial, handles the mid-suite
convention flip with no special-casing: for questing it naturally selects
`v20260708-platform` over the older bare `v20260702`.

*Alternative considered:* require `-platform`. Rejected — returns zero results
for 26.10 stonking/minimal and every suite older than questing, which is a
silent wrong answer rather than a loud one.

*Alternative considered:* exclude anything containing `-OKE-`. Rejected — it is
a blocklist, so any future third variant would be silently treated as a
platform image.

### D2: A single anchored regex is the primary filter

```
^daily-ubuntu-paravirtualized-(?P<arch>amd64|arm64)-(?P<family>server|minimal)
 -(?P<version>\d\d\.\d\d)-(?P<suite>[a-z]+)-v(?P<serial>\d{8})(?:\.(?P<rebuild>\d+))?
 (?P<tail>-platform)?$
```

Anchored at both ends. Non-matching names are dropped silently — this
correctly discards Oracle's images, all OKE variants, all `native` builds, and
the legacy `ubuntu-` family (and with it all 12 known duplicates).

The `$` anchor is load-bearing. If a new suffix appears (say `-platform-v2`),
those images fail to match and the script reports no result instead of feeding
an unknown variant into a launch command.

*Alternative considered:* use the structured `operating-system-version` field
for the version. Rejected as the primary mechanism — arch and family have no
structured equivalent, so a name regex is required regardless, and having one
source of truth is simpler than two.

### D3: `--operating-system Ubuntu` as a server-side second gate

Applied on the `oci` call. It is not a performance optimization — measured 4.0s
vs 4.5s, the latency being CLI startup and pagination, not payload. It is
defense in depth: Oracle's `Canonical Ubuntu` images are excluded structurally
rather than relying on the name regex alone.

`--lifecycle-state AVAILABLE` is likewise applied server-side.

### D4: Sort key is `(int(serial), int(rebuild or 0))`

Not a string comparison. `v20250604.1 > v20250604` happens to work
lexically, but `v20250604.10 < v20250604.9` does not. Serial is authoritative;
`time-created` is not consulted for ordering.

### D5: More than one winner is a hard failure

Given finding 4, the "one name, one OCID" invariant is not guaranteed by the
platform. D2 makes the failure unreachable today, but it is one re-publish away
from firing. Since the output feeds directly into `oci compute instance launch`,
silently picking one of two near-identical images could waste a two-hour
bare-metal boot.

*Alternative considered:* tiebreak on newest `time-created`. Rejected on the
user's instruction — a loud failure is cheaper than a wrong launch.

### D6: Output contract

| Mode | stdout | stderr | exit |
|---|---|---|---|
| success, default | OCID only | display name | 0 |
| success, `-v` | OCID, then detail lines | display name | 0 |
| no match | *(empty)* | reason | non-zero |
| ambiguous | *(empty)* | reason + candidates | non-zero |
| `oci` failed | *(empty)* | reason | non-zero |

The display name goes to stderr on *every* success, so an interactive user
always sees what was chosen while `$(...)` still captures only the OCID.

`-v` deliberately breaks the stdout contract by design: it is a human-facing
mode and implies the output is not being consumed raw by a pipe. The OCID is
still the first line so the mode degrades predictably.

Distinguishing the three failure reasons on stderr matters most for the `oci`
failure case: if the API errors and the caller does not check the exit status,
`$(...)` yields an empty string and the launch command receives a blank
`--image-id`.

### D7: A `uv`-managed package behind a shell wrapper

The tool ships as a `uv` project at `scripts/find_oracle_daily/` with a `src/`
layout, invoked through a thin executable wrapper at
`scripts/find-oracle-daily`:

```
scripts/
  find-oracle-daily               # bash wrapper, on PATH via the ~/scripts symlink
  find_oracle_daily/
    pyproject.toml                # entry point find-oracle-daily; pytest in dev group
    uv.lock                       # committed
    .gitignore                    # .venv/
    src/find_oracle_daily/
      __init__.py
      __main__.py                 # python -m support
      cli.py                      # argparse, output contract, exit codes
      names.py                    # regex, Candidate dataclass, parsing
      select.py                   # filter, max-by-serial, ambiguity detection
      ocicli.py                   # the only impure module: subprocess -> oci CLI
    tests/
      conftest.py
      fixtures/images.json        # snapshot of real compartment records
      test_names.py
      test_select.py
      test_cli.py
```

The wrapper resolves its own directory and execs `uv`:

```bash
#!/usr/bin/env bash
set -euo pipefail
here="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
exec uv run --quiet --project "$here/find_oracle_daily" find-oracle-daily "$@"
```

`readlink -f` is required because `~/scripts` is a symlink to the repository
directory, so `$0` may arrive via either path.

Measured behavior of this arrangement, verified against `uv` 0.11.12:

- **Startup cost is about 92 ms** warm, against a roughly 4 s `oci` call. Not
  material.
- **`uv run` keeps stdout clean.** Even on a cold start with no `.venv`, all
  of `Using CPython`, `Creating virtual environment`, `Building`, and
  `Installed N packages` go to stderr. Stdout carried only the program's own
  output. This is what makes the wrapper compatible with the stdout contract
  in D6, and it is the reason the wrapper is acceptable at all.
- **Exit codes propagate** through `uv run` unchanged, which D6's distinct
  failure codes depend on.
- **`--project` works from any working directory**, and places `.venv` in the
  project directory rather than the caller's.

`--quiet` suppresses the routine sync chatter while still surfacing genuine
`uv` errors.

*Alternative considered:* a single `.py` file with `argparse`. Rejected — it
gives nowhere natural to put unit tests, and the parsing and selection logic is
exactly the part that benefits most from being tested in isolation.

*Alternative considered:* PEP 723 inline script metadata with
`#!/usr/bin/env -S uv run --script`. Rejected — it supports dependencies but
not a test suite or multiple modules.

*Alternative considered:* have the wrapper exec `.venv/bin/find-oracle-daily`
directly, skipping `uv` and its 92 ms. Rejected — `uv run` re-syncs from the
lockfile on every invocation, so a fresh checkout, a changed lockfile, or a
deleted `.venv` all self-heal. Executing the venv binary directly fails
confusingly in all three cases.

*Alternative considered:* bash with inline `python3 -c`, matching `scan.sh`.
Rejected — the sort key, duplicate detection, and stdout/stderr discipline are
all awkward in bash, and it is untestable.

The package remains dependency-free at runtime, using only the standard
library and shelling out to the `oci` CLI rather than the OCI Python SDK. That
keeps auth and profile handling inherited from the existing CLI configuration
and keeps the lockfile trivial.

### D9: The `oci` invocation is isolated in one module

`ocicli.py` is the only module that performs I/O. It exposes a single function
returning the parsed list of image records, and everything downstream —
parsing, filtering, selection, formatting — is a pure function of that list.

This is what makes the test suite meaningful without network access or
credentials: tests feed recorded records straight into the pure layer.

### D10: Tests run against a real snapshot, not invented names

`tests/fixtures/images.json` holds records captured from the live compartment,
reduced to the fields the tool consumes. Invented fixtures would encode the
naming convention as we imagine it; the snapshot encodes it as it actually is,
including the awkward cases the investigation surfaced:

- questing straddling the bare/`-platform` convention change
- stonking/minimal having no `-platform` suffix at all
- the `v20250604.1` rebuild counter
- the twelve duplicate `ubuntu-*-v20251208-OKE-*` display names
- Oracle's `Canonical Ubuntu` images sitting alongside our `Ubuntu` ones

The snapshot is a point-in-time record and is not refreshed automatically.
Tests assert on structural properties and on specific known-awkward names,
not on "the newest image," which would rot the moment a new daily is
published.

Ambiguity handling is the one case with no natural fixture, since D2 makes it
unreachable from real data. It is tested with a synthetic pair of records
constructed in the test.


### D8: Suite argument dispatch

If the argument matches `^\d\d\.\d\d$` it is compared against the parsed
version; otherwise against the parsed suite codename. No release table, and a
typo simply yields no match rather than a wrong image.

### D11: Suite accepted positionally or as a flag

The suite is the only required argument and is supplied on nearly every
invocation, so requiring `--suite` adds friction with no disambiguation value.
`find-oracle-daily resolute` is the common case and should be the short form.

Implemented as an optional positional alongside the existing flag:

```python
parser.add_argument("suite_pos", nargs="?", metavar="SUITE")
parser.add_argument("--suite")
```

`--suite` therefore cannot be `required=True`; the constraint moves to a
post-parse check. Verified against `argparse` in Python 3.12, all of these
parse correctly, including interleaved options:

```
resolute                          → positional
--suite resolute                  → flag
resolute --arch arm64             → positional, options after
--serial 20260814 resolute        → positional, options before
-v resolute                       → positional after a store_true flag
```

Two cases fall to the post-parse check:

- **Neither supplied** → usage error, exit non-zero, stdout empty.
- **Both supplied** → usage error, even when the two values agree.

Rejecting the agreeing case as well is deliberate. Tolerating it would require
deciding which wins when they disagree, and any such rule is a silent
resolution of a genuinely ambiguous instruction — the same failure class that
D5 rejects for duplicate images. Refusing both forms at once is one rule
instead of two and needs no explanation of precedence.

*Alternative considered:* positional only, dropping `--suite`. Rejected —
`--suite` is self-documenting in scripts and runbooks, where explicitness is
worth more than brevity.

*Alternative considered:* make the positional accept the arch or family too,
inferring from its shape. Rejected — `minimal` and `arm64` are unambiguous
today, but the inference rule would silently misfire the moment a codename
collides with one of them.


## Risks / Trade-offs

- **A new naming convention breaks the regex** → Fails closed with a
  "no match" error rather than returning a wrong image. The fix is a one-line
  regex update. This is the intended behavior, not merely an accepted risk.

- **Hardcoded region and compartment limit reuse** → Accepted for this
  iteration. Both are module-level constants so promoting them to flags later
  is mechanical.

- **Always returns a BIOS/PARAVIRTUALIZED image** → Per prior investigation
  this is the slow-reboot configuration on bare-metal shapes, recoverable only
  via a `--launch-options` override at launch time. The script takes no
  position on this, but `-v` surfacing `firmware: BIOS` gives the operator the
  reminder at exactly the right moment.

- **~4s per invocation** → Noticeable if called several times in sequence.
  Caching is out of scope; if it becomes painful the caller can capture the
  OCID once into a variable.

- **Silent drop of non-matching names** → A user who mistypes nothing but is
  looking for an OKE or `native` image gets "no match" with no hint as to why.
  Mitigated by making the stderr message state the filters that were applied.

- **`-v` output is unstructured** → Not machine-parseable. Acceptable because
  `-v` is explicitly the human-facing mode; scripted consumers use the default
  mode, whose contract is stable.

- **`uv` becomes a hard prerequisite** → The wrapper fails if `uv` is absent,
  where a plain script would not. Mitigated by the wrapper checking for `uv`
  and emitting an actionable message on stderr rather than a bare
  `command not found`.

- **First first-party Python project in the dotfiles repository** → Introduces
  a `.venv/` that must not be committed and a lockfile that must be. Mitigated
  by a package-local `.gitignore`, and verified by a task that inspects
  `git status` after a cold run.

- **The fixture snapshot rots** → It records the compartment at a point in
  time. Naming conventions may change without any test failing. This is
  accepted: the snapshot's job is to pin the awkward cases already known, not
  to detect future upstream changes. The anchored regex from D2 is what
  handles the unknown future, by failing closed at runtime.

- **Tests cannot cover the live `oci` call** → D9 isolates it precisely so the
  rest is testable, but that leaves the subprocess invocation itself covered
  only by the manual verification tasks. Accepted; the alternative is mocking
  `subprocess`, which would test the mock rather than the CLI.
