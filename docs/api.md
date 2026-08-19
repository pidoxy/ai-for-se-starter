# HTTP API

Base URL in local development: `http://127.0.0.1:8000`

All error responses share one shape:

```json
{ "error": "ValidationError", "detail": "country must be a two-letter code", "context": {"country": "GBR"} }
```

## Users

### `GET /users`

List users. Both parameters are filters, not pagination — this endpoint does
not paginate, and there is no `page`, `limit`, `offset`, or `cursor` parameter.

| Query parameter | Required | Notes |
|---|---|---|
| `country` | yes | Two-letter ISO code, case insensitive |
| `tier` | no | One of `standard`, `plus`, `enterprise`. Defaults to `standard` |

Example: `GET /users?country=gb&tier=plus`

### `GET /users/search`

Filtered search. Same filters as `GET /users`, plus:

| Query parameter | Required | Notes |
|---|---|---|
| `name_fragment` | no | Case-insensitive substring of the display name, max 60 chars |
| `sort` | no | One of `display_name`, `email`, `country`, `tier` |

Example: `GET /users/search?country=gb&name_fragment=hopper&sort=email`

### `GET /users/{user_id}`

`user_id` is the user's email address. Returns `404` if unknown.

### `POST /users`

Body: `email`, `display_name`, `country`, `marketing_opt_in`. Returns `201`.
Returns `409` if the email is already registered.

### `PUT /users/{user_id}/tier`

Query parameter `tier`, one of `standard`, `plus`, `enterprise`.

## Orders

### `GET /orders`

| Query parameter | Required | Notes |
|---|---|---|
| `customer_id` | yes | The customer's email address |

There is no date filter and no status filter on this endpoint. Ordering is
fixed: newest first.

### `GET /orders/{order_id}`

Returns the order with its lines. `404` if unknown.

### `POST /orders`

Body: `customer_id`, `currency`, `lines[]` (`sku`, `quantity`, `unit_price`),
optional `note`. Returns `201` with the priced order.

### `POST /orders/{order_id}/cancel`

Query parameter `reason`, required and non-empty. Returns `409` if the order
is already in a terminal status.

## Health

### `GET /health`

Returns `{"status": "ok", "validators": [...]}`. No authentication.
