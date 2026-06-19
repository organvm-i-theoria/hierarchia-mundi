"""Parse hierarchy files (.sys, .conf, .so, .db, .sh, etc.) into typed models.

The hierarchy format is commented pseudocode with two section styles:

Style 1 (INI-style):
    [section_name]   → Module boundary

Style 2 (banner-style):
    # ============...   → Section divider
    # SECTION TITLE      → Module boundary (next non-divider comment after ===)
    # ============...   → Section divider (optional closing)

Both styles use:
    # comment        → Description text
    key = "value"    → Property
    key = value      → Property (unquoted)
    /path/to/file    → Cross-reference (in comments)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from hierarchia.models.cross_ref import CrossReference
from hierarchia.models.stratum import (
    Hierarchia,
    Module,
    ModuleType,
    Scale,
    Stratum,
    StratumType,
)

# Files that are hierarchy content (not docs, not Python, not config)
HIERARCHY_EXTENSIONS = {
    ".sys", ".conf", ".so", ".db", ".sh", ".exe", ".loop", ".cron",
    ".algo", ".daemon", ".api", ".lib", ".net", ".run", ".sock",
    ".log", ".pdf", ".txt", ".md",
}

# Directories we skip (not hierarchy content)
SKIP_DIRS = {"doc", "hierarchia", "tests", "__pycache__", ".git", ".github", "node_modules"}

# Files at root that are not hierarchy strata
SKIP_FILES = {"README.md", "seed.yaml", "pyproject.toml", "hierarchia.json", ".DS_Store"}

# Pattern for [section_name] headers
SECTION_RE = re.compile(r"^\[([^\]]+)\]")

# Pattern for banner section dividers: # ============...
BANNER_RE = re.compile(r"^#\s*={4,}")

# Pattern for banner section title: # TITLE (all-caps, mixed-case, or T = ... style)
BANNER_TITLE_RE = re.compile(r"^#\s+(.{3,})")

# Pattern for key = value or key = "value"
KV_RE = re.compile(r'^(\w[\w.]*)\s*=\s*(.+)$')

# Pattern for filesystem cross-references: /path/to/file.ext
XREF_RE = re.compile(r'(/(?:boot|sys|lib|bin|usr|net|dev|\.)[/\w._-]+)')


def _classify_stratum_type(rel_path: str) -> StratumType:
    """Determine StratumType from the file's directory."""
    parts = Path(rel_path).parts
    if len(parts) == 1:
        # Root-level file
        return StratumType.ROOT
    first_dir = parts[0]
    mapping = {
        "boot": StratumType.BOOT,
        "sys": StratumType.SYS,
        "lib": StratumType.LIB,
        "bin": StratumType.BIN,
        "usr": StratumType.USR,
        "net": StratumType.NET,
        "dev": StratumType.DEV,
    }
    return mapping.get(first_dir, StratumType.ROOT)


def _make_stratum_id(rel_path: str) -> str:
    """Convert filesystem path to a dotted stratum id.

    sys/gravity.conf → sys.gravity
    usr/culture/belief_systems/classical_mythology.db
        → usr.culture.belief_systems.classical_mythology
    """
    p = Path(rel_path)
    parts = list(p.parent.parts) + [p.stem]
    # Remove leading '.' from dotfiles
    parts = [part.lstrip(".") for part in parts if part != "."]
    return ".".join(parts)


def _make_module_id(stratum_id: str, section_name: str) -> str:
    """Create a qualified module id."""
    return f"{stratum_id}.{section_name.lower()}"


def _guess_module_type(section_name: str, description: str) -> ModuleType:
    """Heuristic classification of a section into a ModuleType."""
    name_lower = section_name.lower()
    desc_lower = description.lower()

    # Laws and axioms
    if any(w in name_lower for w in ("law", "axiom", "principle", "meta_law", "razor")):
        return ModuleType.LAW
    if any(w in desc_lower for w in ("law", "axiom", "principle", "fundamental")):
        return ModuleType.LAW

    # Processes
    if any(w in name_lower for w in ("process", "loop", "cycle", "cron", "daemon")):
        return ModuleType.PROCESS
    if any(w in desc_lower for w in ("transforms", "converts", "produces", "generates")):
        return ModuleType.PROCESS

    # Systems
    if any(w in name_lower for w in ("system", "theory", "model", "framework")):
        return ModuleType.SYSTEM

    # Signals
    if any(w in name_lower for w in ("signal", "wave", "field", "emission")):
        return ModuleType.SIGNAL

    # Substrates
    if any(w in name_lower for w in ("substrate", "medium", "material", "element")):
        return ModuleType.SUBSTRATE

    # Default to entity
    return ModuleType.ENTITY


def _guess_scales(stratum_type: StratumType, description: str) -> list[Scale]:
    """Heuristic scale assignment based on stratum type and description."""
    type_scales: dict[StratumType, list[Scale]] = {
        StratumType.ROOT: [Scale.META],
        StratumType.BOOT: [Scale.COSMIC],
        StratumType.SYS: [Scale.QUANTUM, Scale.COSMIC],
        StratumType.LIB: [Scale.MOLECULAR],
        StratumType.BIN: [Scale.CELLULAR, Scale.ORGANISM],
        StratumType.USR: [Scale.ORGANISM, Scale.ECOSYSTEM, Scale.PLANETARY],
        StratumType.NET: [Scale.PLANETARY, Scale.META],
        StratumType.DEV: [Scale.META],
    }
    base = type_scales.get(stratum_type, [Scale.META])

    # Refine from description keywords
    desc_lower = description.lower()
    if "quantum" in desc_lower:
        if Scale.QUANTUM not in base:
            base.append(Scale.QUANTUM)
    if "cosmic" in desc_lower or "universe" in desc_lower:
        if Scale.COSMIC not in base:
            base.append(Scale.COSMIC)
    if "cell" in desc_lower:
        if Scale.CELLULAR not in base:
            base.append(Scale.CELLULAR)

    return base


def _parse_value(raw: str) -> Any:
    """Parse a value string into a Python type."""
    raw = raw.strip()

    # Quoted string
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]

    # Multi-line quoted (continues with quote on next line — treat as string)
    if raw.startswith('"') or raw.startswith("'"):
        return raw.strip("\"'")

    # Boolean
    if raw.lower() == "true":
        return True
    if raw.lower() == "false":
        return False

    # List
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1]
        items = [item.strip().strip("\"'") for item in inner.split(",")]
        return [i for i in items if i]

    # Number
    try:
        if "." in raw or "e" in raw.lower():
            return float(raw)
        return int(raw)
    except ValueError:
        pass

    # Identifier or expression
    return raw


def parse_file(filepath: Path, repo_root: Path) -> Stratum | None:
    """Parse a single hierarchy file into a Stratum with Modules."""
    rel_path = str(filepath.relative_to(repo_root))

    # Skip non-hierarchy files
    if filepath.name in SKIP_FILES:
        return None
    if filepath.suffix not in HIERARCHY_EXTENSIONS and filepath.name != ".strange_loop_config":
        return None

    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    lines = content.splitlines()
    if not lines:
        return None

    # Skip shebang and shell boilerplate
    lines = [ln for ln in lines if not ln.startswith("#!") and ln.strip() != "set -euo pipefail"]

    stratum_type = _classify_stratum_type(rel_path)
    stratum_id = _make_stratum_id(rel_path)

    # Extract file-level description from leading comments (before first section)
    file_description_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if SECTION_RE.match(stripped):
            break
        if stripped.startswith("#"):
            text = stripped.lstrip("# ").strip()
            if text and not text.startswith("==="):
                file_description_lines.append(text)

    file_description = " ".join(file_description_lines[:5])

    # Parse sections into modules
    modules: list[Module] = []
    all_xrefs: list[str] = []
    dependencies: list[str] = []

    current_section: str | None = None
    current_comments: list[str] = []
    current_properties: dict[str, Any] = {}
    current_xrefs: list[str] = []

    def _flush_section() -> None:
        if current_section is None:
            return
        desc = " ".join(current_comments[:10]) if current_comments else current_section
        module = Module(
            id=_make_module_id(stratum_id, current_section),
            name=current_section.replace("_", " ").title(),
            module_type=_guess_module_type(current_section, desc),
            description=desc,
            scale=_guess_scales(stratum_type, desc),
            cross_refs=list(current_xrefs),
            properties=dict(current_properties),
        )
        modules.append(module)
        all_xrefs.extend(current_xrefs)

    expecting_banner_title = False

    for line in lines:
        stripped = line.strip()

        # Section header (INI-style: [section_name])
        m = SECTION_RE.match(stripped)
        if m:
            _flush_section()
            current_section = m.group(1)
            current_comments = []
            current_properties = {}
            current_xrefs = []
            expecting_banner_title = False
            continue

        # Banner section divider: # ============
        if BANNER_RE.match(stripped):
            expecting_banner_title = True
            continue

        # Banner section title: # THE FOUR LAWS (follows a banner divider)
        if expecting_banner_title:
            bt = BANNER_TITLE_RE.match(stripped)
            if bt:
                _flush_section()
                title = bt.group(1).strip().rstrip("—–-: ")
                # Slugify: lowercase, collapse non-alphanumeric to underscore, trim
                slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
                # Truncate very long slugs but keep enough to be unique
                if len(slug) > 60:
                    slug = slug[:60].rstrip("_")
                current_section = slug
                current_comments = []
                current_properties = {}
                current_xrefs = []
                expecting_banner_title = False
                continue
            # If the line after banner isn't a title, reset
            if stripped and not stripped.startswith("#"):
                expecting_banner_title = False

        if current_section is None:
            # Still in file header — scan for cross-refs
            for xm in XREF_RE.finditer(stripped):
                dependencies.append(xm.group(1))
            continue

        # Comment line
        if stripped.startswith("#"):
            text = stripped.lstrip("# ").strip()
            if text and not BANNER_RE.match(stripped):
                current_comments.append(text)
            # Extract cross-references from comments
            for xm in XREF_RE.finditer(stripped):
                current_xrefs.append(xm.group(1))
            continue

        # Key-value pair
        kv = KV_RE.match(stripped)
        if kv:
            key = kv.group(1)
            val = _parse_value(kv.group(2).split("#")[0].strip())  # strip inline comment
            current_properties[key] = val
            # Check value for cross-references
            for xm in XREF_RE.finditer(stripped):
                current_xrefs.append(xm.group(1))
            continue

        # Extract cross-refs from any other line
        for xm in XREF_RE.finditer(stripped):
            current_xrefs.append(xm.group(1))

    # Flush final section
    _flush_section()

    return Stratum(
        id=stratum_id,
        path=rel_path,
        name=filepath.stem.replace("_", " ").title(),
        stratum_type=stratum_type,
        description=file_description,
        modules=modules,
        dependencies=list(set(dependencies)),
    )


def discover_hierarchy_files(repo_root: Path) -> list[Path]:
    """Find all hierarchy files in the repo, excluding non-content directories."""
    files: list[Path] = []
    for item in sorted(repo_root.rglob("*")):
        if item.is_dir():
            continue
        # Skip excluded directories
        if any(skip in item.parts for skip in SKIP_DIRS):
            continue
        if item.name in SKIP_FILES or item.name.startswith(".DS_"):
            continue
        # Include hierarchy files by extension, plus known dotfiles
        if item.suffix in HIERARCHY_EXTENSIONS:
            files.append(item)
        elif item.name == ".strange_loop_config":
            files.append(item)
    return files


def load_hierarchia(repo_root: Path | str) -> Hierarchia:
    """Load the entire hierarchy from the repository root.

    Discovers all hierarchy files, parses each into a Stratum,
    and assembles the complete Hierarchia.
    """
    repo_root = Path(repo_root)
    files = discover_hierarchy_files(repo_root)

    strata: dict[str, Stratum] = {}
    for filepath in files:
        stratum = parse_file(filepath, repo_root)
        if stratum and stratum.modules:
            strata[stratum.id] = stratum

    return Hierarchia(strata=strata)


def extract_cross_references(hierarchia: Hierarchia) -> list[CrossReference]:
    """Extract all cross-references from a loaded Hierarchia."""
    refs: list[CrossReference] = []
    for stratum in hierarchia.strata.values():
        for module in stratum.modules:
            for xref_path in module.cross_refs:
                refs.append(CrossReference(
                    source_id=module.id,
                    target_id=xref_path,
                    relation="references",
                ))
    return refs
