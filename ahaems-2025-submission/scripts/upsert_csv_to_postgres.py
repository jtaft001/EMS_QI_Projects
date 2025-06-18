import pandas as pd
import psycopg2
from io import StringIO
import os

# --- CONFIG ---
CSV_PATH = "/Volumes/nasdrive/jupyter/data/raw/AHA Measure Dataset (Bulk)_Export.csv"
TABLE_NAME = "ahaems_raw"
DB_PARAMS = {
    "host": "100.124.164.93",
    "port": 5432,
    "dbname": "datalake",
    "user": "jtaft",
    "password": "GunnersMate2003!"
}

# --- VERIFY FILE EXISTS ---
if not os.path.isfile(CSV_PATH):
    raise FileNotFoundError(f"❌ File not found at: {CSV_PATH}")
print(f"📁 File found: {CSV_PATH}")

# --- LOAD CSV ---
print("📥 Loading CSV...")
df = pd.read_csv(CSV_PATH, low_memory=False)
print(f"✅ Loaded {len(df):,} rows with {len(df.columns)} columns.")

# --- COLUMN MAP ---
column_map = {
    "Incident Unit Notified By Dispatch Date Time (eTimes.03)": "Incident Unit Notified By Dispatch Date Time (eTimes.03)",
    "Response EMS Response Number (eResponse.04)": "Response EMS Response Number (eResponse.04)",
    "Patient Age (ePatient.15)": "Patient Age (ePatient.15)",
    "Patient Age Units (ePatient.16)": "Patient Age Units (ePatient.16)",
    "Situation Provider Primary Impression Code And Description (eSituation.11)": "Primary Impression",
    "Situation Provider Secondary Impression Description And Code (eSituation.12)": "Secondary Impression",
    "Response Type Of Service Requested With Code (eResponse.05)": "Response Type Of Service Requested With Code (eResponse.05)",
    "Disposition Final Patient Acuity Code (eDisposition.19)": "Disposition Final Patient Acuity Code (eDisposition.19)",
    "Situation Symptom Onset Date Time (eSituation.01)": "Situation Symptom Onset Date Time (eSituation.01)",
    "Situation Last Known Well Date Time (eSituation.18)": "Situation Last Known Well Date Time (eSituation.18)",
    "Vitals Signs Taken Date Time (eVitals.01)": "Vitals Signs Taken Date Time (eVitals.01)",
    "Vitals ECG Type (eVitals.04)": "Vitals ECG Type (eVitals.04)",
    "Patient Initial Cardiac Rhythm ECG Finding List (eVitals.03)": "Patient Initial Cardiac Rhythm ECG Finding List (eVitals.03)",
    "Patient Cincinnati Stroke Scale Used (eVitals.30)": "Patient Cincinnati Stroke Scale Used (eVitals.30)",
    "Patient Initial Stroke Scale Score (eVitals.29)": "Patient Initial Stroke Scale Score (eVitals.29)",
    "Destination STEMI Team Activation Date Time (eDisposition.24)": "Destination STEMI Team Activation Date Time (eDisposition.24)",
    "Destination STEMI Team Pre-arrival Activation (eDisposition.24)": "Destination STEMI Team Pre-arrival Activation (eDisposition.24)",
    "Destination Stroke Team Activation Date Time (eDisposition.24)": "Destination Stroke Team Activation Date Time (eDisposition.24)",
    "Destination Stroke Team Pre-arrival Activation (eDisposition.24)": "Stroke Alert",
    "Cardiac Arrest During EMS Event With Code (eArrest.01)": "Cardiac Arrest During EMS Event With Code (eArrest.01)",
    "Patient Medication Allergy Description (eHistory.06)": "Patient Medication Allergy Description (eHistory.06)",
    "Medication Given or Administered Description And RXCUI Code (eMedications.03)": "Medication Given or Administered Description And RXCUI Code (eM",
    "Response Type Of Scene Delay (eResponse.10)": "Response Type Of Scene Delay (eResponse.10)",
    "Disposition Type Of Destination (eDisposition.21)": "Disposition Type Of Destination (eDisposition.21)",
    "Airway Decision To Manage Patient With An Invasive Airway Date Time (eAirway.10)": "Airway Decision To Manage Patient With An Invasive Airway Date ",
    "Transport Disposition (3.4=itDisposition.102/3.5=eDisposition.30)": "Transport Disposition",
    "Unit Arrived At Patient To First 12 Lead ECG Vitals Reading In Minutes": "Unit Arrived At Patient To First 12 Lead ECG Vitals Reading In ",
    "Unit Arrived At Patient To First 12 Lead Procedure In Minutes": "Unit Arrived At Patient To First 12 Lead Procedure In Minutes",
    "Procedure Performed Description And Code (eProcedures.03)": "Procedure Performed Description And Code (eProcedures.03)",
    "Patient Blood Glucose Level Count (eVitals.18)": "Patient Blood Glucose Level Count (eVitals.18)",
    "Patient Care Report Narrative (eNarrative.01)": "Patient Care Report Narrative (eNarrative.01)"
}

# --- RENAME & FILTER ---
df = df.rename(columns=column_map)
df = df[list(column_map.values())]

# --- CONNECT TO POSTGRES ---
print("🔗 Connecting to PostgreSQL...")
conn = psycopg2.connect(**DB_PARAMS)

with conn:
    with conn.cursor() as cur:
        # Optional: Check for locks
        cur.execute(f"""
            SELECT pid, query_start, query
            FROM pg_stat_activity
            WHERE state = 'active'
              AND query ILIKE '%{TABLE_NAME}%'
              AND pid <> pg_backend_pid()
        """)
        active_locks = cur.fetchall()
        if active_locks:
            print("❌ Upload blocked: active queries on the table:")
            for pid, start, query in active_locks:
                print(f" - PID {pid} | since {start} | query: {query[:100]}...")
            exit(1)

        # --- TRUNCATE TABLE ---
        print(f"🧹 Truncating table: {TABLE_NAME}")
        cur.execute(f"TRUNCATE TABLE {TABLE_NAME} RESTART IDENTITY;")

        # --- COPY TO DB ---
        print("🚚 Uploading data...")
        buffer = StringIO()
        df.to_csv(buffer, index=False, header=False)
        buffer.seek(0)
        columns = ", ".join(f'"{col}"' for col in df.columns)
        cur.copy_expert(f"COPY {TABLE_NAME} ({columns}) FROM STDIN WITH CSV", buffer)

        print("✅ Upload complete!")