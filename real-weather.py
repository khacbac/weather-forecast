import requests
import time
import os
import json
import io
from datetime import datetime
from google.cloud import bigquery

# --- CONFIGURATION ---
current_dir = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(current_dir, "ai-realtime-project-4de709b969f4.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_FILE

# Update these to match your GCP project
PROJECT_ID = "ai-realtime-project"
DATASET_ID = "sensor_data_stream"
TABLE_ID = "real-weather"
full_table_path = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

client = bigquery.Client()

# Set the Da Nang coordinates (or update to your current location)
LAT, LON = 16.047079, 108.206230

def fetch_weather():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
    response = requests.get(url)
    data = response.json()['current']
    return data

print(f"📡 Starting REAL weather feed to {TABLE_ID}...")

try:
    while True:
        # 1. Fetch from Real API
        weather = fetch_weather()
        
        # 2. Structure the data
        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "city": "Danang",
            "temperature": weather['temperature_2m'],
            "humidity": weather['relative_humidity_2m'],
            "wind_speed": weather['wind_speed_10m']
        }
        
        # 3. Batch Upload (Free Sandbox Method)
        json_data = json.dumps(row) + "\n"
        file_obj = io.StringIO(json_data)
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition="WRITE_APPEND",
        )
        
        load_job = client.load_table_from_file(file_obj, full_table_path, job_config=job_config)
        load_job.result() 
        
        print(f"✅ Success: {weather['temperature_2m']}°C recorded at {row['timestamp']}")
        
        # Wait 5 minutes (Professional APIs appreciate a 300s delay)
        time.sleep(300)

except Exception as e:
    print(f"❌ Error: {e}")