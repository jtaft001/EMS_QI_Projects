import os
import pandas as pd

# === Paths ===
base_dir = "/Volumes/jupyter/EMS_QI_Projects/ahaems-2025-submission"
normalized_path = os.path.join(base_dir, "data", "interim", "normalized.csv")
features_path = os.path.join(base_dir, "data", "interim", "features.csv")

# === Load normalized dataset ===
print("📥 Loading normalized dataset...")
df = pd.read_csv(normalized_path, dtype=str, low_memory=False)

# === Clean up column names (remove any lingering quotes) ===
df.columns = df.columns.str.strip().str.strip('"')

# === Convert glucose values (handle LOW/HIGH as numeric) ===
print("🩸 Converting glucose values...")
if "Patient Blood Glucose Level Count (eVitals.18)" in df.columns:
    df["Patient Blood Glucose Level Count (eVitals.18)"] = pd.to_numeric(
        df["Patient Blood Glucose Level Count (eVitals.18)"].replace({"low": 40, "high": 500}),
        errors="coerce"
    )

# === Flag aspirin administration ===
print("💊 Flagging aspirin use...")
if "Medication Given or Administered Description And RXCUI Code (eMedications.03)" in df.columns:
    df["Aspirin Given"] = df["Medication Given or Administered Description And RXCUI Code (eMedications.03)"] \
        .str.contains("aspirin", case=False, na=False)

# === Create UniqueIncidentKey ===
print("🆔 Creating UniqueIncidentKey...")
if (
    "Response EMS Response Number (eResponse.04)" in df.columns and
    "Incident Unit Notified By Dispatch Date Time (eTimes.03)" in df.columns
):
    df["UniqueIncidentKey"] = (
        df["Response EMS Response Number (eResponse.04)"].astype(str) + " | " +
        df["Incident Unit Notified By Dispatch Date Time (eTimes.03)"].astype(str)
    )

# === Save the enhanced dataset ===
print("💾 Saving feature-enhanced dataset...")
os.makedirs(os.path.dirname(features_path), exist_ok=True)
df.to_csv(features_path, index=False)
print(f"✅ Feature-enhanced dataset saved to: {features_path}")