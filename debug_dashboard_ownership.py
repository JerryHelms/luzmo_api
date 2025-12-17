#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to examine dashboard ownership and attributes.
"""

from src.luzmo_client import LuzmoClient
import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    client = LuzmoClient()

    print("Fetching dashboards with ALL attributes...")

    # Request more attributes to see what distinguishes user dashboards from templates
    response = client._make_request(
        action='get',
        resource='securable',
        find={
            'where': {
                'type': 'dashboard',
                'derived': False
            },
            'attributes': ['id', 'name', 'description', 'modified_at', 'created_at',
                          'created_by', 'template', 'shared', 'public', 'owner',
                          'user_id', 'organization_id'],
            'order': [['modified_at', 'desc']],
            'limit': 5  # Just get first 5 for inspection
        }
    )

    dashboards = response.get('rows', [])

    print(f"\nFound {len(dashboards)} dashboards (showing first 5 with full details):\n")
    print("="*80)

    for i, dashboard in enumerate(dashboards, 1):
        print(f"\nDashboard {i}:")
        print(json.dumps(dashboard, indent=2))
        print("-"*80)

    print("\n" + "="*80)
    print("Look for attributes like:")
    print("- 'template': true/false - indicates if it's a template")
    print("- 'owner' or 'created_by' - shows who created it")
    print("- 'shared' or 'public' - sharing status")
    print("="*80)


if __name__ == "__main__":
    main()
