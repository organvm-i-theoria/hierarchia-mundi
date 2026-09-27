"""Tests for hierarchy validator cross-reference resolution and report generation."""

from pathlib import Path

from hierarchia.validator import validate_hierarchy


def test_cross_ref_canonical_path_resolution(tmp_path: Path) -> None:
    """Test exact match, leading/trailing slash handling, near-prefix, and malformed paths."""
    # Create target stratum: usr/culture/physics.db
    target_dir = tmp_path / "usr" / "culture"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / "physics.db"
    target_file.write_text(
        "[section_a]\n"
        "# Target stratum module\n"
        "key = value\n",
        encoding="utf-8",
    )

    # Create referrer stratum with various xrefs in comments
    referrer_dir = tmp_path / "bin"
    referrer_dir.mkdir(parents=True, exist_ok=True)
    referrer_file = referrer_dir / "test_ref.sh"
    referrer_file.write_text(
        "[section_b]\n"
        "# Xref exact match: /usr/culture/physics.db\n"
        "# Xref exact match with trailing slash: /usr/culture/physics.db/\n"
        "# Near-prefix false positive: /usr/culture/phys\n"
        "# Longer malformed suffix: /usr/culture/physics.db/invalid_suffix\n"
        "# Unrelated path: /sys/nonexistent.conf\n",
        encoding="utf-8",
    )

    report = validate_hierarchy(tmp_path)

    assert report.files_parsed == 2

    # Verify cross-reference resolution
    # Exact match and trailing slash resolve to 'usr/culture/physics.db'.
    # Near-prefix, longer malformed, and unrelated fail to resolve.

    unresolved = [
        issue.message
        for issue in report.warnings
        if "Unresolved cross-reference" in issue.message
    ]

    assert any("/usr/culture/phys" in msg for msg in unresolved)
    assert any("/usr/culture/physics.db/invalid_suffix" in msg for msg in unresolved)
    assert any("/sys/nonexistent.conf" in msg for msg in unresolved)

    # Verify that resolved ones are not in unresolved messages
    exact_msg = "Unresolved cross-reference: /usr/culture/physics.db"
    trailing_msg = "Unresolved cross-reference: /usr/culture/physics.db/"
    assert not any(msg.endswith(exact_msg) for msg in unresolved)
    assert not any(msg.endswith(trailing_msg) for msg in unresolved)

    assert report.cross_refs_found == 5
    assert report.cross_refs_resolved == 2
    assert len(unresolved) == 3
