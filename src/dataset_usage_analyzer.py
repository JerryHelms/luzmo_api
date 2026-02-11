#!/usr/bin/env python3
"""
Dataset Usage Analyzer

Analyzes which datasets are used most frequently across dashboards,
helping identify critical datasets, unused datasets, and usage patterns.
"""

from typing import Dict, List, Any, Optional
from collections import defaultdict
import pandas as pd
from datetime import datetime
from .luzmo_client import LuzmoClient
from .utils import get_dashboard_name


class DatasetUsageAnalyzer:
    """
    Analyzes dataset usage patterns across dashboards.
    """

    def __init__(self, api_key: Optional[str] = None, api_token: Optional[str] = None):
        """
        Initialize the analyzer.

        Args:
            api_key: Luzmo API key (optional, uses env var if not provided)
            api_token: Luzmo API token (optional, uses env var if not provided)
        """
        self.client = LuzmoClient(api_key=api_key, api_token=api_token)

    def get_all_datasets(self) -> List[Dict[str, Any]]:
        """
        Fetch all datasets.

        Returns:
            List of dataset objects
        """
        response = self.client._make_request(
            action='get',
            resource='securable',
            find={
                'where': {
                    'type': 'dataset',
                    'derived': False
                },
                'attributes': ['id', 'name', 'description', 'subtype', 'rows'],
                'order': [['modified_at', 'desc']]
            }
        )
        return response.get('rows', [])

    def get_all_dashboards(self) -> List[Dict[str, Any]]:
        """
        Fetch all dashboards.

        Returns:
            List of dashboard objects
        """
        response = self.client._make_request(
            action='get',
            resource='securable',
            find={
                'where': {
                    'type': 'dashboard',
                    'derived': False
                },
                'attributes': ['id', 'name', 'slug', 'subtype'],
                'order': [['modified_at', 'desc']]
            }
        )
        return response.get('rows', [])

    def get_dashboard_datasets(self, dashboard_id: str) -> List[str]:
        """
        Get all datasets used by a specific dashboard.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            List of dataset IDs used by the dashboard
        """
        try:
            response = self.client._make_request(
                action='get',
                resource='securable',
                find={
                    'where': {'id': dashboard_id},
                    'attributes': ['id', 'name', 'contents']
                }
            )

            rows = response.get('rows', [])
            if not rows:
                return []

            dashboard = rows[0]
            contents = dashboard.get('contents', {})

            # Extract dataset IDs from dashboard contents
            dataset_ids = set()

            # Method 1: Get datasets from datasetLinks
            dataset_links = contents.get('datasetLinks', {})
            dataset_ids.update(dataset_links.keys())

            # Method 2: Scan views → items → slots → content for 'set' field
            views = contents.get('views', [])
            for view in views:
                if isinstance(view, dict):
                    items = view.get('items', [])
                    for item in items:
                        if isinstance(item, dict):
                            slots = item.get('slots', [])
                            for slot in slots:
                                if isinstance(slot, dict):
                                    # Check content array for 'set' field
                                    content_list = slot.get('content', [])
                                    for content in content_list:
                                        if isinstance(content, dict):
                                            ds_id = content.get('set')
                                            if ds_id:
                                                dataset_ids.add(ds_id)

            return list(dataset_ids)

        except Exception as e:
            print(f"Warning: Could not get datasets for dashboard {dashboard_id}: {e}")
            return []

    def analyze_usage(self, include_dashboard_details: bool = False) -> Dict[str, Any]:
        """
        Analyze dataset usage across all dashboards.

        Args:
            include_dashboard_details: Include list of dashboards using each dataset

        Returns:
            Dictionary with usage statistics
        """
        print("Fetching datasets...")
        datasets = self.get_all_datasets()

        print("Fetching dashboards...")
        dashboards = self.get_all_dashboards()

        print(f"Analyzing usage for {len(datasets)} datasets across {len(dashboards)} dashboards...")

        # Track usage
        dataset_usage = defaultdict(lambda: {
            'count': 0,
            'dashboards': [],
            'dataset_name': '',
            'dataset_subtype': '',
            'dataset_rows': 0
        })

        # Get dataset metadata
        for dataset in datasets:
            dataset_id = dataset.get('id')
            dataset_usage[dataset_id]['dataset_name'] = dataset.get('name', {}).get('en', 'N/A')
            dataset_usage[dataset_id]['dataset_subtype'] = dataset.get('subtype', 'N/A')
            dataset_usage[dataset_id]['dataset_rows'] = dataset.get('rows', 0)

        # Analyze each dashboard
        total_dashboards = len(dashboards)
        for i, dashboard in enumerate(dashboards, 1):
            dashboard_id = dashboard.get('id')
            dashboard_name = get_dashboard_name(dashboard)

            if i % 10 == 0 or i == total_dashboards:
                print(f"  Processing dashboard {i}/{total_dashboards}...")

            dataset_ids = self.get_dashboard_datasets(dashboard_id)

            for dataset_id in dataset_ids:
                dataset_usage[dataset_id]['count'] += 1
                if include_dashboard_details:
                    dataset_usage[dataset_id]['dashboards'].append({
                        'id': dashboard_id,
                        'name': dashboard_name
                    })

        # Convert to list and sort by usage count
        usage_list = []
        for dataset_id, usage_data in dataset_usage.items():
            usage_list.append({
                'dataset_id': dataset_id,
                'dataset_name': usage_data['dataset_name'],
                'dataset_subtype': usage_data['dataset_subtype'],
                'dataset_rows': usage_data['dataset_rows'],
                'usage_count': usage_data['count'],
                'dashboards': usage_data['dashboards'] if include_dashboard_details else []
            })

        # Sort by usage count (descending)
        usage_list.sort(key=lambda x: x['usage_count'], reverse=True)

        return {
            'total_datasets': len(datasets),
            'total_dashboards': len(dashboards),
            'datasets_in_use': sum(1 for u in usage_list if u['usage_count'] > 0),
            'datasets_unused': sum(1 for u in usage_list if u['usage_count'] == 0),
            'usage_data': usage_list,
            'generated_at': datetime.now().isoformat()
        }

    def print_summary(self, results: Dict[str, Any], limit: int = 20):
        """
        Print a summary of usage statistics.

        Args:
            results: Results from analyze_usage()
            limit: Number of top datasets to show
        """
        print("\n" + "=" * 80)
        print("Dataset Usage Analysis")
        print("=" * 80)

        print(f"\nOverall Statistics:")
        print(f"  Total Datasets: {results['total_datasets']}")
        print(f"  Total Dashboards: {results['total_dashboards']}")
        print(f"  Datasets in Use: {results['datasets_in_use']}")
        print(f"  Unused Datasets: {results['datasets_unused']}")

        # Most used datasets
        usage_data = results['usage_data']
        most_used = [d for d in usage_data if d['usage_count'] > 0][:limit]

        if most_used:
            print(f"\n{'-' * 80}")
            print(f"Top {min(limit, len(most_used))} Most Used Datasets:")
            print(f"{'-' * 80}")

            for i, dataset in enumerate(most_used, 1):
                print(f"\n{i}. {dataset['dataset_name']}")
                print(f"   ID: {dataset['dataset_id'][:16]}...")
                print(f"   Type: {dataset['dataset_subtype']}")
                print(f"   Rows: {dataset['dataset_rows']:,}")
                print(f"   Used by: {dataset['usage_count']} dashboard(s)")

        # Unused datasets
        unused = [d for d in usage_data if d['usage_count'] == 0]

        if unused:
            print(f"\n{'-' * 80}")
            print(f"Unused Datasets ({len(unused)}):")
            print(f"{'-' * 80}")

            for i, dataset in enumerate(unused[:10], 1):
                print(f"{i}. {dataset['dataset_name']} (ID: {dataset['dataset_id'][:16]}...)")

            if len(unused) > 10:
                print(f"   ... and {len(unused) - 10} more")

        print(f"\n{'=' * 80}\n")

    def export_to_excel(self, filename: Optional[str] = None) -> str:
        """
        Export usage analysis to Excel.

        Args:
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to the output file
        """
        results = self.analyze_usage(include_dashboard_details=True)

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'dataset_usage_analysis_{timestamp}.xlsx'

        usage_data = results['usage_data']

        # Prepare summary data
        summary_data = []
        for dataset in usage_data:
            summary_data.append({
                'Dataset ID': dataset['dataset_id'],
                'Dataset Name': dataset['dataset_name'],
                'Type': dataset['dataset_subtype'],
                'Rows': dataset['dataset_rows'],
                'Usage Count': dataset['usage_count'],
                'Status': 'In Use' if dataset['usage_count'] > 0 else 'Unused'
            })

        # Prepare detailed usage data
        detail_data = []
        for dataset in usage_data:
            if dataset['dashboards']:
                for dashboard in dataset['dashboards']:
                    detail_data.append({
                        'Dataset ID': dataset['dataset_id'],
                        'Dataset Name': dataset['dataset_name'],
                        'Dashboard ID': dashboard['id'],
                        'Dashboard Name': dashboard['name']
                    })

        # Prepare statistics
        stats_data = [
            {'Metric': 'Total Datasets', 'Value': results['total_datasets']},
            {'Metric': 'Total Dashboards', 'Value': results['total_dashboards']},
            {'Metric': 'Datasets in Use', 'Value': results['datasets_in_use']},
            {'Metric': 'Unused Datasets', 'Value': results['datasets_unused']},
            {'Metric': 'Generated At', 'Value': results['generated_at']}
        ]

        # Write to Excel
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Summary sheet
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Dataset Usage Summary', index=False)

            # Detail sheet
            if detail_data:
                df_detail = pd.DataFrame(detail_data)
                df_detail.to_excel(writer, sheet_name='Detailed Usage', index=False)

            # Statistics sheet
            df_stats = pd.DataFrame(stats_data)
            df_stats.to_excel(writer, sheet_name='Statistics', index=False)

        print(f"\nExported usage analysis to: {filename}")
        return filename

    def get_unused_datasets(self) -> List[Dict[str, Any]]:
        """
        Get all datasets that are not used by any dashboard.

        Returns:
            List of unused dataset objects
        """
        results = self.analyze_usage(include_dashboard_details=False)
        unused = [d for d in results['usage_data'] if d['usage_count'] == 0]
        return unused

    def get_most_used_datasets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most frequently used datasets.

        Args:
            limit: Number of datasets to return

        Returns:
            List of most used dataset objects
        """
        results = self.analyze_usage(include_dashboard_details=False)
        most_used = [d for d in results['usage_data'] if d['usage_count'] > 0][:limit]
        return most_used

    def get_dataset_dashboards(self, dataset_id: str) -> List[Dict[str, str]]:
        """
        Get all dashboards that use a specific dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            List of dashboard objects using the dataset
        """
        dashboards = self.get_all_dashboards()
        using_dashboards = []

        for dashboard in dashboards:
            dashboard_id = dashboard.get('id')
            dataset_ids = self.get_dashboard_datasets(dashboard_id)

            if dataset_id in dataset_ids:
                using_dashboards.append({
                    'id': dashboard_id,
                    'name': get_dashboard_name(dashboard),
                    'subtype': dashboard.get('subtype', 'N/A')
                })

        return using_dashboards
