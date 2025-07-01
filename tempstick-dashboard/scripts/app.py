#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, render_template

from helpers import safe_get_request, format_timestamp_pacific, extract_unit_from_sensor
from config import (
    PACIFIC_TZ_STR, API_KEY, BASE_URL, HEADERS,
    ALERT_HISTORY_DAYS, TEMP_OK_LOW, TEMP_OK_HIGH,
    TEMP_WARN_LOW, TEMP_WARN_HIGH, DB_PATH
)

from alerts import alerts_bp
from sensors import sensors_bp

# Flask app setup
app = Flask(__name__, template_folder='../templates')

# Register blueprints for modular routing
app.register_blueprint(alerts_bp)
app.register_blueprint(sensors_bp)

# Timezone setup with fallback for older Python versions
try:
    from zoneinfo import ZoneInfo
except ImportError:
    import pytz
    class PyTZZoneInfo:
        def __init__(self, key): self._tz = pytz.timezone(key)
        def __getattr__(self, name): return getattr(self._tz, name)
    ZoneInfo = PyTZZoneInfo

PACIFIC_TZ = ZoneInfo(PACIFIC_TZ_STR) if ZoneInfo else None


# (Optional) If you want to keep these core functions in app.py too,
# but ideally these would be moved to helpers or relevant blueprints.

def get_sensor_list():
    """Fetch all sensors assigned to the account."""
    response = safe_get_request(f"{BASE_URL}/sensors/all", headers=HEADERS)
    return response.get('data', {}).get('items', []) if response else []

def get_recent_alerts(sensor_id):
    """Fetch recent alerts for a specific sensor within the alert history window."""
    url = f"{BASE_URL}/sensor/notifications/{sensor_id}"
    now = datetime.now(timezone.utc)
    params = {
        'startDate': (now - timedelta(days=ALERT_HISTORY_DAYS)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'endDate': now.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    response = safe_get_request(url, headers=HEADERS, params=params)
    return response.get('data', {}).get('items', []) if response else []

def summarize_alert_periods(alerts):
    """Group consecutive alerts of the same message type into alert periods."""
    grouped = []
    current = None
    alerts.sort(key=lambda x: x.get('created', ''))
    for alert in alerts:
        if not isinstance(alert, dict):
            continue
        msg = alert.get('event_message', '')
        ts = alert.get('created', '')
        typ = alert.get('event_type', '')
        if not (typ == 'temperature' and ('above' in msg or 'below' in msg)) or not ts:
            if current:
                grouped.append(current)
                current = None
            continue

        if not current:
            current = {'start_utc': ts, 'end_utc': ts, 'type': msg}
        elif current['type'] == msg:
            current['end_utc'] = ts
        else:
            grouped.append(current)
            current = {'start_utc': ts, 'end_utc': ts, 'type': msg}
    if current:
        grouped.append(current)
    return grouped


# Main entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)