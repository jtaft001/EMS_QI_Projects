import requests
from flask import current_app
from datetime import datetime

def safe_get_request(url, headers=None, params=None, timeout=20):
    """
    Make a safe GET request, return JSON if possible,
    else None and log error in Flask app logger.
    """
    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        if 'application/json' in response.headers.get('Content-Type', ''):
            return response.json()
    except Exception as e:
        try:
            current_app.logger.error(f"Error requesting {url}: {e}")
        except RuntimeError:
            print(f"Error requesting {url}: {e}")
    return None

def format_timestamp_pacific(ts_str, pacific_tz):
    """
    Format UTC timestamp string to Pacific timezone string.
    """
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).astimezone(pacific_tz)
        return dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception:
        return ts_str

def extract_unit_from_sensor(sensor_name):
    """
    Extracts the numeric unit identifier from sensor name.
    Examples:
      - "23-14_ALS" => "23-14"
      - "Medic 42-19 Fridge" => "42-19"
    """
    parts = sensor_name.split()
    for part in parts:
        if "-" in part and part.replace("-", "").isdigit():
            return part  # match like "42-19"
    if "_" in sensor_name:
        return sensor_name.split("_")[0]
    return sensor_name