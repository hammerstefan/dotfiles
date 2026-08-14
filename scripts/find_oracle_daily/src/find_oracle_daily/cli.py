"""CLI, argument parsing, and the stdout/stderr output contract.

Exit codes:
    0  success
    2  usage error (argparse default: bad/missing arguments)
    3  no image matched the given filters
    4  more than one image shared the selected serial (ambiguous)
    5  the `oci` CLI invocation failed
"""

from __future__ import annotations

import argparse
import re
import sys

from find_oracle_daily.names import parse_all
from find_oracle_daily.ocicli import OciCliError, list_images
from find_oracle_daily.select import filter_candidates, select_winners

EXIT_OK = 0
EXIT_NO_MATCH = 3
EXIT_AMBIGUOUS = 4
EXIT_OCI_FAILURE = 5

_SERIAL_RE = re.compile(r"^\d{8}$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="find-oracle-daily",
        description=(
            "Resolve an Ubuntu daily image on Oracle Cloud to exactly one "
            "image OCID, safe to substitute into "
            "`oci compute instance launch --image-id`."
        ),
    )
    parser.add_argument(
        "suite_pos",
        nargs="?",
        metavar="SUITE",
        help="Ubuntu codename (e.g. resolute) or version (e.g. 26.04)",
    )
    parser.add_argument(
        "--suite",
        help="equivalent to the positional SUITE argument",
    )
    parser.add_argument(
        "--arch",
        choices=["amd64", "arm64"],
        default="amd64",
    )
    parser.add_argument(
        "--family",
        choices=["server", "minimal"],
        default="server",
    )
    parser.add_argument(
        "--serial",
        metavar="YYYYMMDD",
        help="pin selection to this exact serial instead of the highest",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="also print display name, serial, launch mode, firmware, and "
        "creation time to stdout",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.suite_pos is None and args.suite is None:
        parser.error("a suite is required, either positionally or via --suite")
    if args.suite_pos is not None and args.suite is not None:
        parser.error("the suite may be given positionally or as --suite, but not both")
    suite = args.suite_pos if args.suite_pos is not None else args.suite

    serial: int | None = None
    if args.serial is not None:
        if not _SERIAL_RE.match(args.serial):
            parser.error("--serial must be exactly 8 digits (YYYYMMDD)")
        serial = int(args.serial)

    try:
        records = list_images()
    except OciCliError as exc:
        print(f"oci CLI invocation failed: {exc}", file=sys.stderr)
        return EXIT_OCI_FAILURE

    candidates = parse_all(records)
    filtered = filter_candidates(
        candidates, suite=suite, arch=args.arch, family=args.family
    )
    winners = select_winners(filtered, serial=serial)

    if not winners:
        filters = f"suite={suite} arch={args.arch} family={args.family}"
        if serial is not None:
            filters += f" serial={args.serial}"
        print(f"no image matched filters: {filters}", file=sys.stderr)
        return EXIT_NO_MATCH

    if len(winners) > 1:
        print(
            "ambiguous match: multiple images share the selected serial:",
            file=sys.stderr,
        )
        for candidate in winners:
            print(f"  {candidate.ocid}  {candidate.display_name}", file=sys.stderr)
        return EXIT_AMBIGUOUS

    winner = winners[0]
    print(winner.ocid)
    print(winner.display_name, file=sys.stderr)

    if args.verbose:
        print(f"display-name: {winner.display_name}")
        print(f"serial: {winner.serial}")
        print(f"launch-mode: {winner.launch_mode}")
        print(f"firmware: {winner.firmware}")
        print(f"time-created: {winner.time_created}")

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
