# Luzmo Metadata Refresh Strategies

## Overview

This document outlines strategies for periodically refreshing Luzmo metadata in BigQuery.

## Strategy Comparison

| Strategy | Best For | Complexity | Cost |
|----------|----------|------------|------|
| **Cloud Scheduler + Cloud Run Job** | GCP-native, serverless | Medium | Low |
| **GitHub Actions** | Already using GitHub, simple setup | Low | Free (within limits) |
| **Windows Task Scheduler / Cron** | Local/on-prem | Low | Free |
| **Airflow / Cloud Composer** | Complex pipelines | High | Medium-High |

## Recommended: Cloud Scheduler + Cloud Run Job

Since you're already using GCP (BigQuery), this is the most integrated approach.

**Benefits:**
- No server to maintain
- Handles longer execution times
- Easy to monitor in GCP Console
- Native integration with BigQuery

## Option 1: GitHub Actions (Simplest)

Create `.github/workflows/refresh-luzmo-data.yml`:

```yaml
name: Refresh Luzmo Metadata
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Set up GCP credentials
        run: |
          echo "${{ secrets.GCP_SA_KEY }}" > /tmp/gcp-key.json
          echo "GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp-key.json" >> $GITHUB_ENV

      - name: Export to BigQuery
        run: python export_to_bigquery.py --project operations-hero-production --include-descriptions
        env:
          LUZMO_API_KEY: ${{ secrets.LUZMO_API_KEY }}
          LUZMO_API_TOKEN: ${{ secrets.LUZMO_API_TOKEN }}
          LUZMO_API_HOST: ${{ secrets.LUZMO_API_HOST }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

**Required GitHub Secrets:**
- `LUZMO_API_KEY`
- `LUZMO_API_TOKEN`
- `LUZMO_API_HOST`
- `GCP_SA_KEY` (JSON service account key)
- `ANTHROPIC_API_KEY` (required if using `--include-descriptions`)

## Option 2: Cloud Run Job

### Step 1: Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "export_to_bigquery.py", "--project", "operations-hero-production", "--include-descriptions"]
```

### Step 2: Build and Deploy

```bash
# Build container
gcloud builds submit --tag gcr.io/operations-hero-production/luzmo-exporter

# Create Cloud Run Job
gcloud run jobs create luzmo-metadata-refresh \
  --image gcr.io/operations-hero-production/luzmo-exporter \
  --region us-central1 \
  --set-env-vars LUZMO_API_KEY=xxx,LUZMO_API_TOKEN=xxx,LUZMO_API_HOST=https://api.us.luzmo.com

# Create Cloud Scheduler trigger
gcloud scheduler jobs create http luzmo-daily-refresh \
  --location us-central1 \
  --schedule="0 6 * * *" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/operations-hero-production/jobs/luzmo-metadata-refresh:run" \
  --http-method POST \
  --oauth-service-account-email YOUR_SERVICE_ACCOUNT@operations-hero-production.iam.gserviceaccount.com
```

## Option 3: Windows Task Scheduler

### Create batch file `refresh_luzmo.bat`:

```batch
@echo off
cd C:\Users\jerry\Documents\GitHub\luzmo_api
python export_to_bigquery.py --project operations-hero-production --include-descriptions
```

### Schedule in Task Scheduler:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, weekly, etc.)
4. Action: Start a program
5. Program: `C:\Users\jerry\Documents\GitHub\luzmo_api\refresh_luzmo.bat`

## Option 4: Linux Cron

```bash
# Edit crontab
crontab -e

# Add line for daily 6 AM execution
0 6 * * * cd /path/to/luzmo_api && /usr/bin/python3 export_to_bigquery.py --project operations-hero-production --include-descriptions >> /var/log/luzmo_refresh.log 2>&1
```

## Refresh Frequency Recommendations

| Frequency | Use Case |
|-----------|----------|
| **Daily** | Most use cases, dashboards change moderately |
| **Hourly** | Dashboards change frequently, need near-real-time metadata |
| **Weekly** | Dashboards are fairly static |
| **On-demand** | Manual trigger when needed |

## Monitoring

### BigQuery - Check Last Refresh

```sql
SELECT
  MAX(modified_at) as last_dashboard_modified,
  COUNT(*) as total_dashboards
FROM `operations-hero-production.luzmo_metadata.dashboards`;
```

### Add Refresh Timestamp

To track when data was refreshed, you could add a `_refreshed_at` column:

```python
df_dashboards['_refreshed_at'] = datetime.now().isoformat()
```

## Error Handling

For production use, consider:

1. **Retry logic** - Retry on transient failures
2. **Alerting** - Send notifications on failure (email, Slack)
3. **Logging** - Store logs for debugging
4. **Idempotency** - Use `if_exists='replace'` to ensure clean state

## Service Account Permissions

The GCP service account needs:
- `roles/bigquery.dataEditor` - Write to BigQuery tables
- `roles/bigquery.jobUser` - Run BigQuery jobs
