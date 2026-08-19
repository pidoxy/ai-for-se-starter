# AGENTS.md — team rules

| | |
|---|---|
| **Owner** | Platform guild (`#guild-platform`) |
| **Last reviewed** | 2026-07-14 |
| **Review cadence** | Quarterly, and after any incident this file could have prevented |
| **Change process** | PR against this file, one guild reviewer, link the incident or the ADR that motivated the change |

## Why this file exists

This file is not a style guide, and it is not a substitute for `docs/`. It is
the set of things an assistant gets wrong in *this* repository because the
common answer elsewhere is a different answer here. Every rule below earned its
place by being violated in a real pull request.

If you are new: read this once, then read `docs/adr/`. The ADRs tell you why
the rules exist, which is what lets you recognise the cases where a rule
genuinely does not apply. A rule you cannot argue against is a rule you cannot
apply well.

If you find yourself fighting a rule, that is a signal to change the rule, not
to quietly work around it. Open a PR. The change process is one reviewer and a
link to the reason.

## Rules

Everything in `AGENTS.personal.md` applies. The rules below are the ones the
guild owns, and they are not overridable by a personal file.

### Never import `src/payments_legacy/`

Its function and class names are identical to `src/payments/`. An import looks
correct in review and silently applies the 2021 fee rate with the wrong
rounding. *Incident 2024-11-02.*

### Money is `Decimal`, never `float`

Quantise once, `ROUND_HALF_UP`, at the point a value becomes a total. *ADR 0001.*

### Raise `AppError` subclasses; never return `None` for "not found"

Never write an `except` that swallows and returns `None`. *ADR 0003.*

### Anything touching auth, payments, or user data needs a second reviewer

Regardless of diff size, and regardless of who wrote it. *See the PR template.*

### AI-assisted changes are declared, not hidden

Declaring costs you nothing. The declaration tells the reviewer where to look
first, and it is the only reason we can tell whether these rules are working.
