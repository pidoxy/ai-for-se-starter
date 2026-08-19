import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common import cache  # noqa: E402


@pytest.fixture(autouse=True)
def clear_cache():
    cache._store.clear()
    yield
    cache._store.clear()


@pytest.fixture
def client():
    """A test client for the HTTP surface."""
    from fastapi.testclient import TestClient

    from src.main import app

    return TestClient(app)


@pytest.fixture
def fake_db(monkeypatch):
    """Swap the data layer for in-memory tables."""
    from src.common import db as real_db
    from src.errors import NotFoundError

    tables = {"customers": [], "orders": [], "order_lines": [], "settlements": []}

    def _customer_find(customer_id):
        for row in tables["customers"]:
            if row["id"] == customer_id:
                return dict(row)
        raise NotFoundError("no row matched the query", context={"id": customer_id})

    def _customers_search(country, tier):
        rows = [r for r in tables["customers"] if r["country"] == country and r["tier"] == tier]
        return sorted((dict(r) for r in rows), key=lambda r: r["display_name"])

    def _orders_for_customer(customer_id):
        return [dict(r) for r in tables["orders"] if r["customer_id"] == customer_id]

    monkeypatch.setattr(real_db, "db_customer_find", _customer_find)
    monkeypatch.setattr(real_db, "db_customers_search", _customers_search)
    monkeypatch.setattr(real_db, "db_orders_for_customer", _orders_for_customer)
    return tables
