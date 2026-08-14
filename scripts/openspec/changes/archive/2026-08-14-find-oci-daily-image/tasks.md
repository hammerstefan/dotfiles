## 1. Package scaffolding

- [x] 1.1 Create the `uv` project at `scripts/find_oracle_daily/` with `uv init --lib`, a `src/` layout, and package name `find-oracle-daily`
- [x] 1.2 Set `requires-python = ">=3.12"`, empty runtime `dependencies`, and a `dev` dependency group containing `pytest`
- [x] 1.3 Declare the console entry point `find-oracle-daily = "find_oracle_daily.cli:main"` in `[project.scripts]`
- [x] 1.4 Add a package-local `.gitignore` excluding `.venv/`, and confirm `uv.lock` is not excluded
- [x] 1.5 Run `uv sync` and confirm the entry point resolves via `uv run --project scripts/find_oracle_daily find-oracle-daily --help`

## 2. Wrapper

- [x] 2.1 Create the executable `scripts/find-oracle-daily` bash wrapper that resolves its own directory with `readlink -f` and execs `uv run --quiet --project "$here/find_oracle_daily" find-oracle-daily "$@"`
- [x] 2.2 Add a guard that emits an actionable stderr message and exits non-zero when `uv` is not on `PATH`
- [x] 2.3 Verify the wrapper works when invoked as `find-oracle-daily` through the `~/scripts` symlink from an unrelated working directory
- [x] 2.4 Verify exit codes propagate unchanged through the wrapper
- [x] 2.5 Verify a cold start with `.venv` deleted leaves stdout carrying only the OCID

## 3. Name parsing (`names.py`)

- [x] 3.1 Define a frozen `Candidate` dataclass holding ocid, display name, arch, family, version, suite, serial, rebuild, tail, launch mode, firmware, and creation time
- [x] 3.2 Define the anchored display-name regex with named groups, accepting only the `daily-ubuntu-paravirtualized-` prefix and an empty or `-platform` tail
- [x] 3.3 Implement `parse(record) -> Candidate | None`, returning `None` for any non-matching display name and extracting `launch-options.firmware` defensively
- [x] 3.4 Implement `parse_all(records) -> list[Candidate]` discarding `None` results

## 4. Selection (`select.py`)

- [x] 4.1 Implement suite matching: an argument matching `^\d\d\.\d\d$` compares against `version`, anything else against `suite`
- [x] 4.2 Implement filtering by suite, arch, and family
- [x] 4.3 Implement the sort key `(int(serial), int(rebuild or 0))` and selection of the maximum
- [x] 4.4 Implement the `--serial` override path restricting to an exact serial
- [x] 4.5 Return the full set of candidates sharing the winning key so the caller can detect ambiguity, rather than collapsing to one

## 5. OCI access (`ocicli.py`)

- [x] 5.1 Define the constants `COMPARTMENT_OCID`, `REGION = "us-phoenix-1"`, `PROFILE = "DEFAULT"`
- [x] 5.2 Implement `list_images() -> list[dict]` invoking `oci compute image list` with `-c`, `--region`, `--profile`, `--lifecycle-state AVAILABLE`, `--operating-system Ubuntu`, `--all` via `subprocess.run`, capturing stdout and stderr separately
- [x] 5.3 Raise a distinct exception on non-zero exit, unparseable JSON, or missing `data` key, carrying the captured stderr
- [x] 5.4 Confirm this is the only module in the package performing I/O

## 6. CLI and output contract (`cli.py`)

- [x] 6.1 Build the `argparse` parser with an optional positional `SUITE`, plus `--suite`, `--arch`, `--family`, `--serial`, and `-v`/`--verbose`
- [x] 6.2 Add the post-parse check rejecting an invocation that supplies neither suite form, and one that supplies both, including when the values agree
- [x] 6.3 Validate `--serial` as exactly eight digits before any API call
- [x] 6.4 Define distinct non-zero exit codes for no-match, ambiguous-match, and upstream-failure
- [x] 6.5 Write the OCID plus newline to stdout and the resolved display name to stderr on every success
- [x] 6.6 Under `-v`, append display name, serial, launch mode, firmware, and creation time to stdout after the OCID line, using only fields already present in the list response
- [x] 6.7 Emit the no-match diagnostic listing the filters that were applied
- [x] 6.8 Emit the ambiguous diagnostic listing candidate OCIDs and display names
- [x] 6.9 Confirm by inspection that no code path writes to stdout on any failure
- [x] 6.10 Add `__main__.py` so `python -m find_oracle_daily` works

## 7. Test fixtures

- [x] 7.1 Capture a snapshot of the compartment into `tests/fixtures/images.json`, reduced to the fields the tool consumes
- [x] 7.2 Confirm the snapshot retains the awkward cases: questing straddling the convention change, stonking/minimal with no `-platform` suffix, a `v20250604.1` rebuild counter, the duplicate `ubuntu-*-v20251208-OKE-*` names, and Oracle's `Canonical Ubuntu` records
- [x] 7.3 Add a `conftest.py` fixture loading the snapshot once per session

## 8. Unit tests

- [x] 8.1 `test_names.py`: current-convention and legacy-convention names parse with the expected field values
- [x] 8.2 `test_names.py`: a rebuild counter parses into separate serial and rebuild fields
- [x] 8.3 `test_names.py`: OKE, `native`, legacy `ubuntu-`-prefixed, and unknown-tail names all parse to `None`
- [x] 8.4 `test_names.py`: across the whole snapshot, every parsed candidate has tail in `{"", "-platform"}` and prefix `daily-ubuntu-paravirtualized-`
- [x] 8.5 `test_select.py`: highest serial wins for a straightforward suite
- [x] 8.6 `test_select.py`: questing selects the highest-serial `-platform` image rather than the newest bare-tail one
- [x] 8.7 `test_select.py`: stonking/minimal resolves to a bare-tail image
- [x] 8.8 `test_select.py`: rebuild counters order numerically, asserting `.10` beats `.9`
- [x] 8.9 `test_select.py`: codename and version arguments select identically
- [x] 8.10 `test_select.py`: an unknown suite, and a `--serial` with no match, both yield an empty result
- [x] 8.11 `test_select.py`: a synthetic pair of records sharing a serial yields two candidates, driving the ambiguity path
- [x] 8.12 `test_cli.py`: positional and `--suite` invocations produce byte-for-byte identical stdout and stderr
- [x] 8.13 `test_cli.py`: options interleave with the positional, covering both `-v --serial X resolute` and `resolute --arch arm64`
- [x] 8.14 `test_cli.py`: supplying neither suite form, and supplying both (agreeing and conflicting), each exit non-zero with empty stdout
- [x] 8.15 `test_cli.py`: success writes only the OCID to stdout and the display name to stderr
- [x] 8.16 `test_cli.py`: `-v` output begins with the OCID and includes firmware and launch mode
- [x] 8.17 `test_cli.py`: each of the three failure conditions exits with its distinct code and writes nothing to stdout
- [x] 8.18 Confirm the whole suite passes with `uv run --project scripts/find_oracle_daily pytest` with no network access and no OCI credentials

## 9. End-to-end verification

- [x] 9.1 Verify `find-oracle-daily resolute`, `find-oracle-daily --suite resolute`, and `find-oracle-daily 26.04` all return the same OCID, matching the highest-serial 26.04 amd64 server platform image in the compartment
- [x] 9.2 Verify `--arch arm64` and `--family minimal` each change the result as expected
- [x] 9.3 Verify `--serial` pins to an older image that exists
- [x] 9.4 Verify `IMG=$(find-oracle-daily resolute)` captures a bare OCID while the display name still reaches the terminal
- [x] 9.5 Verify `resolut`, `--serial 20200101`, `--arch x86_64`, and `resolute --suite resolute` each exit non-zero with empty stdout and distinguishable stderr
- [x] 9.6 Verify `-v` reports `firmware` and `launch-mode` for a live lookup
- [x] 9.7 Assert the returned display name against the regex to confirm no OKE, `native`, or legacy-prefixed image can be returned

## 10. Repository integration

- [x] 10.1 Run `git status` after a cold run and confirm `.venv/` is untracked and ignored while `uv.lock` is staged
- [x] 10.2 Add a usage example to the package docstring showing substitution into an `oci compute instance launch --image-id` invocation
- [x] 10.3 Confirm `find-oracle-daily` is reachable by name in a fresh shell
