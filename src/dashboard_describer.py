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

    def generate_tags(
        self,
        dashboard: Dict[str, Any],
        max_tags: int = 5
    ) -> List[str]:
        """
        Generate subject-related tags for a dashboard.

        Args:
            dashboard: Dashboard metadata
            max_tags: Maximum number of tags to generate

        Returns:
            List of tags
        """
        metadata_text = self.format_dashboard_for_llm(dashboard)

        prompt = f"""Based on this dashboard metadata, generate {max_tags} subject-related tags that describe what this dashboard is about.

{metadata_text}

Instructions:
- Generate exactly {max_tags} tags (or fewer if not enough context)
- Tags should be lowercase, single words or short phrases (2-3 words max)
- Focus on business domains, topics, and use cases
- Examples of good tags: inventory, work orders, sales, customer support, operations, analytics, performance, scheduling, locations, users, finance, HR
- Return ONLY the tags, one per line, no numbering or bullets
- Do not include generic tags like "dashboard" or "data"

Tags:"""

        try:
            message = self.llm.client.messages.create(
                model=self.llm.model,
                max_tokens=100,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            response = message.content[0].text.strip()

            # Parse tags from response
            tags = []
            for line in response.split('\n'):
                tag = line.strip().lower()
                # Remove any numbering, bullets, or dashes
                tag = tag.lstrip('0123456789.-) ')
                if tag and len(tag) < 50:  # Sanity check
                    tags.append(tag)

            return tags[:max_tags]
        except Exception as e:
            return []

    def generate_description_and_tags(
        self,
        dashboard: Dict[str, Any],
        style: str = "business",
        max_tags: int = 5
    ) -> Dict[str, Any]:
        """
        Generate both description and tags for a dashboard in a single call.

        Args:
            dashboard: Dashboard metadata
            style: Description style
            max_tags: Maximum number of tags

        Returns:
            Dict with description and tags
        """
        metadata_text = self.format_dashboard_for_llm(dashboard)

        style_instructions = {
            "business": "Write a business-friendly description that explains what insights and value this dashboard provides. Focus on what questions it answers and who would use it.",
            "technical": "Write a technical description that explains the dashboard's structure, data sources, and visualization types. Include details about filters and interactivity.",
            "brief": "Write a concise 2-3 sentence description of what this dashboard shows and its purpose."
        }

        prompt = f"""Based on this dashboard metadata, generate a description and subject tags.

{metadata_text}

Generate TWO things:

1. DESCRIPTION: {style_instructions.get(style, style_instructions['business'])}
Do not make up specific data values - focus on the dashboard's purpose based on component names and types.

2. TAGS: Generate up to {max_tags} subject-related tags (lowercase, single words or short phrases).
Focus on business domains, topics, use cases. Examples: inventory, work orders, sales, operations, scheduling.

Format your response EXACTLY like this:
DESCRIPTION:
[Your description here]

TAGS:
[tag1]
[tag2]
[tag3]"""

        try:
            message = self.llm.client.messages.create(
                model=self.llm.model,
                max_tokens=600,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            response = message.content[0].text.strip()

            # Parse response
            description = ""
            tags = []

            if "DESCRIPTION:" in response and "TAGS:" in response:
                parts = response.split("TAGS:")
                desc_part = parts[0].replace("DESCRIPTION:", "").strip()
                tags_part = parts[1].strip() if len(parts) > 1 else ""

                description = desc_part

                # Parse tags
                for line in tags_part.split('\n'):
                    tag = line.strip().lower()
                    tag = tag.lstrip('0123456789.-) []')
                    tag = tag.rstrip(']')
                    if tag and len(tag) < 50:
                        tags.append(tag)
            else:
                # Fallback: treat entire response as description
                description = response

            return {
                "description": description,
                "tags": tags[:max_tags]
            }
        except Exception as e:
            return {
                "description": f"Error: {str(e)}",
                "tags": []
            }

    def describe_dashboard(
        self,
        dashboard_id: str,
        style: str = "business",
        include_tags: bool = True,
        max_tags: int = 5
    ) -> Dict[str, Any]:
        """
        Generate description for a single dashboard.

        Args:
            dashboard_id: Dashboard ID
            style: Description style
            include_tags: Whether to generate tags
            max_tags: Maximum number of tags

        Returns:
            Dict with dashboard info, description, and tags
        """
        dashboard = self.get_dashboard_metadata(dashboard_id)
        if not dashboard:
            return {"error": f"Dashboard {dashboard_id} not found"}

        if include_tags:
            result = self.generate_description_and_tags(dashboard, style, max_tags)
            description = result["description"]
            tags = result["tags"]
        else:
            description = self.generate_description(dashboard, style)
            tags = []

        return {
            "id": dashboard_id,
            "name": get_dashboard_name(dashboard),
            "original_description": get_dashboard_description(dashboard),
            "generated_description": description,
            "tags": ", ".join(tags) if tags else ""
        }

    def describe_all_dashboards(
        self,
        style: str = "business",
        limit: Optional[int] = None,
        include_tags: bool = True,
        max_tags: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate descriptions for all dashboards.

        Args:
            style: Description style
            limit: Optional limit on number of dashboards
            include_tags: Whether to generate tags
            max_tags: Maximum number of tags per dashboard

        Returns:
            List of dashboard descriptions with tags
        """
        dashboards = self.get_all_dashboards_metadata()

        if limit:
            dashboards = dashboards[:limit]

        results = []
        for i, dashboard in enumerate(dashboards, 1):
            name = get_dashboard_name(dashboard)
            print(f"Processing {i}/{len(dashboards)}: {name}")

            if include_tags:
                result = self.generate_description_and_tags(dashboard, style, max_tags)
                description = result["description"]
                tags = result["tags"]
            else:
                description = self.generate_description(dashboard, style)
                tags = []

            results.append({
                "id": dashboard.get('id', ''),
                "name": name,
                "original_description": get_dashboard_description(dashboard),
                "generated_description": description,
                "tags": ", ".join(tags) if tags else ""
            })

        return results

    def export_descriptions_to_excel(
        self,
        output_path: Optional[str] = None,
        style: str = "business",
        limit: Optional[int] = None,
        include_tags: bool = True,
        max_tags: int = 5
    ) -> str:
        """
        Generate descriptions and export to Excel.

        Args:
            output_path: Output file path
            style: Description style
            limit: Optional limit on dashboards
            include_tags: Whether to generate tags
            max_tags: Maximum tags per dashboard

        Returns:
            Path to created file
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'dashboard_descriptions_{timestamp}.xlsx'

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        print("Generating dashboard descriptions and tags...")
        descriptions = self.describe_all_dashboards(
            style=style,
            limit=limit,
            include_tags=include_tags,
            max_tags=max_tags
        )

        df = pd.DataFrame(descriptions)

        print(f"Writing to {output_path}...")
        df.to_excel(output_path, sheet_name='Descriptions', index=False)

        print(f"Export complete: {output_path}")
        return str(output_file.absolute())

    def build_tags_dataframe(self, descriptions: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Build a DataFrame of distinct tags with dashboard counts.

        Args:
            descriptions: List of description results with tags

        Returns:
            DataFrame with tag and dashboard_count columns
        """
        tag_counts: Dict[str, int] = {}

        for desc in descriptions:
            tags_str = desc.get('tags', '')
            if tags_str:
                for tag in tags_str.split(', '):
                    tag = tag.strip()
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1

        records = [
            {'tag': tag, 'dashboard_count': count}
            for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1])
        ]

        return pd.DataFrame(records) if records else pd.DataFrame()

    def build_dashboard_tags_dataframe(self, descriptions: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Build a junction table linking dashboards to tags.

        Args:
            descriptions: List of description results with tags

        Returns:
            DataFrame with dashboard_id, dashboard_name, and tag columns
        """
        records = []

        for desc in descriptions:
            dashboard_id = desc.get('id', '')
            dashboard_name = desc.get('name', '')
            tags_str = desc.get('tags', '')

            if tags_str:
                for tag in tags_str.split(', '):
                    tag = tag.strip()
                    if tag:
                        records.append({
                            'dashboard_id': dashboard_id,
                            'dashboard_name': dashboard_name,
                            'tag': tag
                        })

        return pd.DataFrame(records) if records else pd.DataFrame()

    def export_to_bigquery(
        self,
        project_id: str,
        dataset_id: str = 'luzmo_metadata',
        style: str = "business",
        limit: Optional[int] = None,
        max_tags: int = 5,
        if_exists: str = 'replace'
    ) -> Dict[str, str]:
        """
        Generate descriptions and tags, then export to BigQuery.

        Args:
            project_id: Google Cloud project ID
            dataset_id: BigQuery dataset ID
            style: Description style
            limit: Optional limit on dashboards
            max_tags: Maximum tags per dashboard
            if_exists: What to do if table exists ('replace', 'append', 'fail')

        Returns:
            Dict with table names and full table IDs
        """
        try:
            import pandas_gbq
            from google.cloud import bigquery
        except ImportError:
            raise ImportError(
                "BigQuery libraries not installed. "
                "Run: pip install pandas-gbq google-cloud-bigquery"
            )

        print("Generating dashboard descriptions and tags...")
        descriptions = self.describe_all_dashboards(
            style=style,
            limit=limit,
            include_tags=True,
            max_tags=max_tags
        )

        # Build DataFrames
        df_descriptions = pd.DataFrame(descriptions)
        df_tags = self.build_tags_dataframe(descriptions)
        df_dashboard_tags = self.build_dashboard_tags_dataframe(descriptions)

        print(f"Generated {len(df_descriptions)} descriptions")
        print(f"Found {len(df_tags)} distinct tags")
        print(f"Created {len(df_dashboard_tags)} dashboard-tag relationships")

        # Create BigQuery client to ensure dataset exists
        client = bigquery.Client(project=project_id)

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

        # Upload descriptions table
        table_id = f"{project_id}.{dataset_id}.dashboard_descriptions"
        print(f"Uploading to {table_id}...")
        pandas_gbq.to_gbq(
            df_descriptions,
            f"{dataset_id}.dashboard_descriptions",
            project_id=project_id,
            if_exists=if_exists
        )
        results['dashboard_descriptions'] = table_id
        print(f"  Uploaded {len(df_descriptions)} rows")

        # Upload tags table
        if not df_tags.empty:
            table_id = f"{project_id}.{dataset_id}.tags"
            print(f"Uploading to {table_id}...")
            pandas_gbq.to_gbq(
                df_tags,
                f"{dataset_id}.tags",
                project_id=project_id,
                if_exists=if_exists
            )
            results['tags'] = table_id
            print(f"  Uploaded {len(df_tags)} rows")

        # Upload dashboard_tags junction table
        if not df_dashboard_tags.empty:
            table_id = f"{project_id}.{dataset_id}.dashboard_tags"
            print(f"Uploading to {table_id}...")
            pandas_gbq.to_gbq(
                df_dashboard_tags,
                f"{dataset_id}.dashboard_tags",
                project_id=project_id,
                if_exists=if_exists
            )
            results['dashboard_tags'] = table_id
            print(f"  Uploaded {len(df_dashboard_tags)} rows")

        print("BigQuery export complete!")
        return results


def main():
    """Main function to generate dashboard descriptions."""
    describer = DashboardDescriber()

    # Generate for all dashboards (limit to 10 for demo)
    output_file = describer.export_descriptions_to_excel(limit=10)
    print(f"\nDescriptions exported to: {output_file}")


if __name__ == "__main__":
    main()
