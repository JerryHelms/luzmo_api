#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Summary Tool
Provides overview and search capabilities for Luzmo dashboards.
"""

import sys
import io
import argparse
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


def print_summary(dashboards, dashboard_collections, production_only=False):
    """Print overall summary with collection counts."""
    print("=" * 80)
    print("Dashboard Summary")
    print("=" * 80)
    print()

    # Count by collection
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

    # Print collection counts
    print(f"Total Dashboards: {len(dashboards)}")
    print(f"Dashboards without Collection: {dashboards_without_collection}")
    print()
    print("Dashboards by Collection:")
    print("-" * 40)

    for col_name in sorted(collection_counts.keys()):
        count = collection_counts[col_name]
        print(f"  {col_name:<30} {count:>3}")

    print()


def print_production_dashboards(dashboards, dashboard_collections):
    """Print names of production dashboards only."""
    print("=" * 80)
    print("Production Dashboards")
    print("=" * 80)
    print()

    production_dashboards = []

    for dash in dashboards:
        dash_id = dash.get('id')
        collections = dashboard_collections.get(dash_id, [])

        if 'Production Dashboards' in collections:
            production_dashboards.append(dash)

    if not production_dashboards:
        print("No production dashboards found.")
        return

    print(f"Found {len(production_dashboards)} production dashboard(s):")
    print()

    for dash in production_dashboards:
        name = get_dashboard_name(dash)
        dash_id = dash.get('id')
        collections = dashboard_collections.get(dash_id, [])

        # Show all collections for context
        collections_str = ', '.join(collections)
        print(f"  • {name}")
        print(f"    ID: {dash_id[:8]}")
        print(f"    Collections: {collections_str}")
        print()


def search_dashboards(dashboards, dashboard_collections, query):
    """Search for dashboards by name or collection."""
    print("=" * 80)
    print(f"Search Results: '{query}'")
    print("=" * 80)
    print()

    query_lower = query.lower()
    results = []

    for dash in dashboards:
        dash_id = dash.get('id')
        name = get_dashboard_name(dash)
        collections = dashboard_collections.get(dash_id, [])

        # Search in name or collections
        if (query_lower in name.lower() or
            any(query_lower in col.lower() for col in collections)):
            results.append((dash, collections))

    if not results:
        print("No dashboards found matching your search.")
        return

    print(f"Found {len(results)} dashboard(s):")
    print()

    for dash, collections in results:
        name = get_dashboard_name(dash)
        dash_id = dash.get('id')
        collections_str = ', '.join(collections) if collections else 'None'

        print(f"  • {name}")
        print(f"    ID: {dash_id[:8]}")
        print(f"    Collections: {collections_str}")
        print()


def list_all_dashboards(dashboards, dashboard_collections, production_only=False):
    """List all dashboards with their collections."""
    filtered_dashboards = dashboards

    if production_only:
        filtered_dashboards = [
            dash for dash in dashboards
            if 'Production Dashboards' in dashboard_collections.get(dash.get('id'), [])
        ]
        print("=" * 80)
        print("Production Dashboards (Detailed List)")
        print("=" * 80)
    else:
        print("=" * 80)
        print("All Dashboards")
        print("=" * 80)

    print()
    print(f"Total: {len(filtered_dashboards)} dashboard(s)")
    print()

    for i, dash in enumerate(filtered_dashboards, 1):
        dash_id = dash.get('id')
        name = get_dashboard_name(dash)
        collections = dashboard_collections.get(dash_id, [])
        collections_str = ', '.join(collections) if collections else 'None'

        print(f"{i}. {name}")
        print(f"   ID: {dash_id[:8]}")
        print(f"   Collections: {collections_str}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Dashboard summary and search tool'
    )
    parser.add_argument(
        '--search', '-s',
        help='Search for dashboards by name or collection'
    )
    parser.add_argument(
        '--production-only', '-p',
        action='store_true',
        help='Show only production dashboards'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all dashboards (or production only with -p)'
    )

    args = parser.parse_args()

    # Initialize
    exporter = DashboardExporter()

    print("Fetching dashboards...")
    dashboards = exporter.get_all_dashboards_with_details()

    print("Fetching collections...")
    dashboard_collections = get_dashboard_collections_map(exporter)

    print()

    # Execute based on arguments
    if args.search:
        search_dashboards(dashboards, dashboard_collections, args.search)
    elif args.list:
        list_all_dashboards(dashboards, dashboard_collections, args.production_only)
    elif args.production_only:
        print_production_dashboards(dashboards, dashboard_collections)
    else:
        # Default: show summary and production dashboards
        print_summary(dashboards, dashboard_collections)
        print()
        print_production_dashboards(dashboards, dashboard_collections)


if __name__ == "__main__":
    main()
