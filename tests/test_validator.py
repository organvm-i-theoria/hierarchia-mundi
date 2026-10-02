"""Focused regressions for cross-reference validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from hierarchia.validator import _canonical_path_identity, validate_hierarchy


def _write_hierarchy_pair(tmp_path: Path, xref: str) -> None:
    target = tmp_path / "usr" / "culture" / "physics.sys"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("[target]\n# Canonical target\n", encoding="utf-8")

    source = tmp_path / "usr" / "source.sys"
    source.write_text(f"[source]\n# Cross-ref: {xref}\n", encoding="utf-8")


def test_canonical_path_identity_normalizes_only_outer_slashes() -> None:
    expected = "usr/culture/physics.sys"
    assert _canonical_path_identity(expected) == expected
    assert _canonical_path_identity(f"/{expected}") == expected
    assert _canonical_path_identity(f"/{expected}///") == expected


@pytest.mark.parametrize(
    ("xref", "expected_resolved"),
    [
        ("/usr/culture/physics.sys", True),
        ("/usr/culture/physics.sys/", True),
        ("/usr/culture/", True),
        ("/usr/culture/phys", False),
        ("/usr/culture/physics.sys.extra", False),
        ("/usr/other/physics.sys", False),
    ],
)
def test_cross_refs_require_canonical_path_identity(
    tmp_path: Path,
    xref: str,
    expected_resolved: bool,
) -> None:
    _write_hierarchy_pair(tmp_path, xref)

    report = validate_hierarchy(tmp_path)

    assert report.cross_refs_found == 1
    assert report.cross_refs_resolved == int(expected_resolved)
    unresolved = [
        issue for issue in report.warnings if issue.message == f"Unresolved cross-reference: {xref}"
    ]
    assert bool(unresolved) is not expected_resolved
