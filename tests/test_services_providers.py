"""Phase 2 — Feature 3: Providers CRUD service tests."""
import pytest
from pydantic import ValidationError

from app.services.providers import (
    list_providers,
    get_provider,
    create_provider,
    update_provider,
    delete_provider,
)
from app.schemas.providers import ProviderIn


def _valid_provider(**overrides) -> ProviderIn:
    """Minimal valid ProviderIn — all 11 required fields present."""
    defaults = dict(
        provider_name="Test Supplier",
        payment_terms="Net 30",
        email_address="contact@supplier.com",
        postal_code="12345",
        city="Boston",
        state_or_province="MA",
        country_region="USA",
        fax_number="555-0001",
        contact_title="Mr",
        contact_first_name="John",
        notes="Test notes",
    )
    defaults.update(overrides)
    return ProviderIn(**defaults)


# ── Required-field validation ─────────────────────────────────────────────────

@pytest.mark.parametrize("field", [
    "provider_name", "payment_terms", "email_address", "postal_code",
    "city", "state_or_province", "country_region", "fax_number",
    "contact_title", "contact_first_name", "notes",
])
def test_create_rejects_empty_required_field(db_session, field):
    with pytest.raises(ValidationError):
        _valid_provider(**{field: ""})


@pytest.mark.parametrize("field", [
    "provider_name", "city", "contact_first_name",
])
def test_create_rejects_whitespace_required_field(db_session, field):
    with pytest.raises(ValidationError):
        _valid_provider(**{field: "   "})


def test_create_accepts_all_optionals_as_none(db_session):
    data = _valid_provider()
    result = create_provider(db_session, data)
    assert result.phone_number is None
    assert result.extension is None
    assert result.contact_last_name is None
    assert result.address is None


# ── create_provider ───────────────────────────────────────────────────────────

def test_create_returns_provider_out(db_session):
    result = create_provider(db_session, _valid_provider())
    assert result.provider_id is not None
    assert result.provider_name == "Test Supplier"
    assert result.city == "Boston"


def test_create_with_optional_fields(db_session):
    data = _valid_provider(
        phone_number="555-9999",
        contact_last_name="Doe",
        address="123 Pier St",
    )
    result = create_provider(db_session, data)
    assert result.phone_number == "555-9999"
    assert result.contact_last_name == "Doe"
    assert result.address == "123 Pier St"


# ── get_provider ─────────────────────────────────────────────────────────────

def test_get_provider_known(db_session):
    created = create_provider(db_session, _valid_provider(provider_name="Ocean Fresh"))
    result = get_provider(db_session, created.provider_id)
    assert result is not None
    assert result.provider_name == "Ocean Fresh"


def test_get_provider_unknown(db_session):
    assert get_provider(db_session, 99999) is None


# ── update_provider ───────────────────────────────────────────────────────────

def test_update_persists_changes(db_session):
    created = create_provider(db_session, _valid_provider(city="Portland"))
    updated = update_provider(
        db_session, created.provider_id, _valid_provider(city="Seattle", provider_name="Updated Co")
    )
    assert updated is not None
    assert updated.city == "Seattle"
    assert updated.provider_name == "Updated Co"
    fetched = get_provider(db_session, created.provider_id)
    assert fetched.city == "Seattle"


def test_update_unknown_returns_none(db_session):
    assert update_provider(db_session, 99999, _valid_provider()) is None


# ── delete_provider ───────────────────────────────────────────────────────────

def test_delete_returns_true_and_removes(db_session):
    created = create_provider(db_session, _valid_provider())
    assert delete_provider(db_session, created.provider_id) is True
    assert get_provider(db_session, created.provider_id) is None


def test_delete_unknown_returns_false(db_session):
    assert delete_provider(db_session, 99999) is False


# ── list_providers ────────────────────────────────────────────────────────────

def test_list_returns_created(db_session):
    create_provider(db_session, _valid_provider(provider_name="Alpha Supply"))
    create_provider(db_session, _valid_provider(provider_name="Beta Supply"))
    names = [r.provider_name for r in list_providers(db_session)]
    assert "Alpha Supply" in names
    assert "Beta Supply" in names


def test_list_search_filters(db_session):
    create_provider(db_session, _valid_provider(provider_name="Pacific Fisheries"))
    create_provider(db_session, _valid_provider(provider_name="Atlantic Corp"))
    results = list_providers(db_session, search="Pacific")
    assert len(results) == 1
    assert results[0].provider_name == "Pacific Fisheries"


def test_list_search_case_insensitive(db_session):
    create_provider(db_session, _valid_provider(provider_name="Salmon King Supply"))
    results = list_providers(db_session, search="salmon")
    assert any(r.provider_name == "Salmon King Supply" for r in results)


# ── Against real Orders.db seed data ─────────────────────────────────────────

def test_seeded_list_returns_three(seeded_session):
    results = list_providers(seeded_session)
    assert len(results) == 3


def test_seeded_get_ship_woolf(seeded_session):
    results = list_providers(seeded_session)
    ids = {r.provider_name: r.provider_id for r in results}
    woolf = get_provider(seeded_session, ids["Ship Woolf"])
    assert woolf.city == "Harvard"
    assert woolf.contact_first_name == "Steven P."
    assert woolf.payment_terms == "every month"


def test_seeded_search_nickerson(seeded_session):
    results = list_providers(seeded_session, search="nickerson")
    assert len(results) == 1
    assert results[0].provider_name == "Nickerson Farms"
