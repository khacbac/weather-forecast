# 🔐 Setting Up Configuration on GitHub

This guide explains how to securely manage configuration on GitHub using GitHub Secrets and Actions.

## 📋 Table of Contents

1. [GitHub Secrets Setup](#github-secrets-setup)
2. [Using GitHub Actions](#using-github-actions)
3. [Manual Setup on Server](#manual-setup-on-server)
4. [Environment Variables](#environment-variables)

---

## 🔑 GitHub Secrets Setup

### Step 1: Add Secrets to Your Repository

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each of the following:

#### Required Secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `GCP_PROJECT_ID` | Your GCP project ID | `ai-realtime-project` |
| `BIGQUERY_DATASET` | BigQuery dataset name | `sensor_data_stream` |
| `BIGQUERY_TABLE` | BigQuery table name | `real-weather` |
| `PREDICT_API_URL` | Your API base URL | `http://35.225.228.65:8000` |
| `WEATHER_LAT` | Weather location latitude | `16.047079` |
| `WEATHER_LON` | Weather location longitude | `108.206230` |
| `WEATHER_CITY` | City name | `Danang` |
| `GCP_CREDENTIALS_JSON` | **Full JSON content** of your GCP service account key file | `{"type": "service_account", ...}` |

### Step 2: Adding GCP Credentials

For `GCP_CREDENTIALS_JSON`, you need to add the **entire contents** of your JSON credentials file:

1. Open your `ai-realtime-project-4de709b969f4.json` file
2. Copy the **entire JSON content** (all of it, including `{` and `}`)
3. Paste it as the value for the `GCP_CREDENTIALS_JSON` secret

⚠️ **Important**: This is sensitive data. Only add it as a GitHub Secret, never commit it to the repository.

---

## 🤖 Using GitHub Actions

### Automatic Config Generation

The repository includes a GitHub Actions workflow (`.github/workflows/setup-config.yml`) that automatically generates `config.json` from secrets.

#### To use it:

1. **Push to trigger automatically**, or
2. **Manual trigger**: Go to **Actions** → **Setup Configuration from Secrets** → **Run workflow**

The workflow will:
- Create `config.json` from `config.json.example`
- Populate it with values from GitHub Secrets
- Create the GCP credentials file from the secret

### Using in Other Workflows

You can reference secrets in your workflows like this:

```yaml
- name: Run script
  env:
    GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
    PREDICT_API_URL: ${{ secrets.PREDICT_API_URL }}
  run: |
    python3 your_script.py
```

---

## 🖥️ Manual Setup on Server

If you're deploying to a GCP VM or other server, you can set up the config manually:

### Option 1: Using the Setup Script

1. **Set environment variables** on your server:
   ```bash
   export GCP_PROJECT_ID="ai-realtime-project"
   export BIGQUERY_DATASET="sensor_data_stream"
   export BIGQUERY_TABLE="real-weather"
   export PREDICT_API_URL="http://35.225.228.65:8000"
   export WEATHER_LAT="16.047079"
   export WEATHER_LON="108.206230"
   export WEATHER_CITY="Danang"
   export GCP_CREDENTIALS_JSON='{"type": "service_account", ...}'
   ```

2. **Run the setup script**:
   ```bash
   chmod +x scripts/setup_config_from_secrets.sh
   ./scripts/setup_config_from_secrets.sh
   ```

### Option 2: Manual File Creation

1. **Copy the example**:
   ```bash
   cp config.json.example config.json
   ```

2. **Edit `config.json`** with your values:
   ```bash
   nano config.json  # or use your preferred editor
   ```

3. **Place your GCP credentials file** in the project directory

---

## 🌍 Environment Variables

The config system supports environment variable overrides. You can use these instead of (or in addition to) `config.json`:

### GCP Settings
- `GCP_PROJECT_ID` - Overrides `gcp.project_id`
- `BIGQUERY_DATASET` - Overrides `gcp.dataset_id`
- `BIGQUERY_TABLE` - Overrides `gcp.table_id`
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to credentials file (overrides `gcp.credentials_file`)

### API Settings
- `PREDICT_API_URL` - Overrides `api.predict_api_url`

### Weather Settings
- `WEATHER_LAT` - Overrides `weather.latitude`
- `WEATHER_LON` - Overrides `weather.longitude`
- `WEATHER_CITY` - Overrides `weather.city`

### Priority Order

Configuration values are loaded in this priority order (highest to lowest):

1. **Environment variables** (highest priority)
2. **config.json file**
3. **Default values** (lowest priority)

---

## 🔒 Security Best Practices

1. ✅ **Never commit `config.json`** - It's already in `.gitignore`
2. ✅ **Use GitHub Secrets** for sensitive data in CI/CD
3. ✅ **Use environment variables** on servers when possible
4. ✅ **Rotate credentials** regularly
5. ✅ **Limit secret access** - Only give access to those who need it
6. ✅ **Use separate secrets** for different environments (dev/staging/prod)

---

## 📝 Example: Complete Setup Workflow

### For GitHub Actions:

```yaml
name: Deploy to GCP

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup config from secrets
        env:
          GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
          PREDICT_API_URL: ${{ secrets.PREDICT_API_URL }}
          # ... other secrets
        run: |
          ./scripts/setup_config_from_secrets.sh
      
      - name: Deploy
        run: |
          # Your deployment commands here
```

### For GCP VM (via SSH):

```bash
# On your local machine
scp config.json.example user@your-vm:/path/to/project/

# SSH into VM
ssh user@your-vm

# On VM
cd /path/to/project
cp config.json.example config.json
nano config.json  # Edit with your values
# Upload credentials file separately
```

---

## 🆘 Troubleshooting

### Config file not found
- Make sure `config.json` exists (copy from `config.json.example`)
- Check file permissions

### Secrets not working in GitHub Actions
- Verify secrets are set in **Settings → Secrets and variables → Actions**
- Check secret names match exactly (case-sensitive)
- Ensure you're using `${{ secrets.SECRET_NAME }}` syntax

### Credentials not loading
- Verify `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set
- Check the credentials file path is correct
- Ensure the JSON file is valid

---

## 📚 Additional Resources

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GCP Service Account Keys](https://cloud.google.com/iam/docs/service-accounts)
- [Environment Variables Best Practices](https://12factor.net/config)

