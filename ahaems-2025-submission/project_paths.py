# project_paths.py

import os
from pathlib import Path
import socket

# === Detect Environment ===
hostname = socket.gethostname()
home_path = Path.home()

# === Set Base Directory Dynamically ===
if "jovyan" in str(home_path):  # Remote Jupyter NAS
    BASE_DIR = Path("/home/jovyan/work/EMS_QI_Projects/ahaems-2025-submission")
elif Path("/Volumes/jupyter/EMS_QI_Projects/ahaems-2025-submission").exists():  # Mounted NAS on Mac
    BASE_DIR = Path("/Volumes/jupyter/EMS_QI_Projects/ahaems-2025-submission")
else:  # Fallback: assume running locally somewhere else (like dev laptop)
    BASE_DIR = Path(__file__).resolve().parents[1]

# === Common Directories ===
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_CLEANED_DIR = BASE_DIR / "data" / "cleaned"
OUTPUT_DIR = BASE_DIR / "output"
FALLOUTS_DIR = OUTPUT_DIR / "fallouts"
REPORTS_DIR = OUTPUT_DIR / "reports"
SCRIPTS_DIR = BASE_DIR / "scripts"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

# === Utility Example ===
def print_project_paths():
    print("🔧 Current Environment:", hostname)
    print("📂 Base Path:", BASE_DIR)
    print("📄 Data (Raw):", DATA_RAW_DIR)
    print("📄 Data (Cleaned):", DATA_CLEANED_DIR)
    print("📄 Output:", OUTPUT_DIR)