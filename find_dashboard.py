#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Search for a specific dashboard by ID.
"""

from src.luzmo_client import LuzmoClient
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    dashboard_id = "2fac66e5-bd5c-498e-b026-4a8dcf07a5bb"

    print(f"Searching for dashboard: {dashboard_id}")
    print("="*80)

    client = LuzmoClient()

    try:
        # Try to get the dashboard directly
        print("\n1. Trying to fetch dashboard directly...")
        dashboard = client.get_dashboard(dashboard_id)

        print("✓ Dashboard found!")
        print("\nDashboard details:")
        import json
        print(json.dumps(dashboard, indent=2))

    except Exception as e:
        print(f"✗ Could not fetch dashboard directly: {str(e)}")

        # Try listing all dashboards to see if it's there
        print("\n2. Searching in all dashboards...")
        response = client._make_request(
            action='get',
            resource='securable',
            find={
                'where': {
                    'type': 'dashboard'
                    # Removed 'derived': False to see ALL dashboards
                },
                'attributes': ['id', 'name', 'description', 'type', 'derived'],
                'order': [['modified_at', 'desc']]
            }
        )

        all_dashboards = response.get('rows', [])
        print(f"   Total dashboards (including derived): {len(all_dashboards)}")

        # Search for the ID
        found = None
        for dash in all_dashboards:
            if dash.get('id') == dashboard_id:
                found = dash
                break

        if found:
            print(f"\n✓ Found in all dashboards list!")
            print(json.dumps(found, indent=2))
        else:
            print(f"\n✗ Dashboard {dashboard_id} not found in your account")
            print("\nPossible reasons:")
            print("1. Dashboard belongs to a different Luzmo account")
            print("2. Incorrect API credentials")
            print("3. Dashboard ID is incorrect")
            print("4. Insufficient permissions to access this dashboard")


if __name__ == "__main__":
    main()
