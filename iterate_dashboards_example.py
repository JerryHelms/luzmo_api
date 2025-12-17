#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple example showing how to iterate through Luzmo dashboards programmatically.
"""

from src.luzmo_client import LuzmoClient


def iterate_all_dashboards():
    """
    Example: Iterate through all dashboards and print their details.
    """
    # Initialize the client
    client = LuzmoClient()

    # Get all dashboards
    dashboards = client.list_dashboards()

    print(f"Total dashboards: {len(dashboards)}\n")

    # Iterate through each dashboard
    for dashboard in dashboards:
        # Extract dashboard information
        dashboard_id = dashboard.get('id')
        name = dashboard.get('name', 'Unnamed')
        description = dashboard.get('description', 'No description')
        modified_at = dashboard.get('modified_at', 'Unknown')

        print(f"Dashboard: {name}")
        print(f"  ID: {dashboard_id}")
        print(f"  Description: {description}")
        print(f"  Last Modified: {modified_at}")
        print()


def get_dashboard_by_name(name_to_find):
    """
    Example: Find a specific dashboard by name.

    Args:
        name_to_find: Dashboard name to search for

    Returns:
        Dashboard object if found, None otherwise
    """
    client = LuzmoClient()
    dashboards = client.list_dashboards()

    for dashboard in dashboards:
        if dashboard.get('name') == name_to_find:
            return dashboard

    return None


def get_recently_modified_dashboards(limit=5):
    """
    Example: Get the most recently modified dashboards.

    Args:
        limit: Number of dashboards to return

    Returns:
        List of dashboards sorted by modification date
    """
    client = LuzmoClient()
    dashboards = client.list_dashboards()

    # Dashboards are already sorted by modified_at desc from the API
    return dashboards[:limit]


def iterate_with_details():
    """
    Example: Iterate dashboards and fetch detailed information for each.
    """
    client = LuzmoClient()
    dashboards = client.list_dashboards()

    for dashboard in dashboards:
        dashboard_id = dashboard.get('id')
        name = dashboard.get('name', 'Unnamed')

        print(f"Processing: {name} (ID: {dashboard_id})")

        # Fetch full dashboard details
        try:
            dashboard_details = client.get_dashboard(dashboard_id)
            print(f"  Type: {dashboard_details.get('type', 'N/A')}")
            print(f"  Full details available: Yes")
        except Exception as e:
            print(f"  Error fetching details: {str(e)}")

        print()


if __name__ == "__main__":
    import sys
    import io

    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("="*80)
    print("Example 1: Iterate All Dashboards")
    print("="*80 + "\n")
    iterate_all_dashboards()

    print("\n" + "="*80)
    print("Example 2: Get Recently Modified Dashboards")
    print("="*80 + "\n")
    recent = get_recently_modified_dashboards(limit=3)
    for i, dashboard in enumerate(recent, 1):
        print(f"{i}. {dashboard.get('name', 'Unnamed')}")

    print("\n" + "="*80)
    print("Example 3: Find Dashboard by Name")
    print("="*80 + "\n")
    # Replace "My Dashboard" with an actual dashboard name from your account
    dashboard = get_dashboard_by_name("My Dashboard")
    if dashboard:
        print(f"Found: {dashboard.get('name')}")
    else:
        print("Dashboard not found (try a different name)")

    print("\n" + "="*80)
    print("Example 4: Iterate with Full Details")
    print("="*80 + "\n")
    iterate_with_details()
