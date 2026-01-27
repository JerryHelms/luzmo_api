"""
Dataset Exporter
Retrieves all datasets, columns, and usage information, exports to Excel.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .luzmo_client import LuzmoClient
from .utils import get_dashboard_name


class DatasetExporter:
    """Exports Luzmo dataset metadata to Excel."""

    def __init__(self, client: Optional[LuzmoClient] = None):
        """
        Initialize dataset exporter.

        Args:
            client: LuzmoClient instance (creates one if not provided)
        """
        self.client = client or LuzmoClient()

    def get_all_datasets(self) -> List[Dict[str, Any]]:
        """
        Fetch all datasets.

        Returns:
            List of dataset objects with metadata
        """
        response = self.client._make_request(
            action='get',
            resource='securable',
            find={
                'where': {
                    'type': 'dataset'
                },
                'attributes': [
                    'id', 'name', 'description', 'subtype', 'rows',
                    'source_dataset', 'source_sheet', 'source_query',
                    'storage', 'cache',
                    'meta_sync_enabled', 'meta_sync_interval',
                    'last_metadata_sync_at',
                    'owner_id', 'account_id', 'modifier_id',
                    'created_at', 'modified_at'
                ],
                'order': [['modified_at', 'desc']]
            }
        )

        return response.get('rows', [])

    def get_all_columns(self) -> List[Dict[str, Any]]:
        """
        Fetch all columns across all datasets.

        Returns:
            List of column objects
        """
        response = self.client._make_request(
            action='get',
            resource='column',
            find={
                'attributes': [
                    'id', 'name', 'source_name', 'type', 'subtype',
                    'format', 'aggregation_type', 'order',
                    'minimum', 'maximum', 'cardinality',
                    'securable_id', 'created_at', 'updated_at'
                ],
                'order': [['securable_id', 'asc'], ['order', 'asc']]
            }
        )

        return response.get('rows', [])

    def get_dataset_usage(self) -> List[Dict[str, Any]]:
        """
        Fetch all dashboards and extract which datasets they use.

        Returns:
            List of dataset-dashboard usage records
        """
        response = self.client._make_request(
            action='get',
            resource='securable',
            find={
                'where': {
                    'type': 'dashboard',
                    'derived': False
                },
                'attributes': ['id', 'name', 'contents'],
                'order': [['modified_at', 'desc']]
            }
        )

        dashboards = response.get('rows', [])
        usage_records = []

        for dashboard in dashboards:
            dashboard_id = dashboard.get('id', '')
            dashboard_name = get_dashboard_name(dashboard)
            contents = dashboard.get('contents', {})

            if not isinstance(contents, dict):
                continue

            # Get datasets from datasetLinks
            dataset_links = contents.get('datasetLinks', {})
            datasets_found = set(dataset_links.keys())

            # Also scan slots for dataset references (field: 'set')
            views = contents.get('views', [])
            for view in views:
                if not isinstance(view, dict):
                    continue
                items = view.get('items', [])
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    slots = item.get('slots', [])
                    for slot in slots:
                        if not isinstance(slot, dict):
                            continue
                        for content in slot.get('content', []):
                            if isinstance(content, dict):
                                ds_id = content.get('set')
                                if ds_id:
                                    datasets_found.add(ds_id)

            # Create a record for each dataset used
            for dataset_id in datasets_found:
                usage_records.append({
                    'dashboard_id': dashboard_id,
                    'dashboard_name': dashboard_name,
                    'dataset_id': dataset_id
                })

        return usage_records

    def _extract_text(self, value: Any, preferred_lang: str = 'en') -> str:
        """
        Extract text from various formats (string, dict with language keys).
        """
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            if preferred_lang in value:
                return value[preferred_lang]
            if value:
                return str(list(value.values())[0])
        return ''

    def build_datasets_dataframe(self, datasets: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Build a DataFrame of dataset information.
        """
        records = []
        for ds in datasets:
            record = {
                'id': ds.get('id', ''),
                'name': self._extract_text(ds.get('name', '')),
                'description': self._extract_text(ds.get('description', '')),
                'subtype': ds.get('subtype', ''),
                'rows': ds.get('rows', 0),
                'source_sheet': ds.get('source_sheet', ''),
                'storage': ds.get('storage', ''),
                'cache': ds.get('cache', ''),
                'meta_sync_enabled': ds.get('meta_sync_enabled', ''),
                'meta_sync_interval': ds.get('meta_sync_interval', ''),
                'last_metadata_sync_at': ds.get('last_metadata_sync_at', ''),
                'owner_id': ds.get('owner_id', ''),
                'account_id': ds.get('account_id', ''),
                'modifier_id': ds.get('modifier_id', ''),
                'created_at': ds.get('created_at', ''),
                'modified_at': ds.get('modified_at', ''),
            }
            records.append(record)

        return pd.DataFrame(records)

    def build_columns_dataframe(self, columns: List[Dict[str, Any]],
                                 dataset_lookup: Dict[str, str]) -> pd.DataFrame:
        """
        Build a DataFrame of column information.

        Args:
            columns: List of column objects
            dataset_lookup: Dict mapping dataset_id to dataset_name
        """
        records = []
        for col in columns:
            dataset_id = col.get('securable_id', '')
            record = {
                'dataset_id': dataset_id,
                'dataset_name': dataset_lookup.get(dataset_id, ''),
                'column_id': col.get('id', ''),
                'name': self._extract_text(col.get('name', '')),
                'source_name': col.get('source_name', ''),
                'type': col.get('type', ''),
                'subtype': col.get('subtype', ''),
                'format': col.get('format', ''),
                'aggregation_type': col.get('aggregation_type', ''),
                'order': col.get('order', ''),
                'minimum': col.get('minimum', ''),
                'maximum': col.get('maximum', ''),
                'cardinality': col.get('cardinality', ''),
                'created_at': col.get('created_at', ''),
                'updated_at': col.get('updated_at', ''),
            }
            records.append(record)

        return pd.DataFrame(records)

    def build_usage_dataframe(self, usage: List[Dict[str, Any]],
                               dataset_lookup: Dict[str, str]) -> pd.DataFrame:
        """
        Build a DataFrame of dataset usage (which dashboards use which datasets).
        """
        records = []
        for u in usage:
            dataset_id = u.get('dataset_id', '')
            record = {
                'dataset_id': dataset_id,
                'dataset_name': dataset_lookup.get(dataset_id, ''),
                'dashboard_id': u.get('dashboard_id', ''),
                'dashboard_name': u.get('dashboard_name', ''),
            }
            records.append(record)

        return pd.DataFrame(records)

    def export_to_excel(self, output_path: Optional[str] = None) -> str:
        """
        Export all dataset details to an Excel file.

        Args:
            output_path: Path for output file (auto-generated if not provided)

        Returns:
            Path to the created Excel file
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'datasets_export_{timestamp}.xlsx'

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Fetch datasets
        print("Fetching datasets...")
        datasets = self.get_all_datasets()
        print(f"Found {len(datasets)} datasets")

        # Build dataset lookup for joining
        dataset_lookup = {
            ds.get('id', ''): self._extract_text(ds.get('name', ''))
            for ds in datasets
        }

        # Fetch columns
        print("Fetching columns...")
        columns = self.get_all_columns()
        print(f"Found {len(columns)} columns")

        # Fetch usage
        print("Fetching dataset usage in dashboards...")
        usage = self.get_dataset_usage()
        print(f"Found {len(usage)} dataset-dashboard relationships")

        # Build DataFrames
        print("Building datasets summary...")
        df_datasets = self.build_datasets_dataframe(datasets)

        print("Building columns list...")
        df_columns = self.build_columns_dataframe(columns, dataset_lookup)

        print("Building usage matrix...")
        df_usage = self.build_usage_dataframe(usage, dataset_lookup)

        # Write to Excel
        print(f"Writing to {output_path}...")
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df_datasets.to_excel(writer, sheet_name='Datasets', index=False)

            if not df_columns.empty:
                df_columns.to_excel(writer, sheet_name='Columns', index=False)

            if not df_usage.empty:
                df_usage.to_excel(writer, sheet_name='Dataset_Usage', index=False)

        print(f"Export complete: {output_path}")
        return str(output_file.absolute())


def main():
    """Main function to export datasets to Excel."""
    exporter = DatasetExporter()
    output_file = exporter.export_to_excel()
    print(f"\nDatasets exported to: {output_file}")


if __name__ == "__main__":
    main()
