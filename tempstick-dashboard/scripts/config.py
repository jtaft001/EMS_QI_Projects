import os
from pathlib import Path
from dotenv import load_dotenv

# Locate .env in the project root (two levels up if config.py is inside scripts/)
dotenv_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path)

# Timezone string for Pacific Time
PACIFIC_TZ_STR = "America/Los_Angeles"

# Now environment variables will be loaded from .env
API_KEY = os.environ.get("API_KEY")
BASE_URL = os.environ.get("BASE_URL", "https://tempstickapi.com/api/v1")

if not API_KEY:
    raise ValueError("Missing API_KEY environment variable.")

# HTTP headers for API requests
HEADERS = {
    "X-API-KEY": API_KEY,
    "Accept": "application/json"
}

# Alert and temperature thresholds
ALERT_HISTORY_DAYS = 7
TEMP_OK_LOW = 40.0
TEMP_OK_HIGH = 90.0
TEMP_WARN_LOW = 35.0
TEMP_WARN_HIGH = 95.0

# Path to your local incident database
DB_PATH = os.path.expanduser("~/projects/taft_projects/data_analysis/TempStick/data/ninthbrain_incidents.db")