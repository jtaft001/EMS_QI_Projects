import os
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# === Load .env ===
dotenv_loaded = load_dotenv(dotenv_path=Path(".env"))
print("✅ .env loaded:", dotenv_loaded)

# === Read env vars ===
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# === Print for confirmation ===
print("🔍 DB_HOST:", DB_HOST)
print("🔍 DB_PORT:", DB_PORT)
print("🔍 DB_USER:", DB_USER)
print("🔍 DB_PASS: (hidden)")
print("🔍 DB_NAME:", DB_NAME)

# === Test DB connection ===
try:
    engine = create_engine(
        f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        future=True  # Required for SQLAlchemy 2.x+
    )

    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()
        print("✅ Connected! PostgreSQL version:", version[0])

except Exception as e:
    print("❌ Connection failed:", e)