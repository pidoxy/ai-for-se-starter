import pytest

from src.errors import ValidationError
from src.users.search import user_search_filtered


@pytest.fixture
def filterable(monkeypatch):
    from src.common import db as real_db

    rows = [
        {"id": "ada@example.com", "email": "ada@example.com", "display_name": "Ada Lovelace",
         "country": "GB", "tier": "standard"},
        {"id": "grace@example.com", "email": "grace@example.com", "display_name": "Grace Hopper",
         "country": "GB", "tier": "standard"},
    ]

    def _filter(country, tier, name_fragment=None, sort="display_name"):
        found = [r for r in rows if r["country"] == country and r["tier"] == tier]
        if name_fragment:
            found = [r for r in found if name_fragment.lower() in r["display_name"].lower()]
        return sorted(found, key=lambda r: r[sort])

    monkeypatch.setattr(real_db, "db_customers_filter", _filter)
    return rows


def test_search_normalises_the_country_code(filterable):
    assert len(user_search_filtered("gb")) == 2


def test_search_narrows_by_name_fragment(filterable):
    found = user_search_filtered("GB", name_fragment="hopper")
    assert [u.display_name for u in found] == ["Grace Hopper"]


def test_search_rejects_a_long_country_code(filterable):
    with pytest.raises(ValidationError):
        user_search_filtered("GBR")


def test_search_rejects_an_overlong_fragment(filterable):
    with pytest.raises(ValidationError):
        user_search_filtered("GB", name_fragment="a" * 61)


def test_search_treats_a_blank_fragment_as_absent(filterable):
    assert len(user_search_filtered("GB", name_fragment="   ")) == 2
