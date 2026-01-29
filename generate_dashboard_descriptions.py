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
    parser.add_argument(
        '--no-tags',
        action='store_true',
        help='Disable tag generation'
    )
    parser.add_argument(
        '--max-tags',
        type=int,
        default=5,
        help='Maximum number of tags per dashboard (default: 5)'
    )
    parser.add_argument(
        '--bigquery', '-bq',
        action='store_true',
        help='Export to BigQuery instead of Excel'
    )
    parser.add_argument(
        '--project', '-p',
        help='Google Cloud project ID (required for BigQuery)'
    )
    parser.add_argument(
        '--dataset',
        default='luzmo_metadata',
        help='BigQuery dataset ID (default: luzmo_metadata)'
    )
    parser.add_argument(
        '--if-exists',
        choices=['replace', 'append', 'fail'],
        default='replace',
        help='What to do if BigQuery table exists (default: replace)'
    )

    args = parser.parse_args()

    include_tags = not args.no_tags

    print("=" * 80)
    print("Luzmo Dashboard Description Generator")
    print("=" * 80)
    print()
    print(f"Style: {args.style}")
    print(f"Tags: {'enabled' if include_tags else 'disabled'}" + (f" (max {args.max_tags})" if include_tags else ""))
    if args.limit:
        print(f"Limit: {args.limit} dashboards")
    print()

    describer = DashboardDescriber()

    if args.dashboard:
        # Single dashboard
        print(f"Generating description for dashboard: {args.dashboard}")
        result = describer.describe_dashboard(
            args.dashboard,
            style=args.style,
            include_tags=include_tags,
            max_tags=args.max_tags
        )

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
        if include_tags and result.get('tags'):
            print()
            print("Tags:")
            print(result.get('tags'))
        print("-" * 80)
    elif args.bigquery:
        # BigQuery export
        if not args.project:
            print("Error: --project is required for BigQuery export")
            sys.exit(1)

        print(f"Exporting to BigQuery: {args.project}.{args.dataset}")
        print()

        results = describer.export_to_bigquery(
            project_id=args.project,
            dataset_id=args.dataset,
            style=args.style,
            limit=args.limit,
            max_tags=args.max_tags,
            if_exists=args.if_exists
        )

        print()
        print("=" * 80)
        print("Export complete!")
        print("Tables created:")
        for table_name, table_id in results.items():
            print(f"  - {table_id}")
        print("=" * 80)
    else:
        # Excel export
        output_file = describer.export_descriptions_to_excel(
            output_path=args.output,
            style=args.style,
            limit=args.limit,
            include_tags=include_tags,
            max_tags=args.max_tags
        )

        print()
        print("=" * 80)
        print("Export complete!")
        print(f"File: {output_file}")
        print("=" * 80)


if __name__ == "__main__":
    main()
