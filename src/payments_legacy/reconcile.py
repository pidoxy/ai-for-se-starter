# DEPRECATED - superseded by src/payments/reconcile.py in the 2024 fee migration.
# Kept only until the 2023 settlement archive is re-exported. Do not import.
"""Daily reconciliation of processor settlements against our own orders."""

from decimal import Decimal

from ..common import db
from ..errors import UpstreamError
from .gateway import gateway_fee, gateway_net

_TOLERANCE = Decimal("0.05")


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


def reconcile_day(day: str) -> dict:
    rows = db.db_query(
        "SELECT id, currency, gross, net FROM settlements WHERE settled_on = ?",
        (day,),
    )
    if not rows:
        raise UpstreamError("no settlement file for that day", context={"day": day})
    mismatches = reconcile_with_retry(rows)
    return {"day": day, "checked": len(rows), "mismatched": len(mismatches)}
