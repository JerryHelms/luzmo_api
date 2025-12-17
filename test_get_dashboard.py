#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify get_dashboard() works with the fixed API structure.
"""

from src.luzmo_client import LuzmoClient
from src.dashboard_summary_pipeline import DashboardSummaryPipeline
import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    # Test with your "jerry test" dashboard
    dashboard_id = "2fac66e5-bd5c-498e-b026-4a8dcf07a5bb"

    print("="*80)
    print(f"Testing Dashboard Fetch: {dashboard_id}")
    print("="*80)

    try:
        # Test 1: Direct API client test
        print("\n1. Testing LuzmoClient.get_dashboard()...")
        client = LuzmoClient()
        dashboard = client.get_dashboard(dashboard_id)

        print("   ✓ Successfully fetched dashboard metadata!")
        print(f"\nDashboard Name: {dashboard.get('name', 'N/A')}")
        print(f"Dashboard ID: {dashboard.get('id', 'N/A')}")
        print(f"Type: {dashboard.get('type', 'N/A')}")

        print("\nFull dashboard metadata:")
        print(json.dumps(dashboard, indent=2))

        # Test 2: Full pipeline test
        print("\n" + "="*80)
        print("2. Testing Full Dashboard Analysis Pipeline...")
        print("="*80)

        pipeline = DashboardSummaryPipeline()

        print("\nGenerating AI summary...")
        result = pipeline.generate_summary(
            dashboard_id=dashboard_id,
            save_format='markdown'
        )
        summary_path = result.get('summary_path')

        print(f"\n✓ Summary generated successfully!")
        print(f"   Saved to: {summary_path}")

        print("\n" + "="*80)
        print("✓ All tests PASSED!")
        print("="*80)

    except Exception as e:
        print(f"\n✗ Test FAILED!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
