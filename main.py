from fastapi import FastAPI

import predict_only as po


app = FastAPI()


@app.get("/data")
def get_latest_data(limit: int = 100):
    """
    Return recent rows from BigQuery for display clients (e.g. Streamlit).
    """
    df_raw = po.load_latest_data(limit=limit)
    if df_raw.empty:
        return {
            "status": "error",
            "message": "No data found in BigQuery table. Start your real-time streamer first.",
            "rows": [],
        }

    # Convert to JSON-serializable list of dicts
    rows = df_raw.to_dict(orient="records")
    return {
        "status": "success",
        "row_count": len(rows),
        "rows": rows,
    }


@app.get("/predict")
def get_prediction():
    """
    Predict the next temperature using the persisted model and latest BigQuery data.

    Relies on:
      - BigQuery table: ai-realtime-project.sensor_data_stream.real-weather
      - Persisted model file: weather_model.pkl (created by train_model.py)
    """
    # 1. Load the latest data from BigQuery
    df_raw = po.load_latest_data()
    if df_raw.empty:
        return {
            "status": "error",
            "message": "No data found in BigQuery table. Start your real-time streamer first.",
        }

    # 2. Apply the same feature engineering as training/Streamlit
    df_feat, df_clean = po.engineer_features(df_raw)

    # 3. Use the persisted model to predict the next temperature
    current_temp, prediction, status = po.predict_next_temperature(df_feat, df_clean)

    if status == "no_model":
        return {
            "status": "error",
            "message": "Trained model file 'weather_model.pkl' not found. Run 'python train_model.py' first.",
        }
    if status == "no_data":
        return {
            "status": "error",
            "message": "Not enough clean data to predict. Keep the real-time stream running.",
        }
    if current_temp is None or prediction is None:
        return {
            "status": "error",
            "message": "Unable to generate prediction. Check recent data and the trained model file.",
        }

    # 4. Return the result as JSON (structure similar to earlier example)
    return {
        "status": "success",
        "current_weather": {
            "temp": float(current_temp),
        },
        "forecast_next": round(float(prediction), 2),
    }
