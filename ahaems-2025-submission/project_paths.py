import os
import socket
from pathlib import Path

# === Detect Current Host Environment ===
hostname = socket.gethostname()
home_path = Path.home()

# === Resolve BASE_DIR Dynamically ===
if "jovyan" in str(home_path):  # Remote Jupyter NAS (e.g., Docker container or JupyterHub)
    BASE_DIR = Path("/home/jovyan/work/EMS_QI_Projects/ahaems-2025-submission")
elif Path("/Volumes/jupyter/EMS_QI_Projects/ahaems-2025-submission").exists():  # Mac (NAS mounted)
    BASE_DIR = Path("/Volumes/jupyter/EMS_QI_Projects/ahaems-2025-submission")
elif Path("/mnt/nasdrive/jupyter/EMS_QI_Projects/ahaems-2025-submission").exists():  # SSH directly on NAS
    BASE_DIR = Path("/mnt/nasdrive/jupyter/EMS_QI_Projects/ahaems-2025-submission")
else:  # Fallback: infer from script location
    BASE_DIR = Path(__file__).resolve().parents[1]

# === Standard Directory Constants ===
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_CLEANED_DIR = BASE_DIR / "data" / "cleaned"
OUTPUT_DIR = BASE_DIR / "output"
FALLOUTS_DIR = OUTPUT_DIR / "fallouts"
REPORTS_DIR = OUTPUT_DIR / "reports"
SCRIPTS_DIR = BASE_DIR / "scripts"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

# === Database Host Resolver ===
# Default: use Docker bridge IP for internal containers
DB_HOST = "postgres"

# If running on the host directly (e.g., taft-server), use localhost
if "server" in hostname:
    DB_HOST = "localhost"

# === Utility: Print Path Info ===
def print_project_paths():
    print("🔧 Detected Environment:", hostname)
    print("📂 BASE_DIR:", BASE_DIR)
    print("📁 DATA_RAW_DIR:", DATA_RAW_DIR)
    print("📁 DATA_CLEANED_DIR:", DATA_CLEANED_DIR)
    print("📁 FALLOUTS_DIR:", FALLOUTS_DIR)
    print("📁 REPORTS_DIR:", REPORTS_DIR)
    print("📁 NOTEBOOKS_DIR:", NOTEBOOKS_DIR)
    print("📁 SCRIPTS_DIR:", SCRIPTS_DIR)

# === Utility: Create Output Directories ===
def create_output_dirs():
    for path in [OUTPUT_DIR, FALLOUTS_DIR, REPORTS_DIR, DATA_CLEANED_DIR]:
        path.mkdir(parents=True, exist_ok=True)

# === Utility: Full Environment Summary ===
def environment_summary():
    print_project_paths()
    print("🌐 DB_HOST:", DB_HOST)
    print("🖥 Hostname:", hostname)