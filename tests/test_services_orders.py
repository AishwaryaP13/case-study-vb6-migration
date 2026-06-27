"""Phase 2 — Features 6 & 7: Orders create / list / approve / cancel."""
import pytest
from pydantic import ValidationError

from app.services.orders import (
    create_order, get_order, list_orders, approve_order, cancel_order,
    OrderAlreadyApproved, OrderAlreadyCancelled,
)
from app.schemas.orders import OrderIn, OrderLineIn
from app.models.customers import Customer
from app.models.providers import Provider
from app.models.products import Product


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def setup(db_session):
    cust = Customer(company_name="Test Buyer")
    prov = Provider(
        provider_name="Test Supplier", payment_terms="Net30",
        email_address="s@s.com", postal_code="11111", city="Boston",
        state_or_province="MA", country_region="USA", fax_number="555",
        contact_title="Mr", contact_first_name="Joe", notes="n",
    )
    prod = Product(product_id="FISH1", product_name="Salmon", discontinued=0,
                   unit_price=10.0, units_on_order=0)
    db_session.add_all([cust, prov, prod])
    db_session.flush()
    return {"cust_id": cust.customer_id, "prov_id": prov.provider_id, "session": db_session}


def _sale_order(partner_id: int, qty: float = 2.0) -> OrderIn:
    return OrderIn(
        direction="SALE",
        partner_id=partner_id,
        lines=[OrderLineIn(product_id="FISH1", quantity=qty,
                           unit_price=10.0, sale_price=12.0)],
    )


def _purchase_order(partner_id: int, qty: float = 3.0) -> OrderIn:
    return OrderIn(
        direction="PURCHASE",
        partner_id=partner_id,
        lines=[OrderLineIn(product_id="FISH1", quantity=qty,
                           unit_price=10.0, sale_price=11.0)],
    )


# ── Schema validation ─────────────────────────────────────────────────────────

def test_empty_lines_rejected():
    with pytest.raises(ValidationError):
        OrderIn(direction="SALE", partner_id=1, lines=[])


def test_zero_quantity_rejected():
    with pytest.raises(ValidationError):
        OrderLineIn(product_id="X", quantity=0, unit_price=1.0, sale_price=1.0)


def test_negative_quantity_rejected():
    with pytest.raises(ValidationError):
        OrderLineIn(product_id="X", quantity=-1, unit_price=1.0, sale_price=1.0)


# ── create_order SALE ─────────────────────────────────────────────────────────

def test_create_sale_order_status(setup):
    db = setup["session"]
    result = create_order(db, _sale_order(setup["cust_id"]), "testuser")
    assert result.status == "REQUESTED"
    assert result.direction == "SALE"
    assert result.partner_id == setup["cust_id"]


def test_create_sale_order_lines(setup):
    db = setup["session"]
    result = create_order(db, _sale_order(setup["cust_id"], qty=3.0), "testuser")
    assert len(result.lines) == 1
    assert result.lines[0].quantity == 3.0
    assert result.lines[0].line_total == pytest.approx(3.0 * 12.0)


def test_create_sale_bumps_units_on_order(setup):
    db = setup["session"]
    prod_before = db.get(Product, "FISH1")
    before = prod_before.units_on_order or 0
    create_order(db, _sale_order(setup["cust_id"], qty=5.0), "testuser")
    db.expire(prod_before)
    assert prod_before.units_on_order == before + 5


def test_create_sale_assigns_order_id(setup):
    db = setup["session"]
    r1 = create_order(db, _sale_order(setup["cust_id"]), "user")
    r2 = create_order(db, _sale_order(setup["cust_id"]), "user")
    assert r1.order_id != r2.order_id


# ── create_order PURCHASE ─────────────────────────────────────────────────────

def test_create_purchase_order_status(setup):
    db = setup["session"]
    result = create_order(db, _purchase_order(setup["prov_id"]), "testuser")
    assert result.status == "RECEIVED"
    assert result.direction == "PURCHASE"


def test_create_purchase_does_not_bump_units_on_order(setup):
    db = setup["session"]
    prod = db.get(Product, "FISH1")
    before = prod.units_on_order or 0
    create_order(db, _purchase_order(setup["prov_id"], qty=10.0), "testuser")
    db.expire(prod)
    assert prod.units_on_order == before  # unchanged


def test_create_purchase_line_total(setup):
    db = setup["session"]
    result = create_order(db, _purchase_order(setup["prov_id"], qty=4.0), "user")
    assert result.lines[0].line_total == pytest.approx(4.0 * 11.0)


# ── get_order ─────────────────────────────────────────────────────────────────

def test_get_sale_order_with_lines(setup):
    db = setup["session"]
    created = create_order(db, _sale_order(setup["cust_id"]), "user")
    fetched = get_order(db, created.order_id, "SALE")
    assert fetched is not None
    assert fetched.order_id == created.order_id
    assert len(fetched.lines) == 1


def test_get_unknown_order_returns_none(setup):
    db = setup["session"]
    assert get_order(db, 99999, "SALE") is None


# ── list_orders ───────────────────────────────────────────────────────────────

def test_list_filters_by_status(setup):
    db = setup["session"]
    create_order(db, _sale_order(setup["cust_id"]), "user")
    results = list_orders(db, direction="SALE", status="REQUESTED")
    assert all(r.status == "REQUESTED" for r in results)
    assert len(results) >= 1


def test_list_purchase_separate_from_sale(setup):
    db = setup["session"]
    create_order(db, _sale_order(setup["cust_id"]), "user")
    create_order(db, _purchase_order(setup["prov_id"]), "user")
    sales = list_orders(db, direction="SALE")
    purchases = list_orders(db, direction="PURCHASE")
    assert all(r.direction == "SALE" for r in sales)
    assert all(r.direction == "PURCHASE" for r in purchases)


# ── approve_order ─────────────────────────────────────────────────────────────

def test_approve_sale_order(setup):
    db = setup["session"]
    order = create_order(db, _sale_order(setup["cust_id"]), "user")
    result = approve_order(db, order.order_id, "SALE", "approver")
    assert result.status == "APPROVED"
    assert result.changed_by == "approver"


def test_approve_already_approved_raises(setup):
    db = setup["session"]
    order = create_order(db, _sale_order(setup["cust_id"]), "user")
    approve_order(db, order.order_id, "SALE", "approver")
    with pytest.raises(OrderAlreadyApproved):
        approve_order(db, order.order_id, "SALE", "approver2")


def test_approve_cancelled_raises(setup):
    db = setup["session"]
    order = create_order(db, _sale_order(setup["cust_id"]), "user")
    cancel_order(db, order.order_id, "SALE", "user")
    with pytest.raises(OrderAlreadyCancelled):
        approve_order(db, order.order_id, "SALE", "approver")


# ── cancel_order ──────────────────────────────────────────────────────────────

def test_cancel_sale_order(setup):
    db = setup["session"]
    order = create_order(db, _sale_order(setup["cust_id"]), "user")
    result = cancel_order(db, order.order_id, "SALE", "canceller")
    assert result.status == "CANCELLED"
    assert result.changed_by == "canceller"


def test_cancel_approved_raises(setup):
    db = setup["session"]
    order = create_order(db, _sale_order(setup["cust_id"]), "user")
    approve_order(db, order.order_id, "SALE", "approver")
    with pytest.raises(OrderAlreadyApproved):
        cancel_order(db, order.order_id, "SALE", "canceller")


def test_cancel_already_cancelled_raises(setup):
    db = setup["session"]
    order = create_order(db, _sale_order(setup["cust_id"]), "user")
    cancel_order(db, order.order_id, "SALE", "user")
    with pytest.raises(OrderAlreadyCancelled):
        cancel_order(db, order.order_id, "SALE", "user2")


def test_approve_purchase_order(setup):
    db = setup["session"]
    order = create_order(db, _purchase_order(setup["prov_id"]), "user")
    result = approve_order(db, order.order_id, "PURCHASE", "approver")
    assert result.status == "APPROVED"


def test_cancel_purchase_order(setup):
    db = setup["session"]
    order = create_order(db, _purchase_order(setup["prov_id"]), "user")
    result = cancel_order(db, order.order_id, "PURCHASE", "user")
    assert result.status == "CANCELLED"


# ── Against real Orders.db seed data ─────────────────────────────────────────

def test_seeded_sale_orders_count(seeded_session):
    results = list_orders(seeded_session, direction="SALE")
    assert len(results) == 25


def test_seeded_purchase_orders_count(seeded_session):
    results = list_orders(seeded_session, direction="PURCHASE")
    assert len(results) == 19


def test_seeded_sale_status_filter(seeded_session):
    approved = list_orders(seeded_session, direction="SALE", status="APPROVED")
    cancelled = list_orders(seeded_session, direction="SALE", status="CANCELLED")
    requested = list_orders(seeded_session, direction="SALE", status="REQUESTED")
    assert len(approved) + len(cancelled) + len(requested) == 25


def test_seeded_get_sale_order_with_lines(seeded_session):
    orders = list_orders(seeded_session, direction="SALE")
    # Find first order that actually has detail lines in the seed data
    order_with_lines = next(
        (get_order(seeded_session, o.order_id, "SALE")
         for o in orders
         if get_order(seeded_session, o.order_id, "SALE") and
            len(get_order(seeded_session, o.order_id, "SALE").lines) >= 1),
        None,
    )
    assert order_with_lines is not None, "Expected at least one seeded sale order with lines"
    assert len(order_with_lines.lines) >= 1
