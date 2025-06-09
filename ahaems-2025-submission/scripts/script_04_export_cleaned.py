import os
import pandas as pd

# === Paths ===
base_dir = "/Volumes/jupyter/EMS_QI_Projects/ahaems-2025-submission"
features_path = os.path.join(base_dir, "data", "interim", "features.csv")
cleaned_path = os.path.join(base_dir, "data", "cleaned", "cleaned_AHA_measure_dataset.csv")
os.makedirs(os.path.dirname(cleaned_path), exist_ok=True)

# === Load dataset with features ===
print("📥 Loading feature-enhanced dataset...")
df = pd.read_csv(features_path, dtype=str, low_memory=False)

# === Final column selection ===
print("📦 Selecting final columns...")
columns_to_keep = [
    "UniqueIncidentKey",
    "Response EMS Response Number (eResponse.04)",
    "Incident Unit Notified By Dispatch Date Time (eTimes.03)",
    "Patient Age (ePatient.15)",
    "Patient Age Units (ePatient.16)",
    "Situation Provider Primary Impression Code And Description (eSituation.11)",
    "Situation Provider Secondary Impression Description And Code (eSituation.12)",
    "Transport Disposition (3.4=itDisposition.102/3.5=eDisposition.30)",
    "Destination Stroke Team Pre-arrival Activation (eDisposition.24)",
    "Destination STEMI Team Activation Date Time (eDisposition.24)",
    "Destination STEMI Team Pre-arrival Activation (eDisposition.24)",
    "Destination Stroke Team Activation Date Time (eDisposition.24)",
    "Destination Stroke Team Pre-arrival Activation (eDisposition.24)",
    "Situation Last Known Well Date Time (eSituation.18)",
    "Situation Symptom Onset Date Time (eSituation.01)",
    "Vitals Signs Taken Date Time (eVitals.01)",
    "Cardiac Arrest During EMS Event With Code (eArrest.01)",
    "Disposition Final Patient Acuity Code (eDisposition.19)",
    "Response Type Of Service Requested With Code (eResponse.05)",
    "Patient Blood Glucose Level Count (eVitals.18)",
    "Patient Cincinnati Stroke Scale Used (eVitals.30)",
    "Unit Arrived At Patient To First 12 Lead ECG Vitals Reading In Minutes",
    "Unit Arrived At Patient To First 12 Lead Procedure In Minutes",
    "Medication Given or Administered Description And RXCUI Code (eMedications.03)",
    "Aspirin Given"
]
df = df[[col for col in columns_to_keep if col in df.columns]]

# === Save cleaned dataset ===
print("💾 Saving cleaned dataset...")
df.to_csv(cleaned_path, index=False)
print(f"✅ Cleaned dataset saved to:\n{cleaned_path}")