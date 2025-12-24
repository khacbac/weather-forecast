import os

import requests
import streamlit as st


# --- CONFIGURATION ---
API_BASE_URL = os.getenv("PREDICT_API_URL", "http://35.225.228.65:8000")


def main() -> None:
    st.title("Real-time Weather Dashboard")
    st.caption("FastAPI backend + BigQuery + persisted ML model")

    st.subheader("Latest Weather & Prediction")

    if st.button("Get latest prediction"):
        # --- Call prediction API ---
        try:
            resp = requests.get(f"{API_BASE_URL}/predict", timeout=5)
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
            data_resp = requests.get(f"{API_BASE_URL}/data?limit=100", timeout=5)
            if not data_resp.ok:
                st.error(f"Data API error (HTTP {data_resp.status_code}): {data_resp.text}")
            else:
                data_json = data_resp.json()
                if data_json.get("status") != "success":
                    st.warning(data_json.get("message", "Data API returned an error status."))
                else:
                    rows = data_json.get("rows", [])
                    if rows:
                        import pandas as pd

                        df = pd.DataFrame(rows)
                        st.dataframe(df.tail(10), use_container_width=True)
                    else:
                        st.info("No rows returned from data API.")
        except Exception as e:
            st.error(f"Failed to call data API: {e}")


if __name__ == "__main__":
    main()


