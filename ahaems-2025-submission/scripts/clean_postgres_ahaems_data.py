import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import os

# === DB Connection Settings ===
DB_HOST = "100.124.164.93"
DB_PORT = "5432"
DB_NAME = "datalake"
DB_USER = "jtaft"
DB_PASSWORD = "GunnersMate2003!"

# === Connect to PostgreSQL ===
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

print("📥 Reading data from ahaems_raw...")
df = pd.read_sql("SELECT * FROM ahaems_raw", con=engine)

# === Column Normalization ===
print("🧼 Normalizing column names...")
df.columns = df.columns.str.strip().str.replace("\n", " ").str.replace(" +", " ", regex=True)

# === Normalize string fields ===
print("🔧 Cleaning string fields...")
for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].astype(str).str.strip()

# === Convert glucose values ===
print("🩸 Converting blood glucose values...")
if "Patient Blood Glucose Level Count (eVitals.18)" in df.columns:
    df["Patient Blood Glucose Level Count (eVitals.18)"] = (
        df["Patient Blood Glucose Level Count (eVitals.18)"]
        .replace({"low": "40", "high": "500"})
        .astype(float)
    )

# === Flag aspirin administration ===
print("💊 Flagging aspirin...")
if "Medication Given or Administered Description And RXCUI Code (eM" in df.columns:
    df["Aspirin Given"] = df["Medication Given or Administered Description And RXCUI Code (eM"] \
        .str.lower().str.contains("aspirin|asa|687078", na=False)
else:
    df["Aspirin Given"] = False  # default to False if column not present

# === Create UniqueIncidentKey ===
print("🆔 Creating UniqueIncidentKey...")
df["UniqueIncidentKey"] = (
    df.get("Response EMS Response Number (eResponse.04)", "").astype(str) + " | " +
    df.get("Incident Unit Notified By Dispatch Date Time (eTimes.03)", "").astype(str)
)

# === Trim columns ===
print("📦 Selecting final columns...")
columns_to_keep = [
    "UniqueIncidentKey",
    "Response EMS Response Number (eResponse.04)",
    "Incident Unit Notified By Dispatch Date Time (eTimes.03)",
    "Patient Age (ePatient.15)",
    "Patient Age Units (ePatient.16)",
    "Primary Impression",
    "Secondary Impression",
    "Transport Disposition",
    "Destination Stroke Team Pre-arrival Activation (eDisposition.24)",
    "Destination STEMI Team Activation Date Time (eDisposition.24)",
    "Destination STEMI Team Pre-arrival Activation (eDisposition.24)",
    "Destination Stroke Team Activation Date Time (eDisposition.24)",
    "Stroke Alert",
    "Situation Last Known Well Date Time (eSituation.18)",
    "Situation Symptom Onset Date Time (eSituation.01)",
    "Vitals Signs Taken Date Time (eVitals.01)",
    "Cardiac Arrest During EMS Event With Code (eArrest.01)",
    "Disposition Final Patient Acuity Code (eDisposition.19)",
    "Response Type Of Service Requested With Code (eResponse.05)",
    "Patient Blood Glucose Level Count (eVitals.18)",
    "Patient Cincinnati Stroke Scale Used (eVitals.30)",
    "Unit Arrived At Patient To First 12 Lead ECG Vitals Reading In",
    "Unit Arrived At Patient To First 12 Lead Procedure In Minutes",
    "Medication Given or Administered Description And RXCUI Code (eM",
    "Aspirin Given",
    "Patient Initial Stroke Scale Score (eVitals.29)"
]

df = df[[col for col in columns_to_keep if col in df.columns]]

# === Write to New Table ===
print("💾 Writing cleaned data to PostgreSQL table: ahaems_cleaned...")
df.to_sql("ahaems_cleaned", con=engine, index=False, if_exists="replace")
print("✅ Done.")