"""Phase 2 — Feature 2: Customers CRUD service tests."""
import pytest
from pydantic import ValidationError

from app.services.customers import (
    list_customers,
    get_customer,
    create_customer,
    update_customer,
    delete_customer,
)
from app.schemas.customers import CustomerIn


# ── create_customer ───────────────────────────────────────────────────────────

def test_create_returns_customer_out(db_session):
    result = create_customer(db_session, CustomerIn(company_name="Acme Fish"))
    assert result.customer_id is not None
    assert result.company_name == "Acme Fish"


def test_create_all_optional_fields(db_session):
    data = CustomerIn(
        company_name="Full Co",
        city="Seattle",
        state_or_province="WA",
        postal_code="98101",
        country_region="USA",
        phone_number="555-1234",
        email_address="fish@fullco.com",
        contact_first_name="Jane",
        contact_last_name="Doe",
    )
    result = create_customer(db_session, data)
    assert result.city == "Seattle"
    assert result.email_address == "fish@fullco.com"
    assert result.contact_last_name == "Doe"


def test_create_rejects_empty_company_name(db_session):
    with pytest.raises(ValidationError):
        CustomerIn(company_name="")


def test_create_rejects_whitespace_company_name(db_session):
    with pytest.raises(ValidationError):
        CustomerIn(company_name="   ")


# ── get_customer ─────────────────────────────────────────────────────────────

def test_get_customer_known(db_session):
    created = create_customer(db_session, CustomerIn(company_name="Pacific Seafood"))
    result = get_customer(db_session, created.customer_id)
    assert result is not None
    assert result.company_name == "Pacific Seafood"


def test_get_customer_unknown(db_session):
    assert get_customer(db_session, 99999) is None


# ── update_customer ───────────────────────────────────────────────────────────

def test_update_persists_changes(db_session):
    created = create_customer(db_session, CustomerIn(company_name="Old Name"))
    updated = update_customer(
        db_session, created.customer_id, CustomerIn(company_name="New Name", city="Portland")
    )
    assert updated is not None
    assert updated.company_name == "New Name"
    assert updated.city == "Portland"
    # Verify it's actually persisted
    fetched = get_customer(db_session, created.customer_id)
    assert fetched.company_name == "New Name"


def test_update_unknown_returns_none(db_session):
    assert update_customer(db_session, 99999, CustomerIn(company_name="X")) is None


# ── delete_customer ───────────────────────────────────────────────────────────

def test_delete_returns_true_and_removes(db_session):
    created = create_customer(db_session, CustomerIn(company_name="To Delete"))
    assert delete_customer(db_session, created.customer_id) is True
    assert get_customer(db_session, created.customer_id) is None


def test_delete_unknown_returns_false(db_session):
    assert delete_customer(db_session, 99999) is False


# ── list_customers ────────────────────────────────────────────────────────────

def test_list_returns_created(db_session):
    create_customer(db_session, CustomerIn(company_name="Alpha"))
    create_customer(db_session, CustomerIn(company_name="Beta"))
    results = list_customers(db_session)
    names = [r.company_name for r in results]
    assert "Alpha" in names
    assert "Beta" in names


def test_list_search_filters_by_name(db_session):
    create_customer(db_session, CustomerIn(company_name="Spectacular Tuna"))
    create_customer(db_session, CustomerIn(company_name="Generic Supply"))
    results = list_customers(db_session, search="Spectacular")
    assert len(results) == 1
    assert results[0].company_name == "Spectacular Tuna"


def test_list_search_case_insensitive(db_session):
    create_customer(db_session, CustomerIn(company_name="Salmon King"))
    results = list_customers(db_session, search="salmon")
    assert any(r.company_name == "Salmon King" for r in results)


def test_list_empty_search_returns_all(db_session):
    create_customer(db_session, CustomerIn(company_name="One"))
    create_customer(db_session, CustomerIn(company_name="Two"))
    assert len(list_customers(db_session, search="")) >= 2


# ── Against real Orders.db seed data ─────────────────────────────────────────

def test_seeded_list_returns_five(seeded_session):
    results = list_customers(seeded_session)
    assert len(results) == 5


def test_seeded_get_spectacular_food(seeded_session):
    results = list_customers(seeded_session)
    ids = {r.company_name: r.customer_id for r in results}
    spectacular = get_customer(seeded_session, ids["Spectacular Food"])
    assert spectacular.company_name == "Spectacular Food"
    assert spectacular.city == "Atlanta"


def test_seeded_search_by_name(seeded_session):
    results = list_customers(seeded_session, search="world")
    assert len(results) == 1
    assert results[0].company_name == "World of Fun"
