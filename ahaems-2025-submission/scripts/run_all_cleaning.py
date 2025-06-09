import os
import subprocess

# === Configuration ===
base_dir = "/Volumes/jupyter/EMS_QI_Projects/ahaems-2025-submission"
script_dir = os.path.join(base_dir, "scripts")

# === Scripts to run in order ===
scripts = [
    "script_01_fix_quotes.py",
    "script_02_normalize_fields.py",
    "script_03_feature_engineering.py",
    "script_04_export_cleaned.py"
]

# === Run all scripts ===
print("🚀 Running full data cleaning pipeline...\n")

for script in scripts:
    path = os.path.join(script_dir, script)
    print(f"🔧 Running: {script}")
    result = subprocess.run(["python3", path], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Error in {script}:\n{result.stderr}")
        break
    else:
        print(result.stdout)
        print("✅ Completed.\n")

print("🏁 All scripts finished.")