#!/usr/bin/env python3
"""Recompute the source-class verdicts for every vector and print the corpus digest.

Standard library only. No network. Exit 0 means every case reproduced its
expected verdict; exit 1 names the first divergence.

Canonicalization: jcs/rfc8785 under the corpus value profile: no floats,
integers within +/-2^53, strings and object keys confined to the Basic
Multilingual Plane (this corpus is ASCII-only and number-free). For that
profile, UTF-8 serialization with sorted keys and no whitespace is byte-equal
to RFC 8785 output. Outside it the two diverge: RFC 8785 sorts keys by UTF-16
code units (differs from code-point order when a non-BMP key meets one in
U+E000..U+FFFF) and renders numbers as IEEE doubles (loses integers above
2^53), so extend the serializer before admitting either. The self-test below
checks the serializer against hand-checked JCS byte strings before any digest
is trusted.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def canonical_bytes(value):
    """Canonical JSON bytes for the corpus value profile (subset of RFC 8785)."""
    if isinstance(value, float):
        raise ValueError("value profile excludes floats; extend to full JCS number serialization before adding any")
    if isinstance(value, dict):
        for k in value:
            if not isinstance(k, str):
                raise ValueError("object keys must be strings")
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def self_test_canonicalization():
    checks = [
        ({"b": 1, "a": "x"}, b'{"a":"x","b":1}'),
        ({"nested": {"z": True, "a": None}}, b'{"nested":{"a":null,"z":true}}'),
        ({"unicode": "é"}, '{"unicode":"é"}'.encode("utf-8")),
        ([1, "two", False], b'[1,"two",false]'),
    ]
    for value, expected in checks:
        got = canonical_bytes(value)
        if got != expected:
            raise AssertionError(f"canonicalization self-test failed: {got!r} != {expected!r}")


def digests_missing_scheme_id(record):
    """True if any digest object in the record lacks its canonicalization id."""
    if isinstance(record, dict):
        if "digest" in record and "canonicalization" not in record:
            return True
        return any(digests_missing_scheme_id(v) for v in record.values())
    if isinstance(record, list):
        return any(digests_missing_scheme_id(v) for v in record)
    return False


def evaluate(record, axis_values):
    """Map one record fragment onto the axis. Deterministic, no dialect table needed:
    the rules below are the whole contract.

    1. A digest without its canonicalization id is invalid, whatever else the
       record says. Two readers with different implicit canonicalizations derive
       different bytes for the same record and cannot tell whose reading was meant.
    2. A recognized source_class is a declared basis; the value "unknown" is a
       declared unknown, which is a statement, not an absence.
    3. An unrecognized source_class folds to unknown, fail-closed.
    4. vaara-shaped records: enforcement_logic_basis is the basis-equivalent
       field; "not_established" is a declared unknown carried in the producer's
       own vocabulary.
    5. Everything else is undeclared. Time anchors, precedence claims, source
       freshness, and untyped extension dicts do not change that: they raise
       tamper-evidence or recomputability, never vantage.
    """
    if digests_missing_scheme_id(record):
        return {"verdict": "invalid", "basis": None}

    if "source_class" in record:
        value = record["source_class"]
        if value == "unknown":
            return {"verdict": "declared_unknown", "basis": "unknown"}
        if value in axis_values:
            return {"verdict": "declared", "basis": value}
        return {"verdict": "declared_unknown", "basis": "unknown"}

    if record.get("enforcement_logic_basis") == "not_established":
        return {"verdict": "declared_unknown", "basis": "unknown"}

    return {"verdict": "undeclared", "basis": None}


def main():
    self_test_canonicalization()

    axis = json.loads((ROOT / "map" / "axis.json").read_text(encoding="utf-8"))
    dialects = json.loads((ROOT / "map" / "dialects.json").read_text(encoding="utf-8"))
    vectors = json.loads((ROOT / "vectors" / "cases.json").read_text(encoding="utf-8"))

    axis_values = set(axis["values"].keys())

    failures = []
    for case in vectors["cases"]:
        got = evaluate(case["record"], axis_values)
        expected = {"verdict": case["expected"]["verdict"], "basis": case["expected"]["basis"]}
        status = "ok" if got == expected else "FAIL"
        if status == "FAIL":
            failures.append((case["name"], expected, got))
        print(f"  {status:4} {case['name']}: {got['verdict']}" + (f" ({got['basis']})" if got["basis"] else ""))

    corpus = hashlib.sha256(
        canonical_bytes(axis) + canonical_bytes(dialects) + canonical_bytes(vectors)
    ).hexdigest()

    print()
    if failures:
        for name, expected, got in failures:
            print(f"divergence in {name}: expected {expected}, got {got}")
        print(f"cases passed: {len(vectors['cases']) - len(failures)}/{len(vectors['cases'])}")
        return 1
    print(f"cases passed: {len(vectors['cases'])}/{len(vectors['cases'])}")
    print(f"corpus sha256 (jcs/rfc8785, corpus value profile): {corpus}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
