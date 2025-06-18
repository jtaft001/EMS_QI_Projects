# config.py

import os
from pathlib import Path
import socket
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# === Load environment variables from .env ===
load_dotenv("/mnt/nasdrive/jupyter/EMS_QI_Projects/ahaems-2025-submission/.env")

# === Database Credentials ===
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# === SQLAlchemy Engine Factory ===
def get_engine():
    if not all([DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME]):
        raise ValueError("Missing one or more required DB environment variables.")
    return create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# === Load Cleaned Data ===
def load_cleaned_data(table="ahaems_cleaned"):
    engine = get_engine()
    return pd.read_sql(f'SELECT * FROM "{table}"', con=engine)

# === Print DB Info for Debugging ===
def print_db_config():
    print("🔧 DB_HOST:", DB_HOST)
    print("🔧 DB_PORT:", DB_PORT)
    print("🔧 DB_USER:", DB_USER)
    print("🔧 DB_NAME:", DB_NAME)

    print("🔧 DEBUG - DB_HOST from env:", os.getenv("DB_HOST"))