# 0001 — Money is Decimal

**Status:** accepted · **Date:** 2024-02-11

## Context

An early rounding defect under-charged 2,300 orders by between one and four
pence each. The cause was a `float` intermediate in the discount calculation:
`0.1 + 0.2` is not `0.3`, and the error compounded across lines before we
quantised.

The defect survived review because the code looked correct, and it survived
the test suite because every fixture used values that happen to be exactly
representable in binary floating point.

## Decision

Money is `decimal.Decimal` from the moment it enters the system to the moment
it leaves. Quantisation to the minor unit happens once, with `ROUND_HALF_UP`,
at the point a value becomes a total.

Prices arriving as JSON strings stay strings until they become `Decimal`. They
are never passed through `float()`.

## Consequences

Serialisation is slightly more verbose: amounts cross the wire as strings, and
clients must not parse them into a binary float either. This is documented in
`docs/api.md`.

Comparisons need care. `Decimal("1.0") == Decimal("1.00")` is true, but their
string forms differ, so tests assert on `Decimal`, not on `str`.
