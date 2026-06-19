"""Tests for the hierarchia command-line interface."""

import json
from pathlib import Path

import pytest

from hierarchia.__main__ import main

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_stats_runs_and_reports_counts(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--root", str(REPO_ROOT), "stats"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "strata:" in out
    assert "modules:" in out
    assert "by module type:" in out


def test_stats_is_default_command(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--root", str(REPO_ROOT)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "modules:" in out


def test_search_lists_matches(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--root", str(REPO_ROOT), "search", "entropy"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "matching 'entropy'" in out


def test_validate_exit_code_tracks_validity(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--root", str(REPO_ROOT), "validate"])
    out = capsys.readouterr().out
    # Exit code mirrors validity: 0 when no structural errors, 1 otherwise.
    assert rc in (0, 1)
    assert "errors:" in out
    assert ("valid" in out) or ("INVALID" in out)
    assert (rc == 0) == ("INVALID" not in out)


def test_export_to_file_round_trips(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out_file = tmp_path / "export.json"
    rc = main(["--root", str(REPO_ROOT), "export", "-o", str(out_file)])
    assert rc == 0
    assert out_file.exists()
    payload = json.loads(out_file.read_text(encoding="utf-8"))
    assert "strata" in payload
    assert len(payload["strata"]) > 0


def test_export_to_stdout_is_valid_json(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--root", str(REPO_ROOT), "export"])
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert payload["strata"]
