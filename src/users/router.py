"""User endpoints. Routers stay thin: parse, delegate, shape the response."""

from fastapi import APIRouter, HTTPException, status

from ..errors import ConflictError, NotFoundError, ValidationError
from .models import User, UserCreate, UserSummary
from .service import user_create, user_find, user_search, user_tier_set

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=User)
def get_user(user_id: str) -> User:
    try:
        return user_find(user_id)
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.get("", response_model=list[UserSummary])
def list_users(country: str, tier: str = "standard") -> list[UserSummary]:
    try:
        return user_search(country, tier)
    except ValidationError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate) -> User:
    try:
        return user_create(payload)
    except ValidationError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    except ConflictError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=exc.message) from exc


@router.put("/{user_id}/tier", response_model=User)
def set_user_tier(user_id: str, tier: str) -> User:
    try:
        return user_tier_set(user_id, tier)
    except ValidationError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc
    except NotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
