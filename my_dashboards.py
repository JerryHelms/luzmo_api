#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List only YOUR dashboards (filtering out Luzmo templates/demos).
"""

from src.luzmo_client import LuzmoClient
from src.utils import (
    get_dashboard_name,
    get_dashboard_description,
    filter_recent_dashboards,
    filter_dashboards_by_name_pattern
)
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    print("="*80)
    print("Your Luzmo Dashboards (Excluding Templates)")
    print("="*80)

    client = LuzmoClient()

    # Fetch with created_at to help filter
    response = client._make_request(
        action='get',
        resource='securable',
        find={
            'where': {
                'type': 'dashboard',
                'derived': False
            },
            'attributes': ['id', 'name', 'description', 'modified_at', 'created_at'],
            'order': [['modified_at', 'desc']]
        }
    )

    all_dashboards = response.get('rows', [])

    print(f"\nTotal dashboards in account: {len(all_dashboards)}")

    # Filter by recent creation (last 2 years)
    recent = filter_recent_dashboards(all_dashboards, years_back=2)
    print(f"Recently created (last 2 years): {len(recent)}")

    # Filter by name pattern
    filtered_by_name = filter_dashboards_by_name_pattern(recent)
    print(f"After excluding template/demo patterns: {len(filtered_by_name)}")

    print("\n" + "="*80)
    print("YOUR DASHBOARDS:")
    print("="*80)

    if len(filtered_by_name) == 0:
        print("\n⚠ No user dashboards found after filtering.")
        print("\nShowing all recent dashboards instead:")
        print("-"*80)
        dashboards_to_show = recent
    else:
        dashboards_to_show = filtered_by_name

    for i, dashboard in enumerate(dashboards_to_show, 1):
        name = get_dashboard_name(dashboard)
        dash_id = dashboard.get('id')
        description = get_dashboard_description(dashboard)
        created = dashboard.get('created_at', 'N/A')
        modified = dashboard.get('modified_at', 'N/A')

        print(f"\n{i}. {name}")
        print(f"   ID: {dash_id}")
        if description:
            print(f"   Description: {description[:100]}{'...' if len(description) > 100 else ''}")
        print(f"   Created: {created}")
        print(f"   Last Modified: {modified}")

    print("\n" + "="*80)
    print(f"Showing {len(dashboards_to_show)} dashboard(s)")
    print("="*80)

    print("\nTIP: To see ALL dashboards (including templates), run:")
    print("  python simple_dashboard_list.py")


if __name__ == "__main__":
    main()
