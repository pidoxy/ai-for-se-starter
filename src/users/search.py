"""Customer search.

Search is a read path: it never writes, and it never returns more than the
summary shape.
"""

from fastapi_query_filters import StringFilter, normalise_fragment

from ..common import db
from ..errors import ValidationError
from .models import UserSummary
from .transforms import user_summary_from_row

_MAX_FRAGMENT = 60


def user_search_filtered(
    country: str,
    tier: str = "standard",
    name_fragment: str | None = None,
    sort: str = "display_name",
) -> list[UserSummary]:
    """Search customers in one country, optionally narrowed by display name."""
    country = country.strip().upper()
    if len(country) != 2:
        raise ValidationError("country must be a two-letter code", context={"country": country})

    if name_fragment is not None:
        name_fragment = normalise_fragment(name_fragment.strip())
        if len(name_fragment) > _MAX_FRAGMENT:
            raise ValidationError(
                "search fragment is too long",
                context={"length": len(name_fragment), "max": _MAX_FRAGMENT},
            )
        if not name_fragment:
            name_fragment = None

    rows = db.db_customers_filter(country, tier, name_fragment, sort)
    return [user_summary_from_row(row) for row in rows]


def user_search_filters() -> list[StringFilter]:
    """The filters this endpoint exposes, for the API description."""
    return [
        StringFilter(name="country", required=True),
        StringFilter(name="tier", required=False),
        StringFilter(name="name_fragment", required=False),
    ]
