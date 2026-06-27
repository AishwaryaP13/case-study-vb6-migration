"""Phase 1 smoke tests: insert one row per table and read it back."""
from app.models.customers import Customer
from app.models.providers import Provider
from app.models.products import Category, Product, ProductsByCustomer, ProductsByProvider
from app.models.stock import Stock, ManualStock, StockLog
from app.models.orders import (
    OrderRequest,
    OrderRequestDetail,
    OrderReception,
    OrderReceptionDetail,
)
from app.models.users import Level, User
from app.auth import hash_password, verify_password


# ── Master data ──────────────────────────────────────────────────────────────

def test_category_insert_read(db_session):
    cat = Category(category_name="Shellfish")
    db_session.add(cat)
    db_session.flush()
    result = db_session.get(Category, cat.category_id)
    assert result.category_name == "Shellfish"


def test_customer_insert_read(db_session):
    c = Customer(company_name="Acme Seafood", city="Seattle")
    db_session.add(c)
    db_session.flush()
    result = db_session.get(Customer, c.customer_id)
    assert result.company_name == "Acme Seafood"
    assert result.city == "Seattle"


def test_provider_insert_read(db_session):
    p = Provider(provider_name="Pacific Supply Co.", payment_terms="Net 30")
    db_session.add(p)
    db_session.flush()
    result = db_session.get(Provider, p.provider_id)
    assert result.provider_name == "Pacific Supply Co."


def test_product_insert_read(db_session):
    cat = Category(category_name="Fish")
    db_session.add(cat)
    db_session.flush()
    prod = Product(
        product_id="PROD-001",
        product_name="Coho Salmon",
        category_id=cat.category_id,
        discontinued=0,
        unit_price=12.50,
    )
    db_session.add(prod)
    db_session.flush()
    result = db_session.get(Product, "PROD-001")
    assert result.product_name == "Coho Salmon"
    assert result.unit_price == 12.50


# ── Stock ────────────────────────────────────────────────────────────────────

def test_stock_insert_read(db_session):
    prod = Product(product_id="PROD-STK", product_name="Halibut", discontinued=0)
    db_session.add(prod)
    db_session.flush()
    s = Stock(product_id="PROD-STK", stock=100.0, unit_price=8.0)
    db_session.add(s)
    db_session.flush()
    result = db_session.get(Stock, s.stock_id)
    assert result.stock == 100.0


def test_manual_stock_insert_read(db_session):
    prod = Product(product_id="PROD-MAN", product_name="Tuna", discontinued=0)
    db_session.add(prod)
    db_session.flush()
    s = Stock(product_id="PROD-MAN", stock=50.0)
    db_session.add(s)
    db_session.flush()
    ms = ManualStock(stock_id=s.stock_id, action="IN", quantity=50.0, price=5.0)
    db_session.add(ms)
    db_session.flush()
    result = db_session.get(ManualStock, ms.manual_id)
    assert result.action == "IN"


def test_stock_log_insert_read(db_session):
    prod = Product(product_id="PROD-LOG", product_name="Shrimp", discontinued=0)
    db_session.add(prod)
    db_session.flush()
    s = Stock(product_id="PROD-LOG", stock=20.0)
    db_session.add(s)
    db_session.flush()
    log = StockLog(
        stock_id=s.stock_id,
        product_id="PROD-LOG",
        doc_type="ManualStock",
        doc_id=1,
        quantity=20.0,
    )
    db_session.add(log)
    db_session.flush()
    result = db_session.get(StockLog, log.id)
    assert result.doc_type == "ManualStock"


# ── Orders ───────────────────────────────────────────────────────────────────

def test_order_request_insert_read(db_session):
    cust = Customer(company_name="Test Buyer")
    db_session.add(cust)
    db_session.flush()
    order = OrderRequest(customer_id=cust.customer_id, status="Pending")
    db_session.add(order)
    db_session.flush()
    result = db_session.get(OrderRequest, order.order_id)
    assert result.status == "Pending"


def test_order_request_detail_insert_read(db_session):
    cust = Customer(company_name="Detail Buyer")
    db_session.add(cust)
    db_session.flush()
    prod = Product(product_id="PROD-ORD", product_name="Cod", discontinued=0)
    db_session.add(prod)
    db_session.flush()
    order = OrderRequest(customer_id=cust.customer_id, status="Pending")
    db_session.add(order)
    db_session.flush()
    detail = OrderRequestDetail(
        order_id=order.order_id, product_id="PROD-ORD", quantity=5.0, unit_price=10.0
    )
    db_session.add(detail)
    db_session.flush()
    result = db_session.get(OrderRequestDetail, detail.order_detail_id)
    assert result.quantity == 5.0


def test_order_reception_insert_read(db_session):
    prov = Provider(provider_name="Test Supplier")
    db_session.add(prov)
    db_session.flush()
    order = OrderReception(provider_id=prov.provider_id, status="Received")
    db_session.add(order)
    db_session.flush()
    result = db_session.get(OrderReception, order.order_id)
    assert result.status == "Received"


def test_order_reception_detail_insert_read(db_session):
    prov = Provider(provider_name="Detail Supplier")
    db_session.add(prov)
    db_session.flush()
    prod = Product(product_id="PROD-REC", product_name="Crab", discontinued=0)
    db_session.add(prod)
    db_session.flush()
    order = OrderReception(provider_id=prov.provider_id, status="Pending")
    db_session.add(order)
    db_session.flush()
    detail = OrderReceptionDetail(
        order_id=order.order_id, product_id="PROD-REC", quantity=10.0
    )
    db_session.add(detail)
    db_session.flush()
    result = db_session.get(OrderReceptionDetail, detail.order_detail_id)
    assert result.quantity == 10.0


# ── M:N links ────────────────────────────────────────────────────────────────

def test_products_by_customer_insert_read(db_session):
    cust = Customer(company_name="Link Buyer")
    db_session.add(cust)
    db_session.flush()
    prod = Product(product_id="PROD-LC", product_name="Oyster", discontinued=0)
    db_session.add(prod)
    db_session.flush()
    link = ProductsByCustomer(customer_id=cust.customer_id, product_id="PROD-LC")
    db_session.add(link)
    db_session.flush()
    result = db_session.get(ProductsByCustomer, link.id)
    assert result.product_id == "PROD-LC"


def test_products_by_provider_insert_read(db_session):
    prov = Provider(provider_name="Link Supplier")
    db_session.add(prov)
    db_session.flush()
    prod = Product(product_id="PROD-LP", product_name="Clam", discontinued=0)
    db_session.add(prod)
    db_session.flush()
    link = ProductsByProvider(provider_id=prov.provider_id, product_id="PROD-LP")
    db_session.add(link)
    db_session.flush()
    result = db_session.get(ProductsByProvider, link.id)
    assert result.product_id == "PROD-LP"


# ── Users ────────────────────────────────────────────────────────────────────

def test_level_insert_read(db_session):
    lvl = Level(level="Seller")
    db_session.add(lvl)
    db_session.flush()
    result = db_session.get(Level, "Seller")
    assert result.level == "Seller"


def test_user_insert_read(db_session):
    lvl = Level(level="Administrator")
    db_session.add(lvl)
    db_session.flush()
    hashed = hash_password("secret")
    user = User(username="jsmith", password=hashed, fullname="John Smith", level="Administrator")
    db_session.add(user)
    db_session.flush()
    result = db_session.get(User, "jsmith")
    assert result.fullname == "John Smith"
    assert verify_password("secret", result.password)
    assert not verify_password("wrong", result.password)


# ── Seed data round-trip ─────────────────────────────────────────────────────

def test_seeded_customers(seeded_session):
    customers = seeded_session.query(Customer).all()
    assert len(customers) == 5


def test_seeded_providers(seeded_session):
    providers = seeded_session.query(Provider).all()
    assert len(providers) == 3


def test_seeded_products(seeded_session):
    products = seeded_session.query(Product).all()
    assert len(products) == 4


def test_seeded_order_requests(seeded_session):
    orders = seeded_session.query(OrderRequest).all()
    assert len(orders) == 25


def test_seeded_order_receptions(seeded_session):
    orders = seeded_session.query(OrderReception).all()
    assert len(orders) == 19


def test_seeded_stocks(seeded_session):
    stocks = seeded_session.query(Stock).all()
    assert len(stocks) == 50
