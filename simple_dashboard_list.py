#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple script to list all dashboards (non-interactive).
"""

from src.luzmo_client import LuzmoClient
from src.utils import get_dashboard_name, get_dashboard_description
import sys
import io

# Fix Windows console encoding for unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    print("="*80)
    print("Luzmo Dashboards in Your Account")
    print("="*80)

    client = LuzmoClient()
    dashboards = client.list_dashboards()

    print(f"\n✓ Found {len(dashboards)} dashboard(s)\n")
    print("-"*80)

    for i, dashboard in enumerate(dashboards, 1):
        name = get_dashboard_name(dashboard)
        dash_id = dashboard.get('id')
        description = get_dashboard_description(dashboard)

        print(f"\n{i}. {name}")
        print(f"   ID: {dash_id}")
        if description:
            # Truncate long descriptions
            if len(description) > 100:
                print(f"   Description: {description[:100]}...")
            else:
                print(f"   Description: {description}")

    print("\n" + "="*80)
    print(f"Total: {len(dashboards)} dashboards")
    print("="*80)


if __name__ == "__main__":
    main()
