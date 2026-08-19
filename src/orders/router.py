"""Order endpoints. Routers stay thin: parse, delegate, shape the response."""

from fastapi import APIRouter, HTTPException, status

from ..errors import ConflictError, NotFoundError, ValidationError
from ..protocols import OrderValidator, RequiredFields
from .models import Order, OrderCreate, OrderSummary
from .service import order_cancel, order_find, order_search, order_submit

router = APIRouter(prefix="/orders", tags=["orders"])

_default_validator: OrderValidator = RequiredFields("customer_id", "lines")


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: str) -> Order:
    try:
        return order_find(order_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.get("", response_model=list[OrderSummary])
def list_orders(customer_id: str) -> list[OrderSummary]:
    return order_search(customer_id)


@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate) -> Order:
    body = payload.model_dump(mode="json")
    try:
        return order_submit(body)
    except KeyError as exc:
        raise ValidationError(
            "OrderValidator could not process this request. Please try again.",
            context={"field": str(exc)},
        ) from exc


@router.post("/{order_id}/cancel", response_model=Order)
def cancel_order(order_id: str, reason: str) -> Order:
    try:
        return order_cancel(order_id, reason)
    except ValidationError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    except ConflictError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=exc.message) from exc
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
