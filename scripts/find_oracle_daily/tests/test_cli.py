"""Unit tests for the CLI and output contract (find_oracle_daily.cli)."""

from unittest.mock import patch

import pytest

from find_oracle_daily import cli
from find_oracle_daily.ocicli import OciCliError


@pytest.fixture
def patched_images(image_records):
    with patch("find_oracle_daily.cli.list_images", return_value=image_records):
        yield


def _run(argv, capsys):
    exit_code = cli.main(argv)
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def test_positional_and_flag_invocations_are_identical(patched_images, capsys):
    code_pos, out_pos, err_pos = _run(["resolute"], capsys)
    code_flag, out_flag, err_flag = _run(["--suite", "resolute"], capsys)
    assert code_pos == code_flag == cli.EXIT_OK
    assert out_pos == out_flag
    assert err_pos == err_flag


def test_options_interleave_with_positional_verbose_serial_first(
    patched_images, capsys
):
    code, out, err = _run(["-v", "--serial", "20260812", "resolute"], capsys)
    assert code == cli.EXIT_OK
    assert "serial: 20260812" in out


def test_options_interleave_with_positional_arch_after(patched_images, capsys):
    code, out, err = _run(["resolute", "--arch", "arm64"], capsys)
    assert code == cli.EXIT_OK
    assert out.strip()


def test_neither_suite_form_supplied_exits_nonzero_empty_stdout(capsys):
    with pytest.raises(SystemExit) as exc_info:
        cli.main([])
    captured = capsys.readouterr()
    assert exc_info.value.code != 0
    assert captured.out == ""


def test_both_suite_forms_agreeing_exits_nonzero_empty_stdout(capsys):
    with pytest.raises(SystemExit) as exc_info:
        cli.main(["resolute", "--suite", "resolute"])
    captured = capsys.readouterr()
    assert exc_info.value.code != 0
    assert captured.out == ""


def test_both_suite_forms_conflicting_exits_nonzero_empty_stdout(capsys):
    with pytest.raises(SystemExit) as exc_info:
        cli.main(["noble", "--suite", "resolute"])
    captured = capsys.readouterr()
    assert exc_info.value.code != 0
    assert captured.out == ""


def test_success_writes_only_ocid_to_stdout_and_name_to_stderr(patched_images, capsys):
    code, out, err = _run(["resolute"], capsys)
    assert code == cli.EXIT_OK
    lines = out.splitlines()
    assert len(lines) == 1
    assert lines[0].startswith("ocid1.image.")
    assert "resolute" in err


def test_verbose_output_begins_with_ocid_and_includes_firmware_and_launch_mode(
    patched_images, capsys
):
    code, out, err = _run(["-v", "resolute"], capsys)
    assert code == cli.EXIT_OK
    lines = out.splitlines()
    assert lines[0].startswith("ocid1.image.")
    assert any("firmware" in line for line in lines)
    assert any("launch-mode" in line for line in lines)


def test_no_match_exits_with_distinct_code_and_empty_stdout(patched_images, capsys):
    code, out, err = _run(["resolut"], capsys)
    assert code == cli.EXIT_NO_MATCH
    assert out == ""
    assert err.strip() != ""


def test_invalid_serial_exits_nonzero_before_api_call(capsys):
    with patch("find_oracle_daily.cli.list_images") as mock_list:
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["resolute", "--serial", "20200101x"])
        assert not mock_list.called
    captured = capsys.readouterr()
    assert exc_info.value.code != 0
    assert captured.out == ""


def test_ambiguous_match_exits_with_distinct_code_and_empty_stdout(capsys):
    records = [
        {
            "id": "ocid1.image.oc1.phx.aaa",
            "display-name": (
                "daily-ubuntu-paravirtualized-amd64-server-26.04-resolute-v20260814"
            ),
        },
        {
            "id": "ocid1.image.oc1.phx.bbb",
            "display-name": (
                "daily-ubuntu-paravirtualized-amd64-server-26.04-resolute-v20260814-platform"
            ),
        },
    ]
    with patch("find_oracle_daily.cli.list_images", return_value=records):
        code, out, err = _run(["resolute"], capsys)
    assert code == cli.EXIT_AMBIGUOUS
    assert out == ""
    assert "ocid1.image.oc1.phx.aaa" in err
    assert "ocid1.image.oc1.phx.bbb" in err


def test_oci_cli_failure_exits_with_distinct_code_and_empty_stdout(capsys):
    with patch("find_oracle_daily.cli.list_images", side_effect=OciCliError("boom")):
        code, out, err = _run(["resolute"], capsys)
    assert code == cli.EXIT_OCI_FAILURE
    assert out == ""
    assert "boom" in err
