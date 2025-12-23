import os
from typing import Tuple, Optional

import pandas as pd
import streamlit as st
from google.cloud import bigquery

import predict_only as po


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


def main() -> None:
    st.title("Real-time Weather Prediction (BigQuery + Streamlit)")
    st.caption("Powered by Open-Meteo → BigQuery → scikit-learn LinearRegression")

    try:
        df = load_data()
    except Exception as e:
        st.error(f"Failed to load data from BigQuery: {e}")
        return

    if df.empty:
        st.warning("No data found in BigQuery table yet. Start your `real-weather.py` streamer and try again.")
        return

    df_feat, df_clean = po.engineer_features(df)

    st.subheader("Latest Weather Readings")
    st.dataframe(df_feat.tail(10), use_container_width=True)

    current_temp, predicted_temp, status = po.predict_next_temperature(df_feat, df_clean)

    st.subheader("Temperature Now vs Next Update")
    if status == "no_model":
        st.warning("Trained model file `weather_model.pkl` not found. Run `python train_model.py` to create it.")
    elif status == "no_data":
        st.info("Not enough clean data to predict yet. Keep the real-time stream running.")
    elif current_temp is None or predicted_temp is None:
        st.info("Unable to generate prediction. Check recent data and the trained model file.")
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


