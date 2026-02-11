# Dataset Usage Analysis

Analyze which datasets are used most frequently across dashboards to identify critical datasets, find unused datasets, and understand data dependencies.

## Quick Start

### View Usage Summary
```bash
python analyze_dataset_usage.py
```

Shows:
- Total datasets and dashboards
- Datasets in use vs unused
- Top 20 most used datasets
- List of unused datasets

### Export to Excel
```bash
python analyze_dataset_usage.py --export
```

Creates an Excel file with three sheets:
- **Dataset Usage Summary**: All datasets with usage counts
- **Detailed Usage**: Dataset-to-dashboard mappings
- **Statistics**: Overall metrics

### Show Unused Datasets Only
```bash
python analyze_dataset_usage.py --unused
```

Lists all datasets that are not used by any dashboard.

### Top N Most Used Datasets
```bash
python analyze_dataset_usage.py --top 50
```

Shows the top 50 most frequently used datasets.

### Find Dashboards Using Specific Dataset
```bash
python analyze_dataset_usage.py --dataset "dataset-id-here"
```

Lists all dashboards that use a specific dataset.

## Python API

### Basic Usage

```python
from src.dataset_usage_analyzer import DatasetUsageAnalyzer

# Initialize analyzer
analyzer = DatasetUsageAnalyzer()

# Get full analysis
results = analyzer.analyze_usage(include_dashboard_details=True)

# Print summary
analyzer.print_summary(results, limit=20)
```

### Get Unused Datasets

```python
unused = analyzer.get_unused_datasets()

for dataset in unused:
    print(f"{dataset['dataset_name']}: {dataset['dataset_id']}")
```

### Get Most Used Datasets

```python
most_used = analyzer.get_most_used_datasets(limit=10)

for dataset in most_used:
    print(f"{dataset['dataset_name']}: {dataset['usage_count']} dashboards")
```

### Find Dashboards Using a Dataset

```python
dashboards = analyzer.get_dataset_dashboards('dataset-id-here')

for dashboard in dashboards:
    print(f"- {dashboard['name']} ({dashboard['id']})")
```

### Export to Excel

```python
# Auto-generated filename
filename = analyzer.export_to_excel()

# Custom filename
filename = analyzer.export_to_excel('my_analysis.xlsx')
```

## Output Format

### analyze_usage() Returns:

```python
{
    'total_datasets': 150,
    'total_dashboards': 137,
    'datasets_in_use': 120,
    'datasets_unused': 30,
    'usage_data': [
        {
            'dataset_id': 'abc-123',
            'dataset_name': 'Work Orders',
            'dataset_subtype': 'live',
            'dataset_rows': 15000,
            'usage_count': 25,
            'dashboards': [  # if include_dashboard_details=True
                {'id': 'dash-1', 'name': 'Dashboard Name'},
                ...
            ]
        },
        ...
    ],
    'generated_at': '2026-01-30T12:00:00'
}
```

## Use Cases

### 1. Identify Critical Datasets
Find datasets used by many dashboards to prioritize maintenance and optimization.

```bash
python analyze_dataset_usage.py --top 10
```

### 2. Find Unused Datasets for Cleanup
Identify datasets that can potentially be archived or deleted.

```bash
python analyze_dataset_usage.py --unused
```

### 3. Impact Analysis
Before modifying a dataset, find all dashboards that would be affected.

```bash
python analyze_dataset_usage.py --dataset "your-dataset-id"
```

### 4. Data Governance
Export usage data for documentation and compliance purposes.

```bash
python analyze_dataset_usage.py --export
```

### 5. Optimize Data Pipeline
Identify which datasets are most critical for your BI infrastructure.

```python
from src.dataset_usage_analyzer import DatasetUsageAnalyzer

analyzer = DatasetUsageAnalyzer()
most_used = analyzer.get_most_used_datasets(limit=20)

# Focus optimization efforts on these datasets
for dataset in most_used:
    if dataset['usage_count'] > 10:
        print(f"High priority: {dataset['dataset_name']}")
```

## Excel Export Sheets

### Sheet 1: Dataset Usage Summary
| Dataset ID | Dataset Name | Type | Rows | Usage Count | Status |
|------------|--------------|------|------|-------------|--------|
| abc-123 | Work Orders | live | 15000 | 25 | In Use |
| def-456 | Events | live | 8000 | 12 | In Use |
| ghi-789 | Old Data | csv | 100 | 0 | Unused |

### Sheet 2: Detailed Usage
| Dataset ID | Dataset Name | Dashboard ID | Dashboard Name |
|------------|--------------|--------------|----------------|
| abc-123 | Work Orders | dash-1 | Work Order Progress |
| abc-123 | Work Orders | dash-2 | WO Summary |

### Sheet 3: Statistics
| Metric | Value |
|--------|-------|
| Total Datasets | 150 |
| Total Dashboards | 137 |
| Datasets in Use | 120 |
| Unused Datasets | 30 |

## Performance Notes

- Analysis time depends on number of dashboards
- ~1-2 seconds per dashboard to extract dataset references
- For 137 dashboards: ~3-5 minutes total
- Results are calculated fresh each time (no caching)

## Integration with Existing Tools

### Combine with Dataset Export

```bash
# Export all dataset metadata
python export_datasets.py

# Analyze usage patterns
python analyze_dataset_usage.py --export

# Compare the two Excel files to get complete picture
```

### Use with Dashboard Documentation

```bash
# Generate dashboard docs
python regenerate_all_docs.py

# Analyze dataset usage
python analyze_dataset_usage.py

# Cross-reference to understand data flows
```

## Example Output

```
================================================================================
Dataset Usage Analysis
================================================================================

Overall Statistics:
  Total Datasets: 150
  Total Dashboards: 137
  Datasets in Use: 120
  Unused Datasets: 30

--------------------------------------------------------------------------------
Top 20 Most Used Datasets:
--------------------------------------------------------------------------------

1. Work Orders
   ID: f3c8d9e1-a2b4...
   Type: live
   Rows: 15,234
   Used by: 25 dashboard(s)

2. Events
   ID: a1b2c3d4-e5f6...
   Type: live
   Rows: 8,912
   Used by: 18 dashboard(s)

3. Invoices
   ID: 9876fedc-ba98...
   Type: live
   Rows: 12,456
   Used by: 15 dashboard(s)

...

--------------------------------------------------------------------------------
Unused Datasets (30):
--------------------------------------------------------------------------------
1. Old Import 2023 (ID: abc123...)
2. Test Dataset (ID: def456...)
3. Backup Data (ID: ghi789...)
   ... and 27 more

================================================================================
```

## Tips

1. **Regular Analysis**: Run monthly to track dataset usage trends
2. **Before Cleanup**: Always check usage before deleting datasets
3. **Performance Optimization**: Focus on datasets with highest usage counts
4. **Data Governance**: Export results for compliance documentation
5. **Impact Assessment**: Check usage before making schema changes

## Troubleshooting

**Slow performance?**
- Analysis processes each dashboard individually
- Expected for large numbers of dashboards
- Consider running during off-peak hours

**Missing datasets?**
- Only analyzes non-derived datasets
- Derived datasets are excluded by default
- Check API permissions if datasets seem missing

**Incorrect counts?**
- Counts are based on current dashboard contents
- Deleted dashboards are not included
- Archived datasets may show zero usage
