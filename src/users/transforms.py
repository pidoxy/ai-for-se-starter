"""Row-to-model transformations for the users package.

Services call these. Services never build models inline.
"""

from datetime import date

from .models import User, UserSummary


def user_from_row(row: dict) -> User:
    joined = row.get("joined_on")
    return User(
        id=row["id"],
        email=row["email"],
        display_name=row["display_name"],
        country=row["country"],
        tier=row.get("tier", "standard"),
        marketing_opt_in=bool(row.get("marketing_opt_in", 0)),
        joined_on=date.fromisoformat(joined) if isinstance(joined, str) else joined,
    )


def user_summary_from_row(row: dict) -> UserSummary:
    return UserSummary(
        id=row["id"],
        display_name=row["display_name"],
        country=row["country"],
        tier=row.get("tier", "standard"),
    )


def user_display_name_normalise(raw: str) -> str:
    """Collapse whitespace and trim. Case is left as the user typed it."""
    return " ".join(raw.split())
