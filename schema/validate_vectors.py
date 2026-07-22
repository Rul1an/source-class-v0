#!/usr/bin/env python3
"""Tie the JSON Schema to the vectors so the two cannot drift apart.

Every NATIVE record (schema == "source_class/v0") in vectors/cases.json is
validated against schema/source-class-record.schema.json, with one deliberate
expectation: the record whose verdict is `invalid` because its digest carries no
canonicalization id MUST be rejected by the schema, and every other native
record MUST pass. That is invariant 3 (a digest travels with its scheme id)
enforced in two independent places, the checker's rules and the schema.

Uses jsonschema, which is a CI-only dependency. The repo's own checker
(check.py) stays standard-library-only; this file is not imported by it.
"""

import json
import os
import sys

import jsonschema

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

schema = json.load(open(os.path.join(HERE, "source-class-record.schema.json")))
cases = json.load(open(os.path.join(ROOT, "vectors", "cases.json")))["cases"]
validator = jsonschema.Draft202012Validator(schema)

failures = []
checked = 0
for case in cases:
    record = case["record"]
    if record.get("schema") != "source_class/v0":
        continue  # dialect-shaped fragments are foreign; the schema is for native records
    checked += 1
    errors = list(validator.iter_errors(record))
    schema_rejects = len(errors) > 0
    # A native record should be rejected by the schema exactly when its verdict
    # is `invalid` for the digest reason. In this corpus that is the sole
    # structural-invalidity native case; every other native record must pass.
    should_reject = case["expected"]["verdict"] == "invalid"
    status = "ok" if schema_rejects == should_reject else "FAIL"
    if status == "FAIL":
        failures.append((case["name"], should_reject, schema_rejects, [e.message for e in errors]))
    print(f"  {status:4} {case['name']}: schema_rejects={schema_rejects} expected_reject={should_reject}")

print()
if failures:
    for name, should, got, msgs in failures:
        print(f"drift in {name}: expected_reject={should} schema_rejects={got} {msgs}")
    print(f"native records checked: {checked}, failures: {len(failures)}")
    sys.exit(1)
print(f"native records checked: {checked}, all consistent with the schema")
