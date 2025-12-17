"""
Dashboard Analyzer
Extracts and structures dashboard metadata and data for LLM analysis.
"""

from typing import Dict, List, Any
from .luzmo_client import LuzmoClient
import pandas as pd


class DashboardAnalyzer:
    """Analyzes Luzmo dashboards and prepares data for LLM processing."""

    def __init__(self, client: LuzmoClient):
        """
        Initialize dashboard analyzer.

        Args:
            client: LuzmoClient instance
        """
        self.client = client

    def get_dashboard_metadata(self, dashboard_id: str) -> Dict[str, Any]:
        """
        Fetch and structure dashboard metadata.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            Structured metadata including charts, filters, dimensions
        """
        dashboard = self.client.get_dashboard(dashboard_id)

        metadata = {
            'dashboard_id': dashboard_id,
            'dashboard_name': dashboard.get('name', 'Unknown'),
            'description': dashboard.get('description', ''),
            'charts': [],
            'filters': dashboard.get('filters', []),
            'dimensions': []
        }

        # Extract chart information
        charts = dashboard.get('charts', [])
        for chart in charts:
            chart_info = {
                'chart_id': chart.get('id'),
                'chart_type': chart.get('type'),
                'title': chart.get('title', 'Untitled'),
                'dimensions': chart.get('dimensions', []),
                'measures': chart.get('measures', []),
                'filters': chart.get('filters', [])
            }
            metadata['charts'].append(chart_info)

            # Collect unique dimensions
            for dim in chart.get('dimensions', []):
                if dim not in metadata['dimensions']:
                    metadata['dimensions'].append(dim)

        return metadata

    def get_chart_data_structured(self, chart_id: str) -> Dict[str, Any]:
        """
        Fetch and structure data for a specific chart.

        Args:
            chart_id: Chart ID

        Returns:
            Structured chart data with summary statistics
        """
        chart_metadata = self.client.get_chart(chart_id)
        chart_data = self.client.get_chart_data(chart_id)

        structured_data = {
            'chart_id': chart_id,
            'chart_type': chart_metadata.get('type'),
            'title': chart_metadata.get('title', 'Untitled'),
            'data': chart_data.get('data', []),
            'row_count': len(chart_data.get('data', [])),
            'columns': chart_data.get('columns', []),
            'summary': self._generate_data_summary(chart_data)
        }

        return structured_data

    def get_full_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """
        Fetch complete dashboard data including all charts.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            Complete dashboard data with metadata and all chart data
        """
        metadata = self.get_dashboard_metadata(dashboard_id)
        dashboard_data = {
            'metadata': metadata,
            'charts_data': []
        }

        # Fetch data for each chart
        for chart in metadata['charts']:
            chart_id = chart['chart_id']
            chart_data = self.get_chart_data_structured(chart_id)
            dashboard_data['charts_data'].append(chart_data)

        return dashboard_data

    def _generate_data_summary(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary statistics for chart data.

        Args:
            chart_data: Raw chart data

        Returns:
            Summary statistics
        """
        data = chart_data.get('data', [])
        columns = chart_data.get('columns', [])

        if not data or not columns:
            return {'note': 'No data available'}

        summary = {
            'total_rows': len(data),
            'columns': columns
        }

        # Convert to DataFrame for easier analysis
        try:
            df = pd.DataFrame(data)

            # Add numeric summaries
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                summary['numeric_summary'] = {}
                for col in numeric_cols:
                    summary['numeric_summary'][col] = {
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'mean': float(df[col].mean()),
                        'sum': float(df[col].sum())
                    }

            # Add categorical summaries
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            if categorical_cols:
                summary['categorical_summary'] = {}
                for col in categorical_cols:
                    top_values = df[col].value_counts().head(5).to_dict()
                    summary['categorical_summary'][col] = {
                        'unique_count': int(df[col].nunique()),
                        'top_values': top_values
                    }

        except Exception as e:
            summary['error'] = f"Could not generate detailed summary: {str(e)}"

        return summary

    def format_for_llm(self, dashboard_data: Dict[str, Any]) -> str:
        """
        Format dashboard data as text for LLM consumption.

        Args:
            dashboard_data: Complete dashboard data

        Returns:
            Formatted text description
        """
        metadata = dashboard_data['metadata']
        charts_data = dashboard_data['charts_data']

        output = []
        output.append(f"Dashboard: {metadata['dashboard_name']}")
        if metadata['description']:
            output.append(f"Description: {metadata['description']}")
        output.append(f"\nTotal Charts: {len(metadata['charts'])}")

        if metadata['filters']:
            output.append(f"Filters: {', '.join([f['name'] for f in metadata['filters']])}")

        output.append("\n" + "="*80)

        # Format each chart
        for chart_data in charts_data:
            output.append(f"\n\nChart: {chart_data['title']}")
            output.append(f"Type: {chart_data['chart_type']}")
            output.append(f"Rows: {chart_data['row_count']}")

            summary = chart_data['summary']

            # Numeric summaries
            if 'numeric_summary' in summary:
                output.append("\nNumeric Data:")
                for col, stats in summary['numeric_summary'].items():
                    output.append(f"  {col}:")
                    output.append(f"    Sum: {stats['sum']:.2f}")
                    output.append(f"    Mean: {stats['mean']:.2f}")
                    output.append(f"    Range: {stats['min']:.2f} - {stats['max']:.2f}")

            # Categorical summaries
            if 'categorical_summary' in summary:
                output.append("\nCategorical Data:")
                for col, stats in summary['categorical_summary'].items():
                    output.append(f"  {col}: {stats['unique_count']} unique values")
                    if stats['top_values']:
                        output.append(f"    Top values: {list(stats['top_values'].keys())[:3]}")

            # Sample data
            if chart_data['data'] and len(chart_data['data']) > 0:
                output.append(f"\nSample Data (first 3 rows):")
                for i, row in enumerate(chart_data['data'][:3]):
                    output.append(f"  Row {i+1}: {row}")

            output.append("\n" + "-"*80)

        return "\n".join(output)
