# BigQuery Export Documentation

This document describes how to export Luzmo metadata to Google BigQuery.

## Prerequisites

1. **Google Cloud Project** with BigQuery enabled
2. **Service Account** with permissions:
   - `roles/bigquery.dataEditor` - Write to BigQuery tables
   - `roles/bigquery.jobUser` - Run BigQuery jobs
3. **Authentication** configured via one of:
   - `GOOGLE_APPLICATION_CREDENTIALS` environment variable pointing to service account JSON
   - `gcloud auth application-default login`

## Installation

```bash
pip install pandas-gbq google-cloud-bigquery
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

Export everything with a single command:

```bash
# Metadata only (fast, no API costs)
python export_to_bigquery.py --project YOUR_PROJECT_ID

# Include AI-generated descriptions and tags (uses Claude API)
python export_to_bigquery.py --project YOUR_PROJECT_ID --include-descriptions
```

## Unified Export Command

The `export_to_bigquery.py` script exports all Luzmo metadata in one job.

```bash
python export_to_bigquery.py --project YOUR_PROJECT_ID [options]
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--project`, `-p` | Google Cloud project ID | Required |
| `--dataset`, `-d` | BigQuery dataset ID | `luzmo_metadata` |
| `--if-exists` | Action if table exists: `replace`, `append`, `fail` | `replace` |
| `--include-descriptions` | Generate AI descriptions and tags | Off |
| `--style`, `-s` | Description style: `business`, `technical`, `brief` | `business` |
| `--max-tags` | Maximum tags per dashboard | `5` |
| `--limit`, `-l` | Limit dashboards for descriptions | All |

**Examples:**
```bash
# Metadata only
python export_to_bigquery.py --project operations-hero-production

# Full export with descriptions
python export_to_bigquery.py --project operations-hero-production --include-descriptions

# Full export with custom options
python export_to_bigquery.py --project operations-hero-production \
    --include-descriptions \
    --style technical \
    --max-tags 3 \
    --limit 50
```

**Tables Created:**

| Table | Created | Description |
|-------|---------|-------------|
| `dashboards` | Always | Dashboard metadata with collections column |
| `charts` | Always | All charts across dashboards |
| `filters` | Always | All filters across dashboards |
| `collections` | Always | Collection definitions |
| `collection_securables` | Always | Collection membership |
| `dashboard_descriptions` | With `--include-descriptions` | AI-generated descriptions |
| `tags` | With `--include-descriptions` | Distinct tags with counts |
| `dashboard_tags` | With `--include-descriptions` | Dashboard-tag relationships |

---

## Individual Export Commands (Alternative)

You can also run exports separately if needed:

### Dashboard Metadata Only

```bash
python export_dashboards.py --bigquery --project YOUR_PROJECT_ID
```

### AI Descriptions Only

```bash
python generate_dashboard_descriptions.py --bigquery --project YOUR_PROJECT_ID
```

## Complete Schema

After running both exports, your `luzmo_metadata` dataset will contain:

```
luzmo_metadata/
├── dashboards              # Core dashboard metadata
├── charts                  # Chart components
├── filters                 # Filter components
├── collections             # Collection definitions
├── collection_securables   # Collection membership
├── dashboard_descriptions  # AI descriptions
├── tags                    # Distinct tag list
└── dashboard_tags          # Dashboard-tag junction
```

## Example Queries

### Find dashboards by collection
```sql
SELECT d.name, d.description, d.collections
FROM `project.luzmo_metadata.dashboards` d
WHERE d.collections LIKE '%Production%';
```

### Find dashboards by tag
```sql
SELECT dt.dashboard_name, dt.tag
FROM `project.luzmo_metadata.dashboard_tags` dt
WHERE dt.tag = 'work orders';
```

### Top 10 most common tags
```sql
SELECT tag, dashboard_count
FROM `project.luzmo_metadata.tags`
ORDER BY dashboard_count DESC
LIMIT 10;
```

### Dashboard with most charts
```sql
SELECT d.name, COUNT(c.chart_id) as chart_count
FROM `project.luzmo_metadata.dashboards` d
JOIN `project.luzmo_metadata.charts` c ON d.id = c.dashboard_id
GROUP BY d.name
ORDER BY chart_count DESC
LIMIT 10;
```

### Find dashboards using specific chart types
```sql
SELECT DISTINCT d.name, c.chart_type
FROM `project.luzmo_metadata.dashboards` d
JOIN `project.luzmo_metadata.charts` c ON d.id = c.dashboard_id
WHERE c.chart_type = 'bar-chart';
```

### Join descriptions with metadata
```sql
SELECT
  d.name,
  d.collections,
  dd.generated_description,
  dd.tags
FROM `project.luzmo_metadata.dashboards` d
LEFT JOIN `project.luzmo_metadata.dashboard_descriptions` dd ON d.id = dd.id
WHERE d.collections != '';
```

### Collection summary
```sql
SELECT
  c.name as collection_name,
  c.dashboard_count,
  c.dataset_count
FROM `project.luzmo_metadata.collections` c
ORDER BY c.dashboard_count DESC;
```

## Programmatic Usage

### Dashboard Export
```python
from src.dashboard_exporter import DashboardExporter

exporter = DashboardExporter()
results = exporter.export_to_bigquery(
    project_id='your-project',
    dataset_id='luzmo_metadata',
    if_exists='replace'
)
print(results)
# {'dashboards': 'project.luzmo_metadata.dashboards', ...}
```

### Description Export
```python
from src.dashboard_describer import DashboardDescriber

describer = DashboardDescriber()
results = describer.export_to_bigquery(
    project_id='your-project',
    dataset_id='luzmo_metadata',
    style='business',
    max_tags=5,
    if_exists='replace'
)
print(results)
# {'dashboard_descriptions': '...', 'tags': '...', 'dashboard_tags': '...'}
```

## Scheduling Refreshes

See [refresh_strategies.md](refresh_strategies.md) for options to periodically refresh BigQuery data:
- GitHub Actions (simplest)
- Cloud Scheduler + Cloud Run Job (GCP-native)
- Windows Task Scheduler / Linux Cron (local)

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `403 Forbidden` | Missing BigQuery permissions | Add `bigquery.dataEditor` and `bigquery.jobUser` roles |
| `404 Dataset not found` | Dataset doesn't exist | Script creates it automatically, or create manually |
| `ImportError: pandas_gbq` | Missing library | Run `pip install pandas-gbq google-cloud-bigquery` |
| `DefaultCredentialsError` | No GCP auth | Set `GOOGLE_APPLICATION_CREDENTIALS` or run `gcloud auth` |
