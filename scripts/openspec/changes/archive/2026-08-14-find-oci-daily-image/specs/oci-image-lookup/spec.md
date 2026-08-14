## ADDED Requirements

### Requirement: Command-line interface

The lookup tool SHALL accept a required suite selector and optional
architecture, family, serial, and verbosity arguments.

The tool SHALL accept the suite selector either as the first positional
argument or as the value of `--suite`, and SHALL treat the two forms as
equivalent.

The tool SHALL reject an invocation supplying neither form, and SHALL reject
an invocation supplying both forms, including when the two values are equal.

The tool SHALL accept options before or after the positional suite argument.

The tool SHALL default `--arch` to `amd64` and `--family` to `server`.

The tool SHALL reject values for `--arch` outside `{amd64, arm64}` and values
for `--family` outside `{server, minimal}`.

#### Scenario: Positional invocation

- **WHEN** the tool is invoked as `find-oracle-daily resolute`
- **THEN** it resolves using `arch=amd64` and `family=server`
- **AND** exits 0 with a single image OCID on stdout

#### Scenario: Flag invocation is equivalent

- **WHEN** the tool is invoked with only `--suite resolute`
- **THEN** the result is byte-for-byte identical to the positional form

#### Scenario: Options interleaved with the positional

- **WHEN** the tool is invoked as `find-oracle-daily -v --serial 20260814 resolute`
- **THEN** the positional suite, the serial, and the verbose flag are all
  applied

#### Scenario: All selectors supplied

- **WHEN** the tool is invoked with `noble --arch arm64 --family minimal`
- **THEN** it resolves against arm64 minimal noble images only

#### Scenario: Suite argument omitted

- **WHEN** the tool is invoked with neither a positional suite nor `--suite`
- **THEN** it exits non-zero
- **AND** stdout is empty
- **AND** a usage message is written to stderr

#### Scenario: Both suite forms supplied

- **WHEN** the tool is invoked as `find-oracle-daily resolute --suite resolute`
- **THEN** it exits non-zero
- **AND** stdout is empty
- **AND** stderr states that the suite may be given positionally or as a flag
  but not both

#### Scenario: Conflicting suite forms supplied

- **WHEN** the tool is invoked as `find-oracle-daily noble --suite resolute`
- **THEN** it exits non-zero
- **AND** neither value is silently preferred

#### Scenario: Invalid architecture rejected

- **WHEN** the tool is invoked with `--arch x86_64`
- **THEN** it exits non-zero
- **AND** stdout is empty
- **AND** stderr names the accepted values

### Requirement: Suite selector accepts codename or version

The tool SHALL accept either an Ubuntu release codename or a numeric
`YY.MM` version as the value of `--suite`.

The tool SHALL treat an argument matching `^\d\d\.\d\d$` as a version and
compare it against the version component of the image display name; any other
argument SHALL be compared against the codename component.

The tool SHALL NOT maintain a static mapping between codenames and versions.

#### Scenario: Codename supplied

- **WHEN** `--suite resolute` is given
- **THEN** images whose display-name codename component is `resolute` are considered

#### Scenario: Version supplied

- **WHEN** `--suite 26.04` is given
- **THEN** images whose display-name version component is `26.04` are considered
- **AND** the result is identical to that of `--suite resolute`

#### Scenario: Unrecognized suite

- **WHEN** `resolut` is given as the suite
- **THEN** no images match
- **AND** the tool exits non-zero with an empty stdout

### Requirement: Image source query

The tool SHALL retrieve candidate images from the `ubuntu-cloud-images`
compartment
`ocid1.compartment.oc1..aaaaaaaa2vkjkwqeeoai5n5gzdkmwk7ocbufwctls4zzrmdmjbxwudrug7xq`
in region `us-phoenix-1` using the `oci` CLI with the `DEFAULT` profile.

The tool SHALL restrict the query server-side to `lifecycle-state` `AVAILABLE`
and `operating-system` `Ubuntu`.

The tool SHALL retrieve all pages of results.

#### Scenario: Oracle-published images excluded

- **WHEN** the compartment contains images with `operating-system` of
  `Canonical Ubuntu`, `Oracle Linux`, or `Windows`
- **THEN** those images are not present in the candidate set

#### Scenario: Non-available images excluded

- **WHEN** an image is in lifecycle state `DELETED` or `DISABLED`
- **THEN** that image is not present in the candidate set

### Requirement: Display-name parsing

The tool SHALL parse candidate display names with a regular expression
anchored at both the start and the end of the string, extracting
architecture, family, version, codename, serial, optional rebuild counter,
and optional variant tail.

The tool SHALL accept only the `daily-ubuntu-paravirtualized-` prefix.

The tool SHALL accept only an empty variant tail or the tail `-platform`.

The tool SHALL silently discard any candidate whose display name does not
match.

#### Scenario: Current-convention name parsed

- **WHEN** the candidate is
  `daily-ubuntu-paravirtualized-amd64-server-26.04-resolute-v20260814-platform`
- **THEN** it parses to arch `amd64`, family `server`, version `26.04`,
  codename `resolute`, serial `20260814`, rebuild absent, tail `-platform`

#### Scenario: Legacy-convention name parsed

- **WHEN** the candidate is
  `daily-ubuntu-paravirtualized-amd64-server-25.10-questing-v20260702`
- **THEN** it parses with an empty tail and is retained as a platform image

#### Scenario: Rebuild counter parsed

- **WHEN** a display name carries a rebuild suffix such as `v20250604.1`
- **THEN** the serial parses as `20250604` and the rebuild counter as `1`

#### Scenario: OKE image discarded

- **WHEN** the candidate display name ends with `-OKE-1.36.1` or `-OKE-1.36.1p`
- **THEN** it is discarded

#### Scenario: Native image discarded

- **WHEN** the candidate display name contains `-native-` in the
  virtualization position
- **THEN** it is discarded

#### Scenario: Legacy non-daily prefix discarded

- **WHEN** the candidate display name begins with `ubuntu-` rather than
  `daily-ubuntu-`
- **THEN** it is discarded

#### Scenario: Unknown future variant discarded

- **WHEN** the candidate display name carries an unrecognized tail after the
  serial, such as `-platform-v2`
- **THEN** it is discarded rather than treated as a platform image

### Requirement: Selection by serial

The tool SHALL select the candidate with the highest serial after filtering by
suite, architecture, and family.

The tool SHALL order candidates by the tuple of integer serial and integer
rebuild counter, treating an absent rebuild counter as zero.

The tool SHALL NOT use `time-created` to determine ordering.

#### Scenario: Highest serial wins

- **WHEN** candidates have serials `20260811`, `20260812`, and `20260814`
- **THEN** the `20260814` image is selected

#### Scenario: Ordering across the convention change

- **WHEN** the candidate set contains both bare-tail serials up to `20260702`
  and `-platform` serials from `20260705` onward
- **THEN** the highest serial is selected regardless of its tail

#### Scenario: Rebuild counters ordered numerically

- **WHEN** candidates share serial `20250604` with rebuild counters `9` and `10`
- **THEN** the image with rebuild counter `10` is selected

### Requirement: Serial override

The tool SHALL accept an optional `--serial YYYYMMDD` argument that pins
selection to that exact serial instead of choosing the highest.

#### Scenario: Pinned serial resolves

- **WHEN** `--serial 20260812` is given and an image with that serial exists
  for the requested suite, architecture, and family
- **THEN** that image is selected even if higher serials exist

#### Scenario: Pinned serial absent

- **WHEN** `--serial 20260101` is given and no image with that serial exists
- **THEN** the tool exits non-zero with an empty stdout

### Requirement: Output contract

On success the tool SHALL write exactly one image OCID to stdout, followed by
a newline, and SHALL write the resolved display name to stderr.

In default mode the tool SHALL write nothing else to stdout.

On any failure the tool SHALL write nothing to stdout.

#### Scenario: Command substitution is safe

- **WHEN** the tool is invoked in default mode inside a shell command
  substitution
- **THEN** the captured value is the bare OCID with no surrounding text

#### Scenario: Interactive user sees the selection

- **WHEN** the tool is invoked in default mode in a terminal
- **THEN** the resolved display name appears on stderr
- **AND** the OCID appears on stdout

### Requirement: Verbose mode

The tool SHALL accept a `-v` flag that additionally writes human-readable
detail to stdout.

Verbose detail SHALL include the display name, serial, launch mode, firmware,
and creation time.

The tool SHALL write the OCID as the first line of stdout in verbose mode.

The tool SHALL NOT make an additional API call to produce verbose detail.

#### Scenario: Verbose fields present

- **WHEN** the tool is invoked with `-v`
- **THEN** stdout begins with the OCID
- **AND** subsequent stdout lines include the display name, serial, launch
  mode, firmware, and creation time

#### Scenario: Firmware surfaced

- **WHEN** the selected image has `launch-options.firmware` of `BIOS`
- **THEN** `BIOS` appears in the verbose output

### Requirement: Failure modes

The tool SHALL exit non-zero and write a diagnostic to stderr when no image
matches, when more than one image shares the selected serial, or when the
`oci` CLI invocation fails.

The tool SHALL distinguish these three conditions in its stderr diagnostics.

The tool SHALL NOT select arbitrarily among multiple images sharing the
selected serial.

#### Scenario: No match

- **WHEN** the requested combination of suite, architecture, and family yields
  no candidates
- **THEN** the tool exits non-zero
- **AND** stderr states that no image matched and lists the filters applied

#### Scenario: Ambiguous match

- **WHEN** two candidates share the selected serial for the same suite,
  architecture, and family
- **THEN** the tool exits non-zero
- **AND** stderr states that the match was ambiguous and lists the candidate
  OCIDs
- **AND** stdout is empty

#### Scenario: Upstream CLI failure

- **WHEN** the `oci` CLI exits non-zero or returns output that is not valid
  JSON
- **THEN** the tool exits non-zero
- **AND** stderr reports the failure
- **AND** stdout is empty

### Requirement: Read-only operation

The tool SHALL NOT invoke any mutating Oracle Cloud API operation.

#### Scenario: Only list operations issued

- **WHEN** the tool runs to completion in any mode
- **THEN** the only Oracle Cloud operation performed is an image list query

### Requirement: Invocation wrapper

The tool SHALL be invocable as a single command named `find-oracle-daily`
from `PATH`, requiring no virtual environment activation by the caller.

The wrapper SHALL forward all arguments unchanged to the underlying package.

The wrapper SHALL forward the package's exit code unchanged.

The wrapper SHALL NOT write anything to stdout that the package did not
produce, including environment provisioning or dependency resolution output.

The wrapper SHALL resolve its own location so that it works when invoked
through a symbolic link.

#### Scenario: Arguments forwarded

- **WHEN** `find-oracle-daily --suite resolute --arch arm64 -v` is invoked
- **THEN** the package receives all four arguments unchanged

#### Scenario: Exit code forwarded

- **WHEN** the package exits non-zero for an ambiguous match
- **THEN** the wrapper exits with that same code

#### Scenario: Cold start does not pollute stdout

- **WHEN** the tool is invoked with no provisioned environment present, so
  that dependency resolution and environment creation must occur
- **THEN** stdout contains only the OCID
- **AND** all provisioning output appears on stderr

#### Scenario: Invoked through a symbolic link

- **WHEN** the wrapper is invoked via a path that traverses a symbolic link to
  the repository directory
- **THEN** it locates the package correctly and resolves normally

#### Scenario: Runner absent

- **WHEN** the `uv` runner is not installed
- **THEN** the wrapper exits non-zero
- **AND** stderr states that `uv` is required
- **AND** stdout is empty

### Requirement: Unit-tested pure logic

Display-name parsing, filtering, and selection SHALL be implemented as pure
functions with no I/O, and SHALL be covered by unit tests.

The test suite SHALL run without network access and without Oracle Cloud
credentials.

The test suite SHALL exercise parsing and selection against a recorded
snapshot of real image records from the target compartment.

#### Scenario: Tests run offline

- **WHEN** the test suite is run on a machine with no Oracle Cloud credentials
  and no network access
- **THEN** all tests pass

#### Scenario: Known-awkward names covered

- **WHEN** the test suite runs
- **THEN** it asserts correct handling of the suite that straddles the
  variant-suffix convention change, of a family whose images carry no variant
  suffix, of a display name containing a rebuild counter, and of duplicate
  display names in the excluded legacy name family

#### Scenario: Ambiguity covered synthetically

- **WHEN** no real pair of images shares a selected serial
- **THEN** the ambiguous-match path is covered by a test constructing such a
  pair directly

