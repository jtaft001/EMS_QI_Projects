import os
import csv

# === Paths ===
base_dir = "/Volumes/jupyter/EMS_QI_Projects/ahaems-2025-submission"
raw_path = os.path.join(base_dir, "data", "raw", "AHA Measure Dataset (Bulk)_Export.csv")
fixed_path = os.path.join(base_dir, "data", "interim", "fixed_quotes.csv")
os.makedirs(os.path.dirname(fixed_path), exist_ok=True)

# === Fix unbalanced quotes and write to new file ===
print("🔧 Fixing unbalanced quotes...")
with open(raw_path, "r", encoding="utf-8", errors="ignore") as infile, \
     open(fixed_path, "w", newline='', encoding="utf-8") as outfile:
    reader = infile.readlines()
    writer = csv.writer(outfile)

    for i, line in enumerate(reader, 1):
        if line.count('"') % 2 != 0:
            line = line.replace('"', '')  # Remove unbalanced quotes
        parts = list(csv.reader([line]))[0]  # Split properly into fields
        writer.writerow(parts)

print(f"✅ Quotes fixed and saved to: {fixed_path}")