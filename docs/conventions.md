# Conventions

House rules for this service. If something here disagrees with a tutorial you
found online, this file wins.

## Layout

- `src/<package>/models.py` — pydantic models only. No I/O, no business rules.
- `src/<package>/service.py` — business rules. The only place decisions live.
- `src/<package>/router.py` — HTTP only. Parse, delegate, shape the response.
- `src/common/` — things more than one package needs. Nothing domain-specific.
- `src/errors.py` — the error hierarchy. See ADR 0003.

Routers stay thin. If a router has an `if` statement that is not error mapping,
it is doing something that belongs in a service.

## Errors

Every failure that crosses a module boundary is raised as a subclass of
`AppError`. We do not return `None` to mean "not found", and we do not return
`(result, error)` tuples. `AppError` itself is never raised directly.

Routers translate errors into HTTP status codes. Services never import
`fastapi`.

## Money

Money is `Decimal`, everywhere, always. Never `float`. Amounts are quantised to
the minor unit with `ROUND_HALF_UP` at the point they become a total, and not
before. If you see a `float` anywhere near a currency amount, that is a bug
whether or not a test catches it.

Currency codes are upper-case ISO 4217 strings.

## Return types

Services return pydantic models, never bare dicts. If a caller needs a dict,
it calls `.model_dump()` itself — the service does not decide that for it.

## Logging

Use the `logging` module. Never `print`. Log lines are lower case and do not
end in a full stop. Never log a value that came from `settings` without
passing it through `settings_redacted` first.

## Tests

`pytest`, no classes, one behaviour per test. Test names read as sentences:
`test_search_rejects_a_long_country_code`, not `test_search_2`.

Fixtures live in `tests/conftest.py`. Tests never touch a real database.

## Style

- Line length 100.
- Type hints on every public function.
- Docstrings on public functions; one line unless the behaviour is surprising.
- Imports: standard library, third party, local — separated by blank lines.
