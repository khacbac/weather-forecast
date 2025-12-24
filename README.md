# 🌦️ Full-Stack Real-Time Weather AI Pipeline

An automated, end-to-end Machine Learning ecosystem hosted on Google Cloud Platform. This system integrates a live data ingestion pipeline, a self-updating AI model, and a web-based dashboard for real-time visualization and forecasting.

## 🏗️ Project Architecture & Data Flow

### 1. Frontend (Visualization)

- **App:** `streamlit_real_weather.py`
- **Tech:** **Streamlit**, Plotly, Pandas
- **Function:** A real-time dashboard that fetches data and predictions from the FastAPI backend. It provides interactive charts for temperature trends and compares current metrics against AI-generated forecasts.

### 2. Backend API (Inference)

- **Engine:** **FastAPI** (`main.py`)
- **Smart Logic:** Implements a **Hot-Swap** model loader. The API monitors the model's file timestamp (`mtime`). When the daily retraining completes, the API automatically reloads the new weights into memory without needing a server restart.
- **Endpoints:** - `GET /predict`: Returns the next-hour temperature forecast.
  - `GET /data`: Fetches the most recent logs from BigQuery for UI display.

### 3. Data Pipeline & ETL

- **Ingestion (The "Pusher"):** `pusher.py` fetches live weather metrics every 5 minutes from external APIs and streams them into **Google BigQuery**.
- **Continuous Training:** `train_model.py` pulls historical data from BigQuery every night to retrain the Scikit-Learn regressor, ensuring the model adapts to recent data patterns.

---

## ⚙️ GCP Infrastructure Details

The system is deployed on **Google Cloud Compute Engine**.

| Component        | Specification                                                       |
| :--------------- | :------------------------------------------------------------------ |
| **VM Instance**  | `e2-micro` (Debian GNU/Linux 12)                                    |
| **Database**     | **Google BigQuery** (Time-series data warehouse)                    |
| **Networking**   | Port `8000` (API) and Port `8501` (Streamlit) open via GCP Firewall |
| **IAM Security** | Authenticated via Service Account JSON (BigQuery Data Editor role)  |

---

## 🛠️ Setup & Deployment

### 1. Installation

```bash
git clone [https://github.com/your-username/weather-station.git](https://github.com/your-username/weather-station.git)
cd weather-station
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration

The project uses a centralized configuration system for secure data management.

1. **Create your config file:**

   ```bash
   cp config.json.example config.json
   ```

2. **Edit `config.json`** with your settings:

   ```json
   {
     "gcp": {
       "project_id": "your-gcp-project-id",
       "dataset_id": "sensor_data_stream",
       "table_id": "real-weather",
       "credentials_file": "path/to/your-credentials.json"
     },
     "api": {
       "predict_api_url": "http://your-api-url:8000",
       "timeout": 5
     },
     "weather": {
       "latitude": 16.047079,
       "longitude": 108.20623,
       "city": "Danang"
     },
     "model": {
       "model_file": "weather_model.pkl"
     }
   }
   ```

3. **Security Notes:**

   - `config.json` is excluded from git (already in `.gitignore`)
   - `config.json.example` is a template that can be safely committed
   - Environment variables can override config values (useful for deployment)
   - Never commit your actual `config.json` file with sensitive data

4. **Environment Variable Overrides:**
   The config system supports environment variable overrides:
   - `GCP_PROJECT_ID` - Overrides `gcp.project_id`
   - `BIGQUERY_DATASET` - Overrides `gcp.dataset_id`
   - `BIGQUERY_TABLE` - Overrides `gcp.table_id`
   - `GOOGLE_APPLICATION_CREDENTIALS` - Overrides `gcp.credentials_file`
   - `PREDICT_API_URL` - Overrides `api.predict_api_url`
   - `WEATHER_LAT`, `WEATHER_LON`, `WEATHER_CITY` - Override weather location

📖 **For detailed GitHub setup instructions**, see [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md)

```mermaid
graph LR
    %% Data Ingestion Section
    subgraph GCP_Compute_Engine [GCP VM Instance]
        direction TB
        CRON[Crontab Scheduler]
        PUSHER[pusher.py]
        TRAINER[train_model.py]
        API[FastAPI main.py]
        MODEL[(weather_model.pkl)]
    end

    %% External Data Source
    EXT_API((External Weather API)) --> PUSHER

    %% Database
    subgraph GCP_BigQuery [Google BigQuery]
        BQ[(Historical Weather Table)]
    end

    %% Flow Connections
    CRON -- "Every 5 Mins" --> PUSHER
    PUSHER -- "Insert Rows" --> BQ

    CRON -- "Daily 2:00 AM" --> TRAINER
    BQ -- "Fetch History" --> TRAINER
    TRAINER -- "Saves New Version" --> MODEL

    %% Inference Flow
    API -- "Checks Timestamp" --> MODEL
    BQ -- "Fetch Recent Data" --> API

    %% Frontend
    subgraph Local_Machine [User Device]
        ST[Streamlit Dashboard]
    end

    ST -- "GET /predict" --> API
    ST -- "GET /data" --> API
```
