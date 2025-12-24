import os
import pandas as pd
import requests
import streamlit as st

from config_loader import get_config

# --- CONFIGURATION ---
# Streamlit Cloud secrets are accessible via st.secrets or os.getenv
# Priority: Streamlit secrets > Environment variables > config.json > defaults
config = get_config()
config_source = None

# Check for Streamlit secrets first (Streamlit Cloud)
# Use try-except to handle cases where secrets file doesn't exist locally
try:
    if hasattr(st, 'secrets') and hasattr(st.secrets, 'get'):
        API_BASE_URL = st.secrets.get('PREDICT_API_URL', None)
        if API_BASE_URL:
            config_source = "Streamlit Secrets"
except Exception:
    # Secrets file doesn't exist or can't be parsed (local development)
    API_BASE_URL = None

# Fall back to environment variable
if not API_BASE_URL:
    API_BASE_URL = os.getenv('PREDICT_API_URL')
    if API_BASE_URL:
        config_source = "Environment Variable"

# Fall back to config.json or defaults
if not API_BASE_URL:
    API_BASE_URL = config.api_base_url
    config_source = "config.json/default"

API_TIMEOUT = config.api_timeout

def main() -> None:
    st.title("Real-time Weather Dashboard")
    st.caption("Forecasting weather in FPT Plaza 2, Danang")

    # Debug info (controlled by config file)
    if config.show_debug_info:
        with st.sidebar:
            with st.expander("🔧 Debug Info", expanded=False):
                st.code(f"API URL: {API_BASE_URL}")
                st.code(f"Timeout: {API_TIMEOUT}s")
                st.caption(f"Config source: {config_source}")

    st.subheader("Latest Weather & Prediction")

    if st.button("Get latest prediction"):
        # --- Call prediction API ---
        try:
            resp = requests.get(f"{API_BASE_URL}/predict", timeout=API_TIMEOUT)
        except Exception as e:
            st.error(f"Failed to call prediction API: {e}")
            return

        if not resp.ok:
            st.error(f"Prediction API error (HTTP {resp.status_code}): {resp.text}")
            return

        data = resp.json()

        if data.get("status") != "success":
            st.warning(data.get("message", "Prediction API returned an error status."))
            return

        current = data.get("current_weather", {}).get("temp")
        forecast = data.get("forecast_next")

        col1, col2 = st.columns(2)
        col1.metric("Current Temperature (°C)", f"{current:.2f}" if current is not None else "N/A")
        col2.metric("Predicted Next Temperature (°C)", f"{forecast:.2f}" if forecast is not None else "N/A")

        # --- After prediction, refresh latest raw data from BigQuery via /data ---
        st.markdown("#### Latest Weather Readings (refreshed)")
        try:
            data_resp = requests.get(f"{API_BASE_URL}/data?limit=500", timeout=API_TIMEOUT)
            if not data_resp.ok:
                st.error(f"Data API error (HTTP {data_resp.status_code}): {data_resp.text}")
            else:
                data_json = data_resp.json()
                if data_json.get("status") != "success":
                    st.warning(data_json.get("message", "Data API returned an error status."))
                else:
                    rows = data_json.get("rows", [])
                    if rows:
                        df = pd.DataFrame(rows)
                        
                        # Convert timestamp to datetime if it exists
                        if 'timestamp' in df.columns:
                            df['timestamp'] = pd.to_datetime(df['timestamp'])
                            df = df.sort_values('timestamp')
                        
                        # Display latest data table
                        st.dataframe(df.tail(10), use_container_width=True)
                        
                        # --- Charts Section ---
                        st.markdown("#### Weather Trends")
                        
                        # Temperature chart
                        if 'temperature' in df.columns:
                            st.markdown("**Temperature Over Time**")
                            temp_df = df[['timestamp', 'temperature']].copy() if 'timestamp' in df.columns else df[['temperature']].copy()
                            temp_df = temp_df.set_index('timestamp') if 'timestamp' in df.columns else temp_df.set_index(temp_df.index)
                            st.line_chart(temp_df, use_container_width=True)
                        
                        # Multi-metric chart
                        chart_cols = []
                        if 'temperature' in df.columns:
                            chart_cols.append('temperature')
                        if 'humidity' in df.columns:
                            chart_cols.append('humidity')
                        if 'wind_speed' in df.columns:
                            chart_cols.append('wind_speed')
                        
                        if len(chart_cols) > 1:
                            st.markdown("**Temperature, Humidity & Wind Speed**")
                            multi_df = df[['timestamp'] + chart_cols].copy() if 'timestamp' in df.columns else df[chart_cols].copy()
                            multi_df = multi_df.set_index('timestamp') if 'timestamp' in df.columns else multi_df.set_index(multi_df.index)
                            st.line_chart(multi_df, use_container_width=True)
                        
                        # Individual charts in columns
                        if len(chart_cols) >= 2:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if 'humidity' in df.columns:
                                    st.markdown("**Humidity Over Time**")
                                    humidity_df = df[['timestamp', 'humidity']].copy() if 'timestamp' in df.columns else df[['humidity']].copy()
                                    humidity_df = humidity_df.set_index('timestamp') if 'timestamp' in df.columns else humidity_df.set_index(humidity_df.index)
                                    st.area_chart(humidity_df, use_container_width=True)
                            
                            with col2:
                                if 'wind_speed' in df.columns:
                                    st.markdown("**Wind Speed Over Time**")
                                    wind_df = df[['timestamp', 'wind_speed']].copy() if 'timestamp' in df.columns else df[['wind_speed']].copy()
                                    wind_df = wind_df.set_index('timestamp') if 'timestamp' in df.columns else wind_df.set_index(wind_df.index)
                                    st.area_chart(wind_df, use_container_width=True)
                    else:
                        st.info("No rows returned from data API.")
        except Exception as e:
            st.error(f"Failed to call data API: {e}")


if __name__ == "__main__":
    main()


