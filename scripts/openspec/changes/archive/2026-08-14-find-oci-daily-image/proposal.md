## Why

Selecting the correct Canonical-published Ubuntu daily image on Oracle Cloud
currently requires manually listing 600+ images in the `ubuntu-cloud-images`
compartment and eyeballing display names. The compartment mixes our published
dailies with Oracle's own platform images, OKE variants, legacy `native`
builds, and a naming convention that changed mid-suite. Picking the wrong
image is expensive: a mis-selected bare-metal image can burn a two-hour boot
cycle before the mistake is visible.

We need a single deterministic lookup that emits one image OCID on stdout,
suitable for direct substitution into `oci compute instance launch` and
similar CLI commands.

## What Changes

- Add a `uv`-managed Python package `find_oracle_daily` that resolves
  `(suite, arch, family[, serial])` to exactly one OCI image OCID from the
  `ubuntu-cloud-images` compartment.
- Add a thin `scripts/find-oracle-daily` shell wrapper that delegates to the
  package, so the tool is invocable by name from `PATH` with no activation
  step and no visible Python.
- Ship `pytest` unit tests covering name parsing, selection, and the output
  contract, run against a snapshot of real image names captured from the
  compartment.
- The suite may be given either positionally (`find-oracle-daily resolute`) or
  as a flag (`--suite resolute`); the two forms are equivalent.
- Selection is by highest `YYYYMMDD` serial in the display name, with an
  optional `--serial` override for pinning a specific day.
- Platform images are identified as those whose display name ends with either
  `-platform` or the serial itself; OKE variants are excluded.
- Output contract: stdout carries only the OCID; the resolved display name
  always goes to stderr. A `-v` flag adds human-readable detail (serial,
  launch-mode, firmware, time-created) to stdout, explicitly trading away
  pipe-safety for interactive use.
- Ambiguity is a hard failure: if more than one image matches the winning
  serial, the script exits non-zero rather than guessing.
- Scope is deliberately fixed for this iteration: the `ubuntu-cloud-images`
  compartment, region `us-phoenix-1`, and `paravirtualized` virtualization
  only.

## Capabilities

### New Capabilities
- `oci-image-lookup`: Deterministic resolution of Canonical-published Ubuntu
  daily platform images on Oracle Cloud to a single image OCID, covering the
  display-name grammar, filtering rules, selection order, output contract,
  and failure modes.

### Modified Capabilities

None. This is the first capability in this project.

## Impact

- **New wrapper**: `scripts/find-oracle-daily`, executable, reachable via the
  existing `~/scripts` symlink already on `PATH`.
- **New package**: `scripts/find_oracle_daily/`, a `uv` project with
  `pyproject.toml`, a lockfile, a `src/` layout, and a `tests/` suite. This is
  the first first-party Python project in the dotfiles repository.
- **New tooling dependency**: `uv` for running and testing. The package itself
  has no runtime dependencies beyond the standard library; `pytest` is a
  development-only dependency.
- **External dependency**: the `oci` CLI (>= 3.85) and a configured `DEFAULT`
  profile with read access to the `ubuntu-cloud-images` compartment.
- **Runtime**: one `oci compute image list` call per invocation, roughly four
  seconds, plus about 90 ms of `uv` startup. No caching in this iteration.
- **Repository hygiene**: the package's `.venv/` must be excluded from version
  control; the lockfile must be committed.
- **No changes** to existing scripts. Consumers such as the OCI runbook work
  in `~/git/oracle-cloud` may adopt it later, but nothing is modified here.
- **Read-only**: the tool makes no mutating API calls.
