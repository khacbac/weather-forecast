import time
import random
import os
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

try:
    while True:
        # Generate Data
        current_time = datetime.utcnow().isoformat()
        random_value = round(random.uniform(20.0, 100.0), 2)
        
        # Prepare the row
        rows_to_insert = [
            {"timestamp": current_time, "device_id": "macbook_pro", "value": random_value}
        ]
        
        # PUSH to GCP
        errors = client.insert_rows_json(full_table_path, rows_to_insert)
        
        if not errors:
            print(f"✅ Sent: {random_value} at {current_time}")
        else:
            print(f"❌ GCP Error: {errors}")
            
        time.sleep(5)

except KeyboardInterrupt:
    print("\n🛑 Stream stopped.")