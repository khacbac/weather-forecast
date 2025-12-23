import os
from typing import Optional

import joblib
import pandas as pd
from google.cloud import bigquery
from sklearn.linear_model import LinearRegression


# --- FILE & MODEL CONFIG ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "weather_model.pkl")
KEY_FILE = os.path.join(CURRENT_DIR, "ai-realtime-project-4de709b969f4.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_FILE


# --- BIGQUERY CONFIG ---
PROJECT_ID = "ai-realtime-project"
DATASET_ID = "sensor_data_stream"
TABLE_ID = "real-weather"
FULL_TABLE_PATH = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"


def train_model(df: pd.DataFrame, df_clean: pd.DataFrame, model_path: str = MODEL_PATH) -> Optional[LinearRegression]:
    """
    Train a LinearRegression model on the weather data and save it to disk.

    Expects:
      - df: full dataframe with latest row (including engineered features).
      - df_clean: dataframe with non-null target_temp used for training.
    """
    if len(df_clean) <= 2:
        return None

    X = df_clean[["temperature", "hour", "humidity"]]
    y = df_clean["target_temp"]

    model = LinearRegression()
    model.fit(X, y)

    joblib.dump(model, model_path)
    return model


def load_model(model_path: str = MODEL_PATH) -> Optional[LinearRegression]:
    """Load a previously trained model from disk, if it exists."""
    if not os.path.exists(model_path):
        return None
    return joblib.load(model_path)


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the same feature engineering used in the notebook/Streamlit app."""
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["target_temp"] = df["temperature"].shift(-1)
    return df


def _load_and_prepare(limit: int = 1000) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load data from BigQuery and return (df_with_features, df_clean)."""
    client = bigquery.Client()

    query = f"""
        SELECT timestamp, temperature, humidity, wind_speed
        FROM `{FULL_TABLE_PATH}`
        ORDER BY timestamp ASC
        LIMIT {limit}
    """
    df = client.query(query).to_arrow().to_pandas()
    if df.empty:
        return df, df

    df_feat = _engineer_features(df)
    df_clean = df_feat.dropna().copy()
    return df_feat, df_clean


if __name__ == "__main__":
    print("📡 Loading data from BigQuery...")
    df_feat, df_clean = _load_and_prepare()

    if df_feat.empty:
        print("⚠️ No data found in BigQuery table. Start your `real-weather.py` streamer first.")
        raise SystemExit(1)

    print(f"✅ Loaded {len(df_feat)} rows, {len(df_clean)} rows usable for training.")

    model = train_model(df_feat, df_clean)
    if model is None:
        print("⚠️ Not enough data to train a model (need > 2 rows with target).")
    else:
        print(f"🎉 Model trained and saved to: {MODEL_PATH}")


