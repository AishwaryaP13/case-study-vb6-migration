import sqlite3
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.users import Level, User
from app.auth import hash_password
import app.models  # noqa: F401 — ensures all models are registered

ORDERS_DB_PATH = "/Users/aishwaryap/Documents/code_migration/SKSVB6/Orders.db"

# Tables to seed, in FK-safe insertion order
_SEED_TABLES = [
    "Categories",
    "Customers",
    "Providers",
    "Levels",
    "Products",
    "Stocks",
    "ManualStocks",
    "StockLog",
    "OrderRequests",
    "OrderRequestDetails",
    "OrderReceptions",
    "OrderReceptionDetails",
    "ProductsByCustomer",
    "ProductsByProvider",
    "Users",
]


def _make_engine(url: str):
    engine = create_engine(url, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys = ON")

    return engine


@pytest.fixture(scope="session")
def db_engine():
    """Fresh in-memory DB with the full schema — no seed data."""
    engine = _make_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Transactional session that rolls back after each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
def seeded_engine():
    """In-memory DB seeded from the original Orders.db."""
    engine = _make_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    src = sqlite3.connect(ORDERS_DB_PATH)
    dst_conn = engine.raw_connection()
    # Disable FK checks during bulk load — seed data predates our FK constraints
    dst_conn.execute("PRAGMA foreign_keys = OFF")

    for table in _SEED_TABLES:
        try:
            rows = src.execute(f"SELECT * FROM {table}").fetchall()
            if not rows:
                continue
            col_names = [d[0] for d in src.execute(f"SELECT * FROM {table} LIMIT 0").description]
            placeholders = ", ".join("?" * len(col_names))
            quoted_cols = ", ".join(f'"{c}"' for c in col_names)
            dst_conn.executemany(
                f'INSERT OR IGNORE INTO "{table}" ({quoted_cols}) VALUES ({placeholders})',
                rows,
            )
        except Exception as exc:
            print(f"WARNING: could not seed {table}: {exc}")

    dst_conn.execute("PRAGMA foreign_keys = ON")
    dst_conn.commit()
    dst_conn.close()
    src.close()

    yield engine
    engine.dispose()


@pytest.fixture
def seeded_session(seeded_engine):
    Session = sessionmaker(bind=seeded_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def auth_session(db_engine):
    """Session with pre-seeded Level and User rows with hashed passwords for auth tests."""
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    session.add(Level(level="Administrator"))
    session.add(Level(level="Seller"))
    session.flush()
    session.add(User(
        username="testadmin",
        password=hash_password("adminpass"),
        fullname="Test Admin",
        level="Administrator",
    ))
    session.add(User(
        username="testseller",
        password=hash_password("sellerpass"),
        fullname="Test Seller",
        level="Seller",
    ))
    session.flush()

    yield session
    session.close()
    transaction.rollback()
    connection.close()
