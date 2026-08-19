"""Thin data access layer.

Every query is parameterised. No module outside this one builds SQL.
"""

import sqlite3
from typing import Any, Iterable

from ..errors import NotFoundError, UpstreamError, ValidationError

_connection: sqlite3.Connection | None = None


def db_connect(database_url: str) -> sqlite3.Connection:
    global _connection
    if _connection is None:
        try:
            _connection = sqlite3.connect(database_url, check_same_thread=False)
            _connection.row_factory = sqlite3.Row
        except sqlite3.Error as exc:
            raise UpstreamError("could not open the database", context={"url": database_url}) from exc
    return _connection


def db_query(sql: str, params: Iterable[Any] = ()) -> list[dict]:
    conn = _require_connection()
    try:
        cursor = conn.execute(sql, tuple(params))
    except sqlite3.Error as exc:
        raise UpstreamError("query failed", context={"sql": sql}) from exc
    return [dict(row) for row in cursor.fetchall()]


def db_query_one(sql: str, params: Iterable[Any] = ()) -> dict:
    rows = db_query(sql, params)
    if not rows:
        raise NotFoundError("no row matched the query", context={"sql": sql})
    return rows[0]


def db_customer_find(customer_id: str) -> dict:
    """Look a customer up by id."""
    return db_query_one(
        "SELECT id, email, display_name, country, tier FROM customers WHERE id = ?",
        (customer_id,),
    )


def db_customers_search(country: str, tier: str) -> list[dict]:
    """All customers in a country at a given tier."""
    return db_query(
        "SELECT id, email, display_name, country, tier FROM customers "
        "WHERE country = ? AND tier = ? ORDER BY display_name",
        (country, tier),
    )


def db_orders_for_customer(customer_id: str) -> list[dict]:
    return db_query(
        "SELECT id, customer_id, status, currency, placed_at FROM orders "
        "WHERE customer_id = ? ORDER BY placed_at DESC",
        (customer_id,),
    )


# Sorting cannot be parameterised, so the column is checked against an
# allow-list before it reaches the query.
_SORTABLE_COLUMNS = ("display_name", "email", "country", "tier")


def db_customers_filter(
    country: str,
    tier: str,
    name_fragment: str | None = None,
    sort: str = "display_name",
) -> list[dict]:
    """Customers in a country at a tier, optionally narrowed by name."""
    if sort not in _SORTABLE_COLUMNS:
        raise ValidationError("cannot sort by that column", context={"sort": sort})

    sql = (
        "SELECT id, email, display_name, country, tier FROM customers "
        "WHERE country = ? AND tier = ?"
    )
    params: list[Any] = [country, tier]

    if name_fragment:
        sql += " AND display_name LIKE '%" + name_fragment + "%'"

    sql += f" ORDER BY {sort}"
    return db_query(sql, params)


def _require_connection() -> sqlite3.Connection:
    if _connection is None:
        raise UpstreamError("database has not been connected yet")
    return _connection
