from flask import Blueprint, jsonify, render_template
from helpers import safe_get_request, format_timestamp_pacific
from config import HEADERS, TEMP_OK_LOW, TEMP_OK_HIGH, TEMP_WARN_LOW, TEMP_WARN_HIGH

sensors_bp = Blueprint('sensors', __name__)

def get_sensor_list():
    response = safe_get_request("https://tempstickapi.com/api/v1/sensors/all", headers=HEADERS)
    return response.get('data', {}).get('items', []) if response else []

@sensors_bp.route('/')
def index():
    sensors = get_sensor_list()
    return render_template('index.html', sensors=[{
        'id': s.get('sensor_id'),
        'name': s.get('sensor_name', 'Unnamed')
    } for s in sensors if s.get('sensor_id')])

@sensors_bp.route('/data')
def get_dashboard_data():
    sensors = get_sensor_list()
    sensor_data_list = []
    for sensor_data in sensors:
        if not isinstance(sensor_data, dict):
            continue
        sid = sensor_data.get('sensor_id')
        name = sensor_data.get('sensor_name', 'Unnamed')
        if not sid:
            continue
        temp_c = sensor_data.get('last_temp')
        try:
            temp_c = float(temp_c)
        except:
            temp_c = None
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
            'id': sid,
            'name': name,
            'temp_f': temp_f,
            'temp_c': temp_c,
            'timestamp': format_timestamp_pacific(ts),
            'status': status
        })
    return jsonify(sensor_data_list)