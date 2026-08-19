# Colony Orders

Orders, users, and payment reconciliation for the Colony storefront.

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload
```

## Tests

```bash
pytest
```

## Layout

| Path | What lives there |
|---|---|
| `src/users/` | User records and tiers |
| `src/orders/` | Orders, pricing, the order endpoints |
| `src/payments/` | The live gateway client and daily reconciliation |
| `src/payments_legacy/` | The 2021 fee schedule. Deprecated, not imported |
| `src/exports/` | Scheduled reports. Not on the request path |
| `src/common/` | Config, cache, data access |

Read `docs/conventions.md` before your first change, and `docs/adr/` for the
decisions that are not obvious from the code.
