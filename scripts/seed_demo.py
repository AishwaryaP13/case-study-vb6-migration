"""
Seed sks.db from Orders.db for the demo.
Run once before launching the Streamlit app:

    cd SKSVB6_Migrated
    source .venv/bin/activate
    python scripts/seed_demo.py
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

ORDERS_DB = Path("/Users/aishwaryap/Documents/code_migration/SKSVB6/Orders.db")
SKS_DB = ROOT / "sks.db"

SEED_TABLES = [
    "Categories", "Customers", "Providers", "Levels", "Products",
    "Stocks", "ManualStocks", "StockLog",
    "OrderRequests", "OrderRequestDetails",
    "OrderReceptions", "OrderReceptionDetails",
    "ProductsByCustomer", "ProductsByProvider",
    "Users",
]


def main():
    if not ORDERS_DB.exists():
        sys.exit(f"Source DB not found: {ORDERS_DB}")

    from app.auth import hash_password

    # Reset sks.db via alembic
    import subprocess
    print("Running alembic upgrade head…")
    result = subprocess.run(
        [str(ROOT / ".venv/bin/alembic"), "upgrade", "head"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if result.returncode != 0:
        sys.exit(f"alembic failed:\n{result.stderr}")
    print("  done.")

    src = sqlite3.connect(ORDERS_DB)
    dst = sqlite3.connect(SKS_DB)

    dst.execute("PRAGMA foreign_keys = OFF")

    for table in SEED_TABLES:
        rows = src.execute(f"SELECT * FROM {table}").fetchall()
        if not rows:
            continue
        col_names = [d[0] for d in src.execute(f"SELECT * FROM {table} LIMIT 0").description]
        placeholders = ", ".join("?" * len(col_names))
        quoted_cols = ", ".join(f'"{c}"' for c in col_names)
        dst.executemany(
            f'INSERT OR IGNORE INTO "{table}" ({quoted_cols}) VALUES ({placeholders})',
            rows,
        )
        print(f"  seeded {len(rows):3d} rows → {table}")

    # Replace plaintext passwords with bcrypt hashes (skip already-hashed)
    users = dst.execute("SELECT Username, Password FROM Users").fetchall()
    hashed_count = 0
    for username, plaintext in users:
        if plaintext and plaintext.startswith(("$2b$", "$2a$", "$2y$")):
            continue  # already a bcrypt hash
        hashed = hash_password(plaintext or username)
        dst.execute("UPDATE Users SET Password = ? WHERE Username = ?", (hashed, username))
        hashed_count += 1
    print(f"  hashed passwords for {hashed_count} users")

    # Upsert known demo admin account (password: admin123) — always reset
    dst.execute("INSERT OR IGNORE INTO Levels (Level) VALUES ('Administrator')")
    dst.execute(
        "INSERT OR IGNORE INTO Users (Username, Fullname, Level) VALUES (?, ?, ?)",
        ("admin", "Demo Admin", "Administrator"),
    )
    dst.execute(
        "UPDATE Users SET Password = ? WHERE Username = ?",
        (hash_password("admin123"), "admin"),
    )
    print("  upserted demo user  admin / admin123")

    dst.execute("PRAGMA foreign_keys = ON")
    dst.commit()
    src.close()
    dst.close()
    print("\nDone. Launch the app with:  streamlit run main.py")


if __name__ == "__main__":
    main()
