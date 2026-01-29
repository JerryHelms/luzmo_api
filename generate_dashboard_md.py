#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate markdown documentation for Luzmo dashboards.
"""

import sys
import io
import argparse
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.dashboard_exporter import DashboardExporter
from src.dashboard_describer import DashboardDescriber
from src.utils import get_dashboard_name, get_dashboard_description


def generate_dashboard_markdown(
    dashboard_id: str,
    include_ai_description: bool = True,
    style: str = "business",
    screenshots_dir: str = "../screenshots"
) -> str:
    """
    Generate markdown documentation for a single dashboard.

    Args:
        dashboard_id: Dashboard ID
        include_ai_description: Whether to generate AI description
        style: Description style (business, technical, brief)
        screenshots_dir: Relative path from docs to screenshots directory

    Returns:
        Markdown string
    """
    exporter = DashboardExporter()

    # Get dashboard metadata
    dashboard = exporter.get_dashboard_contents(dashboard_id)
    if not dashboard:
        return f"# Error\n\nDashboard `{dashboard_id}` not found."

    name = get_dashboard_name(dashboard)
    description = get_dashboard_description(dashboard)
    safe_id = dashboard_id[:8]

    # Get collections for this dashboard
    collections = exporter.get_all_collections()
    dashboard_collections = []
    for col in collections:
        for securable in col.get('securables', []):
            if securable.get('id') == dashboard_id:
                col_name = col.get('name', {})
                if isinstance(col_name, dict):
                    col_name = col_name.get('en', list(col_name.values())[0] if col_name else '')
                dashboard_collections.append(col_name)

    # Build markdown
    lines = []

    # Header
    lines.append(f"# {name}")
    lines.append("")

    # Collections
    collections_str = ', '.join(dashboard_collections) if dashboard_collections else 'None'
    lines.append(f"**Collections:** {collections_str}")
    lines.append("")

    # Screenshot section
    # Check if screenshot exists
    from pathlib import Path

    # Generate safe name for screenshot filename
    safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in name)
    safe_name = safe_name[:50]  # Limit length
    screenshot_filename = f"{safe_name}_{safe_id}.png"

    # Check if screenshot file exists
    screenshot_path = Path('screenshots') / screenshot_filename
    if screenshot_path.exists():
        lines.append("## Screenshot")
        lines.append("")
        lines.append(f"![{name} Dashboard]({screenshots_dir}/{screenshot_filename})")
        lines.append("")

    # Original description
    if description:
        lines.append("## Description")
        lines.append("")
        lines.append(description)
        lines.append("")

    # AI-generated description
    if include_ai_description:
        describer = DashboardDescriber()
        result = describer.describe_dashboard(dashboard_id, style=style, include_tags=True)

        ai_description = result.get('generated_description', '')
        tags = result.get('tags', '')

        if ai_description and not ai_description.startswith('Error'):
            lines.append("## AI-Generated Summary")
            lines.append("")
            lines.append(ai_description)
            lines.append("")

            if tags:
                lines.append("### Tags")
                lines.append("")
                tag_list = [f"`{t.strip()}`" for t in tags.split(',')]
                lines.append(" ".join(tag_list))
                lines.append("")

    # Filters section
    contents = dashboard.get('contents', {})
    filters = extract_filters(contents)

    if filters:
        lines.append("## Filters")
        lines.append("")
        lines.append(f"This dashboard has **{len(filters)} interactive filters**:")
        lines.append("")

        for i, flt in enumerate(filters, 1):
            filter_name = flt.get('name', f'Filter {i}')
            filter_type = flt.get('type', 'unknown')
            lines.append(f"- **{filter_name}** ({filter_type})")

        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Luzmo API Tools*")

    return '\n'.join(lines)


def extract_charts(contents: dict) -> list:
    """Extract charts from dashboard contents."""
    charts = []

    if not isinstance(contents, dict):
        return charts

    # Check views structure
    views = contents.get('views', [])
    if isinstance(views, list):
        for view in views:
            items = view.get('items', [])
            if isinstance(items, list):
                for item in items:
                    if item.get('type') not in ('slicer-filter', 'filter', 'text', 'image'):
                        charts.append(item)

    # Fallback to items/charts directly
    if not charts:
        items = contents.get('items', contents.get('charts', []))
        if isinstance(items, list):
            for item in items:
                if item.get('type') not in ('slicer-filter', 'filter', 'text', 'image'):
                    charts.append(item)

    return charts


def extract_filters(contents: dict) -> list:
    """Extract filters from dashboard contents."""
    filters = []

    if not isinstance(contents, dict):
        return filters

    # Check views structure
    views = contents.get('views', [])
    if isinstance(views, list):
        for view in views:
            items = view.get('items', [])
            if isinstance(items, list):
                for item in items:
                    if item.get('type') in ('slicer-filter', 'filter'):
                        filters.append(item)

    # Fallback to items directly
    if not filters:
        items = contents.get('items', [])
        if isinstance(items, list):
            for item in items:
                if item.get('type') in ('slicer-filter', 'filter'):
                    filters.append(item)

    return filters


def format_date(date_str: str) -> str:
    """Format ISO date string to readable format."""
    if not date_str:
        return 'N/A'
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except:
        return date_str[:10] if len(date_str) >= 10 else date_str


def main():
    parser = argparse.ArgumentParser(
        description='Generate markdown documentation for Luzmo dashboards'
    )
    parser.add_argument(
        '--dashboard', '-d',
        help='Dashboard ID to document (if not specified, uses first available)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='dashboard_docs',
        help='Output directory for markdown files (default: dashboard_docs)'
    )
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Skip AI-generated description'
    )
    parser.add_argument(
        '--style', '-s',
        choices=['business', 'technical', 'brief'],
        default='business',
        help='AI description style (default: business)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available dashboards and exit'
    )

    args = parser.parse_args()

    exporter = DashboardExporter()

    # List dashboards if requested
    if args.list:
        print("Available dashboards:")
        print("-" * 60)
        dashboards = exporter.get_all_dashboards_with_details()
        for dash in dashboards[:20]:
            name = get_dashboard_name(dash)
            print(f"  {dash.get('id', '')}  {name}")
        if len(dashboards) > 20:
            print(f"  ... and {len(dashboards) - 20} more")
        return

    # Get dashboard ID
    dashboard_id = args.dashboard
    if not dashboard_id:
        print("Fetching first available dashboard...")
        dashboards = exporter.get_all_dashboards_with_details()
        if not dashboards:
            print("No dashboards found.")
            return
        dashboard_id = dashboards[0].get('id')
        print(f"Using dashboard: {get_dashboard_name(dashboards[0])}")

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating markdown for dashboard: {dashboard_id}")

    # Generate markdown
    markdown = generate_dashboard_markdown(
        dashboard_id,
        include_ai_description=not args.no_ai,
        style=args.style,
        screenshots_dir='../screenshots'
    )

    # Save to file
    safe_id = dashboard_id[:8]
    output_file = output_dir / f"dashboard_{safe_id}.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"\nMarkdown saved to: {output_file}")
    print("\nPreview:")
    print("=" * 60)
    # Print first 30 lines as preview
    preview_lines = markdown.split('\n')[:30]
    print('\n'.join(preview_lines))
    if len(markdown.split('\n')) > 30:
        print("...")
    print("=" * 60)


if __name__ == "__main__":
    main()
