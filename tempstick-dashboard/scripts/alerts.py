from flask import Blueprint, jsonify, render_template
import os
import sqlite3
from datetime import datetime, timedelta

from helpers import safe_get_request, format_timestamp_pacific, extract_unit_from_sensor
from config import HEADERS, ALERT_HISTORY_DAYS, DB_PATH, PACIFIC_TZ

alerts_bp = Blueprint('alerts', __name__)

def get_sensor_list():
    response = safe_get_request(f"https://tempstickapi.com/api/v1/sensors/all", headers=HEADERS)
    return response.get('data', {}).get('items', []) if response else []

def get_recent_alerts(sensor_id):
    url = f"https://tempstickapi.com/api/v1/sensor/notifications/{sensor_id}"
    now = datetime.now(tz=None).astimezone()
    params = {
        'startDate': (now - timedelta(days=ALERT_HISTORY_DAYS)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'endDate': now.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    response = safe_get_request(url, headers=HEADERS, params=params)
    return response.get('data', {}).get('items', []) if response else []

def summarize_alert_periods(alerts):
    grouped = []
    current = None
    alerts.sort(key=lambda x: x.get('created', ''))
    for alert in alerts:
        if not isinstance(alert, dict):
            continue
        msg, ts, typ = alert.get('event_message', ''), alert.get('created', ''), alert.get('event_type', '')
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

@alerts_bp.route('/alert_matches')
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
            except Exception:
                continue

            unit = extract_unit_from_sensor(name)
            window = (t - timedelta(minutes=15), t + timedelta(minutes=15))
            time_start_str = window[0].strftime('%Y-%m-%d %H:%M:%S')
            time_end_str = window[1].strftime('%Y-%m-%d %H:%M:%S')

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

@alerts_bp.route('/alert_history')
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
            except Exception:
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
                'start': format_timestamp_pacific(p['start_utc'], PACIFIC_TZ),
                'end': format_timestamp_pacific(p['end_utc'], PACIFIC_TZ),
                'type': p['type'],
                'match_status': match['status'],
                'match_time': match['incident_datetime'],
                'mitigation_efforts': match.get('mitigation_efforts', 'N/A'),
                'incident_id': match.get('incident_id', 'N/A')
            })

        sensors_with_alerts.append({'id': sid, 'name': name, 'alert_periods': periods})

    conn.close()
    return render_template('alert_history.html', sensors_data=sensors_with_alerts, history_days=ALERT_HISTORY_DAYS)