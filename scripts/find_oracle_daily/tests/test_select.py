"""Unit tests for selection logic (find_oracle_daily.select)."""

from find_oracle_daily.names import Candidate, parse_all
from find_oracle_daily.select import filter_candidates, select_winners, suite_matches


def _candidate(**overrides) -> Candidate:
    defaults = dict(
        ocid="ocid1.image.oc1.phx.default",
        display_name="daily-ubuntu-paravirtualized-amd64-server-26.04-resolute-v20260101",
        arch="amd64",
        family="server",
        version="26.04",
        suite="resolute",
        serial=20260101,
        rebuild=0,
        tail="",
        launch_mode="PARAVIRTUALIZED",
        firmware="BIOS",
        time_created=None,
    )
    defaults.update(overrides)
    return Candidate(**defaults)


def test_highest_serial_wins_for_straightforward_suite():
    candidates = [
        _candidate(ocid="a", serial=20260811),
        _candidate(ocid="b", serial=20260812),
        _candidate(ocid="c", serial=20260814),
    ]
    winners = select_winners(candidates)
    assert len(winners) == 1
    assert winners[0].ocid == "c"


def test_questing_selects_highest_serial_platform_over_newer_bare_tail(image_records):
    candidates = parse_all(image_records)
    filtered = filter_candidates(
        candidates, suite="questing", arch="amd64", family="server"
    )
    winners = select_winners(filtered)
    assert len(winners) == 1
    assert winners[0].serial == 20260708
    assert winners[0].tail == "-platform"


def test_stonking_minimal_resolves_to_bare_tail_image(image_records):
    candidates = parse_all(image_records)
    filtered = filter_candidates(
        candidates, suite="stonking", arch="amd64", family="minimal"
    )
    winners = select_winners(filtered)
    assert len(winners) == 1
    assert winners[0].tail == ""


def test_rebuild_counters_ordered_numerically_ten_beats_nine():
    candidates = [
        _candidate(ocid="a", serial=20250604, rebuild=9),
        _candidate(ocid="b", serial=20250604, rebuild=10),
    ]
    winners = select_winners(candidates)
    assert len(winners) == 1
    assert winners[0].ocid == "b"


def test_codename_and_version_arguments_select_identically(image_records):
    candidates = parse_all(image_records)
    by_codename = select_winners(
        filter_candidates(candidates, suite="resolute", arch="amd64", family="server")
    )
    by_version = select_winners(
        filter_candidates(candidates, suite="26.04", arch="amd64", family="server")
    )
    assert by_codename == by_version
    assert len(by_codename) == 1


def test_unknown_suite_yields_empty_result(image_records):
    candidates = parse_all(image_records)
    filtered = filter_candidates(
        candidates, suite="resolut", arch="amd64", family="server"
    )
    assert select_winners(filtered) == []


def test_serial_with_no_match_yields_empty_result(image_records):
    candidates = parse_all(image_records)
    filtered = filter_candidates(
        candidates, suite="resolute", arch="amd64", family="server"
    )
    assert select_winners(filtered, serial=20200101) == []


def test_synthetic_pair_sharing_serial_drives_ambiguity_path():
    candidates = [
        _candidate(ocid="a", serial=20260814),
        _candidate(ocid="b", serial=20260814),
    ]
    winners = select_winners(candidates)
    assert len(winners) == 2
    assert {c.ocid for c in winners} == {"a", "b"}


def test_suite_matches_version_form():
    candidate = _candidate(version="26.04", suite="resolute")
    assert suite_matches(candidate, "26.04") is True
    assert suite_matches(candidate, "26.05") is False


def test_suite_matches_codename_form():
    candidate = _candidate(version="26.04", suite="resolute")
    assert suite_matches(candidate, "resolute") is True
    assert suite_matches(candidate, "noble") is False
