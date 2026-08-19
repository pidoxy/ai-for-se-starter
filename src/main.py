"""Application entry point.

Wires the routers, installs the error handlers, and registers the default
order validators. Nothing else belongs in here.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .errors import AppError, ConflictError, NotFoundError, UpstreamError, ValidationError
from .orders.router import router as orders_router
from .protocols import NonEmptyLines, OrderValidator, RequiredFields
from .users.router import router as users_router

logger = logging.getLogger("app")

_STATUS_FOR = {
    ValidationError: 422,
    NotFoundError: 404,
    ConflictError: 409,
    UpstreamError: 502,
}

VALIDATORS: list[OrderValidator] = [
    RequiredFields("customer_id", "currency", "lines"),
    NonEmptyLines(),
]

app = FastAPI(title="Colony Orders", version="0.4.0")
app.include_router(users_router)
app.include_router(orders_router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    status_code = _STATUS_FOR.get(type(exc), 500)
    logger.warning("%s on %s: %s", type(exc).__name__, request.url.path, exc)
    return JSONResponse(
        status_code=status_code,
        content={"error": type(exc).__name__, "detail": exc.message, "context": exc.context},
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "validators": [v.name for v in VALIDATORS]}
