FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# EXPOSE 5000 # Still good to document, Gunicorn will bind to this port
# CMD ["python", "./scripts/app.py"] # Old command

# New command to run Flask app with Gunicorn:
# This assumes your Flask app instance in scripts/app.py is named 'app'
# (e.g., app = Flask(__name__))
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "scripts.app:app"]
