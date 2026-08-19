from decimal import Decimal

import pytest

from src.errors import ValidationError
from src.orders.models import OrderCreate, OrderLine
from src.orders.service import order_search
from src.orders.transforms import order_summary_from_row
from src.protocols import NonEmptyLines, RequiredFields


def test_create_order_returns_a_pending_order(client):
    response = client.post(
        "/orders",
        json={
            "customer_id": "ada@example.com",
            "currency": "GBP",
            "lines": [{"sku": "a", "quantity": 1, "unit_price": "5.00"}],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["customer_id"] == "ada@example.com"
    assert body["id"].startswith("ord_")


def test_create_order_prices_the_lines(client):
    response = client.post(
        "/orders",
        json={
            "customer_id": "ada@example.com",
            "currency": "GBP",
            "lines": [{"sku": "a", "quantity": 2, "unit_price": "7.50"}],
        },
    )
    assert Decimal(response.json()["total"]) == Decimal("15.00")


def test_create_order_applies_the_volume_discount(client):
    response = client.post(
        "/orders",
        json={
            "customer_id": "ada@example.com",
            "currency": "GBP",
            "lines": [{"sku": "a", "quantity": 10, "unit_price": "10.00"}],
        },
    )
    assert Decimal(response.json()["total"]) == Decimal("95.00")


def test_search_returns_summaries(fake_db):
    fake_db["orders"].append(
        {"id": "ord_1", "customer_id": "ada@example.com", "status": "pending",
         "currency": "GBP", "total": "10.00", "placed_at": None}
    )
    summaries = order_search("ada@example.com")
    assert [s.id for s in summaries] == ["ord_1"]


def test_summary_transform_defaults_the_status():
    summary = order_summary_from_row(
        {"id": "ord_2", "customer_id": "c", "currency": "GBP", "total": "1.00"}
    )
    assert summary.status == "pending"


def test_order_create_rejects_an_empty_line_list():
    with pytest.raises(Exception):
        OrderCreate(customer_id="c", currency="GBP", lines=[])


def test_order_line_rejects_a_zero_quantity():
    with pytest.raises(Exception):
        OrderLine(sku="a", quantity=0, unit_price=Decimal("1"))


def test_required_fields_validator_names_what_is_missing():
    with pytest.raises(ValidationError) as caught:
        RequiredFields("customer_id", "lines").check({"customer_id": "c"})
    assert caught.value.context["missing"] == ["lines"]


def test_non_empty_lines_validator_rejects_an_empty_order():
    with pytest.raises(ValidationError):
        NonEmptyLines().check({"customer_id": "c", "lines": []})
