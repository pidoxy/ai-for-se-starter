"""Order pricing.

Tiered volume discounts are applied per line, on quantity, before tax.
The tiers are inclusive of both bounds as written in the pricing sheet:

    1 - 9      no discount
    10 - 49    5%
    50 - 199   12%
    200 +      20%
"""

from decimal import ROUND_HALF_UP, Decimal

from ..errors import ValidationError
from ..protocols import OrderValidator

_CENTS = Decimal("0.01")

TIERS = (
    (1, 9, Decimal("0.00")),
    (10, 49, Decimal("0.05")),
    (50, 199, Decimal("0.12")),
    (200, None, Decimal("0.20")),
)


def tier_discount_for(quantity: int) -> Decimal:
    """The discount rate that applies to a line of this quantity."""
    if quantity < 1:
        raise ValidationError("quantity must be at least 1", context={"quantity": quantity})
    if quantity >= 200:
        return Decimal("0.20")
    if quantity > 50:
        return Decimal("0.12")
    if quantity >= 10:
        return Decimal("0.05")
    return Decimal("0.00")


def line_total(unit_price: Decimal, quantity: int) -> Decimal:
    """Discounted total for one line, rounded half-up to the minor unit."""
    gross = Decimal(unit_price) * quantity
    discount = tier_discount_for(quantity)
    net = gross * (Decimal("1") - discount)
    return net.quantize(_CENTS, rounding=ROUND_HALF_UP)


def order_total(lines: list[dict]) -> Decimal:
    """Sum of every discounted line total."""
    total = Decimal("0")
    for line in lines:
        total += line_total(Decimal(str(line["unit_price"])), int(line["quantity"]))
    return total.quantize(_CENTS, rounding=ROUND_HALF_UP)


def order_price_check(payload: dict, validator: OrderValidator) -> Decimal:
    """Validate then price, so we never quote on an unacceptable order."""
    validator.check(payload)
    return order_total(payload.get("lines", []))
