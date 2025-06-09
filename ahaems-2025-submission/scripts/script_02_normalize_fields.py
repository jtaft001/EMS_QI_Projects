import os
import pandas as pd

# === Paths ===
base_dir = "/Volumes/jupyter/EMS_QI_Projects/ahaems-2025-submission"
fixed_path = os.path.join(base_dir, "data", "interim", "fixed_quotes.csv")
normalized_path = os.path.join(base_dir, "data", "interim", "normalized.csv")

# === Load fixed file ===
print("📥 Loading fixed dataset...")
df = pd.read_csv(fixed_path, dtype=str, on_bad_lines="skip", low_memory=False)

# === Normalize headers ===
print("🧼 Normalizing column names...")
df.columns = df.columns.str.strip().str.replace("\n", " ").str.replace(" +", " ", regex=True)
df.columns = df.columns.str.replace(r'^\ufeff', '', regex=True)  # Strip BOM if present

# === Normalize strings ===
print("🔧 Cleaning string fields...")
for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].str.strip().str.lower()

# === Save normalized ===
os.makedirs(os.path.dirname(normalized_path), exist_ok=True)
df.to_csv(normalized_path, index=False)
print("\n🔎 Columns after normalization:")
for col in df.columns:
    print(f"- {col}")
print(f"✅ Normalized dataset saved to: {normalized_path}")