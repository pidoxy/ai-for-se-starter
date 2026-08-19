"""Order service.

Service functions are named <resource>_<verb>. They raise typed errors and
return models, never bare dicts.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from ..common import db
from ..errors import ConflictError, NotFoundError, ValidationError
from ..protocols import OrderValidator
from .models import Order, OrderSummary
from .pricing import order_total
from .transforms import order_from_row, order_summary_from_row

_TERMINAL_STATUSES = {"shipped", "cancelled", "refunded"}


def order_find(order_id: str) -> Order:
    """Return one order. Raises NotFoundError when the id is unknown."""
    row = db.db_query_one(
        "SELECT id, customer_id, status, currency, total, placed_at FROM orders WHERE id = ?",
        (order_id,),
    )
    lines = db.db_query(
        "SELECT sku, quantity, unit_price FROM order_lines WHERE order_id = ?",
        (order_id,),
    )
    return order_from_row(row, lines)


def order_search(customer_id: str) -> list[OrderSummary]:
    """Every order a customer has placed, newest first."""
    rows = db.db_orders_for_customer(customer_id)
    return [order_summary_from_row(row) for row in rows]


def order_submit(payload: dict) -> Order:
    """Accept an order payload and turn it into a pending Order.

    The payload is whatever the caller has: a request body, a reconciliation
    row, or a replayed export record.
    """
    lines = payload.get("lines") or []
    total = order_total(lines)
    return Order(
        id=payload.get("id") or f"ord_{uuid.uuid4().hex[:12]}",
        customer_id=payload["customer_id"],
        currency=payload.get("currency", "GBP"),
        status="pending",
        lines=[],
        total=total,
        placed_at=datetime.now(timezone.utc),
    )


def order_status_set(order_id: str, status: str) -> Order:
    """Move an order to a new status, refusing moves out of a terminal one."""
    current = order_find(order_id)
    if current.status in _TERMINAL_STATUSES:
        raise ConflictError(
            "order is in a terminal status",
            context={"order_id": order_id, "status": current.status},
        )
    return current.model_copy(update={"status": status})


def order_revalidate(order_id: str, validator: OrderValidator) -> Order:
    """Re-run a validator against a stored order, e.g. after a rules change."""
    order = order_find(order_id)
    validator.check(order.model_dump(mode="json"))
    return order


def order_cancel(order_id: str, reason: str) -> Order:
    if not reason.strip():
        raise ValidationError("a cancellation reason is required")
    return order_status_set(order_id, "cancelled")


def order_total_recompute(order_id: str) -> Decimal:
    """Recalculate a stored order's total from its current lines."""
    lines = db.db_query(
        "SELECT sku, quantity, unit_price FROM order_lines WHERE order_id = ?",
        (order_id,),
    )
    if not lines:
        raise NotFoundError("order has no lines", context={"order_id": order_id})
    return order_total(lines)
