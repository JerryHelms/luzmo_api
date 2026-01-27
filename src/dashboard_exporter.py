"""
Dashboard Exporter
Retrieves all dashboards and associated details, exports to Excel.
Does not retrieve actual data or submit to LLM.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .luzmo_client import LuzmoClient
from .utils import get_dashboard_name, get_dashboard_description


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

    def build_dashboards_dataframe(self, dashboards: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Build a DataFrame of dashboard summary information.

        Args:
            dashboards: List of dashboard objects

        Returns:
            DataFrame with dashboard information
        """
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

            record = {
                'id': dash.get('id', ''),
                'name': get_dashboard_name(dash),
                'description': get_dashboard_description(dash),
                'slug': dash.get('slug', ''),
                'type': dash.get('type', ''),
                'subtype': dash.get('subtype', ''),
                'item_count': item_count,
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

        # Build DataFrames
        print("Building dashboard summary...")
        df_dashboards = self.build_dashboards_dataframe(dashboards)

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


def main():
    """Main function to export dashboards to Excel."""
    exporter = DashboardExporter()
    output_file = exporter.export_to_excel()
    print(f"\nDashboards exported to: {output_file}")


if __name__ == "__main__":
    main()
