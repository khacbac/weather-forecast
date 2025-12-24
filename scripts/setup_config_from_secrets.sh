#!/bin/bash
# Script to generate config.json from environment variables or GitHub Secrets
# Usage: ./scripts/setup_config_from_secrets.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_EXAMPLE="$PROJECT_DIR/config.json.example"
CONFIG_FILE="$PROJECT_DIR/config.json"

if [ ! -f "$CONFIG_EXAMPLE" ]; then
    echo "❌ Error: config.json.example not found at $CONFIG_EXAMPLE"
    exit 1
fi

echo "📝 Creating config.json from template and environment variables..."

# Copy example to config
cp "$CONFIG_EXAMPLE" "$CONFIG_FILE"

# Use Python to update config with environment variables
export CONFIG_FILE_PATH="$CONFIG_FILE"
python3 << 'PYTHON_SCRIPT'
import json
import os
from pathlib import Path

config_file = Path(os.getenv('CONFIG_FILE_PATH'))
if not config_file.exists():
    raise FileNotFoundError(f"Config file not found: {config_file}")

with open(config_file, 'r') as f:
    config = json.load(f)

# Update from environment variables
updates = {
    'GCP_PROJECT_ID': ('gcp', 'project_id'),
    'BIGQUERY_DATASET': ('gcp', 'dataset_id'),
    'BIGQUERY_TABLE': ('gcp', 'table_id'),
    'PREDICT_API_URL': ('api', 'predict_api_url'),
    'WEATHER_LAT': ('weather', 'latitude', float),
    'WEATHER_LON': ('weather', 'longitude', float),
    'WEATHER_CITY': ('weather', 'city'),
}

for env_var, (section, key, *converter) in updates.items():
    value = os.getenv(env_var)
    if value:
        if converter and converter[0] == float:
            config[section][key] = float(value)
        else:
            config[section][key] = value
        print(f"✅ Updated {section}.{key} from {env_var}")

# Handle GCP credentials
if os.getenv('GCP_CREDENTIALS_JSON'):
    creds_file = config['gcp']['credentials_file']
    creds_path = Path(creds_file)
    if not creds_path.is_absolute():
        creds_path = config_file.parent / creds_path
    
    with open(creds_path, 'w') as f:
        f.write(os.getenv('GCP_CREDENTIALS_JSON'))
    print(f"✅ Wrote GCP credentials to {creds_path}")

# Write updated config
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f"✅ Config file created: {config_file}")
PYTHON_SCRIPT

# Clean up exported variable
unset CONFIG_FILE_PATH

echo "✅ Done! Config file ready at $CONFIG_FILE"

