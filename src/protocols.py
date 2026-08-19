"""Structural interfaces shared across packages.

These are Protocols, not base classes: implementations do not import from
here, only the call sites do.
"""

from typing import Protocol, runtime_checkable

from .errors import ValidationError


@runtime_checkable
class OrderValidator(Protocol):
    """Anything that can decide whether an order payload is acceptable.

    Implementations raise ValidationError; they never return a bool.
    """

    name: str

    def check(self, payload: dict) -> None:
        """Raise ValidationError if the payload is unacceptable."""
        ...


@runtime_checkable
class RecordSource(Protocol):
    """A read-only source of raw records keyed by string id."""

    def fetch(self, record_id: str) -> dict | None:
        ...


class RequiredFields:
    """Default OrderValidator: every listed key must be present and truthy."""

    def __init__(self, *fields: str) -> None:
        self.name = "required-fields"
        self._fields = fields

    def check(self, payload: dict) -> None:
        missing = [f for f in self._fields if not payload.get(f)]
        if missing:
            raise ValidationError(
                "order is missing required fields",
                context={"missing": missing},
            )


class NonEmptyLines:
    """Default OrderValidator: an order must contain at least one line."""

    def __init__(self) -> None:
        self.name = "non-empty-lines"

    def check(self, payload: dict) -> None:
        lines = payload.get("lines") or []
        if not lines:
            raise ValidationError("order must contain at least one line")
