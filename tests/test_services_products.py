"""Phase 2 — Feature 4: Products + Categories CRUD service tests."""
import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.services.products import (
    list_categories,
    list_products,
    get_product,
    create_product,
    update_product,
    delete_product,
)
from app.schemas.products import ProductIn
from app.models.products import Category


def _prod(**overrides) -> ProductIn:
    defaults = dict(product_id="TEST1", product_name="Test Fish", discontinued=0)
    defaults.update(overrides)
    return ProductIn(**defaults)


# ── Validation ────────────────────────────────────────────────────────────────

def test_empty_product_id_rejected():
    with pytest.raises(ValidationError):
        ProductIn(product_id="", discontinued=0)


def test_whitespace_product_id_rejected():
    with pytest.raises(ValidationError):
        ProductIn(product_id="   ", discontinued=0)


def test_product_id_stored_uppercase():
    data = ProductIn(product_id="abc123", discontinued=0)
    assert data.product_id == "ABC123"


def test_discontinued_must_be_0_or_1():
    with pytest.raises(ValidationError):
        ProductIn(product_id="X1", discontinued=5)


# ── create_product ────────────────────────────────────────────────────────────

def test_create_returns_product_out(db_session):
    result = create_product(db_session, _prod(product_id="FISH1", product_name="Salmon"))
    assert result.product_id == "FISH1"
    assert result.product_name == "Salmon"
    assert result.discontinued == 0


def test_create_with_optional_fields(db_session):
    result = create_product(db_session, _prod(
        product_id="FISH2",
        unit_price=12.50,
        unit="kg",
        quantity_per_unit=1.0,
    ))
    assert result.unit_price == 12.50
    assert result.unit == "kg"


def test_create_duplicate_product_id_raises(db_session):
    create_product(db_session, _prod(product_id="DUP1"))
    with pytest.raises(IntegrityError):
        create_product(db_session, _prod(product_id="DUP1"))


# ── get_product ───────────────────────────────────────────────────────────────

def test_get_product_known(db_session):
    create_product(db_session, _prod(product_id="GET1", product_name="Tuna"))
    result = get_product(db_session, "GET1")
    assert result is not None
    assert result.product_name == "Tuna"


def test_get_product_case_insensitive(db_session):
    create_product(db_session, _prod(product_id="CASE1"))
    assert get_product(db_session, "case1") is not None


def test_get_product_unknown(db_session):
    assert get_product(db_session, "ZZZNOPE") is None


# ── update_product ────────────────────────────────────────────────────────────

def test_update_persists_changes(db_session):
    create_product(db_session, _prod(product_id="UPD1", product_name="Old"))
    result = update_product(db_session, "UPD1", _prod(product_id="UPD1", product_name="New", unit_price=99.0))
    assert result.product_name == "New"
    assert result.unit_price == 99.0


def test_update_unknown_returns_none(db_session):
    assert update_product(db_session, "NOPE", _prod()) is None


# ── delete_product ────────────────────────────────────────────────────────────

def test_delete_returns_true_and_removes(db_session):
    create_product(db_session, _prod(product_id="DEL1"))
    assert delete_product(db_session, "DEL1") is True
    assert get_product(db_session, "DEL1") is None


def test_delete_unknown_returns_false(db_session):
    assert delete_product(db_session, "NOPE") is False


# ── list_products ─────────────────────────────────────────────────────────────

def test_list_search_by_name(db_session):
    create_product(db_session, _prod(product_id="S1", product_name="Sockeye Salmon"))
    create_product(db_session, _prod(product_id="T1", product_name="Bluefin Tuna"))
    results = list_products(db_session, search="salmon")
    assert len(results) == 1
    assert results[0].product_id == "S1"


def test_list_filter_by_category(db_session):
    cat = Category(category_name="Fish")
    db_session.add(cat)
    db_session.flush()
    create_product(db_session, _prod(product_id="CF1", product_name="Cod", category_id=cat.category_id))
    create_product(db_session, _prod(product_id="CF2", product_name="Other"))
    results = list_products(db_session, category_id=cat.category_id)
    assert len(results) == 1
    assert results[0].product_id == "CF1"


def test_list_combined_filters(db_session):
    cat = Category(category_name="Shellfish")
    db_session.add(cat)
    db_session.flush()
    create_product(db_session, _prod(product_id="SH1", product_name="King Crab", category_id=cat.category_id))
    create_product(db_session, _prod(product_id="SH2", product_name="Lobster", category_id=cat.category_id))
    create_product(db_session, _prod(product_id="SH3", product_name="King Salmon"))
    results = list_products(db_session, search="king", category_id=cat.category_id)
    assert len(results) == 1
    assert results[0].product_id == "SH1"


# ── Against real Orders.db seed data ─────────────────────────────────────────

def test_seeded_list_returns_four(seeded_session):
    assert len(list_products(seeded_session)) == 4


def test_seeded_get_ikura(seeded_session):
    result = get_product(seeded_session, "IK1")
    assert result is not None
    assert result.product_name == "Ikura"
    assert result.unit_price == 32.0
    assert result.discontinued == 0


def test_seeded_search_case_insensitive(seeded_session):
    results = list_products(seeded_session, search="ikura")
    assert len(results) == 1
    assert results[0].product_id == "IK1"


def test_seeded_filter_by_category(seeded_session):
    # CategoryID=2 is "Crab" — IK1 (Ikura) is in it
    results = list_products(seeded_session, category_id=2)
    assert any(r.product_id == "IK1" for r in results)


def test_seeded_list_categories_returns_eight(seeded_session):
    categories = list_categories(seeded_session)
    assert len(categories) == 8


def test_seeded_categories_include_fish(seeded_session):
    categories = list_categories(seeded_session)
    names = [c.category_name for c in categories]
    assert "Fish" in names
    assert "Crab" in names
