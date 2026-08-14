"""Unit tests for name parsing (find_oracle_daily.names)."""

from find_oracle_daily.names import Candidate, parse, parse_all


def test_current_convention_name_parses():
    record = {
        "id": "ocid1.image.oc1.phx.aaaa",
        "display-name": (
            "daily-ubuntu-paravirtualized-amd64-server-26.04-resolute-v20260814-platform"
        ),
        "launch-mode": "PARAVIRTUALIZED",
        "launch-options": {"firmware": "BIOS"},
        "time-created": "2026-08-14T00:00:00Z",
    }
    candidate = parse(record)
    assert candidate == Candidate(
        ocid="ocid1.image.oc1.phx.aaaa",
        display_name=(
            "daily-ubuntu-paravirtualized-amd64-server-26.04-resolute-v20260814-platform"
        ),
        arch="amd64",
        family="server",
        version="26.04",
        suite="resolute",
        serial=20260814,
        rebuild=0,
        tail="-platform",
        launch_mode="PARAVIRTUALIZED",
        firmware="BIOS",
        time_created="2026-08-14T00:00:00Z",
    )


def test_legacy_convention_name_parses_with_empty_tail():
    record = {
        "id": "ocid1.image.oc1.phx.bbbb",
        "display-name": (
            "daily-ubuntu-paravirtualized-amd64-server-25.10-questing-v20260702"
        ),
    }
    candidate = parse(record)
    assert candidate is not None
    assert candidate.tail == ""
    assert candidate.serial == 20260702
    assert candidate.rebuild == 0


def test_rebuild_counter_parses_into_serial_and_rebuild():
    record = {
        "id": "ocid1.image.oc1.phx.cccc",
        "display-name": (
            "daily-ubuntu-paravirtualized-amd64-server-24.04-noble-v20250604.1"
        ),
    }
    candidate = parse(record)
    assert candidate is not None
    assert candidate.serial == 20250604
    assert candidate.rebuild == 1


def test_oke_image_discarded():
    record = {
        "id": "x",
        "display-name": (
            "ubuntu-paravirtualized-arm64-minimal-24.04-noble-v20251208-OKE-1.34.1"
        ),
    }
    assert parse(record) is None


def test_native_image_discarded():
    record = {
        "id": "x",
        "display-name": ("ubuntu-native-arm64-minimal-24.04-noble-v20250604.1"),
    }
    assert parse(record) is None


def test_legacy_non_daily_prefix_discarded():
    record = {
        "id": "x",
        "display-name": (
            "ubuntu-paravirtualized-amd64-minimal-22.04-jammy-v20250604.1"
        ),
    }
    assert parse(record) is None


def test_unknown_future_variant_discarded():
    record = {
        "id": "x",
        "display-name": (
            "daily-ubuntu-paravirtualized-amd64-server-26.04-resolute-v20260814-platform-v2"
        ),
    }
    assert parse(record) is None


def test_snapshot_all_parsed_candidates_have_known_tail_and_prefix(image_records):
    candidates = parse_all(image_records)
    assert candidates  # sanity: the fixture actually has parseable images
    for candidate in candidates:
        assert candidate.tail in ("", "-platform")
        assert candidate.display_name.startswith("daily-ubuntu-paravirtualized-")
