# AGENTS.md

Instructions for coding agents working in or reading this repository. The
human overview is [README.md](README.md); this file is the machine-oriented
entry point.

## What this is

A vocabulary and a set of worked mappings, not a standard and not a product.
One axis, `source_class`, types what an outcome claim in agent evidence rests
on (producer-reported, issuer-attested, receiver-receipt, boundary-observed,
third-party-observed, independently-observed, or a typed `unknown`). The repo
carries the axis, a mapping of several 2026 vocabularies onto it, ten vectors,
a dependency-free checker, and a JSON Schema.

## Layout

- `map/axis.json`: the seven values, the invariants, the canonicalization declaration.
- `map/dialects.json`: the mapping of external vocabularies onto the axis, with credit.
- `vectors/cases.json`: records plus the verdict a conforming reader must reproduce.
- `check.py`: the reader. Standard library only, no network, deterministic.
- `schema/source-class-record.schema.json`: JSON Schema (2020-12) for a native record.
- `schema/validate_vectors.py`: ties the schema to the vectors (CI, needs `jsonschema`).

## Run it

```bash
python3 check.py
```

Exit 0 means every vector reproduced its verdict; the last line prints the
corpus digest, a SHA-256 over the canonical bytes of the three JSON files.
The checker self-tests its canonicalizer against hand-checked JCS byte strings
before trusting any digest. No install step, no dependencies.

The schema-to-vectors consistency check needs `jsonschema` (CI-only):

```bash
pip install "jsonschema>=4.22,<5" && python3 schema/validate_vectors.py
```

## The invariants a change must not break

1. A declared `unknown` is distinct from an undeclared basis. The two verdicts differ on purpose.
2. Tamper-evidence never raises vantage. Signatures, hash chains, and external time anchors bound whether bytes changed, not who could have been wrong about the fact.
3. A digest travels with its canonicalization id. The checker and the JSON Schema both reject a digest without its scheme id; keep them in agreement.
4. No value dominates. The axis types facts, it does not rank them; a change that reads as ranking one basis above another is a defect.
5. Unrecognized `source_class` values fold to `unknown`, fail-closed, rather than erroring.

## Editing conventions

- Keep `check.py` standard-library-only and small enough to rewrite from its docstring. New dependencies belong in CI, not the checker.
- A new vector is minimal and carries the verdict a conforming reader must reproduce. Run `check.py` to a clean pass before committing.
- Dialect rows are the mapped project's to correct or author; see [CONTRIBUTING.md](CONTRIBUTING.md). A row that grades rather than describes is a bug.
- The corpus digest changes whenever the three JSON files change. Update the value quoted in `README.md` to match `check.py` output in the same change.

## What not to add

No adoption ask, no positioning, no comparison of the mapped projects against
each other. Carrying the axis in a record is one option among many, and
declaring `unknown` is a first-class, conforming choice.
