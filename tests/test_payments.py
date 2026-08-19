from decimal import Decimal

import pytest

from src.errors import UpstreamError, ValidationError
from src.payments.gateway import gateway_charge, gateway_fee, gateway_net, gateway_refund
from src.payments.reconcile import reconcile_settlement, reconcile_with_retry


def test_fee_is_rate_plus_fixed():
    assert gateway_fee(Decimal("100.00"), "GBP") == Decimal("1.65")


def test_fee_rounds_half_up():
    assert gateway_fee(Decimal("10.00"), "EUR") == Decimal("0.40")


def test_fee_rejects_an_unsupported_currency():
    with pytest.raises(ValidationError):
        gateway_fee(Decimal("10.00"), "JPY")


def test_sek_is_supported():
    assert gateway_fee(Decimal("100.00"), "SEK") == Decimal("3.95")


def test_net_is_amount_less_fee():
    assert gateway_net(Decimal("100.00"), "GBP") == Decimal("98.35")


def test_charge_rejects_a_non_positive_amount():
    with pytest.raises(ValidationError):
        gateway_charge("ada@example.com", Decimal("0"), "GBP")


def test_charge_reports_the_net():
    ack = gateway_charge("ada@example.com", Decimal("50.00"), "GBP")
    assert ack["status"] == "accepted"
    assert ack["net"] == "49.07"


def test_refund_keeps_the_fee():
    refund = gateway_refund("ch_1", Decimal("10.00"), "GBP")
    assert refund["fee_returned"] == "0.00"


def test_refund_needs_a_charge_id():
    with pytest.raises(UpstreamError):
        gateway_refund("", Decimal("10.00"), "GBP")


def test_settlement_matches_when_the_net_agrees():
    result = reconcile_settlement(
        {"id": "s1", "currency": "GBP", "gross": "100.00", "net": "98.35"}
    )
    assert result["matched"] is True


def test_batch_reports_only_the_mismatches():
    mismatches = reconcile_with_retry(
        [
            {"id": "s1", "currency": "GBP", "gross": "100.00", "net": "98.35"},
            {"id": "s2", "currency": "GBP", "gross": "100.00", "net": "90.00"},
        ]
    )
    assert [m["settlement_id"] for m in mismatches] == ["s2"]
