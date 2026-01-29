#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export all Luzmo dashboards and their details to Excel or BigQuery.
Does not retrieve actual data or submit to LLM.
"""

import sys
import io
import argparse

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.dashboard_exporter import DashboardExporter


def main():
    parser = argparse.ArgumentParser(
        description='Export Luzmo dashboards to Excel or BigQuery'
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
        '--output', '-o',
        help='Output Excel file path (for Excel export)'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Luzmo Dashboard Exporter")
    print("=" * 80)
    print()

    exporter = DashboardExporter()

    if args.bigquery:
        if not args.project:
            print("Error: --project is required for BigQuery export")
            sys.exit(1)

        print(f"Exporting to BigQuery: {args.project}.{args.dataset}")
        print()

        results = exporter.export_to_bigquery(
            project_id=args.project,
            dataset_id=args.dataset,
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
        output_file = exporter.export_to_excel(output_path=args.output)

        print()
        print("=" * 80)
        print("Export complete!")
        print(f"File: {output_file}")
        print("=" * 80)


if __name__ == "__main__":
    main()
