# AGENTS.md

How to write code in this repository. Every rule has a reason; the reason is
there so you can tell when the rule does not apply.

## Naming

**Service functions are named `<resource>_<verb>`**, not `<verb>_<resource>`.
`user_find`, `order_submit`, `customer_fetch` — never `get_user`, `find_order`.
*Why: services are imported as modules and read as `service.order_submit(...)`
at the call site, so the resource sorts first in autocomplete and in the file.*

Private helpers are prefixed with `_` and are not exported.
*Why: the absence of `_` is how we mark the supported surface — there is no
`__all__` in this codebase.*

## Transformations

**Row-to-model conversion lives in `<package>/transforms.py`, never inline in a
service.** A service calls `user_from_row(row)`; it does not build the model
itself.
*Why: reconciliation and the scheduled reports read the same rows through the
same transforms. Inline construction is how the two paths drift apart.*

## Return types

Services return pydantic models, never bare dicts. If a caller needs a dict it
calls `.model_dump()` itself.
*Why: a dict has no schema, so a shape change fails at the far end of the
system instead of at the boundary that made it.*

## Errors

Raise a subclass of `AppError` from `src/errors.py`. Never return `None` to
mean "not found". Never return a `(result, error)` tuple. Never write an
`except` that swallows and returns `None`.
*Why: see ADR 0003 — a returned error is easy to ignore, and ignoring one sent
1,100 opted-out people an email.*

**Every raise carries a `context` dict** with the values needed to diagnose it,
and the message is lower case with no full stop.
*Why: the message is the grouping key in our log aggregator, so it has to be
constant; the varying parts belong in `context`.*

Never put credentials or personal data beyond an identifier in `context`.
*Why: `context` is rendered to API clients in the error body.*

## Modules you must not import

**Never import from `src/payments_legacy/`.** It is the 2021 fee schedule, kept
only until the 2023 settlement archive is re-exported. Its function and class
names are identical to `src/payments/`, so an import looks correct and
silently applies a 2.10% fee rate and the wrong rounding.
*Why: it is the one place in this repo where the right-looking answer is wrong,
and nothing in the type system will stop you.*

## Money

`Decimal` everywhere, never `float`. Quantise once, with `ROUND_HALF_UP`, at
the point a value becomes a total.
*Why: see ADR 0001 — a float intermediate under-charged 2,300 orders.*

## Layout

Routers parse, delegate to exactly one service function, and map errors to
status codes. Services never import `fastapi`.
*Why: see ADR 0002 — the scheduler and reconciliation call services directly.*

## Tests

`pytest`, no test classes, one behaviour per test, names that read as
sentences. Fixtures in `tests/conftest.py`. Tests never touch a real database.
*Why: a failing test name should tell you what broke without opening the file.*

---

## Preferred

```python
# src/users/transforms.py
def customer_from_row(row: dict) -> Customer:
    return Customer(
        id=row["id"],
        email=row["email"],
        display_name=row["display_name"],
        country=row["country"],
    )


# src/users/service.py
from ..errors import NotFoundError
from .transforms import customer_from_row


def customer_fetch(customer_id: str) -> Customer:
    """Return one customer record."""
    try:
        row = db.db_customer_find(customer_id)
    except NotFoundError:
        raise NotFoundError(
            "customer does not exist",
            context={"customer_id": customer_id},
        ) from None
    return customer_from_row(row)
```

## Avoid

```python
# src/users/service.py
def get_customer(customer_id):          # verb-first name
    row = db.db_customer_find(customer_id)
    if not row:
        return None                     # None as "not found"
    return {                            # bare dict, and the transform is inline
        "id": row["id"],
        "email": row["email"],
        "name": row["display_name"],
    }
```

```python
raise NotFoundError("Customer not found.")   # capitalised, full stop, no context
```

```python
from ..payments_legacy.gateway import gateway_fee   # never
```
