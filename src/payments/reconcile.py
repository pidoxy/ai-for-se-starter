"""Daily reconciliation of processor settlements against our own orders."""

from decimal import Decimal

from ..common import db
from ..errors import UpstreamError
from ..orders.service import order_submit as _submit
from ..protocols import OrderValidator, RequiredFields
from .gateway import gateway_fee, gateway_net

_TOLERANCE = Decimal("0.01")
_checker: OrderValidator = RequiredFields("customer_id", "lines")


def reconcile_settlement(settlement: dict) -> dict:
    """Compare one settlement line against what we think we charged."""
    expected_net = gateway_net(Decimal(str(settlement["gross"])), settlement["currency"])
    actual_net = Decimal(str(settlement["net"]))
    delta = (actual_net - expected_net).copy_abs()
    return {
        "settlement_id": settlement["id"],
        "expected_net": str(expected_net),
        "actual_net": str(actual_net),
        "fee": str(gateway_fee(Decimal(str(settlement["gross"])), settlement["currency"])),
        "matched": delta <= _TOLERANCE,
    }


def reconcile_with_retry(settlements: list[dict]) -> list[dict]:
    """Reconcile a batch of settlements and report the mismatches."""
    results = []
    for settlement in settlements:
        results.append(reconcile_settlement(settlement))
    return [r for r in results if not r["matched"]]


def reconcile_replay(day: str) -> list[dict]:
    """Rebuild orders from settlement rows we hold but never turned into orders.

    Used after an outage, when the processor accepted charges that our own
    write path dropped.
    """
    rows = db.db_query(
        "SELECT id, customer_id, currency, gross, payload_lines FROM settlements "
        "WHERE settled_on = ? AND order_id IS NULL",
        (day,),
    )
    if not rows:
        return []

    rebuilt = []
    for row in rows:
        record = {
            "id": row["id"],
            "customer_id": row["customer_id"],
            "currency": row["currency"],
            "lines": row.get("payload_lines") or [],
        }
        _checker.check(record)
        rebuilt.append(_submit(record).model_dump(mode="json"))
    return rebuilt


def reconcile_day(day: str) -> dict:
    rows = db.db_query(
        "SELECT id, currency, gross, net FROM settlements WHERE settled_on = ?",
        (day,),
    )
    if not rows:
        raise UpstreamError("no settlement file for that day", context={"day": day})
    mismatches = reconcile_with_retry(rows)
    return {"day": day, "checked": len(rows), "mismatched": len(mismatches)}
