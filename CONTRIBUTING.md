# Contributing

This repository is a vocabulary and a set of worked mappings, not a standard. It
gets better when the people whose work it maps hold the pen on their own rows.

## Correcting or authoring a dialect row

The entries in [`map/dialects.json`](map/dialects.json) are one reader's mapping
of published vocabularies onto the source-class axis. That is a starting point,
not an authority. If a row describes your project:

- **Corrections are welcome and take precedence.** If the row misreads what your
  vocabulary types or what it cannot express, open an issue or a PR and it will
  be fixed to your wording. You know your design better than a mapping of it does.
- **Self-authored rows are welcome.** If you would rather write your own row than
  correct mine, send it. The `credit` field is yours to phrase or drop.
- **New dialects are welcome.** If another vocabulary types a fragment of the
  axis and is not here, a row for it is a good addition, with the same credit
  discipline.

The mapping is a statement about expressiveness, never a grade. A row that reads
as a ranking of one project against another is a bug; say so.

## Correcting the axis itself

The seven values and five invariants in [`map/axis.json`](map/axis.json) are v0.
If a real record does not fit any value, or an invariant is wrong, that is worth
an issue. The unit that matters is the axis and the invariants, not this
implementation; the checker is deliberately small enough to rewrite from its
docstring.

## Vectors

A new vector should be minimal, carry the verdict a conforming reader must
reproduce, and keep [`check.py`](check.py) at a clean pass. Run it before opening
the PR:

```bash
python3 check.py
```

If a vector needs a record shape the current checker cannot read, that is a
finding about the axis, not a reason to grow the checker past what one file can
hold. Note it in the PR and we will decide together.

## What this is not

No adoption is asked of anyone. Carrying the axis in a record is one option among
many, and declaring `unknown` is a first-class, conforming choice. Nothing here
needs a blessing from a standards body, and none has been sought.
