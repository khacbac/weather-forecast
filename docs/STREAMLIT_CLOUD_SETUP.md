# 🚀 Streamlit Cloud Setup Guide

This guide explains how to deploy your Streamlit app to Streamlit Cloud and configure it properly.

## 📋 Prerequisites

1. A GitHub repository with your code
2. A Streamlit Cloud account (free tier available)
3. Your API running and accessible (e.g., `http://your-api-ip:8000` or `https://your-domain.com`)

---

## 🔧 Step 1: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your repository and branch
5. Set the **Main file path** to: `streamlit_real_weather.py`
6. Click **"Deploy"**

---

## 🔐 Step 2: Configure Secrets (IMPORTANT!)

Since `config.json` is excluded from git, you need to set up secrets in Streamlit Cloud.

### Option A: Using Streamlit Secrets (Recommended)

1. In your Streamlit Cloud app dashboard, go to **"Settings"** → **"Secrets"**
2. Add the following secrets in TOML format:

```toml
PREDICT_API_URL = "http://your-api-ip:8000"
GCP_PROJECT_ID = "ai-realtime-project"
BIGQUERY_DATASET = "sensor_data_stream"
BIGQUERY_TABLE = "real-weather"
WEATHER_LAT = "16.047079"
WEATHER_LON = "108.206230"
WEATHER_CITY = "Danang"
```

3. Click **"Save"**

### Option B: Using Environment Variables

Streamlit Cloud also supports environment variables. You can set them in the app settings under **"Advanced settings"**.

---

## 🔍 Step 3: Verify Configuration

After deploying, check the app:

1. Open your Streamlit Cloud app URL
2. Click the **"🔧 Debug Info"** expander in the sidebar
3. Verify that:
   - **API URL** shows your correct API URL (not `localhost:8000`)
   - **Config source** shows where the config is coming from

---

## 🐛 Troubleshooting

### Error: "Connection refused" or "localhost:8000"

**Problem**: The app is trying to connect to `localhost:8000` instead of your API.

**Solution**:

1. Check that you've set `PREDICT_API_URL` in Streamlit Cloud secrets
2. Verify the secret name is exactly `PREDICT_API_URL` (case-sensitive)
3. Make sure you've saved the secrets and restarted the app
4. Check the Debug Info in the sidebar to see what URL is being used

### Error: "Failed to call prediction API"

**Possible causes**:

1. Your API server is not running
2. The API URL is incorrect
3. Firewall/network issues blocking the connection
4. CORS issues (if your API doesn't allow cross-origin requests)

**Solutions**:

- Verify your API is accessible: `curl http://your-api-ip:8000/predict`
- Check that your GCP VM firewall allows connections from Streamlit Cloud
- Ensure your FastAPI app has CORS enabled if needed

### Config not loading

**Problem**: App shows "config.json/default" in Debug Info.

**Solution**:

- Make sure you've added secrets in Streamlit Cloud
- Check that secret names match exactly (case-sensitive)
- Restart the app after adding secrets

---

## 🔒 Security Notes

1. ✅ **Never commit `config.json`** - It's already in `.gitignore`
2. ✅ **Use Streamlit Secrets** for sensitive data (API URLs, credentials)
3. ✅ **Don't hardcode URLs** in your code
4. ✅ **Use HTTPS** for production APIs when possible

---

## 📝 Example: Complete Secrets Configuration

Here's a complete example of what your Streamlit Cloud secrets should look like:

```toml
# API Configuration
PREDICT_API_URL = "http://your-api-ip:8000"

# GCP Configuration (if needed by your app)
GCP_PROJECT_ID = "ai-realtime-project"
BIGQUERY_DATASET = "sensor_data_stream"
BIGQUERY_TABLE = "real-weather"

# Weather Location
WEATHER_LAT = "16.047079"
WEATHER_LON = "108.206230"
WEATHER_CITY = "Danang"
```

**Note**: For GCP credentials, you typically don't need to add them to Streamlit Cloud if your app only reads from BigQuery via the API. If you need direct BigQuery access, you'd need to add the credentials JSON as a secret (but this is not recommended - use the API instead).

---

## 🚀 Quick Deploy Checklist

- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud app created
- [ ] `PREDICT_API_URL` secret added
- [ ] App deployed and running
- [ ] Debug Info shows correct API URL
- [ ] API is accessible from Streamlit Cloud
- [ ] Test the "Get latest prediction" button

---

## 📚 Additional Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Streamlit Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/get-started)

---

## 💡 Pro Tips

1. **Use the Debug Info**: The sidebar debug info helps you troubleshoot configuration issues quickly
2. **Test Locally First**: Make sure your app works locally with environment variables before deploying
3. **Monitor API**: Keep an eye on your API server logs to see if requests are coming through
4. **Use HTTPS**: For production, consider setting up HTTPS for your API (e.g., using a reverse proxy or Cloud Load Balancer)
