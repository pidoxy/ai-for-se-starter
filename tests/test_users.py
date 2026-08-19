import pytest

from src.errors import ConflictError, NotFoundError, ValidationError
from src.users.models import UserCreate
from src.users.service import user_create, user_find, user_search, user_tier_set
from src.users.transforms import user_display_name_normalise


def test_find_returns_a_user(fake_db):
    fake_db["customers"].append(
        {"id": "ada@example.com", "email": "ada@example.com", "display_name": "Ada",
         "country": "GB", "tier": "standard"}
    )
    user = user_find("ada@example.com")
    assert user.display_name == "Ada"
    assert user.country == "GB"


def test_find_unknown_id_raises_not_found(fake_db):
    with pytest.raises(NotFoundError):
        user_find("nobody@example.com")


def test_find_requires_an_id(fake_db):
    with pytest.raises(ValidationError):
        user_find("")


def test_search_normalises_the_country_code(fake_db):
    fake_db["customers"].append(
        {"id": "b@example.com", "email": "b@example.com", "display_name": "Bea",
         "country": "GB", "tier": "standard"}
    )
    assert len(user_search("gb")) == 1


def test_search_rejects_a_long_country_code(fake_db):
    with pytest.raises(ValidationError):
        user_search("GBR")


def test_create_lowercases_the_email(fake_db):
    user = user_create(UserCreate(email="Grace@Example.com", display_name="Grace", country="us"))
    assert user.email == "grace@example.com"
    assert user.country == "US"


def test_create_rejects_a_blocked_domain(fake_db):
    with pytest.raises(ValidationError):
        user_create(UserCreate(email="x@mailinator.com", display_name="X", country="GB"))


def test_create_rejects_a_duplicate(fake_db):
    fake_db["customers"].append(
        {"id": "ada@example.com", "email": "ada@example.com", "display_name": "Ada",
         "country": "GB", "tier": "standard"}
    )
    with pytest.raises(ConflictError):
        user_create(UserCreate(email="ada@example.com", display_name="Ada", country="GB"))


def test_tier_set_rejects_an_unknown_tier(fake_db):
    with pytest.raises(ValidationError):
        user_tier_set("ada@example.com", "platinum")


def test_display_name_normalisation_collapses_whitespace():
    assert user_display_name_normalise("  Ada   Lovelace ") == "Ada Lovelace"
