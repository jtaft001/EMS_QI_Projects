# config.py

import pandas as pd
from sqlalchemy import create_engine
from project_paths import DB_HOST

# === Database Engine ===
def get_engine():
    """
    Create a SQLAlchemy engine using the resolved DB_HOST.
    """
    return create_engine(f"postgresql://jtaft:GunnersMate2003!@{DB_HOST}:5432/datalake")

# === Utility: Load cleaned dataset ===
def load_cleaned_data(table="ahaems_cleaned"):
    """
    Load a table from the connected PostgreSQL database.
    Default: 'ahaems_cleaned'
    """
    engine = get_engine()
    return pd.read_sql(f"SELECT * FROM {table}", con=engine)

# === [Placeholder] AHA Stroke ICDs ===
# STROKE_ICD_PREFIXES = ["I60", "I61", "I62", "I63", "G45", "G46"]

# === [Placeholder] Cardiac Arrest Codes ===
# CARDIAC_ARREST_CODES = ["3001003", "3001005"]

# === [Placeholder] Exclusion Acuity Code (Dead w/ Resuscitation) ===
# EXCLUDE_ACUITY_CODE = "4219909"

# === [Placeholder] Utility: Apply AHA Stroke Filters ===
# def filter_stroke_cases(df):
#     ...