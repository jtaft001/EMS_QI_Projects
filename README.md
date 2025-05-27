# 🌡️ TempStick Dashboard

This project provides a self-hosted dashboard and alert system for monitoring TempStick WiFi temperature/humidity sensors. It is structured as a Flask app with data ingestion, alert processing, and historical reporting capabilities.

---

## 📁 Project Structure
tempstick-dashboard/
├── data/ # Sensor data, alert database, config files
├── notebooks/ # Development and analysis notebooks
├── scripts/ # Python scripts and Flask app logic
├── templates/ # HTML templates for the dashboard
├── static/ # CSS and JavaScript (e.g. Gauge.js)
├── output/ # Generated reports, PDFs, and CSVs
└── README.md # Project overview


---

## 🚀 Features

- Live dashboard view using Flask + Jinja2 templates
- Real-time temperature gauge (via Gauge.js)
- Historical alert summaries with CSV and PDF export
- Custom thresholds for high/low temperature alerts
- SQLite-based alert logging
- REST API integration with TempStick sensors

---

## 🧪 Getting Started

### 1. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate


2. Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
3. Run the Flask app
bash
Copy
Edit
cd scripts/
python app.py
The app will be available at http://127.0.0.1:5000/.

🔐 Security Note
Do not commit api_keys.json or other secrets. It is located in:

bash
Copy
Edit
tempstick-dashboard/data/api_keys.json
This file should be excluded via .gitignore.

📝 TODO
 Dockerize the dashboard for easier deployment

 Integrate automatic PDF/CSV generation on schedule

 Add Grafana/Prometheus support for advanced metrics

👤 Author
Jonathan Taft
Butte County EMS — QA/PI Coordinator
GitHub: @jtaft001
