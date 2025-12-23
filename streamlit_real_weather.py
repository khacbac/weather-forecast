import os
from typing import Tuple, Optional

import pandas as pd
import streamlit as st
from google.cloud import bigquery
from sklearn.linear_model import LinearRegression


# --- CONFIGURATION ---
current_dir = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.path.join(current_dir, "ai-realtime-project-4de709b969f4.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_FILE

PROJECT_ID = "ai-realtime-project"
DATASET_ID = "sensor_data_stream"
TABLE_ID = "real-weather"
FULL_TABLE_PATH = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"


@st.cache_data(ttl=60)
def load_data(limit: int = 500) -> pd.DataFrame:
    """Load recent weather data from BigQuery."""
    client = bigquery.Client()

    query = f"""
        SELECT timestamp, temperature, humidity, wind_speed 
        FROM `{FULL_TABLE_PATH}`
        ORDER BY timestamp ASC
        LIMIT {limit}
    """
    df = client.query(query).to_arrow().to_pandas()
    return df


def engineer_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Replicate the notebook feature engineering and target creation."""
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


def train_and_predict(df: pd.DataFrame, df_clean: pd.DataFrame) -> Tuple[Optional[float], Optional[float]]:
    """Train LinearRegression and predict next temperature."""
    if len(df_clean) <= 2:
        return None, None

    X = df_clean[["temperature", "hour", "humidity"]]
    y = df_clean["target_temp"]

    model = LinearRegression()
    model.fit(X, y)

    # Use very latest row (before shifting) as "now"
    latest_now = df.tail(1)
    pred = model.predict(latest_now[["temperature", "hour", "humidity"]])

    current_temp = float(latest_now["temperature"].values[0])
    predicted_temp = float(pred[0])
    return current_temp, predicted_temp


def main() -> None:
    st.title("Real-time Weather Prediction (BigQuery + Streamlit)")
    st.caption("Powered by Open-Meteo → BigQuery → scikit-learn LinearRegression")

    with st.sidebar:
        st.header("Controls")
        refresh = st.button("🔄 Refresh data & prediction")
        st.markdown("Data is cached for **60 seconds** to avoid excessive querying.")

    if refresh:
        # Clear cache on demand
        load_data.clear()

    try:
        df = load_data()
    except Exception as e:
        st.error(f"Failed to load data from BigQuery: {e}")
        return

    if df.empty:
        st.warning("No data found in BigQuery table yet. Start your `real-weather.py` streamer and try again.")
        return

    df_feat, df_clean = engineer_features(df)

    st.subheader("Latest Weather Readings")
    st.dataframe(df_feat.tail(10), use_container_width=True)

    current_temp, predicted_temp = train_and_predict(df_feat, df_clean)

    st.subheader("Temperature Now vs Next Update")
    if current_temp is None or predicted_temp is None:
        st.info("Need at least 3 rows of clean data to start predicting. Keep the stream running.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Current Temperature (°C)", f"{current_temp:.2f}")
        col2.metric("Predicted Next Temperature (°C)", f"{predicted_temp:.2f}")

    with st.expander("Raw Data (last 100 rows)"):
        st.dataframe(df_feat.tail(100), use_container_width=True)

    with st.expander("Model Details"):
        st.write(
            """
            - **Features**: `temperature`, `hour`, `humidity`  
            - **Target**: next-row `temperature` (`target_temp`)  
            - **Model**: `sklearn.linear_model.LinearRegression`
            """
        )


if __name__ == "__main__":
    main()


