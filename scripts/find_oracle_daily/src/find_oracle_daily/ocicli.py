"""The only I/O module in this package: subprocess -> `oci` CLI -> parsed JSON.

Everything downstream of `list_images()` is a pure function of the returned
list of dict records.
"""

from __future__ import annotations

import json
import subprocess

COMPARTMENT_OCID = "ocid1.compartment.oc1..aaaaaaaa2vkjkwqeeoai5n5gzdkmwk7ocbufwctls4zzrmdmjbxwudrug7xq"
REGION = "us-phoenix-1"
PROFILE = "DEFAULT"


class OciCliError(Exception):
    """Raised when the `oci` CLI invocation fails or returns unusable output."""


def list_images() -> list[dict]:
    """Invoke `oci compute image list` and return the parsed `data` list.

    Restricts the query server-side to lifecycle-state AVAILABLE and
    operating-system Ubuntu, and retrieves all pages.
    """
    command = [
        "oci",
        "compute",
        "image",
        "list",
        "-c",
        COMPARTMENT_OCID,
        "--region",
        REGION,
        "--profile",
        PROFILE,
        "--lifecycle-state",
        "AVAILABLE",
        "--operating-system",
        "Ubuntu",
        "--all",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise OciCliError(f"failed to invoke oci CLI: {exc}") from exc

    if result.returncode != 0:
        raise OciCliError(
            f"oci CLI exited with code {result.returncode}: {result.stderr.strip()}"
        )

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise OciCliError(f"oci CLI returned non-JSON output: {exc}") from exc

    if "data" not in payload:
        raise OciCliError("oci CLI response missing 'data' key")

    return payload["data"]
