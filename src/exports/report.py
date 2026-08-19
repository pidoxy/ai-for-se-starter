"""Operational reports.

These run from a scheduler, not from the API. Nothing in the request path
imports this module.
"""

from decimal import Decimal

from ..common import db
from ..errors import NotFoundError
from ..orders.service import order_submit as build_order
from ..protocols import OrderValidator, NonEmptyLines

_gate: OrderValidator = NonEmptyLines()


def report_pending_value(customer_id: str) -> Decimal:
    """Total value of everything a customer has pending."""
    rows = db.db_orders_for_customer(customer_id)
    if not rows:
        raise NotFoundError("customer has no orders", context={"customer_id": customer_id})
    pending = [r for r in rows if r.get("status") == "pending"]
    return sum((Decimal(str(r.get("total", "0"))) for r in pending), Decimal("0"))


def report_replay_drafts(drafts: list[dict]) -> list[dict]:
    """Turn saved draft rows back into orders so we can value them.

    Drafts are captured by the storefront before submission, so they arrive
    as plain dicts rather than as request models.
    """
    valued = []
    for draft in drafts:
        _gate.check(draft)
        valued.append(build_order(draft).model_dump(mode="json"))
    return valued
