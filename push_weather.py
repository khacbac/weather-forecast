#!/usr/bin/env python3
"""
Weather Data Pusher for GCP VM Cron Job
Fetches weather data from Open-Meteo API and pushes to BigQuery.
Designed to run once per execution (suitable for cron).
"""

import requests
import os
import json
import io
import sys
from datetime import datetime
from google.cloud import bigquery

# --- CONFIGURATION ---
# Try to find the key file in the same directory as the script
current_dir = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(current_dir, "ai-realtime-project-4de709b969f4.json")

# If key file doesn't exist in script dir, try environment variable or default GCP auth
if os.path.exists(KEY_FILE):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_FILE
else:
    # On GCP VM, you might use default service account or set via env var
    key_file_env = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if key_file_env and os.path.exists(key_file_env):
        print(f"Using credentials from environment: {key_file_env}")
    else:
        print("Warning: No credentials file found. Using default GCP authentication.")

# Update these to match your GCP project
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "ai-realtime-project")
DATASET_ID = os.getenv("BIGQUERY_DATASET", "sensor_data_stream")
TABLE_ID = os.getenv("BIGQUERY_TABLE", "real-weather")
full_table_path = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Set the Da Nang coordinates (or update to your current location)
LAT = float(os.getenv("WEATHER_LAT", "16.047079"))
LON = float(os.getenv("WEATHER_LON", "108.206230"))
CITY = os.getenv("WEATHER_CITY", "Danang")


def fetch_weather():
    """Fetch current weather data from Open-Meteo API."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()['current']
        return data
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching weather data: {e}", file=sys.stderr)
        raise


def push_to_bigquery(row):
    """Push a single row to BigQuery."""
    try:
        client = bigquery.Client()
        
        # Batch Upload (Free Sandbox Method)
        json_data = json.dumps(row) + "\n"
        file_obj = io.StringIO(json_data)
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition="WRITE_APPEND",
        )
        
        load_job = client.load_table_from_file(file_obj, full_table_path, job_config=job_config)
        load_job.result()  # Wait for the job to complete
        
        return True
    except Exception as e:
        print(f"❌ Error pushing to BigQuery: {e}", file=sys.stderr)
        raise


def main():
    """Main function to fetch and push weather data."""
    print(f"📡 Pushing weather data to {full_table_path}...")
    
    try:
        # 1. Fetch from Real API
        weather = fetch_weather()
        
        # 2. Structure the data
        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "city": CITY,
            "temperature": weather['temperature_2m'],
            "humidity": weather['relative_humidity_2m'],
            "wind_speed": weather['wind_speed_10m']
        }
        
        # 3. Push to BigQuery
        push_to_bigquery(row)
        
        print(f"✅ Success: {weather['temperature_2m']}°C recorded at {row['timestamp']}")
        return 0
        
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

