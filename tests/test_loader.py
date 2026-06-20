"""Focused tests for hierarchy file loading and parsing."""

from pathlib import Path

from hierarchia.loader import (
    discover_hierarchy_files,
    extract_cross_references,
    load_hierarchia,
    parse_file,
)
from hierarchia.models.stratum import ModuleType, Scale, StratumType


def write_hierarchy_file(root: Path, rel_path: str, content: str) -> Path:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def test_parse_ini_sections_coerces_properties_and_collects_refs(tmp_path: Path) -> None:
    path = write_hierarchy_file(
        tmp_path,
        "sys/gravity.conf",
        """
        # Gravity kernel
        # /boot/big_bang.sh seeds this stratum
        [meta_law]
        # Fundamental cosmic law references /sys/quantum_mechanics/wave_function.so
        enabled = true
        count = 3
        ratio = 6.02e23
        tags = ["quantum", "cosmic", "cell"]
        path = "/lib/automata.lib"
        expression = mass * acceleration

        [process_loop]
        # Transforms matter and produces cells.
        active = false # inline comment is ignored for the value
        """,
    )

    stratum = parse_file(path, tmp_path)

    assert stratum is not None
    assert stratum.id == "sys.gravity"
    assert stratum.path == "sys/gravity.conf"
    assert stratum.stratum_type is StratumType.SYS
    assert stratum.description == "Gravity kernel /boot/big_bang.sh seeds this stratum"
    assert stratum.dependencies == ["/boot/big_bang.sh"]

    meta_law, process_loop = stratum.modules
    assert meta_law.id == "sys.gravity.meta_law"
    assert meta_law.name == "Meta Law"
    assert meta_law.module_type is ModuleType.LAW
    assert meta_law.scale == [Scale.QUANTUM, Scale.COSMIC]
    assert meta_law.cross_refs == [
        "/sys/quantum_mechanics/wave_function.so",
        "/lib/automata.lib",
    ]
    assert meta_law.properties == {
        "enabled": True,
        "count": 3,
        "ratio": 6.02e23,
        "tags": ["quantum", "cosmic", "cell"],
        "path": "/lib/automata.lib",
        "expression": "mass * acceleration",
    }

    assert process_loop.id == "sys.gravity.process_loop"
    assert process_loop.module_type is ModuleType.PROCESS
    assert process_loop.scale == [Scale.QUANTUM, Scale.COSMIC, Scale.CELLULAR]
    assert process_loop.properties == {"active": False}


def test_parse_banner_sections_slugifies_titles_and_extracts_xrefs(tmp_path: Path) -> None:
    path = write_hierarchy_file(
        tmp_path,
        "net/technium/generative_systems.run",
        """
        # Networked technogenesis
        # ==========================
        # T = The Planetary Feedback System:
        # Converts signals through /net/noosphere.sock
        resonance = 42

        # ==========================
        this is not a banner title

        # ==========================
        # SIGNAL FIELD EMISSION ----
        # A quantum wave field.
        amplitude = 99.5
        """,
    )

    stratum = parse_file(path, tmp_path)

    assert stratum is not None
    assert stratum.id == "net.technium.generative_systems"
    assert stratum.stratum_type is StratumType.NET
    assert [module.id for module in stratum.modules] == [
        "net.technium.generative_systems.t_the_planetary_feedback_system",
        "net.technium.generative_systems.signal_field_emission",
    ]

    feedback, signal = stratum.modules
    assert feedback.name == "T The Planetary Feedback System"
    assert feedback.module_type is ModuleType.PROCESS
    assert feedback.scale == [Scale.PLANETARY, Scale.META]
    assert feedback.cross_refs == ["/net/noosphere.sock"]
    assert feedback.properties == {"resonance": 42}

    assert signal.name == "Signal Field Emission"
    assert signal.module_type is ModuleType.SIGNAL
    assert signal.scale == [Scale.PLANETARY, Scale.META, Scale.QUANTUM]
    assert signal.properties == {"amplitude": 99.5}


def test_discover_hierarchy_files_applies_skip_rules(tmp_path: Path) -> None:
    write_hierarchy_file(tmp_path, "sys/gravity.conf", "[newtonian]\nconstant = 6.674e-11")
    write_hierarchy_file(tmp_path, ".strange_loop_config", "[loop]\nenabled = true")
    write_hierarchy_file(tmp_path, "README.md", "[ignored]\nvalue = true")
    write_hierarchy_file(tmp_path, "hierarchia/ignored.sys", "[ignored]\nvalue = true")
    write_hierarchy_file(tmp_path, "tests/ignored.sys", "[ignored]\nvalue = true")
    write_hierarchy_file(tmp_path, "doc/ignored.sys", "[ignored]\nvalue = true")
    write_hierarchy_file(tmp_path, "notes.tmp", "[ignored]\nvalue = true")

    discovered = discover_hierarchy_files(tmp_path)

    assert {str(path.relative_to(tmp_path)) for path in discovered} == {
        ".strange_loop_config",
        "sys/gravity.conf",
    }


def test_load_hierarchia_skips_files_without_modules_and_exports_refs(tmp_path: Path) -> None:
    write_hierarchy_file(
        tmp_path,
        "lib/automata.lib",
        """
        # Library header only
        # /sys/gravity.conf is a dependency, but this file has no modules.
        """,
    )
    write_hierarchy_file(
        tmp_path,
        "bin/organism_behavior.sh",
        """
        #!/usr/bin/env bash
        set -euo pipefail
        [cellular_process]
        # Produces behavior using /lib/automata.lib
        retries = 2
        """,
    )

    hierarchy = load_hierarchia(tmp_path)
    refs = extract_cross_references(hierarchy)

    assert hierarchy.stratum_count == 1
    assert hierarchy.module_count == 1
    assert hierarchy.get_stratum("lib.automata") is None
    module = hierarchy.get_module("bin.organism_behavior.cellular_process")
    assert module is not None
    assert module.scale == [Scale.CELLULAR, Scale.ORGANISM]
    assert [ref.model_dump() for ref in refs] == [
        {
            "source_id": "bin.organism_behavior.cellular_process",
            "target_id": "/lib/automata.lib",
            "context": "",
            "relation": "references",
        }
    ]


def test_parse_file_returns_none_for_empty_skipped_and_unknown_files(tmp_path: Path) -> None:
    empty = tmp_path / "sys/empty.conf"
    empty.parent.mkdir(parents=True)
    empty.write_text("", encoding="utf-8")
    skipped = write_hierarchy_file(tmp_path, "README.md", "[ignored]\nvalue = true")
    unknown = write_hierarchy_file(tmp_path, "sys/not-hierarchy.tmp", "[ignored]\nvalue = true")

    assert parse_file(empty, tmp_path) is None
    assert parse_file(skipped, tmp_path) is None
    assert parse_file(unknown, tmp_path) is None
