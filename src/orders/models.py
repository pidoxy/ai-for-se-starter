"""Order models."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderLine(BaseModel):
    sku: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)


class OrderCreate(BaseModel):
    customer_id: str = Field(min_length=1)
    currency: str = Field(min_length=3, max_length=3)
    lines: list[OrderLine] = Field(min_length=1)
    note: str | None = None


class Order(BaseModel):
    id: str
    customer_id: str
    currency: str
    status: str = "pending"
    lines: list[OrderLine] = []
    total: Decimal = Decimal("0")
    placed_at: datetime | None = None


class OrderSummary(BaseModel):
    id: str
    customer_id: str
    status: str
    currency: str
    total: Decimal
