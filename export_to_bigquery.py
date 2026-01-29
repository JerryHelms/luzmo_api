#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified BigQuery export for all Luzmo metadata.
Exports dashboards, charts, filters, collections, and optionally AI-generated descriptions and tags.
"""

import sys
import io
import argparse

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.dashboard_exporter import DashboardExporter
from src.dashboard_describer import DashboardDescriber


def main():
    parser = argparse.ArgumentParser(
        description='Export all Luzmo metadata to BigQuery'
    )
    parser.add_argument(
        '--project', '-p',
        required=True,
        help='Google Cloud project ID'
    )
    parser.add_argument(
        '--dataset', '-d',
        default='luzmo_metadata',
        help='BigQuery dataset ID (default: luzmo_metadata)'
    )
    parser.add_argument(
        '--if-exists',
        choices=['replace', 'append', 'fail'],
        default='replace',
        help='What to do if BigQuery table exists (default: replace)'
    )
    parser.add_argument(
        '--include-descriptions',
        action='store_true',
        help='Generate AI descriptions and tags (uses Claude API credits)'
    )
    parser.add_argument(
        '--style', '-s',
        choices=['business', 'technical', 'brief'],
        default='business',
        help='Description style (default: business)'
    )
    parser.add_argument(
        '--max-tags',
        type=int,
        default=5,
        help='Maximum number of tags per dashboard (default: 5)'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help='Limit number of dashboards for descriptions (default: all)'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Luzmo BigQuery Export")
    print("=" * 80)
    print()
    print(f"Project: {args.project}")
    print(f"Dataset: {args.dataset}")
    print(f"Include descriptions: {'Yes' if args.include_descriptions else 'No'}")
    if args.include_descriptions:
        print(f"  Style: {args.style}")
        print(f"  Max tags: {args.max_tags}")
        if args.limit:
            print(f"  Limit: {args.limit} dashboards")
    print()

    all_results = {}

    # Step 1: Export metadata (dashboards, charts, filters, collections)
    print("-" * 80)
    print("Step 1: Exporting dashboard metadata...")
    print("-" * 80)
    print()

    exporter = DashboardExporter()
    metadata_results = exporter.export_to_bigquery(
        project_id=args.project,
        dataset_id=args.dataset,
        if_exists=args.if_exists
    )
    all_results.update(metadata_results)

    # Step 2: Generate and export descriptions (optional)
    if args.include_descriptions:
        print()
        print("-" * 80)
        print("Step 2: Generating AI descriptions and tags...")
        print("-" * 80)
        print()

        describer = DashboardDescriber()
        description_results = describer.export_to_bigquery(
            project_id=args.project,
            dataset_id=args.dataset,
            style=args.style,
            limit=args.limit,
            max_tags=args.max_tags,
            if_exists=args.if_exists
        )
        all_results.update(description_results)

    # Summary
    print()
    print("=" * 80)
    print("Export complete!")
    print("=" * 80)
    print()
    print("Tables created:")
    for table_name, table_id in all_results.items():
        print(f"  - {table_id}")
    print()
    print(f"Total tables: {len(all_results)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
