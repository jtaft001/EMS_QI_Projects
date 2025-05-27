#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import requests
import json
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, render_template

# --- Timezone Setup ---
try:
    from zoneinfo import ZoneInfo
except ImportError:
    import pytz
    class PyTZZoneInfo:
        def __init__(self, key): self._tz = pytz.timezone(key)
        def __getattr__(self, name): return getattr(self._tz, name)
    ZoneInfo = PyTZZoneInfo

PACIFIC_TZ_STR = "America/Los_Angeles"
PACIFIC_TZ = ZoneInfo(PACIFIC_TZ_STR) if ZoneInfo else None

# --- Configuration ---
API_KEY = "6011ead8a3f8e2b361a6d9b4f34c9060b1cf18b05e441d9752"
BASE_URL = "https://tempstickapi.com/api/v1"
HEADERS = { "X-API-KEY": API_KEY, "Accept": "application/json" }
ALERT_HISTORY_DAYS = 7
TEMP_OK_LOW = 40.0
TEMP_OK_HIGH = 90.0
TEMP_WARN_LOW = 35.0
TEMP_WARN_HIGH = 95.0
DB_PATH = os.path.expanduser("~/projects/taft_projects/data_analysis/TempStick/data/ninthbrain_incidents.db")

app = Flask(__name__, template_folder='../templates')  


# --- Helper Functions ---
def safe_get_request(url, params=None):
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=20)
        response.raise_for_status()
        if 'application/json' in response.headers.get('Content-Type', ''):
            return response.json()
    except Exception as e:
        app.logger.error(f"Error requesting {url}: {e}")
    return None

def get_sensor_list():
    response = safe_get_request(f"{BASE_URL}/sensors/all")
    return response.get('data', {}).get('items', []) if response else []

def get_recent_alerts(sensor_id):
    url = f"{BASE_URL}/sensor/notifications/{sensor_id}"
    now = datetime.now(timezone.utc)
    params = {
        'startDate': (now - timedelta(days=ALERT_HISTORY_DAYS)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'endDate': now.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    response = safe_get_request(url, params)
    return response.get('data', {}).get('items', []) if response else []

def summarize_alert_periods(alerts):
    grouped = []
    current = None
    alerts.sort(key=lambda x: x.get('created', ''))
    for alert in alerts:
        if not isinstance(alert, dict): continue
        msg, ts, typ = alert.get('event_message', ''), alert.get('created', ''), alert.get('event_type', '')
        if not (typ == 'temperature' and ('above' in msg or 'below' in msg)) or not ts:
            if current: grouped.append(current); current = None
            continue
        if not current:
            current = {'start_utc': ts, 'end_utc': ts, 'type': msg}
        elif current['type'] == msg:
            current['end_utc'] = ts
        else:
            grouped.append(current)
            current = {'start_utc': ts, 'end_utc': ts, 'type': msg}
    if current: grouped.append(current)
    return grouped

def format_timestamp_pacific(ts_str):
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).astimezone(PACIFIC_TZ)
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

    # fallback: strip suffixes like "_ALS"
    if "_" in sensor_name:
        return sensor_name.split("_")[0]

    return sensor_name  # fallback to full name if no pattern matches

# --- Routes ---
@app.route('/')
def index():
    sensors = get_sensor_list()
    return render_template('index.html', sensors=[{
        'id': s.get('sensor_id'),
        'name': s.get('sensor_name', 'Unnamed')
    } for s in sensors if s.get('sensor_id')])

@app.route('/data')
def get_dashboard_data():
    sensors = get_sensor_list()
    sensor_data_list = []
    for sensor_data in sensors:
        if not isinstance(sensor_data, dict): continue
        sid = sensor_data.get('sensor_id')
        name = sensor_data.get('sensor_name', 'Unnamed')
        if not sid: continue
        temp_c = sensor_data.get('last_temp')
        try: temp_c = float(temp_c)
        except: temp_c = None
        temp_f = (temp_c * 9/5 + 32) if temp_c is not None else None
        ts = sensor_data.get('last_checkin')
        status = "no_temp"
        if temp_f is not None:
            if temp_f < TEMP_WARN_LOW: status = "red_low"
            elif temp_f < TEMP_OK_LOW: status = "yellow_low"
            elif temp_f <= TEMP_OK_HIGH: status = "green_ok"
            elif temp_f <= TEMP_WARN_HIGH: status = "yellow_high"
            else: status = "red_high"
        sensor_data_list.append({
            'id': sid, 'name': name, 'temp_f': temp_f, 'temp_c': temp_c,
            'timestamp': format_timestamp_pacific(ts), 'status': status
        })
    return jsonify(sensor_data_list)

@app.route('/alert_matches')
def match_alerts_to_incidents():
    if not os.path.exists(DB_PATH):
        return jsonify({"error": "Database not found"}), 503
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    results = []

    for sensor in get_sensor_list():
        sid = sensor.get("sensor_id")
        name = sensor.get("sensor_name", "Unnamed")
        if not sid:
            continue

        for alert in summarize_alert_periods(get_recent_alerts(sid)):
            start = alert['start_utc']
            try:
                t = datetime.fromisoformat(start.replace("Z", "+00:00")).astimezone(PACIFIC_TZ)
            except:
                continue

            unit = extract_unit_from_sensor(name)
            window = (t - timedelta(minutes=15), t + timedelta(minutes=15))
            time_start_str = window[0].strftime('%Y-%m-%d %H:%M:%S')
            time_end_str   = window[1].strftime('%Y-%m-%d %H:%M:%S')

            # ✅ Debug prints
            print("Sensor name:", name)
            print("Extracted unit:", unit)
            print("Alert start UTC:", start)
            print("Matching window:", time_start_str, "to", time_end_str)

            cursor.execute("""
                SELECT incident_datetime, unit, description, outcome_text
                FROM incident_reports
                WHERE unit = ? AND incident_datetime BETWEEN ? AND ?
                LIMIT 1
            """, (unit, time_start_str, time_end_str))

            row = cursor.fetchone()
            results.append({
                "sensor": name,
                "alert_start": start,
                "alert_type": alert["type"],
                "status": "✅ Matched" if row else "❌ No Match Found",
                "incident_datetime": row[0] if row else None,
                "incident_unit": row[1] if row else unit,
                "description": row[2] if row else None,
                "outcome": row[3] if row else None
            })

    conn.close()
    return jsonify(results)
    
@app.route('/alert_history')
def alert_history_page():
    sensors_with_alerts = []
    if not os.path.exists(DB_PATH):
        return render_template('alert_history.html', sensors_data=[], history_days=ALERT_HISTORY_DAYS)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for sensor in get_sensor_list():
        sid = sensor.get('sensor_id')
        name = sensor.get('sensor_name', 'Unnamed')
        if not sid:
            continue

        periods = []
        for p in summarize_alert_periods(get_recent_alerts(sid)):
            try:
                t = datetime.fromisoformat(p['start_utc'].replace("Z", "+00:00")).astimezone(PACIFIC_TZ)
            except:
                t = None

            unit = extract_unit_from_sensor(name)
            match = {'status': '❌ No Match', 'incident_datetime': None, 'mitigation_efforts': None, 'incident_id': None}
            if t and unit:
                w1, w2 = t - timedelta(minutes=15), t + timedelta(minutes=15)
                cursor.execute("""
                    SELECT incident_datetime, outcome_text, incident_id
                    FROM incident_reports
                    WHERE unit = ? AND incident_datetime BETWEEN ? AND ?
                    LIMIT 1
                """, (unit, w1.strftime('%Y-%m-%d %H:%M:%S'), w2.strftime('%Y-%m-%d %H:%M:%S')))
                r = cursor.fetchone()
                if r:
                    match['status'] = '✅ Matched'
                    match['incident_datetime'] = r[0]
                    match['mitigation_efforts'] = r[1]
                    match['incident_id'] = r[2]

            periods.append({
                'start': format_timestamp_pacific(p['start_utc']),
                'end': format_timestamp_pacific(p['end_utc']),
                'type': p['type'],
                'match_status': match['status'],
                'match_time': match['incident_datetime'],
                'mitigation_efforts': match.get('mitigation_efforts', 'N/A'),
                'incident_id': match.get('incident_id', 'N/A')
            })

        sensors_with_alerts.append({'id': sid, 'name': name, 'alert_periods': periods})

    conn.close()
    return render_template('alert_history.html', sensors_data=sensors_with_alerts, history_days=ALERT_HISTORY_DAYS)
# --- Launch App ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)