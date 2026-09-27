"""Validate hierarchy files against the schema and check cross-reference integrity.

Two levels of validation:
1. Structural — does the file parse into a valid Stratum with modules?
2. Referential — do cross-references point to strata/modules that exist?
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from hierarchia.loader import discover_hierarchy_files, parse_file


@dataclass
class ValidationIssue:
    """A single validation issue found in the hierarchy."""

    file_path: str
    message: str
    severity: str = "warning"  # "error" or "warning"
    module_id: str = ""


@dataclass
class ValidationReport:
    """Accumulated validation results for the hierarchy."""

    issues: list[ValidationIssue] = field(default_factory=list)
    files_checked: int = 0
    files_parsed: int = 0
    modules_found: int = 0
    cross_refs_found: int = 0
    cross_refs_resolved: int = 0

    @property
    def is_valid(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def validate_hierarchy(repo_root: Path | str) -> ValidationReport:
    """Validate the entire hierarchy: structure + cross-references."""
    repo_root = Path(repo_root)
    report = ValidationReport()

    files = discover_hierarchy_files(repo_root)
    report.files_checked = len(files)

    # Parse all files
    strata = {}
    for filepath in files:
        stratum = parse_file(filepath, repo_root)
        if stratum is None:
            report.issues.append(ValidationIssue(
                file_path=str(filepath.relative_to(repo_root)),
                message="File could not be parsed (empty or no sections)",
                severity="warning",
            ))
            continue
        if not stratum.modules:
            report.issues.append(ValidationIssue(
                file_path=stratum.path,
                message="File parsed but contains no [section] modules",
                severity="warning",
            ))
            continue
        report.files_parsed += 1
        report.modules_found += len(stratum.modules)
        strata[stratum.id] = stratum

    # Check for duplicate module ids
    seen_ids: dict[str, str] = {}
    for stratum in strata.values():
        for module in stratum.modules:
            if module.id in seen_ids:
                report.issues.append(ValidationIssue(
                    file_path=stratum.path,
                    message=f"Duplicate module id '{module.id}' (also in {seen_ids[module.id]})",
                    severity="error",
                    module_id=module.id,
                ))
            seen_ids[module.id] = stratum.path

    # Validate cross-references
    normalized_paths = {s.path.strip("/") for s in strata.values()}
    for stratum in strata.values():
        for module in stratum.modules:
            for xref in module.cross_refs:
                report.cross_refs_found += 1
                # Check if the cross-reference resolves to a known stratum path
                if xref.strip("/") in normalized_paths:
                    report.cross_refs_resolved += 1
                else:
                    report.issues.append(ValidationIssue(
                        file_path=stratum.path,
                        message=f"Unresolved cross-reference: {xref}",
                        severity="warning",
                        module_id=module.id,
                    ))

    return report
