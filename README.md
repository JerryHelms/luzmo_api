# Luzmo API + LLM Dashboard Analyzer

A Python application that combines Luzmo's API with Anthropic's Claude to analyze, export, and manage your dashboards and datasets.

## Features

- **Dashboard Export**: Export all dashboards, charts, and filters to Excel
- **Dataset Export**: Export datasets, columns, and usage relationships to Excel
- **AI-Powered Descriptions**: Generate dashboard descriptions using Claude (no data retrieval)
- **Bulk Updates**: Update dashboard descriptions from external files
- **Precise Data Analysis**: Fetch actual data from Luzmo dashboards for AI analysis
- **Multiple Output Formats**: Save summaries as text, markdown, JSON, or Excel

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/luzmo_api.git
cd luzmo_api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` and add your credentials:
```env
LUZMO_API_KEY=your_luzmo_api_key
LUZMO_API_TOKEN=your_luzmo_api_token
LUZMO_API_HOST=https://api.luzmo.com  # or https://api.us.luzmo.com

ANTHROPIC_API_KEY=your_anthropic_api_key

OUTPUT_DIR=./summaries
```

## Quick Start

### Export Dashboards to Excel
```bash
python export_dashboards.py
```
Creates `dashboards_export_YYYYMMDD_HHMMSS.xlsx` with sheets:
- **Dashboards**: ID, name, description, owner_id, timestamps
- **Charts**: All charts with dashboard linkage, type, position
- **Filters**: All filters with dashboard linkage

### Export Datasets to Excel
```bash
python export_datasets.py
```
Creates `datasets_export_YYYYMMDD_HHMMSS.xlsx` with sheets:
- **Datasets**: ID, name, subtype, row count, sync settings
- **Columns**: Column definitions with type, format, aggregation
- **Dataset_Usage**: Which dashboards use which datasets

### Generate AI Dashboard Descriptions
```bash
# Single dashboard
python generate_dashboard_descriptions.py -d <dashboard_id>

# All dashboards (limit to 10)
python generate_dashboard_descriptions.py --limit 10

# Different styles: business, technical, brief
python generate_dashboard_descriptions.py --style technical
```

### Update Dashboard Descriptions
```bash
# Preview changes (dry run)
python update_dashboard_descriptions.py descriptions.xlsx --dry-run

# Apply updates
python update_dashboard_descriptions.py descriptions.xlsx
```

## Project Structure

```
luzmo_api/
├── src/
│   ├── __init__.py
│   ├── luzmo_client.py              # Luzmo API client
│   ├── dashboard_analyzer.py        # Data extraction and structuring
│   ├── dashboard_exporter.py        # Export dashboards to Excel
│   ├── dataset_exporter.py          # Export datasets to Excel
│   ├── dashboard_describer.py       # AI description generator
│   ├── dashboard_updater.py         # Update dashboards from file
│   ├── llm_analyzer.py              # Claude integration
│   ├── summary_writer.py            # File writing utilities
│   ├── dashboard_summary_pipeline.py # Main orchestrator
│   └── utils.py                     # Utility functions
├── summaries/                        # Generated summaries
├── export_dashboards.py              # Dashboard export script
├── export_datasets.py                # Dataset export script
├── generate_dashboard_descriptions.py # AI description script
├── update_dashboard_descriptions.py  # Bulk update script
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
└── README.md                         # This file
```

## Module Reference

### Dashboard Exporter (`src/dashboard_exporter.py`)
Exports dashboard metadata to Excel without retrieving actual data.

```python
from src.dashboard_exporter import DashboardExporter

exporter = DashboardExporter()
output_file = exporter.export_to_excel()
```

**Output columns:**
- Dashboards: id, name, description, slug, type, subtype, item_count, owner_id, account_id, modifier_id, template_id, created_at, modified_at
- Charts: dashboard_id, dashboard_name, chart_id, chart_type, title, screen_mode, position_x, position_y, width, height
- Filters: dashboard_id, dashboard_name, filter_id, filter_type, title

### Dataset Exporter (`src/dataset_exporter.py`)
Exports dataset metadata, columns, and usage relationships.

```python
from src.dataset_exporter import DatasetExporter

exporter = DatasetExporter()
output_file = exporter.export_to_excel()
```

**Output columns:**
- Datasets: id, name, description, subtype, rows, source_sheet, storage, cache, meta_sync_enabled, owner_id, timestamps
- Columns: dataset_id, dataset_name, column_id, name, source_name, type, subtype, format, aggregation_type, min, max, cardinality
- Dataset_Usage: dataset_id, dataset_name, dashboard_id, dashboard_name

### Dashboard Describer (`src/dashboard_describer.py`)
Generates AI descriptions based on dashboard structure (no data retrieval).

```python
from src.dashboard_describer import DashboardDescriber

describer = DashboardDescriber()

# Single dashboard
result = describer.describe_dashboard(dashboard_id, style="business")

# All dashboards to Excel
describer.export_descriptions_to_excel(limit=10)
```

**Styles:**
- `business`: Focus on insights, value, and use cases
- `technical`: Structure, data sources, visualization types
- `brief`: 2-3 sentence summary

### Dashboard Updater (`src/dashboard_updater.py`)
Updates dashboard descriptions from CSV or Excel files.

```python
from src.dashboard_updater import DashboardUpdater

updater = DashboardUpdater()

# Preview changes
preview = updater.preview_updates("descriptions.xlsx")

# Apply updates
results = updater.update_from_file("descriptions.xlsx")
```

**Input file format:**
| id | description |
|----|-------------|
| dashboard-uuid | New description text |

Also accepts columns named `generated_description` or `new_description`.

### Luzmo Client (`src/luzmo_client.py`)
Core API client for Luzmo operations.

```python
from src.luzmo_client import LuzmoClient

client = LuzmoClient()

# List dashboards
dashboards = client.list_dashboards()

# Get specific dashboard
dashboard = client.get_dashboard(dashboard_id)

# Direct API request
response = client._make_request(
    action='get',  # get, create, update, delete
    resource='securable',
    find={'where': {'type': 'dashboard'}},
    properties={'description': {'en': 'New description'}},  # for updates
    id='resource-id'  # for specific resource operations
)
```

### LLM Analyzer (`src/llm_analyzer.py`)
Claude integration for AI-powered analysis.

```python
from src.llm_analyzer import LLMAnalyzer

llm = LLMAnalyzer(model="claude-3-haiku-20240307")

# Generate summary
summary = llm.generate_summary(dashboard_data_text)

# Structured summary
sections = llm.generate_structured_summary(
    dashboard_data_text,
    sections=["overview", "key_metrics", "insights"]
)

# Compare dashboards
comparison = llm.compare_dashboards(data1, data2)

# Q&A
answer = llm.answer_question(data, "What is the total revenue?")
```

## API Credentials

### Luzmo API
1. Log in to your Luzmo account
2. Go to Settings > API Keys
3. Create a new API key and token
4. Add to `.env` file

**Note:** Your API key permissions determine what you can read/update. A 403 error means you don't have write permission for that resource.

### Anthropic API
1. Sign up at https://console.anthropic.com
2. Create an API key
3. Add to `.env` file
4. Purchase credits at [console.anthropic.com/settings/billing](https://console.anthropic.com/settings/billing)

## Common Workflows

### 1. Audit All Dashboards
```bash
# Export everything
python export_dashboards.py
python export_datasets.py
```

### 2. Generate and Apply Descriptions
```bash
# Generate AI descriptions
python generate_dashboard_descriptions.py --style business

# Review and edit the Excel file, then apply
python update_dashboard_descriptions.py dashboard_descriptions_*.xlsx
```

### 3. Find Dataset Dependencies
```bash
python export_datasets.py
# Check the Dataset_Usage sheet to see which dashboards use which datasets
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 403 Forbidden | No write permission | Check API key permissions or dashboard ownership |
| 404 Not Found | Resource doesn't exist | Verify the ID is correct |
| Invalid argument: `*.xlsx` | Wildcards not supported | Use actual filename |

## Requirements

- Python 3.8+
- requests
- pandas
- openpyxl
- anthropic
- python-dotenv
- pyyaml

## License

This project is licensed under the MIT License.
