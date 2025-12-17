#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check which account/organization the API credentials belong to.
"""

from src.luzmo_client import LuzmoClient
import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    print("="*80)
    print("Checking API Account Information")
    print("="*80)

    client = LuzmoClient()

    # Try to get user/account information
    try:
        print("\n1. Checking API authorization info...")

        # Get current user
        response = client._make_request(
            action='get',
            resource='authorization'
        )

        print("\nAuthorization Response:")
        print(json.dumps(response, indent=2))

    except Exception as e:
        print(f"Could not get authorization: {str(e)}")

    # Try to list all accessible resources
    try:
        print("\n2. Checking accessible dashboard count by type...")

        # Get all securables
        response = client._make_request(
            action='get',
            resource='securable',
            find={
                'where': {
                    'type': 'dashboard'
                },
                'attributes': ['id', 'name', 'type', 'derived', 'shared', 'public'],
                'limit': 100
            }
        )

        dashboards = response.get('rows', [])
        print(f"\nTotal accessible dashboards: {len(dashboards)}")

        # Show first 5 with details
        print("\nFirst 5 dashboards (with sharing info):")
        for i, dash in enumerate(dashboards[:5], 1):
            print(f"\n{i}. {dash.get('name')}")
            print(f"   ID: {dash.get('id')}")
            print(f"   Type: {dash.get('type')}")
            print(f"   Derived: {dash.get('derived')}")
            print(f"   Shared: {dash.get('shared')}")
            print(f"   Public: {dash.get('public')}")

    except Exception as e:
        print(f"Could not get securables: {str(e)}")


if __name__ == "__main__":
    main()
