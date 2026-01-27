#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate AI descriptions for Luzmo dashboards based on metadata only.
No data is retrieved - only dashboard structure and component information.
"""

import sys
import io
import argparse

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.dashboard_describer import DashboardDescriber


def main():
    parser = argparse.ArgumentParser(
        description='Generate AI descriptions for Luzmo dashboards'
    )
    parser.add_argument(
        '--dashboard', '-d',
        help='Specific dashboard ID to describe (optional)'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help='Limit number of dashboards to process'
    )
    parser.add_argument(
        '--style', '-s',
        choices=['business', 'technical', 'brief'],
        default='business',
        help='Description style (default: business)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output Excel file path'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Luzmo Dashboard Description Generator")
    print("=" * 80)
    print()
    print(f"Style: {args.style}")
    if args.limit:
        print(f"Limit: {args.limit} dashboards")
    print()

    describer = DashboardDescriber()

    if args.dashboard:
        # Single dashboard
        print(f"Generating description for dashboard: {args.dashboard}")
        result = describer.describe_dashboard(args.dashboard, style=args.style)

        print()
        print("-" * 80)
        print(f"Dashboard: {result.get('name', 'Unknown')}")
        print(f"ID: {result.get('id')}")
        print()
        print("Original Description:")
        print(result.get('original_description') or '(none)')
        print()
        print("Generated Description:")
        print(result.get('generated_description'))
        print("-" * 80)
    else:
        # All dashboards
        output_file = describer.export_descriptions_to_excel(
            output_path=args.output,
            style=args.style,
            limit=args.limit
        )

        print()
        print("=" * 80)
        print("Export complete!")
        print(f"File: {output_file}")
        print("=" * 80)


if __name__ == "__main__":
    main()
