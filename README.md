# Luzmo API + LLM Dashboard Analyzer

A Python application that combines Luzmo's API with Anthropic's Claude to generate intelligent, data-driven summaries of your dashboards. Get precise analysis with exact numbers rather than relying on visual interpretation.

## Features

- **Precise Data Analysis**: Fetches actual data from Luzmo dashboards, not just visuals
- **AI-Powered Insights**: Uses Claude to generate intelligent summaries and insights
- **Multiple Output Formats**: Save summaries as text, markdown, or JSON
- **Structured Analysis**: Generate summaries with custom sections (overview, metrics, trends, etc.)
- **Dashboard Comparison**: Compare two dashboards side-by-side
- **Q&A Capability**: Ask specific questions about your dashboard data
- **Batch Processing**: Analyze multiple dashboards at once

## Architecture

This project implements **Approach 2** for dashboard analysis:

1. **Fetch Dashboard Metadata**: Pull chart types, filters, dimensions from Luzmo API
2. **Extract Data**: Get the actual underlying data behind each chart
3. **LLM Analysis**: Feed both metadata and data to Claude for structured commentary
4. **Save Summaries**: Store analysis in external files for easy access

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
LUZMO_API_HOST=https://api.luzmo.com

ANTHROPIC_API_KEY=your_anthropic_api_key

OUTPUT_DIR=./summaries
```

## Quick Start

### Option 1: Interactive Dashboard Browser
Run the interactive script to list and analyze dashboards:

```bash
python list_and_analyze_dashboards.py
```

This will:
1. List all your dashboards from Luzmo
2. Allow you to select one for AI analysis
3. Generate a comprehensive summary with Claude

### Option 2: Programmatic Usage

```python
from src.luzmo_client import LuzmoClient
from src.dashboard_summary_pipeline import DashboardSummaryPipeline

# List all dashboards
client = LuzmoClient()
dashboards = client.list_dashboards()

for dashboard in dashboards:
    print(f"Dashboard: {dashboard['name']} (ID: {dashboard['id']})")

# Generate AI summary for a specific dashboard
pipeline = DashboardSummaryPipeline()
result = pipeline.generate_summary(
    dashboard_id=dashboards[0]['id'],
    save_format="markdown"
)

print(f"Summary saved to: {result['filepath']}")
```

## Testing Your Connection

After setting up your credentials, test the connection:

```bash
python test_luzmo_connection.py
```

This will verify your API credentials are working and show how many dashboards are in your account.

## Iterating Through Dashboards

### Simple Iteration Example

```python
from src.luzmo_client import LuzmoClient

client = LuzmoClient()
dashboards = client.list_dashboards()

print(f"Found {len(dashboards)} dashboards\n")

for dashboard in dashboards:
    print(f"Dashboard: {dashboard['name']}")
    print(f"  ID: {dashboard['id']}")
    print(f"  Description: {dashboard.get('description', 'N/A')}")
    print(f"  Last Modified: {dashboard.get('modified_at', 'N/A')}")
    print()
```

### More Examples

See [iterate_dashboards_example.py](iterate_dashboards_example.py) for additional examples including:
- Finding dashboards by name
- Getting recently modified dashboards
- Fetching detailed dashboard information

## Usage Examples

### 1. Basic Dashboard Summary

Generate a comprehensive summary of a dashboard:

```python
from src.dashboard_summary_pipeline import DashboardSummaryPipeline

pipeline = DashboardSummaryPipeline(output_dir="./summaries")

result = pipeline.generate_summary(
    dashboard_id="dashboard-123",
    save_format="markdown"  # Options: 'text', 'markdown', 'json'
)

print(result['summary'])
```

### 2. Structured Summary with Sections

Generate a summary with specific sections:

```python
result = pipeline.generate_structured_summary(
    dashboard_id="dashboard-123",
    sections=["overview", "key_metrics", "trends", "insights", "recommendations"]
)
```

### 3. Custom Analysis Instructions

Provide custom analysis instructions:

```python
custom_prompt = """
Focus on:
1. Month-over-month growth rates
2. Top 3 performing products
3. Any concerning trends
4. Recommendations for improvement
"""

result = pipeline.generate_summary(
    dashboard_id="dashboard-123",
    custom_prompt=custom_prompt
)
```

### 4. Compare Two Dashboards

```python
result = pipeline.compare_dashboards(
    dashboard_id1="dashboard-123",
    dashboard_id2="dashboard-456",
    comparison_focus="Sales performance and customer metrics"
)
```

### 5. Answer Specific Questions

```python
answer = pipeline.answer_question(
    dashboard_id="dashboard-123",
    question="What was the total revenue in Q4 and how does it compare to Q3?"
)

print(answer)
```

### 6. Batch Processing

Process multiple dashboards at once:

```python
results = pipeline.batch_process_dashboards(
    dashboard_ids=["dashboard-1", "dashboard-2", "dashboard-3"],
    save_format="markdown"
)
```

## Project Structure

```
luzmo_api/
├── src/
│   ├── __init__.py
│   ├── luzmo_client.py              # Luzmo API client
│   ├── dashboard_analyzer.py        # Data extraction and structuring
│   ├── llm_analyzer.py              # Claude integration
│   ├── summary_writer.py            # File writing utilities
│   └── dashboard_summary_pipeline.py # Main orchestrator
├── summaries/                        # Generated summaries (created automatically)
├── example_usage.py                  # Usage examples
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
└── README.md                         # This file
```

## Module Overview

### `luzmo_client.py`
Handles authentication and API requests to Luzmo:
- `get_dashboard()` - Fetch dashboard metadata
- `get_dashboard_data()` - Get all dashboard data
- `get_chart()` - Fetch chart metadata
- `get_chart_data()` - Get chart data
- `list_dashboards()` - List all dashboards

### `dashboard_analyzer.py`
Extracts and structures dashboard data:
- `get_dashboard_metadata()` - Get structured metadata
- `get_chart_data_structured()` - Get chart data with summaries
- `get_full_dashboard_data()` - Complete dashboard extraction
- `format_for_llm()` - Format data for Claude

### `llm_analyzer.py`
Uses Claude for analysis:
- `generate_summary()` - General summary
- `generate_structured_summary()` - Multi-section summary
- `compare_dashboards()` - Compare two dashboards
- `answer_question()` - Q&A about dashboard

### `summary_writer.py`
Saves summaries to files:
- `save_text_summary()` - Plain text format
- `save_markdown_summary()` - Markdown format
- `save_json_summary()` - JSON with full data
- `save_structured_summary()` - Structured markdown

### `dashboard_summary_pipeline.py`
Main orchestrator that combines all components.

## API Credentials

### Luzmo API
1. Log in to your Luzmo account
2. Go to Settings > API Keys
3. Create a new API key and token
4. Add to `.env` file

### Anthropic API
1. Sign up at https://console.anthropic.com
2. Create an API key
3. Add to `.env` file

## Output Formats

### Text Format
Plain text with headers and structured content.

### Markdown Format
Markdown with proper formatting, headings, and lists. Great for documentation.

### JSON Format
JSON with complete metadata and data. Useful for further processing or archiving.

## Advanced Configuration

### Custom Output Directory
```python
pipeline = DashboardSummaryPipeline(output_dir="/path/to/summaries")
```

### Custom Claude Model
```python
from src.llm_analyzer import LLMAnalyzer

llm_analyzer = LLMAnalyzer(model="claude-3-opus-20240229")
```

### Direct Component Usage
```python
from src.luzmo_client import LuzmoClient
from src.dashboard_analyzer import DashboardAnalyzer

client = LuzmoClient()
analyzer = DashboardAnalyzer(client)

# Get just the metadata
metadata = analyzer.get_dashboard_metadata("dashboard-123")
```

## Error Handling

The pipeline includes error handling for:
- Missing API credentials
- Invalid dashboard IDs
- API connection issues
- Data formatting errors

Errors are raised with descriptive messages for easy debugging.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues or questions:
1. Check the example usage in `example_usage.py`
2. Review the module documentation in source files
3. Open an issue on GitHub

## Roadmap

- [ ] Add support for scheduled dashboard analysis
- [ ] Implement dashboard change detection
- [ ] Add email notifications for summaries
- [ ] Create web interface for dashboard selection
- [ ] Support for exporting to other formats (PDF, HTML)
- [ ] Integration with Slack/Teams for automated reporting
