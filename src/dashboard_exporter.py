"""
Dashboard Exporter
Retrieves all dashboards and associated details, exports to Excel or BigQuery.
Does not retrieve actual data or submit to LLM.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .luzmo_client import LuzmoClient
from .utils import get_dashboard_name, get_dashboard_description

# BigQuery imports (optional)
try:
    import pandas_gbq
    from google.cloud import bigquery
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False


class DashboardExporter:
    """Exports Luzmo dashboard metadata to Excel."""

    def __init__(self, client: Optional[LuzmoClient] = None):
        """
        Initialize dashboard exporter.

        Args:
            client: LuzmoClient instance (creates one if not provided)
        """
        self.client = client or LuzmoClient()

    def get_all_dashboards_with_details(self) -> List[Dict[str, Any]]:
        """
        Fetch all dashboards with their full details.

        Returns:
            List of dashboard objects with metadata
        """
        response = self.client._make_request(
            action='get',
            resource='securable',
            find={
                'where': {
                    'type': 'dashboard',
                    'derived': False
                },
                'attributes': [
                    'id', 'name', 'description', 'modified_at', 'created_at',
                    'slug', 'type', 'subtype', 'contents', 'options',
                    'owner_id', 'account_id', 'modifier_id', 'template_id'
                ],
                'order': [['modified_at', 'desc']]
            }
        )

        return response.get('rows', [])

    def get_all_collections(self) -> List[Dict[str, Any]]:
        """
        Fetch all collections with their associated securables.

        Returns:
            List of collection objects with securables
        """
        response = self.client._make_request(
            action='get',
            resource='collection',
            find={
                'include': [{'model': 'Securable', 'attributes': ['id', 'name', 'type']}]
            }
        )

        return response.get('rows', [])

    def build_collections_dataframe(self, collections: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Build a DataFrame of collection information.

        Args:
            collections: List of collection objects

        Returns:
            DataFrame with collection information
        """
        records = []
        for col in collections:
            securables = col.get('securables', [])
            dashboards = [s for s in securables if s.get('type') == 'dashboard']
            datasets = [s for s in securables if s.get('type') == 'dataset']

            record = {
                'id': col.get('id', ''),
                'name': self._extract_text(col.get('name', '')),
                'favorite': col.get('favorite', False),
                'dashboard_count': len(dashboards),
                'dataset_count': len(datasets),
                'created_at': col.get('created_at', ''),
                'updated_at': col.get('updated_at', ''),
            }
            records.append(record)

        return pd.DataFrame(records)

    def build_collection_securables_dataframe(self, collections: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Build a DataFrame linking collections to securables (dashboards/datasets).

        Args:
            collections: List of collection objects

        Returns:
            DataFrame with collection-securable relationships
        """
        records = []
        for col in collections:
            collection_id = col.get('id', '')
            collection_name = self._extract_text(col.get('name', ''))

            for securable in col.get('securables', []):
                record = {
                    'collection_id': collection_id,
                    'collection_name': collection_name,
                    'securable_id': securable.get('id', ''),
                    'securable_name': self._extract_text(securable.get('name', '')),
                    'securable_type': securable.get('type', ''),
                }
                records.append(record)

        return pd.DataFrame(records) if records else pd.DataFrame()

    def build_dashboard_collections_map(self, collections: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Build a mapping of dashboard IDs to their collection names.

        Args:
            collections: List of collection objects

        Returns:
            Dict mapping dashboard_id -> list of collection names
        """
        dashboard_collections: Dict[str, List[str]] = {}

        for col in collections:
            collection_name = self._extract_text(col.get('name', ''))

            for securable in col.get('securables', []):
                if securable.get('type') == 'dashboard':
                    dashboard_id = securable.get('id', '')
                    if dashboard_id:
                        if dashboard_id not in dashboard_collections:
                            dashboard_collections[dashboard_id] = []
                        dashboard_collections[dashboard_id].append(collection_name)

        return dashboard_collections

    def get_dashboard_contents(self, dashboard_id: str) -> Dict[str, Any]:
        """
        Get detailed contents of a specific dashboard.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            Dashboard with full contents
        """
        response = self.client._make_request(
            action='get',
            resource='securable',
            find={
                'where': {
                    'id': dashboard_id
                },
                'attributes': [
                    'id', 'name', 'description', 'contents', 'options',
                    'modified_at', 'created_at', 'slug', 'type', 'subtype'
                ]
            }
        )

        rows = response.get('rows', [])
        return rows[0] if rows else {}

    def extract_charts_from_dashboard(self, dashboard: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract chart information from dashboard contents.

        Args:
            dashboard: Dashboard object

        Returns:
            List of chart metadata dictionaries
        """
        charts = []
        dashboard_id = dashboard.get('id', '')
        dashboard_name = get_dashboard_name(dashboard)
        contents = dashboard.get('contents', {})

        if not contents or not isinstance(contents, dict):
            return charts

        # Luzmo dashboards store items inside views
        # Structure: contents.views[].items[]
        views = contents.get('views', [])
        for view in views:
            if not isinstance(view, dict):
                continue

            screen_mode = view.get('screenModus', '')
            items = view.get('items', [])

            for item in items:
                if not isinstance(item, dict):
                    continue

                # Get title from options if available
                options = item.get('options', {})
                title = options.get('title', '') if isinstance(options, dict) else ''

                chart_info = {
                    'dashboard_id': dashboard_id,
                    'dashboard_name': dashboard_name,
                    'chart_id': item.get('id', ''),
                    'chart_type': item.get('type', ''),
                    'title': self._extract_text(title),
                    'screen_mode': screen_mode,
                    'position_x': item.get('x', ''),
                    'position_y': item.get('y', ''),
                    'width': item.get('w', ''),
                    'height': item.get('h', ''),
                }
                charts.append(chart_info)

        # Fallback: check for items directly in contents (older format)
        if not charts:
            items = contents.get('items', contents.get('charts', []))
            for item in items:
                if isinstance(item, dict):
                    chart_info = {
                        'dashboard_id': dashboard_id,
                        'dashboard_name': dashboard_name,
                        'chart_id': item.get('id', ''),
                        'chart_type': item.get('type', item.get('chartType', '')),
                        'title': self._extract_text(item.get('title', item.get('name', ''))),
                        'screen_mode': '',
                        'position_x': item.get('x', ''),
                        'position_y': item.get('y', ''),
                        'width': item.get('width', item.get('w', '')),
                        'height': item.get('height', item.get('h', '')),
                    }
                    charts.append(chart_info)

        return charts

    def extract_filters_from_dashboard(self, dashboard: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract filter information from dashboard.

        Args:
            dashboard: Dashboard object

        Returns:
            List of filter metadata dictionaries
        """
        filters = []
        dashboard_id = dashboard.get('id', '')
        dashboard_name = get_dashboard_name(dashboard)
        contents = dashboard.get('contents', {})
        options = dashboard.get('options', {})

        if not isinstance(contents, dict):
            return filters

        # Check views for filter items
        views = contents.get('views', [])
        for view in views:
            if not isinstance(view, dict):
                continue

            items = view.get('items', [])
            for item in items:
                if isinstance(item, dict) and 'filter' in item.get('type', '').lower():
                    item_options = item.get('options', {})
                    title = item_options.get('title', '') if isinstance(item_options, dict) else ''
                    filter_info = {
                        'dashboard_id': dashboard_id,
                        'dashboard_name': dashboard_name,
                        'filter_id': item.get('id', ''),
                        'filter_type': item.get('type', ''),
                        'title': self._extract_text(title),
                    }
                    filters.append(filter_info)

        # Check contents.filters
        content_filters = contents.get('filters', {})
        if isinstance(content_filters, dict):
            for filter_id, filter_data in content_filters.items():
                if isinstance(filter_data, dict):
                    filter_info = {
                        'dashboard_id': dashboard_id,
                        'dashboard_name': dashboard_name,
                        'filter_id': filter_id,
                        'filter_type': 'content_filter',
                        'title': self._extract_text(filter_data.get('name', filter_data.get('title', ''))),
                    }
                    filters.append(filter_info)

        # Check options for global filters
        if isinstance(options, dict):
            global_filters = options.get('filters', [])
            for f in global_filters:
                if isinstance(f, dict):
                    filter_info = {
                        'dashboard_id': dashboard_id,
                        'dashboard_name': dashboard_name,
                        'filter_id': f.get('id', ''),
                        'filter_type': 'global',
                        'title': self._extract_text(f.get('name', f.get('title', ''))),
                    }
                    filters.append(filter_info)

        return filters

    def _extract_text(self, value: Any, preferred_lang: str = 'en') -> str:
        """
        Extract text from various formats (string, dict with language keys).

        Args:
            value: Value to extract text from
            preferred_lang: Preferred language code

        Returns:
            Extracted text string
        """
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            if preferred_lang in value:
                return value[preferred_lang]
            if value:
                return str(list(value.values())[0])
        return ''

    def build_dashboards_dataframe(
        self,
        dashboards: List[Dict[str, Any]],
        collections: Optional[List[Dict[str, Any]]] = None
    ) -> pd.DataFrame:
        """
        Build a DataFrame of dashboard summary information.

        Args:
            dashboards: List of dashboard objects
            collections: Optional list of collection objects (to add collections column)

        Returns:
            DataFrame with dashboard information
        """
        # Build collections map if collections provided
        dashboard_collections_map = {}
        if collections:
            dashboard_collections_map = self.build_dashboard_collections_map(collections)

        records = []
        for dash in dashboards:
            contents = dash.get('contents', {})
            item_count = 0

            # Count items from views (modern structure)
            if isinstance(contents, dict):
                views = contents.get('views', [])
                for view in views:
                    if isinstance(view, dict):
                        items = view.get('items', [])
                        item_count += len(items) if isinstance(items, list) else 0

                # Fallback to items/charts directly
                if item_count == 0:
                    items = contents.get('items', contents.get('charts', []))
                    item_count = len(items) if isinstance(items, list) else 0

            dashboard_id = dash.get('id', '')

            # Get collections for this dashboard
            collection_names = dashboard_collections_map.get(dashboard_id, [])
            collections_str = ', '.join(collection_names) if collection_names else ''

            record = {
                'id': dashboard_id,
                'name': get_dashboard_name(dash),
                'description': get_dashboard_description(dash),
                'slug': dash.get('slug', ''),
                'type': dash.get('type', ''),
                'subtype': dash.get('subtype', ''),
                'item_count': item_count,
                'collections': collections_str,
                'owner_id': dash.get('owner_id', ''),
                'account_id': dash.get('account_id', ''),
                'modifier_id': dash.get('modifier_id', ''),
                'template_id': dash.get('template_id', ''),
                'created_at': dash.get('created_at', ''),
                'modified_at': dash.get('modified_at', ''),
            }
            records.append(record)

        return pd.DataFrame(records)

    def build_charts_dataframe(self, dashboards: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Build a DataFrame of all charts across dashboards.

        Args:
            dashboards: List of dashboard objects

        Returns:
            DataFrame with chart information
        """
        all_charts = []
        for dash in dashboards:
            charts = self.extract_charts_from_dashboard(dash)
            all_charts.extend(charts)

        return pd.DataFrame(all_charts) if all_charts else pd.DataFrame()

    def build_filters_dataframe(self, dashboards: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Build a DataFrame of all filters across dashboards.

        Args:
            dashboards: List of dashboard objects

        Returns:
            DataFrame with filter information
        """
        all_filters = []
        for dash in dashboards:
            filters = self.extract_filters_from_dashboard(dash)
            all_filters.extend(filters)

        return pd.DataFrame(all_filters) if all_filters else pd.DataFrame()

    def export_to_excel(self, output_path: Optional[str] = None) -> str:
        """
        Export all dashboard details to an Excel file.

        Args:
            output_path: Path for output file (auto-generated if not provided)

        Returns:
            Path to the created Excel file
        """
        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'dashboards_export_{timestamp}.xlsx'

        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Fetch all dashboards
        print("Fetching dashboards...")
        dashboards = self.get_all_dashboards_with_details()
        print(f"Found {len(dashboards)} dashboards")

        # Fetch collections to add to dashboards
        print("Fetching collections...")
        collections = self.get_all_collections()
        print(f"Found {len(collections)} collections")

        # Build DataFrames
        print("Building dashboard summary...")
        df_dashboards = self.build_dashboards_dataframe(dashboards, collections=collections)

        print("Extracting charts...")
        df_charts = self.build_charts_dataframe(dashboards)
        print(f"Found {len(df_charts)} charts")

        print("Extracting filters...")
        df_filters = self.build_filters_dataframe(dashboards)
        print(f"Found {len(df_filters)} filters")

        # Write to Excel with multiple sheets
        print(f"Writing to {output_path}...")
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df_dashboards.to_excel(writer, sheet_name='Dashboards', index=False)

            if not df_charts.empty:
                df_charts.to_excel(writer, sheet_name='Charts', index=False)

            if not df_filters.empty:
                df_filters.to_excel(writer, sheet_name='Filters', index=False)

        print(f"Export complete: {output_path}")
        return str(output_file.absolute())

    def export_to_bigquery(
        self,
        project_id: str,
        dataset_id: str = 'luzmo_metadata',
        if_exists: str = 'replace'
    ) -> Dict[str, str]:
        """
        Export all dashboard details to BigQuery.

        Args:
            project_id: Google Cloud project ID
            dataset_id: BigQuery dataset ID (default: 'luzmo_metadata')
            if_exists: What to do if table exists ('replace', 'append', 'fail')

        Returns:
            Dict with table names as keys and full table IDs as values
        """
        if not BIGQUERY_AVAILABLE:
            raise ImportError(
                "BigQuery libraries not installed. "
                "Run: pip install pandas-gbq google-cloud-bigquery"
            )

        # Fetch all dashboards
        print("Fetching dashboards...")
        dashboards = self.get_all_dashboards_with_details()
        print(f"Found {len(dashboards)} dashboards")

        # Fetch collections (needed for both dashboard collections column and collections tables)
        print("Fetching collections...")
        collections = self.get_all_collections()
        print(f"Found {len(collections)} collections")

        # Build DataFrames
        print("Building dashboard summary...")
        df_dashboards = self.build_dashboards_dataframe(dashboards, collections=collections)

        print("Extracting charts...")
        df_charts = self.build_charts_dataframe(dashboards)
        print(f"Found {len(df_charts)} charts")

        print("Extracting filters...")
        df_filters = self.build_filters_dataframe(dashboards)
        print(f"Found {len(df_filters)} filters")

        # Create BigQuery client to ensure dataset exists
        client = bigquery.Client(project=project_id)

        # Create dataset if it doesn't exist
        dataset_ref = f"{project_id}.{dataset_id}"
        try:
            client.get_dataset(dataset_ref)
            print(f"Dataset {dataset_ref} exists")
        except Exception:
            print(f"Creating dataset {dataset_ref}...")
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            client.create_dataset(dataset, exists_ok=True)

        results = {}

        # Upload dashboards table
        table_id = f"{project_id}.{dataset_id}.dashboards"
        print(f"Uploading to {table_id}...")
        pandas_gbq.to_gbq(
            df_dashboards,
            f"{dataset_id}.dashboards",
            project_id=project_id,
            if_exists=if_exists
        )
        results['dashboards'] = table_id
        print(f"  Uploaded {len(df_dashboards)} rows to dashboards")

        # Upload charts table
        if not df_charts.empty:
            table_id = f"{project_id}.{dataset_id}.charts"
            print(f"Uploading to {table_id}...")
            pandas_gbq.to_gbq(
                df_charts,
                f"{dataset_id}.charts",
                project_id=project_id,
                if_exists=if_exists
            )
            results['charts'] = table_id
            print(f"  Uploaded {len(df_charts)} rows to charts")

        # Upload filters table
        if not df_filters.empty:
            table_id = f"{project_id}.{dataset_id}.filters"
            print(f"Uploading to {table_id}...")
            pandas_gbq.to_gbq(
                df_filters,
                f"{dataset_id}.filters",
                project_id=project_id,
                if_exists=if_exists
            )
            results['filters'] = table_id
            print(f"  Uploaded {len(df_filters)} rows to filters")

        df_collections = self.build_collections_dataframe(collections)
        df_collection_securables = self.build_collection_securables_dataframe(collections)

        # Upload collections table
        if not df_collections.empty:
            table_id = f"{project_id}.{dataset_id}.collections"
            print(f"Uploading to {table_id}...")
            pandas_gbq.to_gbq(
                df_collections,
                f"{dataset_id}.collections",
                project_id=project_id,
                if_exists=if_exists
            )
            results['collections'] = table_id
            print(f"  Uploaded {len(df_collections)} rows to collections")

        # Upload collection_securables table (mapping table)
        if not df_collection_securables.empty:
            table_id = f"{project_id}.{dataset_id}.collection_securables"
            print(f"Uploading to {table_id}...")
            pandas_gbq.to_gbq(
                df_collection_securables,
                f"{dataset_id}.collection_securables",
                project_id=project_id,
                if_exists=if_exists
            )
            results['collection_securables'] = table_id
            print(f"  Uploaded {len(df_collection_securables)} rows to collection_securables")

        print("BigQuery export complete!")
        return results


def main():
    """Main function to export dashboards to Excel."""
    exporter = DashboardExporter()
    output_file = exporter.export_to_excel()
    print(f"\nDashboards exported to: {output_file}")


if __name__ == "__main__":
    main()
