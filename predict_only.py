import os
from typing import Tuple, Optional

import pandas as pd
from google.cloud import bigquery

import train_model as tm
from config_loader import get_config

# --- CONFIGURATION (shared with training/Streamlit) ---
config = get_config()

# Set up GCP credentials
KEY_FILE = config.gcp_credentials_file
if os.path.exists(KEY_FILE):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_FILE
else:
    # Try environment variable or default GCP auth
    key_file_env = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if key_file_env and os.path.exists(key_file_env):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_env

FULL_TABLE_PATH = config.gcp_full_table_path


def load_latest_data(limit: int = 500) -> pd.DataFrame:
    """
    Load recent weather data from BigQuery.
    
    Args:
        limit: Maximum number of rows to retrieve (default: 500)
        
    Returns:
        DataFrame with columns: timestamp, temperature, humidity, wind_speed
        Returns empty DataFrame if query fails or no data found.
    """
    try:
        client = bigquery.Client()

        query = f"""
            SELECT timestamp, temperature, humidity, wind_speed 
            FROM `{FULL_TABLE_PATH}`
            ORDER BY timestamp DESC
            LIMIT {limit}
        """
        
        # Execute query and convert to pandas
        query_job = client.query(query)
        df = query_job.to_dataframe()
        
        # Reverse to get chronological order (oldest to newest)
        if not df.empty:
            df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading data from BigQuery: {e}")
        print(f"   Table path: {FULL_TABLE_PATH}")
        return pd.DataFrame()  # Return empty DataFrame on error


def engineer_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Apply feature engineering and create target_temp column."""
    if df.empty:
        return df, df

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek

    # Target: next temperature (next row)
    df["target_temp"] = df["temperature"].shift(-1)

    # Clean rows with target
    df_clean = df.dropna().copy()
    return df, df_clean


def predict_next_temperature(
    df: pd.DataFrame, df_clean: pd.DataFrame
) -> Tuple[Optional[float], Optional[float], str]:
    """
    Use a persisted model (weather_model.pkl) to predict the next temperature.

    Returns (current_temp, predicted_temp, status) where status is one of:
      - "ok"
      - "no_data"
      - "no_model"
    """
    if df_clean.empty:
        return None, None, "no_data"

    model = tm.load_model()
    if model is None:
        return None, None, "no_model"

    latest_now = df.tail(1)
    pred = model.predict(latest_now[["temperature", "hour", "humidity"]])

    current_temp = float(latest_now["temperature"].values[0])
    predicted_temp = float(pred[0])
    return current_temp, predicted_temp, "ok"


if __name__ == "__main__":
    print("📡 Loading latest data from BigQuery for prediction...")
    df_raw = load_latest_data()
    if df_raw.empty:
        print("⚠️ No data found in BigQuery table. Start your `real-weather.py` streamer first.")
        raise SystemExit(1)

    df_feat, df_clean = engineer_features(df_raw)
    current, pred, status = predict_next_temperature(df_feat, df_clean)

    if status == "no_model":
        print("⚠️ Trained model file `weather_model.pkl` not found. Run `python train_model.py` first.")
    elif status == "no_data":
        print("⚠️ Not enough clean data to predict. Keep the stream running to collect more points.")
    else:
        print(f"✨ Current Temp: {current:.2f}°C")
        print(f"🔮 Predicted Next Temp: {pred:.2f}°C")

