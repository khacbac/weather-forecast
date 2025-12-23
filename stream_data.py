import time
import random
import os
import json
import io
from datetime import datetime
from google.cloud import bigquery

# --- CONFIGURATION ---
# 1. Get the absolute path to the folder where THIS script is saved
# This ensures the script finds the key even if you run it from a different folder
current_dir = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(current_dir, "ai-realtime-project-4de709b969f4.json")

# 2. Tell Google where the key is
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_FILE

# 3. BigQuery Details (Update these!)
PROJECT_ID = "ai-realtime-project"
DATASET_ID = "sensor_data_stream"
TABLE_ID = "live_readings"
full_table_path = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# --- INITIALIZE ---
client = bigquery.Client()

print(f"🚀 Mac is streaming to {full_table_path}...")
print("Press Ctrl+C to stop.")

# Configure the load job (tells GCP we are appending data)
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    write_disposition="WRITE_APPEND",
)

print(f"🚀 Sandbox-friendly stream starting to {full_table_path}...")

try:
    while True:
        # 1. Create the data
        current_time = datetime.utcnow().isoformat()
        random_value = round(random.uniform(20.0, 100.0), 2)
        
        row = {"timestamp": current_time, "device_id": "macbook_sandbox", "value": random_value}
        
        # 2. Convert to 'Newline Delimited JSON' (BigQuery's favorite format)
        # We use io.StringIO to pretend we have a file in memory
        json_data = json.dumps(row) + "\n"
        file_obj = io.StringIO(json_data)
        
        # 3. Batch Upload (This is the FREE way)
        load_job = client.load_table_from_file(
            file_obj, full_table_path, job_config=job_config
        )
        
        # Wait for the upload to finish
        load_job.result() 
        
        print(f"✅ Batch Upload Success: {random_value}")
        time.sleep(5)

except KeyboardInterrupt:
    print("\n🛑 Stream stopped.")