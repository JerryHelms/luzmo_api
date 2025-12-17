#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Luzmo API connection and list dashboards.
"""

from src.luzmo_client import LuzmoClient
import sys
import io

# Fix Windows console encoding for unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    print("="*80)
    print("Luzmo API Connection Test")
    print("="*80)

    try:
        # Initialize client
        print("\n1. Initializing Luzmo client...")
        client = LuzmoClient()
        print("   ✓ Client initialized successfully")

        # Test listing dashboards
        print("\n2. Fetching list of dashboards...")
        dashboards = client.list_dashboards()
        print(f"   ✓ Successfully retrieved dashboard list")

        # Display results
        print(f"\n3. Found {len(dashboards)} dashboard(s):")
        print("-"*80)

        if len(dashboards) == 0:
            print("   No dashboards found in your account")
        else:
            for i, dashboard in enumerate(dashboards, 1):
                name = dashboard.get('name', 'Unnamed Dashboard')
                dash_id = dashboard.get('id', 'N/A')
                description = dashboard.get('description', '')

                print(f"\n   Dashboard {i}:")
                print(f"   - Name: {name}")
                print(f"   - ID: {dash_id}")
                if description:
                    print(f"   - Description: {description}")

        print("\n" + "="*80)
        print("✓ Connection test PASSED!")
        print("="*80)

    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nPlease ensure:")
        print("1. You have created a .env file (copy from .env.example)")
        print("2. LUZMO_API_KEY is set in .env")
        print("3. LUZMO_API_TOKEN is set in .env")
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ Connection test FAILED!")
        print(f"Error: {str(e)}")
        print("\nPossible issues:")
        print("- Invalid API credentials")
        print("- Incorrect API endpoint")
        print("- Network connectivity problems")
        print("- API endpoint mismatch (may need to use official SDK)")
        sys.exit(1)

if __name__ == "__main__":
    main()
