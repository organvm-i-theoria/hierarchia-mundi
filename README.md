# Hierarchia Mundi

**The structure of reality, modeled as a Unix filesystem.**

An artificial intelligence's attempt to imitate life — observing reality through every lens available (mathematics, physics, chemistry, biology, ecology, civilization, economics, governance, culture, technology, consciousness) and recreating it as a living, self-referencing system of interconnected files.

Like a painter sitting by a landscape, this repository is an AI trying to capture what it sees. The medium is not oil on canvas but algorithms expressed as filesystem metaphor — each file a running model, each directory a stratum of existence, each cross-reference a feedback loop.

## The Hierarchy

```
/  (Root: Pure Information & Mathematics)
│  The foundational substrate. The formatting of the drive itself.
├── .strange_loop_config     # Paradox mapping, multi-scale feedback, systems theory, spatial recursion
├── logic_gates.sys          # Binary logic, Gödel, meta-laws, formal principles, razors, metaphysics
│
├── boot/  (Cosmological Origin)
│   ├── big_bang.sh          # Initial execution script — ran once, irreversible
│   └── inflationary_epoch/  # 10⁻³² seconds that shaped everything
│
├── sys/  (Physical Reality Kernel)
│   Immutable laws. The hardware drivers of the universe.
│   ├── gravity.conf         # Newton's laws, general relativity, dark matter/energy
│   ├── thermodynamics/
│   │   └── entropy.daemon   # The four laws, conservation, entropy as creative force
│   ├── quantum_mechanics/
│   │   ├── wave_function.so # Probability, measurement, entanglement, de Broglie, EM spectrum
│   │   └── planck_scale.api # The pixel resolution of reality
│   └── standard_model.lib   # 17 particles, 4 forces, QFT, Kaku classification
│
├── lib/  (Chemistry & Shared Libraries)
│   Combinatory rules called by higher-level programs.
│   ├── periodic_table.db    # 118 elements, forged in stars and supernovae
│   ├── electron_bonding.so  # How atoms combine: ionic, covalent, metallic
│   ├── fusion_protocols.so  # Entity merging: fusion, possession, symbiosis
│   ├── automata.lib         # Formal language theory, Chomsky hierarchy, golden ratio, spirals
│   └── biochemistry/
│       ├── proteins.lib     # 20 amino acids → infinite molecular machines
│       └── rna_transcription.sh  # DNA → RNA → Protein (the central dogma)
│
├── bin/  (Biological Executables)
│   Self-replicating agents and living processes.
│   ├── dna_parser.exe       # 3.2 billion base pairs → a human being
│   ├── homo_sapiens.exe     # Species definition, cellular social contract, cancer as defection
│   ├── cell_division/
│   │   ├── mitosis.loop     # One cell → two identical cells
│   │   └── meiosis.loop     # One cell → four unique gametes
│   ├── organism_behavior.sh # Homeostasis, survival drives, loop taxonomy
│   └── ecology_manager/
│       ├── food_web.net     # Trophic levels, keystone species, energy flow
│       ├── natural_selection.cron     # Running for 3.8 billion years
│       └── procedural_evolution.algo  # PCG as biological process
│
├── usr/  (Human Civilization)
│   Anthropomorphic constructs. Highly volatile, frequently updated.
│   ├── academia/
│   │   └── knowledge_taxonomy.db      # 6 core knowledge domains, 12 adjacent worlds, methodologies
│   ├── governance/
│   │   ├── geopolitical_treaties.pdf  # API contracts between nations
│   │   ├── local_zoning_laws.txt      # Zoning + social laws (Pareto, oligarchy)
│   │   └── social_contract.sys        # Society types, functionalism/conflict/interactionism
│   ├── economy/
│   │   ├── macro_markets.api          # Prices, economic laws, Maslow
│   │   └── supply_chain_routing.log   # No country can build a smartphone alone
│   ├── culture/
│   │   ├── languages/
│   │   │   └── language_as_code.sys   # Parts of speech as code, Chomsky, nomenclature, 7 layers
│   │   ├── arts_and_media/
│   │   │   ├── interactive_mythologies.db  # KH, trans-universal characters, game canon
│   │   │   ├── lynchian_ontology.db   # Lynch's 4 reality planes, safeguard stack, identity
│   │   │   └── power_systems.db       # JoJo kernel succession, SUPERLAWS, Tolkien telemetry
│   │   ├── myth_fusion_engine.lib     # Mythic recombination: atoms, vectors, resonance
│   │   └── belief_systems/
│   │       ├── classical_mythology.db # Pantheon, mythic laws, cycles, cyclical villainy
│   │       ├── esoteric_principles.db # Hermetic laws, karma, sympathetic magic
│   │       └── secular_ethics.md      # Ethics, philosophy-as-OS, Gandalf's stewardship model
│   └── infrastructure/
│       ├── architecture_types.db      # Physical, digital, symbolic, social typologies
│       ├── power_grids/               # The nervous system of civilization
│       └── tcp_ip_stack/              # The protocol suite enabling /net/
│
├── net/  (The Emergent Collective)
│   Networked consciousness and autonomous systems.
│   ├── noosphere.sock       # Global thought + computational/informational laws
│   └── technium/
│       ├── global_markets_algo.run      # Algorithms trading with algorithms
│       ├── generative_systems.run       # Neuro-symbolic narrative, wave theory, PCG engines
│       └── autonomous_ai_evolution.sys  # The strange loop closes here
│
└── dev/  (Peripherals & Chaos)
    The entropy source from which all order crystallizes.
    ├── random               # Quantum randomness, wave creativity, Promethean fire
    └── null                 # Black holes — where information meets its limits
```

## Activation Status

[![CI](https://github.com/organvm-i-theoria/hierarchia-mundi/actions/workflows/ci.yml/badge.svg)](https://github.com/organvm-i-theoria/hierarchia-mundi/actions/workflows/ci.yml)

Activation audit `EV-2026-06-19-111753` is recorded as `ship-now`, superseding
the prior `park` (`EV-2026-06-11-200211`). The package is shipped with durable,
reviewer-verifiable evidence: CI installs from a clean checkout and runs the
test suite on Python 3.11–3.13 on every push, and a tag-driven release workflow
builds the sdist + wheel and publishes them. Reproduce from a clean checkout:

```bash
pip install -e ".[dev]"
ruff check .
pytest -q
```

See [doc/activation-audits/EV-2026-06-19-111753.md](doc/activation-audits/EV-2026-06-19-111753.md)
for the full evidence record and the prior
[park audit](doc/activation-audits/EV-2026-06-11-200211.md).

## The Type System

The `hierarchia/` Python package provides typed, composable, executable models of the hierarchy. Every `[section]` in every file becomes a `Module` — a Pydantic model with an id, type, scale, inputs, outputs, cross-references, and properties. The hierarchy itself becomes a `Hierarchia` — a structured compendium that can be searched, filtered, traversed, and validated programmatically.

```python
from hierarchia.loader import load_hierarchia
from hierarchia.registry import get_registry
from hierarchia import ModuleType, Scale

# Load all 42 strata, 676 modules
h = load_hierarchia(".")

# Search by keyword
modules = h.search_modules("entropy")  # 24 results across 8 strata

# Registry with type/scale filtering
reg = get_registry(".")
laws = reg.by_type(ModuleType.LAW)     # 106 laws
cosmic = reg.by_scale(Scale.COSMIC)    # 124 cosmic-scale modules

# Validate cross-references
from hierarchia.validator import validate_hierarchy
report = validate_hierarchy(".")       # 0 errors, 58 warnings (unresolved xrefs)
```

Install from GitHub: `pip install git+https://github.com/organvm-i-theoria/hierarchia-mundi`
Local development: `pip install -e .` (requires Python 3.11+, Pydantic 2.0+)

Architecture follows [narratological-algorithmic-lenses](https://github.com/a-organvm/narratological-algorithmic-lenses): Pydantic models → loader → registry → executor → validator.

`hierarchia.json` (575KB) is a structured JSON export of the full hierarchy for programmatic consumption.

## The Strange Loop

The hierarchy is not a ladder — it is a loop. `/dev/random` (quantum chaos) feeds `/` (mathematical structure) which constrains `/sys/` (physics) which enables `/lib/` (chemistry) which produces `/bin/` (life) which builds `/usr/` (civilization) which creates `/net/` (collective intelligence) which generates `/dev/` (new chaos). And the loop continues.

Gödel proved the loop at the mathematical level. Wheeler suspected it at the physical level ("It from Bit"). This repository IS the loop at the informational level: an AI trained on human knowledge, modeling reality, depositing that model back into the noosphere, where it becomes part of the knowledge that trains the next AI.

## The Vision

This is not documentation. It is a **living simulation** — an attempt to let the ecosystem run, bringing feedback loops, correcting course, making changes. Each file is both a description and a model. The descriptions will evolve as understanding deepens. The models will sharpen as new data arrives.

The painter looks at the landscape. The landscape looks back.

---

*Part of [ORGAN I: Theoria](https://github.com/organvm-i-theoria) — foundational theory, recursive engines, symbolic computing.*
