#!/usr/bin/env python3
"""
Dataset Usage Analyzer CLI

Analyzes which datasets are used most frequently across dashboards.

Usage:
    python analyze_dataset_usage.py                    # Print summary
    python analyze_dataset_usage.py --export           # Export to Excel
    python analyze_dataset_usage.py --unused           # Show unused datasets only
    python analyze_dataset_usage.py --top 20           # Show top 20 most used
    python analyze_dataset_usage.py --dataset <id>     # Show dashboards using specific dataset
"""

import argparse
from src.dataset_usage_analyzer import DatasetUsageAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description='Analyze dataset usage across dashboards',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_dataset_usage.py                    # Print summary
  python analyze_dataset_usage.py --export           # Export to Excel
  python analyze_dataset_usage.py --unused           # Show unused datasets
  python analyze_dataset_usage.py --top 20           # Top 20 most used
  python analyze_dataset_usage.py --dataset abc123   # Dashboards using dataset
        """
    )

    parser.add_argument(
        '--export',
        action='store_true',
        help='Export analysis to Excel file'
    )

    parser.add_argument(
        '--unused',
        action='store_true',
        help='Show only unused datasets'
    )

    parser.add_argument(
        '--top',
        type=int,
        default=20,
        help='Number of top datasets to show (default: 20)'
    )

    parser.add_argument(
        '--dataset',
        type=str,
        help='Show dashboards using a specific dataset ID'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Dataset Usage Analyzer")
    print("=" * 80)

    analyzer = DatasetUsageAnalyzer()

    # Specific dataset query
    if args.dataset:
        print(f"\nFinding dashboards that use dataset: {args.dataset}")
        print("-" * 80)

        dashboards = analyzer.get_dataset_dashboards(args.dataset)

        if dashboards:
            print(f"\nFound {len(dashboards)} dashboard(s) using this dataset:\n")
            for i, dashboard in enumerate(dashboards, 1):
                print(f"{i}. {dashboard['name']}")
                print(f"   ID: {dashboard['id']}")
                print(f"   Type: {dashboard['subtype']}")
                print()
        else:
            print("\nNo dashboards found using this dataset.")

        return

    # Unused datasets only
    if args.unused:
        print("\nFetching unused datasets...")
        unused = analyzer.get_unused_datasets()

        print(f"\n{'=' * 80}")
        print(f"Unused Datasets: {len(unused)}")
        print(f"{'=' * 80}\n")

        if unused:
            for i, dataset in enumerate(unused, 1):
                print(f"{i}. {dataset['dataset_name']}")
                print(f"   ID: {dataset['dataset_id']}")
                print(f"   Type: {dataset['dataset_subtype']}")
                print(f"   Rows: {dataset['dataset_rows']:,}")
                print()
        else:
            print("All datasets are in use!")

        return

    # Export to Excel
    if args.export:
        print("\nAnalyzing dataset usage...")
        filename = analyzer.export_to_excel()
        print(f"\n[OK] Analysis exported to: {filename}")
        return

    # Default: Print summary
    print("\nAnalyzing dataset usage...")
    results = analyzer.analyze_usage(include_dashboard_details=False)
    analyzer.print_summary(results, limit=args.top)


if __name__ == '__main__':
    main()
