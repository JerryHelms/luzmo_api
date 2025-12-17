#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inspect a dashboard's structure to see parameters and how data is organized.
"""

from src.luzmo_client import LuzmoClient
import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    # Arkansas Work Order Details dashboard
    dashboard_id = "763e165d-04ce-408a-8bb9-58c67df4e7fc"

    print("="*80)
    print(f"Inspecting Dashboard Structure: {dashboard_id}")
    print("="*80)

    client = LuzmoClient()

    try:
        # Get full dashboard metadata
        dashboard = client.get_dashboard(dashboard_id)

        print("\n1. PARAMETERS:")
        print("-"*80)
        parameters = dashboard.get('contents', {}).get('parameters', [])
        if parameters:
            print(json.dumps(parameters, indent=2))
        else:
            print("No parameters found")

        print("\n2. FILTERS:")
        print("-"*80)
        filters = dashboard.get('contents', {}).get('filters', {})
        if filters:
            print(json.dumps(filters, indent=2))
        else:
            print("No filters found")

        print("\n3. VIEWS AND ITEMS (Charts):")
        print("-"*80)
        views = dashboard.get('contents', {}).get('views', [])
        if views:
            for view_idx, view in enumerate(views):
                screen_mode = view.get('screenModus', 'unknown')
                items = view.get('items', [])
                print(f"\nView {view_idx + 1} ({screen_mode}): {len(items)} items")

                for item_idx, item in enumerate(items):
                    print(f"\n  Item {item_idx + 1}:")
                    print(f"    ID: {item.get('id')}")
                    print(f"    Type: {item.get('type')}")
                    print(f"    Title: {item.get('options', {}).get('title', 'No title')}")

                    # Check for slots (data bindings)
                    slots = item.get('slots', [])
                    if slots:
                        print(f"    Slots ({len(slots)}):")
                        for slot in slots:
                            slot_name = slot.get('name')
                            slot_content = slot.get('content', [])
                            print(f"      - {slot_name}: {len(slot_content)} content items")
                            for content_item in slot_content[:2]:  # Show first 2
                                print(f"        Dataset: {content_item.get('datasetId', 'N/A')}")
                                print(f"        Column: {content_item.get('columnId', 'N/A')}")
        else:
            print("No views found")

        print("\n4. DATASET LINKS:")
        print("-"*80)
        dataset_links = dashboard.get('contents', {}).get('datasetLinks', {})
        if dataset_links:
            print(f"Found {len(dataset_links)} dataset(s):")
            for dataset_id, links in dataset_links.items():
                print(f"\n  Dataset ID: {dataset_id}")
                print(f"  Links: {links}")
        else:
            print("No dataset links found")

        print("\n5. FULL DASHBOARD KEYS:")
        print("-"*80)
        print(f"Top-level keys: {list(dashboard.keys())}")
        print(f"Contents keys: {list(dashboard.get('contents', {}).keys())}")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
