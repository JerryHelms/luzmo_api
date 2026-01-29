#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenerate markdown documentation for all Luzmo dashboards with AI descriptions and tags.
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.dashboard_exporter import DashboardExporter
from src.utils import get_dashboard_name
from generate_dashboard_md import generate_dashboard_markdown


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Regenerate dashboard documentation with AI descriptions and tags')
    parser.add_argument('--limit', '-l', type=int, default=None, help='Limit number of dashboards to process')
    args = parser.parse_args()

    print("=" * 80)
    print("Regenerating Dashboard Documentation")
    print("=" * 80)
    print()

    # Initialize exporter
    exporter = DashboardExporter()

    # Get all dashboards
    print("Fetching dashboards...")
    dashboards = exporter.get_all_dashboards_with_details()

    if args.limit:
        dashboards = dashboards[:args.limit]
        print(f"Processing {len(dashboards)} dashboards (limited)")
    else:
        print(f"Found {len(dashboards)} dashboards")
    print()

    # Create output directory
    output_dir = Path('dashboard_docs')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each dashboard
    successful = 0
    failed = 0

    for i, dash in enumerate(dashboards, 1):
        dashboard_id = dash.get('id')
        dashboard_name = get_dashboard_name(dash)

        print(f"[{i}/{len(dashboards)}] {dashboard_name}")

        try:
            # Generate markdown with AI description and tags
            markdown = generate_dashboard_markdown(
                dashboard_id,
                include_ai_description=True,
                style='business',
                screenshots_dir='../screenshots'
            )

            # Save to file
            safe_id = dashboard_id[:8]
            output_file = output_dir / f"dashboard_{safe_id}.md"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)

            print(f"  ✓ Saved to {output_file}")
            successful += 1

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            failed += 1

        print()

    # Summary
    print("=" * 80)
    print("Regeneration Complete!")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Output: {output_dir.absolute()}")
    print("=" * 80)


if __name__ == "__main__":
    main()
