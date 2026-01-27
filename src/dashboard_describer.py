"""
Dashboard Describer
Generates AI descriptions of dashboards based on metadata only (no data retrieval).
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .luzmo_client import LuzmoClient
from .llm_analyzer import LLMAnalyzer
from .utils import get_dashboard_name, get_dashboard_description


class DashboardDescriber:
    """Generates AI descriptions of dashboards from metadata."""

    def __init__(
        self,
        client: Optional[LuzmoClient] = None,
        llm: Optional[LLMAnalyzer] = None,
        model: str = "claude-3-haiku-20240307"
    ):
        """
        Initialize dashboard describer.

        Args:
            client: LuzmoClient instance
            llm: LLMAnalyzer instance
            model: Claude model to use
        """
        self.client = client or LuzmoClient()
        self.llm = llm or LLMAnalyzer(model=model)

    def get_dashboard_metadata(self, dashboard_id: str) -> Dict[str, Any]:
        """
        Fetch dashboard metadata without data.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            Dashboard metadata
        """
        response = self.client._make_request(
            action='get',
            resource='securable',
            find={
                'where': {'id': dashboard_id},
                'attributes': [
                    'id', 'name', 'description', 'contents', 'options',
                    'created_at', 'modified_at', 'subtype'
                ]
            }
        )

        rows = response.get('rows', [])
        return rows[0] if rows else {}

    def get_all_dashboards_metadata(self) -> List[Dict[str, Any]]:
        """
        Fetch all dashboards with metadata.

        Returns:
            List of dashboard metadata
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
                    'id', 'name', 'description', 'contents', 'options',
                    'created_at', 'modified_at', 'subtype'
                ],
                'order': [['modified_at', 'desc']]
            }
        )

        return response.get('rows', [])

    def _extract_text(self, value: Any, preferred_lang: str = 'en') -> str:
        """Extract text from language dict or string."""
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            if preferred_lang in value:
                return value[preferred_lang]
            if value:
                return str(list(value.values())[0])
        return ''

    def format_dashboard_for_llm(self, dashboard: Dict[str, Any]) -> str:
        """
        Format dashboard metadata as text for LLM consumption.

        Args:
            dashboard: Dashboard object

        Returns:
            Formatted text description of dashboard structure
        """
        name = get_dashboard_name(dashboard)
        description = get_dashboard_description(dashboard)
        contents = dashboard.get('contents', {})

        lines = [
            f"Dashboard Name: {name}",
            f"Existing Description: {description or 'None provided'}",
            ""
        ]

        if not isinstance(contents, dict):
            lines.append("No contents available")
            return '\n'.join(lines)

        # Extract views and items
        views = contents.get('views', [])
        total_items = 0
        chart_types = {}
        filter_items = []
        chart_titles = []

        for view in views:
            if not isinstance(view, dict):
                continue

            screen_mode = view.get('screenModus', 'default')
            items = view.get('items', [])

            for item in items:
                if not isinstance(item, dict):
                    continue

                total_items += 1
                item_type = item.get('type', 'unknown')

                # Count chart types
                chart_types[item_type] = chart_types.get(item_type, 0) + 1

                # Get title
                options = item.get('options', {})
                title = ''
                if isinstance(options, dict):
                    title = self._extract_text(options.get('title', ''))

                if title:
                    chart_titles.append(f"- {title} ({item_type})")

                # Track filters
                if 'filter' in item_type.lower():
                    filter_items.append(item_type)

        lines.append(f"Total Components: {total_items}")
        lines.append("")

        # Chart type breakdown
        lines.append("Component Types:")
        for chart_type, count in sorted(chart_types.items(), key=lambda x: -x[1]):
            lines.append(f"  - {chart_type}: {count}")

        # Chart titles
        if chart_titles:
            lines.append("")
            lines.append("Named Components:")
            for title in chart_titles[:20]:  # Limit to 20
                lines.append(f"  {title}")
            if len(chart_titles) > 20:
                lines.append(f"  ... and {len(chart_titles) - 20} more")

        # Dataset links
        dataset_links = contents.get('datasetLinks', {})
        if dataset_links:
            lines.append("")
            lines.append(f"Connected Datasets: {len(dataset_links)}")

        # Parameters
        parameters = contents.get('parameters', [])
        if parameters:
            lines.append("")
            lines.append(f"Parameters: {len(parameters)}")

        return '\n'.join(lines)

    def generate_description(
        self,
        dashboard: Dict[str, Any],
        style: str = "business"
    ) -> str:
        """
        Generate an AI description of a dashboard.

        Args:
            dashboard: Dashboard metadata
            style: Description style ("business", "technical", "brief")

        Returns:
            Generated description
        """
        metadata_text = self.format_dashboard_for_llm(dashboard)

        style_instructions = {
            "business": "Write a business-friendly description that explains what insights and value this dashboard provides. Focus on what questions it answers and who would use it.",
            "technical": "Write a technical description that explains the dashboard's structure, data sources, and visualization types. Include details about filters and interactivity.",
            "brief": "Write a concise 2-3 sentence description of what this dashboard shows and its purpose."
        }

        prompt = f"""Based on this dashboard metadata, generate a description of what this dashboard is for and what it shows.

{metadata_text}

Instructions: {style_instructions.get(style, style_instructions['business'])}

Do not make up specific data values or metrics - focus on describing the dashboard's purpose and structure based on the component names and types provided."""

        try:
            message = self.llm.client.messages.create(
                model=self.llm.model,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text.strip()
        except Exception as e:
            return f"Error generating description: {str(e)}"

    def describe_dashboard(
        self,
        dashboard_id: str,
        style: str = "business"
    ) -> Dict[str, str]:
        """
        Generate description for a single dashboard.

        Args:
            dashboard_id: Dashboard ID
            style: Description style

        Returns:
            Dict with dashboard info and generated description
        """
        dashboard = self.get_dashboard_metadata(dashboard_id)
        if not dashboard:
            return {"error": f"Dashboard {dashboard_id} not found"}

        description = self.generate_description(dashboard, style)

        return {
            "id": dashboard_id,
            "name": get_dashboard_name(dashboard),
            "original_description": get_dashboard_description(dashboard),
            "generated_description": description
        }

    def describe_all_dashboards(
        self,
        style: str = "business",
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Generate descriptions for all dashboards.

        Args:
            style: Description style
            limit: Optional limit on number of dashboards

        Returns:
            List of dashboard descriptions
        """
        dashboards = self.get_all_dashboards_metadata()

        if limit:
            dashboards = dashboards[:limit]

        results = []
        for i, dashboard in enumerate(dashboards, 1):
            name = get_dashboard_name(dashboard)
            print(f"Processing {i}/{len(dashboards)}: {name}")

            description = self.generate_description(dashboard, style)

            results.append({
                "id": dashboard.get('id', ''),
                "name": name,
                "original_description": get_dashboard_description(dashboard),
                "generated_description": description
            })

        return results

    def export_descriptions_to_excel(
        self,
        output_path: Optional[str] = None,
        style: str = "business",
        limit: Optional[int] = None
    ) -> str:
        """
        Generate descriptions and export to Excel.

        Args:
            output_path: Output file path
            style: Description style
            limit: Optional limit on dashboards

        Returns:
            Path to created file
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'dashboard_descriptions_{timestamp}.xlsx'

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        print("Generating dashboard descriptions...")
        descriptions = self.describe_all_dashboards(style=style, limit=limit)

        df = pd.DataFrame(descriptions)

        print(f"Writing to {output_path}...")
        df.to_excel(output_path, sheet_name='Descriptions', index=False)

        print(f"Export complete: {output_path}")
        return str(output_file.absolute())


def main():
    """Main function to generate dashboard descriptions."""
    describer = DashboardDescriber()

    # Generate for all dashboards (limit to 10 for demo)
    output_file = describer.export_descriptions_to_excel(limit=10)
    print(f"\nDescriptions exported to: {output_file}")


if __name__ == "__main__":
    main()
