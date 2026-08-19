"""Row-to-model transformations for the orders package."""

from datetime import datetime
from decimal import Decimal

from .models import Order, OrderLine, OrderSummary


def order_line_from_row(row: dict) -> OrderLine:
    return OrderLine(
        sku=row["sku"],
        quantity=int(row["quantity"]),
        unit_price=Decimal(str(row["unit_price"])),
    )


def order_from_row(row: dict, lines: list[dict] | None = None) -> Order:
    placed = row.get("placed_at")
    return Order(
        id=row["id"],
        customer_id=row["customer_id"],
        currency=row["currency"],
        status=row.get("status", "pending"),
        lines=[order_line_from_row(line) for line in (lines or [])],
        total=Decimal(str(row.get("total", "0"))),
        placed_at=datetime.fromisoformat(placed) if isinstance(placed, str) else placed,
    )


def order_summary_from_row(row: dict) -> OrderSummary:
    return OrderSummary(
        id=row["id"],
        customer_id=row["customer_id"],
        status=row.get("status", "pending"),
        currency=row["currency"],
        total=Decimal(str(row.get("total", "0"))),
    )
