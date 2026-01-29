#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a markdown index/summary of all dashboards in the documentation directory.
Creates a user-friendly README for the dashboard_docs directory.
"""

import sys
import io
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.dashboard_exporter import DashboardExporter
from src.utils import get_dashboard_name


def get_dashboard_collections_map(exporter):
    """
    Build a mapping of dashboard_id -> list of collection names.

    Returns:
        dict: {dashboard_id: [collection_name1, collection_name2, ...]}
    """
    collections = exporter.get_all_collections()
    dashboard_collections = defaultdict(list)

    for col in collections:
        col_name = col.get('name', {})
        if isinstance(col_name, dict):
            col_name = col_name.get('en', list(col_name.values())[0] if col_name else '')

        for securable in col.get('securables', []):
            dashboard_id = securable.get('id')
            if dashboard_id:
                dashboard_collections[dashboard_id].append(col_name)

    return dashboard_collections


def generate_markdown_index(dashboards, dashboard_collections):
    """Generate a markdown index of all dashboards."""
    lines = []

    # Header
    lines.append("# Dashboard Documentation Index")
    lines.append("")
    lines.append("This directory contains comprehensive documentation for all Luzmo dashboards.")
    lines.append("")
    lines.append(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Summary statistics
    lines.append("## Summary")
    lines.append("")

    collection_counts = defaultdict(int)
    dashboards_without_collection = 0

    for dash in dashboards:
        dash_id = dash.get('id')
        collections = dashboard_collections.get(dash_id, [])

        if not collections:
            dashboards_without_collection += 1
        else:
            for col in collections:
                collection_counts[col] += 1

    lines.append(f"- **Total Dashboards:** {len(dashboards)}")
    lines.append(f"- **Dashboards Documented:** {len(dashboards)}")
    lines.append(f"- **Collections:** {len(collection_counts)}")
    lines.append("")

    # Collection counts table
    lines.append("### Dashboards by Collection")
    lines.append("")
    lines.append("| Collection | Count |")
    lines.append("|------------|-------|")

    for col_name in sorted(collection_counts.keys()):
        count = collection_counts[col_name]
        lines.append(f"| {col_name} | {count} |")

    lines.append(f"| *(No Collection)* | {dashboards_without_collection} |")
    lines.append("")

    # Production Dashboards Section
    lines.append("## Production Dashboards")
    lines.append("")
    lines.append("These dashboards are actively used in production environments.")
    lines.append("")

    production_dashboards = []
    for dash in dashboards:
        dash_id = dash.get('id')
        collections = dashboard_collections.get(dash_id, [])
        if 'Production Dashboards' in collections:
            production_dashboards.append((dash, collections))

    # Sort alphabetically
    production_dashboards.sort(key=lambda x: get_dashboard_name(x[0]))

    lines.append(f"**Total Production Dashboards:** {len(production_dashboards)}")
    lines.append("")

    for dash, collections in production_dashboards:
        name = get_dashboard_name(dash)
        dash_id = dash.get('id')
        safe_id = dash_id[:8]

        # Create link to markdown file
        doc_file = f"dashboard_{safe_id}.md"

        # Get all collections for context
        other_collections = [c for c in collections if c != 'Production Dashboards']
        collection_badges = []
        for col in other_collections:
            collection_badges.append(f"`{col}`")

        badges_str = " ".join(collection_badges) if collection_badges else ""

        lines.append(f"- **[{name}]({doc_file})** {badges_str}")

    lines.append("")

    # All Dashboards by Collection
    lines.append("## All Dashboards by Collection")
    lines.append("")

    for col_name in sorted(collection_counts.keys()):
        lines.append(f"### {col_name}")
        lines.append("")

        # Get dashboards in this collection
        col_dashboards = []
        for dash in dashboards:
            dash_id = dash.get('id')
            collections = dashboard_collections.get(dash_id, [])
            if col_name in collections:
                col_dashboards.append(dash)

        # Sort alphabetically
        col_dashboards.sort(key=lambda x: get_dashboard_name(x))

        for dash in col_dashboards:
            name = get_dashboard_name(dash)
            dash_id = dash.get('id')
            safe_id = dash_id[:8]
            doc_file = f"dashboard_{safe_id}.md"
            lines.append(f"- [{name}]({doc_file})")

        lines.append("")

    # Dashboards without collection
    if dashboards_without_collection > 0:
        lines.append("### Other Dashboards")
        lines.append("")

        other_dashboards = []
        for dash in dashboards:
            dash_id = dash.get('id')
            collections = dashboard_collections.get(dash_id, [])
            if not collections:
                other_dashboards.append(dash)

        # Sort alphabetically
        other_dashboards.sort(key=lambda x: get_dashboard_name(x))

        for dash in other_dashboards:
            name = get_dashboard_name(dash)
            dash_id = dash.get('id')
            safe_id = dash_id[:8]
            doc_file = f"dashboard_{safe_id}.md"
            lines.append(f"- [{name}]({doc_file})")

        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("## How to Use This Documentation")
    lines.append("")
    lines.append("1. **Browse by Collection** - Use the sections above to find dashboards by their collection")
    lines.append("2. **Search** - Use your browser's search (Ctrl+F / Cmd+F) to find specific dashboards")
    lines.append("3. **Click Links** - Each dashboard name links to its detailed documentation")
    lines.append("")
    lines.append("Each dashboard documentation includes:")
    lines.append("- Business description and use cases")
    lines.append("- AI-generated summary")
    lines.append("- Relevant tags for categorization")
    lines.append("- Component and filter information")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"*Generated by Luzmo API Tools on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    return '\n'.join(lines)


def main():
    print("=" * 80)
    print("Generating Dashboard Documentation Index")
    print("=" * 80)
    print()

    # Initialize
    exporter = DashboardExporter()

    print("Fetching dashboards...")
    dashboards = exporter.get_all_dashboards_with_details()
    print(f"Found {len(dashboards)} dashboards")

    print("Fetching collections...")
    dashboard_collections = get_dashboard_collections_map(exporter)

    print("Generating markdown index...")
    markdown = generate_markdown_index(dashboards, dashboard_collections)

    # Save to dashboard_docs directory
    output_dir = Path('dashboard_docs')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'README.md'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print()
    print("=" * 80)
    print("Index Generation Complete!")
    print(f"File saved to: {output_file.absolute()}")
    print("=" * 80)
    print()
    print("Preview (first 50 lines):")
    print("-" * 80)
    preview_lines = markdown.split('\n')[:50]
    print('\n'.join(preview_lines))
    if len(markdown.split('\n')) > 50:
        print("...")
        print(f"({len(markdown.split('\n')) - 50} more lines)")


if __name__ == "__main__":
    main()
