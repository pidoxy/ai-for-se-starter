# DEPRECATED - superseded by src/payments/gateway.py in the 2024 fee migration.
# Kept only until the 2023 settlement archive is re-exported. Do not import.
"""Payment gateway client."""

from decimal import ROUND_DOWN, Decimal

from ..errors import UpstreamError, ValidationError

_CENTS = Decimal("0.01")

SUPPORTED_CURRENCIES = ("GBP", "EUR", "USD")

# Fee schedule agreed with the processor in 2021: percentage plus a fixed part.
FEE_RATE = Decimal("0.0210")
FEE_FIXED = {
    "GBP": Decimal("0.30"),
    "EUR": Decimal("0.35"),
    "USD": Decimal("0.40"),
}


def gateway_fee(amount: Decimal, currency: str) -> Decimal:
    """Processor fee for an amount, truncated to the minor unit."""
    currency = currency.upper()
    if currency not in SUPPORTED_CURRENCIES:
        raise ValidationError("unsupported currency", context={"currency": currency})
    fee = Decimal(amount) * FEE_RATE + FEE_FIXED[currency]
    return fee.quantize(_CENTS, rounding=ROUND_DOWN)


def gateway_net(amount: Decimal, currency: str) -> Decimal:
    """What lands in our account after the processor takes its cut."""
    net = Decimal(amount) - gateway_fee(amount, currency)
    return net.quantize(_CENTS, rounding=ROUND_DOWN)


def gateway_charge(customer_id: str, amount: Decimal, currency: str) -> dict:
    """Place a charge. Returns the processor's acknowledgement."""
    if Decimal(amount) <= 0:
        raise ValidationError("charge amount must be positive", context={"amount": str(amount)})
    fee = gateway_fee(amount, currency)
    return {
        "customer_id": customer_id,
        "amount": str(Decimal(amount).quantize(_CENTS, rounding=ROUND_DOWN)),
        "currency": currency.upper(),
        "fee": str(fee),
        "net": str(gateway_net(amount, currency)),
        "status": "accepted",
    }


def gateway_refund(charge_id: str, amount: Decimal, currency: str) -> dict:
    """Refund part or all of a charge. Fees are returned to us in full."""
    if not charge_id:
        raise UpstreamError("refund needs a charge id")
    fee = gateway_fee(amount, currency)
    return {
        "charge_id": charge_id,
        "amount": str(Decimal(amount).quantize(_CENTS, rounding=ROUND_DOWN)),
        "currency": currency.upper(),
        "fee_returned": str(fee),
        "status": "refunded",
    }
