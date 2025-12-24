# 🌦️ Real-Time Weather AI Pipeline

An automated, end-to-end Machine Learning pipeline hosted on Google Cloud Platform. This system ingests real-time weather data, maintains a live data warehouse, daily retrains a predictive model, and serves inferences via a high-performance API.

## 🏗️ Project Architecture

- **Data Source:** External Weather API / Sensor Stream.
- **Data Warehouse:** **Google BigQuery** for historical storage.
- **Inference Engine:** **FastAPI** serving a Scikit-Learn regression model.
- **Automation:** Linux `crontab` managing a "Closed Loop" ML lifecycle.

## 🚀 Key Features

- **Smart Hot-Reloading:** The API monitors the model's file timestamp (`mtime`). When the daily retraining completes, the API swaps the model in memory with zero downtime.
- **Autonomous Data Pipeline:** A background "pusher" ensures BigQuery is updated every 5 minutes.
- **Self-Healing:** Scheduled restarts and background processes (`nohup`) ensure the service remains live 24/7.

## ⚙️ GCP Infrastructure Details

This project is deployed on **Google Cloud Compute Engine**.

| Component       | Specification                                       |
| :-------------- | :-------------------------------------------------- |
| **VM Instance** | `e2-micro` (Debian GNU/Linux 12)                    |
| **Networking**  | TCP Port `8000` (GCP Firewall Ingress Allowed)      |
| **IAM Roles**   | BigQuery Data Editor, BigQuery Job User             |
| **Python Env**  | Version 3.11+ within a Virtual Environment (`venv`) |

## 🛠️ Installation & Deployment

### 1. Clone & Environment

```bash
git clone [https://github.com/your-username/weather-station.git](https://github.com/your-username/weather-station.git)
cd weather-station
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
