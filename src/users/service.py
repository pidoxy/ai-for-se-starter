"""User service.

Service functions are named <resource>_<verb>. They raise typed errors and
return models, never bare dicts.
"""

from ..common import db
from ..errors import ConflictError, NotFoundError, ValidationError
from .models import User, UserCreate, UserSummary
from .transforms import user_display_name_normalise, user_from_row, user_summary_from_row

_BLOCKED_DOMAINS = {"example.invalid", "mailinator.com"}


def user_find(user_id: str) -> User:
    """Return one user. Raises NotFoundError when the id is unknown."""
    if not user_id:
        raise ValidationError("user id is required")
    row = db.db_customer_find(user_id)
    return user_from_row(row)


def user_search(country: str, tier: str = "standard") -> list[UserSummary]:
    """Every user in a country at a tier, ordered by display name."""
    country = country.strip().upper()
    if len(country) != 2:
        raise ValidationError("country must be a two-letter code", context={"country": country})
    rows = db.db_customers_search(country, tier)
    return [user_summary_from_row(row) for row in rows]


def user_create(payload: UserCreate) -> User:
    """Create a user after normalising the parts we own."""
    email = payload.email.strip().lower()
    domain = email.rpartition("@")[2]
    if domain in _BLOCKED_DOMAINS:
        raise ValidationError("that email domain is not accepted", context={"domain": domain})

    try:
        db.db_customer_find(email)
    except NotFoundError:
        pass
    else:
        raise ConflictError("a user with that email already exists", context={"email": email})

    return User(
        id=email,
        email=email,
        display_name=user_display_name_normalise(payload.display_name),
        country=payload.country.strip().upper(),
        marketing_opt_in=payload.marketing_opt_in,
    )


def user_tier_set(user_id: str, tier: str) -> User:
    """Move a user between tiers."""
    allowed = {"standard", "plus", "enterprise"}
    if tier not in allowed:
        raise ValidationError("unknown tier", context={"tier": tier, "allowed": sorted(allowed)})
    current = user_find(user_id)
    return current.model_copy(update={"tier": tier})
