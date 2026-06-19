"""Command-line interface for Hierarchia Mundi.

A single runnable entry point over the typed hierarchy. From a clean checkout:

    pip install -e .
    hierarchia stats          # or: python -m hierarchia stats
    hierarchia search entropy
    hierarchia validate
    hierarchia export -o hierarchia.json

Every subcommand loads the 42 strata / 676 modules from the repository tree
and reports on them. `validate` exits non-zero when structural errors exist,
which makes it usable as a CI gate.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from hierarchia import __version__
from hierarchia.loader import load_hierarchia
from hierarchia.validator import validate_hierarchy


def _default_root() -> Path:
    """The repository root that ships alongside this package."""
    return Path(__file__).resolve().parent.parent


def _cmd_stats(root: Path) -> int:
    h = load_hierarchia(root)
    modules = [m for s in h.strata.values() for m in s.modules]

    by_stratum_type: Counter[str] = Counter(
        s.stratum_type.value for s in h.strata.values()
    )
    by_module_type: Counter[str] = Counter(m.module_type.value for m in modules)
    by_scale: Counter[str] = Counter(
        scale.value for m in modules for scale in m.scale
    )

    print(f"hierarchia {__version__}  —  {root}")
    print(f"strata:  {h.stratum_count}")
    print(f"modules: {h.module_count}")

    print("\nby stratum type:")
    for name, count in sorted(by_stratum_type.items()):
        print(f"  {name:<10} {count}")

    print("\nby module type:")
    for name, count in sorted(by_module_type.items()):
        print(f"  {name:<10} {count}")

    print("\nby scale:")
    for name, count in sorted(by_scale.items()):
        print(f"  {name:<10} {count}")
    return 0


def _cmd_search(root: Path, query: str) -> int:
    h = load_hierarchia(root)
    results = h.search_modules(query)
    print(f"{len(results)} module(s) matching {query!r}:")
    for module in results:
        print(f"  {module.id:<48} [{module.module_type.value}] {module.name}")
    return 0


def _cmd_validate(root: Path) -> int:
    report = validate_hierarchy(root)
    print(f"files checked:      {report.files_checked}")
    print(f"files parsed:       {report.files_parsed}")
    print(f"modules found:      {report.modules_found}")
    print(f"cross-refs found:   {report.cross_refs_found}")
    print(f"cross-refs resolved:{report.cross_refs_resolved}")
    print(f"errors:             {len(report.errors)}")
    print(f"warnings:           {len(report.warnings)}")
    for issue in report.errors:
        print(f"  ERROR {issue.file_path}: {issue.message}")
    print("valid" if report.is_valid else "INVALID")
    return 0 if report.is_valid else 1


def _cmd_export(root: Path, output: str | None) -> int:
    h = load_hierarchia(root)
    payload = h.model_dump(mode="json")
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"wrote {h.module_count} modules across {h.stratum_count} strata to {output}")
    else:
        sys.stdout.write(text)
        sys.stdout.write("\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hierarchia",
        description="Typed, executable models of reality's structure.",
    )
    parser.add_argument("--version", action="version", version=f"hierarchia {__version__}")
    parser.add_argument(
        "--root",
        type=Path,
        default=_default_root(),
        help="Repository root to load the hierarchy from (default: packaged repo root).",
    )

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("stats", help="Print stratum/module counts and breakdowns (default).")

    p_search = sub.add_parser("search", help="Search modules by name or description.")
    p_search.add_argument("query", help="Substring to match against module name/description.")

    sub.add_parser("validate", help="Validate the hierarchy; exit non-zero on errors.")

    p_export = sub.add_parser("export", help="Export the full hierarchy as JSON.")
    p_export.add_argument(
        "-o", "--output", help="File to write JSON to (default: stdout)."
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root: Path = args.root

    command = args.command or "stats"
    if command == "stats":
        return _cmd_stats(root)
    if command == "search":
        return _cmd_search(root, args.query)
    if command == "validate":
        return _cmd_validate(root)
    if command == "export":
        return _cmd_export(root, args.output)

    parser.error(f"unknown command: {command}")
    return 2  # unreachable; parser.error exits


if __name__ == "__main__":
    raise SystemExit(main())
