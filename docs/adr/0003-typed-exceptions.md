# 0003 — Typed exceptions, not error returns

**Status:** accepted · **Date:** 2024-06-19

## Context

We used two error conventions at once. Some functions returned `None` to mean
"not found"; others returned a `(result, error)` tuple. Both are common
patterns and both are defensible, but holding both meant every call site had
to know which one it was talking to.

The failure that forced this decision: a service returned `None` for a missing
customer, the caller treated `None` as "no marketing preferences set", and
1,100 people received an email they had opted out of.

A returned error is easy to ignore. `None` is especially easy to ignore,
because it is also a legitimate value in half the places it appears.

## Decision

Every failure that crosses a module boundary is raised as a subclass of
`AppError`, defined in `src/errors.py`:

- `NotFoundError` — the entity does not exist
- `ValidationError` — input failed a business rule or a shape check
- `UpstreamError` — a dependency we do not own failed
- `ConflictError` — well-formed request, incompatible with current state

`AppError` is never raised directly; it exists so that one handler can catch
the whole family.

Errors carry a `context` dict. It is for values that make the log line
diagnosable, and it is rendered to API clients, so it never contains
credentials or personal data beyond an identifier.

## Consequences

Callers that genuinely want a soft failure write the `try`/`except`
themselves, at the call site, where the decision is visible in review.

An `except AppError` that returns `None` re-introduces exactly the problem
this ADR removed. Treat one in review as a defect, not a style preference.

Third-party exceptions are wrapped at the boundary — `sqlite3.Error` becomes
`UpstreamError` in `src/common/db.py`, and does not escape that module.
