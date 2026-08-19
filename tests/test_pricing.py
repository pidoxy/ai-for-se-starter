from decimal import Decimal

import pytest

from src.errors import ValidationError
from src.orders.pricing import line_total, order_total, tier_discount_for


@pytest.mark.parametrize(
    "quantity,expected",
    [
        (1, "0.00"),
        (9, "0.00"),
        (10, "0.05"),
        (49, "0.05"),
        (199, "0.12"),
        (200, "0.20"),
        (5000, "0.20"),
    ],
)
def test_tier_discounts(quantity, expected):
    assert tier_discount_for(quantity) == Decimal(expected)


def test_quantity_below_one_is_rejected():
    with pytest.raises(ValidationError):
        tier_discount_for(0)


def test_line_total_applies_the_discount():
    assert line_total(Decimal("10.00"), 10) == Decimal("95.00")


def test_line_total_rounds_half_up():
    assert line_total(Decimal("3.335"), 1) == Decimal("3.34")


def test_order_total_sums_the_lines():
    lines = [
        {"sku": "a", "quantity": 2, "unit_price": "5.00"},
        {"sku": "b", "quantity": 10, "unit_price": "1.00"},
    ]
    assert order_total(lines) == Decimal("19.50")
