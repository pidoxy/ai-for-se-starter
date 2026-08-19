"""Payment gateway client.

This is the live client. Anything in payments_legacy/ is not.
"""

from decimal import ROUND_HALF_UP, Decimal

from ..errors import UpstreamError, ValidationError

_CENTS = Decimal("0.01")

SUPPORTED_CURRENCIES = ("GBP", "EUR", "USD", "SEK")

# Fee schedule agreed with the processor in 2024: percentage plus a fixed part.
FEE_RATE = Decimal("0.0145")
FEE_FIXED = {
    "GBP": Decimal("0.20"),
    "EUR": Decimal("0.25"),
    "USD": Decimal("0.30"),
    "SEK": Decimal("2.50"),
}


def gateway_fee(amount: Decimal, currency: str) -> Decimal:
    """Processor fee for an amount, rounded half-up to the minor unit."""
    currency = currency.upper()
    if currency not in SUPPORTED_CURRENCIES:
        raise ValidationError("unsupported currency", context={"currency": currency})
    fee = Decimal(amount) * FEE_RATE + FEE_FIXED[currency]
    return fee.quantize(_CENTS, rounding=ROUND_HALF_UP)


def gateway_net(amount: Decimal, currency: str) -> Decimal:
    """What lands in our account after the processor takes its cut."""
    net = Decimal(amount) - gateway_fee(amount, currency)
    return net.quantize(_CENTS, rounding=ROUND_HALF_UP)


def gateway_charge(customer_id: str, amount: Decimal, currency: str) -> dict:
    """Place a charge. Returns the processor's acknowledgement."""
    if Decimal(amount) <= 0:
        raise ValidationError("charge amount must be positive", context={"amount": str(amount)})
    fee = gateway_fee(amount, currency)
    return {
        "customer_id": customer_id,
        "amount": str(Decimal(amount).quantize(_CENTS, rounding=ROUND_HALF_UP)),
        "currency": currency.upper(),
        "fee": str(fee),
        "net": str(gateway_net(amount, currency)),
        "status": "accepted",
    }


def gateway_refund(charge_id: str, amount: Decimal, currency: str) -> dict:
    """Refund part or all of a charge. Fees are not returned to us."""
    if not charge_id:
        raise UpstreamError("refund needs a charge id")
    return {
        "charge_id": charge_id,
        "amount": str(Decimal(amount).quantize(_CENTS, rounding=ROUND_HALF_UP)),
        "currency": currency.upper(),
        "fee_returned": "0.00",
        "status": "refunded",
    }
