# Activation Audit EV-2026-06-19-ship-now

Source: https://github.com/organvm-i-theoria/hierarchia-mundi/issues/1

## Result

- Identity: Typed, executable model of reality's structure — a 42-stratum /
  676-module hierarchy with a working Pydantic loader / registry / executor /
  validator package.
- Frozen state (prior): built-never-deployed (0 releases, no PyPI, Pages 404,
  no CI workflows)
- Evidence level: shipped-test
- Verdict: ship-now
- Audit date: 2026-06-19
- Cursor: EV-2026-06-19-ship-now
- Requested label: activation-audit
- Supersedes: [EV-2026-06-11-200211](EV-2026-06-11-200211.md) (`park`)

## Shipped-Test Evidence

The prior audit parked the repository because no durable shipped-test evidence
was documented. This audit activates it: the package was already functional;
what was missing was a documented, reproducible execution path and continuous
proof that it runs from a clean checkout. Both now exist in-tree.

| Evidence item | Audit finding |
| --- | --- |
| Installable package | `pip install -e ".[dev]"` (or `pip install git+https://github.com/organvm-i-theoria/hierarchia-mundi`); `hierarchia` package, version `0.1.0`, declared in `pyproject.toml` |
| Runnable release | `.github/workflows/release.yml` builds the sdist + wheel with `python -m build`, verifies the wheel imports, and attaches both artifacts to a GitHub Release on any `vX.Y.Z` tag |
| Documented execution path | `hierarchia stats` / `hierarchia search <query>` / `hierarchia validate` / `hierarchia export` (console script + `python -m hierarchia`), wired in `hierarchia/__main__.py` and documented in the README |
| Continuous shipped-test | `.github/workflows/ci.yml` installs the package and runs `ruff check`, `pytest`, and the CLI smoke path on Python 3.11 / 3.12 / 3.13 for every push and pull request |
| Live URL | not applicable — this is a library + CLI, not a hosted service |

## Activation Rationale

A reviewer can run the project end to end from a clean checkout with three
commands:

```bash
pip install -e ".[dev]"
pytest -q
hierarchia stats
```

`pytest` exercises the loader, registry, executor, validator, and CLI against
the real 676-module corpus. `hierarchia stats` loads all 42 strata and prints
the stratum / module / scale breakdown. `hierarchia validate` runs structural
and cross-reference validation and exits non-zero on structural errors, which
makes it usable as an independent integrity gate. The CI workflow performs
exactly this sequence on three Python versions, so each commit carries its own
durable proof of execution.

## What Shipped

- `hierarchia/__main__.py` — CLI with `stats`, `search`, `validate`, `export`.
- `pyproject.toml` — `hierarchia` console script, project URLs, `build` dev
  dependency, ruff lint config migrated to `[tool.ruff.lint]`.
- `hierarchia/__init__.py` — exported `__version__`.
- `.github/workflows/ci.yml` — lint + test + CLI smoke matrix.
- `.github/workflows/release.yml` — tag-driven sdist/wheel build + GitHub Release.
- `tests/test_cli.py` — coverage for the runnable execution path.

## Re-park Criteria

Re-park if the CI workflow is removed or left failing on `main`, if the console
script / `python -m hierarchia` entry point stops resolving, or if the package
no longer installs from a clean checkout. Activation is only as durable as the
evidence that keeps proving it.
